#include "Weapons/BRWeapon_Projectile.h"
#include "Weapons/BRProjectileRocket.h"
#include "Character/BRCharacter.h"
#include "CollisionQueryParams.h"
#include "Engine/World.h"
#include "GameFramework/PlayerController.h"

ABRWeapon_Projectile::ABRWeapon_Projectile()
{
	WeaponType = EBRWeaponType::RocketLauncher;
	MagSize = 1;
	CurrentAmmo = 1;
	ReserveAmmo = 5;
	FireRate = 0.5f;
	ReloadTime = 3.5f;
	BaseDamage = 110.0f;
	LaunchSpeed = 3500.0f; // 35 m/s
	AimTraceDistance = 20000.0f; // 200 m

	ProjectileClass = ABRProjectileRocket::StaticClass();
}

void ABRWeapon_Projectile::Fire()
{
	Super::Fire(); // Client-side cosmetic prediction: immediately plays muzzle flash and sound

	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	const FVector SpawnLocation = GetMuzzleLocation();
	FRotator SpawnRotation = GetMuzzleDirection().Rotation();

	// Fix projectile trajectory so it fires towards the crosshair rather than directly down camera forward
	if (OwningCharacter)
	{
		if (AController* Controller = OwningCharacter->GetController())
		{
			FVector CamLoc;
			FRotator CamRot;
			Controller->GetPlayerViewPoint(CamLoc, CamRot);

			const FVector CamForward = CamRot.Vector();
			const FVector TraceEnd = CamLoc + (CamForward * AimTraceDistance);

			FCollisionQueryParams QueryParams;
			QueryParams.AddIgnoredActor(this);
			QueryParams.AddIgnoredActor(OwningCharacter);
			QueryParams.bTraceComplex = true;

			FHitResult HitResult;
			FVector TargetPoint = TraceEnd;
			if (World->LineTraceSingleByChannel(HitResult, CamLoc, TraceEnd, ECC_Visibility, QueryParams))
			{
				TargetPoint = HitResult.ImpactPoint;
			}

			FVector LaunchDirection = (TargetPoint - SpawnLocation).GetSafeNormal();

			// Fallback to camera forward if target point is behind or directly adjacent to the muzzle
			if (FVector::DotProduct(LaunchDirection, CamForward) <= 0.0f)
			{
				LaunchDirection = CamForward;
			}

			SpawnRotation = LaunchDirection.Rotation();
		}
	}

	// Server performs actual projectile spawning
	if (!HasAuthority())
	{
		return;
	}

	if (!ProjectileClass)
	{
		return;
	}

	FActorSpawnParameters SpawnParams;
	SpawnParams.Owner = this;
	SpawnParams.Instigator = OwningCharacter ? OwningCharacter.Get() : GetInstigator();
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	World->SpawnActor<ABRProjectileRocket>(
		ProjectileClass,
		SpawnLocation,
		SpawnRotation,
		SpawnParams
	);
}
