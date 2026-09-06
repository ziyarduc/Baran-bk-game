#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "Data/BRTypes.h"
#include "BRGameMode.generated.h"

UCLASS()
class BAKIRKOYBR_API ABRGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    ABRGameMode();

    virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;
    virtual void HandleStartingNewPlayer_Implementation(APlayerController* NewPlayer) override;

    UFUNCTION(BlueprintCallable, Category = "BakirkoyBR")
    void StartMatch();

    UFUNCTION(BlueprintCallable, Category = "BakirkoyBR")
    void OnPlayerEliminated(AController* Victim, AController* Killer);

    UFUNCTION(BlueprintCallable, Category = "BakirkoyBR")
    int32 GetAlivePlayerCount() const;

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditDefaultsOnly, Category = "Match")
    int32 MaxPlayers = 100;

    UPROPERTY(EditDefaultsOnly, Category = "Match")
    int32 BotFillCount = 0;

private:
    void SpawnBots();
    void CheckWinCondition();
    void TransitionToPhase(EBRMatchPhase NewPhase);

    EBRMatchPhase CurrentPhase = EBRMatchPhase::Lobby;
};
