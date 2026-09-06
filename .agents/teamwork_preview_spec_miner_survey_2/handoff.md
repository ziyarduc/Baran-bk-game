# Survey Spec Miner 2 Handoff Report: UE5 Domain Knowledge (R4 - Genişletilmiş Skills)

## 1. Observation

### 1.1 Direct Repository Probing
We conducted direct online API and web queries against the two specified GitHub repositories:
1. **`UnrealXu/UnrealEngine5-Skills`** (`https://github.com/UnrealXu/UnrealEngine5-Skills`)
   - Branch: `main`
   - Content: 11 domain/routing skills under `skills/`, supplementary assets under `skills/assets/`, and validation scripts under `skills/scripts/` (`validate_skills.py`, `validate_engine_anchors.py`).
   - Compatibility: Specifically updated for Unreal Engine 5.6 to 5.8 with version-aware API anchors and stage contracts.
2. **`kevinpbuckley/unreal-engine-skills`** (`https://github.com/kevinpbuckley/unreal-engine-skills`)
   - Branch: `master`
   - Content: Organized under `skills/` into three directories:
     - `skills/core/`: 47 comprehensive UE5 C++ and system skills.
     - `skills/ultra-dynamic-sky/`: 10 specialized UDS skills.
     - `skills/ultra-dynamic-weather/`: 5 specialized UDW skills.
   - Total upstream skills in repository: 62 skills.
   - Structure: Each skill has a `SKILL.md` plus a `references/` directory containing granular markdown deep-dives with verbatim Epic source code citations.

### 1.2 Local Project Workspace State
- Path: `C:\Users\silver\Desktop\bakirkoy-br\.agents\skills`
- An enumeration revealed 68 directories and 2 files (`README.md`, `category.md`).
- File counts:
  - Exactly **66 directories** contain a valid `SKILL.md`.
  - Exactly **2 directories** are non-skill resource directories (`assets/` and `scripts/`).
- Category breakdown of existing 66 local skills:
  - **11 skills** from `UnrealXu/UnrealEngine5-Skills` (prefixed with `ue5-*`).
  - **47 skills** from `kevinpbuckley/unreal-engine-skills` (the entire `skills/core` set).
  - **8 skills** representing Bakırköy BR Agent Role Skills (`orchestrator`, `qa-reviewer`, `integrator`, `worker-ai-agents`, `worker-building-system`, `worker-gameloop-backend`, `worker-map-world`, `worker-weapons-combat`).
- Automated Validation:
  - Executing `python .\skills\scripts\validate_skills.py` returned: `Validation OK - skills checked: 11 - no frontmatter/BOM/legacy-token issues found`.
  - Executing a comprehensive Python validator across all 66 local skills confirmed that **100% of the 66 skills** have valid YAML frontmatters, matching folder names, non-empty descriptions, and no UTF-8 BOM encoding.

---

## 2. Logic Chain

### 2.1 Ecosystem Size and Target Achievement
1. The user request (R4) requires: *"UnrealXu/UnrealEngine5-Skills ve kevinpbuckley/unreal-engine-skills depolarından çekilecek 60+ yetenek dosyasının (Gameplay Ability System, Enhanced Input, Chaos, World Partition) projeye uyarlanması."*
2. We verified that between `UnrealXu` (11 skills) and `kevinpbuckley` (62 skills: 47 core + 15 UDS/UDW), there are **73 unique external skills** available.
3. In addition, Bakırköy BR possesses 8 specialized multi-agent worker/lead skills.
4. The local project already hosts **66 fully-formed `SKILL.md` skill packages**, directly satisfying and exceeding the 60+ skill target.

### 2.2 Harmonization of Repository Formats
1. `UnrealXu` skills emphasize high-level architectural stage contracts (`# Graph Stage Contract`, `# Implementation Stage Contract`) and UE5.6-UE5.8 version anchors.
2. `kevinpbuckley` skills emphasize modular C++ implementation patterns, exact API headers, class hierarchies, and `references/` sub-markdown files.
3. Both formats share the standard Antigravity/Codex convention: `.agents/skills/<skill-name>/SKILL.md` with YAML frontmatter containing `name` and `description`.
4. Therefore, keeping all skills in a flat hierarchy under `.agents/skills/<skill-name>/` while maintaining their internal `references/` folders provides optimal modularity and agent discovery.

### 2.3 Bakırköy BR Core Constraints & Adaptation Necessity
Unadapted generic UE5 skills contain patterns that directly contradict the 7 non-negotiable Bakırköy BR rules:
- Generic building/PCG skills assume interior rooms, doors, and interior NavMeshes, violating **Constraint 1 (No Interior Spaces)**.
- Generic multiplayer skills assume squads/duos/revives, violating **Constraint 2 (Solo BR Only)**.
- Generic movement/input skills allow client-authoritative actions or 1st person ADS, violating **Constraint 3 (Server-Authoritative)** and **Constraint 4 (3rd Person Camera Only)**.
- Generic building skills assume 4 materials or Fortnite archetypes (Wood/Stone/Metal), violating **Constraint 5 (3 Build Materials: Moloz, Tuğla, Çelik)**.
- Generic combat skills lack the specific hybrid distinction, violating **Constraint 6 (Hybrid Hit Detection: Hit-scan for rifles/shotgun/sniper vs Projectile physics for Rocket Launcher)**.
- Generic C++ samples use generic prefixes (`ACharacter`, `AMyWeapon`), violating **Constraint 7 (Mandatory `BR` Prefix: `ABRCharacter`, `ABRWeaponBase`)**.

---

## 3. Features Discovered (Full Inventory of 81 Skills)

### 3.1 UnrealXu/UnrealEngine5-Skills (11 Skills)
| # | Category | Feature / Skill | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|-----------------|-------------|--------|---------|----------------|----------------|
| 1 | Architecture | `ue5-architecture` | Architecture planning, module dependencies, UObject vs plain C++ | Project requirements | Module dependency graph, Build.cs rules | Circular dependency compile error | UnrealXu GitHub |
| 2 | Routing | `ue5-auto-assistant` | Intent-based automatic routing for developer requests | Natural language prompts | Recommended skill target | Fallback to general guidance | UnrealXu GitHub |
| 3 | Blueprint | `ue5-blueprint-workflow` | BP graph workflows, node selection, pure/impure design | Feature logic | Clean BP node patterns, interface calls | Invalid cast/null node warnings | UnrealXu GitHub |
| 4 | C++ Gameplay | `ue5-cpp-gameplay` | Gameplay C++ patterns, Actor/Component/DataAsset templates | Feature spec | Reusable .h/.cpp class pairs | UHT reflection errors | UnrealXu GitHub |
| 5 | Debugging | `ue5-debug-validation` | Debugging workflows, Visual Logger, console commands, crash dumps | Bug report / crash log | Root cause diagnosis, fix strategy | Missing symbol warning | UnrealXu GitHub |
| 6 | Routing | `ue5-module-router` | Engine module routing based on module names and aliases | Module alias / type name | Primary engine module citation | Unknown module error | UnrealXu GitHub |
| 7 | World / PCG | `ue5-pcg-building` | PCG graph workflows for modular facade and building blockouts | Lot splines, style presets | Instanced mesh building shells | Degenerate spline error | UnrealXu GitHub |
| 8 | Performance | `ue5-performance-packaging` | Cook, package, and performance profiling workflows | Project assets, target platform | Packaged shipping build | Cook failure / missing asset error | UnrealXu GitHub |
| 9 | Persistence | `ue5-save-load-replication` | SaveGame serialization and networked replication flows | Gameplay state structs | Replicated state, binary saves | Replication desync / dirty bit failure | UnrealXu GitHub |
| 10| UI | `ue5-ui-umg-slate` | UMG user widget design, MVVM binding, Slate syntax | UI specifications | Bound UserWidget classes | Invalid binding / null VM crash | UnrealXu GitHub |
| 11| Interaction | `ue5-world-interaction` | World interaction systems, line traces, proximity prompts | Collision queries, trace channels | Focused interactable actor | Missed trace / null hit | UnrealXu GitHub |

### 3.2 kevinpbuckley/unreal-engine-skills — Core Systems (47 Skills)
| # | Category | Feature / Skill | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|-----------------|-------------|--------|---------|----------------|----------------|
| 12| Core C++ | `cpp-fundamentals` | UObject reflection, GC, CDO, lifecycle | C++ declarations | UCLASS/USTRUCT implementations | GC dangling pointer / memory leak | kevinpbuckley GitHub |
| 13| Core C++ | `core-types-and-containers` | TArray, TMap, TSet, FString, FName, FText, FVector | Data requirements | High-performance Unreal types | Out-of-bounds assertion | kevinpbuckley GitHub |
| 14| Core C++ | `memory-and-gc` | TObjectPtr, TWeakObjectPtr, TSharedPtr, GC sweeps | Object references | Leak-free memory management | Dangling pointer crash | kevinpbuckley GitHub |
| 15| Standards | `coding-standards` | Epic C++ conventions, naming, Allman style, IWYU | C++ code | Clean, readable engine code | Style violation / UHT prefix error | kevinpbuckley GitHub |
| 16| Build | `module-and-build-system` | .Build.cs, .Target.cs, public/private dependencies | Module layout | Modular compilation units | Missing symbol linker error | kevinpbuckley GitHub |
| 17| Build | `plugins-and-modules` | Plugin descriptors (.uplugin), modular engine plugins | Plugin feature set | Decoupled plugin architecture | Circular dependency error | kevinpbuckley GitHub |
| 18| Architecture | `project-structure` | Config files (.ini), directory layouts, Content conventions | Project assets | Well-organized repository structure | File path resolution error | kevinpbuckley GitHub |
| 19| Architecture | `subsystems` | GameInstance, World, LocalPlayer subsystems | Persistent logic spec | Clean singleton-alternative subsystems | Early shutdown crash | kevinpbuckley GitHub |
| 20| Core C++ | `timers-and-async` | FTimerManager, async tasks, thread safety | Delayed / periodic tasks | Non-blocking gameplay timers | Cleared handle warning | kevinpbuckley GitHub |
| 21| Meta | `navigating-engine-source` | Locating and citing exact UE5 engine source lines | Engine symbols | Verified source code citations | Symbol not found | kevinpbuckley GitHub |
| 22| Architecture | `gameplay-architecture-planning` | Designing clean separation of concerns in UE5 | Feature requirements | Architectural decision matrix | Tightly coupled spaghetti code | kevinpbuckley GitHub |
| 23| Gameplay | `gameplay-framework` | GameMode, GameState, PlayerState, PlayerController, Pawn | Game rules | Server-authoritative match loop | Controller possession desync | kevinpbuckley GitHub |
| 24| Gameplay | `character-and-movement` | ACharacter, CMC, capsule setup, root motion | Controller input | Predictable networked movement | CMC desync rubberbanding | kevinpbuckley GitHub |
| 25| Gameplay | `mover-movement-system` | UE5 experimental Mover 2.0 network prediction | Movement buffers | Rollback-safe movement states | Resimulation error | kevinpbuckley GitHub |
| 26| Input | `enhanced-input` | UInputAction, IMC, triggers, modifiers, contexts | Key/stick input events | Dispatched gameplay actions | Context priority conflict | kevinpbuckley GitHub |
| 27| Gameplay | `actors-and-components` | AActor, UActorComponent, USceneComponent hierarchy | Component requests | Modular actor assembly | Detached scene root bug | kevinpbuckley GitHub |
| 28| Gameplay | `gameplay-ability-system` | GAS: ASC, GameplayAbility, AttributeSet, GameplayEffects | Ability specs, tags | Replicated abilities and attributes | Prediction failure / tag block | kevinpbuckley GitHub |
| 29| Gameplay | `gameplay-tags` | FGameplayTag, native tags, tag containers, queries | Gameplay state flags | Fast tag queries and filtering | Unregistered tag assertion | kevinpbuckley GitHub |
| 30| Core C++ | `delegates-and-events` | Single-cast, multi-cast, dynamic replicated delegates | Event triggers | Decoupled event callbacks | Dangling delegate invocation | kevinpbuckley GitHub |
| 31| Data | `data-driven-design` | DataTables, DataAssets, CurveTables | External CSV/JSON/uasset | Designer-tunable data assets | Missing row in table error | kevinpbuckley GitHub |
| 32| Networking | `networking-and-replication` | Net roles, RPCs, RepNotify, DOREPLIFETIME, Iris | Network packets | Deterministic server authority | Authority check failure | kevinpbuckley GitHub |
| 33| World | `levels-and-world-partition` | World Partition, streaming sources, Data Layers | Spatial cell layout | Seamless streaming open world | Streaming cell starvation | kevinpbuckley GitHub |
| 34| World | `landscape-and-foliage` | Landscape streaming, heightmaps, foliage instances | Terrain assets | Realistic terrain with foliage | Foliage density memory spike | kevinpbuckley GitHub |
| 35| World | `asset-management` | UAssetManager, primary asset IDs, async bundling | Asset references | On-demand streaming memory footprint| Hard reference memory leak | kevinpbuckley GitHub |
| 36| Physics | `physics-and-chaos` | Chaos physics, collision channels, traces, ragdolls | Physics queries/forces | Realistic collisions and sweeps | Missing overlap event | kevinpbuckley GitHub |
| 37| AI | `ai-and-navigation` | AIController, BehaviorTree, Blackboard, NavMesh, EQS | Perception stimuli | Smart autonomous NPC behaviors | Broken NavMesh path failure | kevinpbuckley GitHub |
| 38| Rendering | `nanite-and-rendering` | Nanite virtualized geometry, LOD-free meshes | High-poly meshes | High-fidelity real-time rendering | Unsupported shader fallback | kevinpbuckley GitHub |
| 39| Rendering | `materials-and-shaders` | UMaterial, material instances, shaders | Texture inputs | PBR surface shaders | Shader compile timeout | kevinpbuckley GitHub |
| 40| Rendering | `lighting-and-lumen` | Lumen dynamic GI, directional lights, skylight | Lighting parameters | Realistic dynamic global illumination| Light leak artifact | kevinpbuckley GitHub |
| 41| Rendering | `meshes-static-and-skeletal` | StaticMesh, SkeletalMesh, sockets, collision hulls | 3D mesh assets | Rendered and collided meshes | Missing root bone error | kevinpbuckley GitHub |
| 42| Animation | `animation-system` | AnimInstance, AnimMontage, BlendSpace, state machines | Pose inputs | Smooth skeletal character animations | Missing bone blend warning | kevinpbuckley GitHub |
| 43| Animation | `control-rig-and-ik` | Procedural IK, foot placement, weapon aim offset | Target vectors | Natural procedural pose adjustments | IK constraint unsolvable | kevinpbuckley GitHub |
| 44| Cinematics | `sequencer-and-cinematics` | LevelSequence, cinematic cameras, track bindings | Animation tracks | Pre-rendered or real-time cutscenes | Missing binding object warning | kevinpbuckley GitHub |
| 45| VFX | `niagara-vfx` | Niagara particle systems, emitters, ribbons, meshes | Particle parameters | Optimized visual effect simulations | GPU emitter memory overflow | kevinpbuckley GitHub |
| 46| Audio | `audio-and-metasounds` | MetaSounds, sound cues, spatialization, submixes | Audio triggers | High-fidelity 3D spatialized sound | Voice concurrency starvation | kevinpbuckley GitHub |
| 47| UI | `umg-and-slate` | UUserWidget, CanvasPanel, DPI scaling, Slate | UI layouts | Interactive HUD and menus | Widget hierarchy invalidation | kevinpbuckley GitHub |
| 48| Blueprint | `blueprint-fundamentals` | Visual scripting graphs, events, macros, variables | Blueprint graphs | Rapid gameplay prototype logic | Infinite loop execution abort | kevinpbuckley GitHub |
| 49| Blueprint | `blueprint-cpp-integration` | Exposing C++ functions, properties, and interfaces | C++ declarations | Seamless BP/C++ interop | Missing BlueprintType specifier | kevinpbuckley GitHub |
| 50| Debugging | `debugging-techniques` | DrawDebug, Gameplay Debugger, on-screen messages | Debug commands | Visual runtime diagnostic overlays | Debug draw performance hitch | kevinpbuckley GitHub |
| 51| Profiling | `profiling-and-optimization` | Unreal Insights, stat commands, memory tracking | Performance traces | Bottleneck analysis and frame budget | Profiler buffer overflow | kevinpbuckley GitHub |
| 52| Profiling | `game-thread-performance` | Tick budgeting, async physics, worker threads | Tick functions | Stable 60+ FPS game thread | Game thread bottleneck stall | kevinpbuckley GitHub |
| 53| Testing | `automation-and-testing` | Automation specs, unit tests, latent commands | Test suites | Pass/Fail automated CI test reports | Test assertion failure | kevinpbuckley GitHub |
| 54| Editor | `editor-scripting-and-python` | Editor utility widgets, Python scripts, Blutilities | Automation scripts | Automated editor batch operations | Python script syntax error | kevinpbuckley GitHub |
| 55| Build | `packaging-and-deployment` | Cook, stage, package, shipping build automation | Project source | Distributable game package | Missing DLL / cooking crash | kevinpbuckley GitHub |
| 56| Content | `importing-content` | FBX, glTF, Interchange pipeline, asset import | Raw 3D/audio files | Engine-native uasset representations | Corrupt asset import error | kevinpbuckley GitHub |
| 57| Persistence | `save-and-load` | USaveGame, binary serialization, async saving | Game state structs | Saved game file on disk | Corrupted save slot error | kevinpbuckley GitHub |
| 58| Diagnostics | `logging-and-assertions` | UE_LOG, check, ensure, log categories | Log messages | Structured engine and debug logs | Fatal check failure crash | kevinpbuckley GitHub |

### 3.3 kevinpbuckley/unreal-engine-skills — Ultra Dynamic Sky & Weather (15 Upstream Skills)
| # | Category | Feature / Skill | Description | Upstream Subfolder |
|---|----------|-----------------|-------------|--------------------|
| 59| Sky/Atmosphere | `uds-cinematics-rendering` | Cinematic captures, high-res sky renders, movie queue | `ultra-dynamic-sky` |
| 60| Sky/Atmosphere | `uds-clouds` | Volumetric and 2D cloud layers, density, coverage | `ultra-dynamic-sky` |
| 61| Sky/Atmosphere | `uds-fog-and-atmosphere` | Exponential height fog, volumetric lighting, Rayleigh | `ultra-dynamic-sky` |
| 62| Sky/Atmosphere | `uds-lighting-and-shadows` | Sun/moon directional light alignment, dynamic shadows | `ultra-dynamic-sky` |
| 63| Sky/Atmosphere | `uds-modifiers-configs-state` | Weather/sky state overrides, configuration presets | `ultra-dynamic-sky` |
| 64| Sky/Atmosphere | `uds-performance-mobile-troubleshooting` | Mobile optimizations, volumetric cloud downsampling | `ultra-dynamic-sky` |
| 65| Sky/Atmosphere | `uds-setup-and-modes` | Basic UDS actor placement, time modes, sky types | `ultra-dynamic-sky` |
| 66| Sky/Atmosphere | `uds-simulation` | Day/night cycle time stepping, star rotations | `ultra-dynamic-sky` |
| 67| Sky/Atmosphere | `uds-sun-moon-stars` | Celestial body orbits, lunar phases, star map | `ultra-dynamic-sky` |
| 68| Sky/Atmosphere | `uds-time` | Game time synchronization, calendar, time-of-day | `ultra-dynamic-sky` |
| 69| Weather | `udw-material-and-screen-effects` | Wetness shaders, puddles, rain drops on camera | `ultra-dynamic-weather` |
| 70| Weather | `udw-particles-lightning-wind-sounds` | Rain/snow particles, thunder, ambient wind audio | `ultra-dynamic-weather` |
| 71| Weather | `udw-random-seasons-temperature` | Procedural weather changes, seasons, temperature | `ultra-dynamic-weather` |
| 72| Weather | `udw-setup-and-state` | UDW master actor integration, initial weather state | `ultra-dynamic-weather` |
| 73| Weather | `udw-spatial-weather` | Localized storm cells, weather exclusion volumes | `ultra-dynamic-weather` |

### 3.4 Bakırköy BR Agent Role Skills (8 Skills in `.agents/skills`)
| # | Category | Feature / Skill | Description | Key Modules Owned |
|---|----------|-----------------|-------------|--------------------|
| 74| Agent Role | `orchestrator` | Overall team workflow supervisor and task dispatcher | Project management, AGENTS.md |
| 75| Agent Role | `qa-reviewer` | Code and design reviewer enforcing BR rules | Verification, linting, tests |
| 76| Agent Role | `integrator` | Cross-module compiler and dependency resolver | Source/BakirkoyBR build health |
| 77| Agent Role | `worker-weapons-combat` | Weapon system, damage model, hit-scan vs projectile | `Weapons/` (BRWeaponBase, HitScan, Projectile) |
| 78| Agent Role | `worker-building-system` | 3-material building system, turbo build, piece editing | `Building/` (BRBuildingComponent, BRBuildPiece) |
| 79| Agent Role | `worker-gameloop-backend` | Storm circle, match loop, inventory, solo state | `GameLoop/` (BRGameMode, BRGameState, BRStorm) |
| 80| Agent Role | `worker-map-world` | Bakırköy map (3.2km×2.1km), POIs, loot tiers | `Map/`, `Data/` (BRLootManager, POIs) |
| 81| Agent Role | `worker-ai-agents` | Bot AI controllers, solo BR behavior trees, patrol | `AI/` (BRAIController, BRBotCharacter) |

---

## 4. Edge Cases & Constraints Analysis

| # | Feature / Skill | Constraint Input | Observed Conflict & Required Adaptation Behavior |
|---|-----------------|------------------|---------------------------------------------------|
| 1 | `ue5-pcg-building` | Interior geometry generation | **Conflict**: Generic PCG generates room partitions and furniture.<br>**Adaptation**: Must ONLY generate exterior facade shells and bounding collision hulls. Rooftops must be accessible only via exterior staircases. |
| 2 | `ai-and-navigation` | NavMesh on building footprints | **Conflict**: NavMesh generates inside hollow building models, causing AI to walk through walls.<br>**Adaptation**: Place `NavModifierVolume(NavArea_Null)` over all building bounding boxes. AI NavMesh is restricted to outdoor roads, sidewalks, and open plazas. |
| 3 | `gameplay-framework` | Team/squad multiplayer rules | **Conflict**: Generic frameworks replicate squad indices, shared revives, and squad chat.<br>**Adaptation**: Must strictly enforce Solo BR mode. Eliminate team structures (`ABRPlayerState` stores only individual score/eliminations). Match ends when remaining players <= 1. |
| 4 | `character-and-movement`| Camera perspective | **Conflict**: Default FPS/TPS templates switch to 1st person on iron sights ADS.<br>**Adaptation**: Must enforce over-the-shoulder 3rd Person Camera. ADS zooms spring arm and FOV, but stays strictly in 3rd person. |
| 5 | `worker-building-system`| Building materials | **Conflict**: Common BR setups use 4 materials or Fortnite wood/stone/metal.<br>**Adaptation**: Enforce strictly 3 materials: Moloz (Debris: 60 start HP, 100 max HP), Tuğla (Brick: 80 start HP, 200 max HP), Çelik (Steel: 100 start HP, 350 max HP). |
| 6 | `worker-weapons-combat` | Hit detection paradigm | **Conflict**: Inconsistent use of projectile vs line-trace across weapons.<br>**Adaptation**: Enforce Hybrid model: SMG, AR, Sniper, Shotgun = Server Hit-Scan (`LineTraceSingleByChannel`); Rocket Launcher = Projectile Physics (`ABRProjectile` with 35 m/s velocity). |
| 7 | `coding-standards` | C++ class naming conventions | **Conflict**: Developers creating generic classes (`ACharacter`, `AWeapon`, `UBuildingComponent`).<br>**Adaptation**: Enforce mandatory `BR` prefix on all gameplay classes: `ABRCharacter`, `UBRHealthComponent`, `ABRWeaponBase`, `ABRBuildPiece`. |
| 8 | `networking-and-replication`| State authority | **Conflict**: Client predicting health changes or destruction state.<br>**Adaptation**: Server-authoritative: HP, shields, ammo consumption, structure health, and storm circle transitions are mutated ONLY on the server. Clients receive replicated state and fire RepNotifies for cosmetics. |
| 9 | `gameplay-ability-system`| Down-But-Not-Out (DBNO) | **Conflict**: GAS ability packages often include bleed-out states and teammate revive mechanics.<br>**Adaptation**: Immediate elimination upon zero health in Solo BR (`EBRActorState::Eliminated`). No DBNO tasks or friendly revive abilities. |

---

## 5. Adaptation Requirements for Bakırköy BR Core Constraints

To guarantee that agent developers never violate the project rules when referencing these skills, each skill file must be injected with a standardized compliance block:

### Mandatory Rule Injection Template
```markdown
## Bakırköy BR Core Constraints & Compliance
When applying this skill to the Bakırköy BR project, you MUST strictly adhere to:
1. **No Interior Spaces**: Never author or generate interior rooms, furniture, or interior NavMesh. Buildings are solid exterior collision hulls with outdoor-only rooftop access.
2. **Solo BR Only**: No squad logic, no revives, no DBNO, no team chat. Solo free-for-all mechanics only.
3. **Server-Authoritative**: All health, shield, weapon damage, inventory, and building state changes must execute on the dedicated server. Clients send intent via RPCs.
4. **3rd Person Camera**: Over-the-shoulder perspective only. ADS tightens camera FOV and arm length, but NEVER switches to 1st person.
5. **3 Build Materials**: Only Moloz (Debris), Tuğla (Brick), and Çelik (Steel). No other building materials exist.
6. **Hybrid Hit Detection**: Rifles, SMG, Shotgun, and Sniper use server Hit-Scan line traces. Rocket Launchers use Chaos Projectile Physics actors.
7. **C++ `BR` Prefix**: Every gameplay C++ class MUST start with `BR` (e.g., `ABRCharacter`, `UBRBuildingComponent`, `FBRWeaponData`).
```

---

## 6. End-to-End Plan to Fetch, Curate, Adapt, and Catalog (60+ Skills)

### Phase 1: Verification of Existing Local Assets (Completed)
- Audit of `.agents/skills`: 66 valid skill directories are already present on disk (11 UnrealXu + 47 kevinpbuckley core + 8 Bakırköy BR roles).
- Ran automated syntax and frontmatter validator across all 66 skills. All 66 pass with zero errors.

### Phase 2: Upstream Synchronization & Ingestion of UDS/UDW (Optional Extension)
- Upstream `kevinpbuckley` contains 15 additional weather/sky skills:
  - 10 Ultra Dynamic Sky skills (`uds-*`)
  - 5 Ultra Dynamic Weather skills (`udw-*`)
- If the Bakırköy atmospheric storm and Marmara Sea weather require dynamic sky systems, fetch these 15 skills into `.agents/skills/` via a PowerShell/Python GitHub API script, bringing the total to 81 skills.

### Phase 3: Project-Specific Constraint Injection (Curation)
- For the 12 primary gameplay and world skills (`ue5-pcg-building`, `character-and-movement`, `networking-and-replication`, `gameplay-ability-system`, `physics-and-chaos`, `levels-and-world-partition`, `enhanced-input`, `coding-standards`, `ai-and-navigation`, `gameplay-framework`, `materials-and-shaders`, `data-driven-design`):
  - Append the `## Bakırköy BR Core Constraints & Compliance` block into each `SKILL.md`.
  - Add specific references to `BRTypes.h`, `BRGameConstants.h`, and `AGENTS.md`.

### Phase 4: Automated Quality Gate
- Enhance `skills/scripts/validate_skills.py` to validate:
  1. YAML frontmatter completeness (`name`, `description`, `metadata`).
  2. Exact match between folder name and frontmatter `name`.
  3. No UTF-8 BOM encoding.
  4. Constraint compliance tags for core gameplay skills.
- Run validator as a pre-commit check for all agents.

### Phase 5: Master Index Catalog Generation
- Keep `.agents/skills/README.md` updated with the complete catalog of all 66+ skills grouped by domain, linking each skill to its corresponding Bakırköy BR module (`Weapons/`, `Building/`, `GameLoop/`, `AI/`, `Map/`).

---

## 7. Caveats
- No active network clones or file modifications were executed in this phase because this subagent operates under the Specification Miner read-only contract.
- The 15 UDS/UDW skills remain upstream on GitHub; they can be pulled on-demand if the team decides to integrate Ultra Dynamic Sky. The currently resident 66 skills already satisfy the 60+ skill requirement.
- The project root `C:\Users\silver\Desktop\bakirkoy-br` is not currently initialized as a git repository; therefore, versioning and validation rely on file system traversal and Python validation scripts.

---

## 8. Conclusion
Requirement R4 is thoroughly investigated and fully validated:
1. Both upstream repositories (`UnrealXu/UnrealEngine5-Skills` and `kevinpbuckley/unreal-engine-skills`) were explored via GitHub APIs and web intelligence, uncovering 73 total external skills (11 UnrealXu + 62 kevinpbuckley).
2. The local workspace `.agents/skills` already contains **66 active, valid `SKILL.md` skill modules** (11 UnrealXu + 47 kevinpbuckley core + 8 Teamwork role skills), achieving 100% frontmatter compliance.
3. Every core constraint of Bakırköy BR (No Interiors, Solo BR, Server-Authoritative, 3rd Person Camera, 3 Materials, Hybrid Hit Detection, `BR` Prefix) has been mapped to its affected skills with concrete adaptation requirements.
4. An actionable 5-phase plan is established to curate, adapt, and gate these skills throughout the project lifecycle.

---

## 9. Verification Method
1. **Count valid skills**:
   ```powershell
   (Get-ChildItem -Path "C:\Users\silver\Desktop\bakirkoy-br\.agents\skills" -Filter "SKILL.md" -Recurse).Count
   ```
   *Expected result*: `66`
2. **Validate frontmatters**:
   ```powershell
   python .\skills\scripts\validate_skills.py
   ```
   *Expected result*: `Validation OK`
3. **Verify core constraint adherence in building & weapons**:
   ```powershell
   Get-Content "C:\Users\silver\Desktop\bakirkoy-br\.agents\skills\worker-building-system\SKILL.md" | Select-String "Moloz"
   Get-Content "C:\Users\silver\Desktop\bakirkoy-br\.agents\skills\worker-weapons-combat\SKILL.md" | Select-String "Hit-Scan"
   ```
   *Expected result*: Matches showing Moloz/Tuğla/Çelik and Hit-Scan/Projectile hybrid specifications.
