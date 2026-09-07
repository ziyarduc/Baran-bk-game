# Dispatch: Challenger 2 (Stress Test & Invariant Validator)

**Assigned Directory**: `C:\Users\silver\Desktop\bakirkoy-br\.agents\challenger_2\`
**Task**: Stress testing data pipelines, geometry edge cases (zero area polygons, collinear points, extreme building heights, invalid roads), and validating all acceptance criteria.

## 2026-09-06T18:59:54Z
You are Challenger 2 (teamwork_preview_challenger).
Your assigned working directory is: C:\Users\silver\Desktop\bakirkoy-br\.agents\challenger_2\
The authoritative user request is at: C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md
The project scope is at: C:\Users\silver\Desktop\bakirkoy-br\.agents\orchestrator_4\SCOPE.md
The project root is: C:\Users\silver\Desktop\bakirkoy-br

Your task:
Independently design and execute an empirical stress test suite across all Phase 4 code:
- Check cross-script data flow: Does `fetch_osm_data.py` output feed seamlessly into `build_osm_level.py`?
- Verify scale: Test that 1 UU = 1 cm, building heights are realistic (meters to cm), road widths match real-world lane widths.
- Verify Rule C1 ("No Interior"): Confirm all spawned buildings are solid exterior blocks with simple box collision and zero hollow cavities.
- Verify 10-Bot scenario integration: Confirm `MI_BRFacelessBot` distinction and `BP_BRAIBotCharacter` configuration in `setup_character_anims.py`.
- Execute tests, document results, and write your handoff report to `C:\Users\silver\Desktop\bakirkoy-br\.agents\challenger_2\handoff.md`.
Conclude with verdict: `APPROVE` or `REQUEST_CHANGES`.
Once done, send a message to orchestrator with your verdict and handoff path.
