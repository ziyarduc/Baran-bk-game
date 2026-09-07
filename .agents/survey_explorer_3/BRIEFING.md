# BRIEFING — 2026-09-06T18:50:00Z

## Mission
Survey requirements and technical architecture for R2: setup_character_anims.py (procedural placeholder characters and animations)

## 🔒 My Identity
- Archetype: teamwork_preview_explorer
- Roles: explorer, investigator, synthesizer
- Working directory: C:\Users\silver\Desktop\bakirkoy-br\.agents\survey_explorer_3\
- Original parent: 15e550de-0068-443d-aa0c-ecaadddc5dd4
- Milestone: survey

## 🔒 Key Constraints
- Read-only investigation — do NOT implement
- Zero stubs/mocks in design
- Valid UE5 Python API calls
- Adhere to 7 Core Constraints (C1 No Interior, C2 Solo BR, C3 Server Auth, C4 3rd Person, C5 3 Materials, C6 Hybrid Hit Detection, C7 BR Prefix)
- Adhere to MVP Directives (M1 10 Bots, M2 Dual Weapons, M3 2 GameModes, M4 Building Paused, M5 Exterior Vertical Nav)
- Headless / Offline environment: Unreal Engine 5 is not installed, all scripts must be verifiable via static analysis (py_compile) and include dual-mode execution (real UE5 Python API + standalone dry-run simulation)

## Current Parent
- Conversation ID: 15e550de-0068-443d-aa0c-ecaadddc5dd4
- Updated: not yet

## Investigation State
- **Explored paths**:
  - `C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md` (authoritative task and constraints)
  - `C:\Users\silver\Desktop\bakirkoy-br\setup_blueprints.py` (existing BP generation script and patterns)
  - `C:\Users\silver\Desktop\bakirkoy-br\generate_map.py` (mock environment pattern and level verification)
  - `BakirkoyBR/Source/BakirkoyBR/Character/BRCharacter.h` & `.cpp` (C++ character base, movement, ADS, weapon slots)
  - `BakirkoyBR/Source/BakirkoyBR/AI/BRAIBotCharacter.h` & `.cpp` (C++ AI bot character, cover crouch, 10-bot MVP)
  - `BakirkoyBR/Source/BakirkoyBR/Data/BRTypes.h` (EBRMovementState, weapon types, damage structs)
  - `.agents/skills/animation-system/` (AnimInstance, state machines, montages, layered bone blend)
  - `.agents/skills/editor-scripting-and-python/` (Python API, subsystems, transactions, property access)
  - `.agents/skills/materials-and-shaders/` (Material graph, expressions, Material Instances MIC/MID)
  - `.agents/rules/` (naming-conventions, ue5-coding-standards, constraint-retention)
- **Key findings**:
  - `BP_BRCharacter` and `BP_BRAIBotCharacter` are already created by `setup_blueprints.py` but have empty/default skeletal meshes, materials, and anim instances.
  - `ABRCharacter` exposes `bIsADS`, `CurrentMovementState`, `ActiveWeaponSlot`, and movement component properties (`Velocity`, `IsFalling()`) perfectly suited for AnimBP driving.
  - UE5 Python API allows robust skeletal mesh configuration via CDO (`cdo.get_editor_property("mesh")`), setting `skeletal_mesh_asset`, `relative_location` (0, 0, -90), and `relative_rotation` (0, -90, 0).
  - Material creation in UE5 Python is fully supported via `unreal.MaterialFactoryNew`, `unreal.MaterialEditingLibrary`, and `unreal.MaterialInstanceConstantFactoryNew` creating `M_BRFacelessPlaceholder` with `MI_BRFacelessManny` and `MI_BRFacelessBot`.
  - AnimBP creation / referencing strategy: Two-tier approach (Tier 1 duplicates existing template `ABP_Manny` to `ABP_BRCharacter`; Tier 2 procedurally scaffolds `ABP_BRCharacter` targeting `SK_Mannequin` via `unreal.AnimBlueprintFactory`).
  - Wire AnimBP to Character CDO via `mesh_comp.set_editor_property("anim_class", abp.generated_class())` and `animation_mode = ANIMATION_BLUEPRINT`.
- **Unexplored areas**: None for R2 survey.

## Key Decisions Made
- Architected `setup_character_anims.py` with dual-mode capability: real UE5 Python API when inside Unreal Editor/Commandlet, and comprehensive dry-run simulation when run offline.
- Selected `M_BRFacelessPlaceholder` with `MI_BRFacelessManny` (neutral dark charcoal gray) for player and `MI_BRFacelessBot` (tactical orange/red accent) for AI bots to provide immediate visual identification for the 10-bot test scenario.
- Established two-tier AnimBP resolution to ensure robustness whether template assets are pre-installed or procedural.

## Artifact Index
- C:\Users\silver\Desktop\bakirkoy-br\.agents\survey_explorer_3\DISPATCH.md — Task assignment log
- C:\Users\silver\Desktop\bakirkoy-br\.agents\survey_explorer_3\progress.md — Progress heartbeat
- C:\Users\silver\Desktop\bakirkoy-br\.agents\survey_explorer_3\BRIEFING.md — Situational awareness index
- C:\Users\silver\Desktop\bakirkoy-br\.agents\survey_explorer_3\handoff.md — Final handoff report
