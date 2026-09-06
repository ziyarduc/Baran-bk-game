#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Data/BRTypes.h"
#include "BRBuildingComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class BAKIRKOYBR_API UBRBuildingComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UBRBuildingComponent();

    UFUNCTION(BlueprintCallable, Category = "Building")
    bool PlaceBuildPiece(const FVector& Location, const FRotator& Rotation, EBRBuildPieceType PieceType, EBRMaterialType Material);
};
