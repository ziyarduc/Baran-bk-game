# Technical Architecture & Survey Report: Requirement R2 (`setup_character_anims.py`)
**Procedural Placeholder Characters and Animation Blueprint Integration**

**Agent**: Survey Explorer 3 (`teamwork_preview_explorer`)  
**Assigned Directory**: `C:\Users\silver\Desktop\bakirkoy-br\.agents\survey_explorer_3\`  
**Target Script**: `C:\Users\silver\Desktop\bakirkoy-br\setup_character_anims.py`  
**Date**: 2026-09-06  

---

## 1. Observation

### 1.1 Project Requirements & Operational Constraints
- **Authoritative Directives (`.agents/ORIGINAL_REQUEST.md`)**:
  - Phase 4, Requirement R2 (lines 158–170):
    > "Set up a procedural animation pipeline using UE5's default Skeletal Meshes (Manny/Quinn) or Control Rig. The characters should have placeholder, faceless materials (gray or solid colors). Write the necessary scripts or Blueprints to integrate these models and basic locomotion animations (run, jump, idle, aim) into the existing `ABRCharacter` class."
    > Acceptance Criteria:
    > "- [ ] A script or detailed blueprint setup (`setup_character_anims.py`) exists that assigns a faceless material and a basic Animation Blueprint (AnimBP) to `BP_BRCharacter`."
    > "- [ ] Static analysis (e.g., `python -m py_compile`) confirms all Python files are syntactically valid."
  - Critical Execution Constraint (lines 130–138):
    > "Unreal Engine 5 is NOT installed on this machine, and we cannot install it because it requires Epic Games account authentication and 100GB of disk space. Therefore, you must WAIVE the execution requirements in the Acceptance Criteria. DO NOT try to execute `UnrealEditor-Cmd.exe` or `RunUAT.bat`. Instead, your task is to successfully author and review the required scripts based purely on Unreal Engine 5 Python API documentation and best practices. Verify them using static analysis, syntax checking (e.g., `python -m py_compile`), and rigorous code review among your agents."
  - Project Invariants (`.agents/rules/constraint-retention.md` & `.agents/rules/naming-conventions.md`):
    * **C4 (3rd Person Only)**: Over-the-shoulder perspective; ADS zooms camera FOV and spring arm only, never switches to 1st person.
    * **C7 (Mandatory `BR` Prefix)**: Material `M_BRFacelessPlaceholder`, instances `MI_BRFacelessManny`, `MI_BRFacelessBot`, AnimBP `ABP_BRCharacter`, Blueprints `BP_BRCharacter`, `BP_BRAIBotCharacter`.
    * **M1 (10-Bot MVP)**: Distinct visual identification between player character (`BP_BRCharacter`) and bot character (`BP_BRAIBotCharacter`) is highly advantageous for vertical slice testing.

### 1.2 Existing Codebase Inspection
- **`BakirkoyBR/Source/BakirkoyBR/Character/BRCharacter.h` & `BRCharacter.cpp`**:
  - `ABRCharacter` inherits from `ACharacter` (`BRCharacter.h:20`).
  - Contains default subobject `USkeletalMeshComponent* Mesh` inherited from `ACharacter`.
  - Replicated combat & movement properties (`BRCharacter.h:64-72`):
    * `UPROPERTY(Replicated, BlueprintReadOnly, Category = "Movement") EBRMovementState CurrentMovementState = EBRMovementState::Idle;`
    * `UPROPERTY(Replicated, BlueprintReadOnly, Category = "Combat") bool bIsADS = false;`
    * `UPROPERTY(Replicated, BlueprintReadOnly, Category = "Combat") int32 ActiveWeaponSlot = 0;`
  - Inherited from `ACharacter::GetCharacterMovement()` (`UCharacterMovementComponent`):
    * `Velocity.Size2D()` (forward/lateral speed in cm/s).
    * `IsFalling()` (airborne state for jump/fall).
    * `IsCrouching()` (crouched stance).
- **`BakirkoyBR/Source/BakirkoyBR/AI/BRAIBotCharacter.h` & `BRAIBotCharacter.cpp`**:
  - Inherits from `ABRCharacter` (`BRAIBotCharacter.h:24`).
  - Contains `SetCoverCrouch(bool bShouldCrouch)` (`BRAIBotCharacter.h:43`).
- **`BakirkoyBR/Source/BakirkoyBR/Data/BRTypes.h`**:
  - `EBRMovementState` enum (`BRTypes.h:116-127`): `Idle`, `Walking`, `Sprinting`, `Crouching`, `Jumping`, `Falling`, `Gliding`, `Building`, `Downed`.
- **Existing Blueprint Automation (`setup_blueprints.py`)**:
  - `setup_blueprints.py` creates `BP_BRCharacter` and `BP_BRAIBotCharacter` under `/Game/Blueprints/` (lines 446–455), but does NOT assign skeletal meshes, materials, or animation blueprints.
  - Implements a robust dual-mode pattern: imports `unreal` within a `try/except` block, runs `run_dry_run_simulation()` when running standalone without Unreal Engine, and wraps mutations inside `unreal.ScopedEditorTransaction`.

---

## 2. Logic Chain

1. **Need for Dedicated Setup Script (`setup_character_anims.py`)**:
   - Observations 1.1 and 1.2 show that while `setup_blueprints.py` creates the class definitions for `BP_BRCharacter` and `BP_BRAIBotCharacter`, their component visual assets (SkeletalMesh, Materials) and runtime animation driver (`AnimBlueprint`) remain unset.
   - Requirement R2 explicitly requires `setup_character_anims.py` to bridge this gap, configuring default skeletal meshes (Manny/Quinn), faceless placeholder materials, and a core locomotion/aiming Animation Blueprint.

2. **Skeletal Mesh Resolution & Placement**:
   - In UE5, Manny and Quinn are standard skeletal meshes (`SKM_Manny`, `SKM_Quinn`) sharing skeleton `SK_Mannequin`.
   - Primary candidate package paths:
     1. `/Game/Characters/Mannequins/Meshes/SKM_Manny`
     2. `/Game/Characters/Mannequins/Meshes/SKM_Quinn`
     3. `/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple`
     4. `/Engine/EngineMeshes/SkeletalCube` (headless engine fallback)
   - To configure a Blueprint inheriting from `ACharacter` in UE5 Python:
     * Access the Class Default Object (CDO) via `cdo = unreal.get_default_object(bp_asset.generated_class())`.
     * Retrieve the inherited `USkeletalMeshComponent` via `mesh_comp = cdo.get_editor_property("mesh")`.
     * Set the mesh asset via `mesh_comp.set_editor_property("skeletal_mesh_asset", sk_mesh)` (with fallback to `"skeletal_mesh"` for UE 5.0 compatibility).
     * Set the standard alignment relative transform:
       - `relative_location = unreal.Vector(0.0, 0.0, -90.0)` (aligns mesh feet to capsule bottom).
       - `relative_rotation = unreal.Rotator(0.0, -90.0, 0.0)` (compensates for asset Y-forward to orient actor +X forward).
     * Set collision profile to `"CharacterMesh"`.

3. **Faceless Placeholder Material Generation Pipeline**:
   - Requirement R2 dictates placeholder, faceless materials (gray or solid colors).
   - In Unreal Engine 5, programmatically authoring a material via Python requires:
     * Factory: `unreal.MaterialFactoryNew()`
     * Library: `unreal.MaterialEditingLibrary`
     * Asset: `/Game/Materials/M_BRFacelessPlaceholder`
     * Nodes:
       1. `MaterialExpressionVectorParameter` named `"BaseColor"`, default `LinearColor(0.20, 0.20, 0.22, 1.0)` connected to `MP_BASE_COLOR`.
       2. `MaterialExpressionScalarParameter` named `"Roughness"`, default `0.60` connected to `MP_ROUGHNESS`.
       3. `MaterialExpressionScalarParameter` named `"Metallic"`, default `0.0` connected to `MP_METALLIC`.
     * Update & compile: `unreal.MaterialEditingLibrary.update_material(mat_asset)`.
   - Material Instances (MIC) for character identification:
     * `MI_BRFacelessManny`: Neutral dark charcoal gray (`0.20, 0.20, 0.22`) assigned to player `BP_BRCharacter`.
     * `MI_BRFacelessBot`: Tactical orange/red tinted charcoal (`0.70, 0.25, 0.15`) assigned to `BP_BRAIBotCharacter` to immediately distinguish enemy AI bots during the 10-bot MVP test scenario.
     * `MI_BRFacelessQuinn`: Slate gray (`0.28, 0.28, 0.32`).
     * Instanced via `unreal.MaterialInstanceConstantFactoryNew()` and `unreal.MaterialEditingLibrary.set_material_instance_parent()`.
   - Assignment:
     * Set on `mesh_comp.set_editor_property("override_materials", [mic_asset, ...])` and `mesh_comp.set_material(0, mic_asset)`.

4. **Animation Blueprint (`AnimBP`) Architecture & Resolution**:
   - An `AnimBlueprint` in UE5 requires a target skeleton (`SK_Mannequin`).
   - Strategy: Two-tier resolution:
     * **Tier 1 (Template Asset Duplication)**: If template `/Game/Characters/Mannequins/Animations/ABP_Manny` exists, duplicate it to `/Game/Characters/Mannequins/Animations/ABP_BRCharacter` via `unreal.EditorAssetLibrary.duplicate_asset`. This preserves the entire production-grade Manny state machine, jump sub-graphs, and blend spaces intact.
     * **Tier 2 (Procedural Creation)**: If `ABP_Manny` does not exist (clean project), create `ABP_BRCharacter` using `unreal.AnimBlueprintFactory` with `target_skeleton = sk_mannequin` and `parent_class = unreal.AnimInstance`.
   - Locomotion State Machine Specification:
     * `Locomotion`:
       - `Idle` state: Evaluates idle sequence (`MM_Idle` / `MF_Idle`).
       - `Run` state: Evaluates blendspace or run sequence (`BS_WalkRun` / `MM_Run_Fwd`).
       - Transitions: `Speed > 10.0` (Idle -> Run), `Speed <= 10.0` (Run -> Idle).
     * `Airborne` (Jump/Fall):
       - `JumpStart` -> `JumpLoop` / `Fall` -> `JumpLand`.
       - Transitions: `bIsFalling == true` (enters jump), automatic time remaining (start -> loop), `bIsFalling == false` (enters land).
     * `UpperBody` Layered Blend (`FAnimNode_LayeredBoneBlend`):
       - Branch filter root bone: `spine_01` (depth 1).
       - Slot node: `UpperBody` / `DefaultSlot`.
       - When `bIsADS == true` (or firing/reloading), plays upper body montage while lower body continues running/jumping.
   - Integration with `ABRCharacter`:
     * The AnimBP EventGraph accesses the owning pawn:
       - `TryGetPawnOwner()` -> Cast to `ABRCharacter`
       - `GetVelocity().Size2D()` -> `Speed` (float)
       - `GetCharacterMovement()->IsFalling()` -> `bIsFalling` (bool)
       - `ABRCharacter::bIsADS` -> `bIsAiming` (bool)
       - `ABRCharacter::CurrentMovementState` -> `MovementState` (enum)
   - Assigning to Character CDO:
     * `mesh_comp.set_editor_property("animation_mode", unreal.AnimationMode.ANIMATION_BLUEPRINT)`
     * `mesh_comp.set_editor_property("anim_class", abp_asset.generated_class())`
     * Compiled via `unreal.KismetEditorUtilities.compile_blueprint(bp_asset)` and saved via `unreal.EditorAssetLibrary.save_loaded_asset(bp_asset)`.

5. **Dual-Mode Execution & Headless Safety**:
   - Following Observation 1.1, Unreal Engine is not installed in the current environment.
   - The script must define mock constructs (`_MockLinearColor`, `_MockVector`, `_MockRotator`, `_MockSkeletalMeshComponent`, etc.) and a full simulation suite (`run_dry_run_simulation()`).
   - When executed with `python setup_character_anims.py`, it executes the complete simulation, validates all paths, invariants, and CDO mappings, and exits with code 0.
   - When compiled with `python -m py_compile setup_character_anims.py`, static syntax analysis verifies zero syntax errors.

---

## 3. Caveats

1. **UE5 Python AnimGraph Graph-Node Authoring Limits**:
   - In Unreal Engine, Python does not have a native reflection API to add arbitrary internal execution pins and nodes inside an `AnimGraph` state machine (unlike `MaterialEditingLibrary` for materials).
   - Therefore, the industry-standard methodology in UE5 Python pipelines is:
     * Primary: Duplicate and configure a parent or template AnimBP asset (`ABP_Manny`), which preserves the full graph node topology, state transitions, and sync groups.
     * Fallback: Create the `AnimBlueprint` asset via `AnimBlueprintFactory`, configure its Class Default Object, target skeleton, and assign it to the Character CDO.
2. **Template Asset Availability**:
   - In a vanilla UE5 source engine or fresh project without the "Third Person Template Content" imported, `/Game/Characters/Mannequins/` assets may not be present until imported. The script must handle fallback paths (such as `/Engine/EngineMeshes/SkeletalCube` or logging clean warnings) gracefully.
3. **Control Rig vs Standard AnimBP**:
   - Requirement R2 mentions "UE5's default Skeletal Meshes (Manny/Quinn) or Control Rig". Manny in UE5 includes a default Control Rig (`CR_Mannequin_BasicFootIK`), but for procedural locomotion and combat states, the Animation Blueprint (`AnimBP`) is the authoritative runtime driver in UE5. Foot IK Control Rig can be layered inside the AnimBP if present.

---

## 4. Conclusion & Recommended Architecture

The script `setup_character_anims.py` should be authored as a single, self-contained, production-grade Python script located at the project root (`C:\Users\silver\Desktop\bakirkoy-br\setup_character_anims.py`).

### 4.1 Architecture Specification

| Component | Target Asset Path | Class / Factory | Purpose / Settings |
|---|---|---|---|
| **Base Material** | `/Game/Materials/M_BRFacelessPlaceholder` | `UMaterial` via `MaterialFactoryNew` | Master faceless PBR material (`BaseColor`, `Roughness`, `Metallic`) |
| **Player Material Instance** | `/Game/Materials/MI_BRFacelessManny` | `UMaterialInstanceConstant` | Charcoal studio gray (`LinearColor(0.20, 0.20, 0.22, 1.0)`, Roughness 0.6) |
| **AI Bot Material Instance** | `/Game/Materials/MI_BRFacelessBot` | `UMaterialInstanceConstant` | Tactical orange-red tinted charcoal (`LinearColor(0.70, 0.25, 0.15, 1.0)`) for 10-bot identification |
| **Quinn Material Instance** | `/Game/Materials/MI_BRFacelessQuinn` | `UMaterialInstanceConstant` | Slate gray (`LinearColor(0.28, 0.28, 0.32, 1.0)`) |
| **Animation Blueprint** | `/Game/Characters/Mannequins/Animations/ABP_BRCharacter` | `UAnimBlueprint` via `AnimBlueprintFactory` (or duplicate `ABP_Manny`) | Core locomotion (Idle/Run), Jump states (Start/Loop/Land), UpperBody slot for ADS / firing |
| **Player Character BP** | `/Game/Blueprints/BP_BRCharacter` | Inherits `ABRCharacter` | Mesh: `SKM_Manny`, Material: `MI_BRFacelessManny`, AnimClass: `ABP_BRCharacter_C` |
| **Bot Character BP** | `/Game/Blueprints/BP_BRAIBotCharacter` | Inherits `ABRAIBotCharacter` | Mesh: `SKM_Manny` / `SKM_Quinn`, Material: `MI_BRFacelessBot`, AnimClass: `ABP_BRCharacter_C` |

### 4.2 Detailed Script Structure for `setup_character_anims.py`

```python
"""
setup_character_anims.py — Procedural Character & Animation Setup for Bakirkoy BR.

Configures default UE5 Manny/Quinn skeletal meshes, procedural faceless placeholder
materials (M_BRFacelessPlaceholder, MI_BRFacelessManny, MI_BRFacelessBot), and a
comprehensive Animation Blueprint (ABP_BRCharacter) supporting locomotion, jumping,
and upper-body aiming, wired directly into BP_BRCharacter and BP_BRAIBotCharacter CDOs.

Target Engine: Unreal Engine 5.4 - 5.8 (Python Script Plugin)
Project: Bakırköy BR
"""

# 1. Imports & Safe Unreal Module Wrapper
# 2. Standalone Simulation Mocks (_MockVector, _MockRotator, _MockLinearColor, _MockSkeletalMeshComponent, etc.)
# 3. Helper Functions:
#    - resolve_asset(primary_path, fallback_paths)
#    - get_or_create_material(asset_name, package_path)
#    - create_material_instance(instance_name, package_path, parent_mat, params)
#    - get_or_create_anim_blueprint(asset_name, package_path, skeleton_asset, template_anim_bp)
#    - configure_character_blueprint(bp_path, mesh_asset, material_asset, anim_bp_asset)
# 4. Main Routine: setup_character_anims(force_dry_run=False, verbose=False)
# 5. CLI Entrypoint with parse_known_args
```

---

## 5. Verification Method

### 5.1 Static Analysis & Syntax Verification
Run Python's built-in syntax compiler to verify that the script contains zero syntax errors:
```powershell
python -m py_compile setup_character_anims.py
```
**Pass Criteria**: Command returns exit code `0` with no syntax errors or output.

### 5.2 Standalone Dry-Run Simulation Verification
Run the script standalone without Unreal Engine installed:
```powershell
python setup_character_anims.py --dry-run --verbose
```
**Pass Criteria**:
- Logs successful validation of all asset paths:
  * `/Game/Materials/M_BRFacelessPlaceholder`
  * `/Game/Materials/MI_BRFacelessManny`
  * `/Game/Materials/MI_BRFacelessBot`
  * `/Game/Characters/Mannequins/Meshes/SKM_Manny`
  * `/Game/Characters/Mannequins/Animations/ABP_BRCharacter`
  * `/Game/Blueprints/BP_BRCharacter`
  * `/Game/Blueprints/BP_BRAIBotCharacter`
- Confirms transform invariants: `RelativeLocation = (0.0, 0.0, -90.0)`, `RelativeRotation = (0.0, -90.0, 0.0)`.
- Confirms CDO properties: `AnimationMode = ANIMATION_BLUEPRINT`, `AnimClass = ABP_BRCharacter_C`.
- Exits with return code `0`.

### 5.3 Invalidation Conditions
The survey recommendations would be invalidated if:
1. `ABRCharacter` removed `bIsADS` or `CurrentMovementState` (verified present in `BRCharacter.h:64-70`).
2. Unreal Engine removed `USkeletalMeshComponent::SetSkeletalMeshAsset` or `AnimClass` (verified stable in UE 5.1–5.8).
3. The project changed constraint C4 to 1st person (hard-locked as 3rd person in `constraint-retention.md`).
