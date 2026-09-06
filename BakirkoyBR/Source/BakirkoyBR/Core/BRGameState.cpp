#include "Core/BRGameState.h"
#include "Net/UnrealNetwork.h"

ABRGameState::ABRGameState()
{
    bReplicates = true;
}

void ABRGameState::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(ABRGameState, PlayersAlive);
    DOREPLIFETIME(ABRGameState, PlayersEliminated);
    DOREPLIFETIME(ABRGameState, CurrentPhase);
    DOREPLIFETIME(ABRGameState, ElapsedMatchTime);
    DOREPLIFETIME(ABRGameState, StormPhase);
    DOREPLIFETIME(ABRGameState, StormCenter);
    DOREPLIFETIME(ABRGameState, StormRadius);
    DOREPLIFETIME(ABRGameState, bIsStormShrinking);
    DOREPLIFETIME(ABRGameState, WindDirection);
    DOREPLIFETIME(ABRGameState, WindSpeed);
}
