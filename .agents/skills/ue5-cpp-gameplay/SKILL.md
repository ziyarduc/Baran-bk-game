---
name: ue5-cpp-gameplay
description: UE5.6-UE5.8 gameplay C++ implementation for Actors, Components, DataAssets, and gameplay logic. Use when requests ask to write .h/.cpp pairs, expose UPROPERTY/UFUNCTION to Blueprint, use GameplayTags, or build reusable component-based systems.
---

# Quick Start
- Confirm target class type (`AActor`, `UActorComponent`, `UObject`, `USaveGame`, etc.).
- Define required Blueprint-facing API before implementation.
- Output both header and source files together.

# API Anchors (UE5.6-UE5.8)
- Reflection and UObject anchors:
  - `UCLASS`, `USTRUCT`, `UENUM`, `UINTERFACE`, `GENERATED_BODY()`
  - `UPROPERTY(...)`, `UFUNCTION(...)`
- Core gameplay type anchors:
  - `AActor`, `UActorComponent`, `UDataAsset`, `UGameInstanceSubsystem`
  - `TObjectPtr<>` in headers and `TSubclassOf<>` for class references
- Replication anchors:
  - `GetLifetimeReplicatedProps(...)`
  - `DOREPLIFETIME(...)` in `Net/UnrealNetwork.h`
  - `ReplicatedUsing=OnRep_*`, `UFUNCTION(Server/Client/NetMulticast, ...)`
- Gameplay tag anchors:
  - `FGameplayTag`, `FGameplayTagContainer`
  - explicit tag request/match checks with safe fallback behavior

# Implementation Stage Contract
- Every gameplay C++ task must define:
  - Public header API surface (Blueprint/API visibility)
  - Private runtime implementation path (`.cpp`)
  - Ownership/lifetime model (constructor, init, teardown)
  - Network authority rules (single-player only or replicated flow)
  - Validation method (compile assumptions, usage examples, edge-case behavior)
- If any item is missing, the implementation spec is incomplete.

# Workflow
## 1) Type and File Shape
- Create type declarations with Unreal macros and UE5 pointer conventions (`TObjectPtr` in headers).
- Produce paired `.h` and `.cpp` with forward declarations in header and concrete includes in source.
- Keep class responsibility narrow and reusable.

## 2) Public API Design
- Define Blueprint API (`BlueprintCallable`, `BlueprintPure`, categories, metadata) before implementation.
- Expose minimal callable surface; keep helper methods non-UFUNCTION unless needed.
- Declare clear input/output contracts and failure behavior.

## 3) Runtime Implementation
- Implement logic in `.cpp` with null checks, authority guards, and explicit branch behavior.
- Keep tick usage opt-in; prefer event-driven updates.
- Handle initialization order (`BeginPlay`, `InitializeComponent`, or subsystem init) explicitly.

## 4) Replication and RPC (When Needed)
- Add replicated properties and `OnRep_*` handlers only for true client-visible state.
- Register properties in `GetLifetimeReplicatedProps(...)` with `DOREPLIFETIME(...)`.
- Use server-authoritative RPC entry points for client requests.

## 5) GameplayTags and Data-Driven Hooks
- Use `FGameplayTag`/`FGameplayTagContainer` with explicit tag names.
- Validate required tags at runtime and provide fallback for missing tags.
- Prefer DataAsset-driven config for tunables over hard-coded constants.

## 6) Validation Output
- Ensure output includes both files and required includes.
- Confirm Blueprint exposure, replication behavior, and error-handling paths are documented.
- Provide usage snippet or invocation flow when behavior is non-trivial.

# Constraints
- Always provide matching `.h` and `.cpp` when creating a class.
- Use non-deprecated APIs compatible with UE5.6-UE5.8.
- Keep includes minimal; use forward declarations in headers.
- Avoid hardcoded asset paths unless explicitly requested.
- Prefer `TObjectPtr<>` in UPROPERTY object references in headers.
- Keep server-authoritative checks explicit for any network-affecting gameplay action.

# Failure Handling
- Symptom: class compiles but is missing from Blueprint.
  - Locate: missing `BlueprintType`/`Blueprintable`/`BlueprintCallable` metadata.
  - Fix: add required reflection specifiers and regenerate project files/build.
- Symptom: unresolved symbol or include cycles.
  - Locate: header include graph and forward declaration misuse.
  - Fix: move heavy includes to `.cpp`, keep forward declarations in headers.
- Symptom: replicated property does not update on clients.
  - Locate: `GetLifetimeReplicatedProps(...)` and actor/component replication flags.
  - Fix: register with `DOREPLIFETIME(...)`, ensure owning actor replicates.
- Symptom: `OnRep_*` never fires.
  - Locate: property write path and net role.
  - Fix: mutate on server authority path and verify property actually changes.
- Symptom: RPC callable but ignored at runtime.
  - Locate: RPC specifier and call site authority.
  - Fix: enforce client->server request path and server-side validation.
- Symptom: GameplayTag logic silently fails.
  - Locate: invalid tag names or missing tag config.
  - Fix: validate tags on startup and guard with explicit fallback behavior.

# UE5.6-UE5.8 Compatibility Notes
- Reflection, replication, and GameplayTag APIs above are stable across UE5.6-UE5.8.
- Favor stable core APIs over editor-only helpers when runtime behavior is required.

# Escalation
- Escalate when user asks for plugin/module-level refactor beyond a single gameplay class.
- Escalate when solution needs custom engine source modifications.
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

