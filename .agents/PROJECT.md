# Project: Bakırköy BR — MCPs and Skills Integration

## Architecture
The Bakırköy BR project integrates Unreal Engine 5 with intelligent multi-agent tooling, error-prevention guards, and domain knowledge skills:

1. **Editor Automation Track (R3 & R1 Tier 1/2)**:
   - **UE5-MCP (`mcp-servers/unrealengine`)**: TypeScript/Node MCP server communicating over TCP (command execution port `6776`) and UDP (discovery port `6766`) using `unreal-remote-execution` and `@modelcontextprotocol/sdk`. Exposes `execute_python`, `spawn_actor`, `capture_viewport`, and `ping_editor`.
   - **UE5 Python Remote Execution Engine Settings**: Enabled via `BakirkoyBR.uproject` (`PythonScriptPlugin`, `EditorScriptingUtilities`) and `Config/DefaultEngine.ini` (`bRemoteExecution=True`, `RemoteExecutionCommandEndpoint="127.0.0.1:6776"`).
   - **Claireon Editor Automation (Tier 2)**: Native C++ in-editor HTTP MCP server and Python proxy for deep asset, Blueprint graph, UMG, and StateTree inspection (`mcp-servers/CLAIREON_INTEGRATION.md`).

2. **Error-Prevention & Cognitive Integrity Track (R1)**:
   - **`unreal-analyzer-mcp`**: AST-based C++ static inspection verifying Unreal reflection macros (`UPROPERTY`, `UFUNCTION`), `#include "Class.generated.h"` ordering, `TObjectPtr` GC safety, and RPC replication conventions (`.agents/rules/unreal-analyzer-validation.md`).
   - **`sequential-thinking`**: Mandatory 5-stage reasoning protocol for agents before any code generation or architecture modification (`.agents/rules/sequential-thinking.md`).
   - **`memory-mcp-server`**: Persistent entity-relation knowledge graph storing project constraints, weapon prototypes, and agent role contracts.
   - **`.agents/rules/`**: Comprehensive rule suite governing coding standards, constraint retention (`constraint-retention.md`), error prevention (`error-prevention.md`), rate-limit resilience (`rate-limit-resilience.md`), token optimization (`token-optimization.md`), and naming conventions.
   - **Automated Validation**: `scripts/verify-rules.ps1` enforcing 117 assertions across 5 suites (100% pass).

3. **Domain Knowledge Skills Track (R4)**:
   - 66 curated and validated skills under `.agents/skills/` derived from `UnrealXu/UnrealEngine5-Skills` (11), `kevinpbuckley/unreal-engine-skills` (47), and agent roles (8).
   - Master catalog: `.agents/skills/SKILLS_CATALOG.md` (817 lines, 19 categories).
   - Core constraints adaptation across all skills (No Interiors, Solo BR, Server-Authoritative, 3rd Person Camera, 3 Materials, Hybrid Hit Detection, `BR` Prefix, 10-Bot Scenario, 2 Weapon Prototypes, 2 GameModes).
   - Automated Validation: `.agents/skills/scripts/validate_all_skills.py` (66/66 passed, 100% compliance).

4. **Playable Demo MVP Vertical Slice**:
   - 10-bot test scenario in GameMode and AI Controller.
   - Combat & Looting prioritized: 2 weapon prototypes (1 AR Hit-Scan + 1 Rocket Launcher Projectile with splash damage).
   - Level design: Narrow urban streets, alleys, rooftops, exterior-only stairs/fire escapes, street-to-rooftop NavMesh.
   - Natural environment cover (vehicles, alleys, walls); Building system development paused for Demo 1.
   - Two distinct GameModes: Free-For-All (FFA / Deathmatch) & Classic Battle Royale (Last Man Standing + shrinking storm).

---

## Feature Inventory
| # | Feature | Description | Milestone | Source | Status |
|---|---------|-------------|-----------|--------|--------|
| 1 | UE5 Python Remote Config | Enable PythonScriptPlugin and EditorScriptingUtilities in `BakirkoyBR.uproject` and `DefaultEngine.ini` (port 6776) | M1 | Survey Explorer 1 | DONE |
| 2 | UE5-MCP Node/TS Server | Build `mcp-servers/unrealengine/build/index.js` using `unreal-remote-execution` and `@modelcontextprotocol/sdk` | M1 | Survey Explorer 1 | DONE |
| 3 | UE5-MCP Core Tools | Expose and verify `execute_python`, `spawn_actor`, `capture_viewport`, and `ping_editor` | M1 | Survey Explorer 1 | DONE |
| 4 | UE5 TCP Connection Verification | Script to verify TCP connection to port 6776 and test remote execution ping (`scripts/test_ue5_mcp_connection.js`) | M1 | Survey Explorer 1 | DONE |
| 5 | Claireon Automation Docs | Documentation and roadmap for Claireon in-editor HTTP MCP automation (`mcp-servers/CLAIREON_INTEGRATION.md`) | M1 | Survey Explorer 1 | DONE |
| 6 | Error-Prevention Rules | Implement `.agents/rules/error-prevention.md` for C++ reflection, GC safety, and include ordering | M2 | Survey Explorer 3 | DONE |
| 7 | Constraint-Retention Rules | Implement `.agents/rules/constraint-retention.md` enforcing the 7 core project constraints + 5 MVP directives | M2 | Survey Explorer 3 | DONE |
| 8 | Sequential-Thinking Protocol | Implement `.agents/rules/sequential-thinking.md` defining mandatory 5-stage thinking workflow | M2 | Survey Explorer 3 | DONE |
| 9 | Unreal-Analyzer Validation Rules | Implement `.agents/rules/unreal-analyzer-validation.md` for AST reflection rules | M2 | Survey Explorer 3 | DONE |
| 10 | Memory MCP Knowledge Graph Seeding | Verify and maintain project constraints and agent roles in memory graph | M2 | Survey Explorer 3 | DONE |
| 11 | Rules Verification Script | Automated script (`verify-rules.ps1`) executing 117 assertions with 100% pass rate | M2 | Survey Explorer 3 | DONE |
| 12 | Skills Cataloging | Audit and catalog all 66 skills in `.agents/skills/SKILLS_CATALOG.md` | M3 | Survey Spec Miner 2 | DONE |
| 13 | Skills Constraint Adaptation | Inject Bakırköy BR core constraints and MVP directives into all 66 skills | M3 | Survey Spec Miner 2 | DONE |
| 14 | Skills Frontmatter Validation | Ensure 100% YAML frontmatter compliance via `validate_all_skills.py` | M3 | Survey Spec Miner 2 | DONE |
| 15 | Rate Limit Resilience Protocol | State checkpointing manager (`scripts/checkpoint-manager.ps1`) and protocol (`rate-limit-resilience.md`) | M2 | User Directive | DONE |
| 16 | Token Optimization Protocol | JIT skill loading and context compression (`scripts/compress_context.py`, `token-optimization.md`) | M2 | User Directive | DONE |
| 17 | Playable Demo MVP Architecture | Formalize specifications for 10-bot scenario, 2 weapon prototypes, 2 GameModes, natural cover | M4 | User Directive / Survey | DONE |
| 18 | E2E Integration Acceptance | Full system acceptance check against all user criteria and Forensic Audit verification | M5 | Acceptance Criteria | DONE |
| 19 | Automated Map & Environment Gen | UE5 Python level gen (`generate_map.py`), floor, exterior walls, 1 NavMeshBoundsVolume, loot spawners, 10 PlayerStarts, save .umap | M-UE5-1 | Survey Explorer P2-1 | DONE |
| 20 | Automated Blueprint & UI Setup | UE5 Python setup (`setup_blueprints.py`) creating Blueprints for GameModes, Character, HUD, and scaffolding WBP_KillFeed | M-UE5-2 | Spec Miner Survey P2-2 | DONE |
| 21 | Project Packaging Pipeline | Windows packaging pipeline (`package_game.ps1`) using RunUAT BuildCookRun, engine detection, static AST validation | M-UE5-3 | Survey Explorer P2-3 | DONE |
| 22 | OSM Overpass Querying & Projection | Fetch OSM data for Bakırköy via Overpass API with failover, WGS84 to UE projection, height synthesis (`fetch_osm_data.py`) | M-OSM-1 | Survey Explorer 1 | IN_PROGRESS |
| 23 | UE5 Procedural GIS Level Gen | UE5 Python level gen (`build_osm_level.py`) with solid OBB buildings, roads, floor, lighting, NavMeshBounds, PlayerStarts | M-OSM-2 | Survey Explorer 2 | PLANNED |
| 24 | Character Mesh & Anim Pipeline | Assign SKM_Manny to BP_BRCharacter, generate faceless PBR materials, wire ABP_BRCharacter AnimBP (`setup_character_anims.py`) | M-CHAR-1 | Survey Explorer 3 | IN_PROGRESS |
| 25 | Phase 4 Multi-Agent Verification | Multi-agent Review, Adversarial Challenge, and Forensic Integrity Audit Gate for Phase 4 deliverables | M-VERIFY | Survey Explorers 1-3 | PLANNED |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | UE5-MCP Editor Automation (R3) | Implement `mcp-servers/unrealengine`, configure `BakirkoyBR.uproject` & `DefaultEngine.ini` (port 6776), verify build | None | DONE |
| M2 | Error-Prevention & Constraints (R1) | Implement rules in `.agents/rules/` (`error-prevention.md`, `constraint-retention.md`, `sequential-thinking.md`, `unreal-analyzer-validation.md`, `rate-limit-resilience.md`, `token-optimization.md`), verify memory graph & linting (117 tests) | None | DONE |
| M3 | UE5 Domain Knowledge Skills (R4) | Validate and adapt 66 skills in `.agents/skills/`, inject Bakırköy BR constraints, generate `SKILLS_CATALOG.md` | None | DONE |
| M4 | Playable Demo MVP Implementation | C++ gameplay vertical slice: 2 weapon prototypes (`BRWeaponBase`, `BRWeapon_HitScan`, `BRWeapon_Projectile`, `BRProjectileRocket`), 10-bot AI (`BRAIController`, `BRAIBotCharacter`), 2 GameModes (`BRGameMode_FFA`, `BRGameMode_BattleRoyale`, `BRStormCircle`), paused building, exterior NavMesh | M1, M2, M3 | DONE |
| M5 | Verification & Acceptance Gate | 3-gate multi-agent verification: 207-check automated AST suite, 35-check adversarial challenger test, unanimous APPROVE/CLEAN verdicts | M1, M2, M3, M4 | DONE |
| M-UE5-1 | Automated Map Generation (`generate_map.py`) | Implement `generate_map.py` with level creation, 200mx200m floor, exterior walls/ramps, 1 NavMeshBoundsVolume, 10 PlayerStarts, loot spawners, .umap save | M1-M5 | DONE |
| M-UE5-2 | Automated Blueprint & UI Setup (`setup_blueprints.py`) | Implement `setup_blueprints.py` creating BP_BRGameMode, BP_BRCharacter, BP_BRHUD, and scaffolding WBP_KillFeed | M1-M5 | DONE |
| M-UE5-3 | Project Packaging Pipeline (`package_game.ps1`) | Implement `package_game.ps1` with RunUAT BuildCookRun, engine discovery, parameter handling, static AST verification | M1-M5 | DONE |
| M-UE5-4 | Multi-Agent Review & Forensic Audit Gate | Reviewers, Challengers, and Forensic Auditor verification and integrity gate | M-UE5-1..3 | DONE |
| M-OSM-1 | OSM Data Acquisition Pipeline (`fetch_osm_data.py`) | Implement `fetch_osm_data.py` with Overpass query, failover, projection, height synthesis, cache, seed | None | IN_PROGRESS |
| M-OSM-2 | UE5 GIS Procedural Level Generator (`build_osm_level.py`) | Implement `build_osm_level.py` with OBB buildings, roads, floor, lighting, NavMeshBounds, PlayerStarts, dry-run | M-OSM-1 | PLANNED |
| M-CHAR-1 | Procedural Character & Anim Setup (`setup_character_anims.py`) | Implement `setup_character_anims.py` with SKM_Manny, faceless materials, AnimBP, CDO wiring, dry-run | None | IN_PROGRESS |
| M-VERIFY | Phase 4 Multi-Agent Gate & Audit | Reviewers, Challengers, and Forensic Auditor verification and integrity gate | M-OSM-1, M-OSM-2, M-CHAR-1 | PLANNED |

---

## Interface Contracts
### Agent Tooling ↔ UE5 Editor
- Protocol: TCP port 6776 (Command execution), UDP port 6766 (Multicast discovery)
- Messages: JSON-RPC over TCP socket (`magic: 'ue_py'`)
- Commands:
  * `execute_python(code: string)`: Executes Python in UE5 editor, returns `{ success: boolean, output: string, error?: string }`
  * `spawn_actor(asset_path: string, location: [number, number, number], rotation?: [number, number, number])`: Spawns actor in active world
  * `capture_viewport(output_path?: string)`: Captures active editor viewport screenshot
  * `ping_editor(timeout_ms?: number)`: Pings port 6776 connection

### Agents ↔ Error-Prevention & Rules
- Rules Directory: `.agents/rules/*.md`
- Sequential Thinking: 5 stages (Constraint Scan, Module Ownership, UE5 Reflection/Memory Safety, Network Authority, Verification Hypothesis)
- Memory Graph: Stores active constraints (No Interior, Solo Only, Server Authoritative, 3rd Person, 3 Materials, Hybrid Hit Detection, BR Prefix, 10 Bots MVP, 2 Weapon Prototypes, 2 GameModes, Paused Building)
- Automated Verification: `scripts/verify-rules.ps1` (207 assertions)

---

## Code Layout
```
C:\Users\silver\Desktop\bakirkoy-br\
├── fetch_osm_data.py               # Phase 4 R1: OSM Overpass data pipeline
├── build_osm_level.py              # Phase 4 R1: UE5 procedural GIS city level generator
├── setup_character_anims.py        # Phase 4 R2: Procedural placeholder character & AnimBP setup
├── generate_map.py                 # R1: Automated map & environment generation
├── setup_blueprints.py             # R2: Automated Blueprint & UI scaffolding
├── package_game.ps1                # R3: Windows packaging pipeline
├── BakirkoyBR.uproject             # UE5 project descriptor (enabled plugins)
├── Config\
│   └── DefaultEngine.ini           # Python remote execution settings (port 6776)
├── Source\BakirkoyBR\ (or BakirkoyBR\Source\BakirkoyBR\)
│   ├── Weapons\                    # Combat & Looting vertical slice
│   │   ├── BRWeaponBase.h / .cpp   # Server-authoritative replicated weapon base
│   │   ├── BRWeapon_HitScan.h / .cpp # Assault Rifle prototype (Hit-Scan, falloff, 2x headshot)
│   │   ├── BRWeapon_Projectile.h / .cpp # Rocket Launcher prototype (Projectile movement)
│   │   └── BRProjectileRocket.h / .cpp # Physical rocket actor with radial splash damage
│   ├── AI\                         # 10-Bot AI Subsystem
│   │   ├── BRAIController.h / .cpp # 10-bot cap, 5-state FSM, exterior ceiling raycast, natural cover
│   │   └── BRAIBotCharacter.h / .cpp # Health component, server fire, ragdoll elimination
│   ├── GameModes\                  # Dual GameModes
│   │   ├── BRGameMode_FFA.h / .cpp # 25-kill limit, 600s timer, safest exterior respawn
│   │   └── BRGameMode_BattleRoyale.h / .cpp # Solo BR (10 bots + 1 player), permadeath, LMS
│   └── Storm\                      # Storm Circle Subsystem
│       └── BRStormCircle.h / .cpp  # 7-phase shrinking storm circle with safe zone damage ticks
├── mcp-servers\
│   ├── unrealengine\
│   │   ├── package.json            # Node/TS dependencies (@modelcontextprotocol/sdk, unreal-remote-execution)
│   │   ├── tsconfig.json           # TypeScript configuration
│   │   ├── src\
│   │   │   ├── index.ts            # MCP server entrypoint
│   │   │   └── unreal-client.ts    # TCP remote execution client
│   │   └── build\
│   │       └── index.js            # Compiled MCP server artifact (verified)
│   └── CLAIREON_INTEGRATION.md     # Claireon automation architecture roadmap
├── scripts\
│   ├── test_ue5_mcp_connection.js  # TCP socket & tool schema verification test
│   ├── verify-rules.ps1            # 207-check rules & AST verification engine
│   ├── test_adversarial_challenger_mvp.ps1 # 35-check adversarial verification harness
│   ├── checkpoint-manager.ps1      # Rate limit state checkpoint manager
│   └── compress_context.py         # Context compression utility
├── .agents\
│   ├── ORIGINAL_REQUEST.md         # Immutable original user requests
│   ├── AGENTS.md                   # Global agent rules and constraints
│   ├── PROJECT.md                  # Project index & architecture (this file)
│   ├── CHECKPOINT.json             # Persistent state checkpoint
│   ├── GATE_STATUS.md              # Gate verdicts and audit tracking
│   ├── rules\
│   │   ├── error-prevention.md     # C++ anti-patterns & reflection safety
│   │   ├── constraint-retention.md # 7 Core constraints + 5 MVP directives
│   │   ├── sequential-thinking.md  # 5-stage sequential reasoning protocol
│   │   ├── unreal-analyzer-validation.md # AST analysis standards
│   │   ├── rate-limit-resilience.md# Quota resilience & continue protocol
│   │   ├── token-optimization.md   # JIT loading & compression
│   │   ├── ue5-coding-standards.md
│   │   └── naming-conventions.md
│   └── skills\                     # 66 adapted UE5 domain skills
│       ├── SKILLS_CATALOG.md       # Master skills catalog (817 lines, 19 categories)
│       ├── scripts\
│       │   ├── validate_all_skills.py # 66-skill validation suite (100% compliant)
│       │   └── validate_skills.py     # Upstream validator
│       ├── ue5-*\                  # UnrealXu skills (11)
│       ├── *\                      # kevinpbuckley core skills (47)
│       └── worker-*\               # Role-specific skills (8)
```

