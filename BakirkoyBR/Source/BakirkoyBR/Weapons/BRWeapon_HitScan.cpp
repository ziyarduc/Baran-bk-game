#include "Weapons/BRWeapon_HitScan.h"
#include "Character/BRCharacter.h"
#include "Kismet/GameplayStatics.h"
#include "CollisionQueryParams.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraComponent.h"
#include "Particles/ParticleSystemComponent.h"
#include "Sound/SoundBase.h"

ABRWeapon_HitScan::ABRWeapon_HitScan()
{
	WeaponType = EBRWeaponType::AssaultRifle;
	MagSize = 30;
	CurrentAmmo = 30;
	ReserveAmmo = 120;
	FireRate = 10.0f; // 600 RPM
	ReloadTime = 2.2f;
	BaseDamage = 30.0f;
	HeadshotMultiplier = 2.0f;

	MaxTraceDistance = 10000.0f; // 100 meters
	BaseSpreadAngle = 1.2f;
	ADSSpreadMultiplier = 0.4f;

	DamageFalloffStart = 3500.0f; // 35 meters
	DamageFalloffFloorDistance = 8000.0f; // 80 meters
	DamageFalloffFloorMultiplier = 0.55f;

	TracerEndParamName = TEXT("Target");
}

void ABRWeapon_HitScan::PlayTracerAndImpactEffects(const FVector& MuzzleLoc, const FVector& EndPoint, const FHitResult& HitResult, bool bHit)
{
	if (GetNetMode() == NM_DedicatedServer)
	{
		return;
	}

	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	// Bullet tracer cascade emitter
	if (TracerFX)
	{
		UParticleSystemComponent* TracerComp = UGameplayStatics::SpawnEmitterAtLocation(World, TracerFX, MuzzleLoc);
		if (TracerComp)
		{
			TracerComp->SetVectorParameter(TracerEndParamName, EndPoint);
		}
	}

	// Bullet tracer Niagara system
	if (NiagaraTracerFX)
	{
		UNiagaraComponent* NiagaraTracerComp = UNiagaraFunctionLibrary::SpawnSystemAtLocation(World, NiagaraTracerFX, MuzzleLoc);
		if (NiagaraTracerComp)
		{
			NiagaraTracerComp->SetVariableVec3(TracerEndParamName, EndPoint);
		}
	}

	// Impact effects when surface was hit
	if (bHit)
	{
		const FRotator ImpactRotation = HitResult.ImpactNormal.Rotation();

		if (ImpactFX)
		{
			UGameplayStatics::SpawnEmitterAtLocation(World, ImpactFX, HitResult.ImpactPoint, ImpactRotation);
		}

		if (NiagaraImpactFX)
		{
			UNiagaraFunctionLibrary::SpawnSystemAtLocation(World, NiagaraImpactFX, HitResult.ImpactPoint, ImpactRotation);
		}

		if (ImpactSound)
		{
			UGameplayStatics::PlaySoundAtLocation(World, ImpactSound, HitResult.ImpactPoint);
		}
	}
}

void ABRWeapon_HitScan::Fire()
{
	Super::Fire(); // Immediate client prediction: plays muzzle flash and fire sound

	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	FVector TraceStart = FVector::ZeroVector;
	FVector AimDirection = FVector::ForwardVector;
	GetTraceOriginAndDirection(TraceStart, AimDirection);

	// Compute bullet spread based on ADS state
	float CurrentSpread = BaseSpreadAngle;
	if (OwningCharacter && OwningCharacter->bIsADS)
	{
		CurrentSpread *= ADSSpreadMultiplier;
	}

	const FVector ShotDirection = FMath::VRandCone(AimDirection, FMath::DegreesToRadians(CurrentSpread));
	const FVector TraceEnd = TraceStart + (ShotDirection * MaxTraceDistance);

	FCollisionQueryParams QueryParams;
	QueryParams.AddIgnoredActor(this);
	if (OwningCharacter)
	{
		QueryParams.AddIgnoredActor(OwningCharacter);
	}
	QueryParams.bTraceComplex = true;
	QueryParams.bReturnPhysicalMaterial = true;

	FHitResult HitResult;
	const bool bHit = World->LineTraceSingleByChannel(
		HitResult,
		TraceStart,
		TraceEnd,
		ECC_Visibility,
		QueryParams
	);

	const FVector MuzzleLoc = GetMuzzleLocation();
	const FVector TracerEndPoint = bHit ? HitResult.ImpactPoint : TraceEnd;

	// Client-side cosmetic prediction: immediate tracer and impact effects
	PlayTracerAndImpactEffects(MuzzleLoc, TracerEndPoint, HitResult, bHit);

	// Server performs actual damage calculation
	if (!HasAuthority())
	{
		return;
	}

	if (bHit && HitResult.GetActor())
	{
		AActor* HitActor = HitResult.GetActor();
		const float HitDistance = FVector::Dist(TraceStart, HitResult.ImpactPoint);
		const float FalloffMultiplier = CalculateDamageFalloff(HitDistance);

		// Headshot detection via bone name check
		const bool bIsHeadshot = (HitResult.BoneName == TEXT("head") || HitResult.BoneName == TEXT("Head"));
		const float FinalDamage = BaseDamage * FalloffMultiplier * (bIsHeadshot ? HeadshotMultiplier : 1.0f);

		AController* InstigatorController = GetInstigatorController();
		if (!InstigatorController && OwningCharacter)
		{
			InstigatorController = OwningCharacter->GetController();
		}

		UGameplayStatics::ApplyPointDamage(
			HitActor,
			FinalDamage,
			ShotDirection,
			HitResult,
			InstigatorController,
			this,
			nullptr
		);
	}
}

float ABRWeapon_HitScan::CalculateDamageFalloff(float Distance) const
{
	if (Distance <= DamageFalloffStart)
	{
		return 1.0f;
	}

	if (Distance >= DamageFalloffFloorDistance)
	{
		return DamageFalloffFloorMultiplier;
	}

	const float DistanceRange = DamageFalloffFloorDistance - DamageFalloffStart;
	if (FMath::IsNearlyZero(DistanceRange))
	{
		return DamageFalloffFloorMultiplier;
	}

	const float Alpha = (Distance - DamageFalloffStart) / DistanceRange;
	return FMath::Lerp(1.0f, DamageFalloffFloorMultiplier, Alpha);
}

void ABRWeapon_HitScan::GetTraceOriginAndDirection(FVector& OutTraceStart, FVector& OutDirection) const
{
	if (OwningCharacter)
	{
		if (AController* Controller = OwningCharacter->GetController())
		{
			FRotator ControlRotation;
			Controller->GetPlayerViewPoint(OutTraceStart, ControlRotation);
			OutDirection = ControlRotation.Vector();
			return;
		}
	}

	OutTraceStart = GetMuzzleLocation();
	OutDirection = GetMuzzleDirection();
}
