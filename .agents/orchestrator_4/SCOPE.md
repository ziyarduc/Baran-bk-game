# Scope: Phase 4 — 1:1 Bakırköy OSM Map Generation & Procedural Character Animations

## Architecture
The Phase 4 architecture implements a two-pronged automation pipeline for the Bakırköy Battle Royale project:
1. **GIS / OpenStreetMap Ingestion Pipeline (`fetch_osm_data.py`)**:
   - Queries OpenStreetMap via Overpass API with a 5-endpoint failover pool (`overpass-api.de`, `lz4.overpass-api.de`, `z.overpass-api.de`, `kumi.systems`, `maps.mail.ru`).
   - Projects WGS84 coordinates (lat, lon) to Unreal Engine Left-Handed Z-Up Cartesian space (+X=North, +Y=East, +Z=Up, 1 UU = 1 cm) with origin datum at Bakırköy Özgürlük Meydanı (40.98186° N, 28.87428° E, alt 25m).
   - Synthesizes 3D building heights via a 4-tier resolution engine (explicit tags -> levels * 3.2m -> semantic heuristics -> deterministic hash).
   - Normalizes road networks by hierarchy (arterial, secondary, residential, pedestrian plazas).
   - Persists intermediate normalized JSON (`data/bakirkoy_level_data.json`) with local disk caching and offline synthetic seed fallback.
2. **UE5 Procedural GIS Level Generator (`build_osm_level.py`)**:
   - Reads `data/bakirkoy_level_data.json` or runs embedded authentic Bakırköy GIS dataset.
   - Generates 100% solid exterior building blocks via Oriented Bounding Box (OBB) `StaticMeshActor` cubes (`/Engine/BasicShapes/Cube.Cube`) with Chaos `BlockAll` collision and flat walkable rooftops, strictly enforcing Rule C1 ("Building interiors strictly OFF-LIMITS").
   - Generates dual-layer road network: physical StaticMesh road slabs for visual surface & NavMesh walkability + `SplineComponent` actors for AI graph routing.
   - Places 4km x 4km arena floor, complete lighting/sky atmosphere, exactly 1 `NavMeshBoundsVolume`, exactly 10 `PlayerStart` actors, and >=10 tactical loot spawners.
   - Features dry-run simulation mode (`_MockUnrealModule`) enabling 100% offline static testability.
3. **Procedural Placeholder Character & Animation Pipeline (`setup_character_anims.py`)**:
   - Configures UE5 standard Manny/Quinn skeletal meshes on `BP_BRCharacter` and `BP_BRAIBotCharacter` CDOs with correct relative transform alignment ((0, 0, -90), (0, -90, 0)).
   - Procedurally authors master PBR faceless material `M_BRFacelessPlaceholder` and instances `MI_BRFacelessManny` (charcoal gray) and `MI_BRFacelessBot` (tactical orange-red for 10-bot distinction).
   - Establishes two-tier `AnimBlueprint` resolution (`ABP_BRCharacter` with Idle, Run, Jump, and Aim/UpperBody slot) and wires CDO `anim_class` and `animation_mode`.
   - Features dry-run simulation mode for standalone offline testability.

## Feature Inventory
| # | Feature | Description | Milestone | Source | Status |
|---|---------|-------------|-----------|--------|--------|
| 1 | OSM Overpass Querying | Fetch buildings & highways for Bakırköy via Overpass API with multi-endpoint failover | M-OSM-1 | Survey Explorer 1 | PLANNED |
| 2 | WGS84 to UE Projection | Pure-math local tangent plane projection to UE Left-Handed Z-Up cm coordinates | M-OSM-1 | Survey Explorer 1 | PLANNED |
| 3 | 4-Tier Height Synthesis | Resolve building heights using tags, levels, semantic heuristics, and deterministic hashing | M-OSM-1 | Survey Explorer 1 | PLANNED |
| 4 | GIS Caching & Offline Fallback | Persistent raw JSON caching & synthetic Bakırköy seed dataset | M-OSM-1 | Survey Explorer 1 | PLANNED |
| 5 | Level Lifecycle Management | Create & save `/Game/Maps/BakirkoyOSM.umap` with subsystem & library dual-path | M-OSM-2 | Survey Explorer 2 | PLANNED |
| 6 | Solid Exterior OBB Buildings | Procedural solid exterior building blocks with simple box collision & zero interior | M-OSM-2 | Survey Explorer 2 | PLANNED |
| 7 | Dual-Layer Road Network | StaticMesh road slabs & SplineComponent actors with hierarchical lane widths | M-OSM-2 | Survey Explorer 2 | PLANNED |
| 8 | Level Invariants & Spawners | 1 NavMeshBoundsVolume, 10 PlayerStarts, >=10 Loot spawners, 4km floor, lighting | M-OSM-2 | Survey Explorer 2 | PLANNED |
| 9 | Skeletal Mesh CDO Config | Assign SKM_Manny to BP_BRCharacter & BP_BRAIBotCharacter with proper transforms | M-CHAR-1 | Survey Explorer 3 | PLANNED |
| 10 | Faceless PBR Materials | Create M_BRFacelessPlaceholder, MI_BRFacelessManny, and MI_BRFacelessBot | M-CHAR-1 | Survey Explorer 3 | PLANNED |
| 11 | AnimBP Locomotion & Aiming | Configure ABP_BRCharacter with Idle, Run, Jump, Aim wired to ABRCharacter CDO | M-CHAR-1 | Survey Explorer 3 | PLANNED |
| 12 | End-to-End Multi-Agent Gate | Static analysis, dry-run simulation, contract validation, Review/Challenge/Audit | M-VERIFY | Survey Explorers 1-3 | PLANNED |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M-OSM-1 | OSM Data Acquisition Pipeline (`fetch_osm_data.py`) | Implement `fetch_osm_data.py` with Overpass query, failover, projection, height synthesis, cache, seed | None | IN_PROGRESS |
| M-OSM-2 | UE5 GIS Procedural Level Generator (`build_osm_level.py`) | Implement `build_osm_level.py` with OBB buildings, roads, floor, lighting, NavMeshBounds, PlayerStarts, dry-run | M-OSM-1 | PLANNED |
| M-CHAR-1 | Procedural Character & Anim Setup (`setup_character_anims.py`) | Implement `setup_character_anims.py` with SKM_Manny, faceless materials, AnimBP, CDO wiring, dry-run | None | IN_PROGRESS |
| M-VERIFY | Multi-Agent Review, Challenge & Forensic Audit Gate | Reviewers, Challengers, and Forensic Auditor verification and integrity gate | M-OSM-1, M-OSM-2, M-CHAR-1 | PLANNED |

## Interface Contracts
### `fetch_osm_data.py` ↔ `build_osm_level.py`
- Schema: JSON file at `data/bakirkoy_level_data.json`
- Top-level keys:
  * `metadata`: `{ datum: { lat, lon, alt_m, name }, ue_units: "1 UU = 1 cm", coordinate_mapping: { X: "+North", Y: "+East", Z: "+Up" }, bounds_ue: { min_x, max_x, min_y, max_y }, total_buildings, total_roads }`
  * `buildings`: `[ { id, name, type, levels, height_cm, centroid_ue: [x, y], footprint_ue: [[x, y], ...] } ]`
  * `roads`: `[ { id, name, type, width_cm, lanes, oneway, points_ue: [[x, y], ...] } ]`
- Fallback: `build_osm_level.py` embeds authentic fallback data for major Bakırköy landmarks if JSON is missing.

### `setup_character_anims.py` ↔ Blueprint & C++ Classes
- Inputs: `/Game/Blueprints/BP_BRCharacter`, `/Game/Blueprints/BP_BRAIBotCharacter`
- Material Assets: `/Game/Materials/M_BRFacelessPlaceholder`, `/Game/Materials/MI_BRFacelessManny`, `/Game/Materials/MI_BRFacelessBot`
- Animation Asset: `/Game/Characters/Mannequins/Animations/ABP_BRCharacter`
- Target Skeletal Mesh: `/Game/Characters/Mannequins/Meshes/SKM_Manny`
- Target CDO Properties:
  * `mesh.skeletal_mesh_asset = SKM_Manny`
  * `mesh.relative_location = (0, 0, -90)`
  * `mesh.relative_rotation = (0, -90, 0)`
  * `mesh.animation_mode = ANIMATION_BLUEPRINT`
  * `mesh.anim_class = ABP_BRCharacter_C`
  * `mesh.override_materials = [MI_BRFacelessManny]` (or `MI_BRFacelessBot` for AI bot)
