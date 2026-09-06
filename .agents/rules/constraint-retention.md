# Bakırköy BR — Constraint Retention & Project Invariants

> **Bakırköy BR Project Rule**  
> **Status**: MANDATORY & HARD-LOCKED  
> **Applicable To**: All Agents, Orchestrator, Workers, QA Reviewer, and Integrator  
> **Reference**: Requirement R1 & User Directives (2026-09-06T01:25 - 01:29Z)

---

## 1. Executive Summary & Retention Mandate

The Bakırköy BR project is governed by strict architectural, gameplay, and scope invariants. Under no circumstances may any agent alter, relax, or violate these constraints due to context drift, LLM generalization, or standard Battle Royale conventions found in other games (e.g., Fortnite, PUBG, Apex Legends).

Any pull request, code modification, design document, or plan violating any constraint defined below will be **INSTANTLY REJECTED** at the QA Reviewer and Integrator verification gates.

---

## 2. The 7 Core Architectural Constraints (Hard-Locked)

### Constraint 1 (C1): No Interior Spaces (Exterior-Only Gameplay)
- **Specification**:
  - Buildings throughout the Bakırköy urban environment are **exterior-only solid collision volumes** (convex hulls or bounding boxes).
  - There is zero interior geometry, zero interior rooms, zero interior furniture, and zero interior loot spawns.
  - No openable doors, smashable windows, or traversable indoor spaces may be implemented.
  - **Rooftops and Terraces ARE PLAYABLE**: Players and AI bots access rooftops, balconies, and elevated terraces strictly through **external staircases, metal fire escapes, ramps, or exterior vertical structures**.
  - **NavMesh**: NavMesh is generated exclusively on ground streets, sidewalks, plazas, external stairs, and rooftops. Building interiors must have NavMesh generation completely cut out / carved.
- **Forbidden Hallucinations**:
  - Writing code or placing assets for indoor rooms, apartment corridors, indoor chests, interior lighting, or indoor pathfinding.

---

### Constraint 2 (C2): Solo Battle Royale Only
- **Specification**:
  - The initial game architecture and networking loop supports **Solo play only** (Free-For-All survival, every participant for themselves).
  - Elimination is immediate upon reaching 0 HP (and depleted shields).
- **Forbidden Hallucinations**:
  - Implementing Squads, Duos, Trios, team voice chat, friendly fire flags, Down-But-Not-Out (DBNO) states, crawling states, revive interactions, reboot vans, or downed-teammate ping systems.

---

### Constraint 3 (C3): Server-Authoritative Architecture
- **Specification**:
  - The dedicated Unreal server is the single source of truth for all critical gameplay state:
    1. Player Health (`CurrentHealth`) and Shield (`CurrentShield`).
    2. Ammo counts, reload states, and weapon inventories.
    3. Storm circle position, phase transitions, and zone damage ticks.
    4. Hit validation, damage infliction, and player eliminations.
  - Clients run client-side prediction for local character movement and immediate weapon firing visuals/sounds, but all damage and state mutations are validated on the server via Server RPCs (`UFUNCTION(Server, Reliable, WithValidation)`).
  - Server rewinds player positions based on network timestamp to validate hit-scan line traces fairly against latency.
- **Forbidden Hallucinations**:
  - Allowing the client to send "I dealt 45 damage to Player X", decrementing health locally on client, or running storm circle logic locally without server replication.

---

### Constraint 4 (C4): 3rd Person Camera Perspective Only
- **Specification**:
  - The game is exclusively played from an over-the-shoulder 3rd person perspective using a spring arm (`USpringArmComponent`) and camera (`UCameraComponent`).
  - Aiming Down Sights (ADS) tightens weapon crosshair spread and interpolates the camera closer (FOV zoom / over-the-shoulder offset), but **NEVER switches to a 1st person mesh or 1st person camera view**.
- **Forbidden Hallucinations**:
  - Adding a first-person toggle, true 1st person weapon models, or camera attachments to gun iron sights.

---

### Constraint 5 (C5): Exactly 3 Building Materials
- **Specification**:
  - The resource and building system operates strictly with **three (3)** distinct materials:
    1. **Moloz** (Debris / Rubble): Quick to collect, lowest durability, fastest build time.
    2. **Tuğla** (Brick): Medium durability, medium harvesting rate.
    3. **Çelik** (Steel): Highest durability, slowest harvesting rate.
  - Defined authoritatively in `Source/BakirkoyBR/Data/BRTypes.h`:
    ```cpp
    UENUM(BlueprintType)
    enum class EBRMaterialType : uint8
    {
        Moloz UMETA(DisplayName = "Moloz (Debris)"),
        Tugla UMETA(DisplayName = "Tuğla (Brick)"),
        Celik UMETA(DisplayName = "Çelik (Steel)")
    };
    ```
- **Forbidden Hallucinations**:
  - Adding a 4th or 5th material (such as Wood, Stone, Metal, Glass, Gold, or Energy).

---

### Constraint 6 (C6): Hybrid Hit Detection System
- **Specification**:
  - Combat hit registration uses a dual hybrid model determined strictly by weapon archetype:
    - **Hit-Scan (LineTrace)**: High-velocity firearms including Assault Rifles (AR), Submachine Guns (SMG), Pistols, Shotguns, and Sniper Rifles use instant raycasts (`LineTraceSingleByChannel`) with server-side lag compensation and rewind.
    - **Projectile Physics**: Heavy explosive weaponry including Rocket Launchers and Grenade Launchers spawn simulated physical actors (`ABRProjectile`) with velocity, gravity drop, collision detection, and radial splash damage (`UGameplayStatics::ApplyRadialDamageWithFalloff`).
- **Forbidden Hallucinations**:
  - Using simulated bullet drop physics for basic assault rifles or instant hit-scan raycasts for rocket launchers.

---

### Constraint 7 (C7): Strict `BR` Naming Prefix
- **Specification**:
  - All C++ classes, structs, enums, delegates, and core assets belonging to the project must follow Unreal Engine naming conventions with the mandatory `BR` project prefix:
    - Actor Classes: `ABR...` (e.g., `ABRCharacter`, `ABRGameMode`, `ABRWeaponBase`, `ABRProjectile`)
    - UObject Classes: `UBR...` (e.g., `UBRHealthComponent`, `UBRWeaponDataAsset`)
    - Interfaces: `IBR...` (e.g., `IBRDamageable`, `IBRInteractable`)
    - Structs: `FBR...` (e.g., `FBRWeaponStats`, `FBRLootTableEntry`)
    - Enums: `EBR...` (e.g., `EBRMaterialType`, `EBRWeaponState`, `EBRGamePhase`)
    - Delegates: `FOnBR...` (e.g., `FOnBRHealthChanged`, `FOnBRPlayerEliminated`)
    - Blueprints: `BP_BR...`
    - Data Tables: `DT_BR...`
- **Forbidden Hallucinations**:
  - Omitting the prefix (e.g., `ACharacterBase`, `UHealthComponent`, `FWeaponStats`).

---

## 3. Playable Demo MVP Directives (Current Milestone Focus)

Following explicit user updates for the fast playable MVP slice, all agents must adhere to the following 5 MVP directives:

### MVP Directive 1 (M1): Exactly 10-Bot Scenario
- **Directive**: For the playable demo MVP, the AI population is capped at **exactly 10 bots** (plus 1 human player).
- **Engine Optimization**:
  - GameMode (`ABRGameMode`), Spawner (`UBRSpawnManager`), and AI Controller (`ABRAIController`) logic must be optimized and tuned specifically for 10 bots.
  - Spawns must be clustered within the active playable slice of the map to ensure immediate, high-tempo combat engagements.
- **Forbidden Action**: Spawning 50 or 100 bots during this demo phase.

---

### MVP Directive 2 (M2): Dual-Weapon Prototypes (AR Hit-Scan + Rocket Launcher Projectile)
- **Directive**: The initial loot pool and combat system must implement and expose **exactly two (2) weapon prototypes** to test and prove the hybrid hit detection architecture:
  1. **Assault Rifle (AR)**:
     - Archetype: Hit-Scan (LineTrace).
     - Damage: ~30 damage per bullet.
     - Fire Rate: 600 RPM (automatic).
     - Behavior: Instant trace, server rewind validation, tracer line visual.
  2. **Rocket Launcher (RPG)**:
     - Archetype: Physical simulated projectile (`ABRRocketProjectile`).
     - Initial Speed: ~3500 cm/s, slight ballistic arc.
     - Impact: Explodes on collision, deals 110 direct damage and up to 85 radial splash damage within a 400 cm radius with falloff.
- **Forbidden Action**: Spending time implementing a dozen weapon types before these two core prototypes are 100% verified.

---

### MVP Directive 3 (M3): Two Distinct Playable GameModes
- **Directive**: The project must provide **two (2) distinct, playable GameModes** selectable in the demo:
  1. **GameMode 1 — Free-For-All (FFA / Deathmatch)**:
     - Win Condition: First to reach the score limit (e.g., 15 eliminations) or highest score when the 10-minute match timer expires.
     - Respawn: Instant or short-delay respawn at safe exterior spawn points.
  2. **GameMode 2 — Classic Battle Royale (BR)**:
     - Win Condition: Last Man Standing (survival).
     - Elimination: Permadeath (spectator mode on elimination).
     - Circle Mechanic: Shrinking storm / gas circle forcing surviving bots and players into narrow urban choke points.
- **Forbidden Action**: Hardcoding a single game mode or mixing deathmatch respawns into the Battle Royale rule loop.

---

### MVP Directive 4 (M4): Building System Paused for Demo 1
- **Directive**: Development of the player grid-building system (walls, ramps, floors) is **temporarily paused** for Demo 1.
- **Gameplay Focus**:
  - Players and bots rely entirely on **natural urban cover**: abandoned vehicles, concrete barricades, narrow alleyways, exterior walls, and street furniture.
  - Building Worker agents should freeze active build-placement code generation and instead support cover-point generation and exterior level layout.
- **Forbidden Action**: Demanding active grid building mechanics to approve combat or AI movement.

---

### MVP Directive 5 (M5): Exterior Vertical Navigation & Rooftop NavMesh
- **Directive**: The level design for the demo focuses strictly on **tight urban streets, narrow alleys, and rooftops (vertical gameplay)**.
- **Navigation Rules**:
  - Exterior stairs, scaffolding, and metal fire escapes must link street level to building rooftops.
  - The Unreal Navigation Mesh (RecastNavMesh) must generate traversable polygons continuously from street level, up the external stairs, and across accessible rooftops.
  - NavMesh must never generate inside building hulls.
- **Forbidden Action**: Creating flat single-plane maps or failing to connect street-level NavMesh to rooftop NavMesh.

---

## 4. Constraint Retention Matrix

| Constraint ID | Name | Core Mandate | Rejection Trigger |
|---|---|---|---|
| **C1** | **No Interior Spaces** | Exterior collision volumes only; external stairs to roofs | Indoor mesh, indoor rooms, or indoor NavMesh |
| **C2** | **Solo BR Only** | Solo FFA survival; no squad logic | Squads, DBNO, revive, bleed-out |
| **C3** | **Server-Authoritative** | Dedicated server owns HP, Shield, storm, damage | Client-side damage or health modification |
| **C4** | **3rd Person Camera** | Over-the-shoulder; ADS zooms FOV only | 1st person mesh, FPS toggle |
| **C5** | **3 Build Materials** | Moloz, Tuğla, Çelik only | 4th material (Wood, Stone, Gold, etc.) |
| **C6** | **Hybrid Hit Detection** | AR/SMG/Sniper = HitScan; Rocket = Projectile Splash | Projectile AR or HitScan Rocket |
| **C7** | **BR Prefix** | Every class, struct, enum prefixed with `BR` | Missing `BR` prefix |
| **M1** | **10-Bot MVP Demo** | Total AI count capped at exactly 10 bots | > 10 bots configured in MVP test scenario |
| **M2** | **Dual Weapons (AR + RPG)** | 1 HitScan AR + 1 Projectile Rocket Launcher | Omitting either prototype in MVP slice |
| **M3** | **2 GameModes (FFA + BR)** | Separate FFA Deathmatch and Classic BR modes | Single hardcoded mode |
| **M4** | **Building Paused** | Natural cover only (vehicles, walls, alleys) | Requiring active build placement for MVP |
| **M5** | **Exterior Vertical Nav** | Street-to-roof via external stairs/fire escapes | Interior NavMesh or disconnected roofs |
