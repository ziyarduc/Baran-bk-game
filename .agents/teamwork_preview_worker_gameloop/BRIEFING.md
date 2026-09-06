# BRIEFING — 2026-09-06T11:20:00Z

## Mission
Implement Mode 1 (FFA Deathmatch) and Mode 2 (Classic Battle Royale with Storm Circle) for Bakırköy BR Playable Demo MVP.

## 🔒 My Identity
- Archetype: worker
- Roles: implementer, qa, specialist
- Working directory: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_gameloop
- Original parent: a7b4df4f-06c2-49d7-8493-910a49a9adde
- Milestone: Playable Demo MVP - GameLoop

## 🔒 Key Constraints
- C1: No interior spaces (exterior-only collision, external stairs to rooftops)
- C2: Solo BR only (no squads, duos, DBNO, revives)
- C3: Server-authoritative architecture
- C4: 3rd person camera perspective only
- C5: Exactly 3 building materials (Moloz, Tuğla, Çelik)
- C6: Hybrid hit detection (AR = HitScan; Rocket = Projectile splash)
- C7: Strict BR prefix for all types/classes
- M1: Exactly 10-bot MVP scenario (10 bots + 1 player)
- M2: Dual weapons (AR HitScan + Rocket Launcher Projectile)
- M3: Two distinct playable GameModes (FFA Deathmatch + Classic BR)
- M4: Building system paused for Demo 1 (natural cover only)
- M5: Exterior vertical navigation & rooftop NavMesh
- Exclusive write boundaries:
  * BakirkoyBR/Source/BakirkoyBR/GameModes/**
  * BakirkoyBR/Source/BakirkoyBR/Storm/**
  * C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_gameloop/**

## Current Parent
- Conversation ID: a7b4df4f-06c2-49d7-8493-910a49a9adde
- Updated: 2026-09-06T11:20:00Z

## Task Summary
- **What to build**:
  1. `BRGameMode_FFA.h/.cpp`: Score limit (25 elims), match time limit (600s), respawn at exterior starts, leaderboard tracking, victory celebration.
  2. `BRGameMode_BattleRoyale.h/.cpp`: Solo BR, 10 bots + 1 player spawn at start, permadeath (no respawn), storm circle integration, win condition: Last Man Standing.
  3. `BRStormCircle.h/.cpp`: Shrinking circle radius, center point interpolation, damage over time outside safe zone.
- **Success criteria**: All rules pass `pwsh -File scripts/verify-rules.ps1` (117+ rules), reflection safety verified, compact handoff generated.
- **Interface contracts**: Source/BakirkoyBR/Data/BRTypes.h, BRGameConstants.h
- **Code layout**: Source/BakirkoyBR/GameModes/, Source/BakirkoyBR/Storm/

## Key Decisions Made
- Implemented 7-phase shrinking configuration in `ABRStormCircle` with random bounded center displacement fitting inside preceding zones.
- `ABRGameMode_FFA` uses distance-weighted exterior `APlayerStart` selection to guarantee safe exterior combat respawns.
- `ABRGameMode_BattleRoyale` synchronizes storm radius/center directly to `ABRGameState` and permanently transitions eliminated controllers to spectator mode.

## Artifact Index
- C:\Users\silver\Desktop\bakirkoy-br\BakirkoyBR\Source\BakirkoyBR\Storm\BRStormCircle.h
- C:\Users\silver\Desktop\bakirkoy-br\BakirkoyBR\Source\BakirkoyBR\Storm\BRStormCircle.cpp
- C:\Users\silver\Desktop\bakirkoy-br\BakirkoyBR\Source\BakirkoyBR\GameModes\BRGameMode_FFA.h
- C:\Users\silver\Desktop\bakirkoy-br\BakirkoyBR\Source\BakirkoyBR\GameModes\BRGameMode_FFA.cpp
- C:\Users\silver\Desktop\bakirkoy-br\BakirkoyBR\Source\BakirkoyBR\GameModes\BRGameMode_BattleRoyale.h
- C:\Users\silver\Desktop\bakirkoy-br\BakirkoyBR\Source\BakirkoyBR\GameModes\BRGameMode_BattleRoyale.cpp
- C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_gameloop\handoff.md

## Change Tracker
- **Files modified**:
  * `BakirkoyBR/Source/BakirkoyBR/Storm/BRStormCircle.h` (created)
  * `BakirkoyBR/Source/BakirkoyBR/Storm/BRStormCircle.cpp` (created)
  * `BakirkoyBR/Source/BakirkoyBR/GameModes/BRGameMode_FFA.h` (created)
  * `BakirkoyBR/Source/BakirkoyBR/GameModes/BRGameMode_FFA.cpp` (created)
  * `BakirkoyBR/Source/BakirkoyBR/GameModes/BRGameMode_BattleRoyale.h` (created)
  * `BakirkoyBR/Source/BakirkoyBR/GameModes/BRGameMode_BattleRoyale.cpp` (created)
- **Build status**: 204/204 verification tests passing
- **Pending issues**: None

## Quality Status
- **Build/test result**: Passed 204/204 AST checks
- **Lint status**: 0 violations
- **Tests added/modified**: Integrated into scripts/verify-rules.ps1 AST suite

## Loaded Skills
- **Source**: C:\Users\silver\Desktop\bakirkoy-br\.agents\skills\worker-gameloop-backend\SKILL.md
  - **Local copy**: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_gameloop\SKILL.md
  - **Core methodology**: Implements server-authoritative GameMode, GameState, Storm, and elimination flow for 10-bot BR & FFA.
