"""
generate_map.py — Automated Map & Environment Generation for Bakirkoy BR.

Procedurally generates the Bakirkoy Battle Royale level (/Game/Maps/BakirkoyMap.umap)
using the Unreal Engine 5 Python API, adhering to all project constraints:
- 200m x 200m walkable arena floor at Z=-50 with BlockAll collision.
- 4 perimeter boundary walls enclosing the 200m x 200m arena.
- 4 solid exterior commercial buildings (Constraint C1: No interiors).
- 4 external rooftop access ramps connecting streets to building rooftops.
- 6 tactical street cover obstacles for AI combat positioning.
- EXACTLY 1 NavMeshBoundsVolume covering ground, ramps, and rooftops (240m x 240m x 60m).
- 13 tactical loot spawners tagged "Loot" and "WeaponPickup" in open-sky exterior areas.
- EXACTLY 10 PlayerStart actors arranged in a 75m perimeter circle facing the arena center.
- Persists level asset as .umap via LevelEditorSubsystem and EditorAssetSubsystem.
- Includes safe import wrapper with standalone dry-run simulation execution.
"""

from __future__ import annotations

import argparse
import math
import sys
from typing import Any, Dict, List, Optional, Tuple

# Safe import wrapper for Unreal Engine environment
try:
    import unreal
except ImportError:
    unreal = None


# ==============================================================================
# Standalone Simulation & Mock Environment (Used when UE5 is not installed)
# ==============================================================================

class _MockVector:
    """Mock Vector mirroring unreal.Vector."""

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self) -> str:
        return f"Vector(X={self.x:.1f}, Y={self.y:.1f}, Z={self.z:.1f})"


class _MockRotator:
    """Mock Rotator mirroring unreal.Rotator."""

    def __init__(self, pitch: float = 0.0, yaw: float = 0.0, roll: float = 0.0):
        self.pitch = float(pitch)
        self.yaw = float(yaw)
        self.roll = float(roll)

    def __repr__(self) -> str:
        return f"Rotator(Pitch={self.pitch:.1f}, Yaw={self.yaw:.1f}, Roll={self.roll:.1f})"


class _MockStaticMeshComponent:
    """Mock StaticMeshComponent for setting mesh and collision profile."""

    def __init__(self):
        self.static_mesh = None
        self.collision_profile_name = "BlockAll"

    def set_editor_property(self, prop_name: str, value: Any) -> None:
        if prop_name == "static_mesh":
            self.static_mesh = value

    def set_collision_profile_name(self, profile: str) -> None:
        self.collision_profile_name = profile


class _MockActor:
    """Base mock actor mirroring AActor in Unreal Engine."""

    def __init__(self, location: Optional[_MockVector] = None, rotation: Optional[_MockRotator] = None):
        self.location = location or _MockVector()
        self.rotation = rotation or _MockRotator()
        self.scale = _MockVector(1.0, 1.0, 1.0)
        self.label = ""
        self.tags: List[str] = []
        self.static_mesh_component = _MockStaticMeshComponent()

    def set_actor_label(self, label: str) -> None:
        self.label = label

    def get_actor_label(self) -> str:
        return self.label

    def set_actor_scale3d(self, scale: _MockVector) -> None:
        self.scale = scale

    def get_actor_scale3d(self) -> _MockVector:
        return self.scale

    def get_actor_location(self) -> _MockVector:
        return self.location

    def get_actor_rotation(self) -> _MockRotator:
        return self.rotation


class _MockStaticMeshActor(_MockActor):
    pass


class _MockNavMeshBoundsVolume(_MockActor):
    pass


class _MockPlayerStart(_MockActor):
    pass


class _MockEditorActorSubsystem:
    def __init__(self):
        self.actors: List[_MockActor] = []

    def spawn_actor_from_class(
        self, actor_class: Any, location: _MockVector, rotation: _MockRotator
    ) -> _MockActor:
        actor = actor_class(location=location, rotation=rotation)
        self.actors.append(actor)
        return actor

    def get_all_level_actors(self) -> List[_MockActor]:
        return list(self.actors)


class _MockLevelEditorSubsystem:
    def __init__(self, actor_subsystem: Optional[_MockEditorActorSubsystem] = None):
        self.current_level = ""
        self.actor_subsystem = actor_subsystem

    def new_level(self, asset_path: str) -> bool:
        self.current_level = asset_path
        if self.actor_subsystem is not None:
            self.actor_subsystem.actors.clear()
        return True

    def save_current_level(self) -> bool:
        return True


class _MockEditorAssetSubsystem:
    def save_asset(self, asset_path: str, only_if_is_dirty: bool = False) -> bool:
        return True


class _MockEditorAssetLibrary:
    @staticmethod
    def does_directory_exist(directory_path: str) -> bool:
        return True

    @staticmethod
    def make_directory(directory_path: str) -> bool:
        return True

    @staticmethod
    def load_asset(asset_path: str) -> Any:
        return f"StaticMesh'{asset_path}'"

    @staticmethod
    def save_asset(asset_path: str, only_if_is_dirty: bool = False) -> bool:
        return True


class _MockEditorLevelLibrary:
    @staticmethod
    def new_level(asset_path: str) -> bool:
        return True

    @staticmethod
    def save_current_level() -> bool:
        return True


class _MockUnrealModule:
    """Mock Unreal Engine Python module for standalone CLI verification and testing."""

    def __init__(self):
        self.Vector = _MockVector
        self.Rotator = _MockRotator
        self.StaticMeshActor = _MockStaticMeshActor
        self.NavMeshBoundsVolume = _MockNavMeshBoundsVolume
        self.PlayerStart = _MockPlayerStart

        self.LevelEditorSubsystem = _MockLevelEditorSubsystem
        self.EditorActorSubsystem = _MockEditorActorSubsystem
        self.EditorAssetSubsystem = _MockEditorAssetSubsystem

        self.EditorAssetLibrary = _MockEditorAssetLibrary
        self.EditorLevelLibrary = _MockEditorLevelLibrary

        self._actor_subsystem = _MockEditorActorSubsystem()
        self._level_subsystem = _MockLevelEditorSubsystem(actor_subsystem=self._actor_subsystem)
        self._asset_subsystem = _MockEditorAssetSubsystem()

    def get_editor_subsystem(self, subsystem_class: Any) -> Any:
        if subsystem_class == self.LevelEditorSubsystem:
            return self._level_subsystem
        elif subsystem_class == self.EditorActorSubsystem:
            return self._actor_subsystem
        elif subsystem_class == self.EditorAssetSubsystem:
            return self._asset_subsystem
        return None

    @staticmethod
    def log(msg: str) -> None:
        print(f"[BakirkoyBR][LOG] {msg}")

    @staticmethod
    def log_warning(msg: str) -> None:
        print(f"[BakirkoyBR][WARNING] {msg}")

    @staticmethod
    def log_error(msg: str) -> None:
        print(f"[BakirkoyBR][ERROR] {msg}")


# Module-level state tracking for tests and external inspection
LAST_GENERATED_ACTORS: List[Any] = []
LAST_GENERATION_MANIFEST: Dict[str, Any] = {}


# ==============================================================================
# Helper Functions
# ==============================================================================

def get_subsystems(u: Any) -> Tuple[Optional[Any], Optional[Any], Optional[Any]]:
    """Retrieve editor subsystems with fallback handling."""
    level_sub = None
    actor_sub = None
    asset_sub = None

    if hasattr(u, "get_editor_subsystem"):
        try:
            level_sub = u.get_editor_subsystem(u.LevelEditorSubsystem)
        except Exception:
            level_sub = None
        try:
            actor_sub = u.get_editor_subsystem(u.EditorActorSubsystem)
        except Exception:
            actor_sub = None
        try:
            asset_sub = u.get_editor_subsystem(u.EditorAssetSubsystem)
        except Exception:
            asset_sub = None

    return level_sub, actor_sub, asset_sub


def spawn_actor(
    u: Any,
    actor_sub: Optional[Any],
    actor_class: Any,
    location: Any,
    rotation: Any
) -> Optional[Any]:
    """Spawns an actor using EditorActorSubsystem with EditorLevelLibrary fallback."""
    if actor_sub and hasattr(actor_sub, "spawn_actor_from_class"):
        return actor_sub.spawn_actor_from_class(actor_class, location, rotation)
    elif hasattr(u, "EditorLevelLibrary") and hasattr(u.EditorLevelLibrary, "spawn_actor_from_class"):
        return u.EditorLevelLibrary.spawn_actor_from_class(actor_class, location, rotation)
    return None


def get_all_actors(u: Any, actor_sub: Optional[Any]) -> List[Any]:
    """Retrieves all level actors using EditorActorSubsystem with EditorLevelLibrary fallback."""
    if actor_sub and hasattr(actor_sub, "get_all_level_actors"):
        return actor_sub.get_all_level_actors()
    elif hasattr(u, "EditorLevelLibrary") and hasattr(u.EditorLevelLibrary, "get_all_level_actors"):
        return u.EditorLevelLibrary.get_all_level_actors()
    return []


def configure_static_mesh_actor(
    actor: Any,
    mesh_asset: Any,
    label: str,
    scale: Any,
    collision_profile: str = "BlockAll",
    tags: Optional[List[str]] = None
) -> None:
    """Configures label, scale, static mesh, collision profile, and tags for a StaticMeshActor."""
    if not actor:
        return

    actor.set_actor_label(label)
    actor.set_actor_scale3d(scale)

    mesh_comp = getattr(actor, "static_mesh_component", None)
    if mesh_comp:
        if mesh_asset:
            if hasattr(mesh_comp, "set_editor_property"):
                mesh_comp.set_editor_property("static_mesh", mesh_asset)
            elif hasattr(mesh_comp, "set_static_mesh"):
                mesh_comp.set_static_mesh(mesh_asset)
        if hasattr(mesh_comp, "set_collision_profile_name"):
            mesh_comp.set_collision_profile_name(collision_profile)

    if tags and hasattr(actor, "tags"):
        for tag in tags:
            actor.tags.append(tag)


def verify_level_invariants(all_actors: List[Any], u: Any) -> Tuple[bool, Dict[str, int]]:
    """
    Validates that the generated level adheres to all Bakirkoy BR requirements:
    - EXACTLY 1 NavMeshBoundsVolume
    - EXACTLY 10 PlayerStarts
    - At least 10 Loot Spawners tagged 'Loot' and 'WeaponPickup'
    """
    nav_count = 0
    ps_count = 0
    loot_count = 0
    floor_count = 0
    wall_count = 0
    building_count = 0
    ramp_count = 0
    cover_count = 0

    for actor in all_actors:
        # Check NavMeshBoundsVolume
        is_nav = False
        if hasattr(u, "NavMeshBoundsVolume") and isinstance(actor, u.NavMeshBoundsVolume):
            is_nav = True
        elif "NavMeshBounds" in getattr(actor, "tags", []):
            is_nav = True
        elif hasattr(actor, "get_class") and actor.get_class().get_name() == "NavMeshBoundsVolume":
            is_nav = True

        if is_nav:
            nav_count += 1

        # Check PlayerStart
        is_ps = False
        if hasattr(u, "PlayerStart") and isinstance(actor, u.PlayerStart):
            is_ps = True
        elif "PlayerStart" in getattr(actor, "tags", []):
            is_ps = True
        elif hasattr(actor, "get_class") and actor.get_class().get_name() == "PlayerStart":
            is_ps = True

        if is_ps:
            ps_count += 1

        # Check Tags
        tags = getattr(actor, "tags", [])
        if "Loot" in tags or "WeaponPickup" in tags:
            loot_count += 1
        if "Floor" in tags:
            floor_count += 1
        if "ExteriorWall" in tags:
            wall_count += 1
        if "Building" in tags:
            building_count += 1
        if "ExternalRamp" in tags:
            ramp_count += 1
        if "Cover" in tags:
            cover_count += 1

    counts = {
        "nav_bounds": nav_count,
        "player_starts": ps_count,
        "loot_spawners": loot_count,
        "floors": floor_count,
        "walls": wall_count,
        "buildings": building_count,
        "ramps": ramp_count,
        "covers": cover_count,
        "total_actors": len(all_actors),
    }

    b_pass = True
    if nav_count != 1:
        u.log_error(f"INVARIANT VIOLATION: Expected exactly 1 NavMeshBoundsVolume, found {nav_count}")
        b_pass = False
    if ps_count != 10:
        u.log_error(f"INVARIANT VIOLATION: Expected exactly 10 PlayerStarts, found {ps_count}")
        b_pass = False
    if loot_count < 10:
        u.log_error(f"INVARIANT VIOLATION: Expected at least 10 Loot Spawners, found {loot_count}")
        b_pass = False

    return b_pass, counts


# ==============================================================================
# Main Level Generation Function
# ==============================================================================

def generate_map(
    map_path: str = "/Game/Maps/BakirkoyMap",
    dry_run: bool = False,
    unreal_module: Optional[Any] = None
) -> bool:
    """
    Main automated map generation procedure.
    Enforces all Bakirkoy BR constraints (C1 Exterior Only, 10 PlayerStarts, 1 NavMeshBoundsVolume).

    Args:
        map_path: Target asset path for the level (.umap)
        dry_run: If True or if unreal is not available, runs standalone simulation.
        unreal_module: Optional custom or mock unreal module instance for testing.

    Returns:
        bool: True if generation and verification succeed, False otherwise.
    """
    if unreal_module is not None:
        u = unreal_module
        is_simulation = True
    else:
        is_simulation = dry_run or (unreal is None)
        u = _MockUnrealModule() if is_simulation else unreal

    mode_str = "STANDALONE SIMULATION" if is_simulation else "UE5 EDITOR"
    u.log(f"=== [Bakirkoy BR] Starting Automated Map Generation ({mode_str}) ===")
    u.log(f"Target Level Path: {map_path}")

    level_sub, actor_sub, asset_sub = get_subsystems(u)

    # 1. Ensure Target Directory Exists
    folder_path = "/".join(map_path.split("/")[:-1])
    if folder_path and hasattr(u, "EditorAssetLibrary") and hasattr(u.EditorAssetLibrary, "does_directory_exist"):
        if not u.EditorAssetLibrary.does_directory_exist(folder_path):
            u.EditorAssetLibrary.make_directory(folder_path)
            u.log(f"Created map directory: {folder_path}")

    # 2. Create New Blank Level
    u.log(f"Creating new blank level at: {map_path}")
    b_created = False
    if level_sub and hasattr(level_sub, "new_level"):
        b_created = level_sub.new_level(map_path)
    elif hasattr(u, "EditorLevelLibrary") and hasattr(u.EditorLevelLibrary, "new_level"):
        b_created = u.EditorLevelLibrary.new_level(map_path)

    if not b_created:
        u.log_error(f"Failed to create new level at: {map_path}")
        return False

    # Load standard basic shape cube mesh for graybox prototyping
    cube_mesh = None
    if hasattr(u, "EditorAssetLibrary") and hasattr(u.EditorAssetLibrary, "load_asset"):
        cube_mesh = u.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
        if not cube_mesh:
            u.log_warning("Cube mesh /Engine/BasicShapes/Cube.Cube could not be loaded; continuing with default geometry.")

    # 3. Spawn Floor (200m x 200m arena centered at 0, 0, -50, top surface at Z=0)
    floor_loc = u.Vector(0.0, 0.0, -50.0)
    floor_rot = u.Rotator(0.0, 0.0, 0.0)
    floor_scale = u.Vector(200.0, 200.0, 1.0)

    floor_actor = spawn_actor(u, actor_sub, u.StaticMeshActor, floor_loc, floor_rot)
    if floor_actor:
        configure_static_mesh_actor(
            floor_actor,
            cube_mesh,
            label="Floor_Main_200m",
            scale=floor_scale,
            collision_profile="BlockAll",
            tags=["Floor"]
        )
        u.log("Spawned Main Walkable Floor (200m x 200m, BlockAll collision)")
    else:
        u.log_error("Failed to spawn main floor actor!")
        return False

    # 4. Spawn 4 Exterior Perimeter Boundary Walls (North, South, East, West)
    wall_configs = [
        ("Wall_North_Boundary", u.Vector(10000.0, 0.0, 1000.0), u.Vector(2.0, 200.0, 20.0)),
        ("Wall_South_Boundary", u.Vector(-10000.0, 0.0, 1000.0), u.Vector(2.0, 200.0, 20.0)),
        ("Wall_East_Boundary",  u.Vector(0.0, 10000.0, 1000.0), u.Vector(200.0, 2.0, 20.0)),
        ("Wall_West_Boundary",  u.Vector(0.0, -10000.0, 1000.0), u.Vector(200.0, 2.0, 20.0)),
    ]
    for label, loc, scale in wall_configs:
        wall_actor = spawn_actor(u, actor_sub, u.StaticMeshActor, loc, u.Rotator(0.0, 0.0, 0.0))
        if wall_actor:
            configure_static_mesh_actor(
                wall_actor,
                cube_mesh,
                label=label,
                scale=scale,
                collision_profile="BlockAll",
                tags=["ExteriorWall"]
            )
    u.log("Spawned 4 Exterior Perimeter Boundary Walls (200m enclosure, 20m height)")

    # 5. Spawn EXACTLY 1 NavMeshBoundsVolume (Requirement R1 / AC Verification)
    # Extent: 240m x 240m x 60m covering ground, ramps, and building rooftops up to 40m
    nav_volume = spawn_actor(
        u,
        actor_sub,
        u.NavMeshBoundsVolume,
        u.Vector(0.0, 0.0, 1000.0),
        u.Rotator(0.0, 0.0, 0.0)
    )
    if nav_volume:
        nav_volume.set_actor_label("NavMeshBoundsVolume_Main")
        nav_volume.set_actor_scale3d(u.Vector(120.0, 120.0, 30.0))
        if hasattr(nav_volume, "tags"):
            nav_volume.tags.append("NavMeshBounds")
        u.log("Spawned EXACTLY 1 NavMeshBoundsVolume (240m x 240m x 60m bounds)")
    else:
        u.log_error("Failed to spawn NavMeshBoundsVolume!")
        return False

    # 6. Spawn Solid Exterior Urban Buildings (Constraint C1: No Interiors)
    # 4 commercial blocks (40m x 40m x 12m) with flat, traversable rooftops at Z=1200
    building_configs = [
        ("Building_Block_NE", u.Vector(4000.0, 4000.0, 600.0), u.Vector(40.0, 40.0, 12.0)),
        ("Building_Block_NW", u.Vector(-4000.0, 4000.0, 600.0), u.Vector(40.0, 40.0, 12.0)),
        ("Building_Block_SE", u.Vector(4000.0, -4000.0, 600.0), u.Vector(40.0, 40.0, 12.0)),
        ("Building_Block_SW", u.Vector(-4000.0, -4000.0, 600.0), u.Vector(40.0, 40.0, 12.0)),
    ]
    for label, loc, scale in building_configs:
        bld_actor = spawn_actor(u, actor_sub, u.StaticMeshActor, loc, u.Rotator(0.0, 0.0, 0.0))
        if bld_actor:
            configure_static_mesh_actor(
                bld_actor,
                cube_mesh,
                label=label,
                scale=scale,
                collision_profile="BlockAll",
                tags=["Building"]
            )
    u.log("Spawned 4 Solid Exterior Building Blocks (Constraint C1: No Interiors)")

    # 7. Spawn External Rooftop Access Ramps (Connecting Streets to Rooftops)
    ramp_configs = [
        ("Ramp_Access_NE", u.Vector(4000.0, 1500.0, 600.0), u.Rotator(26.5, 90.0, 0.0), u.Vector(26.0, 4.0, 0.5)),
        ("Ramp_Access_NW", u.Vector(-4000.0, 1500.0, 600.0), u.Rotator(26.5, 90.0, 0.0), u.Vector(26.0, 4.0, 0.5)),
        ("Ramp_Access_SE", u.Vector(4000.0, -1500.0, 600.0), u.Rotator(-26.5, 90.0, 0.0), u.Vector(26.0, 4.0, 0.5)),
        ("Ramp_Access_SW", u.Vector(-4000.0, -1500.0, 600.0), u.Rotator(-26.5, 90.0, 0.0), u.Vector(26.0, 4.0, 0.5)),
    ]
    for label, loc, rot, scale in ramp_configs:
        ramp_actor = spawn_actor(u, actor_sub, u.StaticMeshActor, loc, rot)
        if ramp_actor:
            configure_static_mesh_actor(
                ramp_actor,
                cube_mesh,
                label=label,
                scale=scale,
                collision_profile="BlockAll",
                tags=["ExternalRamp"]
            )
    u.log("Spawned 4 External Rooftop Access Ramps")

    # 8. Spawn Tactical Street Cover Obstacles (Concrete Barriers for AI Cover Checks)
    cover_configs = [
        ("Cover_Barrier_NorthPlaza", u.Vector(0.0, 2500.0, 60.0),  u.Vector(3.0, 1.0, 1.2)),
        ("Cover_Barrier_SouthPlaza", u.Vector(0.0, -2500.0, 60.0), u.Vector(3.0, 1.0, 1.2)),
        ("Cover_Barrier_EastAvenue",  u.Vector(2500.0, 0.0, 60.0),  u.Vector(1.0, 3.0, 1.2)),
        ("Cover_Barrier_WestAvenue",  u.Vector(-2500.0, 0.0, 60.0), u.Vector(1.0, 3.0, 1.2)),
        ("Cover_Barrier_Center_1",   u.Vector(700.0, 700.0, 60.0),  u.Vector(2.0, 2.0, 1.2)),
        ("Cover_Barrier_Center_2",   u.Vector(-700.0, -700.0, 60.0), u.Vector(2.0, 2.0, 1.2)),
    ]
    for label, loc, scale in cover_configs:
        cov_actor = spawn_actor(u, actor_sub, u.StaticMeshActor, loc, u.Rotator(0.0, 0.0, 0.0))
        if cov_actor:
            configure_static_mesh_actor(
                cov_actor,
                cube_mesh,
                label=label,
                scale=scale,
                collision_profile="BlockAll",
                tags=["Cover"]
            )
    u.log("Spawned 6 Tactical Street Cover Obstacles")

    # 9. Spawn Tactical Loot Spawners (Rooftops, Alleys, Junctions)
    # Compatible with BRAIController::FindNearestLoot ("Loot", "WeaponPickup")
    loot_spawns = [
        # Rooftops (Z = 1250: Open sky above, 12m building + 0.5m crate)
        ("LootSpawner_Rooftop_NE", u.Vector(4000.0, 4000.0, 1250.0)),
        ("LootSpawner_Rooftop_NW", u.Vector(-4000.0, 4000.0, 1250.0)),
        ("LootSpawner_Rooftop_SE", u.Vector(4000.0, -4000.0, 1250.0)),
        ("LootSpawner_Rooftop_SW", u.Vector(-4000.0, -4000.0, 1250.0)),
        # Narrow Alleys (Z = 50: Ground level)
        ("LootSpawner_Alley_North", u.Vector(0.0, 5000.0, 50.0)),
        ("LootSpawner_Alley_South", u.Vector(0.0, -5000.0, 50.0)),
        ("LootSpawner_Alley_East",  u.Vector(5000.0, 0.0, 50.0)),
        ("LootSpawner_Alley_West",  u.Vector(-5000.0, 0.0, 50.0)),
        # Street Junctions & Plaza (Z = 50)
        ("LootSpawner_Plaza_Center", u.Vector(0.0, 0.0, 50.0)),
        ("LootSpawner_Junction_NE",  u.Vector(2000.0, 2000.0, 50.0)),
        ("LootSpawner_Junction_NW",  u.Vector(-2000.0, 2000.0, 50.0)),
        ("LootSpawner_Junction_SE",  u.Vector(2000.0, -2000.0, 50.0)),
        ("LootSpawner_Junction_SW",  u.Vector(-2000.0, -2000.0, 50.0)),
    ]
    for label, loc in loot_spawns:
        loot_actor = spawn_actor(u, actor_sub, u.StaticMeshActor, loc, u.Rotator(0.0, 0.0, 0.0))
        if loot_actor:
            configure_static_mesh_actor(
                loot_actor,
                cube_mesh,
                label=label,
                scale=u.Vector(0.8, 0.8, 0.6),
                collision_profile="BlockAll",
                tags=["Loot", "WeaponPickup"]
            )
    u.log(f"Spawned {len(loot_spawns)} Tactical Loot Spawners (Tagged 'Loot', 'WeaponPickup')")

    # 10. Spawn EXACTLY 10 PlayerStart Actors (Requirement R1 / AC Verification)
    # Circle perimeter distribution (R=75m, Z=100) facing arena center
    num_player_starts = 10
    radius = 7500.0  # 75 meters from center
    spawn_z = 100.0  # 1 meter above floor to prevent collision clipping
    spawned_ps_count = 0

    for i in range(num_player_starts):
        angle_rad = (2.0 * math.pi * i) / num_player_starts
        x = radius * math.cos(angle_rad)
        y = radius * math.sin(angle_rad)
        # Inward facing orientation toward center (0, 0)
        yaw = (math.degrees(angle_rad) + 180.0) % 360.0

        ps_actor = spawn_actor(
            u,
            actor_sub,
            u.PlayerStart,
            u.Vector(x, y, spawn_z),
            u.Rotator(0.0, yaw, 0.0)
        )
        if ps_actor:
            ps_actor.set_actor_label(f"PlayerStart_{i}")
            if hasattr(ps_actor, "tags"):
                ps_actor.tags.append("PlayerStart")
            spawned_ps_count += 1

    u.log(f"Spawned EXACTLY {spawned_ps_count} PlayerStart actors (Circle R=75m, inward-facing)")

    # 11. Level Content Invariant Verification
    all_actors = get_all_actors(u, actor_sub)
    b_valid, counts = verify_level_invariants(all_actors, u)

    u.log("=== [Bakirkoy BR] Level Content Manifest ===")
    u.log(f"  Total Actors Spawned:   {counts['total_actors']}")
    u.log(f"  NavMeshBoundsVolume:    {counts['nav_bounds']} (Required: 1)")
    u.log(f"  PlayerStart Actors:     {counts['player_starts']} (Required: 10)")
    u.log(f"  Loot Spawners:          {counts['loot_spawners']} (Required: >=10)")
    u.log(f"  Walkable Floor:         {counts['floors']}")
    u.log(f"  Perimeter Walls:        {counts['walls']}")
    u.log(f"  Solid Buildings (C1):   {counts['buildings']}")
    u.log(f"  Rooftop Access Ramps:   {counts['ramps']}")
    u.log(f"  Street Cover Barriers:  {counts['covers']}")

    if not b_valid:
        u.log_error("VERIFICATION FAILED: Level content does not meet required invariants!")
        return False

    # 12. Save Level Asset (.umap)
    u.log(f"Persisting level asset to {map_path}.umap...")
    b_saved = False
    if level_sub and hasattr(level_sub, "save_current_level"):
        b_saved = level_sub.save_current_level()
    elif hasattr(u, "EditorLevelLibrary") and hasattr(u.EditorLevelLibrary, "save_current_level"):
        b_saved = u.EditorLevelLibrary.save_current_level()

    # Explicit package asset save
    if asset_sub and hasattr(asset_sub, "save_asset"):
        asset_sub.save_asset(map_path, only_if_is_dirty=False)
    elif hasattr(u, "EditorAssetLibrary") and hasattr(u.EditorAssetLibrary, "save_asset"):
        u.EditorAssetLibrary.save_asset(map_path, only_if_is_dirty=False)

    # Record state for external test fixtures and audit inspection
    LAST_GENERATED_ACTORS.clear()
    LAST_GENERATED_ACTORS.extend(all_actors)
    LAST_GENERATION_MANIFEST.clear()
    LAST_GENERATION_MANIFEST.update(counts)

    u.log(f"=== [Bakirkoy BR] Successfully Generated and Verified Level: {map_path} ===")
    return True


# ==============================================================================
# CLI Entrypoint
# ==============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Map Generation for Bakirkoy BR (UE5)")
    parser.add_argument(
        "--map-path",
        default="/Game/Maps/BakirkoyMap",
        help="Target Unreal package path for the map asset (default: /Game/Maps/BakirkoyMap)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Force standalone simulation mode (automatically active if unreal module is missing)"
    )

    args, _ = parser.parse_known_args()
    b_success = generate_map(map_path=args.map_path, dry_run=args.dry_run)
    sys.exit(0 if b_success else 1)
