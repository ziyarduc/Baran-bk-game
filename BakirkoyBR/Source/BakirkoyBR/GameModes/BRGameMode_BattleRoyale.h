#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "Data/BRTypes.h"
#include "BRGameMode_BattleRoyale.generated.h"

class ABRStormCircle;
class APlayerStart;
class ABRCharacter;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnBRMatchEnded, AController*, WinnerController, const FString&, WinnerName);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnBRElimination, AController*, Killer, AController*, Victim, int32, RemainingAlive);

UCLASS()
class BAKIRKOYBR_API ABRGameMode_BattleRoyale : public AGameModeBase
{
    GENERATED_BODY()

public:
    ABRGameMode_BattleRoyale();

    virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void PostLogin(APlayerController* NewPlayer) override;
    virtual void HandleStartingNewPlayer_Implementation(APlayerController* NewPlayer) override;
    virtual AActor* ChoosePlayerStart_Implementation(AController* Player) override;

    UFUNCTION(BlueprintCallable, Category = "BakirkoyBR|BattleRoyale")
    void OnPlayerEliminated(AController* Victim, AController* Killer);

    UFUNCTION(BlueprintPure, Category = "BakirkoyBR|BattleRoyale")
    int32 GetAliveCount() const { return AliveParticipants; }

    UFUNCTION(BlueprintPure, Category = "BakirkoyBR|BattleRoyale")
    int32 GetTotalCount() const { return TotalParticipants; }

    UFUNCTION(BlueprintPure, Category = "BakirkoyBR|BattleRoyale")
    bool IsMatchConcluded() const { return bMatchConcluded; }

    UFUNCTION(BlueprintPure, Category = "BakirkoyBR|BattleRoyale")
    AController* GetWinner() const { return WinningController.Get(); }

    UFUNCTION(BlueprintPure, Category = "BakirkoyBR|BattleRoyale")
    ABRStormCircle* GetStormCircle() const { return ActiveStormCircle.Get(); }

    UPROPERTY(BlueprintAssignable, Category = "BakirkoyBR|BattleRoyale")
    FOnBRMatchEnded OnBRMatchEnded;

    UPROPERTY(BlueprintAssignable, Category = "BakirkoyBR|BattleRoyale")
    FOnBRElimination OnBRElimination;

protected:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "BakirkoyBR|Config")
    int32 RequiredBotCount = 10;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "BakirkoyBR|Classes")
    TSubclassOf<ABRStormCircle> StormCircleClass;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "BakirkoyBR|Classes")
    TSubclassOf<APawn> BotPawnClass;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "BakirkoyBR|Classes")
    TSubclassOf<AController> BotControllerClass;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|Storm")
    TObjectPtr<ABRStormCircle> ActiveStormCircle;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|State")
    int32 TotalParticipants = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|State")
    int32 AliveParticipants = 0;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|State")
    bool bMatchConcluded = false;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|State")
    TObjectPtr<AController> WinningController;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|Participants")
    TArray<TObjectPtr<AController>> ActiveParticipants;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "BakirkoyBR|Participants")
    TArray<TObjectPtr<AController>> EliminatedParticipants;

private:
    void InitializeStormCircle();
    void SpawnInitialBattleRoyaleBots();
    void RegisterParticipant(AController* Controller, bool bIsBot);
    void SyncGameStateStorm();
    void CheckLastManStanding();
    void DeclareWinner(AController* Winner);
    void CelebrateBattleRoyaleVictory(AController* Winner);
};
