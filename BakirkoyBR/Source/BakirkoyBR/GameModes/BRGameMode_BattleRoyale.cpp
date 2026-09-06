#include "GameModes/BRGameMode_BattleRoyale.h"
#include "Character/BRCharacter.h"
#include "Character/BRHealthComponent.h"
#include "Core/BRGameState.h"
#include "Core/BRPlayerState.h"
#include "Core/BRPlayerController.h"
#include "Data/BRGameConstants.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerStart.h"
#include "Storm/BRStormCircle.h"

ABRGameMode_BattleRoyale::ABRGameMode_BattleRoyale()
{
    PrimaryActorTick.bCanEverTick = true;

    DefaultPawnClass = ABRCharacter::StaticClass();
    PlayerControllerClass = ABRPlayerController::StaticClass();
    GameStateClass = ABRGameState::StaticClass();
    PlayerStateClass = ABRPlayerState::StaticClass();
    StormCircleClass = ABRStormCircle::StaticClass();

    RequiredBotCount = 10;
    TotalParticipants = 0;
    AliveParticipants = 0;
    bMatchConcluded = false;
}

void ABRGameMode_BattleRoyale::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
    Super::InitGame(MapName, Options, ErrorMessage);

    TotalParticipants = 0;
    AliveParticipants = 0;
    bMatchConcluded = false;
    ActiveParticipants.Empty();
    EliminatedParticipants.Empty();
}

void ABRGameMode_BattleRoyale::BeginPlay()
{
    Super::BeginPlay();

    InitializeStormCircle();
    SpawnInitialBattleRoyaleBots();

    ABRGameState* BRGameState = GetGameState<ABRGameState>();
    if (BRGameState)
    {
        BRGameState->CurrentPhase = EBRMatchPhase::Active;
        BRGameState->PlayersAlive = AliveParticipants;
        BRGameState->PlayersEliminated = 0;
    }
}

void ABRGameMode_BattleRoyale::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);

    if (bMatchConcluded)
    {
        return;
    }

    SyncGameStateStorm();

    ABRGameState* BRGameState = GetGameState<ABRGameState>();
    if (BRGameState)
    {
        BRGameState->ElapsedMatchTime += DeltaSeconds;
    }

    CheckLastManStanding();
}

void ABRGameMode_BattleRoyale::PostLogin(APlayerController* NewPlayer)
{
    Super::PostLogin(NewPlayer);

    RegisterParticipant(NewPlayer, false);
}

void ABRGameMode_BattleRoyale::HandleStartingNewPlayer_Implementation(APlayerController* NewPlayer)
{
    Super::HandleStartingNewPlayer_Implementation(NewPlayer);

    RegisterParticipant(NewPlayer, false);
}

AActor* ABRGameMode_BattleRoyale::ChoosePlayerStart_Implementation(AController* Player)
{
    TArray<APlayerStart*> AvailableStarts;
    for (TActorIterator<APlayerStart> It(GetWorld()); It; ++It)
    {
        AvailableStarts.Add(*It);
    }

    if (AvailableStarts.Num() == 0)
    {
        return Super::ChoosePlayerStart_Implementation(Player);
    }

    APlayerStart* SelectedStart = nullptr;
    float BestSeparation = -1.f;

    for (APlayerStart* StartCandidate : AvailableStarts)
    {
        if (!IsValid(StartCandidate))
        {
            continue;
        }

        const FVector CandidateLocation = StartCandidate->GetActorLocation();
        float NearestCombatantDist = TNumericLimits<float>::Max();

        for (TActorIterator<APawn> PawnIt(GetWorld()); PawnIt; ++PawnIt)
        {
            APawn* ExistingPawn = *PawnIt;
            if (IsValid(ExistingPawn) && ExistingPawn->GetController() != Player)
            {
                const float Dist = FVector::Dist(CandidateLocation, ExistingPawn->GetActorLocation());
                if (Dist < NearestCombatantDist)
                {
                    NearestCombatantDist = Dist;
                }
            }
        }

        if (NearestCombatantDist > BestSeparation)
        {
            BestSeparation = NearestCombatantDist;
            SelectedStart = StartCandidate;
        }
    }

    return SelectedStart ? SelectedStart : AvailableStarts[FMath::RandRange(0, AvailableStarts.Num() - 1)];
}

void ABRGameMode_BattleRoyale::InitializeStormCircle()
{
    if (!GetWorld() || !StormCircleClass)
    {
        return;
    }

    FActorSpawnParameters SpawnParams;
    SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

    ActiveStormCircle = GetWorld()->SpawnActor<ABRStormCircle>(StormCircleClass, FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);
    SyncGameStateStorm();
}

void ABRGameMode_BattleRoyale::SpawnInitialBattleRoyaleBots()
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

void ABRGameMode_BattleRoyale::RegisterParticipant(AController* Controller, bool bIsBot)
{
    if (!IsValid(Controller))
    {
        return;
    }

    if (!ActiveParticipants.Contains(Controller))
    {
        ActiveParticipants.Add(Controller);
        TotalParticipants++;
        AliveParticipants++;

        ABRPlayerState* PS = Controller->GetPlayerState<ABRPlayerState>();
        if (PS)
        {
            PS->PlayerStatus = EBRPlayerStatus::Alive;
            PS->bIsBot = bIsBot;
        }
    }
}

void ABRGameMode_BattleRoyale::OnPlayerEliminated(AController* Victim, AController* Killer)
{
    if (bMatchConcluded)
    {
        return;
    }

    if (IsValid(Victim) && !EliminatedParticipants.Contains(Victim))
    {
        EliminatedParticipants.Add(Victim);
        AliveParticipants = FMath::Max(0, AliveParticipants - 1);

        ABRPlayerState* VictimPS = Victim->GetPlayerState<ABRPlayerState>();
        if (VictimPS)
        {
            VictimPS->PlayerStatus = EBRPlayerStatus::Eliminated;
        }

        APawn* VictimPawn = Victim->GetPawn();
        if (VictimPawn)
        {
            Victim->UnPossess();
            VictimPawn->Destroy();
        }

        APlayerController* PC = Cast<APlayerController>(Victim);
        if (PC)
        {
            PC->StartSpectatingOnly();
        }

        ABRGameState* BRGameState = GetGameState<ABRGameState>();
        if (BRGameState)
        {
            BRGameState->PlayersAlive = AliveParticipants;
            BRGameState->PlayersEliminated++;
        }
    }

    if (IsValid(Killer))
    {
        ABRPlayerState* KillerPS = Killer->GetPlayerState<ABRPlayerState>();
        if (KillerPS)
        {
            KillerPS->Kills++;
        }
    }

    OnBRElimination.Broadcast(Killer, Victim, AliveParticipants);

    CheckLastManStanding();
}

void ABRGameMode_BattleRoyale::SyncGameStateStorm()
{
    ABRGameState* BRGameState = GetGameState<ABRGameState>();
    if (!BRGameState || !ActiveStormCircle)
    {
        return;
    }

    BRGameState->StormPhase = ActiveStormCircle->GetCurrentPhase();
    BRGameState->StormCenter = ActiveStormCircle->GetCurrentCenter();
    BRGameState->StormRadius = ActiveStormCircle->GetCurrentRadius();
    BRGameState->bIsStormShrinking = ActiveStormCircle->IsShrinking();
}

void ABRGameMode_BattleRoyale::CheckLastManStanding()
{
    if (bMatchConcluded)
    {
        return;
    }

    if (TotalParticipants > 1 && AliveParticipants <= 1)
    {
        AController* SoleSurvivor = nullptr;

        for (TObjectPtr<AController>& Participant : ActiveParticipants)
        {
            if (IsValid(Participant) && !EliminatedParticipants.Contains(Participant))
            {
                SoleSurvivor = Participant.Get();
                break;
            }
        }

        DeclareWinner(SoleSurvivor);
    }
}

void ABRGameMode_BattleRoyale::DeclareWinner(AController* Winner)
{
    if (bMatchConcluded)
    {
        return;
    }

    bMatchConcluded = true;
    WinningController = Winner;

    ABRGameState* BRGameState = GetGameState<ABRGameState>();
    if (BRGameState)
    {
        BRGameState->CurrentPhase = EBRMatchPhase::PostGame;
    }

    CelebrateBattleRoyaleVictory(Winner);
}

void ABRGameMode_BattleRoyale::CelebrateBattleRoyaleVictory(AController* Winner)
{
    FString WinnerName = TEXT("Unknown");
    if (IsValid(Winner))
    {
        if (Winner->PlayerState)
        {
            WinnerName = Winner->PlayerState->GetPlayerName();
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

    OnBRMatchEnded.Broadcast(Winner, WinnerName);
}
