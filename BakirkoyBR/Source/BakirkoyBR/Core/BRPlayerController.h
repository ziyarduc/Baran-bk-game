#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "Data/BRTypes.h"
#include "BRPlayerController.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRPlayerController : public APlayerController
{
    GENERATED_BODY()

public:
    ABRPlayerController();

protected:
    virtual void BeginPlay() override;
    virtual void SetupInputComponent() override;

    // Server RPCs
    UFUNCTION(Server, Reliable)
    void ServerFireWeapon(FVector AimLocation, float ClientTimestamp);

    UFUNCTION(Server, Reliable)
    void ServerStartReload();

    UFUNCTION(Server, Reliable)
    void ServerPlaceBuildPiece(FVector Location, FRotator Rotation, EBRBuildPieceType PieceType, EBRMaterialType Material);

    UFUNCTION(Server, Reliable)
    void ServerUseConsumable(EBRConsumableType ConsumableType);
};
