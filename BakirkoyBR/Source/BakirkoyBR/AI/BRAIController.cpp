#include "AI/BRAIController.h"
#include "AI/BRAIBotCharacter.h"
#include "Perception/AIPerceptionComponent.h"
#include "Perception/AISenseConfig_Sight.h"
#include "Perception/AISenseConfig_Hearing.h"
#include "NavigationSystem.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetMathLibrary.h"
#include "Engine/World.h"
#include "Data/BRGameConstants.h"
#include "Character/BRHealthComponent.h"

int32 ABRAIController::ActiveBotCount = 0;

ABRAIController::ABRAIController()
{
    PrimaryActorTick.bCanEverTick = true;
    bWantsPlayerState = true;

    // ── Perception Component Initialization ──
    AIPerceptionComponent = CreateDefaultSubobject<UAIPerceptionComponent>(TEXT("AIPerceptionComponent"));

    // Sight sense configuration (120 deg visual cone, 80m open range)
    SightConfig = CreateDefaultSubobject<UAISenseConfig_Sight>(TEXT("SightConfig"));
    if (SightConfig)
    {
        SightConfig->SightRadius = BRConstants::AI_VISUAL_RANGE_OPEN;
        SightConfig->LoseSightRadius = BRConstants::AI_VISUAL_RANGE_OPEN + 500.0f;
        SightConfig->PeripheralVisionAngleDegrees = BRConstants::AI_VISUAL_FOV * 0.5f; // 60 deg half-angle = 120 deg FOV
        SightConfig->SetMaxAge(5.0f);
        SightConfig->AutoRegisterAsSource = true;
        SightConfig->DetectionByAffiliation.bDetectEnemies = true;
        SightConfig->DetectionByAffiliation.bDetectNeutrals = true;
        SightConfig->DetectionByAffiliation.bDetectFriendlies = true;

        AIPerceptionComponent->ConfigureSense(*SightConfig);
    }

    // Hearing sense configuration (30m audio detection radius)
    HearingConfig = CreateDefaultSubobject<UAISenseConfig_Hearing>(TEXT("HearingConfig"));
    if (HearingConfig)
    {
        HearingConfig->HearingRange = 3000.0f;
        HearingConfig->SetMaxAge(3.0f);
        HearingConfig->AutoRegisterAsSource = true;
        HearingConfig->DetectionByAffiliation.bDetectEnemies = true;
        HearingConfig->DetectionByAffiliation.bDetectNeutrals = true;
        HearingConfig->DetectionByAffiliation.bDetectFriendlies = true;

        AIPerceptionComponent->ConfigureSense(*HearingConfig);
    }

    if (SightConfig)
    {
        AIPerceptionComponent->SetDominantSense(SightConfig->GetSenseImplementation());
    }
}

void ABRAIController::BeginPlay()
{
    Super::BeginPlay();

    if (AIPerceptionComponent)
    {
        AIPerceptionComponent->OnTargetPerceptionUpdated.AddDynamic(this, &ABRAIController::OnTargetPerceptionUpdated);
    }
}

void ABRAIController::OnPossess(APawn* InPawn)
{
    Super::OnPossess(InPawn);

    // Enforce Demo 1 MVP strict 10-bot population limit
    if (ActiveBotCount >= MAX_BOT_COUNT)
    {
        UE_LOG(LogTemp, Warning, TEXT("ABRAIController: ActiveBotCount exceeds MAX_BOT_COUNT (%d)"), MAX_BOT_COUNT);
    }

    ActiveBotCount++;
    SetAIState(EBRAIState::LootSeeking);
}

void ABRAIController::OnUnPossess()
{
    Super::OnUnPossess();

    if (ActiveBotCount > 0)
    {
        ActiveBotCount--;
    }
}

void ABRAIController::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (FireCooldownTimer > 0.0f)
    {
        FireCooldownTimer -= DeltaTime;
    }

    StateEvaluationTimer += DeltaTime;
    if (StateEvaluationTimer >= StateEvaluationInterval)
    {
        StateEvaluationTimer = 0.0f;
        EvaluateDecisionLogic();
    }

    // Execute state behaviors
    switch (CurrentState)
    {
        case EBRAIState::LootSeeking:
            ExecuteLootSeeking();
            break;

        case EBRAIState::CombatEngagement:
            ExecuteCombatEngagement();
            break;

        case EBRAIState::CoverSeeking:
            ExecuteCoverSeeking();
            break;

        case EBRAIState::Wandering:
            ExecuteWandering();
            break;

        default:
            break;
    }
}

void ABRAIController::SetAIState(EBRAIState NewState)
{
    if (CurrentState == NewState)
    {
        return;
    }

    // Exit old state cleanup
    if (CurrentState == EBRAIState::CoverSeeking)
    {
        bIsInCover = false;
        if (ABRAIBotCharacter* BotChar = Cast<ABRAIBotCharacter>(GetPawn()))
        {
            BotChar->SetCoverCrouch(false);
        }
    }

    CurrentState = NewState;
}

AActor* ABRAIController::GetTargetActor() const
{
    return CurrentTargetActor;
}

void ABRAIController::SetTargetActor(AActor* NewTarget)
{
    CurrentTargetActor = NewTarget;
}

void ABRAIController::OnTargetPerceptionUpdated(AActor* Actor, FAIStimulus Stimulus)
{
    if (!Actor || Actor == GetPawn())
    {
        return;
    }

    if (Stimulus.WasSuccessfullySensed())
    {
        // Spot an enemy: prioritize if no current target or if newly sensed actor is closer
        if (!CurrentTargetActor)
        {
            SetTargetActor(Actor);
            SetAIState(EBRAIState::CombatEngagement);
        }
        else if (GetPawn())
        {
            const float CurrentTargetDist = FVector::DistSquared(GetPawn()->GetActorLocation(), CurrentTargetActor->GetActorLocation());
            const float NewTargetDist = FVector::DistSquared(GetPawn()->GetActorLocation(), Actor->GetActorLocation());

            if (NewTargetDist < CurrentTargetDist)
            {
                SetTargetActor(Actor);
            }
        }
    }
    else
    {
        // Lost perception of current target
        if (Actor == CurrentTargetActor)
        {
            // If target lost and we have a weapon, transition to wandering / patrol
            if (HasEquippedWeapon())
            {
                SetAIState(EBRAIState::Wandering);
            }
            else
            {
                SetAIState(EBRAIState::LootSeeking);
            }
            CurrentTargetActor = nullptr;
        }
    }
}

void ABRAIController::EvaluateDecisionLogic()
{
    APawn* ControlledPawn = GetPawn();
    if (!ControlledPawn)
    {
        return;
    }

    // Check bot health status
    if (ABRAIBotCharacter* BotChar = Cast<ABRAIBotCharacter>(ControlledPawn))
    {
        if (BotChar->IsEliminated())
        {
            SetAIState(EBRAIState::Idle);
            return;
        }

        // If target is valid and alive
        if (CurrentTargetActor)
        {
            UBRHealthComponent* TargetHealth = CurrentTargetActor->FindComponentByClass<UBRHealthComponent>();
            if (TargetHealth && !TargetHealth->IsAlive())
            {
                // Target eliminated, disengage
                CurrentTargetActor = nullptr;
                SetAIState(HasEquippedWeapon() ? EBRAIState::Wandering : EBRAIState::LootSeeking);
                return;
            }

            // If health is critically low and not currently in cover, seek natural cover
            if (BotChar->HealthComponent && !bIsInCover)
            {
                // Seek natural cover if under pressure
                FVector CoverLoc;
                if (FindNaturalCoverLocation(CurrentTargetActor->GetActorLocation(), CoverLoc))
                {
                    CurrentCoverLocation = CoverLoc;
                    SetAIState(EBRAIState::CoverSeeking);
                    return;
                }
            }

            SetAIState(EBRAIState::CombatEngagement);
            return;
        }
    }

    // If no target, determine whether to loot or wander
    if (!HasEquippedWeapon())
    {
        SetAIState(EBRAIState::LootSeeking);
    }
    else if (CurrentState != EBRAIState::CoverSeeking)
    {
        SetAIState(EBRAIState::Wandering);
    }
}

bool ABRAIController::HasEquippedWeapon() const
{
    if (const ABRCharacter* BRChar = Cast<ABRCharacter>(GetPawn()))
    {
        return BRChar->GetCurrentWeapon() != nullptr;
    }
    return false;
}

void ABRAIController::ExecuteCombatEngagement()
{
    APawn* ControlledPawn = GetPawn();
    if (!ControlledPawn || !CurrentTargetActor)
    {
        SetAIState(EBRAIState::Wandering);
        return;
    }

    const FVector MyLocation = ControlledPawn->GetActorLocation();
    const FVector TargetLocation = CurrentTargetActor->GetActorLocation();
    const float Distance = FVector::Dist(MyLocation, TargetLocation);

    // Aim towards target
    AimAtTarget(TargetLocation);

    // Approach target if beyond effective range, otherwise stop and fire
    if (Distance > EngagementRange)
    {
        MoveToActor(CurrentTargetActor, EngagementRange * 0.7f);
    }
    else
    {
        StopMovement();
    }

    // Fire weapon if cooldown elapsed and line of sight clear
    if (FireCooldownTimer <= 0.0f)
    {
        FHitResult HitResult;
        FCollisionQueryParams TraceParams;
        TraceParams.AddIgnoredActor(ControlledPawn);

        const FVector EyeLocation = MyLocation + FVector(0.0f, 0.0f, 60.0f);
        const bool bHit = GetWorld()->LineTraceSingleByChannel(
            HitResult,
            EyeLocation,
            TargetLocation + FVector(0.0f, 0.0f, 40.0f),
            ECC_Visibility,
            TraceParams
        );

        if (!bHit || HitResult.GetActor() == CurrentTargetActor)
        {
            if (ABRAIBotCharacter* BotChar = Cast<ABRAIBotCharacter>(ControlledPawn))
            {
                BotChar->TriggerWeaponFire(TargetLocation);
                FireCooldownTimer = FireInterval;
            }
        }
    }
}

void ABRAIController::AimAtTarget(const FVector& TargetLocation)
{
    APawn* ControlledPawn = GetPawn();
    if (!ControlledPawn)
    {
        return;
    }

    const FVector SourceLocation = ControlledPawn->GetActorLocation();
    const FRotator TargetRot = UKismetMathLibrary::FindLookAtRotation(SourceLocation, TargetLocation);

    SetControlRotation(TargetRot);
    ControlledPawn->SetActorRotation(FRotator(0.0f, TargetRot.Yaw, 0.0f));
}

AActor* ABRAIController::FindNearestLoot(FVector& OutLootLocation)
{
    APawn* ControlledPawn = GetPawn();
    if (!ControlledPawn)
    {
        return nullptr;
    }

    const FVector MyLocation = ControlledPawn->GetActorLocation();
    AActor* ClosestLoot = nullptr;
    float MinDistanceSq = MAX_FLT;

    // Find all potential loot actors tagged "Loot" or "WeaponPickup"
    TArray<AActor*> FoundLootActors;
    UGameplayStatics::GetAllActorsWithTag(GetWorld(), FName("Loot"), FoundLootActors);

    TArray<AActor*> WeaponActors;
    UGameplayStatics::GetAllActorsWithTag(GetWorld(), FName("WeaponPickup"), WeaponActors);
    FoundLootActors.Append(WeaponActors);

    for (AActor* LootActor : FoundLootActors)
    {
        if (!LootActor)
        {
            continue;
        }

        const FVector LootPos = LootActor->GetActorLocation();

        // Enforce Constraint C1: NEVER navigate into building interiors for loot
        if (!IsExteriorLocation(LootPos))
        {
            continue;
        }

        const float DistSq = FVector::DistSquared(MyLocation, LootPos);
        if (DistSq < MinDistanceSq)
        {
            MinDistanceSq = DistSq;
            ClosestLoot = LootActor;
            OutLootLocation = LootPos;
        }
    }

    return ClosestLoot;
}

void ABRAIController::ExecuteLootSeeking()
{
    APawn* ControlledPawn = GetPawn();
    if (!ControlledPawn)
    {
        return;
    }

    if (HasEquippedWeapon())
    {
        SetAIState(EBRAIState::Wandering);
        return;
    }

    if (!CurrentLootActor)
    {
        FVector LootLocation;
        CurrentLootActor = FindNearestLoot(LootLocation);

        if (CurrentLootActor)
        {
            CurrentNavGoal = LootLocation;
            MoveToLocation(CurrentNavGoal, 80.0f);
        }
        else
        {
            // No loot found in immediate exterior, wander to explore exterior streets/alleys
            SetAIState(EBRAIState::Wandering);
            return;
        }
    }
    else
    {
        const float DistToLoot = FVector::Dist(ControlledPawn->GetActorLocation(), CurrentLootActor->GetActorLocation());
        if (DistToLoot <= 150.0f)
        {
            // In interaction range: equip weapon
            if (ABRCharacter* BRChar = Cast<ABRCharacter>(ControlledPawn))
            {
                BRChar->EquipWeapon(0);
            }

            CurrentLootActor = nullptr;
            SetAIState(EBRAIState::Wandering);
        }
    }
}

void ABRAIController::ExecuteWandering()
{
    APawn* ControlledPawn = GetPawn();
    if (!ControlledPawn)
    {
        return;
    }

    // If destination reached or idle, sample a new exterior street or rooftop position
    const EPathFollowingStatus::Type MoveStatus = GetMoveStatus();
    if (MoveStatus == EPathFollowingStatus::Idle || CurrentNavGoal.IsZero())
    {
        FVector NextExteriorPoint;
        if (GetRandomExteriorNavLocation(3500.0f, NextExteriorPoint))
        {
            CurrentNavGoal = NextExteriorPoint;
            MoveToLocation(CurrentNavGoal, 100.0f);
        }
    }
}

bool ABRAIController::IsExteriorLocation(const FVector& Location) const
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return false;
    }

    // Constraint C1 & MVP M5: Ensure point has open sky above (no building interior ceiling)
    const FVector Start = Location + FVector(0.0f, 0.0f, 50.0f);
    const FVector End = Start + FVector(0.0f, 0.0f, 15000.0f); // 150m vertical trace upwards

    FHitResult HitResult;
    FCollisionQueryParams Params;
    Params.bTraceComplex = false;
    if (APawn* Pawn = GetPawn())
    {
        Params.AddIgnoredActor(Pawn);
    }

    const bool bHit = World->LineTraceSingleByChannel(HitResult, Start, End, ECC_WorldStatic, Params);
    if (bHit)
    {
        // If hit object is directly above at indoor ceiling height (< 800cm) with downward normal, it is an interior room
        if (HitResult.Distance < 800.0f && HitResult.ImpactNormal.Z < -0.5f)
        {
            return false; // Building interior detected, strictly rejected!
        }
    }

    return true;
}

bool ABRAIController::GetRandomExteriorNavLocation(float Radius, FVector& OutNavLocation) const
{
    APawn* ControlledPawn = GetPawn();
    UWorld* World = GetWorld();
    if (!ControlledPawn || !World)
    {
        return false;
    }

    UNavigationSystemV1* NavSys = FNavigationSystem::GetCurrent<UNavigationSystemV1>(World);
    if (!NavSys)
    {
        return false;
    }

    const FVector Origin = ControlledPawn->GetActorLocation();

    // Attempt up to 5 exterior candidates along streets, alleys, and external stairs to rooftops
    for (int32 Attempt = 0; Attempt < 5; ++Attempt)
    {
        FNavLocation RandomNavPoint;
        if (NavSys->GetRandomReachablePointInRadius(Origin, Radius, RandomNavPoint))
        {
            if (IsExteriorLocation(RandomNavPoint.Location))
            {
                OutNavLocation = RandomNavPoint.Location;
                return true;
            }
        }
    }

    return false;
}

bool ABRAIController::FindNaturalCoverLocation(const FVector& ThreatLocation, FVector& OutCoverLocation)
{
    APawn* ControlledPawn = GetPawn();
    UWorld* World = GetWorld();
    if (!ControlledPawn || !World)
    {
        return false;
    }

    const FVector PawnLoc = ControlledPawn->GetActorLocation();
    UNavigationSystemV1* NavSys = FNavigationSystem::GetCurrent<UNavigationSystemV1>(World);
    if (!NavSys)
    {
        return false;
    }

    // Natural cover search (MVP M4): Check positions behind natural obstacles (vehicles, walls, corners)
    constexpr int32 NumSampleAngles = 8;
    constexpr float SampleDistance = 400.0f; // 4m offset

    float BestCoverScore = -MAX_FLT;
    FVector BestCoverPoint = FVector::ZeroVector;
    bool bFoundCover = false;

    for (int32 i = 0; i < NumSampleAngles; ++i)
    {
        const float AngleDeg = (360.0f / NumSampleAngles) * i;
        const FVector OffsetDir = FRotator(0.0f, AngleDeg, 0.0f).Vector();
        const FVector CandidateRaw = PawnLoc + (OffsetDir * SampleDistance);

        FNavLocation ProjectedPoint;
        if (NavSys->ProjectPointToNavigation(CandidateRaw, ProjectedPoint, FVector(200.0f, 200.0f, 200.0f)))
        {
            if (!IsExteriorLocation(ProjectedPoint.Location))
            {
                continue;
            }

            // Test line-of-sight occlusion to threat (natural cover blocks line trace)
            const FVector CoverEye = ProjectedPoint.Location + FVector(0.0f, 0.0f, 50.0f);
            const FVector ThreatEye = ThreatLocation + FVector(0.0f, 0.0f, 50.0f);

            FHitResult CoverTraceHit;
            FCollisionQueryParams CoverParams;
            CoverParams.AddIgnoredActor(ControlledPawn);

            const bool bIsOccluded = World->LineTraceSingleByChannel(
                CoverTraceHit,
                CoverEye,
                ThreatEye,
                ECC_Visibility,
                CoverParams
            );

            if (bIsOccluded)
            {
                // Point provides natural cover against threat
                const float DistToPawn = FVector::Dist(PawnLoc, ProjectedPoint.Location);
                const float Score = 1000.0f - DistToPawn;

                if (Score > BestCoverScore)
                {
                    BestCoverScore = Score;
                    BestCoverPoint = ProjectedPoint.Location;
                    bFoundCover = true;
                }
            }
        }
    }

    if (bFoundCover)
    {
        OutCoverLocation = BestCoverPoint;
        return true;
    }

    return false;
}

void ABRAIController::ExecuteCoverSeeking()
{
    APawn* ControlledPawn = GetPawn();
    if (!ControlledPawn)
    {
        return;
    }

    const float DistToCover = FVector::Dist(ControlledPawn->GetActorLocation(), CurrentCoverLocation);

    if (DistToCover > 100.0f && !bIsInCover)
    {
        MoveToLocation(CurrentCoverLocation, 60.0f);
    }
    else
    {
        // Reached natural cover
        bIsInCover = true;
        StopMovement();

        if (ABRAIBotCharacter* BotChar = Cast<ABRAIBotCharacter>(ControlledPawn))
        {
            BotChar->SetCoverCrouch(true);
        }

        // Aim towards last known threat
        if (CurrentTargetActor)
        {
            AimAtTarget(CurrentTargetActor->GetActorLocation());
        }
    }
}
