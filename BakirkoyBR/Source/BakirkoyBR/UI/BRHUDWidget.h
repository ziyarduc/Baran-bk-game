#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Data/BRTypes.h"
#include "BRHUDWidget.generated.h"

class UProgressBar;
class UTextBlock;
class ABRCharacter;
class UBRHealthComponent;
class ABRWeaponBase;
class ABRStormCircle;

/**
 * UBRHUDWidget
 * 
 * Minimal HUD UserWidget for Bakırköy: Son Çember Battle Royale.
 * Displays:
 * - Health Bar (0-100)
 * - Shield Bar (0-100)
 * - Ammo Counter (Current / Reserve)
 * - Storm Timer and Phase status
 *
 * Automatically binds to the owning player's UBRHealthComponent and active ABRWeaponBase
 * in NativeConstruct, while also providing Blueprint-callable update functions and
 * Blueprint-implementable event hooks.
 */
UCLASS()
class BAKIRKOYBR_API UBRHUDWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	UBRHUDWidget(const FObjectInitializer& ObjectInitializer);

	virtual void NativeConstruct() override;
	virtual void NativeDestruct() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

	// ------------------------------------------------------------------
	// Binding Methods
	// ------------------------------------------------------------------

	/** Binds this HUD to a player character and its health/weapon delegates. */
	UFUNCTION(BlueprintCallable, Category = "HUD|Binding")
	void BindToCharacter(ABRCharacter* InCharacter);

	/** Unbinds all delegates from the currently bound character. */
	UFUNCTION(BlueprintCallable, Category = "HUD|Binding")
	void UnbindFromCharacter();

	/** Binds to a specific health component for health and shield updates. */
	UFUNCTION(BlueprintCallable, Category = "HUD|Binding")
	void BindToHealthComponent(UBRHealthComponent* InHealthComp);

	/** Unbinds from the currently tracked health component. */
	UFUNCTION(BlueprintCallable, Category = "HUD|Binding")
	void UnbindFromHealthComponent();

	/** Binds to an active weapon for ammo updates. */
	UFUNCTION(BlueprintCallable, Category = "HUD|Binding")
	void BindToWeapon(ABRWeaponBase* InWeapon);

	/** Unbinds from the active weapon. */
	UFUNCTION(BlueprintCallable, Category = "HUD|Binding")
	void UnbindFromWeapon();

	/** Discovers and binds to the active storm circle actor in the world. */
	UFUNCTION(BlueprintCallable, Category = "HUD|Binding")
	void BindToStorm();

	// ------------------------------------------------------------------
	// Manual / Blueprint Update Functions
	// ------------------------------------------------------------------

	/** Updates the health value and refreshes UI widgets/events. */
	UFUNCTION(BlueprintCallable, Category = "HUD|Health")
	void UpdateHealth(float NewHealth, float InMaxHealth = 100.f);

	/** Updates the shield value and refreshes UI widgets/events. */
	UFUNCTION(BlueprintCallable, Category = "HUD|Shield")
	void UpdateShield(float NewShield, float InMaxShield = 100.f);

	/** Updates ammo counters and refreshes UI widgets/events. */
	UFUNCTION(BlueprintCallable, Category = "HUD|Ammo")
	void UpdateAmmo(int32 InCurrentAmmo, int32 InReserveAmmo);

	/** Updates storm phase, timer, and shrinking status. */
	UFUNCTION(BlueprintCallable, Category = "HUD|Storm")
	void UpdateStormInfo(int32 InPhase, float InRemainingTime, bool bInShrinking);

	// ------------------------------------------------------------------
	// Blueprint Pure Getters
	// ------------------------------------------------------------------

	UFUNCTION(BlueprintPure, Category = "HUD|Health")
	float GetHealthPercent() const { return HealthPercent; }

	UFUNCTION(BlueprintPure, Category = "HUD|Health")
	float GetCurrentHealth() const { return CurrentHealth; }

	UFUNCTION(BlueprintPure, Category = "HUD|Health")
	float GetMaxHealth() const { return MaxHealth; }

	UFUNCTION(BlueprintPure, Category = "HUD|Shield")
	float GetShieldPercent() const { return ShieldPercent; }

	UFUNCTION(BlueprintPure, Category = "HUD|Shield")
	float GetCurrentShield() const { return CurrentShield; }

	UFUNCTION(BlueprintPure, Category = "HUD|Shield")
	float GetMaxShield() const { return MaxShield; }

	UFUNCTION(BlueprintPure, Category = "HUD|Ammo")
	int32 GetCurrentAmmo() const { return CurrentAmmo; }

	UFUNCTION(BlueprintPure, Category = "HUD|Ammo")
	int32 GetReserveAmmo() const { return ReserveAmmo; }

	/** Formatted ammo string, e.g. "30 / 120" */
	UFUNCTION(BlueprintPure, Category = "HUD|Ammo")
	FText GetAmmoText() const;

	UFUNCTION(BlueprintPure, Category = "HUD|Storm")
	int32 GetCurrentStormPhase() const { return CurrentStormPhase; }

	UFUNCTION(BlueprintPure, Category = "HUD|Storm")
	float GetStormRemainingTime() const { return StormRemainingTime; }

	UFUNCTION(BlueprintPure, Category = "HUD|Storm")
	bool IsStormShrinking() const { return bIsStormShrinking; }

	/** Formatted storm timer string, e.g. "01:45" */
	UFUNCTION(BlueprintPure, Category = "HUD|Storm")
	FText GetStormTimerText() const;

	/** Formatted storm phase description, e.g. "Phase 1: Safe Zone Closes In" */
	UFUNCTION(BlueprintPure, Category = "HUD|Storm")
	FText GetStormPhaseText() const;

protected:
	// ------------------------------------------------------------------
	// Blueprint-Bindable State Variables
	// ------------------------------------------------------------------

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD|Health")
	float CurrentHealth = 100.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD|Health")
	float MaxHealth = 100.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD|Health")
	float HealthPercent = 1.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD|Shield")
	float CurrentShield = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD|Shield")
	float MaxShield = 100.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD|Shield")
	float ShieldPercent = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD|Ammo")
	int32 CurrentAmmo = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD|Ammo")
	int32 ReserveAmmo = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD|Storm")
	int32 CurrentStormPhase = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD|Storm")
	float StormRemainingTime = 0.f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "HUD|Storm")
	bool bIsStormShrinking = false;

	// ------------------------------------------------------------------
	// Optional Named UMG Widget Bindings (meta = BindWidgetOptional)
	// ------------------------------------------------------------------

	UPROPERTY(meta = (BindWidgetOptional), BlueprintReadOnly, Category = "HUD|Widgets")
	TObjectPtr<UProgressBar> HealthProgressBar;

	UPROPERTY(meta = (BindWidgetOptional), BlueprintReadOnly, Category = "HUD|Widgets")
	TObjectPtr<UProgressBar> ShieldProgressBar;

	UPROPERTY(meta = (BindWidgetOptional), BlueprintReadOnly, Category = "HUD|Widgets")
	TObjectPtr<UTextBlock> HealthText;

	UPROPERTY(meta = (BindWidgetOptional), BlueprintReadOnly, Category = "HUD|Widgets")
	TObjectPtr<UTextBlock> ShieldText;

	UPROPERTY(meta = (BindWidgetOptional), BlueprintReadOnly, Category = "HUD|Widgets")
	TObjectPtr<UTextBlock> AmmoCurrentText;

	UPROPERTY(meta = (BindWidgetOptional), BlueprintReadOnly, Category = "HUD|Widgets")
	TObjectPtr<UTextBlock> AmmoReserveText;

	UPROPERTY(meta = (BindWidgetOptional), BlueprintReadOnly, Category = "HUD|Widgets")
	TObjectPtr<UTextBlock> AmmoTextWidget;

	UPROPERTY(meta = (BindWidgetOptional), BlueprintReadOnly, Category = "HUD|Widgets")
	TObjectPtr<UTextBlock> StormTimerTextWidget;

	UPROPERTY(meta = (BindWidgetOptional), BlueprintReadOnly, Category = "HUD|Widgets")
	TObjectPtr<UTextBlock> StormPhaseTextWidget;

	// ------------------------------------------------------------------
	// Blueprint Implementable Events
	// ------------------------------------------------------------------

	/** Fired whenever health changes. Override in Blueprint to drive custom animations/audio. */
	UFUNCTION(BlueprintImplementableEvent, Category = "HUD|Events")
	void OnHealthUpdated(float NewHealth, float InMaxHealth, float InPercent);

	/** Fired whenever shield changes. Override in Blueprint to drive custom animations/audio. */
	UFUNCTION(BlueprintImplementableEvent, Category = "HUD|Events")
	void OnShieldUpdated(float NewShield, float InMaxShield, float InPercent);

	/** Fired whenever weapon ammo counters change. */
	UFUNCTION(BlueprintImplementableEvent, Category = "HUD|Events")
	void OnAmmoUpdated(int32 InCurrentAmmo, int32 InReserveAmmo);

	/** Fired whenever storm timer or phase updates. */
	UFUNCTION(BlueprintImplementableEvent, Category = "HUD|Events")
	void OnStormInfoUpdated(int32 InPhase, float RemainingTime, bool bShrinking);

	// ------------------------------------------------------------------
	// Delegate Handlers
	// ------------------------------------------------------------------

	UFUNCTION()
	void HandleHealthChanged(float NewHealth, float NewShield, const FBRDamageInfo& DamageInfo);

	UFUNCTION()
	void HandleWeaponEquipped(ABRWeaponBase* NewWeapon);

	UFUNCTION()
	void HandleAmmoChanged(int32 InCurrentAmmo, int32 InReserveAmmo);

	UFUNCTION()
	void HandleStormPhaseChanged(int32 NewPhase);

private:
	void UpdateStormFromWorld();

	UPROPERTY()
	TWeakObjectPtr<ABRCharacter> BoundCharacter;

	UPROPERTY()
	TWeakObjectPtr<UBRHealthComponent> BoundHealthComponent;

	UPROPERTY()
	TWeakObjectPtr<ABRWeaponBase> BoundWeapon;

	UPROPERTY()
	TWeakObjectPtr<ABRStormCircle> CachedStormCircle;
};
