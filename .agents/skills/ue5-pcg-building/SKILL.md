---
name: ue5-pcg-building
description: UE5.6-UE5.8 PCG building generation workflow for modular buildings, blockouts, facade rules, and runtime generation. Use when requests involve Procedural Content Generation (PCG), Shape Grammar, lot-based building spawn, deterministic random seeds, density/filter pipelines, or converting designer constraints into reusable PCG graphs.
---

# Quick Start
- Define generation target: blockout towers, modular facades, or lot-based building sets.
- Define deterministic inputs: lot splines/points, district tags, style preset, and seed.
- Define runtime mode: static bake, on-demand, or runtime scheduled generation.
- Define output mode: Static Mesh instances first, Spawn Actor only for interactive/stateful parts.

# API Anchors (UE5.6-UE5.8)
- Runtime trigger and radii live on `UPCGComponent`:
  - `EPCGComponentGenerationTrigger::GenerateAtRuntime`
  - `bOverrideGenerationRadii`, `GenerationRadii`, `SchedulingPolicyClass`, `SchedulingPolicy`
  - `GenerateLocal(...)`, `Cleanup(...)`
- Runtime scheduler refresh lives on `UPCGSubsystem`:
  - UE5.6/UE5.7: `RefreshRuntimeGenComponent(...)`, `RefreshAllRuntimeGenComponents(...)`
  - UE5.8: `RefreshRuntimeGenExecutionSource(...)`, `RefreshAllRuntimeGenExecutionSources(...)`
  - UE5.8 deferred refresh: `DirtyRuntimeGenExecutionSources(...)`
  - Shared cleanup API: `CleanupLocalComponentsImmediate(...)`
- Output selection anchor classes:
  - `UPCGStaticMeshSpawnerSettings` for high-count rendering
  - `UPCGSpawnActorSettings` for interactive/stateful outputs
- Shape Grammar anchor classes:
  - `UPCGSubdivisionBaseSettings::GrammarSelection`
  - Do not rely on deprecated grammar fields (`bGrammarAsAttribute_DEPRECATED`, `Grammar_DEPRECATED`)

# Graph Stage Contract
- Every stage must explicitly declare:
  - Input data type (`EPCGDataType` or asset source)
  - Core node/classes (minimum two)
  - Required parameters (seed, tags, ranges, radii, or style keys)
  - Output data type
  - Debug method (node-level checks, debug node, or log/assert path)
- If a stage cannot satisfy these five items, treat the graph design as incomplete.

# Workflow
## 1) Input
- Input data type: actor/spline/point sources.
- Core node/classes: `UPCGDataFromActorSettings`, `UPCGGetActorPropertySettings`, `UPCGCreatePointsSettings`.
- Required parameters: lot tag filters, district/style tags, seed source, source bounds.
- Output: normalized lot point or spline data with stable ordering.
- Debug method: run `UPCGDebugSettings` after input stage and verify point count and bounds.

## 2) Filter
- Input data type: point/spline data from Input stage.
- Core node/classes: `UPCGAttributeFilteringSettings`, `UPCGDensityFilterSettings`, `UPCGFilterByTagSettings`.
- Required parameters: slope range, exclusion tags, min lot area/width, occupancy constraints.
- Output: only buildable lots/candidates.
- Debug method: compare candidate count before/after filter and inspect rejected tag distribution.

## 3) Transform
- Input data type: filtered buildable candidates.
- Core node/classes: `UPCGCopyPointsSettings`, `UPCGCreateSplineSettings`, `UPCGApplyScaleToBoundsSettings`.
- Required parameters: floor height, pivot convention, facade orientation basis, local axes.
- Output: footprint transforms and per-floor transforms.
- Debug method: inspect transform axes and floor index attributes on output points.

## 4) Grammar
- Input data type: segment/spline/point data from Transform stage.
- Core node/classes: `UPCGSubdivideSplineSettings`, `UPCGSubdivideSegmentSettings`, `UPCGSelectGrammarSettings`.
- Required parameters: `GrammarSelection`, module size limits, style-based grammar key mapping.
- Output: grammar-resolved module placements/attributes.
- Debug method: use `UPCGPrintGrammarSettings` for grammar parse and token validation.
- Rule: use `GrammarSelection` only; avoid deprecated grammar fields.

## 5) Output
- Input data type: grammar-resolved placements.
- Core node/classes: `UPCGStaticMeshSpawnerSettings`, `UPCGSpawnActorSettings`, `UPCGCreateTargetActor`.
- Required parameters:
  - Static path: mesh selector, instance packer, ISM/HISM policy.
  - Actor path: actor class, spawn attributes, state/interaction requirements.
- Output: rendered buildings and optional interactive building elements.
- Debug method: split output by layer/tag and validate per-layer counts.
- Default policy: prefer Static Mesh Spawner; use Spawn Actor only when stateful behavior is required.

## 6) Validate
- Input data type: final spawned result and runtime generation state.
- Core node/classes: `UPCGDebugSettings`, `UPCGComponent`, `UPCGSubsystem`.
- Required parameters: expected cell bounds, max per-update spawn budget, nav/collision expectations.
- Output: pass/fail signals and fix actions.
- Debug method: run staged checks for overlap, navigation impact, per-cell generation time, and deterministic replay.

# Constraints
- Keep the main pipeline compatible with UE5.6-UE5.8 unless a version-specific note is required.
- Runtime generation must explicitly set:
  - `GenerationTrigger = GenerateAtRuntime`
  - explicit `GenerationRadii` (do not rely on implicit defaults)
  - explicit `SchedulingPolicyClass` for predictable scheduler behavior
- Prefer ISM/HISM style output for large counts; avoid spawning heavyweight actors for each small part.
- Keep runtime generation bounds explicit to avoid uncontrolled world-wide regeneration.
- Avoid hidden dependency on editor-only data when runtime generation is expected.
- Treat World Partition boundaries as hard constraints for runtime scopes.

# Failure Handling
- Symptom: no buildings spawn.
  - Locate: Input stage output count, source bounds, lot tags.
  - Fix: verify source actor/spline ingestion and lot filter tags; confirm non-empty candidate set.
- Symptom: output exists in editor preview but not runtime.
  - Locate: `GenerationTrigger` and runtime radii/scheduling settings.
  - Fix: set `GenerateAtRuntime`, radii override, and valid scheduling policy.
- Symptom: runtime update regenerates too wide an area.
  - Locate: runtime radii and generation source movement.
  - Fix: reduce generation/cleanup radii and tighten source bounds.
- Symptom: stale generated pieces remain after rules shrink.
  - Locate: cleanup path and local component lifecycle.
  - Fix: trigger cleanup with remove-components behavior and force local cleanup when needed.
- Symptom: heavy hitching during runtime generation.
  - Locate: points-per-cell, actor spawn count, per-update workload.
  - Fix: reduce per-cell complexity, cap actor spawns, move non-interactive parts to static mesh instances.
- Symptom: deterministic replay mismatch with same seed.
  - Locate: unstable upstream point ordering or non-seeded random branch.
  - Fix: normalize ordering before random selection and bind every stochastic path to explicit seed inputs.
- Symptom: facade grammar fails or produces empty modules.
  - Locate: grammar parse logs and module token mapping.
  - Fix: validate grammar string, module dictionary, and segment size constraints.
- Symptom: overlap and collision issues.
  - Locate: filter thresholds and final placement constraints.
  - Fix: add clearance/slope filters and occupancy rejection before output stage.
- Symptom: navmesh degradation around generated buildings.
  - Locate: collision profile and nav-affecting flags on spawned outputs.
  - Fix: split nav-affecting vs non-nav-affecting outputs and rebuild nav only where required.
- Symptom: runtime changes do not apply after parameter edits.
  - Locate: scheduler refresh flow.
  - Fix: request runtime scheduler refresh for the modified component or all runtime components.

# Runtime Scheduler Ops
- Use component refresh when one runtime component changed style/radii/scheduling inputs.
- Use global refresh when style/global rules changed for many runtime components.
- Use immediate local cleanup when bounds shrink or partition ownership changed.
- After cleanup, trigger local regeneration only for affected runtime scope.

# UE5.6-UE5.8 Compatibility Notes
- Core runtime trigger and grammar APIs above are stable in UE5.6-UE5.8.
- UE5.8 adds non-destructive manual editing and complex metadata attribute values; treat these as optional 5.8 capabilities rather than requirements for cross-version graphs.
- Header path difference for subsystem:
  - UE5.6 commonly uses `Public/PCGSubsystem.h`
  - UE5.7/UE5.8 use `Public/Subsystems/PCGSubsystem.h` and include `Subsystems/PCGSubsystem.h`
- UE5.8 deprecates component-named scheduler refresh calls. Use the `IPCGGraphExecutionSource`-based APIs in 5.8 code; retain the component-based calls only for 5.6/5.7 branches.

# Escalation
- Escalate when architecture requires custom C++ PCG elements or engine plugin extension.
- Escalate when city-scale generation must be integrated with World Partition streaming policy.
- Escalate when generated layout must be synchronized with save/load or multiplayer authority rules.
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

### Domain Adaptation: PCG & Building Generation
- **Exterior Only**: PCG graphs must ONLY generate exterior facade shells and bounding collision hulls. Never generate internal partitions, rooms, doors, or furniture.
- **Rooftop Navigation**: Generate external staircases, scaffolding, or fire escapes on building exteriors to enable vertical gameplay to rooftops.
- **NavMesh Exclusion**: Ensure generated building footprints write to `NavArea_Null` so navigation mesh generates exclusively on outdoor streets, alleys, and exterior stairways.

