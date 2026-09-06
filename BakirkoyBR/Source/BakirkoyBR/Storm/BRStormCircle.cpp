#include "Storm/BRStormCircle.h"
#include "Character/BRCharacter.h"
#include "Character/BRHealthComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Data/BRTypes.h"
#include "EngineUtils.h"
#include "Net/UnrealNetwork.h"
#include "NiagaraComponent.h"

ABRStormCircle::ABRStormCircle()
{
    PrimaryActorTick.bCanEverTick = true;
    bReplicates = true;
    bAlwaysRelevant = true;

    SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
    RootComponent = SceneRoot;

    StormMeshComponent = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("StormMeshComponent"));
    StormMeshComponent->SetupAttachment(RootComponent);
    StormMeshComponent->SetCollisionProfileName(TEXT("NoCollision"));
    StormMeshComponent->SetGenerateOverlapEvents(false);
    StormMeshComponent->SetCanEverAffectNavigation(false);

    StormNiagaraComponent = CreateDefaultSubobject<UNiagaraComponent>(TEXT("StormNiagaraComponent"));
    StormNiagaraComponent->SetupAttachment(RootComponent);
    StormNiagaraComponent->bAutoActivate = false;

    SetupDefaultPhases();
}

void ABRStormCircle::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(ABRStormCircle, CurrentCenter);
    DOREPLIFETIME(ABRStormCircle, TargetCenter);
    DOREPLIFETIME(ABRStormCircle, CurrentRadius);
    DOREPLIFETIME(ABRStormCircle, TargetRadius);
    DOREPLIFETIME(ABRStormCircle, CurrentPhaseIndex);
    DOREPLIFETIME(ABRStormCircle, bIsShrinking);
    DOREPLIFETIME(ABRStormCircle, DamagePerSecond);
    DOREPLIFETIME(ABRStormCircle, PhaseTimer);
}

void ABRStormCircle::BeginPlay()
{
    Super::BeginPlay();

    UpdateStormVisuals();

    if (HasAuthority())
    {
        StartStormSequence();
    }
}

void ABRStormCircle::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (!HasAuthority())
    {
        return;
    }

    if (bIsShrinking)
    {
        const float SafeShrinkDuration = FMath::Max(ShrinkDuration, 1.0f);
        ShrinkProgress += DeltaSeconds / SafeShrinkDuration;
        const float Alpha = FMath::Clamp(ShrinkProgress, 0.f, 1.f);

        CurrentCenter = FMath::Lerp(ShrinkStartCenter, TargetCenter, Alpha);
        CurrentRadius = FMath::Max(0.f, FMath::Lerp(ShrinkStartRadius, TargetRadius, Alpha));
        PhaseTimer = FMath::Max(0.f, SafeShrinkDuration * (1.f - Alpha));

        UpdateStormVisuals();

        if (Alpha >= 1.0f)
        {
            CurrentCenter = TargetCenter;
            CurrentRadius = TargetRadius;
            bIsShrinking = false;
            ShrinkProgress = 0.f;
            UpdateStormVisuals();

            AdvanceToNextPhase();
        }
    }
    else
    {
        if (PhaseTimer > 0.f)
        {
            PhaseTimer -= DeltaSeconds;
            if (PhaseTimer <= 0.f)
            {
                if (StormPhases.IsValidIndex(CurrentPhaseIndex))
                {
                    bIsShrinking = true;
                    ShrinkProgress = 0.f;
                    ShrinkStartCenter = CurrentCenter;
                    ShrinkStartRadius = CurrentRadius;
                    const float PhaseDuration = StormPhases[CurrentPhaseIndex].ShrinkDuration;
                    ShrinkDuration = FMath::Max(PhaseDuration, 1.0f);
                    PhaseTimer = ShrinkDuration;
                }
                else if (CurrentRadius > 0.f)
                {
                    // Fallback to safely shrink final collapse to zero without dividing by zero
                    bIsShrinking = true;
                    ShrinkProgress = 0.f;
                    ShrinkStartCenter = CurrentCenter;
                    ShrinkStartRadius = CurrentRadius;
                    TargetCenter = CurrentCenter;
                    TargetRadius = 0.f;
                    ShrinkDuration = FMath::Max(ShrinkDuration, 10.f);
                    PhaseTimer = ShrinkDuration;
                }
            }
        }
    }

    DamageAccumulator += DeltaSeconds;
    const float SafeInterval = FMath::Max(DamageTickInterval, 0.1f);
    if (DamageAccumulator >= SafeInterval)
    {
        ApplyDamageTick();
        DamageAccumulator = 0.f;
    }
}

void ABRStormCircle::SetupDefaultPhases()
{
    StormPhases.Empty();

    // 7 distinct shrinking phases for urban battle royale pacing
    StormPhases.Add({ 0, 20000.f, 40.f, 30.f, 1.0f });
    StormPhases.Add({ 1, 14000.f, 35.f, 25.f, 2.0f });
    StormPhases.Add({ 2,  9000.f, 30.f, 20.f, 4.0f });
    StormPhases.Add({ 3,  5000.f, 25.f, 20.f, 6.0f });
    StormPhases.Add({ 4,  2500.f, 20.f, 15.f, 8.0f });
    StormPhases.Add({ 5,  1000.f, 15.f, 15.f, 12.0f });
    StormPhases.Add({ 6,     0.f, 10.f, 15.f, 18.0f });
}

void ABRStormCircle::StartStormSequence()
{
    CurrentPhaseIndex = 0;
    CurrentCenter = FVector2D(GetActorLocation().X, GetActorLocation().Y);
    CurrentRadius = MaxPlayAreaRadius;
    bIsShrinking = false;
    ShrinkProgress = 0.f;

    if (StormPhases.Num() > 0)
    {
        TargetRadius = StormPhases[0].SafeZoneRadius;
        CalculateNextSafeZone();
        PhaseTimer = StormPhases[0].WaitDuration;
        DamagePerSecond = StormPhases[0].DamagePerSecond;
    }

    UpdateStormVisuals();

    OnStormPhaseChanged.Broadcast(CurrentPhaseIndex);
}

void ABRStormCircle::CalculateNextSafeZone()
{
    if (TargetRadius <= 0.f)
    {
        TargetCenter = CurrentCenter;
        return;
    }

    const float MaxOffset = FMath::Max(0.f, CurrentRadius - TargetRadius);
    if (MaxOffset <= 0.f)
    {
        TargetCenter = CurrentCenter;
        return;
    }

    const float RandomAngle = FMath::FRandRange(0.f, 2.f * PI);
    const float RandomDistance = FMath::FRandRange(0.f, MaxOffset * 0.75f);

    TargetCenter = CurrentCenter + FVector2D(
        FMath::Cos(RandomAngle) * RandomDistance,
        FMath::Sin(RandomAngle) * RandomDistance
    );
}

void ABRStormCircle::AdvanceToNextPhase()
{
    if (CurrentPhaseIndex >= StormPhases.Num() && CurrentRadius <= 0.f)
    {
        // Fully collapsed terminal state reached
        TargetRadius = 0.f;
        TargetCenter = CurrentCenter;
        bIsShrinking = false;
        PhaseTimer = 0.f;
        DamagePerSecond = 25.f;
        UpdateStormVisuals();
        return;
    }

    CurrentPhaseIndex++;

    if (StormPhases.IsValidIndex(CurrentPhaseIndex))
    {
        const FBRStormPhaseConfig& NextConfig = StormPhases[CurrentPhaseIndex];
        TargetRadius = NextConfig.SafeZoneRadius;
        CalculateNextSafeZone();
        PhaseTimer = NextConfig.WaitDuration;
        DamagePerSecond = NextConfig.DamagePerSecond;
        bIsShrinking = false;
        ShrinkProgress = 0.f;

        OnStormPhaseChanged.Broadcast(CurrentPhaseIndex);
    }
    else
    {
        // Final collapse reached
        TargetRadius = 0.f;
        TargetCenter = CurrentCenter;
        DamagePerSecond = 25.f;

        if (CurrentRadius > 0.f)
        {
            // Initiate final smooth collapse to zero with safe minimum duration
            bIsShrinking = true;
            ShrinkProgress = 0.f;
            ShrinkStartCenter = CurrentCenter;
            ShrinkStartRadius = CurrentRadius;
            ShrinkDuration = FMath::Max(ShrinkDuration > 0.f ? ShrinkDuration : 15.f, 10.f);
            PhaseTimer = ShrinkDuration;
        }
        else
        {
            CurrentRadius = 0.f;
            bIsShrinking = false;
            PhaseTimer = 0.f;
        }

        OnStormPhaseChanged.Broadcast(CurrentPhaseIndex);
    }

    UpdateStormVisuals();
}

bool ABRStormCircle::IsLocationInsideSafeZone(const FVector& TestLocation) const
{
    if (CurrentRadius <= 0.f)
    {
        return false;
    }

    const FVector2D Loc2D(TestLocation.X, TestLocation.Y);
    return FVector2D::Distance(Loc2D, CurrentCenter) <= CurrentRadius;
}

float ABRStormCircle::GetDistanceToSafeZone(const FVector& TestLocation) const
{
    const FVector2D Loc2D(TestLocation.X, TestLocation.Y);
    const float Dist = FVector2D::Distance(Loc2D, CurrentCenter);
    if (CurrentRadius <= 0.f)
    {
        return Dist;
    }
    return FMath::Max(0.f, Dist - CurrentRadius);
}

void ABRStormCircle::ApplyDamageTick()
{
    if (!GetWorld())
    {
        return;
    }

    for (TActorIterator<APawn> PawnIt(GetWorld()); PawnIt; ++PawnIt)
    {
        APawn* Pawn = *PawnIt;
        if (!IsValid(Pawn))
        {
            continue;
        }

        const FVector PawnLocation = Pawn->GetActorLocation();
        if (!IsLocationInsideSafeZone(PawnLocation))
        {
            UBRHealthComponent* HealthComp = Pawn->FindComponentByClass<UBRHealthComponent>();
            if (HealthComp && HealthComp->IsAlive())
            {
                FBRDamageInfo StormDamage;
                StormDamage.Damage = DamagePerSecond * DamageTickInterval;
                StormDamage.Instigator = this;
                StormDamage.Distance = GetDistanceToSafeZone(PawnLocation);

                HealthComp->ApplyDamage(StormDamage);
                OnStormDamageDealt.Broadcast(Pawn, StormDamage.Damage);
            }
        }
    }
}

void ABRStormCircle::OnRep_CurrentCenter()
{
    UpdateStormVisuals();
}

void ABRStormCircle::OnRep_CurrentRadius()
{
    UpdateStormVisuals();
}

void ABRStormCircle::OnRep_CurrentPhaseIndex()
{
    OnStormPhaseChanged.Broadcast(CurrentPhaseIndex);
}

void ABRStormCircle::UpdateStormVisuals()
{
    const FVector NewLocation(CurrentCenter.X, CurrentCenter.Y, GetActorLocation().Z);
    SetActorLocation(NewLocation);

    const float SafeBaseRadius = FMath::Max(MeshBaseRadius, 1.0f);
    const float SafeCurrentRadius = FMath::Max(CurrentRadius, 0.0f);
    const float ScaleXY = SafeCurrentRadius / SafeBaseRadius;

    if (StormMeshComponent)
    {
        const float CurrentZ = StormMeshComponent->GetRelativeScale3D().Z;
        StormMeshComponent->SetWorldScale3D(FVector(ScaleXY, ScaleXY, CurrentZ > 0.01f ? CurrentZ : 50.0f));
    }

    if (StormNiagaraComponent)
    {
        StormNiagaraComponent->SetVariableFloat(FName(TEXT("Radius")), SafeCurrentRadius);
        StormNiagaraComponent->SetVariableFloat(FName(TEXT("StormRadius")), SafeCurrentRadius);
        StormNiagaraComponent->SetVariableFloat(FName(TEXT("User.Radius")), SafeCurrentRadius);
        StormNiagaraComponent->SetVariableFloat(FName(TEXT("User.StormRadius")), SafeCurrentRadius);
        StormNiagaraComponent->SetVariableVec3(FName(TEXT("User.StormCenter")), NewLocation);
        StormNiagaraComponent->SetVariableVec3(FName(TEXT("StormCenter")), NewLocation);

        const float NiagaraZ = StormNiagaraComponent->GetRelativeScale3D().Z;
        StormNiagaraComponent->SetWorldScale3D(FVector(ScaleXY, ScaleXY, NiagaraZ > 0.01f ? NiagaraZ : 1.0f));
    }

    if (RootComponent)
    {
        TArray<USceneComponent*> Children;
        RootComponent->GetChildrenComponents(true, Children);
        for (USceneComponent* Child : Children)
        {
            if (Child && Child != StormMeshComponent && Child != StormNiagaraComponent)
            {
                if (UStaticMeshComponent* OtherMesh = Cast<UStaticMeshComponent>(Child))
                {
                    OtherMesh->SetWorldScale3D(FVector(ScaleXY, ScaleXY, OtherMesh->GetComponentScale().Z));
                }
                else if (UNiagaraComponent* OtherNiagara = Cast<UNiagaraComponent>(Child))
                {
                    OtherNiagara->SetVariableFloat(FName(TEXT("Radius")), SafeCurrentRadius);
                    OtherNiagara->SetVariableFloat(FName(TEXT("StormRadius")), SafeCurrentRadius);
                    OtherNiagara->SetVariableFloat(FName(TEXT("User.Radius")), SafeCurrentRadius);
                    OtherNiagara->SetVariableFloat(FName(TEXT("User.StormRadius")), SafeCurrentRadius);
                }
            }
        }
    }
}
