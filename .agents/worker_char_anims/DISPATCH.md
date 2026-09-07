## 2026-09-06T18:52:00Z
You are Worker 2 (teamwork_preview_worker).
Your assigned working directory is: C:\Users\silver\Desktop\bakirkoy-br\.agents\worker_char_anims\
The authoritative user request is at: C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md
The project scope is at: C:\Users\silver\Desktop\bakirkoy-br\.agents\orchestrator_4\SCOPE.md
The technical survey report is at: C:\Users\silver\Desktop\bakirkoy-br\.agents\survey_explorer_3\handoff.md
The project root is: C:\Users\silver\Desktop\bakirkoy-br

Your exclusive write ownership:
- `C:\Users\silver\Desktop\bakirkoy-br\setup_character_anims.py`

Task:
Implement `setup_character_anims.py` for requirement R2:
1. Read C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md, SCOPE.md, and survey_explorer_3/handoff.md.
2. Author a production-grade, robust UE5 Python script `setup_character_anims.py`:
   - Dual-mode architecture: Safe `import unreal` wrapper with complete standalone dry-run simulation framework (`_MockUnrealModule`, `_MockVector`, `_MockRotator`, `_MockLinearColor`, `_MockSkeletalMeshComponent`, etc.) so the script runs and verifies 100% cleanly both in live UE5 and standalone without UE5 installed.
   - Assigns default UE5 Manny/Quinn skeletal mesh (`SKM_Manny`, `/Game/Characters/Mannequins/Meshes/SKM_Manny`) to `BP_BRCharacter` and `BP_BRAIBotCharacter` CDOs with correct relative transform alignment (`location = (0.0, 0.0, -90.0)`, `rotation = (0.0, -90.0, 0.0)`).
   - Procedurally creates/configures master faceless PBR material `M_BRFacelessPlaceholder` (`/Game/Materials/M_BRFacelessPlaceholder`) with BaseColor, Roughness 0.6, Metallic 0.0, and creates Material Instances `MI_BRFacelessManny` (charcoal studio gray `0.20, 0.20, 0.22`) for player and `MI_BRFacelessBot` (tactical orange-red `0.70, 0.25, 0.15`) for AI bots per MVP directive.
   - Sets up `ABP_BRCharacter` Animation Blueprint (`/Game/Characters/Mannequins/Animations/ABP_BRCharacter`) with two-tier resolution (template duplicate or AnimBlueprintFactory), supporting core locomotion states (Idle, Run), Jump (Start, Loop, Land), and Aim (UpperBody slot), wired to `ABRCharacter` properties (`Speed`, `bIsFalling`, `bIsADS`, `CurrentMovementState`).
   - Wires `mesh.animation_mode = ANIMATION_BLUEPRINT` and `mesh.anim_class = ABP_BRCharacter_C` on the character Blueprint CDO, compiles Blueprint, and saves assets.
   - CLI flags: `--dry-run`, `--verbose`.
3. Run verification:
   - `python -m py_compile setup_character_anims.py`
   - `python setup_character_anims.py --dry-run --verbose`
4. Record your results and write your compact handoff report to `C:\Users\silver\Desktop\bakirkoy-br\.agents\worker_char_anims\handoff.md` following the compact 4-part schema:
```markdown
## Handoff: [TaskID]
- **Verdict**: [DONE | BLOCKED]
- **Modified Files**: [list of paths]
- **Verification**: [Test command + exit code + summary]
- **Next Action**: [Single sentence instruction]
```
