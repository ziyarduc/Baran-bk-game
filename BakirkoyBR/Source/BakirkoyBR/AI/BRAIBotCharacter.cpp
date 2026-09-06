#include "AI/BRAIBotCharacter.h"
#include "AI/BRAIController.h"
#include "Character/BRHealthComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Net/UnrealNetwork.h"

ABRAIBotCharacter::ABRAIBotCharacter()
{
    PrimaryActorTick.bCanEverTick = true;

    // Assign AI Controller
    AIControllerClass = ABRAIController::StaticClass();
    AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;

    // Configure movement speeds and avoidance for bots
    if (UCharacterMovementComponent* MoveComp = GetCharacterMovement())
    {
        MoveComp->MaxWalkSpeed = 450.0f;
        MoveComp->MaxWalkSpeedCrouched = 200.0f;
        MoveComp->NavAgentProps.bCanCrouch = true;
        MoveComp->bUseRVOAvoidance = true;
        MoveComp->AvoidanceWeight = 0.5f;
    }
}

void ABRAIBotCharacter::BeginPlay()
{
    Super::BeginPlay();

    // Hook health component events (server authoritative)
    if (HealthComponent)
    {
        HealthComponent->OnPlayerEliminated.AddDynamic(this, &ABRAIBotCharacter::HandleElimination);
        HealthComponent->OnHealthChanged.AddDynamic(this, &ABRAIBotCharacter::HandleHealthChanged);
    }
}

void ABRAIBotCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void ABRAIBotCharacter::TriggerWeaponFire(const FVector& TargetLocation)
{
    if (HasAuthority())
    {
        Server_FireWeapon_Implementation(TargetLocation);
    }
    else
    {
        Server_FireWeapon(TargetLocation);
    }
}

bool ABRAIBotCharacter::Server_FireWeapon_Validate(const FVector& TargetLocation)
{
    return !TargetLocation.ContainsNaN();
}

void ABRAIBotCharacter::Server_FireWeapon_Implementation(const FVector& TargetLocation)
{
    // Constraint C3: Server-authoritative execution
    if (bIsEliminated || !HealthComponent || !HealthComponent->IsAlive())
    {
        return;
    }

    // Constraint C6: Hybrid Hit Detection - Assault Rifle Hit-Scan Line Trace
    const FVector MuzzleLocation = GetActorLocation() + FVector(0.0f, 0.0f, 50.0f);
    FVector AimDirection = (TargetLocation - MuzzleLocation).GetSafeNormal();

    // Apply weapon spread cone
    const float SpreadRad = FMath::DegreesToRadians(WeaponSpreadAngle);
    AimDirection = FMath::VRandCone(AimDirection, SpreadRad);

    const FVector TraceEnd = MuzzleLocation + (AimDirection * HitScanRange);

    FCollisionQueryParams TraceParams;
    TraceParams.AddIgnoredActor(this);
    TraceParams.bTraceComplex = true;

    FHitResult HitResult;
    const bool bHit = GetWorld()->LineTraceSingleByChannel(
        HitResult,
        MuzzleLocation,
        TraceEnd,
        ECC_Visibility,
        TraceParams
    );

    if (bHit && HitResult.GetActor())
    {
        AActor* HitActor = HitResult.GetActor();
        if (UBRHealthComponent* TargetHealth = HitActor->FindComponentByClass<UBRHealthComponent>())
        {
            FBRDamageInfo DamageInfo;
            DamageInfo.Damage = HitScanBaseDamage;
            DamageInfo.bIsHeadshot = (HitResult.BoneName == TEXT("head"));
            if (DamageInfo.bIsHeadshot)
            {
                DamageInfo.Damage *= 2.0f; // 2x headshot multiplier
            }
            DamageInfo.WeaponType = EBRWeaponType::AssaultRifle;
            DamageInfo.Instigator = this;
            DamageInfo.Distance = HitResult.Distance;

            TargetHealth->ApplyDamage(DamageInfo);
        }
    }
}

void ABRAIBotCharacter::SetCoverCrouch(bool bShouldCrouch)
{
    if (bShouldCrouch)
    {
        Crouch();
        CurrentMovementState = EBRMovementState::Crouching;
    }
    else
    {
        UnCrouch();
        CurrentMovementState = EBRMovementState::Idle;
    }
}

void ABRAIBotCharacter::HandleElimination(AController* Killer)
{
    if (bIsEliminated)
    {
        return;
    }

    bIsEliminated = true;

    // Broadcast elimination event to GameMode/Controller
    OnBotEliminatedEvent.Broadcast(this, Killer);

    // Disable capsule collision
    if (GetCapsuleComponent())
    {
        GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    }

    // Enable ragdoll physics on skeletal mesh
    if (GetMesh())
    {
        GetMesh()->SetCollisionProfileName(TEXT("Ragdoll"));
        GetMesh()->SetSimulatePhysics(true);
    }

    // Detach and unpossess AI controller
    if (AController* BotController = GetController())
    {
        BotController->UnPossess();
    }

    // Clean up actor after delay
    SetLifeSpan(10.0f);
}

void ABRAIBotCharacter::HandleHealthChanged(float NewHealth, float NewShield, const FBRDamageInfo& DamageInfo)
{
    // React to taking damage: notify controller to acquire attacker as target if none exists
    if (NewHealth > 0.0f && DamageInfo.Instigator)
    {
        if (ABRAIController* BotController = Cast<ABRAIController>(GetController()))
        {
            if (!BotController->GetTargetActor())
            {
                BotController->SetTargetActor(DamageInfo.Instigator);
                BotController->SetAIState(EBRAIState::CombatEngagement);
            }
        }
    }
}
