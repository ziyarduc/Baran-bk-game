#include "Weapons/BRWeaponBase.h"
#include "Character/BRCharacter.h"
#include "Components/SkeletalMeshComponent.h"
#include "Net/UnrealNetwork.h"
#include "TimerManager.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraComponent.h"
#include "Particles/ParticleSystemComponent.h"
#include "Sound/SoundBase.h"

ABRWeaponBase::ABRWeaponBase()
{
	PrimaryActorTick.bCanEverTick = true;
	bReplicates = true;
	SetReplicateMovement(true);

	WeaponMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("WeaponMesh"));
	RootComponent = WeaponMesh;

	CurrentState = EBRWeaponState::Idle;
	WeaponType = EBRWeaponType::AssaultRifle;
	MagSize = 30;
	CurrentAmmo = 30;
	ReserveAmmo = 120;
	FireRate = 10.0f;
	ReloadTime = 2.2f;
	BaseDamage = 30.0f;
	HeadshotMultiplier = 2.0f;
	LastFireTime = 0.0f;

	MuzzleSocketName = TEXT("MuzzleSocket");
	AttachSocketName = TEXT("WeaponSocket_R");
	HolsterSocketName = TEXT("WeaponSocket_Back");
}

void ABRWeaponBase::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);

	DOREPLIFETIME(ABRWeaponBase, OwningCharacter);
	DOREPLIFETIME(ABRWeaponBase, CurrentState);
	DOREPLIFETIME(ABRWeaponBase, CurrentAmmo);
	DOREPLIFETIME(ABRWeaponBase, ReserveAmmo);
}

void ABRWeaponBase::BeginPlay()
{
	Super::BeginPlay();
}

void ABRWeaponBase::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(TimerHandle_HandleFiring);
		World->GetTimerManager().ClearTimer(TimerHandle_Reload);
	}

	Super::EndPlay(EndPlayReason);
}

bool ABRWeaponBase::CanFire() const
{
	return (CurrentState == EBRWeaponState::Idle || CurrentState == EBRWeaponState::Firing)
		&& CurrentAmmo > 0
		&& OwningCharacter != nullptr;
}

bool ABRWeaponBase::CanReload() const
{
	return CurrentState != EBRWeaponState::Reloading
		&& CurrentAmmo < MagSize
		&& ReserveAmmo > 0
		&& OwningCharacter != nullptr;
}

void ABRWeaponBase::StartFire()
{
	if (!HasAuthority())
	{
		Server_StartFire();
	}

	if (!CanFire())
	{
		if (CurrentAmmo <= 0)
		{
			SetWeaponState(EBRWeaponState::OutOfAmmo);
			if (ReserveAmmo > 0)
			{
				Reload();
			}
		}
		return;
	}

	SetWeaponState(EBRWeaponState::Firing);

	const float TimeBetweenShots = (FireRate > 0.0f) ? (1.0f / FireRate) : 0.1f;
	const float TimeSinceLastFire = GetWorld() ? (GetWorld()->GetTimeSeconds() - LastFireTime) : 0.0f;
	const float InitialDelay = FMath::Max(0.0f, TimeBetweenShots - TimeSinceLastFire);

	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().SetTimer(
			TimerHandle_HandleFiring,
			this,
			&ABRWeaponBase::HandleFiring,
			TimeBetweenShots,
			true,
			InitialDelay
		);
	}
}

void ABRWeaponBase::StopFire()
{
	if (!HasAuthority())
	{
		Server_StopFire();
	}

	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(TimerHandle_HandleFiring);
	}

	if (CurrentState == EBRWeaponState::Firing)
	{
		SetWeaponState(CurrentAmmo > 0 ? EBRWeaponState::Idle : EBRWeaponState::OutOfAmmo);
	}
}

void ABRWeaponBase::Reload()
{
	if (!HasAuthority())
	{
		Server_Reload();
		return;
	}

	if (!CanReload())
	{
		return;
	}

	StopFire();
	SetWeaponState(EBRWeaponState::Reloading);

	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().SetTimer(
			TimerHandle_Reload,
			this,
			&ABRWeaponBase::FinishReload,
			ReloadTime,
			false
		);
	}
}

void ABRWeaponBase::HandleFiring()
{
	if (CanFire())
	{
		Fire();
		CurrentAmmo = FMath::Max(0, CurrentAmmo - 1);
		OnAmmoChanged.Broadcast(CurrentAmmo, ReserveAmmo);
		if (UWorld* World = GetWorld())
		{
			LastFireTime = World->GetTimeSeconds();
		}

		if (CurrentAmmo <= 0)
		{
			SetWeaponState(EBRWeaponState::OutOfAmmo);
			StopFire();
			if (ReserveAmmo > 0)
			{
				Reload();
			}
		}
	}
	else
	{
		StopFire();
	}
}

void ABRWeaponBase::FinishReload()
{
	if (!HasAuthority())
	{
		return;
	}

	const int32 AmmoNeeded = MagSize - CurrentAmmo;
	const int32 AmmoToTake = FMath::Min(AmmoNeeded, ReserveAmmo);

	CurrentAmmo += AmmoToTake;
	ReserveAmmo -= AmmoToTake;

	OnAmmoChanged.Broadcast(CurrentAmmo, ReserveAmmo);
	SetWeaponState(CurrentAmmo > 0 ? EBRWeaponState::Idle : EBRWeaponState::OutOfAmmo);
}

void ABRWeaponBase::PlayMuzzleEffects()
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

	const FVector MuzzleLoc = GetMuzzleLocation();

	if (MuzzleFlashFX && WeaponMesh)
	{
		UGameplayStatics::SpawnEmitterAttached(
			MuzzleFlashFX,
			WeaponMesh,
			MuzzleSocketName,
			FVector::ZeroVector,
			FRotator::ZeroRotator,
			EAttachLocation::SnapToTarget
		);
	}

	if (NiagaraMuzzleFlashFX && WeaponMesh)
	{
		UNiagaraFunctionLibrary::SpawnSystemAttached(
			NiagaraMuzzleFlashFX,
			WeaponMesh,
			MuzzleSocketName,
			FVector::ZeroVector,
			FRotator::ZeroRotator,
			EAttachLocation::SnapToTarget,
			true
		);
	}

	if (FireSound)
	{
		UGameplayStatics::PlaySoundAtLocation(World, FireSound, MuzzleLoc);
	}
}

void ABRWeaponBase::Fire()
{
	PlayMuzzleEffects();
}

void ABRWeaponBase::Equip(ABRCharacter* InCharacter)
{
	if (!InCharacter)
	{
		return;
	}

	OwningCharacter = InCharacter;
	SetInstigator(InCharacter);

	if (USkeletalMeshComponent* CharacterMesh = InCharacter->GetMesh())
	{
		if (WeaponMesh)
		{
			WeaponMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			AttachToComponent(CharacterMesh, FAttachmentTransformRules::SnapToTargetNotIncludingScale, AttachSocketName);
		}
	}

	SetWeaponState(CurrentAmmo > 0 ? EBRWeaponState::Idle : EBRWeaponState::OutOfAmmo);
	OnAmmoChanged.Broadcast(CurrentAmmo, ReserveAmmo);
	OnOwnerChanged.Broadcast(OwningCharacter);
}

void ABRWeaponBase::Holster()
{
	StopFire();

	if (UWorld* World = GetWorld())
	{
		World->GetTimerManager().ClearTimer(TimerHandle_Reload);
	}

	if (OwningCharacter && WeaponMesh)
	{
		if (USkeletalMeshComponent* CharacterMesh = OwningCharacter->GetMesh())
		{
			AttachToComponent(CharacterMesh, FAttachmentTransformRules::SnapToTargetNotIncludingScale, HolsterSocketName);
		}
	}

	SetWeaponState(EBRWeaponState::Idle);
}

FVector ABRWeaponBase::GetMuzzleLocation() const
{
	if (WeaponMesh && WeaponMesh->DoesSocketExist(MuzzleSocketName))
	{
		return WeaponMesh->GetSocketLocation(MuzzleSocketName);
	}
	return GetActorLocation();
}

FVector ABRWeaponBase::GetMuzzleDirection() const
{
	if (WeaponMesh && WeaponMesh->DoesSocketExist(MuzzleSocketName))
	{
		return WeaponMesh->GetSocketRotation(MuzzleSocketName).Vector();
	}
	return GetActorForwardVector();
}

void ABRWeaponBase::SetWeaponState(EBRWeaponState NewState)
{
	const EBRWeaponState OldState = CurrentState;
	CurrentState = NewState;
	OnRep_CurrentState(OldState);
}

bool ABRWeaponBase::Server_StartFire_Validate()
{
	return true;
}

void ABRWeaponBase::Server_StartFire_Implementation()
{
	StartFire();
}

bool ABRWeaponBase::Server_StopFire_Validate()
{
	return true;
}

void ABRWeaponBase::Server_StopFire_Implementation()
{
	StopFire();
}

bool ABRWeaponBase::Server_Reload_Validate()
{
	return true;
}

void ABRWeaponBase::Server_Reload_Implementation()
{
	Reload();
}

void ABRWeaponBase::OnRep_CurrentAmmo(int32 OldAmmo)
{
	OnAmmoChanged.Broadcast(CurrentAmmo, ReserveAmmo);

	if (CurrentAmmo <= 0 && CurrentState == EBRWeaponState::Firing)
	{
		SetWeaponState(EBRWeaponState::OutOfAmmo);
	}
}

void ABRWeaponBase::OnRep_ReserveAmmo(int32 OldReserve)
{
	OnAmmoChanged.Broadcast(CurrentAmmo, ReserveAmmo);
}

void ABRWeaponBase::OnRep_CurrentState(EBRWeaponState OldState)
{
	OnWeaponStateChanged.Broadcast(CurrentState, OldState);

	switch (CurrentState)
	{
	case EBRWeaponState::Idle:
		if (OldState == EBRWeaponState::Reloading)
		{
			// Reload completed
		}
		break;
	case EBRWeaponState::Firing:
		// Weapon in firing state
		break;
	case EBRWeaponState::Reloading:
		// Weapon in reload state
		break;
	case EBRWeaponState::OutOfAmmo:
		// Magazine empty
		break;
	default:
		break;
	}
}

void ABRWeaponBase::OnRep_OwningCharacter(ABRCharacter* OldCharacter)
{
	if (OwningCharacter)
	{
		SetInstigator(OwningCharacter);

		if (USkeletalMeshComponent* CharacterMesh = OwningCharacter->GetMesh())
		{
			if (WeaponMesh)
			{
				WeaponMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
				const FName TargetSocket = (OwningCharacter->GetCurrentWeapon() == this) ? AttachSocketName : HolsterSocketName;
				AttachToComponent(CharacterMesh, FAttachmentTransformRules::SnapToTargetNotIncludingScale, TargetSocket);
			}
		}
	}
	else
	{
		DetachFromActor(FDetachmentTransformRules::KeepWorldTransform);
		if (WeaponMesh)
		{
			WeaponMesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
		}
	}

	OnOwnerChanged.Broadcast(OwningCharacter);
}
