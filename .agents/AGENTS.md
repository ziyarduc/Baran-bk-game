# Bakırköy BR — Project-Wide Agent Rules & Governance

> **Project Root**: `C:\Users\silver\Desktop\bakirkoy-br`  
> **Status**: ACTIVE & MANDATORY FOR ALL AGENTS  
> **Target Engine**: Unreal Engine 5.3+ (C++)

---

## 1. Language Policy
- **System prompts & SKILL.md instructions**: English
- **User-facing documentation & design docs**: Turkish
- **C++ code comments**: English
- **Variable, function, class, and asset names**: English (Unreal Engine convention)

---

## 2. Mandatory Rule Architecture Reference
All agents must comply with the authoritative rule suite located in `.agents/rules/`:
- **Error Prevention & Anti-Patterns**: [`.agents/rules/error-prevention.md`](rules/error-prevention.md)  
  *Mandates `.generated.h` strictly last, `TObjectPtr<>` GC pointer safety, replication boilerplate, and strict prohibition of standard C++ (STL) types.*
- **Constraint Retention Matrix**: [`.agents/rules/constraint-retention.md`](rules/constraint-retention.md)  
  *Enforces the 7 Core Constraints and 5 Playable Demo MVP directives without deviation.*
- **Sequential Thinking Protocol**: [`.agents/rules/sequential-thinking.md`](rules/sequential-thinking.md)  
  *Mandatory 5-stage sequential reasoning protocol required before code generation or architectural modification.*
- **Unreal Analyzer Validation Standards**: [`.agents/rules/unreal-analyzer-validation.md`](rules/unreal-analyzer-validation.md)  
  *AST inspection rules, Clang checks, header hygiene, and reflection validation.*
- **No Interior Spaces**: [`.agents/rules/no-interior.md`](rules/no-interior.md)
- **UE5 Coding Standards**: [`.agents/rules/ue5-coding-standards.md`](rules/ue5-coding-standards.md)
- **Naming Conventions**: [`.agents/rules/naming-conventions.md`](rules/naming-conventions.md)

---

## 3. The 7 Core Constraints (NEVER VIOLATE)
1. **No Interior Spaces**: Buildings are exterior-only solid collision volumes. No interior geometry, no interior rooms, no interior NavMesh, and no indoor gameplay. Players and AI bots access rooftops and terraces via external stairs, ramps, and fire escapes only.
2. **Solo BR Only**: First prototype supports Solo mode only. No Duo/Squad logic, no DBNO (down-but-not-out), and no revive mechanics.
3. **Server-Authoritative**: All gameplay state changes (HP, Shield, ammo, eliminations, storm zones) are server-authoritative. Clients predict for local responsiveness, but the server validates and reconciles with rewind.
4. **3rd Person Camera**: Over-the-shoulder 3rd person perspective only. Aiming Down Sights (ADS) zooms FOV / adjusts camera offset, but never switches to a 1st person mesh or 1st person camera view.
5. **3 Build Materials**: Exactly three (3) materials: `Moloz` (Debris), `Tuğla` (Brick), and `Çelik` (Steel). Strictly NOT 4 materials (no Wood, Stone, Metal, Gold).
6. **Hybrid Hit Detection**: SMG/AR/Sniper/Shotgun/Pistol use LineTrace (Hit-Scan) with server rewind validation. Rocket Launcher / Grenade Launcher use physical simulated projectiles (`ABRProjectile`) with splash damage.
7. **BR Class & Asset Prefix**: All gameplay classes, structs, enums, delegates, and core assets must use the project prefix `BR` (`ABRCharacter`, `UBRHealthComponent`, `FBRWeaponStats`, `EBRMaterialType`, `IBRDamageable`, `BP_BR...`, `DT_BR...`).

---

## 4. Playable Demo MVP Directives
For the immediate playable demo MVP slice, agents must prioritize and respect these 5 directives:
1. **10-Bot MVP Test Scenario**: The total AI bot population is capped at **exactly 10 bots**. GameMode, spawner, and AI controller logic must be optimized specifically for a 10-bot scenario.
2. **2 Weapon Prototypes**: The initial combat system and loot pool feature exactly two weapons to validate hybrid hit detection:
   - 1 Assault Rifle (Hit-Scan line-trace logic).
   - 1 Rocket Launcher (Physical projectile simulation with radial splash damage).
3. **2 Distinct GameModes**: Two playable game modes must be configured and selectable:
   - Mode 1: Free-For-All (FFA / Deathmatch with time and score limit).
   - Mode 2: Classic Battle Royale (shrinking Storm circle, Last Man Standing win condition).
4. **Building System Paused for Demo 1**: Active player grid building development is paused. Players and bots rely entirely on natural urban cover (vehicles, narrow alleys, existing walls, street furniture).
5. **Exterior Vertical Navigation**: Level design focuses on tight urban streets, narrow alleys, and rooftops (vertical gameplay). NavMesh must be properly generated from street level up exterior stairs to rooftops without entering building hulls.

---

## 5. UE5 C++ & Reflection Standards
- **Header Hygiene**: `#pragma once` is mandatory on line 1.
- **Strict Include Order**: `#include "ClassName.generated.h"` **MUST ALWAYS BE THE VERY LAST `#include` DIRECTIVE**. No includes or declarations may follow it.
- **Pointers & GC Safety**: All `UObject*` member pointers must use `TObjectPtr<>` and be annotated with `UPROPERTY()`. Use `TWeakObjectPtr<>` for non-owning cached references.
- **No STL Types**: Do NOT use `std::string`, `std::vector`, `std::map`, or standard pointers. Use Unreal equivalents: `FString`, `FName`, `FText`, `TArray`, `TMap`, `TSet`, `TSharedPtr`.
- **Replication Boilerplate**: Every replicated class must implement `GetLifetimeReplicatedProps` with `DOREPLIFETIME` and include `"Net/UnrealNetwork.h"`. All `OnRep_` functions must be annotated with `UFUNCTION()`.
- **Forward Declarations**: Forward-declare pointer types in headers; place concrete header includes in `.cpp` files.

---

## 6. Mandatory Sequential Thinking Protocol
Before any agent creates or modifies C++ code or submits architectural plans, it MUST execute the **5 Mandatory Thought Stages**:
1. **Stage 1 (Constraint Scan)**: Validate against the 7 Core Constraints and 5 MVP Directives.
2. **Stage 2 (Module Ownership Check)**: Verify file boundaries and follow the minimal change principle.
3. **Stage 3 (UE5 Reflection & Header Safety)**: Check `.generated.h` placement, `TObjectPtr`, `BR` prefix, and no STL types.
4. **Stage 4 (Network Authority & Blueprint)**: Validate server authority, RPC declarations, and edge cases.
5. **Stage 5 (Verification Hypothesis)**: Define exact verification command and pass criteria (`nextThoughtNeeded: false`).

---

## 7. Automated Rule Verification
The project provides an automated PowerShell test suite to verify rule files, constraint retention, and AST/regex patterns:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/verify-rules.ps1
```
All code submissions must pass this script with 0 errors before QA sign-off.

---

## 8. File Organization & Module Ownership
| Module Folder | Contents | Assigned Worker |
|---|---|---|
| `Source/BakirkoyBR/Core/` | GameMode, GameState, PlayerState, PlayerController | GameLoop Worker |
| `Source/BakirkoyBR/Character/` | Player character, movement, camera, health | GameLoop Worker |
| `Source/BakirkoyBR/Weapons/` | Hit-scan AR, Rocket Launcher projectile, damage model | WeaponsCombat Worker |
| `Source/BakirkoyBR/AI/` | 10-Bot AI, BT/StateTree, perception, navigation | AIAgents Worker |
| `Source/BakirkoyBR/Building/` | Paused for Demo 1 (natural cover / exterior props) | Building Worker |
| `Source/BakirkoyBR/GameLoop/` | Storm circle, FFA Deathmatch, Classic BR, loot | GameLoop Worker |
| `Source/BakirkoyBR/Network/` | Hit validation, server rewind, replication | GameLoop Worker |
| `Source/BakirkoyBR/Data/` | `BRTypes.h`, `BRGameConstants.h` | All Workers (coordinated) |
