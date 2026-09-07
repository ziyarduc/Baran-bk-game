#!/usr/bin/env python3
"""
test_phase4_empirical_challenger.py
===================================
Adversarial Empirical Stress Test & Invariant Validator Suite for Phase 4.
Authored by Challenger 2 (teamwork_preview_challenger).

Tests:
  1. Cross-script data flow: fetch_osm_data.py -> build_osm_level.py.
  2. Scale verification: 1 UU = 1 cm, height conversion, lane widths, geodesy math.
  3. Rule C1 ("No Interior"): Solid exterior blocks, BlockAll collision, flat walkable roof.
  4. 10-Bot scenario integration: MI_BRFacelessBot vs MI_BRFacelessManny, BP_BRAIBotCharacter CDO.
  5. Adversarial geometry edge cases: degenerate footprints, collinear points, zero area, extreme heights.
  6. Fallback and corrupt dataset resilience.
"""

import copy
import json
import math
import os
import sys
import tempfile
import unittest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import fetch_osm_data
import build_osm_level
import setup_character_anims


class TestPhase4EmpiricalChallenger(unittest.TestCase):
    """Exhaustive empirical test suite challenging Phase 4 implementation."""

    @classmethod
    def setUpClass(cls):
        cls.level_data_path = os.path.join(PROJECT_ROOT, "data", "bakirkoy_level_data.json")
        cls.raw_osm_path = os.path.join(PROJECT_ROOT, "data", "bakirkoy_osm_raw.json")
        
        # Load active level data if present
        if os.path.exists(cls.level_data_path):
            with open(cls.level_data_path, "r", encoding="utf-8") as f:
                cls.active_data = json.load(f)
        else:
            cls.active_data = None

    # =========================================================================
    # 1. CROSS-SCRIPT DATA FLOW & PIPELINE INTEGRATION
    # =========================================================================
    def test_01_json_schema_contract(self):
        """Verify active bakirkoy_level_data.json strictly conforms to Phase 4 architecture contract."""
        self.assertIsNotNone(self.active_data, "data/bakirkoy_level_data.json must exist")
        
        # Check top-level contract keys
        self.assertIn("metadata", self.active_data)
        self.assertIn("buildings", self.active_data)
        self.assertIn("roads", self.active_data)

        meta = self.active_data["metadata"]
        self.assertIn("datum", meta)
        self.assertEqual(meta["datum"]["lat"], fetch_osm_data.ORIGIN_LAT)
        self.assertEqual(meta["datum"]["lon"], fetch_osm_data.ORIGIN_LON)
        self.assertEqual(meta.get("ue_units"), "1 UU = 1 cm")

        # Verify buildings contract
        buildings = self.active_data["buildings"]
        self.assertGreater(len(buildings), 100, "Should have hundreds of buildings")
        b0 = buildings[0]
        for req_key in ("id", "name", "type", "levels", "height_cm", "centroid_ue", "footprint_ue"):
            self.assertIn(req_key, b0, f"Building missing required contract key '{req_key}'")
        self.assertIsInstance(b0["centroid_ue"], (list, tuple))
        self.assertEqual(len(b0["centroid_ue"]), 2)
        self.assertIsInstance(b0["footprint_ue"], list)
        self.assertGreaterEqual(len(b0["footprint_ue"]), 3)

        # Verify roads contract
        roads = self.active_data["roads"]
        self.assertGreater(len(roads), 50, "Should have dozens of roads")
        r0 = roads[0]
        for req_key in ("id", "name", "type", "width_cm", "lanes", "oneway", "points_ue"):
            self.assertIn(req_key, r0, f"Road missing required contract key '{req_key}'")
        self.assertIsInstance(r0["points_ue"], list)
        self.assertGreaterEqual(len(r0["points_ue"]), 2)

    def test_02_fetch_to_build_end_to_end_data_flow(self):
        """Generate level data via fetch_osm_data offline-seed into temp file, then build level from it."""
        import subprocess
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # 1. Run fetch_osm_data generation via CLI
            proc = subprocess.run([
                sys.executable,
                os.path.join(PROJECT_ROOT, "fetch_osm_data.py"),
                "--output", tmp_path,
                "--offline-seed",
                "--verbose"
            ], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, f"fetch_osm_data --offline-seed failed: {proc.stderr}")
            self.assertTrue(os.path.exists(tmp_path))

            # Inspect generated temp json
            with open(tmp_path, "r", encoding="utf-8") as f:
                seed_data = json.load(f)
            self.assertIn("buildings", seed_data)
            self.assertIn("roads", seed_data)
            self.assertGreaterEqual(len(seed_data["buildings"]), 10)
            self.assertGreaterEqual(len(seed_data["roads"]), 5)

            # 2. Feed generated temp json directly into build_osm_level
            build_ok = build_osm_level.build_osm_level(
                map_path="/Game/Maps/TestFeedFlow",
                data_path=tmp_path,
                dry_run=True,
                verbose=False
            )
            self.assertTrue(build_ok, "build_osm_level failed to ingest fetch_osm_data output seamlessly")
            manifest = build_osm_level.LAST_GENERATION_MANIFEST
            self.assertGreaterEqual(manifest["buildings"], len(seed_data["buildings"]))
            self.assertEqual(manifest["nav_bounds"], 1)
            self.assertEqual(manifest["player_starts"], 10)
            self.assertGreaterEqual(manifest["loot_spawners"], 10)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_03_active_level_data_feeding_build_osm_level(self):
        """Execute build_osm_level against the active data/bakirkoy_level_data.json."""
        build_ok = build_osm_level.build_osm_level(
            map_path="/Game/Maps/BakirkoyOSM",
            data_path=self.level_data_path,
            dry_run=True,
            verbose=False
        )
        self.assertTrue(build_ok, "build_osm_level failed with production level data")
        manifest = build_osm_level.LAST_GENERATION_MANIFEST
        self.assertEqual(manifest["buildings"], len(self.active_data["buildings"]))
        self.assertEqual(manifest["nav_bounds"], 1)
        self.assertEqual(manifest["player_starts"], 10)
        self.assertGreaterEqual(manifest["loot_spawners"], 10)
        self.assertGreaterEqual(manifest["road_slabs"], 10)
        self.assertEqual(manifest["road_splines"], len(self.active_data["roads"]))

    # =========================================================================
    # 2. SCALE VERIFICATION (1 UU = 1 cm, Heights, Lane Widths, Geodesy)
    # =========================================================================
    def test_04_scale_1uu_equals_1cm(self):
        """Empirically test that 1 Unreal Unit equals exactly 1 centimeter."""
        # 1 meter displacement North should yield +100 UU along X
        # Compute delta latitude corresponding to 1.0 meter North
        delta_lat_1m = (1.0 / fetch_osm_data.RADIUS_M) * (180.0 / math.pi)
        x_ue, y_ue, z_ue = fetch_osm_data.latlon_to_ue(
            fetch_osm_data.ORIGIN_LAT + delta_lat_1m,
            fetch_osm_data.ORIGIN_LON
        )
        self.assertAlmostEqual(x_ue, 100.0, delta=0.5, msg="1m North must equal 100 UU along +X")
        self.assertAlmostEqual(y_ue, 0.0, delta=0.5, msg="1m North must have ~0 UU along Y")

        # 1 meter displacement East should yield +100 UU along Y
        delta_lon_1m = (1.0 / (fetch_osm_data.RADIUS_N * fetch_osm_data.COS_PHI0)) * (180.0 / math.pi)
        x_ue2, y_ue2, z_ue2 = fetch_osm_data.latlon_to_ue(
            fetch_osm_data.ORIGIN_LAT,
            fetch_osm_data.ORIGIN_LON + delta_lon_1m
        )
        self.assertAlmostEqual(x_ue2, 0.0, delta=0.5, msg="1m East must have ~0 UU along X")
        self.assertAlmostEqual(y_ue2, 100.0, delta=0.5, msg="1m East must equal 100 UU along +Y")

        # Datum origin must map to (0.0, 0.0, 0.0)
        ox, oy, oz = fetch_osm_data.latlon_to_ue(fetch_osm_data.ORIGIN_LAT, fetch_osm_data.ORIGIN_LON)
        self.assertEqual((ox, oy, oz), (0.0, 0.0, 0.0))

    def test_05_wgs84_geodesy_curvature_accuracy(self):
        """Verify WGS84 ellipsoid curvature equations against theoretical values."""
        # At latitude ~40.98 degrees:
        # Standard WGS84 values:
        # RADIUS_M should be ~6,362,800 m
        # RADIUS_N should be ~6,387,300 m
        self.assertGreater(fetch_osm_data.RADIUS_M, 6.35e6)
        self.assertLess(fetch_osm_data.RADIUS_M, 6.38e6)
        self.assertGreater(fetch_osm_data.RADIUS_N, 6.37e6)
        self.assertLess(fetch_osm_data.RADIUS_N, 6.40e6)
        self.assertAlmostEqual(fetch_osm_data.COS_PHI0, math.cos(math.radians(40.98186)), places=5)

    def test_06_building_height_scale_and_units(self):
        """Verify building height units (m -> cm) and realism of synthesized heights."""
        # 1. Explicit height tag: "18.5m" -> 1850 cm
        hm, hcm, lvl = fetch_osm_data.estimate_building_height({"height": "18.5m"}, 123)
        self.assertEqual(hm, 18.5)
        self.assertEqual(hcm, 1850.0)
        self.assertEqual(lvl, 6)

        # 2. Levels tag: 5 levels -> 5 * 3.2m = 16.0m = 1600 cm
        hm, hcm, lvl = fetch_osm_data.estimate_building_height({"levels": "5"}, 123)
        self.assertEqual(hm, 16.0)
        self.assertEqual(hcm, 1600.0)
        self.assertEqual(lvl, 5)

        # 3. Semantic tag: mosque -> 16m = 1600 cm
        hm, hcm, lvl = fetch_osm_data.estimate_building_height({"amenity": "place_of_worship"}, 123)
        self.assertEqual(hm, 16.0)
        self.assertEqual(hcm, 1600.0)

        # 4. Deterministic hash tier (no tags)
        for osm_id in (101, 202, 303, 404, 505):
            hm, hcm, lvl = fetch_osm_data.estimate_building_height({}, osm_id)
            self.assertGreaterEqual(hm, 12.0, "Hash height should be >= 12m for Bakirkoy residential")
            self.assertLessEqual(hm, 18.5, "Hash height should be <= 18.5m")
            self.assertAlmostEqual(hcm, hm * 100.0, delta=1.0)
            self.assertGreaterEqual(lvl, 4)
            self.assertLessEqual(lvl, 6)

        # 5. Check active production buildings
        for bldg in self.active_data["buildings"]:
            h_cm = bldg["height_cm"]
            self.assertGreaterEqual(h_cm, 300.0, f"Building {bldg['id']} height {h_cm}cm is unrealistically small (<3m)")
            self.assertLessEqual(h_cm, 12000.0, f"Building {bldg['id']} height {h_cm}cm is unrealistically tall (>120m)")

    def test_07_road_lane_widths_real_world_scale(self):
        """Verify road widths match real-world standard lane widths (meters to cm)."""
        specs = fetch_osm_data.HIGHWAY_SPECS
        # Motorway: 14m = 1400cm, 4 lanes -> 3.5m/lane
        self.assertEqual(specs["motorway"]["width_m"], 14.0)
        self.assertEqual(specs["motorway"]["lanes"], 4)
        
        # Primary: 12m = 1200cm, 4 lanes -> 3.0m/lane
        self.assertEqual(specs["primary"]["width_m"], 12.0)
        
        # Residential: 6m = 600cm, 2 lanes -> 3.0m/lane
        self.assertEqual(specs["residential"]["width_m"], 6.0)
        self.assertEqual(specs["residential"]["lanes"], 2)

        # Test process_road output
        road_elem = {
            "id": 999,
            "tags": {"highway": "residential", "name": "Istanbul Cd."},
            "geometry": [{"lat": 40.98, "lon": 28.87}, {"lat": 40.981, "lon": 28.871}]
        }
        res = fetch_osm_data.process_road(road_elem)
        self.assertIsNotNone(res)
        self.assertEqual(res["width_m"], 6.0)
        self.assertEqual(res["width_cm"], 600.0)
        self.assertEqual(res["lanes"], 2)

    def test_08_district_scale_and_bounding_box(self):
        """Verify district bounding box fits within the 4km arena floor."""
        xs = []
        ys = []
        for b in self.active_data["buildings"]:
            cx, cy = b["centroid_ue"]
            xs.append(cx)
            ys.append(cy)
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max_x - min_x
        span_y = max_y - min_y

        # Playable district core should be ~1.5km to 3.5km across
        self.assertLess(span_x, 400000.0, "District span X exceeds 4km arena floor")
        self.assertLess(span_y, 400000.0, "District span Y exceeds 4km arena floor")
        self.assertGreater(span_x, 50000.0, "District span X is too small (<500m)")
        self.assertGreater(span_y, 50000.0, "District span Y is too small (<500m)")

    # =========================================================================
    # 3. RULE C1 ("NO INTERIOR") INVARIANT VERIFICATION
    # =========================================================================
    def test_09_rule_c1_solid_exterior_building_blocks(self):
        """Verify all buildings are spawned as solid exterior blocks with zero interior cavity."""
        # Generate level
        build_osm_level.build_osm_level(
            map_path="/Game/Maps/TestC1",
            data_path=self.level_data_path,
            dry_run=True
        )
        actors = build_osm_level.LAST_GENERATED_ACTORS
        building_actors = [a for a in actors if "Building" in getattr(a, "tags", [])]
        self.assertGreaterEqual(len(building_actors), 100)

        for b_actor in building_actors:
            # 1. Must be StaticMeshActor
            self.assertEqual(b_actor.get_class().get_name(), "StaticMeshActor")
            
            # 2. StaticMesh must be /Engine/BasicShapes/Cube.Cube (100% solid primitive)
            comp = b_actor.static_mesh_component
            self.assertIsNotNone(comp)
            self.assertIn("/Engine/BasicShapes/Cube.Cube", str(comp.static_mesh))
            
            # 3. Collision profile must be BlockAll
            self.assertEqual(comp.collision_profile_name, "BlockAll")

            # 4. Elevation: Z must be H / 2 so bottom sits flush on floor at Z=0
            loc = b_actor.get_actor_location()
            scale = b_actor.get_actor_scale3d()
            h_cm = scale.z * 100.0  # Cube base height is 100 cm
            expected_z = h_cm / 2.0
            self.assertAlmostEqual(loc.z, expected_z, delta=1.0, 
                                   msg=f"Building {b_actor.label} bottom must sit on Z=0")

            # 5. Flat walkable rooftop at Z = H
            rooftop_z = loc.z + (h_cm / 2.0)
            self.assertAlmostEqual(rooftop_z, h_cm, delta=1.0)

    def test_10_rule_c1_no_interior_subcomponents(self):
        """Verify spawned building actors contain zero interior props, doors, or hollow rooms."""
        actors = build_osm_level.LAST_GENERATED_ACTORS
        interior_tags = {"Interior", "Room", "Door", "Furniture", "Floor_Internal"}
        for a in actors:
            tags = set(getattr(a, "tags", []))
            intersection = tags.intersection(interior_tags)
            self.assertEqual(len(intersection), 0, f"Actor {a.label} has prohibited interior tags: {intersection}")

    # =========================================================================
    # 4. 10-BOT SCENARIO INTEGRATION
    # =========================================================================
    def test_11_ten_bot_player_start_invariants(self):
        """Verify EXACTLY 10 PlayerStarts are spawned and properly configured for 10-bot scenario."""
        actors = build_osm_level.LAST_GENERATED_ACTORS
        player_starts = [a for a in actors if a.get_class().get_name() == "PlayerStart"]
        self.assertEqual(len(player_starts), 10, "Must spawn EXACTLY 10 PlayerStart actors")

        # Check spacing and elevation
        coords = []
        for ps in player_starts:
            loc = ps.get_actor_location()
            self.assertAlmostEqual(loc.z, 100.0, delta=1.0, msg="PlayerStarts must spawn 1m above ground")
            coords.append((loc.x, loc.y))

        # Ensure no duplicate spawn locations (minimum distance 20m = 2000 UU)
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                dist = math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1])
                self.assertGreater(dist, 2000.0, f"PlayerStarts {i} and {j} too close: {dist} cm")

    def test_12_ten_bot_tactical_loot_spawners(self):
        """Verify at least 10 tactical loot spawners exist tagged for weapons and combat."""
        actors = build_osm_level.LAST_GENERATED_ACTORS
        loot_actors = [a for a in actors if "Loot" in getattr(a, "tags", [])]
        self.assertGreaterEqual(len(loot_actors), 10, "Must spawn >=10 Loot spawners")
        for la in loot_actors:
            self.assertIn("WeaponPickup", la.tags)

    def test_13_character_anims_bot_material_distinction(self):
        """Verify MI_BRFacelessBot material distinction and BP_BRAIBotCharacter CDO configuration."""
        success = setup_character_anims.setup_character_anims(force_dry_run=True, verbose=False)
        self.assertTrue(success, "setup_character_anims failed")

        # Simulate dry run inspection of generated materials
        u = setup_character_anims._MockUnrealModule()
        setup_character_anims.setup_character_anims(force_dry_run=True)

        # Inspect material instances
        mi_manny = u.EditorAssetLibrary.load_asset("/Game/Materials/MI_BRFacelessManny")
        mi_bot = u.EditorAssetLibrary.load_asset("/Game/Materials/MI_BRFacelessBot")
        self.assertIsNotNone(mi_manny)
        self.assertIsNotNone(mi_bot)

        # Check color values
        manny_color = mi_manny.vector_parameter_values.get("BaseColor")
        bot_color = mi_bot.vector_parameter_values.get("BaseColor")
        self.assertIsNotNone(manny_color)
        self.assertIsNotNone(bot_color)

        # Player: Charcoal gray (0.20, 0.20, 0.22)
        self.assertAlmostEqual(manny_color.r, 0.20, places=2)
        self.assertAlmostEqual(manny_color.g, 0.20, places=2)
        self.assertAlmostEqual(manny_color.b, 0.22, places=2)

        # AI Bot: Tactical orange-red (0.70, 0.25, 0.15)
        self.assertAlmostEqual(bot_color.r, 0.70, places=2)
        self.assertAlmostEqual(bot_color.g, 0.25, places=2)
        self.assertAlmostEqual(bot_color.b, 0.15, places=2)

        # Verify distinctness (Euclidean color distance > 0.4)
        color_dist = math.sqrt(
            (manny_color.r - bot_color.r)**2 +
            (manny_color.g - bot_color.g)**2 +
            (manny_color.b - bot_color.b)**2
        )
        self.assertGreater(color_dist, 0.4, "Bot and player materials must be visually distinct")

        # Check BP_BRAIBotCharacter CDO
        bp_bot = u.EditorAssetLibrary.load_asset("/Game/Blueprints/BP_BRAIBotCharacter")
        self.assertIsNotNone(bp_bot)
        cdo_bot = u.get_default_object(bp_bot.generated_class())
        mesh_bot = cdo_bot.mesh

        # Verify skeletal mesh
        self.assertEqual(mesh_bot.skeletal_mesh_asset.get_name(), "SKM_Manny")
        
        # Verify relative transform
        self.assertEqual(mesh_bot.relative_location, u.Vector(0.0, 0.0, -90.0))
        self.assertEqual(mesh_bot.relative_rotation, u.Rotator(0.0, -90.0, 0.0))

        # Verify AnimBP
        self.assertEqual(mesh_bot.animation_mode, "ANIMATION_BLUEPRINT")
        self.assertEqual(mesh_bot.anim_class.get_name(), "ABP_BRCharacter_C")

        # Verify bot override material
        self.assertIn(mi_bot, mesh_bot.override_materials)

    # =========================================================================
    # 5. ADVERSARIAL GEOMETRY & STRESS TEST HARNESS
    # =========================================================================
    def test_14_convex_hull_adversarial_inputs(self):
        """Stress test convex_hull_2d with degenerate, collinear, duplicate, and empty inputs."""
        ch = build_osm_level.convex_hull_2d
        
        # 1. Empty point list
        self.assertEqual(ch([]), [])

        # 2. Single point
        self.assertEqual(ch([[10.0, 20.0]]), [(10.0, 20.0)])

        # 3. Two points
        self.assertEqual(ch([[0.0, 0.0], [10.0, 10.0]]), [(0.0, 0.0), (10.0, 10.0)])

        # 4. Collinear points
        collinear = [[0.0, 0.0], [5.0, 5.0], [10.0, 10.0], [15.0, 15.0]]
        hull_col = ch(collinear)
        self.assertLessEqual(len(hull_col), 2, "Collinear points must reduce to 2 endpoints")

        # 5. Duplicate identical points
        dups = [[5.0, 5.0]] * 10
        self.assertEqual(len(ch(dups)), 1)

        # 6. Standard square
        square = [[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0]]
        hull_sq = ch(square)
        self.assertEqual(len(hull_sq), 4)

    def test_15_obb_rotating_calipers_adversarial_inputs(self):
        """Stress test minimum_area_bounding_box with pathological geometric configurations."""
        obb_fn = build_osm_level.minimum_area_bounding_box

        # 1. Empty polygon
        cx, cy, l, w, yaw = obb_fn([])
        self.assertEqual((cx, cy), (0.0, 0.0))
        self.assertGreater(l, 0)
        self.assertGreater(w, 0)

        # 2. Collinear 3 points
        cx, cy, l, w, yaw = obb_fn([[0.0, 0.0], [500.0, 0.0], [1000.0, 0.0]])
        self.assertAlmostEqual(cx, 500.0, delta=1.0)
        self.assertAlmostEqual(cy, 0.0, delta=1.0)
        self.assertGreaterEqual(l, 200.0)
        self.assertGreaterEqual(w, 200.0)

        # 3. Microscopic polygon (sub-millimeter)
        cx, cy, l, w, yaw = obb_fn([[0.0, 0.0], [0.01, 0.0], [0.01, 0.01], [0.0, 0.01]])
        self.assertAlmostEqual(cx, 0.005, delta=0.01)
        self.assertAlmostEqual(cy, 0.005, delta=0.01)

        # 4. Rotated 45-degree rectangle (side 1000, 2000)
        diag = math.sqrt(2) / 2.0
        # Vertices of box centered at (1000, 2000) rotated 45 deg
        half_l = 1000.0
        half_w = 500.0
        # corners in local coords: (+- half_l, +- half_w)
        corners = [
            (half_l * diag - half_w * diag + 1000, half_l * diag + half_w * diag + 2000),
            (-half_l * diag - half_w * diag + 1000, -half_l * diag + half_w * diag + 2000),
            (-half_l * diag + half_w * diag + 1000, -half_l * diag - half_w * diag + 2000),
            (half_l * diag + half_w * diag + 1000, half_l * diag - half_w * diag + 2000),
        ]
        cx, cy, l, w, yaw = obb_fn(corners)
        self.assertAlmostEqual(cx, 1000.0, delta=5.0)
        self.assertAlmostEqual(cy, 2000.0, delta=5.0)
        dims = sorted([l, w])
        self.assertAlmostEqual(dims[0], 1000.0, delta=5.0)
        self.assertAlmostEqual(dims[1], 2000.0, delta=5.0)
        # Yaw should be ~45 or -45 or 135
        self.assertTrue(abs(abs(yaw) - 45.0) < 2.0 or abs(abs(yaw) - 135.0) < 2.0)

    def test_16_corrupt_and_extreme_dataset_resilience(self):
        """Inject corrupt, incomplete, and adversarial entries into build_osm_level to test resilience."""
        corrupt_dataset = {
            "metadata": {"ue_units": "1 UU = 1 cm"},
            "buildings": [
                # Negative height
                {"id": 1, "name": "NegativeHeight", "height_cm": -500.0, "centroid_ue": [100.0, 100.0]},
                # Zero height
                {"id": 2, "name": "ZeroHeight", "height_cm": 0.0, "centroid_ue": [200.0, 200.0]},
                # Huge height
                {"id": 3, "name": "HugeHeight", "height_cm": 999999.0, "centroid_ue": [300.0, 300.0]},
                # Corrupt footprint format (strings instead of numbers)
                {"id": 4, "name": "CorruptFootprint", "footprint_ue": [["invalid", "pt"], [0, 0]]},
                # Missing coordinates
                {"id": 5, "name": "NoCoords"},
                # Degenerate 1-point footprint
                {"id": 6, "name": "SinglePoint", "footprint_ue": [[50.0, 50.0]]},
            ],
            "roads": [
                # Single point road
                {"id": 1, "points_ue": [[0, 0]]},
                # Zero length road segment
                {"id": 2, "points_ue": [[100, 100], [100, 100]]},
                # Malformed road points
                {"id": 3, "points_ue": "not_a_list"},
            ]
        }
        # Add 10 valid buildings and 10 valid roads to satisfy level invariant thresholds
        for b_i in range(7, 18):
            corrupt_dataset["buildings"].append({
                "id": b_i,
                "name": f"ValidBldg_{b_i}",
                "height_cm": 1500.0,
                "centroid_ue": [b_i * 1000.0, b_i * 1000.0],
                "footprint_ue": [
                    [b_i * 1000.0 - 500, b_i * 1000.0 - 500],
                    [b_i * 1000.0 + 500, b_i * 1000.0 - 500],
                    [b_i * 1000.0 + 500, b_i * 1000.0 + 500],
                    [b_i * 1000.0 - 500, b_i * 1000.0 + 500],
                ]
            })
        for r_i in range(4, 15):
            corrupt_dataset["roads"].append({
                "id": r_i,
                "type": "residential",
                "points_ue": [[r_i * 1000.0, 0], [r_i * 1000.0, 2000.0]]
            })

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as tmp:
            json.dump(corrupt_dataset, tmp)
            corrupt_path = tmp.name

        try:
            # build_osm_level should NOT crash on corrupt data and should satisfy invariants
            build_ok = build_osm_level.build_osm_level(
                map_path="/Game/Maps/TestCorruptResilience",
                data_path=corrupt_path,
                dry_run=True,
                verbose=False
            )
            self.assertTrue(build_ok, "build_osm_level crashed or failed on adversarial/corrupt input")
            manifest = build_osm_level.LAST_GENERATION_MANIFEST
            # Invariants must still hold
            self.assertEqual(manifest["nav_bounds"], 1)
            self.assertEqual(manifest["player_starts"], 10)
            self.assertGreaterEqual(manifest["loot_spawners"], 10)
            self.assertGreaterEqual(manifest["buildings"], 10)
            self.assertGreaterEqual(manifest["road_slabs"], 10)
        finally:
            if os.path.exists(corrupt_path):
                os.remove(corrupt_path)

    def test_17_missing_file_embedded_fallback(self):
        """Verify seamless fallback to authentic embedded Bakirkoy seed when file does not exist."""
        nonexistent_path = os.path.join(PROJECT_ROOT, "data", "definitely_nonexistent_file_999.json")
        build_ok = build_osm_level.build_osm_level(
            map_path="/Game/Maps/TestFallback",
            data_path=nonexistent_path,
            dry_run=True,
            verbose=False
        )
        self.assertTrue(build_ok, "Embedded fallback failed to execute")
        manifest = build_osm_level.LAST_GENERATION_MANIFEST
        self.assertEqual(manifest["nav_bounds"], 1)
        self.assertEqual(manifest["player_starts"], 10)
        self.assertEqual(manifest["buildings"], 25)
        self.assertEqual(manifest["road_splines"], 12)
        self.assertGreaterEqual(manifest["loot_spawners"], 10)



def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase4EmpiricalChallenger)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
