#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "Data/BRTypes.h"
#include "BRGameMode_FFA.generated.h"

class APlayerStart;
class ABRCharacter;

USTRUCT(BlueprintType)
struct FBRFFALeaderboardEntry
{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Leaderboard")
    TObjectPtr<AController> Controller;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Leaderboard")
    FString PlayerName;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Leaderboard")
    int32 Score = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Leaderboard")
    int32 Eliminations = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Leaderboard")
    int32 Deaths = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Leaderboard")
    bool bIsBot = false;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnFFAMatchEnded, AController*, WinnerController, const FString&, WinnerName);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnFFAElimination, AController*, Killer, AController*, Victim);

UCLASS()
class BAKIRKOYBR_API ABRGameMode_FFA : public AGameModeBase
{
    GENERATED_BODY()

public:
    ABRGameMode_FFA();

    virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void PostLogin(APlayerController* NewPlayer) override;
    virtual void HandleStartingNewPlayer_Implementation(APlayerController* NewPlayer) override;
    virtual AActor* ChoosePlayerStart_Implementation(AController* Player) override;

    UFUNCTION(BlueprintCallable, Category = "BakirkoyBR|FFA")
    void OnPlayerEliminated(AController* Victim, AController* Killer);

    UFUNCTION(BlueprintPure, Category = "BakirkoyBR|FFA")
    TArray<FBRFFALeaderboardEntry> GetSortedLeaderboard() const;

    UFUNCTION(BlueprintPure, Category = "BakirkoyBR|FFA")
    float GetRemainingMatchTime() const { return RemainingMatchTime; }

    UFUNCTION(BlueprintPure, Category = "BakirkoyBR|FFA")
    bool HasMatchEnded() const { return bMatchEnded; }

    UFUNCTION(BlueprintPure, Category = "BakirkoyBR|FFA")
    AController* GetMatchWinner() const { return MatchWinnerController.Get(); }

    UPROPERTY(BlueprintAssignable, Category = "BakirkoyBR|FFA")
    FOnFFAMatchEnded OnFFAMatchEnded;

    UPROPERTY(BlueprintAssignable, Category = "BakirkoyBR|FFA")
    FOnFFAElimination OnFFAElimination;

protected:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "BakirkoyBR|Rules")
    int32 ScoreLimit = 25;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "BakirkoyBR|Rules")
    float MatchTimeLimit = 600.f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "BakirkoyBR|Rules")
    float RespawnDelay = 3.f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "BakirkoyBR|Bots")
    int32 RequiredBotCount = 10;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "BakirkoyBR|Classes")
    TSubclassOf<APawn> BotPawnClass;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "BakirkoyBR|Classes")
    TSubclassOf<AController> BotControllerClass;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|State")
    float RemainingMatchTime = 600.f;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|State")
    bool bMatchEnded = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|State")
    TObjectPtr<AController> MatchWinnerController;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|State")
    TArray<FBRFFALeaderboardEntry> Leaderboard;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|Participants")
    TArray<TObjectPtr<AController>> ActiveParticipants;

private:
    void SpawnInitialBots();
    void RegisterParticipant(AController* Controller, bool bIsBot);
    void ScheduleRespawn(AController* EliminatedController);
    void ExecuteRespawn(AController* Controller);
    void EndMatch(AController* Winner);
    void CelebrateVictory(AController* Winner);
    int32 FindLeaderboardIndex(const AController* Controller) const;
};
