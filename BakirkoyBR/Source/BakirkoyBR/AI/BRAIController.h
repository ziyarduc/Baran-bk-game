#pragma once

#include "CoreMinimal.h"
#include "AIController.h"
#include "Perception/AIPerceptionTypes.h"
#include "Data/BRTypes.h"
class UAIPerceptionComponent;
class UAISenseConfig_Sight;
class UAISenseConfig_Hearing;
class ABRAIBotCharacter;
class AActor;
#include "BRAIController.generated.h"

/**
 * AI Decision State for Bakırköy BR Demo 1 Playable MVP
 */
UENUM(BlueprintType)
enum class EBRAIState : uint8
{
    Idle                UMETA(DisplayName = "Idle"),
    LootSeeking         UMETA(DisplayName = "Loot Seeking"),
    CombatEngagement    UMETA(DisplayName = "Combat Engagement"),
    CoverSeeking        UMETA(DisplayName = "Cover Seeking"),
    Wandering           UMETA(DisplayName = "Wandering / Zone Move")
};

/**
 * Natural Cover Point candidate struct
 */
USTRUCT(BlueprintType)
struct FBRAICoverPoint
{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Cover")
    FVector Location = FVector::ZeroVector;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Cover")
    FVector CoverNormal = FVector::ForwardVector;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Cover")
    float CoverScore = 0.0f;
};

/**
 * ABRAIController
 *
 * Dedicated AI Controller for Bakırköy BR Demo 1 Playable MVP.
 * Enforces:
 * - Exactly 10 bots scenario limit (MAX_BOT_COUNT = 10)
 * - UAIPerceptionComponent with Sight (120 deg FOV, 80m open range) and Hearing
 * - State Machine: LootSeeking, CombatEngagement, CoverSeeking, Wandering / ZoneMove
 * - Natural cover usage (vehicles, exterior street walls, corners)
 * - Strict Constraint Check: NEVER enter buildings (exterior street and rooftop NavMesh goals only)
 */
UCLASS()
class BAKIRKOYBR_API ABRAIController : public AAIController
{
    GENERATED_BODY()

public:
    ABRAIController();

    // ── Constant: Exactly 10 Bots MVP Limit ──
    static constexpr int32 MAX_BOT_COUNT = 10;

    // Active AI bot registry count
    static int32 ActiveBotCount;
    static int32 GetActiveBotCount() { return ActiveBotCount; }
    static bool CanSpawnBot() { return ActiveBotCount < MAX_BOT_COUNT; }

    virtual void OnPossess(APawn* InPawn) override;
    virtual void OnUnPossess() override;
    virtual void Tick(float DeltaTime) override;

    // ── State Machine & Decision Logic ──
    UFUNCTION(BlueprintPure, Category = "AI|State")
    EBRAIState GetCurrentAIState() const { return CurrentState; }

    UFUNCTION(BlueprintCallable, Category = "AI|State")
    void SetAIState(EBRAIState NewState);

    // ── Target & Combat ──
    UFUNCTION(BlueprintPure, Category = "AI|Combat")
    AActor* GetTargetActor() const;

    UFUNCTION(BlueprintCallable, Category = "AI|Combat")
    void SetTargetActor(AActor* NewTarget);

    UFUNCTION(BlueprintCallable, Category = "AI|Combat")
    void ExecuteCombatEngagement();

    // ── Loot Seeking ──
    UFUNCTION(BlueprintCallable, Category = "AI|Loot")
    AActor* FindNearestLoot(FVector& OutLootLocation);

    UFUNCTION(BlueprintCallable, Category = "AI|Loot")
    void ExecuteLootSeeking();

    // ── Wandering & Navigation ──
    UFUNCTION(BlueprintCallable, Category = "AI|Navigation")
    void ExecuteWandering();

    // ── Strict Constraint Check: NEVER enter buildings (C1, M5) ──
    /**
     * Strict Constraint Check: Validates that a candidate location is strictly outdoors.
     * Rejects any point inside building interiors or beneath indoor ceilings.
     * Goals must be exterior street, alley, or rooftop positions only.
     */
    UFUNCTION(BlueprintCallable, Category = "AI|Navigation")
    bool IsExteriorLocation(const FVector& Location) const;

    UFUNCTION(BlueprintCallable, Category = "AI|Navigation")
    bool GetRandomExteriorNavLocation(float Radius, FVector& OutNavLocation) const;

    // ── Natural Cover Logic (MVP M4: Building Paused) ──
    UFUNCTION(BlueprintCallable, Category = "AI|Cover")
    bool FindNaturalCoverLocation(const FVector& ThreatLocation, FVector& OutCoverLocation);

    UFUNCTION(BlueprintCallable, Category = "AI|Cover")
    void ExecuteCoverSeeking();

protected:
    virtual void BeginPlay() override;

    // ── Perception Component & Senses ──
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Perception")
    TObjectPtr<UAIPerceptionComponent> AIPerceptionComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Perception")
    TObjectPtr<UAISenseConfig_Sight> SightConfig;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Perception")
    TObjectPtr<UAISenseConfig_Hearing> HearingConfig;

    UFUNCTION()
    void OnTargetPerceptionUpdated(AActor* Actor, FAIStimulus Stimulus);

    // ── State Machine Properties ──
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|State")
    EBRAIState CurrentState = EBRAIState::Idle;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Combat")
    TObjectPtr<AActor> CurrentTargetActor = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Loot")
    TObjectPtr<AActor> CurrentLootActor = nullptr;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Combat")
    float EngagementRange = 5000.0f; // 50m effective engagement range

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Combat")
    float FireCooldownTimer = 0.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "AI|Combat")
    float FireInterval = 0.15f; // AR fire rate interval

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Navigation")
    FVector CurrentNavGoal = FVector::ZeroVector;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Cover")
    FVector CurrentCoverLocation = FVector::ZeroVector;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|Cover")
    bool bIsInCover = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI|State")
    float StateEvaluationTimer = 0.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "AI|State")
    float StateEvaluationInterval = 0.2f; // 5 Hz evaluation rate

private:
    void EvaluateDecisionLogic();
    bool HasEquippedWeapon() const;
    void AimAtTarget(const FVector& TargetLocation);
};
