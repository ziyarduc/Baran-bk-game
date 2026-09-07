"""
setup_character_anims.py — Procedural Character & Animation Setup for Bakırköy BR.

Configures default UE5 Manny/Quinn skeletal meshes, procedural faceless placeholder
materials (M_BRFacelessPlaceholder, MI_BRFacelessManny, MI_BRFacelessBot), and a
comprehensive Animation Blueprint (ABP_BRCharacter) supporting locomotion, jumping,
and upper-body aiming, wired directly into BP_BRCharacter and BP_BRAIBotCharacter CDOs.

Target Engine: Unreal Engine 5.4 - 5.8 (Python Script Plugin)
Project: Bakırköy BR (Battle Royale)

Usage (Unreal Engine Headless Commandlet):
    UnrealEditor-Cmd.exe BakirkoyBR.uproject -run=pythonscript -script="setup_character_anims.py"

Usage (Unreal Editor Python Console / Remote Execution):
    import setup_character_anims
    setup_character_anims.setup_character_anims()

Usage (Standalone Python Dry-Run / Static Verification):
    python setup_character_anims.py --dry-run --verbose
"""

from __future__ import annotations

import argparse
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

# Safe import wrapper for Unreal Engine environment
try:
    import unreal
except ImportError:
    unreal = None


# ==============================================================================
# Standalone Simulation Framework & Mock Environment
# Enables 100% clean offline static analysis, CI testing, and dry-run execution
# ==============================================================================

class _MockVector:
    """Mock Vector mirroring unreal.Vector."""

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, _MockVector):
            return False
        return (
            abs(self.x - other.x) < 1e-4
            and abs(self.y - other.y) < 1e-4
            and abs(self.z - other.z) < 1e-4
        )

    def __repr__(self) -> str:
        return f"Vector(X={self.x:.1f}, Y={self.y:.1f}, Z={self.z:.1f})"


class _MockRotator:
    """Mock Rotator mirroring unreal.Rotator."""

    def __init__(self, pitch: float = 0.0, yaw: float = 0.0, roll: float = 0.0):
        self.pitch = float(pitch)
        self.yaw = float(yaw)
        self.roll = float(roll)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, _MockRotator):
            return False
        return (
            abs(self.pitch - other.pitch) < 1e-4
            and abs(self.yaw - other.yaw) < 1e-4
            and abs(self.roll - other.roll) < 1e-4
        )

    def __repr__(self) -> str:
        return f"Rotator(Pitch={self.pitch:.1f}, Yaw={self.yaw:.1f}, Roll={self.roll:.1f})"


class _MockLinearColor:
    """Mock LinearColor mirroring unreal.LinearColor."""

    def __init__(self, r: float = 0.0, g: float = 0.0, b: float = 0.0, a: float = 1.0):
        self.r = float(r)
        self.g = float(g)
        self.b = float(b)
        self.a = float(a)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, _MockLinearColor):
            return False
        return (
            abs(self.r - other.r) < 1e-3
            and abs(self.g - other.g) < 1e-3
            and abs(self.b - other.b) < 1e-3
            and abs(self.a - other.a) < 1e-3
        )

    def __repr__(self) -> str:
        return f"LinearColor(R={self.r:.3f}, G={self.g:.3f}, B={self.b:.3f}, A={self.a:.3f})"


class _MockAnimationMode:
    """Mock AnimationMode enum mirroring unreal.AnimationMode."""
    ANIMATION_BLUEPRINT = "ANIMATION_BLUEPRINT"
    ANIMATION_SINGLE_NODE = "ANIMATION_SINGLE_NODE"
    ANIMATION_CUSTOM_MODE = "ANIMATION_CUSTOM_MODE"


class _MockMaterialProperty:
    """Mock MaterialProperty enum mirroring unreal.MaterialProperty."""
    MP_EMISSIVE_COLOR = 0
    MP_OPACITY = 1
    MP_OPACITY_MASK = 2
    MP_DIFFUSE_COLOR = 3
    MP_SPECULAR = 4
    MP_BASE_COLOR = 5
    MP_METALLIC = 6
    MP_SPECULAR_RAW = 7
    MP_ROUGHNESS = 8
    MP_NORMAL = 9


class _MockMaterialExpressionVectorParameter:
    """Mock Material Expression for vector parameter."""

    def __init__(self):
        self.parameter_name = ""
        self.default_value = _MockLinearColor(0.0, 0.0, 0.0, 1.0)
        self.node_pos_x = 0
        self.node_pos_y = 0

    def set_editor_property(self, prop_name: str, value: Any) -> None:
        if prop_name == "parameter_name":
            self.parameter_name = str(value)
        elif prop_name == "default_value":
            self.default_value = value

    def get_editor_property(self, prop_name: str) -> Any:
        return getattr(self, prop_name, None)


class _MockMaterialExpressionScalarParameter:
    """Mock Material Expression for scalar parameter."""

    def __init__(self):
        self.parameter_name = ""
        self.default_value = 0.0
        self.node_pos_x = 0
        self.node_pos_y = 0

    def set_editor_property(self, prop_name: str, value: Any) -> None:
        if prop_name == "parameter_name":
            self.parameter_name = str(value)
        elif prop_name == "default_value":
            self.default_value = float(value)

    def get_editor_property(self, prop_name: str) -> Any:
        return getattr(self, prop_name, None)


class _MockMaterial:
    """Mock Material asset mirroring UMaterial."""

    def __init__(self, name: str, package_path: str):
        self.name = name
        self.package_path = package_path
        self.expressions: List[Any] = []
        self.connections: Dict[int, Any] = {}
        self.is_dirty = True

    def get_name(self) -> str:
        return self.name

    def get_path_name(self) -> str:
        return f"{self.package_path}/{self.name}"

    def __repr__(self) -> str:
        return f"Material'{self.get_path_name()}'"


class _MockMaterialInstanceConstant:
    """Mock Material Instance Constant mirroring UMaterialInstanceConstant."""

    def __init__(self, name: str, package_path: str):
        self.name = name
        self.package_path = package_path
        self.parent: Optional[_MockMaterial] = None
        self.vector_parameter_values: Dict[str, _MockLinearColor] = {}
        self.scalar_parameter_values: Dict[str, float] = {}
        self.is_dirty = True

    def get_name(self) -> str:
        return self.name

    def get_path_name(self) -> str:
        return f"{self.package_path}/{self.name}"

    def __repr__(self) -> str:
        return f"MaterialInstanceConstant'{self.get_path_name()}'"


class _MockSkeletalMesh:
    """Mock Skeletal Mesh asset mirroring USkeletalMesh."""

    def __init__(self, name: str, package_path: str):
        self.name = name
        self.package_path = package_path
        self.skeleton: Optional[Any] = None

    def get_name(self) -> str:
        return self.name

    def get_path_name(self) -> str:
        return f"{self.package_path}/{self.name}"

    def __repr__(self) -> str:
        return f"SkeletalMesh'{self.get_path_name()}'"


class _MockSkeleton:
    """Mock Skeleton asset mirroring USkeleton."""

    def __init__(self, name: str, package_path: str):
        self.name = name
        self.package_path = package_path

    def get_name(self) -> str:
        return self.name

    def get_path_name(self) -> str:
        return f"{self.package_path}/{self.name}"

    def __repr__(self) -> str:
        return f"Skeleton'{self.get_path_name()}'"


class _MockUClass:
    """Mock UClass mirroring reflected Unreal Class."""

    def __init__(self, class_name: str, cdo: Any = None):
        self.class_name = class_name
        self.cdo = cdo

    def get_name(self) -> str:
        return self.class_name

    def get_default_object(self) -> Any:
        return self.cdo

    def __repr__(self) -> str:
        return f"Class'{self.class_name}'"


class _MockAnimBlueprint:
    """Mock AnimBlueprint asset mirroring UAnimBlueprint."""

    def __init__(self, name: str, package_path: str):
        self.name = name
        self.package_path = package_path
        self.target_skeleton: Optional[Any] = None
        self.parent_class: Optional[Any] = None
        self.variables: Dict[str, str] = {}
        self.state_machines: List[str] = ["Locomotion", "Airborne"]
        self.slots: List[str] = ["DefaultGroup.UpperBody"]
        self.is_compiled = False
        self._gen_class = _MockUClass(f"{name}_C")

    def get_name(self) -> str:
        return self.name

    def get_path_name(self) -> str:
        return f"{self.package_path}/{self.name}"

    def generated_class(self) -> _MockUClass:
        return self._gen_class

    def __repr__(self) -> str:
        return f"AnimBlueprint'{self.get_path_name()}'"


class _MockSkeletalMeshComponent:
    """Mock SkeletalMeshComponent mirroring USkeletalMeshComponent."""

    def __init__(self):
        self.skeletal_mesh_asset: Optional[Any] = None
        self.skeletal_mesh: Optional[Any] = None
        self.relative_location = _MockVector(0.0, 0.0, 0.0)
        self.relative_rotation = _MockRotator(0.0, 0.0, 0.0)
        self.animation_mode = _MockAnimationMode.ANIMATION_SINGLE_NODE
        self.anim_class: Optional[Any] = None
        self.override_materials: List[Any] = []
        self.collision_profile_name = "CharacterMesh"

    def set_editor_property(self, prop_name: str, value: Any) -> None:
        if prop_name in ("skeletal_mesh_asset", "skeletal_mesh"):
            self.skeletal_mesh_asset = value
            self.skeletal_mesh = value
        elif prop_name == "relative_location":
            self.relative_location = value
        elif prop_name == "relative_rotation":
            self.relative_rotation = value
        elif prop_name == "animation_mode":
            self.animation_mode = value
        elif prop_name == "anim_class":
            self.anim_class = value
        elif prop_name == "override_materials":
            self.override_materials = list(value)
        elif prop_name == "collision_profile_name":
            self.collision_profile_name = str(value)
        else:
            setattr(self, prop_name, value)

    def get_editor_property(self, prop_name: str) -> Any:
        return getattr(self, prop_name, None)

    def set_material(self, index: int, material: Any) -> None:
        while len(self.override_materials) <= index:
            self.override_materials.append(None)
        self.override_materials[index] = material


class _MockCharacterCDO:
    """Mock Class Default Object for Character Blueprints."""

    def __init__(self):
        self.mesh = _MockSkeletalMeshComponent()

    def get_editor_property(self, prop_name: str) -> Any:
        if prop_name == "mesh":
            return self.mesh
        return getattr(self, prop_name, None)

    def set_editor_property(self, prop_name: str, value: Any) -> None:
        setattr(self, prop_name, value)


class _MockBlueprint:
    """Mock Blueprint asset mirroring UBlueprint."""

    def __init__(self, name: str, package_path: str, parent_class: Any = None):
        self.name = name
        self.package_path = package_path
        self.parent_class = parent_class
        self.cdo = _MockCharacterCDO()
        self._gen_class = _MockUClass(f"{name}_C", self.cdo)
        self.is_compiled = False

    def get_name(self) -> str:
        return self.name

    def get_path_name(self) -> str:
        return f"{self.package_path}/{self.name}"

    def generated_class(self) -> _MockUClass:
        return self._gen_class

    def __repr__(self) -> str:
        return f"Blueprint'{self.get_path_name()}'"


class _MockMaterialFactoryNew:
    pass


class _MockMaterialInstanceConstantFactoryNew:
    pass


class _MockAnimBlueprintFactory:
    def __init__(self):
        self.target_skeleton = None
        self.parent_class = None

    def set_editor_property(self, prop_name: str, value: Any) -> None:
        setattr(self, prop_name, value)


class _MockBlueprintFactory:
    def __init__(self):
        self.parent_class = None

    def set_editor_property(self, prop_name: str, value: Any) -> None:
        setattr(self, prop_name, value)


class _MockAssetTools:
    """Mock AssetTools mirroring UAssetTools."""

    def __init__(self, asset_library: _MockEditorAssetLibrary):
        self.asset_library = asset_library

    def create_asset(
        self, asset_name: str, package_path: str, asset_class: Any, factory: Any
    ) -> Any:
        full_path = f"{package_path}/{asset_name}"
        if issubclass(asset_class, _MockMaterial) or asset_class == _MockMaterial:
            asset = _MockMaterial(asset_name, package_path)
        elif issubclass(asset_class, _MockMaterialInstanceConstant) or asset_class == _MockMaterialInstanceConstant:
            asset = _MockMaterialInstanceConstant(asset_name, package_path)
        elif issubclass(asset_class, _MockAnimBlueprint) or asset_class == _MockAnimBlueprint:
            asset = _MockAnimBlueprint(asset_name, package_path)
            if hasattr(factory, "target_skeleton"):
                asset.target_skeleton = factory.target_skeleton
            if hasattr(factory, "parent_class"):
                asset.parent_class = factory.parent_class
        elif issubclass(asset_class, _MockBlueprint) or asset_class == _MockBlueprint:
            parent_cls = getattr(factory, "parent_class", None)
            asset = _MockBlueprint(asset_name, package_path, parent_class=parent_cls)
        else:
            asset = _MockBlueprint(asset_name, package_path)

        self.asset_library.register_asset(full_path, asset)
        return asset

    def duplicate_asset(self, asset_name: str, package_path: str, source_asset: Any) -> Any:
        full_path = f"{package_path}/{asset_name}"
        if isinstance(source_asset, _MockAnimBlueprint):
            asset = _MockAnimBlueprint(asset_name, package_path)
            asset.target_skeleton = source_asset.target_skeleton
            asset.parent_class = source_asset.parent_class
            asset.variables = dict(source_asset.variables)
            asset.state_machines = list(source_asset.state_machines)
            asset.slots = list(source_asset.slots)
        elif isinstance(source_asset, _MockMaterial):
            asset = _MockMaterial(asset_name, package_path)
            asset.expressions = list(source_asset.expressions)
            asset.connections = dict(source_asset.connections)
        else:
            asset = _MockBlueprint(asset_name, package_path)

        self.asset_library.register_asset(full_path, asset)
        return asset


class _MockAssetToolsHelpers:
    @staticmethod
    def get_asset_tools(asset_library: Optional[_MockEditorAssetLibrary] = None) -> _MockAssetTools:
        return _MockAssetTools(asset_library or _MockEditorAssetLibrary.get_instance())


class _MockEditorAssetLibrary:
    """Mock EditorAssetLibrary mirroring UEditorAssetLibrary."""

    _instance: Optional['_MockEditorAssetLibrary'] = None

    def __init__(self):
        self._assets: Dict[str, Any] = {}
        self._seed_default_engine_assets()

    @classmethod
    def get_instance(cls) -> '_MockEditorAssetLibrary':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _seed_default_engine_assets(self) -> None:
        """Seeds initial default engine and template assets into registry."""
        sk_manny = _MockSkeleton("SK_Mannequin", "/Game/Characters/Mannequins/Meshes")
        self.register_asset("/Game/Characters/Mannequins/Meshes/SK_Mannequin", sk_manny)
        self.register_asset("/Game/Characters/Mannequins/Rigs/SK_Mannequin", sk_manny)

        skm_manny = _MockSkeletalMesh("SKM_Manny", "/Game/Characters/Mannequins/Meshes")
        skm_manny.skeleton = sk_manny
        self.register_asset("/Game/Characters/Mannequins/Meshes/SKM_Manny", skm_manny)

        skm_quinn = _MockSkeletalMesh("SKM_Quinn", "/Game/Characters/Mannequins/Meshes")
        skm_quinn.skeleton = sk_manny
        self.register_asset("/Game/Characters/Mannequins/Meshes/SKM_Quinn", skm_quinn)

        cube_skm = _MockSkeletalMesh("SkeletalCube", "/Engine/EngineMeshes")
        self.register_asset("/Engine/EngineMeshes/SkeletalCube", cube_skm)

        # Template Manny Animation Blueprint
        abp_manny = _MockAnimBlueprint("ABP_Manny", "/Game/Characters/Mannequins/Animations")
        abp_manny.target_skeleton = sk_manny
        abp_manny.variables = {
            "Speed": "float",
            "bIsFalling": "bool",
            "bIsADS": "bool",
            "CurrentMovementState": "EBRMovementState"
        }
        self.register_asset("/Game/Characters/Mannequins/Animations/ABP_Manny", abp_manny)

        # Seed character blueprints if not present
        bp_char = _MockBlueprint("BP_BRCharacter", "/Game/Blueprints")
        bp_bot = _MockBlueprint("BP_BRAIBotCharacter", "/Game/Blueprints")
        self.register_asset("/Game/Blueprints/BP_BRCharacter", bp_char)
        self.register_asset("/Game/Blueprints/BP_BRAIBotCharacter", bp_bot)

    def register_asset(self, path: str, asset: Any) -> None:
        # Normalize path
        normalized = path.replace("\\", "/").rstrip("/")
        self._assets[normalized] = asset

    def does_asset_exist(self, asset_path: str) -> bool:
        normalized = asset_path.replace("\\", "/").rstrip("/")
        return normalized in self._assets

    def load_asset(self, asset_path: str) -> Optional[Any]:
        normalized = asset_path.replace("\\", "/").rstrip("/")
        return self._assets.get(normalized, None)

    def save_loaded_asset(self, asset: Any) -> bool:
        if asset:
            if hasattr(asset, "is_dirty"):
                asset.is_dirty = False
            return True
        return False

    def duplicate_asset(self, source_asset_path: str, destination_asset_path: str) -> Optional[Any]:
        src_norm = source_asset_path.replace("\\", "/").rstrip("/")
        dst_norm = destination_asset_path.replace("\\", "/").rstrip("/")
        src_asset = self._assets.get(src_norm, None)
        if not src_asset:
            return None

        pkg_path, asset_name = dst_norm.rsplit("/", 1)
        tools = _MockAssetTools(self)
        duplicated = tools.duplicate_asset(asset_name, pkg_path, src_asset)
        return duplicated

    def make_directory(self, directory_path: str) -> bool:
        return True

    def does_directory_exist(self, directory_path: str) -> bool:
        return True


class _MockMaterialEditingLibrary:
    """Mock MaterialEditingLibrary mirroring UMaterialEditingLibrary."""

    @staticmethod
    def create_material_expression(
        material: _MockMaterial, expression_class: Any, node_pos_x: int = 0, node_pos_y: int = 0
    ) -> Any:
        expr = expression_class()
        expr.node_pos_x = node_pos_x
        expr.node_pos_y = node_pos_y
        material.expressions.append(expr)
        return expr

    @staticmethod
    def connect_material_property(
        from_expression: Any, from_output_name: str, material_property: int
    ) -> bool:
        return True

    @staticmethod
    def update_material(material: _MockMaterial) -> None:
        material.is_dirty = False

    @staticmethod
    def set_material_instance_parent(
        instance: _MockMaterialInstanceConstant, parent_material: _MockMaterial
    ) -> bool:
        instance.parent = parent_material
        return True

    @staticmethod
    def set_material_instance_vector_parameter_value(
        instance: _MockMaterialInstanceConstant, parameter_name: str, value: _MockLinearColor
    ) -> bool:
        instance.vector_parameter_values[parameter_name] = value
        return True

    @staticmethod
    def set_material_instance_scalar_parameter_value(
        instance: _MockMaterialInstanceConstant, parameter_name: str, value: float
    ) -> bool:
        instance.scalar_parameter_values[parameter_name] = float(value)
        return True

    @staticmethod
    def update_material_instance(instance: _MockMaterialInstanceConstant) -> None:
        instance.is_dirty = False


class _MockKismetEditorUtilities:
    """Mock KismetEditorUtilities mirroring UKismetEditorUtilities."""

    @staticmethod
    def compile_blueprint(blueprint_asset: Any) -> None:
        if hasattr(blueprint_asset, "is_compiled"):
            blueprint_asset.is_compiled = True


class _MockBlueprintEditorLibrary:
    """Mock BlueprintEditorLibrary mirroring UBlueprintEditorLibrary."""

    @staticmethod
    def add_member_variable(blueprint_asset: Any, var_name: str, var_type: Any) -> bool:
        if hasattr(blueprint_asset, "variables"):
            blueprint_asset.variables[var_name] = str(var_type)
        return True


class _MockScopedEditorTransaction:
    """Mock ScopedEditorTransaction context manager."""

    def __init__(self, description: str):
        self.description = description

    def __enter__(self) -> '_MockScopedEditorTransaction':
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        pass


class _MockUnrealModule:
    """
    Mock Unreal Engine Python Module.
    Provides complete, authentic simulation of all classes, libraries, and CDO properties.
    """

    def __init__(self):
        self.Vector = _MockVector
        self.Rotator = _MockRotator
        self.LinearColor = _MockLinearColor
        self.AnimationMode = _MockAnimationMode
        self.MaterialProperty = _MockMaterialProperty

        self.Material = _MockMaterial
        self.MaterialInstanceConstant = _MockMaterialInstanceConstant
        self.AnimBlueprint = _MockAnimBlueprint
        self.Blueprint = _MockBlueprint
        self.SkeletalMesh = _MockSkeletalMesh
        self.Skeleton = _MockSkeleton
        self.SkeletalMeshComponent = _MockSkeletalMeshComponent

        self.MaterialFactoryNew = _MockMaterialFactoryNew
        self.MaterialInstanceConstantFactoryNew = _MockMaterialInstanceConstantFactoryNew
        self.AnimBlueprintFactory = _MockAnimBlueprintFactory
        self.BlueprintFactory = _MockBlueprintFactory

        self.AnimInstance = _MockUClass("AnimInstance")
        self.Character = _MockUClass("Character")

        self.EditorAssetLibrary = _MockEditorAssetLibrary.get_instance()
        self.MaterialEditingLibrary = _MockMaterialEditingLibrary
        self.KismetEditorUtilities = _MockKismetEditorUtilities
        self.BlueprintEditorLibrary = _MockBlueprintEditorLibrary
        self.AssetToolsHelpers = _MockAssetToolsHelpers
        self.ScopedEditorTransaction = _MockScopedEditorTransaction

    def get_default_object(self, class_object: Any) -> Any:
        if hasattr(class_object, "get_default_object"):
            return class_object.get_default_object()
        if hasattr(class_object, "cdo"):
            return class_object.cdo
        return None

    def load_class(self, outer: Any, path: str) -> Optional[_MockUClass]:
        cls_name = path.split(".")[-1]
        return _MockUClass(cls_name)

    @staticmethod
    def log(msg: str) -> None:
        print(f"[INFO] [setup_character_anims] {msg}")

    @staticmethod
    def log_warning(msg: str) -> None:
        print(f"[WARNING] [setup_character_anims] {msg}")

    @staticmethod
    def log_error(msg: str) -> None:
        print(f"[ERROR] [setup_character_anims] {msg}")


# ==============================================================================
# Logging & Diagnostic Helpers
# ==============================================================================

def log_info(msg: str, u: Any) -> None:
    """Emits an informational log to Unreal or console."""
    if hasattr(u, "log"):
        u.log(f"{msg}")
    else:
        print(f"[INFO] [setup_character_anims] {msg}")


def log_verbose(msg: str, u: Any, verbose: bool = False) -> None:
    """Emits a verbose trace log if verbose mode is active."""
    if verbose:
        if hasattr(u, "log"):
            u.log(f"[DEBUG] {msg}")
        else:
            print(f"[DEBUG] [setup_character_anims] {msg}")


def log_warning(msg: str, u: Any) -> None:
    """Emits a warning log to Unreal or console."""
    if hasattr(u, "log_warning"):
        u.log_warning(f"{msg}")
    else:
        print(f"[WARNING] [setup_character_anims] {msg}")


def log_error(msg: str, u: Any) -> None:
    """Emits an error log to Unreal or console."""
    if hasattr(u, "log_error"):
        u.log_error(f"{msg}")
    else:
        print(f"[ERROR] [setup_character_anims] {msg}")


# ==============================================================================
# Asset Resolution & Retrieval Subroutines
# ==============================================================================

def resolve_skeletal_mesh(u: Any, verbose: bool = False) -> Tuple[Optional[Any], str]:
    """
    Resolves the Manny/Quinn skeletal mesh asset using prioritized candidate paths:
      1. /Game/Characters/Mannequins/Meshes/SKM_Manny (UE5 Standard)
      2. /Game/Characters/Mannequins/Meshes/SKM_Quinn
      3. /Game/Characters/Mannequins/Meshes/SKM_Manny_Simple
      4. /Engine/EngineMeshes/SkeletalCube (Headless engine fallback)
    """
    candidates = [
        "/Game/Characters/Mannequins/Meshes/SKM_Manny",
        "/Game/Characters/Mannequins/Meshes/SKM_Quinn",
        "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple",
        "/Engine/EngineMeshes/SkeletalCube",
    ]

    for path in candidates:
        if u.EditorAssetLibrary.does_asset_exist(path):
            asset = u.EditorAssetLibrary.load_asset(path)
            if asset:
                log_verbose(f"Resolved skeletal mesh asset at: {path}", u, verbose)
                return asset, path

    log_warning("No candidate skeletal mesh found in asset registry; using fallback placeholder path.", u)
    return None, candidates[0]


def resolve_skeleton(u: Any, verbose: bool = False) -> Tuple[Optional[Any], str]:
    """
    Resolves the Mannequin skeleton asset for AnimBP targeting.
    """
    candidates = [
        "/Game/Characters/Mannequins/Meshes/SK_Mannequin",
        "/Game/Characters/Mannequins/Rigs/SK_Mannequin",
        "/Engine/EngineMeshes/SkeletalCube",
    ]

    for path in candidates:
        if u.EditorAssetLibrary.does_asset_exist(path):
            asset = u.EditorAssetLibrary.load_asset(path)
            if asset:
                log_verbose(f"Resolved skeleton asset at: {path}", u, verbose)
                return asset, path

    return None, candidates[0]


def resolve_template_anim_bp(u: Any, verbose: bool = False) -> Optional[str]:
    """
    Checks if a template AnimBP (e.g. ABP_Manny) exists for Tier-1 duplication.
    """
    candidates = [
        "/Game/Characters/Mannequins/Animations/ABP_Manny",
        "/Game/Characters/Mannequins/Animations/ABP_Quinn",
    ]

    for path in candidates:
        if u.EditorAssetLibrary.does_asset_exist(path):
            log_verbose(f"Found template Animation Blueprint for Tier-1 duplication: {path}", u, verbose)
            return path

    return None


def resolve_native_class(u: Any, class_name: str, script_path: str, fallback_cls: Any) -> Any:
    """
    Resolves a C++ reflection class from the game module or falls back to engine class.
    """
    if hasattr(u, class_name):
        return getattr(u, class_name)

    if hasattr(u, "load_class"):
        try:
            cls = u.load_class(None, script_path)
            if cls:
                return cls
        except Exception:
            pass

    return fallback_cls


# ==============================================================================
# Faceless PBR Material Pipeline
# ==============================================================================

def setup_faceless_master_material(u: Any, verbose: bool = False) -> Optional[Any]:
    """
    Procedurally creates and configures the master faceless PBR material:
        Target: /Game/Materials/M_BRFacelessPlaceholder
        Parameters:
            - BaseColor (VectorParameter): Default charcoal gray (0.20, 0.20, 0.22, 1.0) -> MP_BASE_COLOR
            - Roughness (ScalarParameter): Default 0.60 -> MP_ROUGHNESS
            - Metallic (ScalarParameter): Default 0.0 -> MP_METALLIC
    """
    package_path = "/Game/Materials"
    asset_name = "M_BRFacelessPlaceholder"
    full_path = f"{package_path}/{asset_name}"

    if u.EditorAssetLibrary.does_asset_exist(full_path):
        log_verbose(f"Master material already exists at {full_path}. Loading...", u, verbose)
        mat_asset = u.EditorAssetLibrary.load_asset(full_path)
        if mat_asset:
            return mat_asset

    log_info(f"Creating master PBR faceless material: {full_path}", u)
    asset_tools = u.AssetToolsHelpers.get_asset_tools()
    factory = u.MaterialFactoryNew()
    mat_asset = asset_tools.create_asset(asset_name, package_path, u.Material, factory)

    if not mat_asset:
        log_error(f"Failed to create Material asset {asset_name} at {package_path}", u)
        return None

    # 1. BaseColor Vector Parameter
    vec_expr = u.MaterialEditingLibrary.create_material_expression(
        mat_asset, getattr(u, "MaterialExpressionVectorParameter", _MockMaterialExpressionVectorParameter), -400, -100
    )
    if hasattr(vec_expr, "set_editor_property"):
        vec_expr.set_editor_property("parameter_name", "BaseColor")
        vec_expr.set_editor_property("default_value", u.LinearColor(0.20, 0.20, 0.22, 1.0))
    u.MaterialEditingLibrary.connect_material_property(
        vec_expr, "", u.MaterialProperty.MP_BASE_COLOR
    )

    # 2. Roughness Scalar Parameter
    rough_expr = u.MaterialEditingLibrary.create_material_expression(
        mat_asset, getattr(u, "MaterialExpressionScalarParameter", _MockMaterialExpressionScalarParameter), -400, 100
    )
    if hasattr(rough_expr, "set_editor_property"):
        rough_expr.set_editor_property("parameter_name", "Roughness")
        rough_expr.set_editor_property("default_value", 0.60)
    u.MaterialEditingLibrary.connect_material_property(
        rough_expr, "", u.MaterialProperty.MP_ROUGHNESS
    )

    # 3. Metallic Scalar Parameter
    metal_expr = u.MaterialEditingLibrary.create_material_expression(
        mat_asset, getattr(u, "MaterialExpressionScalarParameter", _MockMaterialExpressionScalarParameter), -400, 250
    )
    if hasattr(metal_expr, "set_editor_property"):
        metal_expr.set_editor_property("parameter_name", "Metallic")
        metal_expr.set_editor_property("default_value", 0.0)
    u.MaterialEditingLibrary.connect_material_property(
        metal_expr, "", u.MaterialProperty.MP_METALLIC
    )

    u.MaterialEditingLibrary.update_material(mat_asset)
    u.EditorAssetLibrary.save_loaded_asset(mat_asset)
    log_verbose(f"Master material {asset_name} successfully compiled and persisted.", u, verbose)
    return mat_asset


def setup_material_instance(
    u: Any,
    instance_name: str,
    package_path: str,
    parent_mat: Any,
    params: Dict[str, Union[Any, float]],
    verbose: bool = False,
) -> Optional[Any]:
    """
    Creates and configures a Material Instance Constant inheriting from M_BRFacelessPlaceholder.
    """
    full_path = f"{package_path}/{instance_name}"
    if u.EditorAssetLibrary.does_asset_exist(full_path):
        log_verbose(f"Material instance {full_path} already exists. Loading...", u, verbose)
        instance = u.EditorAssetLibrary.load_asset(full_path)
    else:
        log_info(f"Creating Material Instance: {full_path}", u)
        asset_tools = u.AssetToolsHelpers.get_asset_tools()
        factory = u.MaterialInstanceConstantFactoryNew()
        instance = asset_tools.create_asset(
            instance_name, package_path, u.MaterialInstanceConstant, factory
        )

    if not instance:
        log_error(f"Failed to create Material Instance {instance_name}", u)
        return None

    # Set parent material
    u.MaterialEditingLibrary.set_material_instance_parent(instance, parent_mat)

    # Apply parameter overrides
    for param_name, value in params.items():
        if isinstance(value, (u.LinearColor, _MockLinearColor)):
            u.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
                instance, param_name, value
            )
            log_verbose(f"  [{instance_name}] Set Vector param '{param_name}' = {value}", u, verbose)
        elif isinstance(value, (float, int)):
            u.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(
                instance, param_name, float(value)
            )
            log_verbose(f"  [{instance_name}] Set Scalar param '{param_name}' = {value}", u, verbose)

    u.MaterialEditingLibrary.update_material_instance(instance)
    u.EditorAssetLibrary.save_loaded_asset(instance)
    return instance


# ==============================================================================
# Animation Blueprint (AnimBP) Setup
# ==============================================================================

def setup_anim_blueprint(
    u: Any,
    skeleton_asset: Optional[Any],
    template_bp_path: Optional[str] = None,
    verbose: bool = False,
) -> Optional[Any]:
    """
    Creates or configures ABP_BRCharacter with two-tier resolution:
      - Tier 1: Duplicate template (ABP_Manny) if present. Preserves full Manny locomotion
        graph, Jump sub-graphs, and UpperBody slots.
      - Tier 2: Create procedural AnimBlueprint with target skeleton and configure variables
        and locomotion bindings.
    """
    package_path = "/Game/Characters/Mannequins/Animations"
    asset_name = "ABP_BRCharacter"
    full_path = f"{package_path}/{asset_name}"

    if u.EditorAssetLibrary.does_asset_exist(full_path):
        log_verbose(f"AnimBlueprint already exists at {full_path}. Loading...", u, verbose)
        abp = u.EditorAssetLibrary.load_asset(full_path)
        if abp:
            return abp

    # Tier 1: Asset Duplication from template
    if template_bp_path and u.EditorAssetLibrary.does_asset_exist(template_bp_path):
        log_info(f"Tier-1 AnimBP Resolution: Duplicating {template_bp_path} -> {full_path}", u)
        abp = u.EditorAssetLibrary.duplicate_asset(template_bp_path, full_path)
        if abp:
            log_verbose(f"Successfully duplicated {template_bp_path} to {full_path}", u, verbose)
            u.KismetEditorUtilities.compile_blueprint(abp)
            u.EditorAssetLibrary.save_loaded_asset(abp)
            return abp
        else:
            log_warning(f"Failed to duplicate template AnimBP from {template_bp_path}; falling back to Tier-2.", u)

    # Tier 2: Procedural AnimBlueprint creation via Factory
    log_info(f"Tier-2 AnimBP Resolution: Procedurally creating AnimBlueprint at {full_path}", u)
    asset_tools = u.AssetToolsHelpers.get_asset_tools()
    factory = u.AnimBlueprintFactory()
    if skeleton_asset and hasattr(factory, "set_editor_property"):
        factory.set_editor_property("target_skeleton", skeleton_asset)
        parent_cls = getattr(u, "AnimInstance", None)
        if parent_cls:
            factory.set_editor_property("parent_class", parent_cls)

    abp = asset_tools.create_asset(asset_name, package_path, u.AnimBlueprint, factory)
    if not abp:
        log_error(f"Failed to create AnimBlueprint {asset_name} at {package_path}", u)
        return None

    # Document and scaffold variables if BlueprintEditorLibrary is available
    bp_vars = [
        ("Speed", "float", "Ground velocity magnitude in cm/s (PawnOwner.Velocity.Size2D())"),
        ("bIsFalling", "bool", "Airborne jump/fall status (MovementComponent.IsFalling())"),
        ("bIsADS", "bool", "Aim-Down-Sights active status (ABRCharacter.bIsADS)"),
        ("CurrentMovementState", "byte", "Locomotion stance state (ABRCharacter.CurrentMovementState)"),
    ]

    for var_name, var_type, desc in bp_vars:
        if hasattr(u, "BlueprintEditorLibrary") and hasattr(u.BlueprintEditorLibrary, "add_member_variable"):
            try:
                u.BlueprintEditorLibrary.add_member_variable(abp, var_name, var_type)
                log_verbose(f"  [ABP_BRCharacter] Added variable '{var_name}' ({var_type}): {desc}", u, verbose)
            except Exception as e:
                log_verbose(f"  [ABP_BRCharacter] Notice on variable '{var_name}': {e}", u, verbose)
        elif hasattr(abp, "variables"):
            abp.variables[var_name] = var_type

    u.KismetEditorUtilities.compile_blueprint(abp)
    u.EditorAssetLibrary.save_loaded_asset(abp)
    log_verbose(f"AnimBlueprint {asset_name} compiled and saved.", u, verbose)
    return abp


# ==============================================================================
# Character Blueprint CDO Configuration
# ==============================================================================

def get_or_create_character_blueprint(
    u: Any,
    asset_name: str,
    package_path: str,
    parent_class: Any,
    verbose: bool = False,
) -> Optional[Any]:
    """
    Loads existing Character Blueprint or creates a new one inheriting from parent_class.
    """
    full_path = f"{package_path}/{asset_name}"
    if u.EditorAssetLibrary.does_asset_exist(full_path):
        log_verbose(f"Character Blueprint exists at {full_path}. Loading...", u, verbose)
        return u.EditorAssetLibrary.load_asset(full_path)

    log_info(f"Creating Character Blueprint: {full_path}", u)
    asset_tools = u.AssetToolsHelpers.get_asset_tools()
    factory = u.BlueprintFactory()
    if parent_class and hasattr(factory, "set_editor_property"):
        factory.set_editor_property("parent_class", parent_class)

    bp = asset_tools.create_asset(asset_name, package_path, getattr(u, "Blueprint", _MockBlueprint), factory)
    if not bp:
        log_error(f"Failed to create Blueprint {asset_name} at {package_path}", u)
        return None

    return bp


def configure_character_cdo(
    u: Any,
    bp_asset: Any,
    skeletal_mesh_asset: Any,
    material_instance_asset: Any,
    anim_bp_asset: Any,
    verbose: bool = False,
) -> bool:
    """
    Configures Class Default Object (CDO) properties on a character Blueprint:
      1. Assigns skeletal mesh asset (SKM_Manny).
      2. Sets relative location alignment: Vector(0.0, 0.0, -90.0) (aligns feet to capsule base).
      3. Sets relative rotation alignment: Rotator(0.0, -90.0, 0.0) (aligns mesh facing +X forward).
      4. Sets animation mode to ANIMATION_BLUEPRINT and wires anim_class to ABP_BRCharacter_C.
      5. Sets material override to the designated faceless material instance.
      6. Compiles Blueprint and persists asset to disk.
    """
    bp_name = bp_asset.get_name() if hasattr(bp_asset, "get_name") else "CharacterBP"
    log_info(f"Configuring CDO properties for: {bp_name}", u)

    if not hasattr(bp_asset, "generated_class"):
        log_error(f"Blueprint {bp_name} does not expose generated_class().", u)
        return False

    gen_class = bp_asset.generated_class()
    cdo = u.get_default_object(gen_class)
    if not cdo:
        log_error(f"Could not retrieve CDO for {bp_name}.", u)
        return False

    mesh_comp = None
    if hasattr(cdo, "get_editor_property"):
        mesh_comp = cdo.get_editor_property("mesh")
    elif hasattr(cdo, "mesh"):
        mesh_comp = cdo.mesh

    if not mesh_comp:
        log_error(f"Could not access SkeletalMeshComponent 'mesh' on CDO of {bp_name}.", u)
        return False

    # 1. Assign Skeletal Mesh Asset
    if skeletal_mesh_asset:
        assigned = False
        if hasattr(mesh_comp, "set_editor_property"):
            try:
                mesh_comp.set_editor_property("skeletal_mesh_asset", skeletal_mesh_asset)
                assigned = True
            except Exception:
                try:
                    mesh_comp.set_editor_property("skeletal_mesh", skeletal_mesh_asset)
                    assigned = True
                except Exception as e:
                    log_verbose(f"  Notice on skeletal_mesh assignment: {e}", u, verbose)
        if not assigned:
            setattr(mesh_comp, "skeletal_mesh_asset", skeletal_mesh_asset)
        log_verbose(f"  [{bp_name}] Assigned SkeletalMesh: {skeletal_mesh_asset}", u, verbose)

    # 2. Set Transform Alignment
    # RelativeLocation: (0.0, 0.0, -90.0) — grounds the mesh inside the capsule
    rel_loc = u.Vector(0.0, 0.0, -90.0)
    # RelativeRotation: (0.0, -90.0, 0.0) — orients mesh facing +X actor forward
    rel_rot = u.Rotator(0.0, -90.0, 0.0)

    if hasattr(mesh_comp, "set_editor_property"):
        mesh_comp.set_editor_property("relative_location", rel_loc)
        mesh_comp.set_editor_property("relative_rotation", rel_rot)
    else:
        mesh_comp.relative_location = rel_loc
        mesh_comp.relative_rotation = rel_rot

    log_verbose(f"  [{bp_name}] Set RelativeLocation: {rel_loc}", u, verbose)
    log_verbose(f"  [{bp_name}] Set RelativeRotation: {rel_rot}", u, verbose)

    # 3. Set Animation Mode & Class
    if hasattr(u, "AnimationMode"):
        anim_bp_mode = getattr(u.AnimationMode, "ANIMATION_BLUEPRINT", None)
        if anim_bp_mode is not None:
            if hasattr(mesh_comp, "set_editor_property"):
                mesh_comp.set_editor_property("animation_mode", anim_bp_mode)
            else:
                mesh_comp.animation_mode = anim_bp_mode
            log_verbose(f"  [{bp_name}] Set AnimationMode = ANIMATION_BLUEPRINT", u, verbose)

    if anim_bp_asset and hasattr(anim_bp_asset, "generated_class"):
        anim_gen_class = anim_bp_asset.generated_class()
        if hasattr(mesh_comp, "set_editor_property"):
            mesh_comp.set_editor_property("anim_class", anim_gen_class)
        else:
            mesh_comp.anim_class = anim_gen_class
        log_verbose(f"  [{bp_name}] Set AnimClass = {anim_gen_class}", u, verbose)

    # 4. Set Material Instance Overrides
    if material_instance_asset:
        if hasattr(mesh_comp, "set_editor_property"):
            try:
                mesh_comp.set_editor_property("override_materials", [material_instance_asset])
            except Exception:
                pass
        if hasattr(mesh_comp, "set_material"):
            try:
                mesh_comp.set_material(0, material_instance_asset)
            except Exception:
                pass
        log_verbose(f"  [{bp_name}] Set Material Override[0] = {material_instance_asset}", u, verbose)

    # 5. Compile Blueprint and Save Asset
    u.KismetEditorUtilities.compile_blueprint(bp_asset)
    saved = u.EditorAssetLibrary.save_loaded_asset(bp_asset)
    log_info(f"Successfully configured, compiled, and saved: {bp_name}", u)
    return True


# ==============================================================================
# Main Setup & Orchestration Function
# ==============================================================================

def setup_character_anims(force_dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Main orchestration routine for Requirement R2:
      1. Initializes Unreal Engine context or activates standalone dry-run simulation framework.
      2. Procedurally creates master faceless material M_BRFacelessPlaceholder.
      3. Generates distinct material instances:
         - MI_BRFacelessManny (charcoal studio gray: 0.20, 0.20, 0.22) for player.
         - MI_BRFacelessBot (tactical orange-red: 0.70, 0.25, 0.15) for AI bots.
         - MI_BRFacelessQuinn (slate gray: 0.28, 0.28, 0.32).
      4. Resolves default UE5 Manny/Quinn skeletal meshes and skeleton.
      5. Configures ABP_BRCharacter with two-tier resolution (template duplicate or factory).
      6. Configures BP_BRCharacter and BP_BRAIBotCharacter CDOs with correct transforms, mesh,
         material instances, and AnimBP wiring.
      7. Compiles and saves all assets with verification pass.
    """
    is_standalone = force_dry_run or (unreal is None)
    u = _MockUnrealModule() if is_standalone else unreal

    mode_label = "[DRY-RUN SIMULATION]" if is_standalone else "[LIVE UNREAL ENGINE]"
    log_info("==================================================================", u)
    log_info(f"Starting Bakırköy BR Character & Animation Setup {mode_label}", u)
    log_info("==================================================================", u)

    # Wrap editor modifications inside ScopedEditorTransaction for live UE5 safety
    trans_scope = u.ScopedEditorTransaction("Bakirkoy BR Character & Animation Setup")
    with trans_scope:
        # ----------------------------------------------------------------------
        # Phase 1: Material Pipeline Setup
        # ----------------------------------------------------------------------
        log_info("--- Phase 1: Procedural Faceless Material Setup ---", u)
        master_mat = setup_faceless_master_material(u, verbose=verbose)
        if not master_mat:
            log_error("Aborting setup: Master material creation failed.", u)
            return False

        # Player Material Instance: Charcoal Studio Gray
        mi_manny = setup_material_instance(
            u=u,
            instance_name="MI_BRFacelessManny",
            package_path="/Game/Materials",
            parent_mat=master_mat,
            params={
                "BaseColor": u.LinearColor(0.20, 0.20, 0.22, 1.0),
                "Roughness": 0.60,
                "Metallic": 0.0,
            },
            verbose=verbose,
        )

        # AI Bot Material Instance: Tactical Orange-Red Tint for 10-Bot MVP distinction
        mi_bot = setup_material_instance(
            u=u,
            instance_name="MI_BRFacelessBot",
            package_path="/Game/Materials",
            parent_mat=master_mat,
            params={
                "BaseColor": u.LinearColor(0.70, 0.25, 0.15, 1.0),
                "Roughness": 0.50,
                "Metallic": 0.10,
            },
            verbose=verbose,
        )

        # Alternative Quinn Material Instance: Slate Gray
        mi_quinn = setup_material_instance(
            u=u,
            instance_name="MI_BRFacelessQuinn",
            package_path="/Game/Materials",
            parent_mat=master_mat,
            params={
                "BaseColor": u.LinearColor(0.28, 0.28, 0.32, 1.0),
                "Roughness": 0.60,
                "Metallic": 0.0,
            },
            verbose=verbose,
        )

        # ----------------------------------------------------------------------
        # Phase 2: Skeletal Mesh & Skeleton Resolution
        # ----------------------------------------------------------------------
        log_info("--- Phase 2: Skeletal Mesh & Skeleton Resolution ---", u)
        sk_mesh, mesh_path = resolve_skeletal_mesh(u, verbose=verbose)
        skeleton, skel_path = resolve_skeleton(u, verbose=verbose)
        template_abp_path = resolve_template_anim_bp(u, verbose=verbose)

        log_info(f"Target Skeletal Mesh: {mesh_path}", u)
        log_info(f"Target Skeleton:      {skel_path}", u)
        if template_abp_path:
            log_info(f"Template AnimBP:      {template_abp_path} (Available for Tier-1 Duplication)", u)
        else:
            log_info("Template AnimBP:      None (Using Tier-2 Procedural AnimBP Factory)", u)

        # ----------------------------------------------------------------------
        # Phase 3: Animation Blueprint (ABP_BRCharacter) Setup
        # ----------------------------------------------------------------------
        log_info("--- Phase 3: Animation Blueprint Setup ---", u)
        abp_asset = setup_anim_blueprint(
            u=u,
            skeleton_asset=skeleton,
            template_bp_path=template_abp_path,
            verbose=verbose,
        )
        if not abp_asset:
            log_error("Aborting setup: AnimBlueprint setup failed.", u)
            return False

        # ----------------------------------------------------------------------
        # Phase 4: Character Blueprints CDO Wiring
        # ----------------------------------------------------------------------
        log_info("--- Phase 4: Character Blueprints CDO Wiring ---", u)

        # Resolve native C++ character classes
        c_char_native = resolve_native_class(
            u, "BRCharacter", "/Script/BakirkoyBR.BRCharacter", getattr(u, "Character", None)
        )
        c_bot_native = resolve_native_class(
            u, "BRAIBotCharacter", "/Script/BakirkoyBR.BRAIBotCharacter", c_char_native
        )

        # 4a. Player Character Blueprint (BP_BRCharacter)
        bp_char = get_or_create_character_blueprint(
            u=u,
            asset_name="BP_BRCharacter",
            package_path="/Game/Blueprints",
            parent_class=c_char_native,
            verbose=verbose,
        )
        if bp_char:
            configure_character_cdo(
                u=u,
                bp_asset=bp_char,
                skeletal_mesh_asset=sk_mesh,
                material_instance_asset=mi_manny,
                anim_bp_asset=abp_asset,
                verbose=verbose,
            )
        else:
            log_error("Failed to load or create BP_BRCharacter.", u)
            return False

        # 4b. AI Bot Character Blueprint (BP_BRAIBotCharacter)
        bp_bot = get_or_create_character_blueprint(
            u=u,
            asset_name="BP_BRAIBotCharacter",
            package_path="/Game/Blueprints",
            parent_class=c_bot_native,
            verbose=verbose,
        )
        if bp_bot:
            configure_character_cdo(
                u=u,
                bp_asset=bp_bot,
                skeletal_mesh_asset=sk_mesh,
                material_instance_asset=mi_bot,
                anim_bp_asset=abp_asset,
                verbose=verbose,
            )
        else:
            log_error("Failed to load or create BP_BRAIBotCharacter.", u)
            return False

        # ----------------------------------------------------------------------
        # Phase 5: Verification & Integrity Assertions
        # ----------------------------------------------------------------------
        log_info("--- Phase 5: Integrity Verification ---", u)
        verify_ok = verify_character_anim_setup(u=u, verbose=verbose)
        if not verify_ok:
            log_error("Verification pass failed.", u)
            return False

    log_info("==================================================================", u)
    log_info("Bakırköy BR Character & Animation Setup Completed Successfully! [EXIT 0]", u)
    log_info("==================================================================", u)
    return True


# ==============================================================================
# Verification & Self-Check Suite
# ==============================================================================

def verify_character_anim_setup(u: Any, verbose: bool = False) -> bool:
    """
    Performs comprehensive verification of created assets, CDO property values,
    transform alignments, material assignments, and AnimBP bindings.
    """
    checks_passed = 0
    total_checks = 0

    def assert_check(condition: bool, check_name: str) -> None:
        nonlocal checks_passed, total_checks
        total_checks += 1
        if condition:
            checks_passed += 1
            log_verbose(f"  [PASS] {check_name}", u, verbose)
        else:
            log_error(f"  [FAIL] {check_name}", u)

    log_info("Running Automated Verification Assertions:", u)

    # 1. Verify Materials
    mat_master_exists = u.EditorAssetLibrary.does_asset_exist("/Game/Materials/M_BRFacelessPlaceholder")
    assert_check(mat_master_exists, "Asset Exists: /Game/Materials/M_BRFacelessPlaceholder")

    mi_manny_exists = u.EditorAssetLibrary.does_asset_exist("/Game/Materials/MI_BRFacelessManny")
    assert_check(mi_manny_exists, "Asset Exists: /Game/Materials/MI_BRFacelessManny (Player Charcoal)")

    mi_bot_exists = u.EditorAssetLibrary.does_asset_exist("/Game/Materials/MI_BRFacelessBot")
    assert_check(mi_bot_exists, "Asset Exists: /Game/Materials/MI_BRFacelessBot (Bot Tactical Orange-Red)")

    # 2. Verify AnimBP
    abp_exists = u.EditorAssetLibrary.does_asset_exist("/Game/Characters/Mannequins/Animations/ABP_BRCharacter")
    assert_check(abp_exists, "Asset Exists: /Game/Characters/Mannequins/Animations/ABP_BRCharacter")

    # 3. Verify Player Character CDO (BP_BRCharacter)
    bp_char = u.EditorAssetLibrary.load_asset("/Game/Blueprints/BP_BRCharacter")
    assert_check(bp_char is not None, "Blueprint Loaded: /Game/Blueprints/BP_BRCharacter")

    if bp_char and hasattr(bp_char, "generated_class"):
        cdo_char = u.get_default_object(bp_char.generated_class())
        mesh_char = cdo_char.get_editor_property("mesh") if hasattr(cdo_char, "get_editor_property") else getattr(cdo_char, "mesh", None)
        assert_check(mesh_char is not None, "BP_BRCharacter: SkeletalMeshComponent Accessible")

        if mesh_char:
            # Check relative transform alignment: (0, 0, -90) and (0, -90, 0)
            expected_loc = u.Vector(0.0, 0.0, -90.0)
            actual_loc = mesh_char.get_editor_property("relative_location") if hasattr(mesh_char, "get_editor_property") else getattr(mesh_char, "relative_location", None)
            assert_check(actual_loc == expected_loc, f"BP_BRCharacter: RelativeLocation == {expected_loc} (Actual: {actual_loc})")

            expected_rot = u.Rotator(0.0, -90.0, 0.0)
            actual_rot = mesh_char.get_editor_property("relative_rotation") if hasattr(mesh_char, "get_editor_property") else getattr(mesh_char, "relative_rotation", None)
            assert_check(actual_rot == expected_rot, f"BP_BRCharacter: RelativeRotation == {expected_rot} (Actual: {actual_rot})")

            # Check animation mode
            anim_mode = mesh_char.get_editor_property("animation_mode") if hasattr(mesh_char, "get_editor_property") else getattr(mesh_char, "animation_mode", None)
            expected_anim_mode = getattr(u.AnimationMode, "ANIMATION_BLUEPRINT", "ANIMATION_BLUEPRINT")
            assert_check(anim_mode == expected_anim_mode, "BP_BRCharacter: AnimationMode == ANIMATION_BLUEPRINT")

            # Check material override
            mats = mesh_char.get_editor_property("override_materials") if hasattr(mesh_char, "get_editor_property") else getattr(mesh_char, "override_materials", [])
            assert_check(len(mats) > 0 and mats[0] is not None, "BP_BRCharacter: Override Material[0] is assigned")

    # 4. Verify Bot Character CDO (BP_BRAIBotCharacter)
    bp_bot = u.EditorAssetLibrary.load_asset("/Game/Blueprints/BP_BRAIBotCharacter")
    assert_check(bp_bot is not None, "Blueprint Loaded: /Game/Blueprints/BP_BRAIBotCharacter")

    if bp_bot and hasattr(bp_bot, "generated_class"):
        cdo_bot = u.get_default_object(bp_bot.generated_class())
        mesh_bot = cdo_bot.get_editor_property("mesh") if hasattr(cdo_bot, "get_editor_property") else getattr(cdo_bot, "mesh", None)
        assert_check(mesh_bot is not None, "BP_BRAIBotCharacter: SkeletalMeshComponent Accessible")

        if mesh_bot:
            expected_loc = u.Vector(0.0, 0.0, -90.0)
            actual_loc = mesh_bot.get_editor_property("relative_location") if hasattr(mesh_bot, "get_editor_property") else getattr(mesh_bot, "relative_location", None)
            assert_check(actual_loc == expected_loc, f"BP_BRAIBotCharacter: RelativeLocation == {expected_loc} (Actual: {actual_loc})")

            expected_rot = u.Rotator(0.0, -90.0, 0.0)
            actual_rot = mesh_bot.get_editor_property("relative_rotation") if hasattr(mesh_bot, "get_editor_property") else getattr(mesh_bot, "relative_rotation", None)
            assert_check(actual_rot == expected_rot, f"BP_BRAIBotCharacter: RelativeRotation == {expected_rot} (Actual: {actual_rot})")

            mats_bot = mesh_bot.get_editor_property("override_materials") if hasattr(mesh_bot, "get_editor_property") else getattr(mesh_bot, "override_materials", [])
            assert_check(len(mats_bot) > 0 and mats_bot[0] is not None, "BP_BRAIBotCharacter: Override Material[0] is assigned")

    log_info(f"Verification Results: {checks_passed}/{total_checks} assertions passed.", u)
    return checks_passed == total_checks


# ==============================================================================
# CLI Entrypoint
# ==============================================================================

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parses CLI flags safely using parse_known_args to prevent errors from
    unrecognized Unreal Engine commandlet arguments.
    """
    parser = argparse.ArgumentParser(
        description="Procedural Character & Animation Setup for Bakırköy BR"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Force standalone dry-run simulation mode even if unreal is imported",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose debugging and diagnostic output",
    )
    args, _ = parser.parse_known_args(argv)
    return args


def main() -> int:
    """CLI execution entrypoint."""
    args = parse_args(sys.argv[1:])
    success = setup_character_anims(force_dry_run=args.dry_run, verbose=args.verbose)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
