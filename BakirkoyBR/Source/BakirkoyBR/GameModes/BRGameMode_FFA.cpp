#include "GameModes/BRGameMode_FFA.h"
#include "Character/BRCharacter.h"
#include "Character/BRHealthComponent.h"
#include "Core/BRGameState.h"
#include "Core/BRPlayerState.h"
#include "Core/BRPlayerController.h"
#include "Data/BRGameConstants.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerStart.h"
#include "Kismet/GameplayStatics.h"

ABRGameMode_FFA::ABRGameMode_FFA()
{
    PrimaryActorTick.bCanEverTick = true;

    DefaultPawnClass = ABRCharacter::StaticClass();
    PlayerControllerClass = ABRPlayerController::StaticClass();
    GameStateClass = ABRGameState::StaticClass();
    PlayerStateClass = ABRPlayerState::StaticClass();

    ScoreLimit = 25;
    MatchTimeLimit = 600.f;
    RemainingMatchTime = 600.f;
    RespawnDelay = 3.f;
    RequiredBotCount = 10;
    bMatchEnded = false;
}

void ABRGameMode_FFA::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
    Super::InitGame(MapName, Options, ErrorMessage);

    RemainingMatchTime = MatchTimeLimit;
    bMatchEnded = false;
    ActiveParticipants.Empty();
    Leaderboard.Empty();
}

void ABRGameMode_FFA::BeginPlay()
{
    Super::BeginPlay();

    SpawnInitialBots();

    ABRGameState* BRGameState = GetGameState<ABRGameState>();
    if (BRGameState)
    {
        BRGameState->CurrentPhase = EBRMatchPhase::Active;
        BRGameState->PlayersAlive = ActiveParticipants.Num();
    }
}

void ABRGameMode_FFA::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (bMatchEnded)
    {
        return;
    }

    RemainingMatchTime -= DeltaSeconds;

    ABRGameState* BRGameState = GetGameState<ABRGameState>();
    if (BRGameState)
    {
        BRGameState->ElapsedMatchTime += DeltaSeconds;
    }

    if (RemainingMatchTime <= 0.f)
    {
        RemainingMatchTime = 0.f;

        TArray<FBRFFALeaderboardEntry> Sorted = GetSortedLeaderboard();
        AController* TopController = Sorted.Num() > 0 ? Sorted[0].Controller.Get() : nullptr;
        EndMatch(TopController);
    }
}

void ABRGameMode_FFA::PostLogin(APlayerController* NewPlayer)
{
    Super::PostLogin(NewPlayer);

    RegisterParticipant(NewPlayer, false);
}

void ABRGameMode_FFA::HandleStartingNewPlayer_Implementation(APlayerController* NewPlayer)
{
    Super::HandleStartingNewPlayer_Implementation(NewPlayer);

    RegisterParticipant(NewPlayer, false);
}

AActor* ABRGameMode_FFA::ChoosePlayerStart_Implementation(AController* Player)
{
    TArray<APlayerStart*> ExteriorStarts;
    for (TActorIterator<APlayerStart> It(GetWorld()); It; ++It)
    {
        ExteriorStarts.Add(*It);
    }

    if (ExteriorStarts.Num() == 0)
    {
        return Super::ChoosePlayerStart_Implementation(Player);
    }

    APlayerStart* BestStart = nullptr;
    float MaxMinDistance = -1.f;

    for (APlayerStart* CandidateStart : ExteriorStarts)
    {
        if (!IsValid(CandidateStart))
        {
            continue;
        }

        const FVector StartLoc = CandidateStart->GetActorLocation();
        float MinDistToCombatant = TNumericLimits<float>::Max();

        for (TActorIterator<APawn> PawnIt(GetWorld()); PawnIt; ++PawnIt)
        {
            APawn* OtherPawn = *PawnIt;
            if (IsValid(OtherPawn) && OtherPawn->GetController() != Player)
            {
                const float Dist = FVector::Dist(StartLoc, OtherPawn->GetActorLocation());
                if (Dist < MinDistToCombatant)
                {
                    MinDistToCombatant = Dist;
                }
            }
        }

        if (MinDistToCombatant > MaxMinDistance)
        {
            MaxMinDistance = MinDistToCombatant;
            BestStart = CandidateStart;
        }
    }

    return BestStart ? BestStart : ExteriorStarts[FMath::RandRange(0, ExteriorStarts.Num() - 1)];
}

void ABRGameMode_FFA::SpawnInitialBots()
{
    UClass* PawnClassToSpawn = BotPawnClass ? BotPawnClass.Get() : DefaultPawnClass.Get();
    UClass* ControllerClassToSpawn = BotControllerClass ? BotControllerClass.Get() : AController::StaticClass();

    if (!PawnClassToSpawn || !GetWorld())
    {
        return;
    }

    for (int32 i = 0; i < RequiredBotCount; ++i)
    {
        FActorSpawnParameters ControllerParams;
        ControllerParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

        AController* NewBotController = GetWorld()->SpawnActor<AController>(ControllerClassToSpawn, FVector::ZeroVector, FRotator::ZeroRotator, ControllerParams);
        if (!NewBotController)
        {
            continue;
        }

        AActor* SpawnPoint = ChoosePlayerStart(NewBotController);
        const FTransform SpawnTransform = SpawnPoint ? SpawnPoint->GetActorTransform() : FTransform::Identity;

        FActorSpawnParameters PawnParams;
        PawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;

        APawn* NewBotPawn = GetWorld()->SpawnActor<APawn>(PawnClassToSpawn, SpawnTransform.GetLocation(), SpawnTransform.GetRotation().Rotator(), PawnParams);
        if (NewBotPawn)
        {
            NewBotController->Possess(NewBotPawn);
        }

        ABRPlayerState* PS = NewBotController->GetPlayerState<ABRPlayerState>();
        if (PS)
        {
            PS->bIsBot = true;
            PS->SetPlayerName(FString::Printf(TEXT("Bot_%02d"), i + 1));
        }

        RegisterParticipant(NewBotController, true);
    }
}

void ABRGameMode_FFA::RegisterParticipant(AController* Controller, bool bIsBot)
{
    if (!IsValid(Controller))
    {
        return;
    }

    if (!ActiveParticipants.Contains(Controller))
    {
        ActiveParticipants.Add(Controller);
    }

    const int32 ExistingIdx = FindLeaderboardIndex(Controller);
    if (ExistingIdx == INDEX_NONE)
    {
        FBRFFALeaderboardEntry Entry;
        Entry.Controller = Controller;
        Entry.bIsBot = bIsBot;

        if (Controller->PlayerState)
        {
            Entry.PlayerName = Controller->PlayerState->GetPlayerName();
        }
        else
        {
            Entry.PlayerName = bIsBot ? FString::Printf(TEXT("Bot_%d"), Leaderboard.Num() + 1) : TEXT("Player");
        }

        Leaderboard.Add(Entry);
    }
}

void ABRGameMode_FFA::OnPlayerEliminated(AController* Victim, AController* Killer)
{
    if (bMatchEnded)
    {
        return;
    }

    if (IsValid(Killer))
    {
        const int32 KillerIdx = FindLeaderboardIndex(Killer);
        if (KillerIdx != INDEX_NONE)
        {
            Leaderboard[KillerIdx].Eliminations++;
            Leaderboard[KillerIdx].Score++;

            ABRPlayerState* KillerPS = Killer->GetPlayerState<ABRPlayerState>();
            if (KillerPS)
            {
                KillerPS->Kills = Leaderboard[KillerIdx].Eliminations;
            }

            if (Leaderboard[KillerIdx].Score >= ScoreLimit)
            {
                EndMatch(Killer);
                return;
            }
        }
    }

    if (IsValid(Victim))
    {
        const int32 VictimIdx = FindLeaderboardIndex(Victim);
        if (VictimIdx != INDEX_NONE)
        {
            Leaderboard[VictimIdx].Deaths++;
        }

        ScheduleRespawn(Victim);
    }

    OnFFAElimination.Broadcast(Killer, Victim);
}

void ABRGameMode_FFA::ScheduleRespawn(AController* EliminatedController)
{
    if (!IsValid(EliminatedController) || bMatchEnded || !GetWorld())
    {
        return;
    }

    APawn* CurrentPawn = EliminatedController->GetPawn();
    if (CurrentPawn)
    {
        EliminatedController->UnPossess();
        CurrentPawn->Destroy();
    }

    FTimerHandle RespawnTimerHandle;
    FTimerDelegate RespawnDelegate;
    RespawnDelegate.BindUObject(this, &ABRGameMode_FFA::ExecuteRespawn, EliminatedController);

    GetWorld()->GetTimerManager().SetTimer(RespawnTimerHandle, RespawnDelegate, RespawnDelay, false);
}

void ABRGameMode_FFA::ExecuteRespawn(AController* Controller)
{
    if (!IsValid(Controller) || bMatchEnded || !GetWorld())
    {
        return;
    }

    AActor* SpawnSpot = ChoosePlayerStart(Controller);
    RestartPlayerAtPlayerStart(Controller, SpawnSpot);

    APawn* NewPawn = Controller->GetPawn();
    if (NewPawn)
    {
        UBRHealthComponent* HealthComp = NewPawn->FindComponentByClass<UBRHealthComponent>();
        if (HealthComp)
        {
            HealthComp->Heal(BRConstants::MAX_HEALTH);
        }
    }
}

void ABRGameMode_FFA::EndMatch(AController* Winner)
{
    if (bMatchEnded)
    {
        return;
    }

    bMatchEnded = true;
    MatchWinnerController = Winner;

    ABRGameState* BRGameState = GetGameState<ABRGameState>();
    if (BRGameState)
    {
        BRGameState->CurrentPhase = EBRMatchPhase::PostGame;
    }

    CelebrateVictory(Winner);
}

void ABRGameMode_FFA::CelebrateVictory(AController* Winner)
{
    FString WinnerName = TEXT("Unknown");
    if (IsValid(Winner))
    {
        if (Winner->PlayerState)
        {
            WinnerName = Winner->PlayerState->GetPlayerName();
        }
        else
        {
            const int32 WinIdx = FindLeaderboardIndex(Winner);
            if (WinIdx != INDEX_NONE)
            {
                WinnerName = Leaderboard[WinIdx].PlayerName;
            }
        }
    }

    for (TObjectPtr<AController>& Participant : ActiveParticipants)
    {
        if (IsValid(Participant))
        {
            APlayerController* PC = Cast<APlayerController>(Participant.Get());
            if (PC)
            {
                PC->SetIgnoreMoveInput(true);
                PC->SetIgnoreLookInput(true);
            }
        }
    }

    OnFFAMatchEnded.Broadcast(Winner, WinnerName);
}

int32 ABRGameMode_FFA::FindLeaderboardIndex(const AController* Controller) const
{
    for (int32 i = 0; i < Leaderboard.Num(); ++i)
    {
        if (Leaderboard[i].Controller.Get() == Controller)
        {
            return i;
        }
    }
    return INDEX_NONE;
}

TArray<FBRFFALeaderboardEntry> ABRGameMode_FFA::GetSortedLeaderboard() const
{
    TArray<FBRFFALeaderboardEntry> SortedList = Leaderboard;
    SortedList.Sort([](const FBRFFALeaderboardEntry& A, const FBRFFALeaderboardEntry& B)
    {
        if (A.Score != B.Score)
        {
            return A.Score > B.Score;
        }
        return A.Deaths < B.Deaths;
    });
    return SortedList;
}
