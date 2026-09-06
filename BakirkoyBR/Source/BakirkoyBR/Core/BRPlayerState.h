#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerState.h"
#include "Data/BRTypes.h"
#include "BRPlayerState.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRPlayerState : public APlayerState
{
    GENERATED_BODY()

public:
    ABRPlayerState();

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Stats")
    int32 Kills = 0;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Stats")
    int32 Assists = 0;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Stats")
    EBRPlayerStatus PlayerStatus = EBRPlayerStatus::Alive;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Stats")
    bool bIsBot = false;
};
