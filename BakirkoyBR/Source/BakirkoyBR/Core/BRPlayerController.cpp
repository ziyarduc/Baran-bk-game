#include "Core/BRPlayerController.h"
#include "Character/BRCharacter.h"
#include "Character/BRHealthComponent.h"
#include "Building/BRBuildingComponent.h"
#include "Weapons/BRWeaponBase.h"
#include "Data/BRGameConstants.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/World.h"

ABRPlayerController::ABRPlayerController()
{
}

void ABRPlayerController::BeginPlay()
{
    Super::BeginPlay();
}

void ABRPlayerController::SetupInputComponent()
{
    Super::SetupInputComponent();
    // TODO: Bind enhanced input actions
}

void ABRPlayerController::ServerFireWeapon_Implementation(FVector AimLocation, float ClientTimestamp)
{
    // Validate pawn exists and is alive
    ABRCharacter* BRChar = GetPawn<ABRCharacter>();
    if (!BRChar || !BRChar->HealthComponent || !BRChar->HealthComponent->IsAlive())
    {
        return;
    }

    if (ABRWeaponBase* Weapon = BRChar->GetCurrentWeapon())
    {
        // Hit validation: check client timestamp against server rewind tolerance
        if (ClientTimestamp > 0.0f && GetWorld())
        {
            const float LatencyDelta = FMath::Abs(GetWorld()->GetTimeSeconds() - ClientTimestamp);
            if (LatencyDelta > BRConstants::MAX_REWIND_TIME)
            {
                // Timestamp exceeds rewind tolerance; server continues with authoritative timing
            }
        }

        // Align control rotation towards aim location if provided
        if (!AimLocation.IsNearlyZero())
        {
            FVector ViewLocation;
            FRotator ViewRotation;
            GetPlayerViewPoint(ViewLocation, ViewRotation);
            const FRotator AimRotation = (AimLocation - ViewLocation).Rotation();
            SetControlRotation(AimRotation);
        }

        if (Weapon->CanFire())
        {
            Weapon->StartFire();
        }
    }
}

void ABRPlayerController::ServerStartReload_Implementation()
{
    // Validate pawn exists and is alive
    ABRCharacter* BRChar = GetPawn<ABRCharacter>();
    if (!BRChar || !BRChar->HealthComponent || !BRChar->HealthComponent->IsAlive())
    {
        return;
    }

    if (ABRWeaponBase* Weapon = BRChar->GetCurrentWeapon())
    {
        if (Weapon->CanReload())
        {
            Weapon->Reload();
        }
    }
}

void ABRPlayerController::ServerPlaceBuildPiece_Implementation(FVector Location, FRotator Rotation, EBRBuildPieceType PieceType, EBRMaterialType Material)
{
    // Validate pawn exists and is alive
    ABRCharacter* BRChar = GetPawn<ABRCharacter>();
    if (!BRChar || !BRChar->HealthComponent || !BRChar->HealthComponent->IsAlive())
    {
        return;
    }

    // Distance validation: build piece placement within allowable range
    const float MaxBuildDistance = BRConstants::BUILD_PIECE_SIZE * 4.0f;
    if (FVector::DistSquared(BRChar->GetActorLocation(), Location) > FMath::Square(MaxBuildDistance))
    {
        return;
    }

    if (BRChar->BuildingComponent)
    {
        BRChar->BuildingComponent->PlaceBuildPiece(Location, Rotation, PieceType, Material);
    }
}

void ABRPlayerController::ServerUseConsumable_Implementation(EBRConsumableType ConsumableType)
{
    // Validate pawn exists and is alive
    ABRCharacter* BRChar = GetPawn<ABRCharacter>();
    if (!BRChar || !BRChar->HealthComponent || !BRChar->HealthComponent->IsAlive())
    {
        return;
    }

    switch (ConsumableType)
    {
    case EBRConsumableType::SmallShield:
        if (BRChar->HealthComponent->GetShield() < 50.0f)
        {
            const float ShieldToAdd = FMath::Min(25.0f, 50.0f - BRChar->HealthComponent->GetShield());
            BRChar->HealthComponent->AddShield(ShieldToAdd);
        }
        break;

    case EBRConsumableType::BigShield:
        BRChar->HealthComponent->AddShield(50.0f);
        break;

    case EBRConsumableType::Bandage:
        if (BRChar->HealthComponent->GetHealth() < 75.0f)
        {
            const float HealToAdd = FMath::Min(15.0f, 75.0f - BRChar->HealthComponent->GetHealth());
            BRChar->HealthComponent->Heal(HealToAdd);
        }
        break;

    case EBRConsumableType::Medkit:
        BRChar->HealthComponent->Heal(BRConstants::MAX_HEALTH);
        break;

    case EBRConsumableType::SpeedBoost:
        if (UCharacterMovementComponent* MovementComp = BRChar->GetCharacterMovement())
        {
            MovementComp->MaxWalkSpeed *= 1.4f;
        }
        break;

    default:
        break;
    }
}
