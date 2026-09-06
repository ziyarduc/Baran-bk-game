"""
test_challenge_p2_1.py — Empirical Challenger Test Suite for P2-1.
Target:
  - generate_map.py
  - setup_blueprints.py
Verifies:
  - NavMeshBoundsVolume (count == 1, volume > 0)
  - PlayerStarts (count == 10, radius = 75m, Z = 100, yaw facing center)
  - Loot Spawners (count >= 10, tagged 'Loot' and 'WeaponPickup')
  - Buildings (4), Ramps (4), Covers (6), Boundary Walls (4), Floor (1)
  - Blueprints (11 assets, correct parent classes, CDO wiring)
  - KillFeed Widget hierarchy (CanvasPanel root, VerticalBox top-right)
  - CLI execution and unknown arg resilience
  - Mock editor full-transaction execution
"""

import ast
import math
import os
import subprocess
import sys
import unittest
from typing import Any, Dict, List

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import generate_map
import setup_blueprints


class TestGenerateMapInvariants(unittest.TestCase):
    """Empirical tests for generate_map.py geometric invariants and actor setups."""

    @classmethod
    def setUpClass(cls):
        """Run map generation once in simulation mode to inspect output actors."""
        cls.success = generate_map.generate_map(
            map_path="/Game/Maps/TestChallengeMap",
            dry_run=True
        )
        cls.actors = list(generate_map.LAST_GENERATED_ACTORS)
        cls.manifest = dict(generate_map.LAST_GENERATION_MANIFEST)

    def test_01_generation_succeeds(self):
        """Verify that generate_map returns True in simulation mode."""
        self.assertTrue(self.success, "generate_map returned False")

    def test_02_navmesh_bounds_volume(self):
        """Verify exactly 1 NavMeshBoundsVolume with positive volume and proper extent."""
        nav_volumes = [
            a for a in self.actors
            if isinstance(a, generate_map._MockNavMeshBoundsVolume) or "NavMeshBounds" in a.tags
        ]
        self.assertEqual(len(nav_volumes), 1, f"Expected exactly 1 NavMeshBoundsVolume, found {len(nav_volumes)}")

        nv = nav_volumes[0]
        # Check scale components are positive
        self.assertGreater(nv.scale.x, 0, "NavMesh scale.x must be > 0")
        self.assertGreater(nv.scale.y, 0, "NavMesh scale.y must be > 0")
        self.assertGreater(nv.scale.z, 0, "NavMesh scale.z must be > 0")

        # Positive scale yields positive volume
        volume = nv.scale.x * nv.scale.y * nv.scale.z
        self.assertGreater(volume, 0, f"NavMeshBoundsVolume must have positive volume, got {volume}")

        # Check location covers the arena vertically and horizontally
        self.assertEqual(nv.location.x, 0.0)
        self.assertEqual(nv.location.y, 0.0)
        self.assertEqual(nv.location.z, 1000.0)
        # Expected scale is 120, 120, 30 covering 240m x 240m x 60m
        self.assertEqual((nv.scale.x, nv.scale.y, nv.scale.z), (120.0, 120.0, 30.0))

    def test_03_player_starts_circle_and_orientation(self):
        """Verify exactly 10 PlayerStart actors in a 75m circle (Z=100) facing center (yaw = atan2(-y, -x))."""
        player_starts = [
            a for a in self.actors
            if isinstance(a, generate_map._MockPlayerStart) or "PlayerStart" in a.tags
        ]
        self.assertEqual(len(player_starts), 10, f"Expected exactly 10 PlayerStarts, found {len(player_starts)}")

        expected_radius = 7500.0  # 75m = 7500 cm
        expected_z = 100.0

        for i, ps in enumerate(player_starts):
            # 1. Radius check
            r = math.hypot(ps.location.x, ps.location.y)
            self.assertAlmostEqual(
                r, expected_radius, delta=0.01,
                msg=f"PlayerStart {i} radius {r} != {expected_radius}"
            )

            # 2. Z position check
            self.assertAlmostEqual(
                ps.location.z, expected_z, delta=0.01,
                msg=f"PlayerStart {i} Z {ps.location.z} != {expected_z}"
            )

            # 3. Heading check: must face center (0, 0)
            # Yaw facing center is atan2(-y, -x) in degrees
            angle_to_center_deg = math.degrees(math.atan2(-ps.location.y, -ps.location.x))
            angle_to_center_mod = (angle_to_center_deg + 360.0) % 360.0

            actual_yaw = (ps.rotation.yaw + 360.0) % 360.0

            # Compute angular difference
            diff = abs(angle_to_center_mod - actual_yaw)
            if diff > 180.0:
                diff = 360.0 - diff

            self.assertAlmostEqual(
                diff, 0.0, delta=0.01,
                msg=f"PlayerStart {i} yaw ({actual_yaw:.2f}) does not face center ({angle_to_center_mod:.2f})"
            )

    def test_04_loot_spawners_count_and_tags(self):
        """Verify >= 10 Loot Spawners tagged with both 'Loot' and 'WeaponPickup'."""
        loot_spawners = [
            a for a in self.actors
            if "Loot" in a.tags or "WeaponPickup" in a.tags
        ]
        self.assertGreaterEqual(len(loot_spawners), 10, f"Expected >= 10 loot spawners, found {len(loot_spawners)}")

        for i, ls in enumerate(loot_spawners):
            self.assertIn("Loot", ls.tags, f"Loot spawner {i} ({ls.label}) missing 'Loot' tag")
            self.assertIn("WeaponPickup", ls.tags, f"Loot spawner {i} ({ls.label}) missing 'WeaponPickup' tag")

    def test_05_geometry_buildings_ramps_covers_walls_floor(self):
        """Verify 4 buildings, 4 ramps, 6 cover obstacles, 4 walls, and floor geometry."""
        buildings = [a for a in self.actors if "Building" in a.tags]
        ramps = [a for a in self.actors if "ExternalRamp" in a.tags]
        covers = [a for a in self.actors if "Cover" in a.tags]
        walls = [a for a in self.actors if "ExteriorWall" in a.tags]
        floors = [a for a in self.actors if "Floor" in a.tags]

        self.assertEqual(len(buildings), 4, f"Expected 4 buildings, got {len(buildings)}")
        self.assertEqual(len(ramps), 4, f"Expected 4 ramps, got {len(ramps)}")
        self.assertEqual(len(covers), 6, f"Expected 6 covers, got {len(covers)}")
        self.assertEqual(len(walls), 4, f"Expected 4 boundary walls, got {len(walls)}")
        self.assertEqual(len(floors), 1, f"Expected 1 floor, got {len(floors)}")

        # Check collision profile is BlockAll
        for a in buildings + ramps + covers + walls + floors:
            self.assertEqual(
                a.static_mesh_component.collision_profile_name,
                "BlockAll",
                f"Actor {a.label} does not have BlockAll collision"
            )

        # Check floor dimensions
        floor = floors[0]
        self.assertEqual((floor.scale.x, floor.scale.y, floor.scale.z), (200.0, 200.0, 1.0))
        self.assertEqual(floor.location.z, -50.0)

        # Check building heights (12m -> scale Z=12)
        for b in buildings:
            self.assertEqual(b.scale.z, 12.0, f"Building {b.label} scale Z != 12.0")

    def test_06_invariant_checker_stress_test(self):
        """Stress-test verify_level_invariants with adversarial mutated actor lists."""
        mock_u = generate_map._MockUnrealModule()

        # Adversarial scenario 1: missing nav volume
        no_nav_actors = [a for a in self.actors if not isinstance(a, generate_map._MockNavMeshBoundsVolume)]
        b_pass, counts = generate_map.verify_level_invariants(no_nav_actors, mock_u)
        self.assertFalse(b_pass, "Invariant checker should fail when NavMesh is missing")
        self.assertEqual(counts["nav_bounds"], 0)

        # Adversarial scenario 2: duplicate nav volumes
        extra_nav = generate_map._MockNavMeshBoundsVolume()
        two_nav_actors = list(self.actors) + [extra_nav]
        b_pass, counts = generate_map.verify_level_invariants(two_nav_actors, mock_u)
        self.assertFalse(b_pass, "Invariant checker should fail when NavMesh count != 1")
        self.assertEqual(counts["nav_bounds"], 2)

        # Adversarial scenario 3: fewer than 10 player starts
        fewer_ps = [a for a in self.actors if not (isinstance(a, generate_map._MockPlayerStart) and a.label == "PlayerStart_0")]
        b_pass, counts = generate_map.verify_level_invariants(fewer_ps, mock_u)
        self.assertFalse(b_pass, "Invariant checker should fail when PlayerStarts != 10")
        self.assertEqual(counts["player_starts"], 9)

        # Adversarial scenario 4: fewer than 10 loot spawners
        non_loot = [a for a in self.actors if "Loot" not in a.tags and "WeaponPickup" not in a.tags]
        b_pass, counts = generate_map.verify_level_invariants(non_loot, mock_u)
        self.assertFalse(b_pass, "Invariant checker should fail when loot spawners < 10")
        self.assertEqual(counts["loot_spawners"], 0)

    def test_07_generation_idempotency(self):
        """Verify that running generate_map repeatedly resets state cleanly and yields identical manifests."""
        second_success = generate_map.generate_map(
            map_path="/Game/Maps/TestChallengeMap2",
            dry_run=True
        )
        self.assertTrue(second_success)
        self.assertEqual(len(generate_map.LAST_GENERATED_ACTORS), 43)
        self.assertEqual(generate_map.LAST_GENERATION_MANIFEST["nav_bounds"], 1)
        self.assertEqual(generate_map.LAST_GENERATION_MANIFEST["player_starts"], 10)
        self.assertEqual(generate_map.LAST_GENERATION_MANIFEST["loot_spawners"], 13)


class TestGenerateMapCLI(unittest.TestCase):
    """Test CLI parameter parsing and dry-run execution of generate_map.py."""

    def test_cli_dry_run(self):
        """Test default --dry-run CLI execution."""
        cmd = [sys.executable, os.path.join(PROJECT_ROOT, "generate_map.py"), "--dry-run"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"generate_map.py --dry-run failed:\n{res.stderr}")
        self.assertIn("Successfully Generated and Verified Level", res.stdout)
        self.assertIn("Total Actors Spawned:   43", res.stdout)

    def test_cli_custom_map_path(self):
        """Test --map-path with a custom package path."""
        custom_path = "/Game/Maps/CustomChallengeArena"
        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "generate_map.py"),
            "--dry-run",
            "--map-path",
            custom_path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"generate_map.py custom path failed:\n{res.stderr}")
        self.assertIn(f"Target Level Path: {custom_path}", res.stdout)
        self.assertIn(f"Successfully Generated and Verified Level: {custom_path}", res.stdout)

    def test_cli_unknown_arguments_resilience(self):
        """Test that unknown arguments (like UnrealEngine -run flags) do not crash the parser."""
        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "generate_map.py"),
            "--dry-run",
            "-run=pythonscript",
            "-unattended",
            "--engine-flag=1"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"generate_map.py failed on unknown args:\n{res.stderr}")


class TestSetupBlueprintsAST(unittest.TestCase):
    """Test AST structure, function definitions, and code hygiene of setup_blueprints.py."""

    @classmethod
    def setUpClass(cls):
        filepath = os.path.join(PROJECT_ROOT, "setup_blueprints.py")
        with open(filepath, "r", encoding="utf-8") as f:
            cls.code = f.read()
        cls.tree = ast.parse(cls.code)

    def test_01_ast_cleanliness(self):
        """Verify that setup_blueprints.py parses cleanly into a valid Python AST."""
        self.assertIsInstance(self.tree, ast.Module)

    def test_02_function_definitions_present(self):
        """Verify that all required orchestration and helper functions are defined."""
        expected_funcs = [
            "log",
            "log_warning",
            "log_error",
            "resolve_class",
            "get_or_create_blueprint",
            "get_or_create_widget_blueprint",
            "set_cdo_properties",
            "scaffold_kill_feed_widget",
            "compile_and_save_asset",
            "run_dry_run_simulation",
            "parse_args",
            "setup_blueprints",
        ]
        defined_funcs = [n.name for n in ast.walk(self.tree) if isinstance(n, ast.FunctionDef)]
        for fn in expected_funcs:
            self.assertIn(fn, defined_funcs, f"Required function '{fn}' missing from setup_blueprints.py")

    def test_03_all_functions_have_docstrings(self):
        """Verify that all top-level functions contain descriptive docstrings."""
        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef):
                doc = ast.get_docstring(node)
                self.assertIsNotNone(doc, f"Function '{node.name}' has no docstring")
                self.assertGreater(len(doc.strip()), 10, f"Function '{node.name}' docstring is too short")


class TestSetupBlueprintsSpecifications(unittest.TestCase):
    """Test Blueprint declarations, C++ parent classes, CDO property schemas, and UI layout."""

    def test_01_dry_run_execution_programmatic(self):
        """Verify setup_blueprints(force_dry_run=True) returns True."""
        result = setup_blueprints.setup_blueprints(force_dry_run=True, verbose=True)
        self.assertTrue(result, "setup_blueprints dry run failed")

    def test_02_all_11_blueprints_declared_with_correct_cpp_parents(self):
        """Verify all 11 Blueprint assets are declared with correct C++ parent classes."""
        expected_assets = {
            # UI
            "WBP_KillFeed": "UserWidget",
            "WBP_BRHUDWidget": "BRHUDWidget",
            # Core Gameplay
            "BP_BRCharacter": "BRCharacter",
            "BP_BRAIBotCharacter": "BRAIBotCharacter",
            "BP_BRPlayerController": "BRPlayerController",
            "BP_BRHUD": "BRHUD",
            # Weapons & Projectiles
            "BP_BRProjectileRocket": "BRProjectileRocket",
            "BP_BRWeapon_AR": "BRWeapon_HitScan",
            "BP_BRWeapon_RocketLauncher": "BRWeapon_Projectile",
            # GameModes
            "BP_BRGameMode": "BRGameMode_BattleRoyale",
            "BP_BRGameMode_FFA": "BRGameMode_FFA",
        }

        self.assertEqual(len(expected_assets), 11, "Must verify exactly 11 Blueprint assets")

        # Capture dry-run output
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            setup_blueprints.run_dry_run_simulation()
        out = buf.getvalue()

        # Check each asset and parent class in output
        for asset_name, parent_class in expected_assets.items():
            self.assertIn(asset_name, out, f"Asset '{asset_name}' not listed in dry-run output")
            self.assertIn(parent_class, out, f"Parent class '{parent_class}' for '{asset_name}' not in output")

        self.assertIn("11 Blueprint assets verified, 0 errors", out)

    def test_03_cdo_properties_gamemode_and_hud(self):
        """Verify CDO properties for BP_BRHUD, BP_BRGameMode, and BP_BRGameMode_FFA."""
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            setup_blueprints.run_dry_run_simulation()
        out = buf.getvalue()

        # HUD CDO
        self.assertIn("main_hud_class = WBP_BRHUDWidget", out)

        # BP_BRGameMode CDO
        self.assertIn("default_pawn_class = BP_BRCharacter", out)
        self.assertIn("player_controller_class = BP_BRPlayerController", out)
        self.assertIn("hud_class = BP_BRHUD", out)
        self.assertIn("bot_pawn_class = BP_BRAIBotCharacter", out)
        self.assertIn("bot_controller_class = BRAIController", out)
        self.assertIn("storm_circle_class = BRStormCircle", out)
        self.assertIn("game_state_class = BRGameState", out)
        self.assertIn("player_state_class = BRPlayerState", out)
        self.assertIn("required_bot_count = 10", out)

        # BP_BRGameMode_FFA CDO
        self.assertIn("score_limit = 25", out)
        self.assertIn("match_time_limit = 600.0", out)
        self.assertIn("respawn_delay = 3.0", out)

    def test_04_killfeed_widget_hierarchy_specification(self):
        """Verify WBP_KillFeed widget hierarchy (root CanvasPanel, VerticalBox in upper-right corner)."""
        class MockVector2D:
            def __init__(self, x=0.0, y=0.0):
                self.x = float(x)
                self.y = float(y)

        class MockAnchors:
            def __init__(self, minimum=None, maximum=None):
                self.minimum = minimum or MockVector2D()
                self.maximum = maximum or MockVector2D()

        class MockCanvasPanelSlot:
            def __init__(self):
                self.anchors = None
                self.alignment = None
                self.position = None
                self.size = None

            def set_anchors(self, a):
                self.anchors = a

            def set_alignment(self, al):
                self.alignment = al

            def set_position(self, pos):
                self.position = pos

            def set_size(self, s):
                self.size = s

        class MockCanvasPanel:
            def __init__(self, outer=None):
                self.outer = outer
                self.children = []
                self.slot = MockCanvasPanelSlot()

            def add_child(self, widget):
                self.children.append(widget)
                return self.slot

        class MockVerticalBox:
            def __init__(self, outer=None):
                self.outer = outer

        class MockWidgetTree:
            def __init__(self):
                self.root_widget = None

            def get_editor_property(self, prop):
                if prop == "root_widget":
                    return self.root_widget
                return None

            def set_editor_property(self, prop, val):
                if prop == "root_widget":
                    self.root_widget = val

        class MockWBP:
            def __init__(self):
                self.tree = MockWidgetTree()

            def get_editor_property(self, prop):
                if prop == "widget_tree":
                    return self.tree
                return None

        class MockUnrealForWidget:
            CanvasPanel = MockCanvasPanel
            VerticalBox = MockVerticalBox
            CanvasPanelSlot = MockCanvasPanelSlot
            Anchors = MockAnchors
            Vector2D = MockVector2D

            @staticmethod
            def new_object(cls, outer=None):
                return cls(outer=outer)

            @staticmethod
            def log(msg): pass
            @staticmethod
            def log_warning(msg): pass
            @staticmethod
            def log_error(msg): pass

        old_unreal = setup_blueprints.unreal
        try:
            setup_blueprints.unreal = MockUnrealForWidget()
            mock_wbp = MockWBP()
            scaffold_success = setup_blueprints.scaffold_kill_feed_widget(mock_wbp)

            self.assertTrue(scaffold_success, "scaffold_kill_feed_widget failed")
            # Verify root is CanvasPanel
            self.assertIsInstance(mock_wbp.tree.root_widget, MockCanvasPanel)
            root_canvas = mock_wbp.tree.root_widget
            # Verify child is VerticalBox
            self.assertEqual(len(root_canvas.children), 1)
            self.assertIsInstance(root_canvas.children[0], MockVerticalBox)
            # Verify Anchors: Top-Right (1.0, 0.0)
            slot = root_canvas.slot
            self.assertIsNotNone(slot.anchors)
            self.assertEqual(slot.anchors.minimum.x, 1.0)
            self.assertEqual(slot.anchors.minimum.y, 0.0)
            self.assertEqual(slot.anchors.maximum.x, 1.0)
            self.assertEqual(slot.anchors.maximum.y, 0.0)
            # Alignment: (1.0, 0.0)
            self.assertEqual(slot.alignment.x, 1.0)
            self.assertEqual(slot.alignment.y, 0.0)
            # Position offset
            self.assertEqual(slot.position.x, -20.0)
            self.assertEqual(slot.position.y, 20.0)
        finally:
            setup_blueprints.unreal = old_unreal

    def test_05_set_cdo_properties_unit_logic(self):
        """Verify set_cdo_properties handles snake_case and CamelCase property resolution."""
        class MockCDO:
            def __init__(self):
                self.props = {}
            def set_editor_property(self, name, val):
                # Simulate Unreal where some properties only exist in CamelCase
                if name == "DefaultPawnClass":
                    self.props["DefaultPawnClass"] = val
                elif name == "score_limit":
                    self.props["score_limit"] = val
                else:
                    raise AttributeError(f"Property {name} not found")

        class MockGeneratedClass:
            pass

        class MockBP:
            def get_name(self): return "BP_Test"
            def generated_class(self): return MockGeneratedClass()

        cdo_instance = MockCDO()
        class MockUnrealForCDO:
            @staticmethod
            def get_default_object(cls): return cdo_instance
            @staticmethod
            def log(msg): pass
            @staticmethod
            def log_warning(msg): pass

        old_u = setup_blueprints.unreal
        try:
            setup_blueprints.unreal = MockUnrealForCDO()
            bp = MockBP()
            # Test direct match (score_limit) and CamelCase match (default_pawn_class -> DefaultPawnClass)
            res = setup_blueprints.set_cdo_properties(bp, {
                "score_limit": 25,
                "default_pawn_class": "BP_Character"
            })
            self.assertTrue(res)
            self.assertEqual(cdo_instance.props.get("score_limit"), 25)
            self.assertEqual(cdo_instance.props.get("DefaultPawnClass"), "BP_Character")
        finally:
            setup_blueprints.unreal = old_u

    def test_06_resolve_class_unit_logic(self):
        """Verify resolve_class checks reflected attributes, explicit paths, and default paths."""
        class MockUnrealForResolve:
            Character = "UCharacterRef"
            @staticmethod
            def load_class(outer, path):
                if path == "/Script/BakirkoyBR.CustomExplicit":
                    return "CustomExplicitClass"
                elif path == "/Script/BakirkoyBR.BRCharacter":
                    return "BRCharacterClass"
                return None
            @staticmethod
            def log_warning(msg): pass

        old_u = setup_blueprints.unreal
        try:
            setup_blueprints.unreal = MockUnrealForResolve()
            # 1. Direct attribute on unreal
            c1 = setup_blueprints.resolve_class("Character")
            self.assertEqual(c1, "UCharacterRef")

            # 2. Explicit script path
            c2 = setup_blueprints.resolve_class("CustomExplicit", "/Script/BakirkoyBR.CustomExplicit")
            self.assertEqual(c2, "CustomExplicitClass")

            # 3. Default path fallback
            c3 = setup_blueprints.resolve_class("BRCharacter")
            self.assertEqual(c3, "BRCharacterClass")

            # 4. Non-existent class
            c4 = setup_blueprints.resolve_class("NonExistentClass")
            self.assertIsNone(c4)
        finally:
            setup_blueprints.unreal = old_u


class TestSetupBlueprintsCLI(unittest.TestCase):
    """Test CLI execution and parameter variations for setup_blueprints.py."""

    def test_cli_dry_run(self):
        """Test setup_blueprints.py --dry-run CLI execution."""
        cmd = [sys.executable, os.path.join(PROJECT_ROOT, "setup_blueprints.py"), "--dry-run"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"setup_blueprints.py --dry-run failed:\n{res.stderr}")
        self.assertIn("11 Blueprint assets verified, 0 errors", res.stdout)

    def test_cli_verbose_flag(self):
        """Test setup_blueprints.py --verbose CLI execution."""
        cmd = [sys.executable, os.path.join(PROJECT_ROOT, "setup_blueprints.py"), "--dry-run", "--verbose"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"setup_blueprints.py --verbose failed:\n{res.stderr}")
        self.assertIn("Standalone simulation completed", res.stdout)

    def test_cli_unknown_arguments_resilience(self):
        """Test setup_blueprints.py tolerance to unknown engine flags."""
        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "setup_blueprints.py"),
            "--dry-run",
            "-run=pythonscript",
            "-script=setup_blueprints.py",
            "-unattended"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"setup_blueprints.py failed with unknown engine flags:\n{res.stderr}")


class TestMockEditorEndToEnd(unittest.TestCase):
    """
    Simulate the full Unreal Editor execution path for setup_blueprints.py
    using a mock unreal module that simulates asset tools, factories, CDO, and kismet utilities.
    """

    def test_mock_editor_full_transaction(self):
        """Test full setup_blueprints() execution path inside a simulated Unreal environment."""
        created_assets = {}

        class MockBlueprint:
            def __init__(self, name, package_path, parent_class):
                self.name = name
                self.package_path = package_path
                self.parent_class = parent_class
                self.cdo_properties = {}
                self.compiled = False
                self.saved = False
                self.tree = MockWidgetTree()

            def get_name(self):
                return self.name

            def generated_class(self):
                return self

            def get_editor_property(self, prop):
                if prop == "widget_tree":
                    return self.tree
                return None

            def set_editor_property(self, prop, val):
                self.cdo_properties[prop] = val

        class MockWidgetTree:
            def __init__(self):
                self.root_widget = None

            def get_editor_property(self, prop):
                if prop == "root_widget":
                    return self.root_widget
                return None

            def set_editor_property(self, prop, val):
                if prop == "root_widget":
                    self.root_widget = val

        class MockCanvasPanelSlot:
            def set_anchors(self, a): self.anchors = a
            def set_alignment(self, a): self.alignment = a
            def set_position(self, p): self.position = p
            def set_size(self, s): self.size = s

        class MockCanvasPanel:
            def __init__(self, outer=None):
                self.outer = outer
                self.slot = MockCanvasPanelSlot()
            def add_child(self, child):
                return self.slot

        class MockVerticalBox:
            def __init__(self, outer=None):
                self.outer = outer

        class MockAssetTools:
            def create_asset(self, asset_name, package_path, asset_class, factory):
                bp = MockBlueprint(asset_name, package_path, getattr(factory, "parent_class", None))
                created_assets[f"{package_path}/{asset_name}"] = bp
                return bp

        class MockAssetToolsHelpers:
            @staticmethod
            def get_asset_tools():
                return MockAssetTools()

        class MockFactory:
            def __init__(self):
                self.parent_class = None
            def set_editor_property(self, prop, val):
                if prop == "parent_class":
                    self.parent_class = val

        class MockEditorAssetLibrary:
            @staticmethod
            def does_asset_exist(path):
                return False
            @staticmethod
            def load_asset(path):
                return created_assets.get(path)
            @staticmethod
            def save_loaded_asset(asset):
                asset.saved = True
                return True

        class MockKismetUtilities:
            @staticmethod
            def compile_blueprint(bp):
                bp.compiled = True

        class MockScopedEditorTransaction:
            def __init__(self, desc):
                self.desc = desc
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc_val, exc_tb):
                pass

        class MockFullUnreal:
            ScopedEditorTransaction = MockScopedEditorTransaction
            AssetToolsHelpers = MockAssetToolsHelpers
            BlueprintFactory = MockFactory
            WidgetBlueprintFactory = MockFactory
            EditorAssetLibrary = MockEditorAssetLibrary
            KismetEditorUtilities = MockKismetUtilities
            CanvasPanel = MockCanvasPanel
            VerticalBox = MockVerticalBox
            CanvasPanelSlot = MockCanvasPanelSlot
            WidgetBlueprint = "WidgetBlueprint"
            Anchors = lambda **kwargs: kwargs
            Vector2D = lambda x, y: (x, y)
            UserWidget = "UUserWidget"

            @staticmethod
            def load_class(outer, path):
                return f"Class'{path}'"

            @staticmethod
            def get_default_object(gen_class):
                return gen_class

            @staticmethod
            def new_object(cls, outer=None):
                return cls(outer=outer)

            @staticmethod
            def log(msg): pass
            @staticmethod
            def log_warning(msg): pass
            @staticmethod
            def log_error(msg): pass

        old_unreal = setup_blueprints.unreal
        try:
            setup_blueprints.unreal = MockFullUnreal()
            success = setup_blueprints.setup_blueprints(force_dry_run=False, verbose=True)
            self.assertTrue(success, "Full in-editor transaction simulation failed")

            # Check that all 11 assets were created, compiled, and saved
            self.assertEqual(len(created_assets), 11, f"Expected 11 assets created, got {len(created_assets)}")
            for path, asset in created_assets.items():
                self.assertTrue(asset.compiled, f"Asset {path} was not compiled")
                self.assertTrue(asset.saved, f"Asset {path} was not saved")

            # Verify GameMode CDO wiring in the mock assets
            gm_asset = created_assets.get("/Game/Blueprints/BP_BRGameMode")
            self.assertIsNotNone(gm_asset)
            self.assertEqual(gm_asset.cdo_properties.get("required_bot_count"), 10)

            ffa_asset = created_assets.get("/Game/Blueprints/BP_BRGameMode_FFA")
            self.assertIsNotNone(ffa_asset)
            self.assertEqual(ffa_asset.cdo_properties.get("score_limit"), 25)
            self.assertEqual(ffa_asset.cdo_properties.get("match_time_limit"), 600.0)

        finally:
            setup_blueprints.unreal = old_unreal


if __name__ == "__main__":
    unittest.main()
