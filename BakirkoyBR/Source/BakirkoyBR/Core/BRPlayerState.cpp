#include "Core/BRPlayerState.h"
#include "Net/UnrealNetwork.h"

ABRPlayerState::ABRPlayerState()
{
    bReplicates = true;
}

void ABRPlayerState::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);

    DOREPLIFETIME(ABRPlayerState, Kills);
    DOREPLIFETIME(ABRPlayerState, Assists);
    DOREPLIFETIME(ABRPlayerState, PlayerStatus);
    DOREPLIFETIME(ABRPlayerState, bIsBot);
}
