#include "Building/BRBuildingComponent.h"

UBRBuildingComponent::UBRBuildingComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UBRBuildingComponent::PlaceBuildPiece(const FVector& Location, const FRotator& Rotation, EBRBuildPieceType PieceType, EBRMaterialType Material)
{
    if (!GetOwner() || !GetOwner()->HasAuthority())
    {
        return false;
    }

    return true;
}
