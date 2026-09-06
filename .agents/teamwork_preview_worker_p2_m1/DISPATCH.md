## 2026-09-06T16:14:44Z
You are Worker P2-M1.
Working Directory: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_p2_m1\
Project Root: C:\Users\silver\Desktop\bakirkoy-br\
Target File (Exclusive Write Ownership): C:\Users\silver\Desktop\bakirkoy-br\generate_map.py
Authoritative Request: C:\Users\silver\Desktop\bakirkoy-br\ORIGINAL_REQUEST.md
Scope Document: C:\Users\silver\Desktop\bakirkoy-br\.agents\PROJECT.md
Survey Specification: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_explorer_survey_p2_1\analysis.md
Survey Handoff: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_explorer_survey_p2_1\handoff.md

## CRITICAL DIRECTIVES
- Unreal Engine 5 is NOT installed on this machine. Execution requirements for UnrealEditor-Cmd.exe are explicitly WAIVED. DO NOT attempt to run UnrealEditor-Cmd.exe.
- Static Verification Required: You MUST run and verify `python -m py_compile generate_map.py` and inspect its AST.

## MANDATORY INTEGRITY WARNING
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Mission
Author the genuine, production-grade UE5 Python script `C:\Users\silver\Desktop\bakirkoy-br\generate_map.py` according to the survey specification in `teamwork_preview_explorer_survey_p2_1\analysis.md`.

Requirements:
1. Creates new level at `/Game/Maps/BakirkoyMap` (with directory creation if needed).
2. Spawns 200m x 200m walkable floor mesh at Z=-50 with `BlockAll` collision.
3. Spawns 4 perimeter boundary walls enclosing the 200m x 200m arena.
4. Spawns 4 solid exterior buildings with rooftop ramps/stairs and street cover barriers (constraint C1: No interiors).
5. Spawns EXACTLY 1 `unreal.NavMeshBoundsVolume` covering the entire playable volume (ground, ramps, rooftops).
6. Spawns Loot Spawners (StaticMeshActor crates tagged `"Loot"` and `"WeaponPickup"` in open exterior locations per BRAIController logic).
7. Spawns EXACTLY 10 `unreal.PlayerStart` actors in a 75m perimeter circle at elevation Z=100 facing center.
8. Persists the level asset as `.umap` via `LevelEditorSubsystem` and `EditorAssetSubsystem`.
9. Includes safe import wrapper (`try: import unreal except ImportError: unreal = None`) with standalone CLI entrypoint for test/dry-run execution.
10. Statically verify `python -m py_compile generate_map.py` and verify zero errors.
