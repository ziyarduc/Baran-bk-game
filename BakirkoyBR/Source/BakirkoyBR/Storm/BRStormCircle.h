#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
class UStaticMeshComponent;
class UNiagaraComponent;
#include "BRStormCircle.generated.h"

USTRUCT(BlueprintType)
struct FBRStormPhaseConfig
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Storm")
    int32 PhaseIndex = 0;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Storm")
    float SafeZoneRadius = 15000.f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Storm")
    float WaitDuration = 45.f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Storm")
    float ShrinkDuration = 30.f;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Storm")
    float DamagePerSecond = 2.f;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnStormPhaseChanged, int32, NewPhase);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnStormDamageDealt, AActor*, TargetActor, float, DamageApplied);

UCLASS()
class BAKIRKOYBR_API ABRStormCircle : public AActor
{
    GENERATED_BODY()

public:
    ABRStormCircle();

    virtual void Tick(float DeltaSeconds) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UFUNCTION(BlueprintPure, Category = "Storm")
    FVector2D GetCurrentCenter() const { return CurrentCenter; }

    UFUNCTION(BlueprintPure, Category = "Storm")
    FVector2D GetTargetCenter() const { return TargetCenter; }

    UFUNCTION(BlueprintPure, Category = "Storm")
    float GetCurrentRadius() const { return CurrentRadius; }

    UFUNCTION(BlueprintPure, Category = "Storm")
    float GetTargetRadius() const { return TargetRadius; }

    UFUNCTION(BlueprintPure, Category = "Storm")
    int32 GetCurrentPhase() const { return CurrentPhaseIndex; }

    UFUNCTION(BlueprintPure, Category = "Storm")
    bool IsShrinking() const { return bIsShrinking; }

    UFUNCTION(BlueprintPure, Category = "Storm")
    float GetDamagePerSecond() const { return DamagePerSecond; }

    UFUNCTION(BlueprintPure, Category = "Storm")
    float GetRemainingPhaseTime() const { return PhaseTimer; }

    UFUNCTION(BlueprintPure, Category = "Storm")
    bool IsLocationInsideSafeZone(const FVector& TestLocation) const;

    UFUNCTION(BlueprintPure, Category = "Storm")
    float GetDistanceToSafeZone(const FVector& TestLocation) const;

    UFUNCTION(BlueprintCallable, Category = "Storm")
    void StartStormSequence();

    UFUNCTION(BlueprintCallable, Category = "Storm")
    void AdvanceToNextPhase();

    UPROPERTY(BlueprintAssignable, Category = "Storm")
    FOnStormPhaseChanged OnStormPhaseChanged;

    UPROPERTY(BlueprintAssignable, Category = "Storm")
    FOnStormDamageDealt OnStormDamageDealt;

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<USceneComponent> SceneRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<UStaticMeshComponent> StormMeshComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    TObjectPtr<UNiagaraComponent> StormNiagaraComponent;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Storm|Visuals")
    float MeshBaseRadius = 100.f;

    UFUNCTION(BlueprintCallable, Category = "Storm|Visuals")
    void UpdateStormVisuals();

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Storm|Config")
    TArray<FBRStormPhaseConfig> StormPhases;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Storm|Config")
    float DamageTickInterval = 1.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Storm|Config")
    float MaxPlayAreaRadius = 25000.f;

    UPROPERTY(ReplicatedUsing = OnRep_CurrentCenter, BlueprintReadOnly, Category = "Storm|State")
    FVector2D CurrentCenter = FVector2D::ZeroVector;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Storm|State")
    FVector2D TargetCenter = FVector2D::ZeroVector;

    UPROPERTY(ReplicatedUsing = OnRep_CurrentRadius, BlueprintReadOnly, Category = "Storm|State")
    float CurrentRadius = 25000.f;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Storm|State")
    float TargetRadius = 25000.f;

    UPROPERTY(ReplicatedUsing = OnRep_CurrentPhaseIndex, BlueprintReadOnly, Category = "Storm|State")
    int32 CurrentPhaseIndex = 0;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Storm|State")
    bool bIsShrinking = false;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Storm|State")
    float DamagePerSecond = 1.f;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Storm|State")
    float PhaseTimer = 0.f;

    UFUNCTION()
    void OnRep_CurrentCenter();

    UFUNCTION()
    void OnRep_CurrentRadius();

    UFUNCTION()
    void OnRep_CurrentPhaseIndex();

private:
    void SetupDefaultPhases();
    void CalculateNextSafeZone();
    void ApplyDamageTick();

    float ShrinkDuration = 30.f;
    float ShrinkProgress = 0.f;
    FVector2D ShrinkStartCenter = FVector2D::ZeroVector;
    float ShrinkStartRadius = 25000.f;
    float DamageAccumulator = 0.f;
};
