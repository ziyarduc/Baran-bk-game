---
name: ue5-architecture
description: UE5.6-UE5.8 architecture planning and module boundary design for Unreal projects. Use when requests involve module layout, Build.cs dependencies, reflection exposure strategy, Public/Private API boundaries, naming conventions, and preventing circular dependencies.
---

# Quick Start
- Collect current module list, `*.Build.cs`, and major gameplay/UI systems.
- Propose one target module graph before writing code.
- Output module responsibilities and ownership in a table.

# Workflow
- Identify runtime, editor, UI, networking, and data modules from current codebase.
- Define Public API for each module as minimal headers and Blueprint surface.
- Define Private implementation boundaries and include rules.
- Define `PublicDependencyModuleNames` and `PrivateDependencyModuleNames` per module.
- Report risks: circular includes, over-exposed reflection types, and cross-layer references.

# Constraints
- Keep `UCLASS/USTRUCT/UENUM` only where reflection is required.
- Prefer forward declarations in headers; include concrete headers in `.cpp`.
- Do not move types across modules without listing migration impact.
- Keep naming aligned with Unreal conventions (`U`, `A`, `F`, `E` prefixes).

# Failure Handling
- If ownership of a class is ambiguous, place it in runtime module first and log a TODO to split after usage mapping.
- If dependency graph becomes cyclic, extract shared contracts into a thin common module.
- If Build.cs dependencies are uncertain, choose minimal set and verify compile paths immediately.

# Escalation
- Escalate when a refactor requires asset redirectors, class renames, or package path migration.
- Escalate when module split changes public Blueprint class paths used by existing content.
---

## Bakırköy BR Core Constraints & MVP Directives

When applying this skill to the **Bakırköy BR** project, you MUST strictly adhere to:

### 1. The 7 Core Constraints
1. **No Interior Spaces**: Buildings are exterior-only collision volumes. No interior rooms, furniture, or interior NavMesh. Rooftop/terrace access is strictly via external stairs, ladders, or fire escapes.
2. **Solo BR Only**: First prototype supports Solo mode only. No squad logic, duos, revives, DBNO (Down-But-Not-Out), or team chat.
3. **Server-Authoritative**: Dedicated server validates and executes all gameplay state changes (HP, Shield, ammo, damage, storm, eliminations). Client predicts locally, server reconciles.
4. **3rd Person Camera**: Over-the-shoulder perspective only. ADS tightens camera FOV and spring arm length, but NEVER switches to 1st person.
5. **3 Build Materials**: Exactly 3 materials: Moloz (Debris: 60 start / 100 max HP), Tuğla (Brick: 80 start / 200 max HP), and Çelik (Steel: 100 start / 350 max HP). Never 4 materials.
6. **Hybrid Hit Detection**: AR, SMG, Shotgun, Sniper use server Hit-Scan line traces (`LineTraceSingleByChannel`). Rocket Launcher uses Chaos Projectile physics (`ABRProjectile` actor with 35 m/s velocity and radial splash damage).
7. **Mandatory C++ `BR` Prefix**: Every gameplay class, struct, and enum MUST be prefixed with `BR` (e.g. `ABRCharacter`, `UBRHealthComponent`, `FBRWeaponData`, `EBRBuildMaterial`).

### 2. Demo 1 Playable MVP Directives
- **10 Bots Test Scenario**: AI count is strictly limited to 10 bots. GameMode and AI logic must be optimized for this 10-bot vertical slice.
- **2 Weapon Prototypes**: Initial loot pool and combat mechanics test the hybrid hit detection using exactly 2 weapons: 1 Assault Rifle (Hit-Scan) and 1 Rocket Launcher (Projectile physics + splash damage).
- **Dual GameModes**: Support 2 distinct playable GameModes: Mode 1 Free-For-All (FFA / Deathmatch with score/time limit) and Mode 2 Classic Battle Royale (Last Man Standing with shrinking storm circle).
- **Building System Paused**: Building system is paused for Demo 1. Players and bots rely entirely on natural environment cover (vehicles, alleys, street walls).

