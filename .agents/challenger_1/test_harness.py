#!/usr/bin/env python3
"""
test_harness.py - Adversarial Test Harness & Empirical Verification Suite
========================================================================
Author: Challenger 1 (teamwork_preview_challenger)
Target Scope: Phase 4 Implementation
Target Scripts:
  - fetch_osm_data.py
  - build_osm_level.py
  - setup_character_anims.py

Tests Corner Cases, Degenerate Geometry, Corrupt Inputs, CLI Handling,
and Invariant Enforcement.
"""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from typing import Any, Callable, Dict, List, Tuple

# Project root path resolution
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)

# Import targets under test
try:
    import fetch_osm_data
    import build_osm_level
    import setup_character_anims
except ImportError as e:
    print(f"[FATAL] Failed to import target modules from {PROJECT_ROOT}: {e}")
    sys.exit(1)


# ==============================================================================
# TEST RUNNER INFRASTRUCTURE
# ==============================================================================

class TestResult:
    def __init__(self, name: str, category: str):
        self.name = name
        self.category = category
        self.passed = False
        self.skipped = False
        self.error_msg = ""
        self.details: Dict[str, Any] = {}

    def pass_test(self, details: Dict[str, Any] = None):
        self.passed = True
        if details:
            self.details.update(details)

    def fail_test(self, error_msg: str, details: Dict[str, Any] = None):
        self.passed = False
        self.error_msg = error_msg
        if details:
            self.details.update(details)

    def __repr__(self) -> str:
        status = "PASS" if self.passed else ("SKIP" if self.skipped else "FAIL")
        return f"[{status}] {self.category} :: {self.name}"


class AdversarialTestRunner:
    def __init__(self):
        self.results: List[TestResult] = []

    def run(self, category: str, name: str, test_func: Callable[[TestResult], None]) -> TestResult:
        res = TestResult(name, category)
        try:
            test_func(res)
        except AssertionError as ae:
            res.fail_test(f"AssertionError: {ae}", {"traceback": traceback.format_exc()})
        except Exception as ex:
            res.fail_test(f"Unexpected Exception ({type(ex).__name__}): {ex}", {"traceback": traceback.format_exc()})
        self.results.append(res)
        print(f"  {res}")
        if not res.passed and res.error_msg:
            print(f"      -> ERROR: {res.error_msg}")
        return res

    def summary(self) -> Dict[str, Any]:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed and not r.skipped)
        skipped = sum(1 for r in self.results if r.skipped)
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "success": failed == 0,
        }


# ==============================================================================
# SUITE 1: fetch_osm_data.py ADVERSARIAL TESTS
# ==============================================================================

def test_fetch_projection_math(res: TestResult):
    """Verify WGS84 to UE local tangent plane projection mathematics."""
    # Datum origin projection must evaluate exactly to (0.0, 0.0, 0.0)
    x0, y0, z0 = fetch_osm_data.latlon_to_ue(40.98186, 28.87428, 25.0)
    assert abs(x0) < 0.01, f"Origin X deviation: {x0}"
    assert abs(y0) < 0.01, f"Origin Y deviation: {y0}"
    assert abs(z0) < 0.01, f"Origin Z deviation: {z0}"

    # Moving North (+lat) must produce positive X in UE (+X = North)
    xn, yn, _ = fetch_osm_data.latlon_to_ue(40.99186, 28.87428, 25.0)
    assert xn > 100000.0, f"Expected positive North X > 1000m, got {xn}"
    assert abs(yn) < 1.0, f"Expected near-zero Y for pure North shift, got {yn}"

    # Moving East (+lon) must produce positive Y in UE (+Y = East)
    xe, ye, _ = fetch_osm_data.latlon_to_ue(40.98186, 28.88428, 25.0)
    assert abs(xe) < 1.0, f"Expected near-zero X for pure East shift, got {xe}"
    assert ye > 80000.0, f"Expected positive East Y > 800m, got {ye}"

    # Altitude delta must translate directly to +Z (1m = 100cm = 100 UU)
    _, _, z_up = fetch_osm_data.latlon_to_ue(40.98186, 28.87428, 35.0)
    assert abs(z_up - 1000.0) < 0.01, f"Expected Z=+1000cm (+10m), got {z_up}"

    res.pass_test({"origin": (x0, y0, z0), "north_test": xn, "east_test": ye, "z_test": z_up})


def test_fetch_centroid_collinear_and_degenerate(res: TestResult):
    """Test compute_polygon_centroid with degenerate inputs (0, 1, 2 points, zero area)."""
    # Empty points
    c_empty = fetch_osm_data.compute_polygon_centroid([])
    assert c_empty == [0.0, 0.0], f"Empty polygon centroid must be [0, 0], got {c_empty}"

    # Single point
    c_one = fetch_osm_data.compute_polygon_centroid([[123.4, 567.8]])
    assert c_one == [123.4, 567.8], f"Single point centroid mismatch: {c_one}"

    # Two collinear points in closed loop: [p1, p2, p1].
    # Closed loop drops duplicate closing point when computing arithmetic mean fallback:
    # unique vertices are [0, 0] and [100, 100], mean is [50.0, 50.0].
    c_collinear = fetch_osm_data.compute_polygon_centroid([[0.0, 0.0], [100.0, 100.0], [0.0, 0.0]])
    assert c_collinear == [50.0, 50.0], f"Collinear mean mismatch: {c_collinear}"

    # Regular triangle centroid
    tri = [[0.0, 0.0], [600.0, 0.0], [0.0, 600.0], [0.0, 0.0]]
    c_tri = fetch_osm_data.compute_polygon_centroid(tri)
    assert abs(c_tri[0] - 200.0) < 0.1 and abs(c_tri[1] - 200.0) < 0.1, f"Triangle centroid mismatch: {c_tri}"

    res.pass_test({"c_empty": c_empty, "c_one": c_one, "c_collinear": c_collinear, "c_tri": c_tri})


def test_fetch_height_synthesis_tiers(res: TestResult):
    """Verify 4-tier height synthesis engine in fetch_osm_data."""
    est = fetch_osm_data.estimate_building_height

    # Tier 1: Explicit height tag
    h_m1, h_cm1, lvl1 = est({"height": "22.5"}, 1001)
    assert h_m1 == 22.5 and h_cm1 == 2250.0 and lvl1 == 7, f"Tier 1 mismatch: {h_m1}, {h_cm1}, {lvl1}"

    # Tier 1b: Explicit building:height tag with units
    h_m1b, h_cm1b, lvl1b = est({"building:height": "16 m"}, 1002)
    assert h_m1b == 16.0 and h_cm1b == 1600.0, f"Tier 1b mismatch: {h_m1b}"

    # Tier 2: Explicit levels tag (levels * 3.2m)
    h_m2, h_cm2, lvl2 = est({"building:levels": "5"}, 1003)
    assert h_m2 == 16.0 and h_cm2 == 1600.0 and lvl2 == 5, f"Tier 2 mismatch: {h_m2}, {h_cm2}, {lvl2}"

    # Tier 3: Semantic heuristic (mosque -> 16m, hospital -> 14m, garage -> 3.5m)
    h_m3, h_cm3, lvl3 = est({"building": "mosque"}, 1004)
    assert h_m3 == 16.0 and h_cm3 == 1600.0, f"Tier 3 mosque mismatch: {h_m3}"

    h_m3_hosp, _, _ = est({"amenity": "hospital"}, 1005)
    assert h_m3_hosp == 14.0, f"Tier 3 hospital mismatch: {h_m3_hosp}"

    # Tier 4: Deterministic hash (unspecified building)
    h_m4a, _, _ = est({"building": "yes"}, 99999)
    h_m4b, _, _ = est({"building": "yes"}, 99999)
    assert h_m4a == h_m4b, "Deterministic hash must produce identical results for same osm_id"
    assert 6.0 <= h_m4a <= 24.0, f"Tier 4 height out of bounds [6, 24]: {h_m4a}"

    res.pass_test({"tier1": h_m1, "tier2": h_m2, "tier3_mosque": h_m3, "tier4_hash": h_m4a})


def test_fetch_corrupt_geometry_points(res: TestResult):
    """Stress test process_building and process_road with corrupt coordinates."""
    # Building with None/missing coordinates
    b_none = fetch_osm_data.process_building({
        "id": 1,
        "tags": {"building": "yes"},
        "geometry": [{"lat": None, "lon": 28.8}, {"lat": 40.9, "lon": None}]
    })
    assert b_none is None, "Building with insufficient valid coordinates must return None"

    # Road with <2 points
    r_one = fetch_osm_data.process_road({
        "id": 2,
        "tags": {"highway": "residential"},
        "geometry": [{"lat": 40.98, "lon": 28.87}]
    })
    assert r_one is None, "Road with 1 point must return None"

    res.pass_test({"corrupt_building_handled": True, "single_pt_road_handled": True})


def test_fetch_nonexistent_cache(res: TestResult):
    """Test fetch_osm_data with nonexistent cache file with --offline-seed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_json = os.path.join(tmpdir, "level_data.json")
        nonexistent_cache = os.path.join(tmpdir, "does_not_exist_raw.json")

        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "fetch_osm_data.py"),
            "--offline-seed",
            "--cache-file", nonexistent_cache,
            "--output", out_json,
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 0, f"Process failed with code {proc.returncode}: {proc.stderr}"
        assert os.path.exists(out_json), "Output JSON was not created"

        with open(out_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["metadata"]["data_source"] == "embedded_offline_seed"
        assert data["metadata"]["total_buildings"] > 0
        assert data["metadata"]["total_roads"] > 0

    res.pass_test({"buildings": data["metadata"]["total_buildings"], "roads": data["metadata"]["total_roads"]})


def test_fetch_corrupt_cache_files(res: TestResult):
    """Adversarial test: fetch_osm_data against severely corrupted cache files."""
    corrupt_scenarios = [
        ("truncated_json", '{"version": 0.6, "elements": [ {"id": 1,'),
        ("empty_file", ""),
        ("integer_root", "12345"),
        ("array_root", "[1, 2, 3]"),
        ("missing_elements", '{"generator": "test"}'),
        ("null_elements", '{"elements": null}'),
        ("elements_not_list", '{"elements": "not a list"}'),
        ("elements_with_corrupt_items", '{"elements": [null, 123, "string", {}, {"id": "invalid"}]}'),
    ]

    results_detail = {}
    for name, content in corrupt_scenarios:
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_cache = os.path.join(tmpdir, f"cache_{name}.json")
            out_json = os.path.join(tmpdir, f"out_{name}.json")
            with open(bad_cache, "w", encoding="utf-8") as f:
                f.write(content)

            cmd = [
                sys.executable,
                os.path.join(PROJECT_ROOT, "fetch_osm_data.py"),
                "--offline-seed",
                "--cache-file", bad_cache,
                "--output", out_json,
            ]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            assert proc.returncode == 0, f"Scenario '{name}' failed with code {proc.returncode}: {proc.stderr}"
            assert os.path.exists(out_json), f"Output file for '{name}' was not created"

            with open(out_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert len(data["buildings"]) > 0, f"Scenario '{name}' yielded 0 buildings"
            results_detail[name] = "HANDLED_CLEANLY"

    res.pass_test(results_detail)


def test_fetch_offline_seed_schema_and_types(res: TestResult):
    """Test schema, numeric types, and bounding box of generated offline seed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_json = os.path.join(tmpdir, "seed_test.json")
        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "fetch_osm_data.py"),
            "--offline-seed",
            "--output", out_json,
            "--verbose",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 0, f"Seed generation failed: {proc.stderr}"

        with open(out_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 1. Check top-level contract keys
        assert "metadata" in data, "Missing 'metadata'"
        assert "buildings" in data, "Missing 'buildings'"
        assert "roads" in data, "Missing 'roads'"

        meta = data["metadata"]
        assert meta["datum"]["lat"] == 40.98186
        assert meta["datum"]["lon"] == 28.87428
        assert meta["datum"]["alt_m"] == 25.0
        assert meta["ue_units"] == "1 UU = 1 cm"

        # 2. Check bounds
        bounds = meta["bounds_ue"]
        assert bounds["min_x"] < bounds["max_x"], f"Invalid X bounds: {bounds}"
        assert bounds["min_y"] < bounds["max_y"], f"Invalid Y bounds: {bounds}"

        # 3. Check building types and fields
        buildings = data["buildings"]
        assert len(buildings) >= 10, f"Expected >=10 seed buildings, got {len(buildings)}"
        for b in buildings:
            assert isinstance(b["id"], int), f"Building ID not int: {b}"
            assert isinstance(b["name"], str), f"Building name not str: {b}"
            assert isinstance(b["height_cm"], (int, float)) and b["height_cm"] > 0, f"Invalid height_cm: {b}"
            assert len(b["centroid_ue"]) == 2 and all(isinstance(c, (int, float)) for c in b["centroid_ue"]), f"Bad centroid: {b}"
            assert len(b["footprint_ue"]) >= 3, f"Footprint has <3 vertices: {b}"
            for pt in b["footprint_ue"]:
                assert len(pt) == 2 and all(isinstance(coord, (int, float)) for coord in pt), f"Bad pt in footprint: {pt}"

        # 4. Check road types and fields
        roads = data["roads"]
        assert len(roads) >= 5, f"Expected >=5 seed roads, got {len(roads)}"
        for r in roads:
            assert isinstance(r["id"], int), f"Road ID not int: {r}"
            assert isinstance(r["width_cm"], (int, float)) and r["width_cm"] > 0, f"Invalid width_cm: {r}"
            assert isinstance(r["lanes"], int), f"Lanes not int: {r}"
            assert isinstance(r["oneway"], bool), f"Oneway not bool: {r}"
            assert len(r["points_ue"]) >= 2, f"Road has <2 points: {r}"
            for pt in r["points_ue"]:
                assert len(pt) == 2 and all(isinstance(coord, (int, float)) for coord in pt), f"Bad pt in road: {pt}"

    res.pass_test({
        "total_buildings": len(buildings),
        "total_roads": len(roads),
        "bounds": bounds,
    })


def test_fetch_invalid_cli_arguments(res: TestResult):
    """Verify fetch_osm_data cleanly rejects invalid CLI arguments."""
    # Test invalid spatial mode
    cmd_mode = [sys.executable, os.path.join(PROJECT_ROOT, "fetch_osm_data.py"), "--mode", "galaxy"]
    proc_mode = subprocess.run(cmd_mode, capture_output=True, text=True)
    assert proc_mode.returncode != 0, f"Expected failure for invalid mode, got code {proc_mode.returncode}"

    # Test unknown flag
    cmd_badflag = [sys.executable, os.path.join(PROJECT_ROOT, "fetch_osm_data.py"), "--nonexistent-flag-xyz"]
    proc_badflag = subprocess.run(cmd_badflag, capture_output=True, text=True)
    assert proc_badflag.returncode != 0, f"Expected failure for unknown flag, got code {proc_badflag.returncode}"

    res.pass_test({
        "mode_exit_code": proc_mode.returncode,
        "badflag_exit_code": proc_badflag.returncode
    })


def test_validate_existing_level_data_json(res: TestResult):
    """Empirically inspect the project level data file data/bakirkoy_level_data.json."""
    data_file = os.path.join(PROJECT_ROOT, "data", "bakirkoy_level_data.json")
    if not os.path.exists(data_file):
        res.fail_test(f"File not found: {data_file}")
        return

    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta = data.get("metadata", {})
    bldgs = data.get("buildings", [])
    roads = data.get("roads", [])

    assert "bounds_ue" in meta, "Missing bounds_ue"
    b = meta["bounds_ue"]
    assert b["min_x"] < b["max_x"], f"min_x ({b['min_x']}) >= max_x ({b['max_x']})"
    assert b["min_y"] < b["max_y"], f"min_y ({b['min_y']}) >= max_y ({b['max_y']})"

    assert len(bldgs) >= 2000, f"Expected large building count (>2000), got {len(bldgs)}"
    assert len(roads) >= 300, f"Expected large road count (>300), got {len(roads)}"

    res.pass_test({
        "buildings_count": len(bldgs),
        "roads_count": len(roads),
        "bounds": b,
        "data_source": meta.get("data_source"),
    })


# ==============================================================================
# SUITE 2: build_osm_level.py ADVERSARIAL TESTS
# ==============================================================================

def test_build_geometry_rotating_calipers_degenerates(res: TestResult):
    """Test Andrew's Monotone Chain Convex Hull and Rotating Calipers with degenerate polygons."""
    mbb = build_osm_level.minimum_area_bounding_box
    ch = build_osm_level.convex_hull_2d

    # 1. Empty polygon
    obb_empty = mbb([])
    assert obb_empty == (0.0, 0.0, 1000.0, 1000.0, 0.0), f"Empty polygon OBB mismatch: {obb_empty}"

    # 2. Single point
    obb_single = mbb([[100.0, 200.0]])
    assert obb_single[0] == 100.0 and obb_single[1] == 200.0
    assert obb_single[2] >= 200.0 and obb_single[3] >= 200.0

    # 3. Two points (degenerate line segment)
    obb_two = mbb([[0.0, 0.0], [500.0, 0.0]])
    assert obb_two[2] >= 500.0
    assert obb_two[3] >= 200.0  # Clamped minimum width

    # 4. Collinear points (3 points on a straight line)
    hull_collinear = ch([[0.0, 0.0], [100.0, 100.0], [200.0, 200.0]])
    assert len(hull_collinear) <= 2, f"Collinear hull must have <=2 vertices, got {len(hull_collinear)}"
    obb_collinear = mbb([[0.0, 0.0], [100.0, 100.0], [200.0, 200.0]])
    assert obb_collinear[2] >= 200.0 and obb_collinear[3] >= 200.0

    # 5. Coincident points (all vertices identical)
    obb_identical = mbb([[50.0, 50.0], [50.0, 50.0], [50.0, 50.0]])
    assert obb_identical[0] == 50.0 and obb_identical[1] == 50.0
    assert obb_identical[2] == 200.0 and obb_identical[3] == 200.0

    # 6. Regular Rectangle: 4000 cm length x 2000 cm width, axis-aligned
    rect_pts = [[-2000.0, -1000.0], [2000.0, -1000.0], [2000.0, 1000.0], [-2000.0, 1000.0]]
    cx, cy, l, w, yaw = mbb(rect_pts)
    assert abs(cx) < 1.0 and abs(cy) < 1.0, f"Rectangle center mismatch: ({cx}, {cy})"
    dim1, dim2 = max(l, w), min(l, w)
    assert abs(dim1 - 4000.0) < 10.0, f"Dimension 1 mismatch: {dim1} != 4000"
    assert abs(dim2 - 2000.0) < 10.0, f"Dimension 2 mismatch: {dim2} != 2000"

    # 7. Circle approximation (100 vertices)
    circle_pts = [
        [1000.0 * math.cos(2 * math.pi * i / 100), 1000.0 * math.sin(2 * math.pi * i / 100)]
        for i in range(100)
    ]
    cx_c, cy_c, l_c, w_c, _ = mbb(circle_pts)
    assert abs(cx_c) < 10.0 and abs(cy_c) < 10.0
    assert abs(l_c - 2000.0) < 50.0 and abs(w_c - 2000.0) < 50.0

    res.pass_test({
        "obb_empty": obb_empty,
        "obb_two": obb_two,
        "obb_collinear": obb_collinear,
        "rect_dimensions": (dim1, dim2),
        "circle_dimensions": (l_c, w_c),
    })


def test_build_missing_gis_data_fallback(res: TestResult):
    """Test build_osm_level with missing GIS data file (verify authentic embedded fallback)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nonexistent = os.path.join(tmpdir, "nonexistent_gis.json")
        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "build_osm_level.py"),
            "--data-path", nonexistent,
            "--dry-run",
            "--verbose",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 0, f"Fallback execution failed with code {proc.returncode}: {proc.stderr}"
        assert "[GIS] Using embedded authentic fallback dataset of central Bakirkoy" in proc.stdout, \
            "Stdout did not indicate fallback activation"

        # Verify manifest in output
        assert "NavMeshBoundsVolume:    1" in proc.stdout
        assert "PlayerStart Actors:     10" in proc.stdout
        assert "Loot Spawners:          16" in proc.stdout

    res.pass_test({"fallback_activated": True, "returncode": proc.returncode})


def test_build_malformed_json_corrupt_syntax(res: TestResult):
    """Test build_osm_level with a corrupt/invalid JSON syntax file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        bad_json = os.path.join(tmpdir, "broken.json")
        with open(bad_json, "w", encoding="utf-8") as f:
            f.write("{ broken json syntax : [1, 2,")

        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "build_osm_level.py"),
            "--data-path", bad_json,
            "--dry-run",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        # It must catch JSONDecodeError, log warning, switch to embedded fallback, and return 0
        assert proc.returncode == 0, f"Expected fallback recovery, failed with code {proc.returncode}: {proc.stderr}"
        assert "Switching to embedded fallback" in proc.stdout

    res.pass_test({"recovered_via_fallback": True})


def test_build_malformed_json_missing_keys_protection(res: TestResult):
    """Adversarial test: Valid JSON but missing buildings or roads must fail invariant checks, protecting level."""
    # Case A: Missing buildings key
    with tempfile.TemporaryDirectory() as tmpdir:
        no_buildings_json = os.path.join(tmpdir, "no_buildings.json")
        with open(no_buildings_json, "w", encoding="utf-8") as f:
            json.dump({"metadata": {}, "roads": [{"id": 1, "points_ue": [[0, 0], [1000, 0]]}]}, f)

        cmd_nb = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "build_osm_level.py"),
            "--data-path", no_buildings_json,
            "--dry-run",
        ]
        proc_nb = subprocess.run(cmd_nb, capture_output=True, text=True)
        # Should fail verification (code 1) because buildings < 10
        assert proc_nb.returncode == 1, f"Expected failure when buildings missing, got code {proc_nb.returncode}"
        assert "INVARIANT VIOLATION: Expected at least 10 Buildings" in proc_nb.stdout

    # Case B: Missing roads key
    with tempfile.TemporaryDirectory() as tmpdir:
        no_roads_json = os.path.join(tmpdir, "no_roads.json")
        with open(no_roads_json, "w", encoding="utf-8") as f:
            # 12 buildings, 0 roads
            bldgs = [{"id": i, "footprint_ue": [[i*100, 0], [i*100+50, 0], [i*100+50, 50], [i*100, 50]]} for i in range(15)]
            json.dump({"metadata": {}, "buildings": bldgs, "roads": []}, f)

        cmd_nr = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "build_osm_level.py"),
            "--data-path", no_roads_json,
            "--dry-run",
        ]
        proc_nr = subprocess.run(cmd_nr, capture_output=True, text=True)
        # Should fail verification (code 1) because road slabs < 10
        assert proc_nr.returncode == 1, f"Expected failure when roads missing, got code {proc_nr.returncode}"
        assert "INVARIANT VIOLATION: Expected at least 10 Road Slabs" in proc_nr.stdout

    res.pass_test({"no_buildings_blocked": True, "no_roads_blocked": True})


def test_build_degenerate_polygons_level_execution(res: TestResult):
    """Stress test: feed dataset containing degenerate polygons to build_osm_level."""
    with tempfile.TemporaryDirectory() as tmpdir:
        degenerate_json = os.path.join(tmpdir, "degenerate_buildings.json")

        # Create 12 buildings with degenerate footprints
        bldgs = [
            {"id": 1, "name": "Collinear", "footprint_ue": [[0, 0], [100, 100], [200, 200]]},
            {"id": 2, "name": "TwoPoints", "footprint_ue": [[0, 0], [500, 500]]},
            {"id": 3, "name": "SinglePoint", "footprint_ue": [[100, 100]]},
            {"id": 4, "name": "EmptyFootprint", "footprint_ue": [], "centroid_ue": [500, 500]},
            {"id": 5, "name": "Coincident", "footprint_ue": [[300, 300], [300, 300], [300, 300]]},
            {"id": 6, "name": "DictPoints", "footprint_ue": [{"x": 0, "y": 0}, {"x": 200, "y": 0}, {"x": 200, "y": 200}]},
            {"id": 7, "name": "ZeroHeight", "height_cm": 0.0, "footprint_ue": [[1000, 1000], [1500, 1000], [1500, 1500], [1000, 1500]]},
            {"id": 8, "name": "NegativeHeight", "height_cm": -500.0, "footprint_ue": [[2000, 1000], [2500, 1000], [2500, 1500], [2000, 1500]]},
            {"id": 9, "name": "ObbExplicit", "obb": {"center_x": 3000, "center_y": 1000, "length": 800, "width": 600, "yaw": 45}},
            {"id": 10, "name": "CentroidOnly", "centroid_ue": [4000, 1000]},
            {"id": 11, "name": "CentroidDict", "centroid_ue": {"x": 5000, "y": 1000}},
            {"id": 12, "name": "LargePoly", "footprint_ue": [[-1000, -1000], [0, -1000], [0, 0], [-1000, 0]]},
        ]
        # 12 valid roads
        roads = [
            {"id": i, "highway": "residential", "points_ue": [[i*1000, -2000], [i*1000, 2000]]}
            for i in range(12)
        ]

        with open(degenerate_json, "w", encoding="utf-8") as f:
            json.dump({"metadata": {}, "buildings": bldgs, "roads": roads}, f)

        cmd = [
            sys.executable,
            os.path.join(PROJECT_ROOT, "build_osm_level.py"),
            "--data-path", degenerate_json,
            "--dry-run",
            "--verbose",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 0, f"Failed on degenerate polygons with code {proc.returncode}: {proc.stderr}"
        assert "Spawned 12 solid exterior buildings" in proc.stdout

    res.pass_test({"handled_degenerate_buildings": 12})


def test_build_road_micro_segments(res: TestResult):
    """Verify road micro-segments (<20 cm) are skipped to prevent degenerate geometry."""
    with tempfile.TemporaryDirectory() as tmpdir:
        micro_json = os.path.join(tmpdir, "micro_roads.json")
        # Road with 5 micro segments of 5cm each, plus 1 valid 500cm segment
        roads = [
            {
                "id": 101,
                "highway": "residential",
                "points_ue": [
                    [0, 0], [5, 0], [10, 0], [15, 0], [500, 0]
                ]
            }
        ]
        bldgs = [{"id": i, "footprint_ue": [[i*200, 0], [i*200+100, 0], [i*200+100, 100], [i*200, 100]]} for i in range(12)]
        with open(micro_json, "w", encoding="utf-8") as f:
            json.dump({"metadata": {}, "buildings": bldgs, "roads": roads}, f)

        mock_module = build_osm_level._MockUnrealModule()
        build_osm_level.build_osm_level(
            data_path=micro_json,
            dry_run=True,
            unreal_module=mock_module
        )
        actors = mock_module._actor_subsystem.get_all_level_actors()
        road_slabs = [a for a in actors if "RoadSlab" in getattr(a, "tags", [])]
        # Only the 500cm segment should be spawned; the 5cm micro segments are skipped
        assert len(road_slabs) == 1, f"Expected exactly 1 road slab (skipping micro-segments), got {len(road_slabs)}"

    res.pass_test({"road_slabs_spawned": len(road_slabs)})


def test_build_invariant_verification_rigorous(res: TestResult):
    """Deep inspection of spawned mock actors and invariant properties."""
    mock_module = build_osm_level._MockUnrealModule()
    level_data_path = os.path.join(PROJECT_ROOT, "data", "bakirkoy_level_data.json")
    if not os.path.exists(level_data_path):
        level_data_path = "nonexistent.json"

    success = build_osm_level.build_osm_level(
        map_path="/Game/Maps/BakirkoyOSM",
        data_path=level_data_path,
        dry_run=True,
        verbose=False,
        unreal_module=mock_module
    )
    assert success is True, "build_osm_level returned False"

    all_actors = mock_module._actor_subsystem.get_all_level_actors()
    manifest = build_osm_level.LAST_GENERATION_MANIFEST

    # 1. NavMeshBoundsVolume invariant
    navs = [a for a in all_actors if "NavMeshBounds" in getattr(a, "tags", [])]
    assert len(navs) == 1, f"Expected EXACTLY 1 NavMeshBoundsVolume, found {len(navs)}"
    nav = navs[0]
    assert nav.location.x == 0.0 and nav.location.y == 0.0 and nav.location.z == 2000.0, f"NavMesh loc: {nav.location}"
    assert nav.scale.x == 4400.0 and nav.scale.y == 4400.0 and nav.scale.z == 80.0, f"NavMesh scale: {nav.scale}"

    # 2. PlayerStart invariant
    player_starts = [a for a in all_actors if "PlayerStart" in getattr(a, "tags", [])]
    assert len(player_starts) == 10, f"Expected EXACTLY 10 PlayerStarts, found {len(player_starts)}"
    # Check that all player starts have Z == 100.0 (anti-floor-clip)
    for ps in player_starts:
        assert abs(ps.location.z - 100.0) < 0.1, f"PlayerStart Z is {ps.location.z}, expected 100.0"

    # 3. Loot Spawners invariant (>=10, tagged Loot and WeaponPickup)
    loot_spawners = [a for a in all_actors if "Loot" in getattr(a, "tags", []) and "WeaponPickup" in getattr(a, "tags", [])]
    assert len(loot_spawners) >= 10, f"Expected >=10 Loot spawners, found {len(loot_spawners)}"

    # 4. Arena Floor invariant
    floors = [a for a in all_actors if "Floor" in getattr(a, "tags", [])]
    assert len(floors) == 1, f"Expected 1 Floor, found {len(floors)}"
    fl = floors[0]
    assert fl.location.z == -50.0, f"Floor location Z is {fl.location.z}, expected -50.0"
    assert fl.scale.x == 4000.0 and fl.scale.y == 4000.0, f"Floor scale is {fl.scale}"
    assert fl.static_mesh_component.collision_profile_name == "BlockAll"

    # 5. Solid exterior buildings (Rule C1)
    bldgs = [a for a in all_actors if "Building" in getattr(a, "tags", [])]
    assert len(bldgs) >= 10, f"Expected >=10 buildings, found {len(bldgs)}"
    for b in bldgs[:50]:  # sample check first 50
        # Elevation Z must be H / 2.0 = scale.z * 100 / 2.0 = scale.z * 50
        expected_z = b.scale.z * 50.0
        assert abs(b.location.z - expected_z) < 1.0, f"Building Z={b.location.z} != scale.z*50 ({expected_z})"
        assert b.static_mesh_component.collision_profile_name == "BlockAll"

    # 6. Road Slabs and Splines
    slabs = [a for a in all_actors if "RoadSlab" in getattr(a, "tags", [])]
    assert len(slabs) >= 10, f"Expected >=10 road slabs, found {len(slabs)}"
    splines = [a for a in all_actors if "RoadSpline" in getattr(a, "tags", [])]
    assert len(splines) >= 5, f"Expected >=5 road splines, found {len(splines)}"

    res.pass_test({
        "total_actors": len(all_actors),
        "nav_bounds": len(navs),
        "player_starts": len(player_starts),
        "loot_spawners": len(loot_spawners),
        "floors": len(floors),
        "buildings": len(bldgs),
        "road_slabs": len(slabs),
        "road_splines": len(splines),
    })


# ==============================================================================
# SUITE 3: setup_character_anims.py ADVERSARIAL TESTS
# ==============================================================================

def test_char_anims_cli_flags(res: TestResult):
    """Test setup_character_anims with various CLI flags and unrecognized arguments."""
    flag_combinations = [
        ["--dry-run"],
        ["--verbose"],
        ["--dry-run", "--verbose"],
        [],  # auto-detection
        ["--dry-run", "-unattended", "-nullrhi", "-NoPause"],  # engine commandlet flags
    ]

    runs_detail = {}
    for flags in flag_combinations:
        cmd = [sys.executable, os.path.join(PROJECT_ROOT, "setup_character_anims.py")] + flags
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 0, f"Flag combo {flags} failed with code {proc.returncode}: {proc.stderr}"
        flag_str = " ".join(flags) if flags else "(default)"
        runs_detail[flag_str] = "EXIT_0"

    res.pass_test(runs_detail)


def test_char_anims_material_parameters(res: TestResult):
    """Inspect and verify procedural material parameters (PBR colors, roughness, metallic)."""
    ok = setup_character_anims.setup_character_anims(force_dry_run=True, verbose=False)
    assert ok is True, "setup_character_anims returned False"

    asset_lib = setup_character_anims._MockEditorAssetLibrary.get_instance()

    # 1. Master Material
    m_master = asset_lib.load_asset("/Game/Materials/M_BRFacelessPlaceholder")
    assert m_master is not None, "Master material M_BRFacelessPlaceholder missing"

    # 2. Player Material Instance (MI_BRFacelessManny: Charcoal Studio Gray)
    mi_manny = asset_lib.load_asset("/Game/Materials/MI_BRFacelessManny")
    assert mi_manny is not None, "MI_BRFacelessManny missing"
    assert mi_manny.parent == m_master, "MI_BRFacelessManny parent != M_BRFacelessPlaceholder"
    assert "BaseColor" in mi_manny.vector_parameter_values, "MI_BRFacelessManny missing BaseColor"
    bc_manny = mi_manny.vector_parameter_values["BaseColor"]
    assert abs(bc_manny.r - 0.20) < 0.02 and abs(bc_manny.g - 0.20) < 0.02 and abs(bc_manny.b - 0.22) < 0.02, \
        f"Manny BaseColor mismatch: {bc_manny}"
    assert abs(mi_manny.scalar_parameter_values.get("Roughness", 0.0) - 0.60) < 0.02, "Manny Roughness mismatch"
    assert abs(mi_manny.scalar_parameter_values.get("Metallic", 0.0) - 0.0) < 0.02, "Manny Metallic mismatch"

    # 3. AI Bot Material Instance (MI_BRFacelessBot: Tactical Orange-Red)
    mi_bot = asset_lib.load_asset("/Game/Materials/MI_BRFacelessBot")
    assert mi_bot is not None, "MI_BRFacelessBot missing"
    assert mi_bot.parent == m_master, "MI_BRFacelessBot parent != M_BRFacelessPlaceholder"
    assert "BaseColor" in mi_bot.vector_parameter_values, "MI_BRFacelessBot missing BaseColor"
    bc_bot = mi_bot.vector_parameter_values["BaseColor"]
    assert abs(bc_bot.r - 0.70) < 0.02 and abs(bc_bot.g - 0.25) < 0.02 and abs(bc_bot.b - 0.15) < 0.02, \
        f"Bot BaseColor mismatch: {bc_bot}"
    assert abs(mi_bot.scalar_parameter_values.get("Roughness", 0.0) - 0.50) < 0.02, "Bot Roughness mismatch"
    assert abs(mi_bot.scalar_parameter_values.get("Metallic", 0.0) - 0.10) < 0.02, "Bot Metallic mismatch"

    res.pass_test({
        "manny_base_color": str(bc_manny),
        "bot_base_color": str(bc_bot),
        "parent_mat": m_master.get_name(),
    })


def test_char_anims_cdo_transform_and_wiring_invariants(res: TestResult):
    """Verify CDO SkeletalMeshComponent relative transform invariants (0, 0, -90) and (0, -90, 0)."""
    ok = setup_character_anims.setup_character_anims(force_dry_run=True, verbose=False)
    assert ok is True, "setup_character_anims returned False"

    asset_lib = setup_character_anims._MockEditorAssetLibrary.get_instance()

    for bp_name, expected_mat_name in [
        ("BP_BRCharacter", "MI_BRFacelessManny"),
        ("BP_BRAIBotCharacter", "MI_BRFacelessBot"),
    ]:
        bp = asset_lib.load_asset(f"/Game/Blueprints/{bp_name}")
        assert bp is not None, f"Failed to load {bp_name}"
        cdo = bp.cdo
        mesh = cdo.mesh

        # Check Location Invariant: (0, 0, -90)
        expected_loc = setup_character_anims._MockVector(0.0, 0.0, -90.0)
        assert mesh.relative_location == expected_loc, \
            f"{bp_name} mesh location {mesh.relative_location} != {expected_loc}"

        # Check Rotation Invariant: (0, -90, 0)
        expected_rot = setup_character_anims._MockRotator(0.0, -90.0, 0.0)
        assert mesh.relative_rotation == expected_rot, \
            f"{bp_name} mesh rotation {mesh.relative_rotation} != {expected_rot}"

        # Check Animation Mode & Anim Class
        assert mesh.animation_mode == "ANIMATION_BLUEPRINT", \
            f"{bp_name} animation_mode {mesh.animation_mode} != ANIMATION_BLUEPRINT"
        assert mesh.anim_class is not None and "ABP_BRCharacter" in mesh.anim_class.get_name(), \
            f"{bp_name} anim_class {mesh.anim_class} does not reference ABP_BRCharacter"

        # Check Material Override
        assert len(mesh.override_materials) > 0, f"{bp_name} has no override materials"
        mat = mesh.override_materials[0]
        assert mat.get_name() == expected_mat_name, \
            f"{bp_name} override material {mat.get_name()} != {expected_mat_name}"

    bp_char = asset_lib.load_asset("/Game/Blueprints/BP_BRCharacter")
    bp_bot = asset_lib.load_asset("/Game/Blueprints/BP_BRAIBotCharacter")
    res.pass_test({
        "BP_BRCharacter_loc": str(bp_char.cdo.mesh.relative_location),
        "BP_BRCharacter_rot": str(bp_char.cdo.mesh.relative_rotation),
        "BP_BRCharacter_anim_mode": bp_char.cdo.mesh.animation_mode,
        "BP_BRCharacter_mat": bp_char.cdo.mesh.override_materials[0].get_name(),
        "BP_BRAIBotCharacter_loc": str(bp_bot.cdo.mesh.relative_location),
        "BP_BRAIBotCharacter_rot": str(bp_bot.cdo.mesh.relative_rotation),
        "BP_BRAIBotCharacter_anim_mode": bp_bot.cdo.mesh.animation_mode,
        "BP_BRAIBotCharacter_mat": bp_bot.cdo.mesh.override_materials[0].get_name(),
    })


def test_char_anims_tier2_procedural_factory(res: TestResult):
    """Verify Tier-2 Procedural AnimBP Factory activates when template AnimBP is missing."""
    mock_u = setup_character_anims._MockUnrealModule()
    # Remove template ABP_Manny from registry to trigger Tier-2
    mock_u.EditorAssetLibrary._assets.pop("/Game/Characters/Mannequins/Animations/ABP_Manny", None)
    mock_u.EditorAssetLibrary._assets.pop("/Game/Characters/Mannequins/Animations/ABP_BRCharacter", None)

    skel = mock_u.EditorAssetLibrary.load_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin")
    abp_asset = setup_character_anims.setup_anim_blueprint(
        u=mock_u,
        skeleton_asset=skel,
        template_bp_path=None,
        verbose=True,
    )
    assert abp_asset is not None, "Tier-2 procedural AnimBP factory failed to create asset"
    assert abp_asset.get_name() == "ABP_BRCharacter"
    assert hasattr(abp_asset, "variables")
    assert "Speed" in abp_asset.variables
    assert "bIsFalling" in abp_asset.variables
    assert "bIsADS" in abp_asset.variables
    assert "CurrentMovementState" in abp_asset.variables

    res.pass_test({
        "tier2_asset_name": abp_asset.get_name(),
        "scaffolded_variables": list(abp_asset.variables.keys())
    })


# ==============================================================================
# MAIN TEST HARNESS RUNNER
# ==============================================================================

def main() -> int:
    print("======================================================================")
    print("=== [CHALLENGER 1] Adversarial Test Harness & Empirical Verification ===")
    print("======================================================================")

    runner = AdversarialTestRunner()

    # Suite 1: fetch_osm_data.py
    print("\n[SUITE 1] fetch_osm_data.py Adversarial & Invariant Tests:")
    runner.run("fetch_osm_data", "Projection Mathematics & Geodesy", test_fetch_projection_math)
    runner.run("fetch_osm_data", "Centroid Collinear & Degenerate", test_fetch_centroid_collinear_and_degenerate)
    runner.run("fetch_osm_data", "Height Synthesis 4-Tier Engine", test_fetch_height_synthesis_tiers)
    runner.run("fetch_osm_data", "Corrupt Geometry Points Handling", test_fetch_corrupt_geometry_points)
    runner.run("fetch_osm_data", "Nonexistent Cache File Fallback", test_fetch_nonexistent_cache)
    runner.run("fetch_osm_data", "Corrupt Cache Files Stress Test", test_fetch_corrupt_cache_files)
    runner.run("fetch_osm_data", "Offline Seed Schema & Types", test_fetch_offline_seed_schema_and_types)
    runner.run("fetch_osm_data", "Invalid CLI Arguments Rejection", test_fetch_invalid_cli_arguments)
    runner.run("fetch_osm_data", "Existing Level Data JSON Validation", test_validate_existing_level_data_json)

    # Suite 2: build_osm_level.py
    print("\n[SUITE 2] build_osm_level.py Adversarial & Invariant Tests:")
    runner.run("build_osm_level", "Rotating Calipers Degenerate Geometry", test_build_geometry_rotating_calipers_degenerates)
    runner.run("build_osm_level", "Missing GIS Data Fallback", test_build_missing_gis_data_fallback)
    runner.run("build_osm_level", "Malformed JSON Syntax Recovery", test_build_malformed_json_corrupt_syntax)
    runner.run("build_osm_level", "Missing Keys Invariant Protection", test_build_malformed_json_missing_keys_protection)
    runner.run("build_osm_level", "Degenerate Polygons Level Generation", test_build_degenerate_polygons_level_execution)
    runner.run("build_osm_level", "Road Micro-Segments Filter", test_build_road_micro_segments)
    runner.run("build_osm_level", "Rigorous Level Invariants Check", test_build_invariant_verification_rigorous)

    # Suite 3: setup_character_anims.py
    print("\n[SUITE 3] setup_character_anims.py Adversarial & Invariant Tests:")
    runner.run("setup_character_anims", "CLI Flags & Unrecognized Args", test_char_anims_cli_flags)
    runner.run("setup_character_anims", "Material Parameters Verification", test_char_anims_material_parameters)
    runner.run("setup_character_anims", "CDO Transform & Wiring Invariants", test_char_anims_cdo_transform_and_wiring_invariants)
    runner.run("setup_character_anims", "Tier-2 Procedural AnimBP Factory", test_char_anims_tier2_procedural_factory)

    summary = runner.summary()
    print("\n======================================================================")
    print(f"=== TEST RUN COMPLETE: {summary['passed']}/{summary['total']} PASSED ({summary['failed']} FAILED) ===")
    print("======================================================================")

    # Write test report json to challenger_1 directory
    report_path = os.path.join(os.path.dirname(__file__), "test_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": summary,
            "results": [
                {
                    "category": r.category,
                    "name": r.name,
                    "passed": r.passed,
                    "error_msg": r.error_msg,
                    "details": r.details,
                }
                for r in runner.results
            ]
        }, f, indent=2)
    print(f"Saved machine-readable test results to: {report_path}")

    return 0 if summary["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
