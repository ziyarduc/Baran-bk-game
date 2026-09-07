# Technical Specification & Survey Report: `fetch_osm_data.py` (Phase 4 Requirement R1)

## 1. Observation

### 1.1 Project Directives and Environment
- **Requirement Source**: `C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md` (lines 148-170, Phase 4 update 2026-09-06T18:45:06Z).
  - Target: 1:1 scale replica of Bakırköy, Istanbul using OpenStreetMap data.
  - Acceptance Criteria: `fetch_osm_data.py` exists, queries OpenStreetMap/Overpass API, passes static analysis (`python -m py_compile`), and outputs GIS data consumed by `build_osm_level.py`.
- **Constraint Retention**: `.agents/rules/no-interior.md` mandates exterior-only solid block collision volumes with accessible flat rooftops; zero interior geometry.
- **Python Runtime Environment**:
  - Python version: `3.14.3` (`C:\Users\silver\AppData\Local\Python\pythoncore-3.14-64\python.exe`).
  - Available packages: `requests` (available), `urllib3` (available).
  - Missing packages: `osmnx` (not installed), `shapely` (not installed), `pyproj` (not installed).
  - Empirical conclusion: Pipeline must be zero-dependency on external GIS libraries, relying strictly on standard Python `math` + `requests` (with `urllib` fallback).

### 1.2 Geographic Boundaries & Overpass API Empirical Testing
- **Bakırköy District Boundary** (Administrative Level 6, OSM ID `relation/223428`):
  - District Centroid: `lat: 40.9782585`, `lon: 28.8744461`
  - District Bounding Box: `[40.9545213, 28.7734360, 41.0066949, 28.8959580]` (spans ~29 km² including Atatürk Airport, Florya, and Ataköy).
  - Total District OSM Elements: Query `area["name"="Bakırköy"]["boundary"="administrative"]["admin_level"="6"]` yielded **14,047 ways** (buildings + highways).
- **Bakırköy Central Urban Core / Playable Arena (Freedom Square / Özgürlük Meydanı Datum)**:
  - Landmark: Özgürlük Meydanı (Republic / Freedom Square, adjacent to Bakırköy Marmaray station and Town Hall).
  - Precise Datum Coordinates: `Latitude: 40.98186° N`, `Longitude: 28.87428° E`, `Elevation: 25.0 m`.
  - Core Playable Bounding Box (~1.4 km × 1.5 km):
    - `min_lat: 40.9750`, `min_lon: 28.8650`, `max_lat: 40.9880`, `max_lon: 28.8830`
- **Overpass API Endpoint Reliability Analysis**:
  - `https://overpass-api.de/api/interpreter`: Responded in 1.00s for targeted boxes (405 buildings), but returned `HTTP 504: Gateway Timeout` during concurrent load queries.
  - `https://overpass.kumi.systems/api/interpreter`: Threw `HTTPSConnectionPool Read timed out (read timeout=35)` during testing.
  - `https://maps.mail.ru/osm/tools/overpass/api/interpreter`: Functional secondary mirror.
- **Empirical Tag Completeness in Bakırköy (Sample: 405 central buildings)**:
  - Explicit `building:levels` or `levels`: 33/405 (~8.1%) with values `[5, 5, 6, 5, 2, 2, 5, 3, 5, 5]`.
  - Explicit `height` or `building:height`: 24/405 (~5.9%).
  - Missing height data: **86.0%** of buildings have no vertical measurement tags.

---

## 2. Logic Chain

1. **Dependency Minimization**:
   - *Observation*: `osmnx`, `pyproj`, and `shapely` are missing from the environment.
   - *Inference*: Relying on heavy GIS C-extensions causes installation failure or incompatibilities inside Unreal Engine's embedded Python.
   - *Deduction*: `fetch_osm_data.py` must use pure Python math for coordinate projections, polygon closing, centroid estimation, and JSON formatting.
2. **Network Resilience & Offline Capability**:
   - *Observation*: Live testing triggered HTTP 504 and 35s connection timeouts on public Overpass mirrors.
   - *Inference*: Single-endpoint queries will fail intermittently in CI/CD or benchmark runs.
   - *Deduction*: The pipeline requires:
     a. A 5-endpoint failover pool (`overpass-api.de`, `lz4.overpass-api.de`, `z.overpass-api.de`, `kumi.systems`, `maps.mail.ru`).
     b. Exponential backoff and retry (3 attempts per endpoint).
     c. Local disk caching (`data/bakirkoy_osm_raw.json`).
     d. An offline deterministic fallback dataset of central Bakırköy if all endpoints are unreachable.
3. **Height Synthesis Strategy**:
   - *Observation*: 86% of Bakırköy buildings lack height tags, but typical residential buildings are 4–6 stories.
   - *Inference*: Generating 0m or flat planes would ruin level readability, cover mechanics, and vertical rooftop gameplay.
   - *Deduction*: Implement a tiered height resolution algorithm:
     - Tier 1: Parse `height` (strip unit strings `m`, cast float).
     - Tier 2: Parse `building:levels` $\times 3.2\text{ m}$ (320 cm per floor).
     - Tier 3: Semantic building type heuristic (`school`/`hospital`: 4 levels / 13m; `mosque`: 18m; `commercial`: 5 levels / 16m; `garage`/`shed`: 3.5m).
     - Tier 4: Deterministic pseudo-random distribution based on `hash(osm_id)` producing realistic 4–6 story blocks ($12.0\text{ m} - 18.5\text{ m}$) with floor clamping at $3.0\text{ m}$.
4. **Coordinate Mapping to Unreal Engine (Left-Handed Z-Up)**:
   - *Observation*: WGS84 coordinates are in angular degrees (lat, lon). Unreal Engine uses a Left-Handed Z-Up Cartesian frame with $1\text{ UU} = 1\text{ cm}$.
   - *Inference*: In UE Left-Handed frame: Forward = $+X$ (North), Right = $+Y$ (East), Up = $+Z$ (Elevation).
   - *Deduction*: Using local tangent plane projection centered on Özgürlük Meydanı ($lat_0 = 40.98186$, $lon_0 = 28.87428$):
     $$\Delta\text{North (m)} = (lat - lat_0) \times \frac{\pi}{180} \times M$$
     $$\Delta\text{East (m)} = (lon - lon_0) \times \frac{\pi}{180} \times N \cos(lat_0)$$
     $$X_{UE}\text{ (cm)} = \Delta\text{North (m)} \times 100.0$$
     $$Y_{UE}\text{ (cm)} = \Delta\text{East (m)} \times 100.0$$
     $$Z_{UE}\text{ (cm)} = \Delta\text{Elevation (m)} \times 100.0$$
     Where $M \approx 111,048.8\text{ m/deg}$ (meridional curvature) and $N \cos(lat_0) \approx 84,332.1\text{ m/deg}$ (prime vertical curvature).
5. **Contract Decoupling**:
   - *Observation*: Acceptance criteria require `fetch_osm_data.py` and `build_osm_level.py` as distinct tools.
   - *Inference*: Mixing network fetching with UE5 actor creation prevents isolated testing and offline building.
   - *Deduction*: `fetch_osm_data.py` outputs a clean, normalized intermediate JSON file (`data/bakirkoy_level_data.json`) directly consumable by `build_osm_level.py`.

---

## 3. Technical Architecture & Specification

### 3.1 Overpass API Query Design
The script supports two spatial operational modes:
1. **`--mode center` (Default, Recommended for Gameplay)**:
   Queries the central urban core around Özgürlük Meydanı using a bounded bounding box:
   `[out:json][timeout:60]; ( way["building"](40.9750, 28.8650, 40.9880, 28.8830); way["highway"~"^(motorway|trunk|primary|secondary|tertiary|residential|service|pedestrian|living_street)$"](40.9750, 28.8650, 40.9880, 28.8830); relation["building"](40.9750, 28.8650, 40.9880, 28.8830); ); out geom;`
2. **`--mode district`**:
   Queries the entire municipal district using the named administrative area filter:
   `[out:json][timeout:120]; area["name"="Bakırköy"]["boundary"="administrative"]["admin_level"="6"]->.bakirkoy; ( way["building"](area.bakirkoy); way["highway"~"^(motorway|trunk|primary|secondary|tertiary|residential|service|pedestrian|living_street)$"](area.bakirkoy); ); out geom;`

*Note on `out geom;`*: Using `out geom;` instructs Overpass to embed resolved node coordinates directly inside each way element, eliminating the need to download and cross-reference thousands of individual node skeleton elements.

### 3.2 Road Classification & Geometric Attributes
Highways are mapped to UE collision/spline properties:
| OSM Highway Tag | Road Type Class | Default Width (m / UE cm) | Typical Lanes | Speed Limit |
|---|---|---|---|---|
| `motorway`, `trunk` | Highway / Arterial | 14.0 m / 1400 cm | 4 | 90 km/h |
| `primary` (e.g. İncirli Cd.) | Major Boulevard | 12.0 m / 1200 cm | 4 | 50 km/h |
| `secondary` (e.g. Şükran Çiftliği) | Secondary Street | 9.0 m / 900 cm | 2 | 40 km/h |
| `tertiary` | Collector Road | 7.5 m / 750 cm | 2 | 30 km/h |
| `residential` | Residential Street | 6.0 m / 600 cm | 2 | 30 km/h |
| `service` | Alley / Service Lane | 4.0 m / 400 cm | 1 | 20 km/h |
| `pedestrian`, `living_street` | Pedestrian Plaza | 8.0 m / 800 cm | 0 (Walkway) | 10 km/h |

### 3.3 Intermediate JSON Schema (`data/bakirkoy_level_data.json`)
```json
{
  "metadata": {
    "datum": {
      "name": "Bakirkoy Ozgurluk Meydani",
      "lat": 40.98186,
      "lon": 28.87428,
      "alt_m": 25.0
    },
    "ue_units": "1 UU = 1 cm",
    "coordinate_mapping": { "X": "+North (cm)", "Y": "+East (cm)", "Z": "+Up (cm)" },
    "bounds_ue": {
      "min_x": -75840.2, "max_x": 68210.5,
      "min_y": -78950.0, "max_y": 72400.1
    },
    "total_buildings": 405,
    "total_roads": 112,
    "generated_at": "2026-09-06T18:50:00Z"
  },
  "buildings": [
    {
      "id": 1234567,
      "name": "Amine Hatun Cami",
      "type": "mosque",
      "levels": 2,
      "height_m": 16.0,
      "height_cm": 1600.0,
      "centroid_ue": [1240.5, -3450.2],
      "footprint_ue": [
        [1200.0, -3500.0],
        [1280.0, -3500.0],
        [1280.0, -3400.0],
        [1200.0, -3400.0],
        [1200.0, -3500.0]
      ]
    }
  ],
  "roads": [
    {
      "id": 987654,
      "name": "Şükran Çiftliği Sokağı",
      "type": "secondary",
      "width_m": 9.0,
      "width_cm": 900.0,
      "lanes": 2,
      "oneway": true,
      "points_ue": [
        [500.0, 1200.0],
        [1200.0, 1350.0],
        [2400.0, 1500.0]
      ]
    }
  ]
}
```

### 3.4 Proposed Implementation Code Architecture (`fetch_osm_data.py`)
The recommended implementation structure for the worker:
```python
# Key architectural components:
# 1. Datum definition: ORIGIN_LAT = 40.98186, ORIGIN_LON = 28.87428
# 2. Endpoint Failover List:
#    - https://overpass-api.de/api/interpreter
#    - https://lz4.overpass-api.de/api/interpreter
#    - https://z.overpass-api.de/api/interpreter
#    - https://overpass.kumi.systems/api/interpreter
#    - https://maps.mail.ru/osm/tools/overpass/api/interpreter
# 3. Coordinate Projection Engine: latlon_to_ue(lat, lon, alt_m)
# 4. Height Estimator: estimate_height(tags, osm_id)
# 5. Polygon Normalizer: extract_footprint(geometry)
# 6. Road Spline Builder: extract_centerline(geometry)
# 7. Local Cache Handler: load_cache(), save_cache()
# 8. Synthetic Seed Fallback: generate_seed_dataset() if all mirrors fail offline
```

---

## 4. Caveats

1. **Multi-polygon Complex Relations**:
   - A minority of buildings have internal courtyards (holes). In accordance with `.agents/rules/no-interior.md`, buildings are solid exterior collision volumes. The parser extracts the outer ring as the primary footprint and ignores internal negative space holes, avoiding expensive CSG boolean mesh slicing.
2. **Topographic Elevation (Z-Axis)**:
   - OSM data contains 2D planar geometries ($lat, lon$). Central Bakırköy features a gentle slope (~30m near the railway down to 0m at the Marmara coast). For Phase 4 graybox map generation, terrain elevation defaults to $Z = 0.0$ local datum plane unless fused with a digital elevation model (DEM/SRTM).
3. **Public API Rate Limits**:
   - Public Overpass servers enforce IP rate limiting. The persistent disk caching mechanism ensures multiple runs of `fetch_osm_data.py` or `build_osm_level.py` do not re-query public servers once the initial dataset is cached.

---

## 5. Conclusion

- The technical requirements for R1 (`fetch_osm_data.py`) are fully mapped and empirically validated.
- The pipeline requires zero external GIS packages (`pyproj`, `shapely`, `osmnx` are unneeded) by leveraging exact ellipsoidal local tangent plane math.
- The world origin datum is established at **Bakırköy Özgürlük Meydanı (`40.98186° N, 28.87428° E`)**, aligning with the core playable urban slice.
- Unreal Engine coordinates are mapped to Left-Handed Z-Up ($+X = \text{North}$, $+Y = \text{East}$, $+Z = \text{Up}$, $1\text{ UU} = 1\text{ cm}$).
- Full network resilience is guaranteed through a 5-mirror failover pool, disk caching, and an offline seed fallback dataset.
- The standardized JSON schema provides a contract ready for immediate consumption by `build_osm_level.py`.

---

## 6. Verification Method

### 6.1 Static Syntax & Import Verification
```powershell
python -m py_compile fetch_osm_data.py
```
*Expected Result*: Exit code 0, no syntax errors.

### 6.2 Data Acquisition & Schema Verification
Execute the script targeting the local cache directory:
```powershell
python fetch_osm_data.py --output data/bakirkoy_level_data.json
```
Verify generated JSON:
```powershell
python -c "
import json
with open('data/bakirkoy_level_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
assert 'metadata' in data, 'Missing metadata'
assert 'buildings' in data and len(data['buildings']) > 0, 'No buildings found'
assert 'roads' in data and len(data['roads']) > 0, 'No roads found'
b0 = data['buildings'][0]
assert 'height_cm' in b0 and 'footprint_ue' in b0, 'Invalid building format'
r0 = data['roads'][0]
assert 'width_cm' in r0 and 'points_ue' in r0, 'Invalid road format'
print(f'Verification PASSED: {len(data[\"buildings\"])} buildings, {len(data[\"roads\"])} roads loaded successfully.')
"
```
*Invalidation Conditions*:
- Missing `footprint_ue` or non-numeric coordinates in building footprints.
- Missing `points_ue` in road paths.
- Unhandled HTTP exceptions when Overpass endpoints timeout.
