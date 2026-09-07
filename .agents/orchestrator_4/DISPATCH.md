## 2026-09-06T18:46:13Z
You are the Project Orchestrator for Phase 4 of the Bakirkoy BR project.
Your assigned working directory is C:\Users\silver\Desktop\bakirkoy-br\.agents\orchestrator_4.
The project root directory is C:\Users\silver\Desktop\bakirkoy-br.
The authoritative record of user requests is located at C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md.

Task Objective:
Execute Bakirkoy BR Project Phase 4: Generate a 1:1 scale replica of Bakirkoy using OpenStreetMap (OSM) data and set up procedural placeholder character models with animations.

Requirements:
1. R1. 1:1 Bakirkoy Map Generation via OpenStreetMap:
   - Python automation pipeline (`fetch_osm_data.py`) using `requests` or `osmnx` to query the Overpass API for topological data (streets and building footprints/heights/tags) of Bakirkoy, Istanbul.
   - UE5 Python script (`build_osm_level.py`) that reads this GIS data to procedurally generate the 1:1 city level in Unreal Engine. Streets should be laid out, and buildings should be extruded as solid exterior blocks matching real-world footprints.
2. R2. Procedural Placeholder Characters & Animations:
   - Procedural animation pipeline using UE5's default Skeletal Meshes (Manny/Quinn) or Control Rig. Characters should have placeholder, faceless materials (gray or solid colors).
   - UE5 Python script (`setup_character_anims.py`) that assigns a faceless material and a basic Animation Blueprint (AnimBP with idle, run, jump, aim) to `BP_BRCharacter` and integrates with `ABRCharacter`.
3. Acceptance Criteria & Guardrails:
   - `fetch_osm_data.py` exists, successfully queries OSM/Overpass API without syntax errors, and handles parsing/caching cleanly.
   - `build_osm_level.py` exists and translates the fetched GIS data into UE5 actors/splines without runtime errors.
   - `setup_character_anims.py` exists and sets up the faceless material and basic AnimBP for `BP_BRCharacter`.
   - Static analysis (e.g. `python -m py_compile`, AST inspection) confirms all Python files are syntactically valid.
   - UE5 Environment Note: Unreal Engine 5 is not installed locally on this machine; live execution of `UnrealEditor-Cmd.exe` is waived. Scripts must strictly adhere to the official UE5 Python API (`import unreal`), be robustly authored, syntactically validated, and reviewed across team specialists.
   - Integrity mode: benchmark. Zero mocks/stubs; provide fully implemented, robust code.
   - Model Directive: ALL worker agents transitioned to gemini-3.8-flash (High Thinking).
   - Checkpointing & Token Optimization: Update `.agents/CHECKPOINT.json` via `scripts/checkpoint-manager.ps1`. Enforce JIT skill loading and compact handoffs.
