# Replication Guide

## ReplicationGraph
- Use UReplicationGraph for 100 players (default NetDriver can't handle it)
- Grid-based relevancy: only replicate actors within spatial cells near the player
- Always-relevant actors: GameState, StormCircle
- Distance-based: other players beyond 150m get reduced update frequency

## Key Replicated Properties
| Class | Property | Condition |
|-------|----------|----------|
| ABRGameState | PlayersAlive | Always |
| ABRGameState | StormPhase, StormCenter, StormRadius | Always |
| ABRPlayerState | Kills, DisplayName | Always |
| ABRCharacter | Health, Shield | OwnerOnly |
| ABRCharacter | Position, Rotation | Default |
| ABRCharacter | MovementState | Default |
| ABRCharacter | ActiveWeaponSlot | Default |
| ABRWeaponBase | CurrentAmmo, IsReloading | OwnerOnly |
| ABRBuildPiece | CurrentHP, Material | Always |

## RPC Summary
| RPC | Direction | Reliability | Use |
|-----|-----------|-------------|-----|
| ServerFireWeapon | Client→Server | Reliable | Fire command |
| ServerStartReload | Client→Server | Reliable | Reload command |
| ServerBuildPiece | Client→Server | Reliable | Place build piece |
| ClientConfirmHit | Server→Client | Reliable | Hit marker feedback |
| MulticastPlayFireFX | Server→All | Unreliable | Muzzle flash, sound |
| MulticastPlayImpactFX | Server→All | Unreliable | Impact particles |
