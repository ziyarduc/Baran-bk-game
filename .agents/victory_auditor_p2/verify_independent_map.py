import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import math
import generate_map

# Run map generation in simulation mode
success = generate_map.generate_map(map_path="/Game/Maps/BakirkoyMap", dry_run=True)
assert success, "generate_map failed!"

actors = generate_map.LAST_GENERATED_ACTORS
manifest = generate_map.LAST_GENERATION_MANIFEST

print(f"[AUDIT] Verifying Generated Actors Manifest: {manifest}")

# 1. Total actors check
assert manifest['total_actors'] == 43, f"Expected 43 actors, got {manifest['total_actors']}"
print("  [PASS] Total actors count is 43.")

# 2. NavMeshBoundsVolume check
assert manifest['nav_bounds'] == 1, f"Expected exactly 1 NavMeshBoundsVolume, got {manifest['nav_bounds']}"
nav_actor = next(a for a in actors if "NavMeshBounds" in getattr(a, 'tags', []))
assert nav_actor.scale.x == 120.0 and nav_actor.scale.y == 120.0 and nav_actor.scale.z == 30.0, f"Incorrect NavMesh scale: {nav_actor.scale}"
print(f"  [PASS] Exactly 1 NavMeshBoundsVolume with scale (120, 120, 30) = 240m x 240m x 60m.")

# 3. PlayerStart actors check
assert manifest['player_starts'] == 10, f"Expected exactly 10 PlayerStarts, got {manifest['player_starts']}"
ps_actors = [a for a in actors if "PlayerStart" in getattr(a, 'tags', [])]
assert len(ps_actors) == 10
radius = 7500.0
for i, ps in enumerate(ps_actors):
    # Check radius from center
    dist = math.sqrt(ps.location.x**2 + ps.location.y**2)
    assert abs(dist - radius) < 1.0, f"PlayerStart {i} distance {dist} not equal to {radius}"
    # Check elevation
    assert ps.location.z == 100.0, f"PlayerStart {i} Z elevation {ps.location.z} != 100.0"
    # Check inward facing yaw
    angle_rad = (2.0 * math.pi * i) / 10
    expected_yaw = (math.degrees(angle_rad) + 180.0) % 360.0
    assert abs(ps.rotation.yaw - expected_yaw) < 0.01, f"PlayerStart {i} yaw {ps.rotation.yaw} != {expected_yaw}"
print(f"  [PASS] Exactly 10 PlayerStart actors arranged in a 75m circle at Z=100 facing inward.")

# 4. Loot Spawners check
assert manifest['loot_spawners'] == 13, f"Expected 13 loot spawners, got {manifest['loot_spawners']}"
loot_actors = [a for a in actors if "Loot" in getattr(a, 'tags', [])]
assert len(loot_actors) == 13
for loot in loot_actors:
    assert "WeaponPickup" in loot.tags, f"Loot actor {loot.label} missing 'WeaponPickup' tag"
    # Verify open sky (either rooftop Z=1250 or ground Z=50)
    assert loot.location.z in (50.0, 1250.0), f"Loot actor {loot.label} at unexpected Z: {loot.location.z}"
print(f"  [PASS] Exactly 13 Loot Spawners dual-tagged ('Loot', 'WeaponPickup') at open-sky locations.")

# 5. Floor check
floor_actors = [a for a in actors if "Floor" in getattr(a, 'tags', [])]
assert len(floor_actors) == 1
floor = floor_actors[0]
assert floor.location.z == -50.0 and floor.scale.x == 200.0 and floor.scale.y == 200.0
assert floor.static_mesh_component.collision_profile_name == "BlockAll"
print(f"  [PASS] Floor is 200m x 200m at Z=-50 with BlockAll collision.")

# 6. Exterior Walls check
wall_actors = [a for a in actors if "ExteriorWall" in getattr(a, 'tags', [])]
assert len(wall_actors) == 4
for w in wall_actors:
    assert w.static_mesh_component.collision_profile_name == "BlockAll"
    assert w.scale.z == 20.0  # 20m tall
print(f"  [PASS] 4 Exterior perimeter boundary walls with BlockAll collision and 20m height.")

# 7. Solid Buildings & Ramps check
bld_actors = [a for a in actors if "Building" in getattr(a, 'tags', [])]
assert len(bld_actors) == 4
for b in bld_actors:
    assert b.scale.x == 40.0 and b.scale.y == 40.0 and b.scale.z == 12.0  # 40m x 40m x 12m
ramp_actors = [a for a in actors if "ExternalRamp" in getattr(a, 'tags', [])]
assert len(ramp_actors) == 4
for r in ramp_actors:
    assert abs(abs(r.rotation.pitch) - 26.5) < 0.1
print(f"  [PASS] 4 Solid buildings (C1 compliant) and 4 external rooftop access ramps (26.5 deg).")

print("[ALL MAP INVARIANT AUDITS PASSED WITH FLYING COLORS]")
