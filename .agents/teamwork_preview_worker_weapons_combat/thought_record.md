# Sequential Thinking Protocol Record — Weapons & Combat Worker
Date: 2026-09-06T11:16:50Z

## Stage 1: Constraint & Invariants Scan
- C1 (No Interior Spaces): Weapon traces and projectiles interact with exterior geometry and players only. No interior rooms, indoor furniture, or interior queries.
- C2 (Solo BR Only): Solo combat model only. No squad ID checks, no revive logic, no DBNO / crawling checks, no teammate damage filters. Direct damage applies to individual player health component.
- C3 (Server-Authoritative Architecture): Dedicated server owns all weapon state (ammo count, magazine capacity, firing state, reload timer, damage calculation). Clients trigger actions via validated Server RPCs. Server verifies ammo before firing, executes line traces or projectile spawns, and applies damage.
- C4 (3rd Person Camera Perspective Only): Weapons do not alter 3rd person camera paradigm. ADS modifies spread/accuracy or spring arm FOV in character, no 1st person meshes or view switching.
- C5 (Exactly 3 Build Materials): No materials created or referenced. No forbidden materials (Wood, Stone, etc.).
- C6 (Hybrid Hit Detection System): Respects the hybrid model: Assault Rifle (BRWeapon_HitScan) uses server LineTraceSingleByChannel, Rocket Launcher (BRWeapon_Projectile) spawns ABRProjectileRocket actor with UProjectileMovementComponent and radial splash damage.
- C7 (Mandatory BR Prefix): All classes, structs, enums prefixed: ABRWeaponBase, ABRWeapon_HitScan, ABRWeapon_Projectile, ABRProjectileRocket, EBRWeaponState.
- MVP M2 (Dual-Weapon Prototypes): Exactly implementing the 2 prototypes: 1 AR (HitScan) and 1 Rocket Launcher (Projectile + Splash).

## Stage 2: Module Ownership & Scope Assessment
- Assigned module: `Weapons/` inside `BakirkoyBR/Source/BakirkoyBR/Weapons/` and worker directory `.agents/teamwork_preview_worker_weapons_combat/`.
- No modifications outside write boundaries. Minimal changes only.

## Stage 3: Unreal Reflection & Header Hygiene
- Line 1 has `#pragma once`.
- `.generated.h` strictly the last `#include`.
- All `UObject*` member pointers wrapped in `TObjectPtr<T>` with `UPROPERTY()`.
- Zero STL usage (`std::vector`, `std::string` banned).
- Forward declarations used for referenced types in headers.
- Replicated properties declared with `UPROPERTY(ReplicatedUsing = ...)` and callbacks tagged with `UFUNCTION()`.

## Stage 4: Network Authority & Implementation Blueprint
- Dedicated server authority over ammo, weapon states, line traces, projectile spawns, and damage application.
- RPCs with validation (`Server_StartFire`, `Server_StopFire`, `Server_Reload`).
- `DOREPLIFETIME` in `GetLifetimeReplicatedProps` with `#include "Net/UnrealNetwork.h"`.
- Concrete Hit-Scan line trace with damage falloff and headshot multiplier.
- Concrete Projectile rocket with `UProjectileMovementComponent` and radial splash damage with falloff.
- Equip and Holster socket attachment interfaces.

## Stage 5: Verification Hypothesis & Acceptance Gate
- Build/Test command: `pwsh -File scripts/verify-rules.ps1`
- Expected: 100% pass across all suites including Suite 4 codebase static AST and reflection hygiene.
