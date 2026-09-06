# Sequential Thinking Record — AIAgents Worker (MVP Demo 1)

## Stage 1: Constraint & Invariants Scan
- **C1 (No Interior Spaces)**: NavMesh goals and wander destinations strictly exterior (streets, alleys, rooftops via external stairs/fire escapes). Strict rejection logic for interior positions.
- **C2 (Solo BR Only)**: Solo combat; bot attacks nearest enemy. No squads, teams, duos, revives, or DBNO.
- **C3 (Server-Authoritative)**: All AI perception, state machine, health component damage handling, and weapon firing are server-authoritative.
- **C4 (3rd Person Camera)**: Inherits from ABRCharacter which uses 3rd person perspective.
- **C5 (3 Build Materials)**: Building system paused for Demo 1 (M4); bots do not place builds, relying entirely on natural cover (vehicles, walls, corners).
- **C6 (Hybrid Hit Detection)**: Supports hit-scan weapon firing (LineTrace) for AR and projectile firing for Rocket Launcher.
- **C7 (BR Prefix)**: All classes/structs/enums prefixed with BR (ABRAIController, ABRAIBotCharacter, EBRAIState, etc.).
- **M1 (10-Bot MVP Scenario)**: Total AI count strictly limited to MAX_BOT_COUNT = 10.
- **M2 (Dual Weapons)**: Loot seeking finds AR Hit-Scan or Rocket Launcher.
- **M3 (2 GameModes)**: Compatible with both FFA and Classic BR.
- **M4 (Building Paused)**: Natural cover usage only (vehicles, walls, street obstacles).
- **M5 (Exterior Vertical Nav)**: External stairs and fire escapes to access rooftops.

## Stage 2: Module Ownership & Scope Assessment
- Write boundaries: `BakirkoyBR/Source/BakirkoyBR/AI/**` and `.agents/teamwork_preview_worker_ai_agents/**`.
- Files to create:
  * `Source/BakirkoyBR/AI/BRAIController.h`
  * `Source/BakirkoyBR/AI/BRAIController.cpp`
  * `Source/BakirkoyBR/AI/BRAIBotCharacter.h`
  * `Source/BakirkoyBR/AI/BRAIBotCharacter.cpp`
- No cross-module violations or unrelated refactoring.

## Stage 3: Unreal Reflection & Memory Safety Check
- `#include "BRAIController.generated.h"` strictly the last include in `BRAIController.h`.
- `#include "BRAIBotCharacter.generated.h"` strictly the last include in `BRAIBotCharacter.h`.
- `#pragma once` on line 1.
- Mandatory `BR` prefix (`ABRAIController`, `ABRAIBotCharacter`, `EBRAIState`, `FBRAICoverPoint`).
- GC Pointer Safety: All `UObject*` member pointers wrapped in `TObjectPtr<>` and annotated with `UPROPERTY()`. Weak references use `TWeakObjectPtr<>`.
- Zero STL usage: No `std::string`, `std::vector`, `std::map`. Exclusively `FString`, `TArray`, `TMap`.
- Forward declarations used for pointer types in headers.

## Stage 4: Network Authority & Implementation Blueprint
- Enforce `MAX_BOT_COUNT = 10` constant and tracking.
- `ABRAIController`:
  * `UAIPerceptionComponent` with `UAISenseConfig_Sight` (120 deg FOV, 8000 range) and `UAISenseConfig_Hearing`.
  * State Machine: `LootSeeking`, `CombatEngagement`, `Wandering` / `ZoneMove`, `CoverSeeking`.
  * Exterior constraint check: Rejects indoor positions (tests upwards line trace to open sky).
  * Natural cover query: Overlaps vehicles and walls, checks occlusion against target.
- `ABRAIBotCharacter`:
  * Inherits from `ABRCharacter`.
  * Integrates `UBRHealthComponent`, handles elimination event.
  * Server-authoritative weapon firing trigger.

## Stage 5: Verification Hypothesis & Acceptance Gate
- Verification script: `pwsh -File scripts/verify-rules.ps1`
- Target: All 117+ checks pass with 0 errors.
- Verification method, surgical diffs, and conclusion documented in `handoff.md`.
