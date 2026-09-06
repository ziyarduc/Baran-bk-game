#pragma once

#include "CoreMinimal.h"
#include "Character/BRCharacter.h"
#include "Data/BRTypes.h"
class UBRHealthComponent;
class ABRAIController;
class AController;
#include "BRAIBotCharacter.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnBRAIBotEliminated, ABRAIBotCharacter*, EliminatedBot, AController*, Killer);

/**
 * ABRAIBotCharacter
 *
 * Dedicated AI Bot Character for Bakırköy BR Demo 1 Playable MVP.
 * Integrates:
 * - ABRCharacter inheritance
 * - UBRHealthComponent integration with elimination handling
 * - Server-authoritative Hit-Scan & Projectile weapon firing trigger
 * - Natural cover crouch and stance support
 */
UCLASS()
class BAKIRKOYBR_API ABRAIBotCharacter : public ABRCharacter
{
    GENERATED_BODY()

public:
    ABRAIBotCharacter();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    // ── Server-Authoritative Weapon Trigger (C3, C6) ──
    UFUNCTION(BlueprintCallable, Category = "AI|Combat")
    void TriggerWeaponFire(const FVector& TargetLocation);

    UFUNCTION(Server, Reliable, WithValidation, Category = "AI|Combat")
    void Server_FireWeapon(const FVector& TargetLocation);

    // ── Natural Cover Stance (MVP M4) ──
    UFUNCTION(BlueprintCallable, Category = "AI|Cover")
    void SetCoverCrouch(bool bShouldCrouch);

    UFUNCTION(BlueprintPure, Category = "AI|Combat")
    bool IsEliminated() const { return bIsEliminated; }

    UPROPERTY(BlueprintAssignable, Category = "AI|Events")
    FOnBRAIBotEliminated OnBotEliminatedEvent;

protected:
    // ── Health Component Event Handlers ──
    UFUNCTION()
    void HandleElimination(AController* Killer);

    UFUNCTION()
    void HandleHealthChanged(float NewHealth, float NewShield, const FBRDamageInfo& DamageInfo);

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|State")
    bool bIsEliminated = false;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "AI|Combat")
    float HitScanRange = 10000.0f; // 100m trace distance

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "AI|Combat")
    float HitScanBaseDamage = 30.0f; // Assault Rifle ~30 per bullet (MVP M2)

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "AI|Combat")
    float WeaponSpreadAngle = 2.0f; // Cone spread in degrees
};
