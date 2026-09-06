#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameStateBase.h"
#include "Data/BRTypes.h"
#include "BRGameState.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRGameState : public AGameStateBase
{
    GENERATED_BODY()

public:
    ABRGameState();

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Match")
    int32 PlayersAlive = 0;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Match")
    int32 PlayersEliminated = 0;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Match")
    EBRMatchPhase CurrentPhase = EBRMatchPhase::Lobby;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Match")
    float ElapsedMatchTime = 0.f;

    // Storm data
    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Storm")
    int32 StormPhase = 0;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Storm")
    FVector2D StormCenter = FVector2D::ZeroVector;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Storm")
    float StormRadius = 0.f;

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "Storm")
    bool bIsStormShrinking = false;

    // Wind
    UPROPERTY(Replicated, BlueprintReadOnly, Category = "World")
    FVector2D WindDirection = FVector2D(1.f, 0.f);

    UPROPERTY(Replicated, BlueprintReadOnly, Category = "World")
    float WindSpeed = 5.f;
};
