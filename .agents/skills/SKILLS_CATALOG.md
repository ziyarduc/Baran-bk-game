# Bakırköy BR — Master Skills Catalog

> **Version**: 1.0.0  
> **Project**: Bakırköy Battle Royale (UE5)  
> **Total Curated Skills**: 66  
> **Compliance Gate**: 100% Verified (7 Core Constraints + Demo 1 MVP Directives)  

---

## Executive Summary

This document is the authoritative master catalog for all domain knowledge skills integrated into the **Bakırköy BR** Unreal Engine 5 project. These skills serve as specialized prompt and procedure modules for autonomous AI agent developers, orchestrators, quality reviewers, and system integrators.

The 66 skills originate from three primary sources:
1. **`UnrealXu/UnrealEngine5-Skills` (11 skills)**: Engine version-anchored (UE5.6–5.8) architectural and pipeline routing skills with formal graph stage contracts.
2. **`kevinpbuckley/unreal-engine-skills` (47 core skills)**: Comprehensive, production-grade Unreal C++ skills with modular class structures and in-depth engine source references.
3. **Bakırköy BR Agent Roles (8 skills)**: Custom lead and worker agent personas specifically structured to manage the project's sub-modules (`AI/`, `Building/`, `Core/`, `GameLoop/`, `Map/`, `Weapons/`).

Every skill in this catalog has been rigorously audited and injected with the **7 Non-Negotiable Bakırköy BR Core Constraints** and the **Demo 1 Playable MVP Directives**.

---

## Non-Negotiable Project Directives

### 🔒 The 7 Core Constraints
1. **No Interior Spaces**: All buildings are solid exterior collision volumes. No interior rooms, furniture, or interior NavMesh. Rooftop access is strictly via external stairs, ladders, or fire escapes.
2. **Solo BR Only**: First prototype supports Solo mode only. No squad logic, duos, revives, DBNO (Down-But-Not-Out), or team chat.
3. **Server-Authoritative**: Dedicated server validates and executes all gameplay state changes (HP, Shield, ammo, damage, storm, eliminations). Client predicts locally, server reconciles.
4. **3rd Person Camera**: Over-the-shoulder perspective only. ADS tightens camera FOV and spring arm length, but NEVER switches to 1st person.
5. **3 Build Materials**: Exactly 3 materials: Moloz (Debris: 60 start / 100 max HP), Tuğla (Brick: 80 start / 200 max HP), and Çelik (Steel: 100 start / 350 max HP). Never 4 materials.
6. **Hybrid Hit Detection**: AR, SMG, Shotgun, Sniper use server Hit-Scan line traces (`LineTraceSingleByChannel`). Rocket Launcher uses Chaos Projectile physics (`ABRProjectile` actor with 35 m/s velocity and radial splash damage).
7. **Mandatory C++ `BR` Prefix**: Every gameplay class, struct, and enum MUST be prefixed with `BR` (e.g. `ABRCharacter`, `UBRHealthComponent`, `FBRWeaponData`, `EBRBuildMaterial`).

### 🎯 Demo 1 Playable MVP Directives
- **10 Bots Test Scenario**: AI count is strictly limited to exactly 10 bots. GameMode and AI logic are optimized for this 10-bot vertical slice.
- **2 Weapon Prototypes**: Initial loot pool and combat mechanics test hybrid hit detection using exactly 2 weapons: 1 Assault Rifle (Hit-Scan) and 1 Rocket Launcher (Projectile physics + splash damage).
- **Dual GameModes**: Support 2 distinct playable GameModes: Mode 1 Free-For-All (FFA / Deathmatch with score/time limit) and Mode 2 Classic Battle Royale (Last Man Standing with shrinking storm circle).
- **Building System Paused**: Building system is PAUSED for Demo 1. Players and bots rely entirely on natural environment cover (vehicles, alleys, street walls).

---

## Master Skills Matrix (Overview)

| # | Skill Identifier | Category | Upstream Origin | Target Module / System | References Count |
|---|------------------|----------|-----------------|------------------------|------------------|
| 1 | [`orchestrator`](#orchestrator) | Bakırköy BR Team Leads | BakirkoyBR Agent Roles | Global Coordination / Task Routing | 3 docs |
| 2 | [`qa-reviewer`](#qa-reviewer) | Bakırköy BR Team Leads | BakirkoyBR Agent Roles | Quality Assurance / Rules Enforcement | 3 docs |
| 3 | [`integrator`](#integrator) | Bakırköy BR Team Leads | BakirkoyBR Agent Roles | Module Dependencies & Cross-Compilation | 3 docs |
| 4 | [`worker-ai-agents`](#worker-ai-agents) | Bakırköy BR Specialized Workers | BakirkoyBR Agent Roles | Source/BakirkoyBR/AI/ | 4 docs |
| 5 | [`worker-building-system`](#worker-building-system) | Bakırköy BR Specialized Workers | BakirkoyBR Agent Roles | Source/BakirkoyBR/Building/ (PAUSED for Demo 1) | 3 docs |
| 6 | [`worker-gameloop-backend`](#worker-gameloop-backend) | Bakırköy BR Specialized Workers | BakirkoyBR Agent Roles | Source/BakirkoyBR/Core/, GameLoop/, Character/ | 4 docs |
| 7 | [`worker-map-world`](#worker-map-world) | Bakırköy BR Specialized Workers | BakirkoyBR Agent Roles | Source/BakirkoyBR/Map/, GameLoop/ (Storm, Loot) | 3 docs |
| 8 | [`worker-weapons-combat`](#worker-weapons-combat) | Bakırköy BR Specialized Workers | BakirkoyBR Agent Roles | Source/BakirkoyBR/Weapons/ | 3 docs |
| 9 | [`ue5-architecture`](#ue5-architecture) | UnrealXu Architectural & Pipeline Skills | UnrealXu/UnrealEngine5-Skills | Project Architecture / Build.cs Dependency Graph | 5 docs |
| 10 | [`ue5-auto-assistant`](#ue5-auto-assistant) | UnrealXu Architectural & Pipeline Skills | UnrealXu/UnrealEngine5-Skills | Multi-Agent Intent Routing | 3 docs |
| 11 | [`ue5-blueprint-workflow`](#ue5-blueprint-workflow) | UnrealXu Architectural & Pipeline Skills | UnrealXu/UnrealEngine5-Skills | Content/Blueprints/ & BP Graphs | 3 docs |
| 12 | [`ue5-cpp-gameplay`](#ue5-cpp-gameplay) | UnrealXu Architectural & Pipeline Skills | UnrealXu/UnrealEngine5-Skills | Source/BakirkoyBR/ Core Gameplay Classes | 3 docs |
| 13 | [`ue5-debug-validation`](#ue5-debug-validation) | UnrealXu Architectural & Pipeline Skills | UnrealXu/UnrealEngine5-Skills | Diagnostic & Visual Logging Pipelines | 3 docs |
| 14 | [`ue5-module-router`](#ue5-module-router) | UnrealXu Architectural & Pipeline Skills | UnrealXu/UnrealEngine5-Skills | Engine Module Identification | 1 docs |
| 15 | [`ue5-pcg-building`](#ue5-pcg-building) | UnrealXu Architectural & Pipeline Skills | UnrealXu/UnrealEngine5-Skills | Content/PCG/ Exterior Facades & Roof Access | 4 docs |
| 16 | [`ue5-performance-packaging`](#ue5-performance-packaging) | UnrealXu Architectural & Pipeline Skills | UnrealXu/UnrealEngine5-Skills | Cook, Stage & Shipping Profile | 2 docs |
| 17 | [`ue5-save-load-replication`](#ue5-save-load-replication) | UnrealXu Architectural & Pipeline Skills | UnrealXu/UnrealEngine5-Skills | Source/BakirkoyBR/Network/ & SaveGame | 3 docs |
| 18 | [`ue5-ui-umg-slate`](#ue5-ui-umg-slate) | UnrealXu Architectural & Pipeline Skills | UnrealXu/UnrealEngine5-Skills | Content/UI/ & Source/BakirkoyBR/UI/ | 3 docs |
| 19 | [`ue5-world-interaction`](#ue5-world-interaction) | UnrealXu Architectural & Pipeline Skills | UnrealXu/UnrealEngine5-Skills | Source/BakirkoyBR/Interaction/ & Traces | 3 docs |
| 20 | [`cpp-fundamentals`](#cpp-fundamentals) | Core C++ & Memory Architecture | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/ Reflection & UObject Lifecycle | 3 docs |
| 21 | [`core-types-and-containers`](#core-types-and-containers) | Core C++ & Memory Architecture | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Data/BRTypes.h | 4 docs |
| 22 | [`memory-and-gc`](#memory-and-gc) | Core C++ & Memory Architecture | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/ Pointer & GC Safety | 3 docs |
| 23 | [`timers-and-async`](#timers-and-async) | Core C++ & Memory Architecture | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Core/ Async Tasks & Timers | 4 docs |
| 24 | [`delegates-and-events`](#delegates-and-events) | Core C++ & Memory Architecture | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/ Event Broadcasting | 3 docs |
| 25 | [`logging-and-assertions`](#logging-and-assertions) | Core C++ & Memory Architecture | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/ Logging & Check Macros | 3 docs |
| 26 | [`coding-standards`](#coding-standards) | Build, Modular Plugins & Standards | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/ C++ Standards & BR Prefix | 3 docs |
| 27 | [`module-and-build-system`](#module-and-build-system) | Build, Modular Plugins & Standards | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/BakirkoyBR.Build.cs | 3 docs |
| 28 | [`plugins-and-modules`](#plugins-and-modules) | Build, Modular Plugins & Standards | kevinpbuckley/unreal-engine-skills | BakirkoyBR.uproject Plugins | 3 docs |
| 29 | [`project-structure`](#project-structure) | Build, Modular Plugins & Standards | kevinpbuckley/unreal-engine-skills | Repository Layout & Directory Conventions | 3 docs |
| 30 | [`navigating-engine-source`](#navigating-engine-source) | Build, Modular Plugins & Standards | kevinpbuckley/unreal-engine-skills | UE5 Engine Source References | 3 docs |
| 31 | [`gameplay-framework`](#gameplay-framework) | Gameplay Framework & Movement | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Core/ GameModes & GameStates | 3 docs |
| 32 | [`character-and-movement`](#character-and-movement) | Gameplay Framework & Movement | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Character/ ABRCharacter | 3 docs |
| 33 | [`mover-movement-system`](#mover-movement-system) | Gameplay Framework & Movement | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Character/ Mover Subsystem | 3 docs |
| 34 | [`actors-and-components`](#actors-and-components) | Gameplay Framework & Movement | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/ Component Hierarchies | 4 docs |
| 35 | [`gameplay-ability-system`](#gameplay-ability-system) | Gameplay Framework & Movement | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Abilities/ GAS Setup | 4 docs |
| 36 | [`gameplay-tags`](#gameplay-tags) | Gameplay Framework & Movement | kevinpbuckley/unreal-engine-skills | Config/DefaultGameplayTags.ini & Native Tags | 3 docs |
| 37 | [`gameplay-architecture-planning`](#gameplay-architecture-planning) | Gameplay Framework & Movement | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/ Separation of Concerns | 1 docs |
| 38 | [`enhanced-input`](#enhanced-input) | Input & Control Systems | kevinpbuckley/unreal-engine-skills | Config/ & Content/Input/ IMC & Input Actions | 3 docs |
| 39 | [`networking-and-replication`](#networking-and-replication) | Networking & Replication | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Network/ Replication Graph | 4 docs |
| 40 | [`levels-and-world-partition`](#levels-and-world-partition) | World Partition & Open World Systems | kevinpbuckley/unreal-engine-skills | Content/Maps/ Bakırköy Open World (3.2km×2.1km) | 3 docs |
| 41 | [`landscape-and-foliage`](#landscape-and-foliage) | World Partition & Open World Systems | kevinpbuckley/unreal-engine-skills | Content/Maps/ Terrain & Coastal Foliage | 3 docs |
| 42 | [`asset-management`](#asset-management) | World Partition & Open World Systems | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Data/ Asset Registry | 3 docs |
| 43 | [`physics-and-chaos`](#physics-and-chaos) | Physics & Collision (Chaos) | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Physics/ Chaos & Traces | 3 docs |
| 44 | [`ai-and-navigation`](#ai-and-navigation) | AI, Perception & Navigation | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/AI/ NavMesh & 10 Bots | 4 docs |
| 45 | [`nanite-and-rendering`](#nanite-and-rendering) | Rendering, Nanite & Materials | kevinpbuckley/unreal-engine-skills | Content/Meshes/ Nanite Geometry | 3 docs |
| 46 | [`materials-and-shaders`](#materials-and-shaders) | Rendering, Nanite & Materials | kevinpbuckley/unreal-engine-skills | Content/Materials/ PBR Shaders | 3 docs |
| 47 | [`lighting-and-lumen`](#lighting-and-lumen) | Rendering, Nanite & Materials | kevinpbuckley/unreal-engine-skills | Config/ & Maps/ Lumen Dynamic GI | 3 docs |
| 48 | [`meshes-static-and-skeletal`](#meshes-static-and-skeletal) | Rendering, Nanite & Materials | kevinpbuckley/unreal-engine-skills | Content/Meshes/ Static & Skeletal Hulls | 4 docs |
| 49 | [`animation-system`](#animation-system) | Animation, Control Rig & Cinematics | kevinpbuckley/unreal-engine-skills | Content/Characters/ Animations & State Machines | 4 docs |
| 50 | [`control-rig-and-ik`](#control-rig-and-ik) | Animation, Control Rig & Cinematics | kevinpbuckley/unreal-engine-skills | Content/Characters/ IK & Weapon Aim Offsets | 3 docs |
| 51 | [`sequencer-and-cinematics`](#sequencer-and-cinematics) | Animation, Control Rig & Cinematics | kevinpbuckley/unreal-engine-skills | Content/Cinematics/ Match Start & Winner Sequence | 4 docs |
| 52 | [`niagara-vfx`](#niagara-vfx) | VFX (Niagara) & Audio (MetaSounds) | kevinpbuckley/unreal-engine-skills | Content/VFX/ Weapon Tracers & Storm Boundary | 3 docs |
| 53 | [`audio-and-metasounds`](#audio-and-metasounds) | VFX (Niagara) & Audio (MetaSounds) | kevinpbuckley/unreal-engine-skills | Content/Audio/ MetaSounds Outdoor Acoustics | 4 docs |
| 54 | [`umg-and-slate`](#umg-and-slate) | UI Systems (UMG & Slate) | kevinpbuckley/unreal-engine-skills | Content/UI/ Solo BR & FFA HUDs | 6 docs |
| 55 | [`blueprint-fundamentals`](#blueprint-fundamentals) | Blueprint & C++ Interop | kevinpbuckley/unreal-engine-skills | Content/Blueprints/ Logic Graphs | 3 docs |
| 56 | [`blueprint-cpp-integration`](#blueprint-cpp-integration) | Blueprint & C++ Interop | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/ BP Exposing Macros | 3 docs |
| 57 | [`debugging-techniques`](#debugging-techniques) | Profiling, Debugging & Test Automation | kevinpbuckley/unreal-engine-skills | Diagnostics & Gameplay Debugger Overlay | 3 docs |
| 58 | [`profiling-and-optimization`](#profiling-and-optimization) | Profiling, Debugging & Test Automation | kevinpbuckley/unreal-engine-skills | Unreal Insights & Frame Profiling | 4 docs |
| 59 | [`game-thread-performance`](#game-thread-performance) | Profiling, Debugging & Test Automation | kevinpbuckley/unreal-engine-skills | Tick Optimization & Game Thread Budget | 0 docs |
| 60 | [`automation-and-testing`](#automation-and-testing) | Profiling, Debugging & Test Automation | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Tests/ Automation Specs | 4 docs |
| 61 | [`editor-scripting-and-python`](#editor-scripting-and-python) | Editor Scripting & Packaging | kevinpbuckley/unreal-engine-skills | Scripts/ & Editor Automation (port 6776) | 3 docs |
| 62 | [`packaging-and-deployment`](#packaging-and-deployment) | Editor Scripting & Packaging | kevinpbuckley/unreal-engine-skills | Binaries/ & Packaged Game Builds | 4 docs |
| 63 | [`importing-content`](#importing-content) | Editor Scripting & Packaging | kevinpbuckley/unreal-engine-skills | Content/ Pipeline for Meshes & Textures | 3 docs |
| 64 | [`save-and-load`](#save-and-load) | Data Systems & Subsystems | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Data/ SaveGame State | 3 docs |
| 65 | [`data-driven-design`](#data-driven-design) | Data Systems & Subsystems | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Data/ DataTables & DataAssets | 4 docs |
| 66 | [`subsystems`](#subsystems) | Data Systems & Subsystems | kevinpbuckley/unreal-engine-skills | Source/BakirkoyBR/Subsystems/ Persistent Singletons | 3 docs |

---

## Category & Skill Detailed Catalog

### Bakırköy BR Team Leads
*Total Skills in this Category: 3*

#### <a id="orchestrator"></a>`orchestrator`
- **Path**: `.agents/skills/orchestrator/SKILL.md`
- **Origin**: BakirkoyBR Agent Roles
- **Target Module**: `Global Coordination / Task Routing`
- **Description**: Master orchestrator agent for the Bakırköy BR game project. Use this skill when coordinating multi-agent game development tasks, assigning work to worker agents, reviewing progress, and managing cross-system dependencies. This is the conductor that drives the entire development pipeline.
- **In-Depth References**: `review-protocol.md`, `task-queue.md`, `team-roster.md`
- **Bakırköy BR Domain Adaptation**:
  - **Demo 1 Alignment**: Prioritize vertical slice tasks: 10 bots scenario, 2 weapon prototypes (AR Hit-Scan + Rocket Launcher Projectile), exterior NavMesh, dual GameModes, paused building.
  - **Constraint Enforcement**: Gate all worker tasks against the 7 Core Constraints. Reject any task that introduces interior spaces, squads/duos, client authority, or 1st person cameras.

#### <a id="qa-reviewer"></a>`qa-reviewer`
- **Path**: `.agents/skills/qa-reviewer/SKILL.md`
- **Origin**: BakirkoyBR Agent Roles
- **Target Module**: `Quality Assurance / Rules Enforcement`
- **Description**: Quality assurance agent that reviews all code produced by worker agents in the Bakırköy BR project. Use this skill when reviewing UE5 C++ code for correctness, coding standards compliance, replication safety, and alignment with the System Design Document.
- **In-Depth References**: `code-standards.md`, `review-checklist.md`, `ue5-best-practices.md`
- **Bakırköy BR Domain Adaptation**:
  - **Constraint Checklist**:
    * [ ] Zero interior spaces, zero interior NavMesh
    * [ ] Solo mode only (no squad arrays, no revive logic)
    * [ ] Server-authoritative gameplay state (HP, damage, storm)
    * [ ] 3rd person camera only (ADS zooms FOV/spring arm, no 1st person)
    * [ ] 3 build materials only (Moloz, Tuğla, Çelik) - building paused for Demo 1
    * [ ] Hybrid hit detection (AR=Hit-Scan, Rocket=Projectile)
    * [ ] All C++ classes prefixed with `BR`
  - **Demo 1 MVP Verification**: Confirm 10 bots scenario, 2 weapon prototypes, and dual GameModes.

#### <a id="integrator"></a>`integrator`
- **Path**: `.agents/skills/integrator/SKILL.md`
- **Origin**: BakirkoyBR Agent Roles
- **Target Module**: `Module Dependencies & Cross-Compilation`
- **Description**: Integration testing agent that validates cross-module compatibility in the Bakırköy BR project. Use this skill when checking that code from different worker agents compiles together, shared types are consistent, and the module dependency graph is respected.
- **In-Depth References**: `compile-test.md`, `dependency-graph.md`, `integration-map.md`
- **Bakırköy BR Domain Adaptation**:
  - **Cross-Module Verification**: Verify all modules use `BR` prefix (`BRTypes.h`, `ABRCharacter`, `ABRWeaponBase`).
  - **Dependency Guard**: Ensure AI, Map, and Combat modules do not reference building system during Demo 1.
  - **GameMode Compatibility**: Verify both FFA and Classic BR GameModes compile cleanly with shared character and weapon types.

### Bakırköy BR Specialized Workers
*Total Skills in this Category: 5*

#### <a id="worker-ai-agents"></a>`worker-ai-agents`
- **Path**: `.agents/skills/worker-ai-agents/SKILL.md`
- **Origin**: BakirkoyBR Agent Roles
- **Target Module**: `Source/BakirkoyBR/AI/`
- **Description**: Worker agent responsible for the bot AI system in the Bakırköy BR project. Use this skill when implementing the FSM state machine, AI perception, agent roles (Assault/Sniper/Support), AI skills (Flanking, High Ground, Suppression), pathfinding, and crowd avoidance.
- **In-Depth References**: `agent-roles.md`, `fsm-design.md`, `pathfinding.md`, `perception-system.md`
- **Bakırköy BR Domain Adaptation**:
  - **10 Bots Scenario**: Focus entirely on a 10-bot test scenario.
  - **Combat & Looting Priority**:
    * 10 bots actively navigate to loot spawns and equip either AR Hit-Scan or Rocket Launcher Projectile.
    * Bots engage player and each other using Hit-Scan and Projectile weapon attacks.
    * Bots use natural cover (vehicles, alley walls) rather than building structures.
  - **Vertical Navigation**: NavMesh and behavior trees must guide bots up exterior stairs and fire escapes from streets to rooftops.
  - **No Interior Entry**: Bots must never enter building interiors.

#### <a id="worker-building-system"></a>`worker-building-system`
- **Path**: `.agents/skills/worker-building-system/SKILL.md`
- **Origin**: BakirkoyBR Agent Roles
- **Target Module**: `Source/BakirkoyBR/Building/ (PAUSED for Demo 1)`
- **Description**: Worker agent responsible for the building/construction system in the Bakırköy BR project. Use this skill when implementing build piece placement, material gathering, build preview, structure editing, turbo build, or structure destruction mechanics.
- **In-Depth References**: `build-pieces.md`, `edit-system.md`, `materials.md`
- **Bakırköy BR Domain Adaptation**:
  - **STATUS: PAUSED FOR DEMO 1**: Per user directive, the building system is PAUSED for Demo 1 to focus on shooting, movement, and 10-bot combat.
  - **3 Materials Constraint**: When development resumes, strictly 3 materials must be implemented: Moloz (60/100 HP), Tuğla (80/200 HP), Çelik (100/350 HP). Never 4 materials.
  - **Natural Cover**: Ensure code allows bots and players to use natural environment props for cover.

#### <a id="worker-gameloop-backend"></a>`worker-gameloop-backend`
- **Path**: `.agents/skills/worker-gameloop-backend/SKILL.md`
- **Origin**: BakirkoyBR Agent Roles
- **Target Module**: `Source/BakirkoyBR/Core/, GameLoop/, Character/`
- **Description**: Worker agent responsible for core game systems, character controller, and network infrastructure in the Bakırköy BR project. Use this skill when implementing GameMode, GameState, PlayerState, character movement, health system, hit validation, server rewind, skydiving mechanics, or network replication.
- **In-Depth References**: `hit-detection.md`, `replication.md`, `server-architecture.md`, `skydiving.md`
- **Bakırköy BR Domain Adaptation**:
  - **Demo 1 GameModes**:
    1. `BRGameMode_FFA`: Free-For-All deathmatch (score/kill limit).
    2. `BRGameMode_BR`: Classic Solo Battle Royale with 7-phase shrinking storm circle.
  - **10-Bot Scenario**: Implement match startup and spawn point distribution for 1 player + 10 bots.
  - **Server Authority**: Health, Shield, storm phase, and player eliminations run strictly on dedicated server.

#### <a id="worker-map-world"></a>`worker-map-world`
- **Path**: `.agents/skills/worker-map-world/SKILL.md`
- **Origin**: BakirkoyBR Agent Roles
- **Target Module**: `Source/BakirkoyBR/Map/, GameLoop/ (Storm, Loot)`
- **Description**: Worker agent responsible for the Bakırköy BR map, world systems, storm circle, loot spawning, and safe zone management. Use this skill when implementing POI configurations, storm circle algorithms, loot tier systems, or NavMesh setup.
- **In-Depth References**: `navmesh-guide.md`, `poi-specs.md`, `storm-circle.md`
- **Bakırköy BR Domain Adaptation**:
  - **Demo 1 Focus**: Narrow urban streets, alleys, and rooftops emphasizing vertical gameplay.
  - **Exterior Only**: All buildings are solid exterior hulls. No interior geometry or interior NavMesh.
  - **Exterior Stairs & Fire Escapes**: Design and place outdoor stairs and ladders connecting street level to rooftops.
  - **Street-to-Rooftop NavMesh**: Verify NavMesh properly connects street level to rooftops via exterior stairs.
  - **Natural Cover**: Place vehicles, dumpsters, concrete planters, and walls across streets for tactical combat.

#### <a id="worker-weapons-combat"></a>`worker-weapons-combat`
- **Path**: `.agents/skills/worker-weapons-combat/SKILL.md`
- **Origin**: BakirkoyBR Agent Roles
- **Target Module**: `Source/BakirkoyBR/Weapons/`
- **Description**: Worker agent responsible for the weapon system, damage model, and equipment in the Bakırköy BR project. Use this skill when implementing weapon classes, hit-scan/projectile mechanics, ADS, spray patterns, reload systems, damage falloff, or consumable items.
- **In-Depth References**: `damage-model.md`, `equipment-specs.md`, `weapon-stats.md`
- **Bakırköy BR Domain Adaptation**:
  - **Demo 1 MVP Focus**: Implement and test exactly 2 weapon prototypes first:
    1. Assault Rifle "İstanbul Fırtınası": Hit-Scan, server line trace, 8 rps, 35m falloff.
    2. Rocket Launcher "Deprem": Projectile physics, `ABRProjectile` actor, 35 m/s speed, radial splash damage.
  - **Hybrid System**: Test both Hit-Scan and Projectile code paths thoroughly on server.

### UnrealXu Architectural & Pipeline Skills
*Total Skills in this Category: 11*

#### <a id="ue5-architecture"></a>`ue5-architecture`
- **Path**: `.agents/skills/ue5-architecture/SKILL.md`
- **Origin**: UnrealXu/UnrealEngine5-Skills
- **Target Module**: `Project Architecture / Build.cs Dependency Graph`
- **Description**: UE5.6-UE5.8 architecture planning and module boundary design for Unreal projects. Use when requests involve module layout, Build.cs dependencies, reflection exposure strategy, Public/Private API boundaries, naming conventions, and preventing circular dependencies.
- **In-Depth References**: `build-cs-patterns.md`, `module-layout.md`, `project-adapter.md`, `ue5-engine-module-index-v2.md`, `ue5-engine-module-index.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="ue5-auto-assistant"></a>`ue5-auto-assistant`
- **Path**: `.agents/skills/ue5-auto-assistant/SKILL.md`
- **Origin**: UnrealXu/UnrealEngine5-Skills
- **Target Module**: `Multi-Agent Intent Routing`
- **Description**: UE5.6-UE5.8 automatic assistant entry for beginners. Use when users ask Unreal questions without naming a specific skill. Auto-route to the most precise UE5 skill and recommend dedicated MCP tools.
- **In-Depth References**: `beginner-smoke-prompts.md`, `mcp-skill-mapping.md`, `natural-language-triggers.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="ue5-blueprint-workflow"></a>`ue5-blueprint-workflow`
- **Path**: `.agents/skills/ue5-blueprint-workflow/SKILL.md`
- **Origin**: UnrealXu/UnrealEngine5-Skills
- **Target Module**: `Content/Blueprints/ & BP Graphs`
- **Description**: UE5.6-UE5.8 Blueprint graph workflow for feature implementation, input events, node wiring, and graph validation. Use when requests involve adding Blueprint logic, keyboard input behavior, function chains, event graph edits, or pin-level connection guidance.
- **In-Depth References**: `bp-node-patterns.md`, `hotkey-fast-path.md`, `project-adapter.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="ue5-cpp-gameplay"></a>`ue5-cpp-gameplay`
- **Path**: `.agents/skills/ue5-cpp-gameplay/SKILL.md`
- **Origin**: UnrealXu/UnrealEngine5-Skills
- **Target Module**: `Source/BakirkoyBR/ Core Gameplay Classes`
- **Description**: UE5.6-UE5.8 gameplay C++ implementation for Actors, Components, DataAssets, and gameplay logic. Use when requests ask to write .h/.cpp pairs, expose UPROPERTY/UFUNCTION to Blueprint, use GameplayTags, or build reusable component-based systems.
- **In-Depth References**: `cpp-class-template.md`, `project-adapter.md`, `reflection-macro-checklist.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="ue5-debug-validation"></a>`ue5-debug-validation`
- **Path**: `.agents/skills/ue5-debug-validation/SKILL.md`
- **Origin**: UnrealXu/UnrealEngine5-Skills
- **Target Module**: `Diagnostic & Visual Logging Pipelines`
- **Description**: UE5.6-UE5.8 debugging and validation workflow for logs, asset checks, and regression triage. Use when requests involve troubleshooting why gameplay does not work, validating expected output, narrowing minimal repro, and producing concrete fix steps.
- **In-Depth References**: `log-triage.md`, `minimal-repro-template.md`, `project-adapter.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="ue5-module-router"></a>`ue5-module-router`
- **Path**: `.agents/skills/ue5-module-router/SKILL.md`
- **Origin**: UnrealXu/UnrealEngine5-Skills
- **Target Module**: `Engine Module Identification`
- **Description**: Route UE5.6-UE5.8 questions to the most precise skill using module names, aliases, intent keywords, and layer context. Works for explicit module prompts (RenderCore, AIModule, AssetRegistry) and natural language requests.
- **In-Depth References**: `routing-policy.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="ue5-pcg-building"></a>`ue5-pcg-building`
- **Path**: `.agents/skills/ue5-pcg-building/SKILL.md`
- **Origin**: UnrealXu/UnrealEngine5-Skills
- **Target Module**: `Content/PCG/ Exterior Facades & Roof Access`
- **Description**: UE5.6-UE5.8 PCG building generation workflow for modular buildings, blockouts, facade rules, and runtime generation. Use when requests involve Procedural Content Generation (PCG), Shape Grammar, lot-based building spawn, deterministic random seeds, density/filter pipelines, or converting designer constraints into reusable PCG graphs.
- **In-Depth References**: `pcg-building-graph-patterns.md`, `project-adapter.md`, `runtime-generation-validation.md`, `shape-grammar-building-pattern.md`
- **Bakırköy BR Domain Adaptation**:
  - **Exterior Only**: PCG graphs must ONLY generate exterior facade shells and bounding collision hulls. Never generate internal partitions, rooms, doors, or furniture.
  - **Rooftop Navigation**: Generate external staircases, scaffolding, or fire escapes on building exteriors to enable vertical gameplay to rooftops.
  - **NavMesh Exclusion**: Ensure generated building footprints write to `NavArea_Null` so navigation mesh generates exclusively on outdoor streets, alleys, and exterior stairways.

#### <a id="ue5-performance-packaging"></a>`ue5-performance-packaging`
- **Path**: `.agents/skills/ue5-performance-packaging/SKILL.md`
- **Origin**: UnrealXu/UnrealEngine5-Skills
- **Target Module**: `Cook, Stage & Shipping Profile`
- **Description**: UE5.6-UE5.8 performance and packaging readiness workflow. Use when requests involve PIE performance checks, runtime stat review, pre-package validation, build configuration sanity, and release readiness checklists.
- **In-Depth References**: `prepackage-checklist.md`, `project-adapter.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="ue5-save-load-replication"></a>`ue5-save-load-replication`
- **Path**: `.agents/skills/ue5-save-load-replication/SKILL.md`
- **Origin**: UnrealXu/UnrealEngine5-Skills
- **Target Module**: `Source/BakirkoyBR/Network/ & SaveGame`
- **Description**: UE5.6-UE5.8 save/load and multiplayer replication workflow for gameplay systems. Use when requests involve SaveGame schema design, serialization, restore pipelines, RepNotify handling, RPC entry points, and server-authoritative validation.
- **In-Depth References**: `project-adapter.md`, `replication-checklist.md`, `savegame-schema-pattern.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="ue5-ui-umg-slate"></a>`ue5-ui-umg-slate`
- **Path**: `.agents/skills/ue5-ui-umg-slate/SKILL.md`
- **Origin**: UnrealXu/UnrealEngine5-Skills
- **Target Module**: `Content/UI/ & Source/BakirkoyBR/UI/`
- **Description**: UE5.6-UE5.8 UI development workflow using UMG and Slate integration. Use when requests involve Widget Blueprint setup, Slate host widgets, lifecycle binding, input and focus handling, tooltip behavior, or viewport clamping logic.
- **In-Depth References**: `project-adapter.md`, `tooltip-patterns.md`, `umg-slate-bridge.md`
- **Bakırköy BR Domain Adaptation**:
  - **Solo BR & FFA HUD**: HUD displays player Health, Shield, weapon ammo, alive player count (out of 11: 1 player + 10 bots), and storm timer / score tracker.
  - **No Squad UI**: Do not create teammate status panels, squad markers, or revive indicators.
  - **3rd Person Crosshair**: Reticle centered on 3rd person aim point with hit markers and damage numbers.

#### <a id="ue5-world-interaction"></a>`ue5-world-interaction`
- **Path**: `.agents/skills/ue5-world-interaction/SKILL.md`
- **Origin**: UnrealXu/UnrealEngine5-Skills
- **Target Module**: `Source/BakirkoyBR/Interaction/ & Traces`
- **Description**: UE5.6-UE5.8 world interaction systems for pickups, spawners, overlap/trace checks, and visual feedback. Use when requests involve interactive world actors, spawn logic, pickup behavior, interaction radius checks, success/failure feedback, and actor lifecycle control.
- **In-Depth References**: `pickup-actor-pattern.md`, `project-adapter.md`, `spawner-randomization.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

### Core C++ & Memory Architecture
*Total Skills in this Category: 6*

#### <a id="cpp-fundamentals"></a>`cpp-fundamentals`
- **Path**: `.agents/skills/cpp-fundamentals/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/ Reflection & UObject Lifecycle`
- **Description**: Write correct Unreal Engine C++ using the UObject reflection system — UCLASS/USTRUCT/ UENUM/UINTERFACE macros, UPROPERTY and UFUNCTION specifiers, GENERATED_BODY, the *.generated.h pipeline, class prefixes (U/A/F/E/I), module API export macros, the Class Default Object (CDO), NewObject vs CreateDefaultSubobject, garbage-collection-safe ownership, and UClass vs UScriptStruct internals. Use when authoring or editing any UE C++ class, exposing members or functions to Blueprints or replication, fixing UHT/reflection build errors, or choosing between pointer and ownership types.
- **In-Depth References**: `object-creation-and-gc.md`, `reflection-macros.md`, `uobject-lifecycle-and-cdo.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="core-types-and-containers"></a>`core-types-and-containers`
- **Path**: `.agents/skills/core-types-and-containers/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Data/BRTypes.h`
- **Description**: Use Unreal's core C++ types instead of the standard library — containers (TArray, TMap, TSet, TQueue, TArrayView), string types (FString, FName, FText, TStringBuilder) with conversion patterns and localization rules, math types (FVector, FRotator, FQuat, FTransform) with Large World Coordinates (LWC/double precision), and utility types (TOptional, TVariant, TTuple). Use when writing any UE C++ that stores collections, manipulates strings, does 3D math, or when choosing between FString/FName/ FText, between std:: and UE containers, or between FRotator and FQuat for rotation.
- **In-Depth References**: `containers.md`, `math-types.md`, `strings-and-text.md`, `utility-types.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="memory-and-gc"></a>`memory-and-gc`
- **Path**: `.agents/skills/memory-and-gc/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/ Pointer & GC Safety`
- **Description**: Manage UObject lifetime and plain C++ memory in Unreal Engine. Covers the garbage collector reachability cycle and root set, keeping UObjects alive with UPROPERTY and TObjectPtr, non-owning TWeakObjectPtr, path-only TSoftObjectPtr, TStrongObjectPtr for non-UObject owners, FGCObject::AddReferencedObjects, AddToRoot/RemoveFromRoot, MarkAsGarbage and IsValid checks, and the non-UObject smart pointers TSharedPtr/TSharedRef/TWeakPtr/TUniquePtr and MakeShared. Use when choosing a pointer or ownership type, debugging crashes after garbage collection, investigating dangling pointer or use-after-free bugs, holding UObjects from non-UObject classes, or picking between TSharedPtr and TUniquePtr for plain C++ objects.
- **In-Depth References**: `object-pointer-types.md`, `smart-pointers.md`, `uobject-gc-and-roots.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="timers-and-async"></a>`timers-and-async`
- **Path**: `.agents/skills/timers-and-async/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Core/ Async Tasks & Timers`
- **Description**: Schedule and defer work in Unreal C++ — FTimerManager (SetTimer with FTimerHandle, looping and one-shot timers, SetTimerForNextTick, ClearTimer, PauseTimer/UnPauseTimer, timer delegates with payloads), async work (Async/EAsyncExecution, AsyncTask/ENamedThreads, TFuture/TPromise, FNonAbandonableTask/FAutoDeleteAsyncTask/FAsyncTask, FRunnable/FRunnableThread, the UE Tasks System UE::Tasks::Launch/FTask/FPipe), FTSTicker for non-actor ticking, thread-safety and game-thread marshaling, latent actions overview. Use when implementing a delay or repeating callback, replacing per-frame Tick with a periodic timer, deferring one frame, offloading CPU-heavy work to a background thread, or building a non-actor ticker. Cross-references actors-and-components (EndPlay cleanup) and delegates-and-events.
- **In-Depth References**: `async-and-tasks.md`, `threads-and-runnables.md`, `tickers-and-latent.md`, `timer-manager.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="delegates-and-events"></a>`delegates-and-events`
- **Path**: `.agents/skills/delegates-and-events/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/ Event Broadcasting`
- **Description**: Wire up callbacks and events in Unreal C++ using delegates — single-cast (DECLARE_DELEGATE, DECLARE_DELEGATE_RetVal, payload variables), multicast (DECLARE_MULTICAST_DELEGATE, DECLARE_TS_MULTICAST_DELEGATE), and dynamic (DECLARE_DYNAMIC_MULTICAST_DELEGATE, BlueprintAssignable, AddDynamic, RemoveDynamic). Covers all binding forms (BindUObject, AddUObject, BindLambda, AddWeakLambda, BindRaw, AddSP), execution (Execute, ExecuteIfBound, Broadcast), FDelegateHandle lifetime management, safe unbinding, and DECLARE_EVENT. Use when implementing the observer pattern, exposing C++ events to Blueprints, decoupling game systems, binding overlap/hit/ability callbacks, or debugging delegate crashes and silent no-ops.
- **In-Depth References**: `binding-and-lifetime.md`, `delegate-types-matrix.md`, `dynamic-and-blueprint.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="logging-and-assertions"></a>`logging-and-assertions`
- **Path**: `.agents/skills/logging-and-assertions/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/ Logging & Check Macros`
- **Description**: Add structured logging and runtime checks to Unreal C++ — UE_LOG with custom log categories (DECLARE_LOG_CATEGORY_EXTERN/DEFINE_LOG_CATEGORY), all seven verbosity levels (Fatal/Error/Warning/Display/Log/Verbose/VeryVerbose), structured named-field logging with UE_LOGFMT, the assertion families check/checkf (halts, compiled out in shipping), verify/verifyf (expression always evaluates), ensure/ensureMsgf/ensureAlways (non-fatal, reports once), and the FMsg/FDebug helpers. Use when adding diagnostics to gameplay or engine code, defining a dedicated log category for a module or feature, choosing between crashing and recovering on a bad assumption, printing transient values to screen during PIE, filtering log output by category, or debugging shipping-only crashes where ensures would help.
- **In-Depth References**: `assertions.md`, `log-categories-and-verbosity.md`, `structured-logging.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

### Build, Modular Plugins & Standards
*Total Skills in this Category: 5*

#### <a id="coding-standards"></a>`coding-standards`
- **Path**: `.agents/skills/coding-standards/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/ C++ Standards & BR Prefix`
- **Description**: Write Unreal C++ that conforms to Epic's coding standard — type prefixes (U/A/F/E/I/T/S), PascalCase naming, the bBool prefix, enum class style, Allman braces, tab indentation, const correctness, nullptr/override/final usage, TEXT() string literals, include order with generated.h last, IWYU and forward declarations, API export macros (MODULE_API), UPROPERTY/UFUNCTION specifiers with Category, TObjectPtr for UObject members, and engine types over std containers. Use when writing or reviewing any UE C++, naming types or members, structuring headers, or making code consistent with the engine and surrounding project code.
- **In-Depth References**: `formatting-and-includes.md`, `naming-conventions.md`, `reflection-and-uht.md`
- **Bakırköy BR Domain Adaptation**:
  - **Mandatory `BR` Prefix**: Every gameplay class, struct, and enum in Bakırköy BR MUST start with `BR`:
    * `ABRCharacter`, `ABRPlayerController`, `ABRGameModeBase`
    * `UBRHealthComponent`, `UBRPerceptionComponent`
    * `FBRWeaponData`, `FBRLootSpawnRow`
    * `EBRHitScanType`, `EBRGameModeType`
  - **Reflection & GC**: Always use `UPROPERTY()`, `UFUNCTION()`, `TObjectPtr<T>`, and `#include "ClassName.generated.h"` as the final include.

#### <a id="module-and-build-system"></a>`module-and-build-system`
- **Path**: `.agents/skills/module-and-build-system/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/BakirkoyBR.Build.cs`
- **Description**: Structure Unreal C++ into modules and configure the build with *.Build.cs (ModuleRules) and *.Target.cs (TargetRules). Use when creating a new module, splitting code out of an existing module, adding a dependency, fixing "unresolved external symbol" / cannot open include file" / "module not found" link errors, choosing public vs private dependencies, wiring IMPLEMENT_MODULE / IMPLEMENT_PRIMARY_GAME_MODULE / IModuleInterface, setting the module loading phase or host type, or understanding how UnrealBuildTool (UBT) discovers and compiles modules. Related to plugins: see plugins-and-modules for packaging modules inside .uplugin files.
- **In-Depth References**: `build-cs-reference.md`, `module-cpp-and-phases.md`, `target-cs-reference.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="plugins-and-modules"></a>`plugins-and-modules`
- **Path**: `.agents/skills/plugins-and-modules/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `BakirkoyBR.uproject Plugins`
- **Description**: Create, structure, and manage Unreal Engine plugins — the .uplugin descriptor (FileVersion, Modules array, CanContainContent, EnabledByDefault, Plugins dependencies), plugin folder layout (Source/Content/Resources), EHostType module types (Runtime, Editor, Developer, UncookedOnly, ServerOnly, ClientOnly) and ELoadingPhase values, IModuleInterface StartupModule/ShutdownModule, IPluginManager/IPlugin runtime queries, content-only plugins, engine vs project plugins, explicit-load plugins, plugin dependency hierarchy, and packaging for distribution. Use when creating a reusable plugin, deciding plugin vs project module, structuring an editor or runtime plugin, wiring plugin module C++, enabling plugins in a project, or troubleshooting a plugin that won't load or whose content won't mount.
- **In-Depth References**: `plugin-dependencies-and-packaging.md`, `plugin-structure-and-modules.md`, `uplugin-descriptor.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="project-structure"></a>`project-structure`
- **Path**: `.agents/skills/project-structure/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Repository Layout & Directory Conventions`
- **Description**: Navigate and configure an Unreal Engine project — the .uproject descriptor (FProjectDescriptor: FileVersion, EngineAssociation, Modules, Plugins), the standard folder layout (Config/ with Default*.ini files, Content/, Source/ with the primary game module, Plugins/, and the generated Binaries/Intermediate/DerivedDataCache/Saved/ folders), the config file hierarchy and ini syntax (sections, array operators, UPROPERTY(config), GConfig), content virtual paths (/Game/ /Engine/), and which files to source-control versus ignore. Use when creating or opening a project, editing .uproject modules or plugin references, changing project settings via Config Default*.ini instead of the editor, deciding what to commit to Git/Perforce, writing a .gitignore, understanding EngineAssociation values, registering a primary game module, or debugging wrong engine version" / "stale generated headers" / config-not-applying problems.
- **In-Depth References**: `config-system.md`, `folder-layout-and-vcs.md`, `uproject-and-modules.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="navigating-engine-source"></a>`navigating-engine-source`
- **Path**: `.agents/skills/navigating-engine-source/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `UE5 Engine Source References`
- **Description**: Locate, read, and cite exact Unreal Engine APIs in the on-disk engine source instead of guessing. Use when you need a real function signature, class hierarchy, UPROPERTY/UFUNCTION specifier, module name, or include path; when verifying that an API exists in UE 5.8; when resolving "which module do I add to Build.cs?"; or when an API changed between engine versions. Covers the full source tree layout (Runtime/Editor/ Developer/Plugins), the Public/Private/Classes folder convention, UHT-generated files, naming prefixes as navigation hints, IWYU include rules, and repeatable search patterns for finding any class, function, or type from first principles.
- **In-Depth References**: `finding-apis.md`, `module-map.md`, `source-conventions.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

### Gameplay Framework & Movement
*Total Skills in this Category: 7*

#### <a id="gameplay-framework"></a>`gameplay-framework`
- **Path**: `.agents/skills/gameplay-framework/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Core/ GameModes & GameStates`
- **Description**: Implement Unreal's gameplay framework in C++ — GameInstance, AGameModeBase/AGameMode, AGameStateBase/AGameState, APlayerController, APawn/ACharacter, APlayerState, and AHUD — including the server-only spawn/login flow, possession, controller-pawn lifecycle, and which class each piece of logic belongs in. Use when setting up game rules, default pawn/controller classes, player login/spawn/possession, replicated game or player state, match-state machines, respawn logic, or deciding "where does this code live?
- **In-Depth References**: `controllers-and-pawns.md`, `gamemode-and-state.md`, `init-and-login-flow.md`
- **Bakırköy BR Domain Adaptation**:
  - **Dual GameModes**:
    1. `ABRGameMode_FFA`: Free-For-All deathmatch with score/kill limit and match countdown timer.
    2. `ABRGameMode_BR`: Classic Battle Royale with 7-phase shrinking storm circle and Last Man Standing victory condition.
  - **Solo BR Architecture**: `ABRGameState` and `ABRPlayerState` track individual players and bots only. No squad structures, team IDs, or shared inventories.
  - **10-Bot Match Loop**: Server spawns 1 player and 10 bots across outdoor spawn points.
  - **Server Authority**: All state transitions (match state, storm phase, score, eliminations) execute strictly on the server.

#### <a id="character-and-movement"></a>`character-and-movement`
- **Path**: `.agents/skills/character-and-movement/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Character/ ABRCharacter`
- **Description**: Implement player/AI characters in Unreal C++ with ACharacter and UCharacterMovementComponent — capsule/mesh setup, movement modes (walking/falling/flying/swimming/custom), rotation behaviors, jumping, crouching, root motion sources, client-predicted networked movement, and the experimental Mover plugin successor. Use when creating or configuring a Character class, setting movement speeds/gravity/air-control, overriding a custom movement mode (PhysCustom), adding root motion, or debugging network smoothing and prediction on a character.
- **In-Depth References**: `movement-modes-and-custom.md`, `networked-movement.md`, `root-motion-and-launch.md`
- **Bakırköy BR Domain Adaptation**:
  - **3rd Person Camera**: Player character `ABRCharacter` must use an over-the-shoulder camera setup with `USpringArmComponent` (TargetArmLength ~250cm, SocketOffset ~[0, 50, 20]).
  - **ADS Zoom Only**: Aim Down Sights (ADS) tightens the spring arm and lowers camera FOV, but MUST NEVER transition to a first-person camera or mesh hide.
  - **Server-Authoritative Movement**: Use standard `UCharacterMovementComponent` with client prediction and server validation.
  - **Building Mode Paused**: Build mode inputs and component activation are disabled for Demo 1.

#### <a id="mover-movement-system"></a>`mover-movement-system`
- **Path**: `.agents/skills/mover-movement-system/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Character/ Mover Subsystem`
- **Description**: Implement actor movement with Unreal's experimental Mover plugin (UE 5.8) — the modular, rollback-networked successor to CharacterMovementComponent. Covers UMoverComponent / UCharacterMoverComponent setup, producing input via IMoverInputProducerInterface and FCharacterDefaultInputs, movement modes and transitions, layered moves, instant movement effects, movement modifiers (stance/crouch), shared settings (UCommonLegacyMovementSettings), sync state queries, and backend selection (Network Prediction, Chaos networked physics, standalone). Use when adopting or evaluating Mover, creating a Mover-based pawn, authoring a custom movement mode or layered move, migrating from CMC, wiring Enhanced Input into ProduceInput, or debugging Mover prediction/rollback behavior.
- **In-Depth References**: `layered-moves-and-instant-effects.md`, `modes-transitions-and-modifiers.md`, `networking-and-backends.md`
- **Bakırköy BR Domain Adaptation**:
  - **3rd Person Restraint**: Mover trajectory generation and root motion must preserve over-the-shoulder 3rd person camera tracking.
  - **Network Resimulation**: Server-authoritative rollback and resimulation for the solo player and 10 bot pawns.

#### <a id="actors-and-components"></a>`actors-and-components`
- **Path**: `.agents/skills/actors-and-components/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/ Component Hierarchies`
- **Description**: Build and compose gameplay objects from Actors and Components in Unreal C++ — the AActor lifecycle (constructor, PostInitializeComponents, BeginPlay, Tick, EndPlay, Destroyed), the component types (UActorComponent, USceneComponent, UPrimitiveComponent), the root component and attachment, spawning actors and creating/registering components at construction or runtime, and ticking. Use when creating an actor or component, setting up a component hierarchy, attaching components, spawning actors, registering runtime components, or debugging lifecycle/ticking/ attachment/overlap issues.
- **In-Depth References**: `actor-lifecycle.md`, `attachment-and-transforms.md`, `components-and-registration.md`, `spawning-and-destroying.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="gameplay-ability-system"></a>`gameplay-ability-system`
- **Path**: `.agents/skills/gameplay-ability-system/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Abilities/ GAS Setup`
- **Description**: Build abilities, attributes, and effects with Unreal's Gameplay Ability System (GAS) — UAbilitySystemComponent (ASC), UGameplayAbility with ActivateAbility/CommitAbility/EndAbility, UAttributeSet with FGameplayAttributeData and ATTRIBUTE_ACCESSORS macro, UGameplayEffect with Instant/HasDuration/Infinite policies and GE Components, FGameplayAbilitySpec for granting, UAbilityTask for async steps (WaitDelay, PlayMontageAndWait, WaitGameplayEvent), GameplayCues for networked VFX/SFX, instancing policies (InstancedPerActor/InstancedPerExecution), net execution policies (LocalPredicted/ServerOnly), and replication modes (Full/Mixed/Minimal). Use when implementing abilities with cooldowns/costs/tags, health/stamina/mana attributes, buffs/debuffs/ damage via Gameplay Effects, ability tasks for async gameplay, Gameplay Cues for cosmetic feedback, or networked server-authoritative ability activation with client prediction. GAS requires the GameplayAbilities plugin and AbilitySystemGlobals initialization.
- **In-Depth References**: `ability-system-component.md`, `ability-tasks-and-cues.md`, `attributes-and-effects.md`, `gameplay-abilities.md`
- **Bakırköy BR Domain Adaptation**:
  - **Solo BR Rules**: No Down-But-Not-Out (DBNO) or team revive gameplay abilities. When health reaches 0, trigger immediate elimination gameplay effect.
  - **Server Authority**: Ability System Component (`UBRAbilitySystemComponent`) and Attribute Set (`UBRAttributeSet`) must be server-authoritative. Replicate attributes (HP 0-100, Shield 0-100) to owner client.
  - **Naming**: All GAS classes and tags must use the `BR.` namespace and `BR` prefix (`UBRGameplayAbility`, `BR.Status.Shield`).

#### <a id="gameplay-tags"></a>`gameplay-tags`
- **Path**: `.agents/skills/gameplay-tags/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Config/DefaultGameplayTags.ini & Native Tags`
- **Description**: Use Gameplay Tags in Unreal C++ — hierarchical FName-based labels (FGameplayTag, FGameplayTagContainer), native tag declaration and definition (UE_DECLARE_GAMEPLAY_TAG_EXTERN / UE_DEFINE_GAMEPLAY_TAG / UE_DEFINE_GAMEPLAY_TAG_COMMENT / UE_DEFINE_GAMEPLAY_TAG_STATIC), tag registration via UGameplayTagsManager, runtime lookup with RequestGameplayTag, container operations (AddTag, RemoveTag, HasTag, HasTagExact, HasAny, HasAll), single-tag matching (MatchesTag, MatchesTagExact, MatchesAny), data-driven conditions with FGameplayTagQuery, the IGameplayTagAssetInterface, and config via DefaultGameplayTags.ini / DataTable sources. Use when modeling states, categories, damage types, ability identifiers, or any open-ended hierarchical label that multiple systems share; when replacing brittle enums or string comparisons; or when working with GAS, AI behavior trees, animation, or UI systems that gate behavior on tags.
- **In-Depth References**: `containers-and-queries.md`, `native-tags.md`, `tag-driven-patterns.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="gameplay-architecture-planning"></a>`gameplay-architecture-planning`
- **Path**: `.agents/skills/gameplay-architecture-planning/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/ Separation of Concerns`
- **Description**: Design and plan Unreal Engine gameplay systems before implementation. Turns an ambiguous feature or game idea into an Unreal-native architecture with explicit ownership, lifetime, Actor/Component/UObject/Subsystem choices, Game Framework placement, C++ versus Blueprint boundaries, communication and replication flows, data and asset models, trade-off analysis, and an ordered implementation plan. Use when brainstorming a new mechanic or system, comparing architectural approaches, deciding where logic or state should live, mapping a feature across gameplay classes, or preparing a safe task list for an implementation agent.
- **In-Depth References**: `decision-matrices.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

### Input & Control Systems
*Total Skills in this Category: 1*

#### <a id="enhanced-input"></a>`enhanced-input`
- **Path**: `.agents/skills/enhanced-input/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Config/ & Content/Input/ IMC & Input Actions`
- **Description**: Implement player input with Unreal's Enhanced Input system — UInputAction (data asset, value types Boolean/Axis1D/Axis2D/Axis3D), UInputMappingContext (key-to-action mappings with per-key modifiers and triggers), UEnhancedInputComponent (BindAction with ETriggerEvent), UEnhancedInputLocalPlayerSubsystem (AddMappingContext/RemoveMappingContext), UInputModifier (Negate, SwizzleAxis, DeadZone, Scalar, Smooth), UInputTrigger (Pressed, Released, Hold, Tap, Pulse, ChordedAction), FInputActionValue (Get<bool>(), Get<float>(), Get<FVector2D>(), Get<FVector>()), and PlayerController/Pawn setup. Use when setting up player controls, binding movement/look/jump/interact actions in C++, adding or swapping mapping contexts at runtime (on-foot vs. in-vehicle vs. menu), reading analog values, or migrating from legacy BindAxis/BindAction input.
- **In-Depth References**: `actions-and-contexts.md`, `binding-and-setup.md`, `modifiers-and-triggers.md`
- **Bakırköy BR Domain Adaptation**:
  - **Camera Controls**: Input actions for aiming (ADS) must interpolate spring arm offset and camera FOV; never toggle first-person camera modes.
  - **Building Actions Paused**: Input mapping contexts for building pieces (Wall, Ramp, Floor) must be disabled or unmapped for Demo 1.
  - **Weapon Switching**: Bind weapon slot keys for the 2 prototype weapons (AR Hit-Scan on Slot 1, Rocket Launcher Projectile on Slot 2).

### Networking & Replication
*Total Skills in this Category: 1*

#### <a id="networking-and-replication"></a>`networking-and-replication`
- **Path**: `.agents/skills/networking-and-replication/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Network/ Replication Graph`
- **Description**: Implement server-authoritative multiplayer in Unreal C++ — network roles and authority (HasAuthority, GetLocalRole, GetRemoteRole, ROLE_Authority/AutonomousProxy/SimulatedProxy), actor replication setup (bReplicates, SetReplicates, bAlwaysRelevant, NetDormancy, NetUpdateFrequency), property replication (UPROPERTY Replicated/ReplicatedUsing, GetLifetimeReplicatedProps, DOREPLIFETIME/DOREPLIFETIME_CONDITION/DOREPLIFETIME_WITH_PARAMS), RepNotify callbacks (OnRep_), RPCs (UFUNCTION Server/Client/NetMulticast, Reliable/Unreliable, WithValidation, _Implementation/_Validate), replication conditions (COND_*), Push Model (MARK_PROPERTY_DIRTY_FROM_NAME, FDoRepLifetimeParams::bIsPushBased), FFastArraySerializer, and the Iris replication system. Use when replicating state across clients, adding RPCs, fixing multiplayer authority bugs, choosing replication conditions, or diagnosing "works in single player but not multiplayer" issues.
- **In-Depth References**: `fast-arrays.md`, `property-replication.md`, `replication-conditions-and-push-model.md`, `rpcs.md`
- **Bakırköy BR Domain Adaptation**:
  - **Server Authority**: Health, Shield, weapon fire validation, and storm circles must only be modified on the server. Clients send input RPCs (`ServerFireHitScan`, `ServerFireProjectile`).
  - **Solo State Only**: Do not replicate squad or team data. Replicate `AlivePlayerCount`, `Kills`, and storm parameters to all clients.
  - **10-Bot Optimization**: Bot AI runs exclusively on the server; replicate bot transform, animation state, and weapon firing to clients.

### World Partition & Open World Systems
*Total Skills in this Category: 3*

#### <a id="levels-and-world-partition"></a>`levels-and-world-partition`
- **Path**: `.agents/skills/levels-and-world-partition/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/Maps/ Bakırköy Open World (3.2km×2.1km)`
- **Description**: Structure and stream Unreal worlds in C++ — UWorld (persistent level + streaming levels), ULevel, ULevelStreaming; World Partition (UWorldPartition, runtime spatial-hash grid, UWorldPartitionRuntimeCell, streaming sources/UWorldPartitionStreamingSourceComponent); Data Layers (UDataLayerAsset, UDataLayerInstance, UDataLayerManager, EDataLayerRuntimeState); Level Instances (ALevelInstance, APackedLevelActor); One File Per Actor (OFPA); legacy sublevel streaming (UGameplayStatics::LoadStreamLevel / UnloadStreamLevel, Level Streaming Volumes). Use when organizing a level, building open-world or large-level streaming, toggling content sets (day/night, quest states) at runtime, creating reusable instanced level chunks, or choosing between World Partition and explicit sublevels.
- **In-Depth References**: `data-layers-and-hlod.md`, `level-instances.md`, `world-partition-streaming.md`
- **Bakırköy BR Domain Adaptation**:
  - **Bakırköy Urban Map**: Map dimensions ~3.2km × 2.1km covering Bakırköy district with narrow streets, alleys, and open plazas.
  - **Exterior Only**: All building actors are solid meshes. No interior rooms or corridors.
  - **Vertical Rooftop Access**: Place exterior fire escapes, steel stairs, and ramps linking street level to rooftops.
  - **Outdoor Loot Spawns**: All loot chests and weapon spawn locations must be situated in outdoor streets, courtyards, and rooftops.

#### <a id="landscape-and-foliage"></a>`landscape-and-foliage`
- **Path**: `.agents/skills/landscape-and-foliage/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/Maps/ Terrain & Coastal Foliage`
- **Description**: Terrain, instanced vegetation, and procedural environment generation in Unreal C++ — ALandscape / ALandscapeProxy / ULandscapeComponent (heightmap grid, material layers, edit layers, splines, Nanite landscape), UFoliageType / AInstancedFoliageActor / UHierarchicalInstancedStaticMeshComponent (HISM-backed instanced foliage, procedural foliage volumes), and the PCG framework (UPCGComponent / UPCGGraph, point data, landscape sampling, runtime generation). Use when creating or sculpting terrain, painting weight layers or foliage, adding landscape splines, batching vegetation with HISM, authoring PCG graphs, querying landscape data from C++, or debugging instancing and PCG generation issues.
- **In-Depth References**: `foliage-and-hism.md`, `landscape.md`, `pcg.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="asset-management"></a>`asset-management`
- **Path**: `.agents/skills/asset-management/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Data/ Asset Registry`
- **Description**: Reference and load Unreal assets correctly — hard vs soft references (TObjectPtr vs TSoftObjectPtr/TSoftClassPtr), virtual content paths, FSoftObjectPath, async loading with FStreamableManager and FStreamableHandle, the Asset Registry for querying without loading, ConstructorHelpers::FObjectFinder, UAssetManager/primary data assets, and asset bundles. Use when choosing a reference type, fixing load hitches or cook/memory bloat from hard references, loading assets on demand (level streaming, DLC, runtime content), enumerating or filtering assets without loading, or setting up a managed primary-asset pipeline with UPrimaryDataAsset.
- **In-Depth References**: `asset-manager-and-bundles.md`, `asset-registry.md`, `streamable-manager.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

### Physics & Collision (Chaos)
*Total Skills in this Category: 1*

#### <a id="physics-and-chaos"></a>`physics-and-chaos`
- **Path**: `.agents/skills/physics-and-chaos/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Physics/ Chaos & Traces`
- **Description**: Implement collision, physics simulation, and world queries using Unreal's Chaos physics engine in C++ — collision channels (ECollisionChannel), response types (ECollisionResponse / ECR_Block/Overlap/Ignore), collision presets and profiles, query vs physics collision (ECollisionEnabled), FBodyInstance damping/mass, SetSimulatePhysics, AddForce/AddImpulse, line traces and shape sweeps (LineTraceSingleByChannel, SweepSingleByChannel, OverlapMultiByChannel), FHitResult/FCollisionQueryParams, hit and overlap events (OnComponentHit, OnComponentBeginOverlap), physical materials (UPhysicalMaterial friction/restitution), ragdoll via UPhysicsAsset, and physics constraints (FConstraintInstance, UPhysicsConstraintComponent). Use when setting up what collides with what, creating trigger volumes, doing line/shape traces for aiming or interaction, simulating rigid-body objects, applying forces or impulses, building ragdolls, constraining bodies, or debugging missing hit/overlap events.
- **In-Depth References**: `collision-channels-and-profiles.md`, `physics-simulation-and-constraints.md`, `traces-and-queries.md`
- **Bakırköy BR Domain Adaptation**:
  - **Hybrid Hit Detection**:
    * AR Hit-Scan: Server line trace (`LineTraceSingleByChannel`) using `ECC_GameTraceChannel1` (Weapon).
    * Rocket Launcher: Spawns `ABRProjectile` actor with `UProjectileMovementComponent` (35 m/s) and radial damage sweep on impact.
  - **Natural Cover Physics**: Vehicle meshes, concrete barriers, and street props must have robust Chaos collision profiles (`BlockAll` or `BlockWeaponTrace`).
  - **Building Pieces Paused**: Structure destruction physics are paused for Demo 1.

### AI, Perception & Navigation
*Total Skills in this Category: 1*

#### <a id="ai-and-navigation"></a>`ai-and-navigation`
- **Path**: `.agents/skills/ai-and-navigation/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/AI/ NavMesh & 10 Bots`
- **Description**: Build AI in Unreal — AIController-driven pawns, Behavior Trees and Blackboards (tasks, decorators, services), the navigation system and NavMesh (MoveTo pathfinding, NavMeshBoundsVolume, NavAreas, avoidance), the Environment Query System (EQS generators, tests, C++ FEnvQueryRequest), AI Perception (sight/hearing/damage senses, ConfigureSense, OnTargetPerceptionUpdated), and StateTree (UStateTreeAIComponent). Use when creating enemy/NPC behavior, pathfinding/movement to targets, decision-making logic, environment queries for cover/flanking/positions, sensing the player, or replacing Behavior Trees with StateTree.
- **In-Depth References**: `behavior-tree-deep-dive.md`, `eqs-deep-dive.md`, `navigation-deep-dive.md`, `perception-and-statetree.md`
- **Bakırköy BR Domain Adaptation**:
  - **10 Bots Scenario**: Configure AIController and NavMesh querying for a 10-bot test scenario. Optimize patrol paths, perception update frequency, and combat engagement for 10 active bots.
  - **Exterior NavMesh**: Place `NavModifierVolume(NavArea_Null)` over all building footprints. NavMesh must generate exclusively on outdoor streets, alleys, plazas, and exterior fire escapes/stairs leading to rooftops.
  - **Combat Behavior**: Bots must navigate to loot spawns, pick up the 2 weapon prototypes (AR Hit-Scan and Rocket Launcher Projectile), and use natural environment cover (vehicles, corners, walls) rather than player builds.

### Rendering, Nanite & Materials
*Total Skills in this Category: 4*

#### <a id="nanite-and-rendering"></a>`nanite-and-rendering`
- **Path**: `.agents/skills/nanite-and-rendering/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/Meshes/ Nanite Geometry`
- **Description**: Configure Nanite virtualized geometry (FMeshNaniteSettings on static and skeletal meshes, fallback mesh, displacement/tessellation, WPO distance threshold) and reason about the broader UE rendering pipeline — deferred vs forward, GPU Scene instancing, Virtual Shadow Maps, Virtual Textures, TSR/temporal upscaling, post-process (FPostProcessSettings), scene capture to render targets, and key r.* cvars. Use when enabling Nanite on a mesh, diagnosing Nanite support failures, choosing anti-aliasing or upscaling method, configuring post-process in code or volumes, rendering to a texture (minimap, mirror, portal), tuning scalability cvars, or understanding the deferred/forward rendering split.
- **In-Depth References**: `nanite.md`, `rendering-pipeline.md`, `virtual-textures-and-shadows.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="materials-and-shaders"></a>`materials-and-shaders`
- **Path**: `.agents/skills/materials-and-shaders/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/Materials/ PBR Shaders`
- **Description**: Author and drive Unreal materials — UMaterial (the node graph asset), material instances (UMaterialInstanceConstant for editor-authored variants, UMaterialInstanceDynamic for runtime parameter changes), material domain (Surface/Deferred Decal/Light Function/Post Process/UI/Volume), shading models (Default Lit/Unlit/Subsurface/Clear Coat/Hair/Cloth/Eye), blend modes (Opaque/Masked/Translucent/Additive), scalar/vector/texture parameters, material functions, material parameter collections (global scene-wide values), and the material C++ API (CreateDynamicMaterialInstance, SetScalarParameterValue, SetVectorParameterValue, SetTextureParameterValue, UKismetMaterialLibrary). Use when creating materials, making parameterized variants, changing material parameters at runtime, setting global weather or world-state parameters, fixing material shader permutation count or translucency overdraw, or cross-referencing the material class hierarchy.
- **In-Depth References**: `material-cpp-and-collections.md`, `material-graph-and-domains.md`, `material-instances-and-parameters.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="lighting-and-lumen"></a>`lighting-and-lumen`
- **Path**: `.agents/skills/lighting-and-lumen/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Config/ & Maps/ Lumen Dynamic GI`
- **Description**: Light Unreal scenes in C++ and configure them correctly — light component types (UDirectionalLightComponent, UPointLightComponent, USpotLightComponent, URectLightComponent, USkyLightComponent), mobility (Static/Stationary/Movable) and its impact on GI, baking, and runtime cost, Lumen global illumination and reflections (enabling, quality settings, hardware vs software ray tracing), Virtual Shadow Maps, sky and atmosphere (USkyAtmosphereComponent, UExponentialHeightFogComponent), post process volumes for exposure/auto-exposure and Lumen overrides, and reflection captures. Use when creating or configuring light components in C++, choosing light mobility, enabling or troubleshooting Lumen GI/reflections, setting up sky/fog/atmosphere, tuning exposure or color grading, placing reflection captures, or deciding between baked and dynamic lighting.
- **In-Depth References**: `light-components-and-mobility.md`, `lumen-gi-and-reflections.md`, `shadows-and-postprocess.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="meshes-static-and-skeletal"></a>`meshes-static-and-skeletal`
- **Path**: `.agents/skills/meshes-static-and-skeletal/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/Meshes/ Static & Skeletal Hulls`
- **Description**: Work with static and skeletal meshes in Unreal C++ — UStaticMesh + UStaticMeshComponent, USkeletalMesh + USkeletalMeshComponent + USkinnedMeshComponent, instanced meshes (ISM/HISM), material slots (SetMaterial/GetMaterial), sockets (static and skeletal), collision setup (UBodySetup, ECollisionTraceFlag, simple vs complex), the Skeleton/PhysicsAsset relationship, Nanite enable flag on static and skeletal meshes, LODs, and mesh sections. Use when assigning or swapping meshes in C++, configuring collision, enabling Nanite, choosing ISM vs HISM vs individual components, attaching to mesh sockets, overriding material slots, querying LOD data, or debugging missing materials, wrong skeleton, or silent socket attachment failures.
- **In-Depth References**: `instanced-meshes.md`, `materials-lods-collision.md`, `skeletal-meshes.md`, `static-meshes.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

### Animation, Control Rig & Cinematics
*Total Skills in this Category: 3*

#### <a id="animation-system"></a>`animation-system`
- **Path**: `.agents/skills/animation-system/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/Characters/ Animations & State Machines`
- **Description**: Animate skeletal meshes in Unreal using the AnimInstance / Animation Blueprint model — C++ UAnimInstance base class (NativeInitializeAnimation, NativeUpdateAnimation, NativeThreadSafeUpdateAnimation), AnimGraph with state machines and blend spaces, animation assets (UAnimSequence, UBlendSpace, UAnimMontage, UAnimComposite, UPoseAsset), anim notifies and notify states, montage playback and delegates, linked anim layers, Motion Matching (Pose Search plugin), and Motion Warping. Use when setting up character animation, driving locomotion blends from C++, playing montages for actions, firing gameplay events at precise animation frames (notifies), switching animation sets at runtime, or integrating the Pose Search / Motion Warping plugins.
- **In-Depth References**: `anim-instance-and-update.md`, `montages-and-slots.md`, `motion-matching-and-warping.md`, `state-machines-and-blending.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="control-rig-and-ik"></a>`control-rig-and-ik`
- **Path**: `.agents/skills/control-rig-and-ik/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/Characters/ IK & Weapon Aim Offsets`
- **Description**: Procedural animation and inverse kinematics in Unreal Engine — Control Rig (RigVM-based graph that manipulates a bone/control hierarchy), IK Rig (solver definitions with Full-Body IK, Limb IK, Set Transform), the IK Retargeter (transfers animation between skeletons of different proportions), and lightweight AnimGraph IK nodes (Two Bone IK, FABRIK, CCDIK). Use when implementing foot placement on terrain, hand/weapon IK, look-at, procedural pose fixups, runtime retargeting, or sharing an animation library across characters with different skeletons. Covers UControlRig, URigHierarchy, FRigUnit, UIKRigDefinition, UIKRetargeter, FAnimNode_ControlRig, FAnimNode_IKRig, FAnimNode_RetargetPoseFromMesh, FIKRigGoal, UControlRigComponent, UIKRigComponent.
- **In-Depth References**: `animgraph-ik-nodes.md`, `control-rig-graph.md`, `ik-retargeter.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="sequencer-and-cinematics"></a>`sequencer-and-cinematics`
- **Path**: `.agents/skills/sequencer-and-cinematics/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/Cinematics/ Match Start & Winner Sequence`
- **Description**: Create and drive Unreal Engine cinematics from C++ — ULevelSequence (the cinematic asset), ALevelSequenceActor (the level-placed container), ULevelSequencePlayer (CreateLevelSequencePlayer, Play, Stop, PlayLooping, SetPlaybackPosition, OnFinished), possessables vs spawnables, runtime binding overrides (SetBinding/SetBindingByTag), track and MovieScene concepts, Cine Camera (UCineCameraComponent, ACineCameraActor — filmback, focal length, aperture, focus), Camera Cuts track, and Movie Render Queue for high-quality offline output. Use when triggering or controlling a cutscene at runtime, overriding sequence bindings for dynamic actors, reacting to sequence-end events, animating a film-style camera, firing gameplay callbacks from an event track, or rendering frames with the Movie Render Pipeline.
- **In-Depth References**: `cameras-and-cuts.md`, `level-sequence-and-player.md`, `movie-render-queue.md`, `tracks-and-bindings.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

### VFX (Niagara) & Audio (MetaSounds)
*Total Skills in this Category: 2*

#### <a id="niagara-vfx"></a>`niagara-vfx`
- **Path**: `.agents/skills/niagara-vfx/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/VFX/ Weapon Tracers & Storm Boundary`
- **Description**: Create and control visual effects using Unreal's Niagara system — UNiagaraSystem, UNiagaraComponent, UNiagaraFunctionLibrary; the system/emitter/module/parameter hierarchy; spawning effects at a world location or attached to an actor/socket (SpawnSystemAtLocation, SpawnSystemAttached); setting User Parameters from C++ (SetVariableFloat, SetVariableVec3, SetVariableActor, SetFloatParameter, SetColorParameter); CPU vs GPU simulation trade-offs; Data Interfaces (skeletal mesh, static mesh, collision); component lifetime management (bAutoDestroy, Activate/Deactivate, OnSystemFinished); and Niagara Data Channels. Use when spawning particle or VFX (fire, smoke, impacts, trails, magic), attaching effects to actors or sockets, driving an effect from gameplay parameters, choosing CPU vs GPU emitters, or migrating from Cascade (deprecated).
- **In-Depth References**: `data-interfaces-and-performance.md`, `spawning-and-parameters.md`, `system-and-emitter-model.md`
- **Bakırköy BR Domain Adaptation**:
  - **Combat VFX**: Niagara systems for AR hit-scan tracer lines, muzzle flashes, surface impact sparks, and Rocket Launcher projectile trail / radial explosion blast.
  - **Storm Barrier VFX**: Cylindrical energy wall effect representing the shrinking storm circle.
  - **Outdoor Environment**: Ambient dust and leaves on streets; no interior atmospheric lighting effects.

#### <a id="audio-and-metasounds"></a>`audio-and-metasounds`
- **Path**: `.agents/skills/audio-and-metasounds/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/Audio/ MetaSounds Outdoor Acoustics`
- **Description**: Play and control audio in Unreal — the sound asset types (SoundWave, SoundCue, MetaSound Source), playing 2D/3D sounds from C++ (UGameplayStatics, UAudioComponent), spatial attenuation, sound classes/submixes/concurrency for mixing, runtime MetaSound parameters, Quartz beat-quantized playback, and the MetaSound Builder API. Use when playing SFX/music, attaching looping sounds to actors, setting up 3D spatialization, mixing/ducking audio, driving procedural audio with MetaSounds, or debugging silent sounds, voice spam, or parameter mismatches.
- **In-Depth References**: `attenuation-and-spatialization.md`, `audiocomponent-and-playback.md`, `metasound-parameters-and-builder.md`, `mixing-classes-submixes-concurrency.md`
- **Bakırköy BR Domain Adaptation**:
  - **Exterior Acoustic Model**: MetaSounds patches should simulate outdoor urban acoustics (narrow street reverb, alley reflections, open rooftop spatialization).
  - **Prototype Weapon Audio**: Audio synthesis for AR firing/reloading and Rocket Launcher launch/explosion.
  - **Storm Warning**: Audio siren and atmospheric bass hum for the shrinking storm boundary.

### UI Systems (UMG & Slate)
*Total Skills in this Category: 1*

#### <a id="umg-and-slate"></a>`umg-and-slate`
- **Path**: `.agents/skills/umg-and-slate/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/UI/ Solo BR & FFA HUDs`
- **Description**: Build game UI in Unreal — UMG user widgets (UUserWidget) with the C++ lifecycle (NativeOnInitialized, NativeConstruct, NativeDestruct, NativeTick), the widget tree and common leaf/panel widgets (UButton/UTextBlock/UImage/UProgressBar/UCanvasPanel/UHorizontalBox/ UVerticalBox/UOverlay), the meta=(BindWidget/BindWidgetOptional) pattern to wire C++ to Blueprint-designed widgets, CreateWidget + AddToViewport / RemoveFromParent, UWidgetComponent for 3D in-world UI, event binding (OnClicked AddDynamic), the Slate layer (SWidget, SCompoundWidget, declarative syntax), and CommonUI for input-routed multiplatform menus — plus UI best practices and performance optimization: invalidation boxes/retainer boxes/ volatility, widget pooling (FUserWidgetPool, ListView), event-driven updates instead of property bindings or Tick, Canvas Panel nesting rules, animation cost tiers, MVVM viewmodels (FieldNotify), CommonUI layer stacks (the Lyra pattern), DPI scaling, and safe zones. Use when creating HUDs/menus/inventory/widgets, wiring UI to gameplay in C++, handling button/input events, choosing UMG vs Slate vs CommonUI, debugging BindWidget name mismatches, optimizing slow UI, or architecting screen flow for a production game.
- **In-Depth References**: `architecture-and-authoring.md`, `common-widgets-and-layout.md`, `performance-and-best-practices.md`, `slate-layer.md`, `userwidget-and-binding.md`, `widget-component-and-input.md`
- **Bakırköy BR Domain Adaptation**:
  - **Solo BR & FFA HUD**: HUD displays player Health, Shield, weapon ammo, alive player count (out of 11: 1 player + 10 bots), and storm timer / score tracker.
  - **No Squad UI**: Do not create teammate status panels, squad markers, or revive indicators.
  - **3rd Person Crosshair**: Reticle centered on 3rd person aim point with hit markers and damage numbers.

### Blueprint & C++ Interop
*Total Skills in this Category: 2*

#### <a id="blueprint-fundamentals"></a>`blueprint-fundamentals`
- **Path**: `.agents/skills/blueprint-fundamentals/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/Blueprints/ Logic Graphs`
- **Description**: Understand Blueprints as Unreal's visual scripting and asset-class system — what a Blueprint class is, the UBlueprint editor asset vs. UBlueprintGeneratedClass runtime class, how it relates to its C++ parent, the graph types (Event Graph, Functions, Construction Script, Macros, Interfaces), variables and categories, components in Blueprint, and the C++-base + Blueprint-subclass workflow. Use when reasoning about Blueprint vs C++ responsibilities, designing a class hierarchy that spans both, explaining how Blueprint logic maps onto the underlying C++/UObject model, or debugging Blueprint compilation and class-relationship issues.
- **In-Depth References**: `blueprint-class-and-generated-class.md`, `cpp-blueprint-boundary.md`, `graphs-variables-and-components.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="blueprint-cpp-integration"></a>`blueprint-cpp-integration`
- **Path**: `.agents/skills/blueprint-cpp-integration/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/ BP Exposing Macros`
- **Description**: Expose C++ classes, functions, and properties to Blueprint in Unreal Engine — UFUNCTION specifiers (BlueprintCallable, BlueprintPure, BlueprintImplementableEvent, BlueprintNativeEvent), UPROPERTY exposure (BlueprintReadWrite/ReadOnly, EditAnywhere/DefaultsOnly, ExposeOnSpawn), UCLASS specifiers (Blueprintable, BlueprintType), meta=(...) tags, Blueprint function libraries, TSubclassOf/soft references, and Blueprint-implementable interfaces. Use when deciding which specifiers to put on C++ members or functions, designing a designer-facing API, calling between C++ and Blueprint, or debugging missing nodes/properties/events in the Blueprint graph.
- **In-Depth References**: `blueprint-interfaces.md`, `ufunction-specifiers.md`, `uproperty-specifiers.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

### Profiling, Debugging & Test Automation
*Total Skills in this Category: 4*

#### <a id="debugging-techniques"></a>`debugging-techniques`
- **Path**: `.agents/skills/debugging-techniques/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Diagnostics & Gameplay Debugger Overlay`
- **Description**: Debug Unreal C++ and gameplay code — native debugger usage (VS/Rider, natvis, Live Coding caveats), DrawDebug* world-space helpers (DrawDebugLine, DrawDebugSphere, DrawDebugString, etc.), on-screen messages (GEngine->AddOnScreenDebugMessage), the Visual Logger (UE_VLOG*, timestamped replay of spatial/temporal events), the Gameplay Debugger (FGameplayDebuggerCategory, custom categories), ensure/check as debugging aids, and stat/console commands for runtime interrogation. Use when diagnosing wrong behavior, visualizing traces/ranges/AI state in the world, reproducing intermittent or AI bugs with timeline replay, stepping through a crash, or adding in-game debug overlays to a custom system.
- **In-Depth References**: `draw-debug-and-console.md`, `gameplay-debugger.md`, `visual-logger.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="profiling-and-optimization"></a>`profiling-and-optimization`
- **Path**: `.agents/skills/profiling-and-optimization/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Unreal Insights & Frame Profiling`
- **Description**: Profile and optimize Unreal Engine performance — Unreal Insights (trace-based CPU/GPU/memory profiling, .utrace sessions, Timing Insights, Memory Insights), stat commands (stat unit/fps/game/gpu/scenerendering/memory and the full stat command table), stat groups, C++ instrumentation (DECLARE_STATS_GROUP, DECLARE_CYCLE_STAT, SCOPE_CYCLE_COUNTER, QUICK_SCOPE_CYCLE_COUNTER, TRACE_CPUPROFILER_EVENT_SCOPE, CSV_SCOPED_TIMING_STAT), memory profiling (LLM, MemReport, memreport -full), and the measurement-first optimization workflow. Use when diagnosing frame-rate drops, hitches, CPU/GPU bottlenecks, or memory growth, when adding timing instrumentation to find a hotspot, or when deciding on CPU vs GPU vs memory optimization levers.
- **In-Depth References**: `instrumenting-cpp.md`, `memory-profiling.md`, `stat-commands.md`, `unreal-insights-and-trace.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="game-thread-performance"></a>`game-thread-performance`
- **Path**: `.agents/skills/game-thread-performance/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Tick Optimization & Game Thread Budget`
- **Description**: Explain how game-thread time drives frame rate and how to optimize it. Use when profiling CPU-bound frame-time spikes, tick-heavy actors, hitches, or when deciding whether to move work off the game thread.
- **In-Depth References**: Self-contained in `SKILL.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="automation-and-testing"></a>`automation-and-testing`
- **Path**: `.agents/skills/automation-and-testing/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Tests/ Automation Specs`
- **Description**: Write and run automated tests for Unreal Engine projects — simple/complex automation tests (IMPLEMENT_SIMPLE_AUTOMATION_TEST, IMPLEMENT_COMPLEX_AUTOMATION_TEST), BDD-style Spec tests (DEFINE_SPEC, BEGIN_DEFINE_SPEC, Describe/It/BeforeEach/AfterEach), functional in-level tests (AFunctionalTest), low-level tests (Catch2-based LLTs), latent/async commands, EAutomationTestFlags, FAutomationTestBase assertion API (TestTrue/TestEqual/TestNotNull/AddError), and running tests from the editor, CLI, or CI. Use when writing unit or integration tests for gameplay logic or systems, setting up headless CI test runs, verifying data/content, or catching regressions.
- **In-Depth References**: `flags-and-ci.md`, `functional-tests.md`, `low-level-tests.md`, `spec-and-latent-commands.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

### Editor Scripting & Packaging
*Total Skills in this Category: 3*

#### <a id="editor-scripting-and-python"></a>`editor-scripting-and-python`
- **Path**: `.agents/skills/editor-scripting-and-python/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Scripts/ & Editor Automation (port 6776)`
- **Description**: Automate and extend the Unreal Editor using Python (the `unreal` module, startup scripts, commandlets), Editor Utility Widgets/Blueprints (Blutility — UEditorUtilityWidget, UEditorUtilityObject, UEditorUtilityWidgetBlueprint, UAssetActionUtility), the editor scripting subsystems (UEditorActorSubsystem, UEditorAssetSubsystem, ULevelEditorSubsystem, UAssetEditorSubsystem, UEditorUtilitySubsystem), and how C++ UFUNCTION specifiers (BlueprintCallable, CallInEditor, ScriptMethod, ScriptName) control which APIs surface in Python and Blueprints. Use when batch-processing assets, building in-editor tools or dockable UMG panels, running headless Python commandlets in CI, scripting repetitive editor tasks, or exposing custom C++ editor APIs to Python/Blueprints. Editor-only — never used in packaged games.
- **In-Depth References**: `editor-subsystems.md`, `editor-utility-widgets.md`, `python-api.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="packaging-and-deployment"></a>`packaging-and-deployment`
- **Path**: `.agents/skills/packaging-and-deployment/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Binaries/ & Packaged Game Builds`
- **Description**: Cook, package, and ship an Unreal project — the cook process (by-the-book vs on-the-fly, cook rules, always/never cook directories, shader sharing), build configurations (Debug/DebugGame/Development/Test/Shipping) and build targets (Game/Client/Server/Editor) declared in *.Target.cs files, UAT BuildCookRun command-line pipeline, pak files and the modern IoStore (.utoc/.ucas) container format, asset chunking and Primary Asset Rules for DLC/patching, ProjectPackagingSettings (bUseIoStore, bGenerateChunks, bCompressed, DirectoriesToAlwaysCook/NeverCook), platform targets, content-on-demand / IoStore On-Demand, and shipping-vs-development behavioral differences (WITH_EDITOR, stripped checks/logs). Use when producing a runnable build, automating cook/package in CI, diagnosing packaging failures, configuring what ships, or setting up chunked DLC delivery.
- **In-Depth References**: `buildcookrun-and-uat.md`, `cook-and-build-configs.md`, `pak-iostore-and-chunking.md`, `platform-and-dlc.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="importing-content"></a>`importing-content`
- **Path**: `.agents/skills/importing-content/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Content/ Pipeline for Meshes & Textures`
- **Description**: Import external assets into Unreal using the Interchange framework (UInterchangeManager, UInterchangePipelineBase, UInterchangeFactoryBase, UInterchangeTranslatorBase, UInterchangeSourceData) and the legacy FBX pipeline (UFbxFactory / UnFbx::FFbxImporter). Covers the three-stage Interchange pipeline (translate → pipeline → factory), pipeline stacks, format support (FBX, glTF/GLB, OBJ, USD, images, audio), mesh and texture import settings (units/axes, normals, lightmap UVs, Nanite, sRGB/compression), skeletal mesh skeleton assignment, import asset data (UInterchangeAssetImportData / UAssetImportData), and programmatic runtime import via C++, Blueprint, and Python. Use when importing DCC content, troubleshooting wrong scale/rotation/shading after import, scripting automated batch import, customising an import pipeline, or setting up a repeatable reimport workflow.
- **In-Depth References**: `interchange-framework.md`, `mesh-and-texture-import.md`, `reimport-and-import-data.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

### Data Systems & Subsystems
*Total Skills in this Category: 3*

#### <a id="save-and-load"></a>`save-and-load`
- **Path**: `.agents/skills/save-and-load/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Data/ SaveGame State`
- **Description**: Persist and restore game data in Unreal C++ using the SaveGame system — define a USaveGame subclass with UPROPERTY members, create/save/load/delete named slots via UGameplayStatics (SaveGameToSlot, LoadGameFromSlot, AsyncSaveGameToSlot, AsyncLoadGameFromSlot, DoesSaveGameExist, DeleteGameInSlot), and serialize actor state into a byte buffer with FMemoryWriter/FMemoryReader and FObjectAndNameAsStringProxyArchive. Covers the SaveGame UPROPERTY specifier and ArIsSaveGame archive flag for selective actor serialization, the ULocalPlayerSaveGame subclass for per-user saves, save versioning and migration, ISaveGameSystem platform abstraction, and design rules for what belongs in a save. Use when implementing save/load, persisting progress, inventory, or settings, handling multiple save slots or user profiles, serializing dynamic actor state, migrating old saves, or troubleshooting missing fields and null returns on load.
- **In-Depth References**: `savegame-objects-and-slots.md`, `serializing-actor-state.md`, `versioning-and-migration.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="data-driven-design"></a>`data-driven-design`
- **Path**: `.agents/skills/data-driven-design/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Data/ DataTables & DataAssets`
- **Description**: Drive Unreal gameplay from externally-editable data instead of hardcoded values — DataTables (UDataTable, FTableRowBase, CSV/JSON import, UCompositeDataTable), DataAssets (UDataAsset, UPrimaryDataAsset with AssetManager), Curves (UCurveFloat, UCurveTable, FRuntimeFloatCurve), config-driven UPROPERTY(config) in .ini files, and DeveloperSettings (UDeveloperSettings) for project-wide tuning. Use when defining item/enemy/level/balance schemas, choosing the right data container, exposing designer-tunable values, replacing magic numbers with editable assets, or layering data across DLC/platforms with composite tables.
- **In-Depth References**: `config-and-developer-settings.md`, `curves-and-runtime-data.md`, `data-assets-and-validation.md`, `datatables-and-composite.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

#### <a id="subsystems"></a>`subsystems`
- **Path**: `.agents/skills/subsystems/SKILL.md`
- **Origin**: kevinpbuckley/unreal-engine-skills
- **Target Module**: `Source/BakirkoyBR/Subsystems/ Persistent Singletons`
- **Description**: Implement engine-managed singletons scoped to a defined lifetime using Unreal's Subsystem framework — UEngineSubsystem, UGameInstanceSubsystem, UWorldSubsystem, UTickableWorldSubsystem, and ULocalPlayerSubsystem. Covers Initialize/Deinitialize lifecycle, ShouldCreateSubsystem for conditional creation, InitializeDependency for ordered init, and Blueprint/Python exposure. Use when building a service or manager (save system, ability registry, match service, analytics) and deciding whether to scope it to the process, game session, world, or local player — and when choosing between a subsystem, a manager actor, or a GameInstance override.
- **In-Depth References**: `choosing-a-subsystem.md`, `lifecycle-and-access.md`, `subsystem-types.md`
- **Bakırköy BR Domain Adaptation**: Standard compliance block applied (Enforces 7 Core Constraints + 4 MVP Directives, `BR` prefix, and server authority).

---

## Automated Validation & Quality Gates

The integrity of the skills catalog is enforced by automated test scripts in `.agents/skills/scripts/`:

1. **`validate_all_skills.py`**: Comprehensive validator checking:
   - YAML frontmatter completeness (`name`, `description`).
   - Name matches folder name exactly.
   - No UTF-8 BOM encoding.
   - Non-empty descriptions (>= 20 characters).
   - Presence of all 7 Bakırköy BR Core Constraints.
   - Presence of all 4 Demo 1 MVP Directives.
   - Run command: `python .agents/skills/scripts/validate_all_skills.py`

2. **`validate_skills.py`**: Upstream UnrealXu syntax and legacy token validator.
   - Run command: `python .agents/skills/scripts/validate_skills.py`

3. **`validate_engine_anchors.py`**: AST and header verification against UE5.6–5.8 engine installs.
   - Run command: `python .agents/skills/scripts/validate_engine_anchors.py --engine-root <PathToEngine>`

---
*Generated automatically by Worker M3 (Skills Adaptation & Catalog Worker) for the Bakırköy BR Project.*
