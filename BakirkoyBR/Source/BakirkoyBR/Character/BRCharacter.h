#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Data/BRTypes.h"
#include "EnhancedInputComponent.h"
#include "BRCharacter.generated.h"

class UBRHealthComponent;
class ABRWeaponBase;
class UBRBuildingComponent;
class UBRSkydiveComponent;
class UBRInputConfig;
class UInputMappingContext;
struct FInputActionValue;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnWeaponEquipped, ABRWeaponBase*, NewWeapon);

UCLASS()
class BAKIRKOYBR_API ABRCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    ABRCharacter();

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void PawnClientRestart() override;

    // Health
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<UBRHealthComponent> HealthComponent;

    // Building
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<UBRBuildingComponent> BuildingComponent;

    // Input Configuration
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UBRInputConfig> InputConfig;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Input")
    TObjectPtr<UInputMappingContext> DefaultMappingContext;

    // Weapons
    UFUNCTION(BlueprintCallable, Category = "Weapons")
    void EquipWeapon(int32 SlotIndex);

    UFUNCTION(BlueprintCallable, Category = "Weapons")
    ABRWeaponBase* GetCurrentWeapon() const;

    UPROPERTY(BlueprintAssignable, Category = "Weapons")
    FOnWeaponEquipped OnWeaponEquipped;

    // Combat / ADS
    UFUNCTION(BlueprintCallable, Category = "Combat")
    void SetADS(bool bNewADS);

    UFUNCTION(Server, Reliable, WithValidation)
    void ServerSetADS(bool bNewADS);

    // Movement State
    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Movement")
    EBRMovementState CurrentMovementState = EBRMovementState::Idle;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Combat")
    bool bIsADS = false;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Combat")
    int32 ActiveWeaponSlot = 0;

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    // Enhanced Input Action Handlers
    void Input_Move(const FInputActionValue& Value);
    void Input_Look(const FInputActionValue& Value);
    void Input_Jump_Started();
    void Input_Jump_Completed();
    void Input_Fire_Started();
    void Input_Fire_Completed();
    void Input_Reload();
    void Input_ADS_Started();
    void Input_ADS_Completed();

    UPROPERTY()
    TArray<TObjectPtr<ABRWeaponBase>> WeaponSlots;
};
