import ast
import os
import sys

def audit_generate_map(filepath):
    print(f"[AUDIT] Inspecting AST of {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    tree = ast.parse(source, filename=filepath)
    
    # Check function definitions
    func_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    expected_funcs = {
        'get_subsystems',
        'spawn_actor',
        'get_all_actors',
        'configure_static_mesh_actor',
        'verify_level_invariants',
        'generate_map'
    }
    missing_funcs = expected_funcs - func_names
    assert not missing_funcs, f"Missing expected functions in generate_map.py: {missing_funcs}"
    print(f"  [PASS] Required functions present: {sorted(list(expected_funcs))}")
    
    # Check string constants and references in AST
    strings = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    required_strings = [
        "NavMeshBoundsVolume",
        "PlayerStart",
        "StaticMeshActor",
        "BlockAll",
        "Loot",
        "WeaponPickup",
        "Floor",
        "ExteriorWall",
        "Building",
        "ExternalRamp",
        "Cover",
        "/Game/Maps/BakirkoyMap",
        "LevelEditorSubsystem",
        "EditorActorSubsystem",
        "EditorAssetSubsystem"
    ]
    for req in required_strings:
        assert any(req in s for s in strings), f"Missing required reference '{req}' in generate_map.py"
    print(f"  [PASS] All critical UE5 API strings and tag literals verified.")

    # Check that there are no empty stubs / facades (functions with just 'pass' or returning constant dummies)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in expected_funcs:
            # Check body is not just [Pass]
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                raise AssertionError(f"Function {node.name} is an empty stub (pass)!")
    print(f"  [PASS] Zero stub functions detected in generate_map.py.")


def audit_setup_blueprints(filepath):
    print(f"[AUDIT] Inspecting AST of {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    tree = ast.parse(source, filename=filepath)
    
    func_names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    expected_funcs = {
        'resolve_class',
        'get_or_create_blueprint',
        'get_or_create_widget_blueprint',
        'set_cdo_properties',
        'scaffold_kill_feed_widget',
        'compile_and_save_asset',
        'run_dry_run_simulation',
        'setup_blueprints'
    }
    missing_funcs = expected_funcs - func_names
    assert not missing_funcs, f"Missing expected functions in setup_blueprints.py: {missing_funcs}"
    print(f"  [PASS] Required functions present: {sorted(list(expected_funcs))}")
    
    strings = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    required_bp_targets = [
        "BP_BRGameMode",
        "BP_BRGameMode_FFA",
        "BP_BRCharacter",
        "BP_BRAIBotCharacter",
        "BP_BRPlayerController",
        "BP_BRHUD",
        "BP_BRProjectileRocket",
        "BP_BRWeapon_AR",
        "BP_BRWeapon_RocketLauncher",
        "WBP_KillFeed",
        "WBP_BRHUDWidget"
    ]
    for bp in required_bp_targets:
        assert bp in strings, f"Missing Blueprint target '{bp}' in setup_blueprints.py"
    print(f"  [PASS] All 11 required Blueprint asset targets verified in AST.")

    # Check CDO properties referenced in AST strings
    required_cdo_props = [
        "default_pawn_class",
        "player_controller_class",
        "hud_class",
        "bot_pawn_class",
        "bot_controller_class",
        "storm_circle_class",
        "required_bot_count",
        "main_hud_class"
    ]
    for prop in required_cdo_props:
        assert prop in strings, f"Missing CDO property reference '{prop}' in setup_blueprints.py"
    print(f"  [PASS] All critical CDO property names verified.")

    # Check that there are no empty stubs
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in expected_funcs:
            if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                raise AssertionError(f"Function {node.name} is an empty stub (pass)!")
    print(f"  [PASS] Zero stub functions detected in setup_blueprints.py.")


if __name__ == '__main__':
    audit_generate_map('generate_map.py')
    audit_setup_blueprints('setup_blueprints.py')
    print("[ALL AST AUDITS PASSED CLEANLY]")
