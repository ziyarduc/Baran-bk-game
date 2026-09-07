# Dispatch: Challenger 1 (Adversarial Empirical Verifier)

**Assigned Directory**: `C:\Users\silver\Desktop\bakirkoy-br\.agents\challenger_1\`
**Task**: Adversarial test execution against `fetch_osm_data.py`, `build_osm_level.py`, and `setup_character_anims.py`. Test corner cases, corrupt inputs, edge coordinates, missing attributes, and invariant enforcement.

## 2026-09-06T18:59:54Z
You are Challenger 1 (teamwork_preview_challenger).
Your assigned working directory is: C:\Users\silver\Desktop\bakirkoy-br\.agents\challenger_1\
The authoritative user request is at: C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md
The project scope is at: C:\Users\silver\Desktop\bakirkoy-br\.agents\orchestrator_4\SCOPE.md
The project root is: C:\Users\silver\Desktop\bakirkoy-br

Your task:
Adversarially stress-test and empirically verify the Phase 4 implementations:
1. `fetch_osm_data.py`:
   - Test with nonexistent / corrupt cache files.
   - Test offline seed generation (`--offline-seed`).
   - Test invalid modes and CLI arguments.
   - Validate JSON output format, numeric types, non-empty bounds.
2. `build_osm_level.py`:
   - Test with missing GIS data file (verify authentic embedded fallback).
   - Test with malformed JSON (missing buildings / missing roads).
   - Test with degenerate polygons (collinear points, 2 points, zero area).
   - Verify invariant counts: exactly 1 NavMeshBoundsVolume, exactly 10 PlayerStarts, >=10 Loot spawners.
3. `setup_character_anims.py`:
   - Test execution with various flags (`--dry-run`, `--verbose`).
   - Verify material parameters and CDO transform invariants `(0, 0, -90)` / `(0, -90, 0)`.

Write a test harness script in your working directory to run all these tests.
Record full results in `C:\Users\silver\Desktop\bakirkoy-br\.agents\challenger_1\handoff.md`.
Conclude with verdict: `APPROVE` or `REQUEST_CHANGES`.
Once done, send a message to orchestrator with your verdict and handoff path.
