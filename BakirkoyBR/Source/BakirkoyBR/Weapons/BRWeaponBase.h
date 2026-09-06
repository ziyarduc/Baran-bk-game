#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Data/BRTypes.h"

class USkeletalMeshComponent;
class ABRCharacter;
class UParticleSystem;
class UNiagaraSystem;
class USoundBase;

#include "BRWeaponBase.generated.h"

UENUM(BlueprintType)
enum class EBRWeaponState : uint8
{
	Idle        UMETA(DisplayName = "Idle"),
	Firing      UMETA(DisplayName = "Firing"),
	Reloading   UMETA(DisplayName = "Reloading"),
	OutOfAmmo   UMETA(DisplayName = "Out Of Ammo")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnWeaponAmmoChanged, int32, CurrentAmmo, int32, ReserveAmmo);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnWeaponStateChanged, EBRWeaponState, NewState, EBRWeaponState, OldState);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnWeaponOwnerChanged, ABRCharacter*, NewOwner);

UCLASS(Abstract)
class BAKIRKOYBR_API ABRWeaponBase : public AActor
{
	GENERATED_BODY()

public:
	ABRWeaponBase();

	UPROPERTY(BlueprintAssignable, Category = "Weapon|Ammo")
	FOnWeaponAmmoChanged OnAmmoChanged;

	UPROPERTY(BlueprintAssignable, Category = "Weapon|State")
	FOnWeaponStateChanged OnWeaponStateChanged;

	UPROPERTY(BlueprintAssignable, Category = "Weapon|Owner")
	FOnWeaponOwnerChanged OnOwnerChanged;

	virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

	// State and ammo queries
	UFUNCTION(BlueprintPure, Category = "Weapon")
	EBRWeaponState GetCurrentState() const { return CurrentState; }

	UFUNCTION(BlueprintPure, Category = "Weapon")
	int32 GetCurrentAmmo() const { return CurrentAmmo; }

	UFUNCTION(BlueprintPure, Category = "Weapon")
	int32 GetReserveAmmo() const { return ReserveAmmo; }

	UFUNCTION(BlueprintPure, Category = "Weapon")
	int32 GetMagSize() const { return MagSize; }

	UFUNCTION(BlueprintPure, Category = "Weapon")
	bool CanFire() const;

	UFUNCTION(BlueprintPure, Category = "Weapon")
	bool CanReload() const;

	UFUNCTION(BlueprintPure, Category = "Weapon")
	ABRCharacter* GetOwningCharacter() const { return OwningCharacter.Get(); }

	// Equip / Holster Interface
	UFUNCTION(BlueprintCallable, Category = "Weapon")
	virtual void Equip(ABRCharacter* InCharacter);

	UFUNCTION(BlueprintCallable, Category = "Weapon")
	virtual void Holster();

	// Firing controls
	UFUNCTION(BlueprintCallable, Category = "Weapon")
	virtual void StartFire();

	UFUNCTION(BlueprintCallable, Category = "Weapon")
	virtual void StopFire();

	UFUNCTION(BlueprintCallable, Category = "Weapon")
	virtual void Reload();

	// Primary firing logic implemented by derived classes
	virtual void Fire();

	// Muzzle transform helpers
	UFUNCTION(BlueprintPure, Category = "Weapon")
	FVector GetMuzzleLocation() const;

	UFUNCTION(BlueprintPure, Category = "Weapon")
	FVector GetMuzzleDirection() const;

	UFUNCTION(BlueprintPure, Category = "Weapon")
	USkeletalMeshComponent* GetWeaponMesh() const { return WeaponMesh.Get(); }

	UFUNCTION(BlueprintCallable, Category = "Weapon|Cosmetics")
	virtual void PlayMuzzleEffects();

protected:
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	// Server RPCs with validation for authoritative actions
	UFUNCTION(Server, Reliable, WithValidation)
	void Server_StartFire();

	UFUNCTION(Server, Reliable, WithValidation)
	void Server_StopFire();

	UFUNCTION(Server, Reliable, WithValidation)
	void Server_Reload();

	// Internal state transition helpers
	void SetWeaponState(EBRWeaponState NewState);
	virtual void HandleFiring();
	virtual void FinishReload();

	// Replication callbacks
	UFUNCTION()
	virtual void OnRep_CurrentAmmo(int32 OldAmmo);

	UFUNCTION()
	virtual void OnRep_ReserveAmmo(int32 OldReserve);

	UFUNCTION()
	virtual void OnRep_CurrentState(EBRWeaponState OldState);

	UFUNCTION()
	virtual void OnRep_OwningCharacter(ABRCharacter* OldCharacter);

protected:
	// Weapon visual mesh
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USkeletalMeshComponent> WeaponMesh;

	// Owning character reference
	UPROPERTY(ReplicatedUsing = OnRep_OwningCharacter, BlueprintReadOnly, Category = "Weapon|Owner")
	TObjectPtr<ABRCharacter> OwningCharacter;

	// Replicated weapon state
	UPROPERTY(ReplicatedUsing = OnRep_CurrentState, BlueprintReadOnly, Category = "Weapon|State")
	EBRWeaponState CurrentState;

	// Replicated ammo counters
	UPROPERTY(ReplicatedUsing = OnRep_CurrentAmmo, BlueprintReadOnly, Category = "Weapon|Ammo")
	int32 CurrentAmmo;

	UPROPERTY(ReplicatedUsing = OnRep_ReserveAmmo, BlueprintReadOnly, Category = "Weapon|Ammo")
	int32 ReserveAmmo;

	// Weapon configuration properties
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Config")
	EBRWeaponType WeaponType;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Config")
	int32 MagSize;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Config")
	float FireRate;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Config")
	float ReloadTime;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Config")
	float BaseDamage;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Config")
	float HeadshotMultiplier;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Sockets")
	FName MuzzleSocketName;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Sockets")
	FName AttachSocketName;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Sockets")
	FName HolsterSocketName;

	// Cosmetic Effects
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Cosmetics")
	TObjectPtr<UParticleSystem> MuzzleFlashFX;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Cosmetics")
	TObjectPtr<UNiagaraSystem> NiagaraMuzzleFlashFX;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|Cosmetics")
	TObjectPtr<USoundBase> FireSound;

	// Timer handles
	FTimerHandle TimerHandle_HandleFiring;
	FTimerHandle TimerHandle_Reload;

	float LastFireTime;
};
