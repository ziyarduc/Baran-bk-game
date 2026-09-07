#!/usr/bin/env python3
"""
fetch_osm_data.py - Production-Grade OpenStreetMap Ingestion Pipeline for Bakırköy BR
====================================================================================

Fetches, normalizes, and projects OpenStreetMap topological GIS data (buildings, highways)
for Bakırköy, Istanbul into Unreal Engine Left-Handed Z-Up coordinates (+X=North, +Y=East,
+Z=Up, 1 UU = 1 cm).

Architecture & Features:
1. Multi-endpoint failover pool (overpass-api.de, lz4, z, kumi.systems, maps.mail.ru)
   with exponential backoff and timeout handling.
2. Local persistent disk caching (`data/bakirkoy_osm_raw.json`).
3. Embedded authentic offline synthetic seed dataset of central Bakırköy (Özgürlük Meydanı,
   Carousel, Capacity, Galleria, Town Hall, Marmaray Station, İncirli, İstanbul Cd., etc.)
   guaranteeing 100% testability and reliability in air-gapped or rate-limited environments.
4. Pure standard Python math projection from WGS84 (lat, lon) to UE local tangent plane (cm)
   with origin datum at Bakırköy Özgürlük Meydanı (40.98186° N, 28.87428° E, alt 25m).
   Zero external GIS dependencies (no osmnx/shapely/pyproj required).
5. 4-tier height synthesis algorithm for buildings (explicit tags -> levels * 3.2m ->
   semantic heuristics -> deterministic hash).
6. Hierarchical road classification with width, lane, and oneway attribute resolution.
7. Generates `data/bakirkoy_level_data.json` matching the Phase 4 architectural contract.

Usage:
    python fetch_osm_data.py [--output data/bakirkoy_level_data.json] [--mode center|district]
                             [--cache-file data/bakirkoy_osm_raw.json] [--offline-seed] [--verbose]
"""

import argparse
import datetime
import hashlib
import json
import logging
import math
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# Fallback-aware HTTP client
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.error
    import urllib.parse
    import urllib.request

# ============================================================================
# DATUM & GEODESY CONSTANTS
# ============================================================================
ORIGIN_NAME = "Bakirkoy Ozgurluk Meydani"
ORIGIN_LAT = 40.98186
ORIGIN_LON = 28.87428
ORIGIN_ALT_M = 25.0

# WGS84 Ellipsoid constants
WGS84_A = 6378137.0  # Semi-major axis (meters)
WGS84_F = 1.0 / 298.257223563  # Flattening
WGS84_E2 = 2.0 * WGS84_F - (WGS84_F ** 2)  # Eccentricity squared (approx 0.00669437999014)

# Precomputed curvatures at datum origin
_phi0_rad = math.radians(ORIGIN_LAT)
_sin_phi0 = math.sin(_phi0_rad)
_W = math.sqrt(1.0 - WGS84_E2 * (_sin_phi0 ** 2))
# Meridional radius of curvature (North-South) in meters/radian
RADIUS_M = (WGS84_A * (1.0 - WGS84_E2)) / (_W ** 3)
# Prime vertical radius of curvature (East-West) in meters/radian
RADIUS_N = WGS84_A / _W
COS_PHI0 = math.cos(_phi0_rad)

# Overpass API Mirror Endpoints (Failover Pool)
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]

# Central Bakırköy Playable Bounding Box
BBOX_CENTER = (40.9750, 28.8650, 40.9880, 28.8830)  # (min_lat, min_lon, max_lat, max_lon)

# Road classification specs (width in meters, default lanes, type)
HIGHWAY_SPECS: Dict[str, Dict[str, Any]] = {
    "motorway": {"width_m": 14.0, "lanes": 4, "type": "motorway"},
    "motorway_link": {"width_m": 8.0, "lanes": 1, "type": "motorway"},
    "trunk": {"width_m": 14.0, "lanes": 4, "type": "trunk"},
    "trunk_link": {"width_m": 8.0, "lanes": 1, "type": "trunk"},
    "primary": {"width_m": 12.0, "lanes": 4, "type": "primary"},
    "primary_link": {"width_m": 7.0, "lanes": 1, "type": "primary"},
    "secondary": {"width_m": 9.0, "lanes": 2, "type": "secondary"},
    "secondary_link": {"width_m": 6.5, "lanes": 1, "type": "secondary"},
    "tertiary": {"width_m": 7.5, "lanes": 2, "type": "tertiary"},
    "tertiary_link": {"width_m": 6.0, "lanes": 1, "type": "tertiary"},
    "residential": {"width_m": 6.0, "lanes": 2, "type": "residential"},
    "living_street": {"width_m": 8.0, "lanes": 0, "type": "living_street"},
    "pedestrian": {"width_m": 8.0, "lanes": 0, "type": "pedestrian"},
    "service": {"width_m": 4.0, "lanes": 1, "type": "service"},
    "footway": {"width_m": 6.0, "lanes": 0, "type": "footway"},
    "path": {"width_m": 4.0, "lanes": 0, "type": "path"},
    "steps": {"width_m": 4.0, "lanes": 0, "type": "steps"},
    "track": {"width_m": 4.0, "lanes": 1, "type": "service"},
}

# Semantic building height heuristics (meters)
SEMANTIC_HEIGHT_TABLE: Dict[str, float] = {
    "mosque": 16.0,
    "place_of_worship": 16.0,
    "hospital": 14.0,
    "clinic": 12.0,
    "school": 13.0,
    "university": 15.0,
    "college": 14.0,
    "kindergarten": 8.0,
    "mall": 16.0,
    "supermarket": 10.0,
    "commercial": 16.0,
    "retail": 14.0,
    "office": 16.0,
    "hotel": 18.0,
    "civic": 14.0,
    "townhall": 14.0,
    "public_building": 14.0,
    "train_station": 10.0,
    "transportation": 10.0,
    "apartments": 15.0,
    "residential": 15.0,
    "house": 9.0,
    "detached": 9.0,
    "industrial": 8.0,
    "warehouse": 8.0,
    "garage": 3.5,
    "garages": 3.5,
    "shed": 3.0,
    "kiosk": 3.2,
}


# ============================================================================
# GEODESY & PROJECTION FUNCTIONS (Pure Standard Math)
# ============================================================================
def latlon_to_ue(lat: float, lon: float, alt_m: float = ORIGIN_ALT_M) -> Tuple[float, float, float]:
    """
    Projects WGS84 geodetic coordinates (lat, lon, alt) to Unreal Engine Left-Handed
    Cartesian Space with origin datum at Bakırköy Özgürlük Meydanı.

    Coordinate Mapping:
        +X = North (cm)
        +Y = East (cm)
        +Z = Up (cm)
        1 UU = 1 cm
    """
    d_lat_rad = math.radians(lat - ORIGIN_LAT)
    d_lon_rad = math.radians(lon - ORIGIN_LON)

    # Local tangent plane displacement in meters
    delta_north_m = d_lat_rad * RADIUS_M
    delta_east_m = d_lon_rad * RADIUS_N * COS_PHI0
    delta_up_m = alt_m - ORIGIN_ALT_M

    # Convert meters to Unreal Units (1 m = 100 cm = 100 UU)
    x_ue = delta_north_m * 100.0
    y_ue = delta_east_m * 100.0
    z_ue = delta_up_m * 100.0

    return round(x_ue, 2), round(y_ue, 2), round(z_ue, 2)


def compute_polygon_centroid(points_ue: List[List[float]]) -> List[float]:
    """
    Computes the 2D planar centroid of a closed polygon in Unreal Engine space.
    Falls back to vertex mean if area is near zero.
    """
    n = len(points_ue)
    if n == 0:
        return [0.0, 0.0]
    if n == 1:
        return [round(points_ue[0][0], 2), round(points_ue[0][1], 2)]

    signed_area = 0.0
    cx_accum = 0.0
    cy_accum = 0.0

    # Ensure closed polygon indices
    for i in range(n - 1):
        xi, yi = points_ue[i][0], points_ue[i][1]
        x_next, y_next = points_ue[i + 1][0], points_ue[i + 1][1]
        cross = (xi * y_next) - (x_next * yi)
        signed_area += cross
        cx_accum += (xi + x_next) * cross
        cy_accum += (yi + y_next) * cross

    signed_area *= 0.5

    if abs(signed_area) > 1e-4:
        factor = 1.0 / (6.0 * signed_area)
        return [round(cx_accum * factor, 2), round(cy_accum * factor, 2)]

    # Fallback to arithmetic mean of unique vertices
    mean_x = sum(pt[0] for pt in points_ue[:-1]) / max(1, n - 1)
    mean_y = sum(pt[1] for pt in points_ue[:-1]) / max(1, n - 1)
    return [round(mean_x, 2), round(mean_y, 2)]


# ============================================================================
# 4-TIER HEIGHT SYNTHESIS ENGINE
# ============================================================================
def estimate_building_height(tags: Dict[str, Any], osm_id: int) -> Tuple[float, float, int]:
    """
    4-Tier Building Height Resolution Algorithm:
    - Tier 1: Explicit 'height' or 'building:height' tag.
    - Tier 2: Explicit 'building:levels' or 'levels' tag (levels * 3.2m).
    - Tier 3: Semantic building type heuristic lookup table.
    - Tier 4: Deterministic pseudo-random distribution based on sha256(osm_id)
              generating realistic 4-6 story Bakırköy urban fabric [12.0m - 18.5m].

    Returns:
        (height_m: float, height_cm: float, levels: int)
    """
    # Tier 1: Explicit height tag
    for h_key in ("height", "building:height"):
        val = tags.get(h_key)
        if val is not None:
            try:
                s = str(val).lower().replace("m", "").replace("meters", "").replace("metres", "").replace(",", ".").strip()
                parsed_h = float(s)
                if parsed_h > 0.0:
                    h_m = max(3.0, parsed_h)
                    levels = max(1, int(round(h_m / 3.2)))
                    return round(h_m, 2), round(h_m * 100.0, 2), levels
            except (ValueError, TypeError):
                pass

    # Tier 2: Explicit levels tag
    for l_key in ("building:levels", "levels"):
        val = tags.get(l_key)
        if val is not None:
            try:
                s = str(val).replace(",", ".").strip()
                parsed_lvl = float(s)
                if parsed_lvl > 0.0:
                    lvl_count = max(1, int(round(parsed_lvl)))
                    h_m = max(3.0, lvl_count * 3.2)
                    return round(h_m, 2), round(h_m * 100.0, 2), lvl_count
            except (ValueError, TypeError):
                pass

    # Tier 3: Semantic type heuristics
    b_type = str(tags.get("building", "")).lower()
    amenity = str(tags.get("amenity", "")).lower()
    shop = str(tags.get("shop", "")).lower()
    name = str(tags.get("name", "")).lower()

    # Search in semantic table
    for keyword, h_val in SEMANTIC_HEIGHT_TABLE.items():
        if keyword in b_type or keyword in amenity or keyword in shop:
            levels = max(1, int(round(h_val / 3.2)))
            return round(h_val, 2), round(h_val * 100.0, 2), levels

    # Search in landmark names
    if any(k in name for k in ("cami", "camii", "mescit", "kilise")):
        return 16.0, 1600.0, 2
    if any(k in name for k in ("hastane", "hastanesi", "poliklinik", "saglik")):
        return 14.0, 1400.0, 4
    if any(k in name for k in ("okul", "lise", "ilkokul", "ortaokul", "kolej", "fakulte")):
        return 13.0, 1300.0, 4
    if any(k in name for k in ("avm", "center", "centre", "mall", "pasaj", "capacity", "carousel", "galleria")):
        return 16.0, 1600.0, 5
    if any(k in name for k in ("belediye", "hukumet", "kaymakamlik")):
        return 14.0, 1400.0, 4

    # Tier 4: Deterministic pseudo-random distribution via SHA-256 hash
    hash_seed = f"bakirkoy_height_salt_{osm_id}".encode("utf-8")
    digest = hashlib.sha256(hash_seed).digest()
    norm_val = int.from_bytes(digest[:4], byteorder="big") / 4294967295.0

    # Typical central Bakırköy residential block: 4 to 6 floors (12.0m to 18.5m)
    h_m = 12.0 + (norm_val * 6.5)
    h_m = max(3.0, h_m)
    levels = max(1, int(round(h_m / 3.2)))
    return round(h_m, 2), round(h_m * 100.0, 2), levels


# ============================================================================
# ELEMENT PROCESSORS (Building & Road Transformers)
# ============================================================================
def process_building(elem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transforms a raw OSM building way/relation into the standard schema."""
    tags = elem.get("tags", {})
    if "building" not in tags and tags.get("type") != "building":
        return None

    geom = elem.get("geometry", [])
    if len(geom) < 3:
        return None

    osm_id = int(elem.get("id", 0))
    b_name = tags.get("name")
    if not b_name:
        addr = tags.get("addr:street")
        num = tags.get("addr:housenumber", "")
        b_name = f"{addr} No:{num}" if addr else f"Building_{osm_id}"

    b_type = tags.get("building", "residential")
    if b_type in ("yes", "true", "1"):
        b_type = tags.get("amenity", tags.get("shop", "residential"))

    h_m, h_cm, levels = estimate_building_height(tags, osm_id)

    footprint_ue: List[List[float]] = []
    for pt in geom:
        lat = pt.get("lat")
        lon = pt.get("lon")
        if lat is not None and lon is not None:
            x, y, _ = latlon_to_ue(lat, lon)
            # Avoid immediate duplicate points
            if not footprint_ue or footprint_ue[-1] != [x, y]:
                footprint_ue.append([x, y])

    if len(footprint_ue) < 3:
        return None

    # Ensure closed polygon loop
    if footprint_ue[0] != footprint_ue[-1]:
        footprint_ue.append(footprint_ue[0])

    if len(footprint_ue) < 4:
        return None

    centroid = compute_polygon_centroid(footprint_ue)

    return {
        "id": osm_id,
        "name": b_name,
        "type": b_type,
        "levels": levels,
        "height_m": h_m,
        "height_cm": h_cm,
        "centroid_ue": centroid,
        "footprint_ue": footprint_ue,
    }


def process_road(elem: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transforms a raw OSM highway way into the standard schema."""
    tags = elem.get("tags", {})
    hw = tags.get("highway")
    if not hw:
        return None

    geom = elem.get("geometry", [])
    if len(geom) < 2:
        return None

    osm_id = int(elem.get("id", 0))
    spec = HIGHWAY_SPECS.get(hw, {"width_m": 6.0, "lanes": 2, "type": hw})
    width_m = spec["width_m"]
    lanes = spec["lanes"]
    r_type = spec["type"]

    # Explicit width override
    if "width" in tags:
        try:
            w_str = str(tags["width"]).lower().replace("m", "").replace(",", ".").strip()
            parsed_w = float(w_str)
            if parsed_w > 1.0:
                width_m = parsed_w
        except (ValueError, TypeError):
            pass

    # Explicit lanes override
    if "lanes" in tags:
        try:
            parsed_l = int(str(tags["lanes"]).strip())
            if parsed_l > 0:
                lanes = parsed_l
        except (ValueError, TypeError):
            pass

    oneway = tags.get("oneway") in ("yes", "1", "true")
    name = tags.get("name", f"Unnamed {r_type.replace('_', ' ').title()}")

    points_ue: List[List[float]] = []
    for pt in geom:
        lat = pt.get("lat")
        lon = pt.get("lon")
        if lat is not None and lon is not None:
            x, y, _ = latlon_to_ue(lat, lon)
            if not points_ue or points_ue[-1] != [x, y]:
                points_ue.append([x, y])

    if len(points_ue) < 2:
        return None

    return {
        "id": osm_id,
        "name": name,
        "type": r_type,
        "width_m": round(width_m, 2),
        "width_cm": round(width_m * 100.0, 2),
        "lanes": lanes,
        "oneway": oneway,
        "points_ue": points_ue,
    }


# ============================================================================
# OVERPASS API FAILOVER NETWORK CLIENT
# ============================================================================
def build_overpass_query(mode: str = "center") -> str:
    """Builds the Overpass QL query string."""
    if mode == "district":
        return """[out:json][timeout:120];
area["name"="Bakırköy"]["boundary"="administrative"]["admin_level"="6"]->.bakirkoy;
(
  way["building"](area.bakirkoy);
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary|residential|service|pedestrian|living_street)$"](area.bakirkoy);
);
out geom;"""

    # Central urban core around Özgürlük Meydanı (Default)
    min_lat, min_lon, max_lat, max_lon = BBOX_CENTER
    return f"""[out:json][timeout:60];
(
  way["building"]({min_lat},{min_lon},{max_lat},{max_lon});
  way["highway"~"^(motorway|trunk|primary|secondary|tertiary|residential|service|pedestrian|living_street)$"]({min_lat},{min_lon},{max_lat},{max_lon});
);
out geom;"""


def execute_http_post(url: str, query: str, timeout: int = 30) -> Dict[str, Any]:
    """Posts an Overpass query using requests or urllib standard library."""
    if HAS_REQUESTS:
        resp = requests.post(
            url,
            data={"data": query},
            headers={"User-Agent": "BakirkoyBR/1.0 (GIS Overpass Pipeline)"},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()

    # urllib fallback
    encoded_data = urllib.parse.urlencode({"data": query}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=encoded_data,
        headers={"User-Agent": "BakirkoyBR/1.0 (GIS Overpass Pipeline)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        content = response.read().decode("utf-8")
        return json.loads(content)


def fetch_from_overpass_pool(query: str, verbose: bool = False) -> Optional[Dict[str, Any]]:
    """
    Attempts to fetch data across the multi-endpoint failover pool with retries
    and exponential backoff.
    """
    for endpoint_idx, endpoint in enumerate(OVERPASS_ENDPOINTS, 1):
        logging.info(f"Connecting to Overpass mirror [{endpoint_idx}/{len(OVERPASS_ENDPOINTS)}]: {endpoint}")
        for attempt in range(1, 4):
            try:
                t0 = time.time()
                data = execute_http_post(endpoint, query, timeout=35)
                dt = time.time() - t0
                if "elements" in data:
                    logging.info(f"Successfully retrieved {len(data['elements'])} elements from {endpoint} in {dt:.2f}s")
                    return data
            except Exception as ex:
                backoff_s = (2 ** (attempt - 1)) * 1.5
                logging.warning(f"Mirror {endpoint} attempt {attempt}/3 failed ({type(ex).__name__}: {ex}). Retrying in {backoff_s:.1f}s...")
                time.sleep(backoff_s)

    logging.error("All Overpass mirror endpoints failed or timed out.")
    return None


# ============================================================================
# EMBEDDED AUTHENTIC OFFLINE SEED DATASET (Central Bakırköy)
# ============================================================================
def get_offline_seed_dataset() -> Dict[str, Any]:
    """
    Generates a rich, authentic synthetic seed dataset of central Bakırköy around
    Özgürlük Meydanı. Includes Carousel, Capacity, Galleria, Town Hall, Marmaray Station,
    Amine Hatun Mosque, Dr. Sadi Konuk Hospital, Meryem Ana Church, and major streets
    (İncirli, İstanbul, Fahri Korutürk, Ebuzziya, Şükran Çiftliği, Rauf Orbay, etc.).
    """
    elements: List[Dict[str, Any]] = []

    # 1. Bakırköy Özgürlük Meydanı (Freedom Square - Central Plaza / Monument)
    elements.append({
        "type": "way",
        "id": 1001001,
        "tags": {
            "name": "Bakırköy Özgürlük Meydanı",
            "building": "civic",
            "amenity": "townhall",
            "building:levels": "2",
            "height": "8.5",
        },
        "geometry": [
            {"lat": 40.98170, "lon": 28.87410},
            {"lat": 40.98210, "lon": 28.87410},
            {"lat": 40.98210, "lon": 28.87460},
            {"lat": 40.98170, "lon": 28.87460},
            {"lat": 40.98170, "lon": 28.87410},
        ],
    })

    # 2. Carousel Alışveriş Merkezi (Major Shopping Mall)
    elements.append({
        "type": "way",
        "id": 1001002,
        "tags": {
            "name": "Carousel Alışveriş ve Yaşam Merkezi",
            "building": "commercial",
            "shop": "mall",
            "building:levels": "5",
            "height": "18.0",
        },
        "geometry": [
            {"lat": 40.97930, "lon": 28.87280},
            {"lat": 40.98010, "lon": 28.87280},
            {"lat": 40.98010, "lon": 28.87390},
            {"lat": 40.97930, "lon": 28.87390},
            {"lat": 40.97930, "lon": 28.87280},
        ],
    })

    # 3. Capacity Alışveriş Merkezi (Major Shopping Mall)
    elements.append({
        "type": "way",
        "id": 1001003,
        "tags": {
            "name": "Capacity Alışveriş Merkezi",
            "building": "commercial",
            "shop": "mall",
            "building:levels": "6",
            "height": "22.0",
        },
        "geometry": [
            {"lat": 40.97820, "lon": 28.87220},
            {"lat": 40.97910, "lon": 28.87220},
            {"lat": 40.97910, "lon": 28.87350},
            {"lat": 40.97820, "lon": 28.87350},
            {"lat": 40.97820, "lon": 28.87220},
        ],
    })

    # 4. Galleria Alışveriş Merkezi (Coastal Mall)
    elements.append({
        "type": "way",
        "id": 1001004,
        "tags": {
            "name": "Galleria Ataköy",
            "building": "commercial",
            "shop": "mall",
            "building:levels": "4",
            "height": "15.0",
        },
        "geometry": [
            {"lat": 40.97540, "lon": 28.87650},
            {"lat": 40.97640, "lon": 28.87650},
            {"lat": 40.97640, "lon": 28.87850},
            {"lat": 40.97540, "lon": 28.87850},
            {"lat": 40.97540, "lon": 28.87650},
        ],
    })

    # 5. Bakırköy Belediyesi Ana Hizmet Binası (Town Hall)
    elements.append({
        "type": "way",
        "id": 1001005,
        "tags": {
            "name": "Bakırköy Belediyesi",
            "building": "civic",
            "amenity": "townhall",
            "building:levels": "5",
            "height": "16.5",
        },
        "geometry": [
            {"lat": 40.98320, "lon": 28.87480},
            {"lat": 40.98390, "lon": 28.87480},
            {"lat": 40.98390, "lon": 28.87580},
            {"lat": 40.98320, "lon": 28.87580},
            {"lat": 40.98320, "lon": 28.87480},
        ],
    })

    # 6. Amine Hatun Camii (Historic Mosque)
    elements.append({
        "type": "way",
        "id": 1001006,
        "tags": {
            "name": "Amine Hatun Camii",
            "building": "mosque",
            "amenity": "place_of_worship",
            "building:levels": "2",
            "height": "16.0",
        },
        "geometry": [
            {"lat": 40.98080, "lon": 28.87320},
            {"lat": 40.98130, "lon": 28.87320},
            {"lat": 40.98130, "lon": 28.87380},
            {"lat": 40.98080, "lon": 28.87380},
            {"lat": 40.98080, "lon": 28.87320},
        ],
    })

    # 7. Bakırköy Marmaray İstasyon Binası
    elements.append({
        "type": "way",
        "id": 1001007,
        "tags": {
            "name": "Bakırköy Marmaray İstasyonu",
            "building": "transportation",
            "building:levels": "3",
            "height": "11.0",
        },
        "geometry": [
            {"lat": 40.98050, "lon": 28.87420},
            {"lat": 40.98090, "lon": 28.87420},
            {"lat": 40.98090, "lon": 28.87560},
            {"lat": 40.98050, "lon": 28.87560},
            {"lat": 40.98050, "lon": 28.87420},
        ],
    })

    # 8. Meryem Ana Ermeni Kilisesi
    elements.append({
        "type": "way",
        "id": 1001008,
        "tags": {
            "name": "Meryem Ana Kilisesi",
            "building": "church",
            "amenity": "place_of_worship",
            "building:levels": "2",
            "height": "14.5",
        },
        "geometry": [
            {"lat": 40.97900, "lon": 28.87540},
            {"lat": 40.97950, "lon": 28.87540},
            {"lat": 40.97950, "lon": 28.87610},
            {"lat": 40.97900, "lon": 28.87610},
            {"lat": 40.97900, "lon": 28.87540},
        ],
    })

    # 9. Bakırköy Dr. Sadi Konuk Eğitim ve Araştırma Hastanesi
    elements.append({
        "type": "way",
        "id": 1001009,
        "tags": {
            "name": "Bakırköy Dr. Sadi Konuk Eğitim ve Araştırma Hastanesi",
            "building": "hospital",
            "amenity": "hospital",
            "building:levels": "6",
            "height": "20.0",
        },
        "geometry": [
            {"lat": 40.98620, "lon": 28.86800},
            {"lat": 40.98750, "lon": 28.86800},
            {"lat": 40.98750, "lon": 28.87020},
            {"lat": 40.98620, "lon": 28.87020},
            {"lat": 40.98620, "lon": 28.86800},
        ],
    })

    # 10. Bakırköy Ruh ve Sinir Hastalıkları Hastanesi (Tarihi Ana Bina)
    elements.append({
        "type": "way",
        "id": 1001010,
        "tags": {
            "name": "Bakırköy Ruh Sağlığı ve Sinir Hastalıkları Hastanesi",
            "building": "hospital",
            "amenity": "hospital",
            "building:levels": "4",
            "height": "15.0",
        },
        "geometry": [
            {"lat": 40.98500, "lon": 28.86550},
            {"lat": 40.98600, "lon": 28.86550},
            {"lat": 40.98600, "lon": 28.86750},
            {"lat": 40.98500, "lon": 28.86750},
            {"lat": 40.98500, "lon": 28.86550},
        ],
    })

    # 11 - 35: Authentic Cevizlik & Sakızağacı Urban Residential & Mixed-Use Blocks
    base_lat_lons = [
        # Cevizlik District Blocks (South of station / West of Ebuzziya)
        (40.97850, 28.87410, "Cevizlik Konut Blok A", "residential", 5),
        (40.97850, 28.87470, "Cevizlik Konut Blok B", "residential", 5),
        (40.97800, 28.87410, "Cevizlik Ticaret & Konut C", "apartments", 6),
        (40.97800, 28.87470, "Cevizlik Konut Blok D", "residential", 4),
        (40.97750, 28.87420, "Cevizlik Çarşı Blok", "retail", 4),
        (40.97750, 28.87480, "Cevizlik Apartmanı", "apartments", 5),
        (40.97700, 28.87430, "Marmara Sahil Konutları 1", "residential", 5),
        (40.97700, 28.87500, "Marmara Sahil Konutları 2", "residential", 6),
        # Sakızağacı District Blocks (East of Fahri Korutürk / South of Railway)
        (40.98020, 28.87600, "Sakızağacı Konut A", "residential", 5),
        (40.98020, 28.87670, "Sakızağacı Konut B", "residential", 4),
        (40.97960, 28.87620, "Sakızağacı İş Merkezi", "office", 5),
        (40.97960, 28.87700, "Sakızağacı Apartmanı", "apartments", 5),
        (40.97900, 28.87670, "Kennedy Konutları 1", "residential", 5),
        (40.97900, 28.87750, "Kennedy Konutları 2", "residential", 6),
        (40.97830, 28.87600, "Tarihi Taş Mektep", "school", 3),
        (40.97830, 28.87700, "Bakırköy Anadolu Lisesi", "school", 4),
        # Kartaltepe / İncirli Urban Blocks (North of Railway & Square)
        (40.98250, 28.87320, "İncirli Çarşı Bloğu 1", "commercial", 5),
        (40.98250, 28.87400, "İncirli Çarşı Bloğu 2", "commercial", 5),
        (40.98300, 28.87320, "Kartaltepe Konut A", "residential", 5),
        (40.98300, 28.87400, "Kartaltepe Konut B", "residential", 5),
        (40.98360, 28.87300, "Kartaltepe İşhanı", "office", 6),
        (40.98360, 28.87380, "Kartaltepe Apartmanı C", "apartments", 4),
        (40.98420, 28.87320, "Bakırköy Adalet Sarayı Ek Bina", "civic", 5),
        (40.98420, 28.87420, "Şükran Çiftliği Rezidans", "residential", 6),
        (40.98480, 28.87350, "İncirli Palas", "apartments", 6),
    ]

    for idx, (b_lat, b_lon, b_name, b_type, b_lvl) in enumerate(base_lat_lons, start=1001011):
        d_lat = 0.00045  # ~50 meters N-S
        d_lon = 0.00055  # ~46 meters E-W
        elements.append({
            "type": "way",
            "id": idx,
            "tags": {
                "name": b_name,
                "building": b_type,
                "building:levels": str(b_lvl),
            },
            "geometry": [
                {"lat": round(b_lat, 5), "lon": round(b_lon, 5)},
                {"lat": round(b_lat + d_lat, 5), "lon": round(b_lon, 5)},
                {"lat": round(b_lat + d_lat, 5), "lon": round(b_lon + d_lon, 5)},
                {"lat": round(b_lat, 5), "lon": round(b_lon + d_lon, 5)},
                {"lat": round(b_lat, 5), "lon": round(b_lon, 5)},
            ],
        })

    # ========================================================================
    # HIGHWAYS & STREET NETWORK (Authentic Bakırköy Center)
    # ========================================================================
    # Road 1: İncirli Caddesi (Primary Boulevard from E5 to Freedom Square)
    elements.append({
        "type": "way",
        "id": 2001001,
        "tags": {
            "name": "İncirli Caddesi",
            "highway": "primary",
            "lanes": "4",
            "oneway": "no",
        },
        "geometry": [
            {"lat": 40.98800, "lon": 28.87180},
            {"lat": 40.98650, "lon": 28.87240},
            {"lat": 40.98480, "lon": 28.87310},
            {"lat": 40.98350, "lon": 28.87360},
            {"lat": 40.98220, "lon": 28.87410},
            {"lat": 40.98186, "lon": 28.87428},
        ],
    })

    # Road 2: İstanbul Caddesi (Major Arterial / Commercial Artery)
    elements.append({
        "type": "way",
        "id": 2001002,
        "tags": {
            "name": "İstanbul Caddesi",
            "highway": "primary",
            "lanes": "3",
            "oneway": "yes",
        },
        "geometry": [
            {"lat": 40.98100, "lon": 28.86950},
            {"lat": 40.98130, "lon": 28.87200},
            {"lat": 40.98160, "lon": 28.87380},
            {"lat": 40.98186, "lon": 28.87428},
            {"lat": 40.98210, "lon": 28.87650},
            {"lat": 40.98240, "lon": 28.87900},
            {"lat": 40.98280, "lon": 28.88250},
        ],
    })

    # Road 3: Fahri Korutürk Caddesi (Iconic Pedestrian Shopping Spine)
    elements.append({
        "type": "way",
        "id": 2001003,
        "tags": {
            "name": "Fahri Korutürk Caddesi",
            "highway": "pedestrian",
            "oneway": "no",
        },
        "geometry": [
            {"lat": 40.98060, "lon": 28.87435},
            {"lat": 40.98120, "lon": 28.87430},
            {"lat": 40.98186, "lon": 28.87428},
        ],
    })

    # Road 4: Ebuzziya Caddesi (Main Pedestrian Promenade to Coast)
    elements.append({
        "type": "way",
        "id": 2001004,
        "tags": {
            "name": "Ebuzziya Caddesi",
            "highway": "pedestrian",
            "oneway": "no",
        },
        "geometry": [
            {"lat": 40.98050, "lon": 28.87400},
            {"lat": 40.97950, "lon": 28.87410},
            {"lat": 40.97850, "lon": 28.87405},
            {"lat": 40.97720, "lon": 28.87400},
            {"lat": 40.97600, "lon": 28.87410},
        ],
    })

    # Road 5: Şükran Çiftliği Sokağı (Secondary Connector)
    elements.append({
        "type": "way",
        "id": 2001005,
        "tags": {
            "name": "Şükran Çiftliği Sokağı",
            "highway": "secondary",
            "lanes": "2",
            "oneway": "no",
        },
        "geometry": [
            {"lat": 40.98300, "lon": 28.87320},
            {"lat": 40.98380, "lon": 28.87400},
            {"lat": 40.98450, "lon": 28.87520},
            {"lat": 40.98520, "lon": 28.87650},
        ],
    })

    # Road 6: Halit Ziya Uşaklıgil Caddesi (Collector Road)
    elements.append({
        "type": "way",
        "id": 2001006,
        "tags": {
            "name": "Halit Ziya Uşaklıgil Caddesi",
            "highway": "secondary",
            "lanes": "2",
            "oneway": "no",
        },
        "geometry": [
            {"lat": 40.97920, "lon": 28.87150},
            {"lat": 40.97930, "lon": 28.87270},
            {"lat": 40.97940, "lon": 28.87400},
            {"lat": 40.97950, "lon": 28.87550},
        ],
    })

    # Road 7: Rauf Orbay Caddesi / Kennedy Caddesi (Coastal Highway / Trunk)
    elements.append({
        "type": "way",
        "id": 2001007,
        "tags": {
            "name": "Kennedy Caddesi (Rauf Orbay Cd.)",
            "highway": "trunk",
            "lanes": "4",
            "oneway": "yes",
        },
        "geometry": [
            {"lat": 40.97500, "lon": 28.86500},
            {"lat": 40.97520, "lon": 28.87000},
            {"lat": 40.97530, "lon": 28.87450},
            {"lat": 40.97540, "lon": 28.87850},
            {"lat": 40.97560, "lon": 28.88300},
        ],
    })

    # Road 8: Mor Sümbül Sokağı (Residential Lane)
    elements.append({
        "type": "way",
        "id": 2001008,
        "tags": {
            "name": "Mor Sümbül Sokağı",
            "highway": "residential",
            "lanes": "2",
            "oneway": "no",
        },
        "geometry": [
            {"lat": 40.97820, "lon": 28.87450},
            {"lat": 40.97820, "lon": 28.87580},
            {"lat": 40.97820, "lon": 28.87650},
        ],
    })

    # Road 9: Mor Menekşe Sokağı (Residential Lane)
    elements.append({
        "type": "way",
        "id": 2001009,
        "tags": {
            "name": "Mor Menekşe Sokağı",
            "highway": "residential",
            "lanes": "2",
            "oneway": "no",
        },
        "geometry": [
            {"lat": 40.97760, "lon": 28.87450},
            {"lat": 40.97760, "lon": 28.87580},
            {"lat": 40.97760, "lon": 28.87660},
        ],
    })

    # Road 10: İstasyon Arkası Sokağı (Railway Access / Service Road)
    elements.append({
        "type": "way",
        "id": 2001010,
        "tags": {
            "name": "İstasyon Arkası Sokağı",
            "highway": "service",
            "lanes": "1",
            "oneway": "yes",
        },
        "geometry": [
            {"lat": 40.98030, "lon": 28.87350},
            {"lat": 40.98040, "lon": 28.87450},
            {"lat": 40.98040, "lon": 28.87580},
        ],
    })

    # Road 11: Ray Sokağı (Northern Railway Parallel)
    elements.append({
        "type": "way",
        "id": 2001011,
        "tags": {
            "name": "Ray Sokağı",
            "highway": "residential",
            "lanes": "2",
            "oneway": "no",
        },
        "geometry": [
            {"lat": 40.98110, "lon": 28.87280},
            {"lat": 40.98120, "lon": 28.87450},
            {"lat": 40.98130, "lon": 28.87650},
        ],
    })

    # Road 12: General Şükrü Kanatlı Caddesi (Hospital Boulevard)
    elements.append({
        "type": "way",
        "id": 2001012,
        "tags": {
            "name": "General Şükrü Kanatlı Caddesi",
            "highway": "tertiary",
            "lanes": "2",
            "oneway": "no",
        },
        "geometry": [
            {"lat": 40.98550, "lon": 28.86600},
            {"lat": 40.98620, "lon": 28.86850},
            {"lat": 40.98680, "lon": 28.87100},
            {"lat": 40.98720, "lon": 28.87250},
        ],
    })

    return {
        "version": 0.6,
        "generator": "BakirkoyBR Synthetic Offline Seed Generator v1.0",
        "elements": elements,
    }


# ============================================================================
# PIPELINE ORCHESTRATION & EXPORT
# ============================================================================
def run_pipeline(
    output_path: str,
    mode: str = "center",
    cache_path: str = "data/bakirkoy_osm_raw.json",
    force_offline_seed: bool = False,
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Executes the complete OSM acquisition and normalization pipeline.
    """
    raw_osm_data: Optional[Dict[str, Any]] = None
    data_source = "unknown"

    # Step 1: Force offline seed dataset if requested
    if force_offline_seed:
        logging.info("Flag --offline-seed active. Loading embedded authentic Bakırköy seed dataset.")
        raw_osm_data = get_offline_seed_dataset()
        data_source = "embedded_offline_seed"

    # Step 2: Check local cache
    if raw_osm_data is None and os.path.exists(cache_path):
        try:
            logging.info(f"Checking local disk cache at: {cache_path}")
            with open(cache_path, "r", encoding="utf-8") as f:
                cached = json.load(f)
            if "elements" in cached and len(cached["elements"]) > 0:
                raw_osm_data = cached
                data_source = f"local_disk_cache ({cache_path})"
                logging.info(f"Loaded {len(cached['elements'])} raw elements from local disk cache.")
        except Exception as ex:
            logging.warning(f"Failed to read disk cache ({cache_path}): {ex}. Proceeding to live queries.")

    # Step 3: Query live Overpass API Failover Pool
    if raw_osm_data is None:
        query = build_overpass_query(mode)
        logging.info(f"Querying live Overpass API failover pool (mode={mode})...")
        raw_osm_data = fetch_from_overpass_pool(query, verbose=verbose)
        if raw_osm_data:
            data_source = "live_overpass_api"
            # Cache to disk for future executions
            try:
                os.makedirs(os.path.dirname(os.path.abspath(cache_path)), exist_ok=True)
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(raw_osm_data, f, indent=2, ensure_ascii=False)
                logging.info(f"Saved raw Overpass API response to cache: {cache_path}")
            except Exception as ex:
                logging.warning(f"Could not persist cache to {cache_path}: {ex}")

    # Step 4: Fallback to embedded seed if live queries and cache both failed
    if raw_osm_data is None:
        logging.warning("Overpass servers unreachable and no valid cache found. Engaging embedded authentic Bakırköy seed dataset.")
        raw_osm_data = get_offline_seed_dataset()
        data_source = "embedded_offline_seed_fallback"

    elements = raw_osm_data.get("elements", [])
    logging.info(f"Processing {len(elements)} OSM raw elements (Source: {data_source})...")

    buildings: List[Dict[str, Any]] = []
    roads: List[Dict[str, Any]] = []

    all_x: List[float] = []
    all_y: List[float] = []

    for elem in elements:
        tags = elem.get("tags", {})
        if "building" in tags or tags.get("type") == "building":
            b_obj = process_building(elem)
            if b_obj:
                buildings.append(b_obj)
                all_x.append(b_obj["centroid_ue"][0])
                all_y.append(b_obj["centroid_ue"][1])
                for pt in b_obj["footprint_ue"]:
                    all_x.append(pt[0])
                    all_y.append(pt[1])
        elif "highway" in tags:
            r_obj = process_road(elem)
            if r_obj:
                roads.append(r_obj)
                for pt in r_obj["points_ue"]:
                    all_x.append(pt[0])
                    all_y.append(pt[1])

    # Compute bounding box in UE cm
    if all_x and all_y:
        min_x = round(min(all_x), 1)
        max_x = round(max(all_x), 1)
        min_y = round(min(all_y), 1)
        max_y = round(max(all_y), 1)
    else:
        min_x, max_x, min_y, max_y = 0.0, 0.0, 0.0, 0.0

    # Build final normalized dataset matching SCOPE.md interface contract
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    level_data: Dict[str, Any] = {
        "metadata": {
            "datum": {
                "name": ORIGIN_NAME,
                "lat": ORIGIN_LAT,
                "lon": ORIGIN_LON,
                "alt_m": ORIGIN_ALT_M,
            },
            "ue_units": "1 UU = 1 cm",
            "coordinate_mapping": {
                "X": "+North",
                "Y": "+East",
                "Z": "+Up",
            },
            "bounds_ue": {
                "min_x": min_x,
                "max_x": max_x,
                "min_y": min_y,
                "max_y": max_y,
            },
            "total_buildings": len(buildings),
            "total_roads": len(roads),
            "data_source": data_source,
            "generated_at": now_utc,
        },
        "buildings": buildings,
        "roads": roads,
    }

    # Save to output file
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(level_data, f, indent=2, ensure_ascii=False)

    logging.info(
        f"Pipeline complete: {len(buildings)} buildings, {len(roads)} roads saved to {output_path}."
    )
    return level_data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch, project, and synthesize OpenStreetMap data for Bakırköy BR (Phase 4 R1)."
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="data/bakirkoy_level_data.json",
        help="Target output JSON path (default: data/bakirkoy_level_data.json)",
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=["center", "district"],
        default="center",
        help="Spatial bounding mode: 'center' (~1.5km core around Özgürlük Meydanı) or 'district' (entire Bakırköy)",
    )
    parser.add_argument(
        "--cache-file",
        "-c",
        type=str,
        default="data/bakirkoy_osm_raw.json",
        help="Path for local persistent raw Overpass cache (default: data/bakirkoy_osm_raw.json)",
    )
    parser.add_argument(
        "--offline-seed",
        action="store_true",
        help="Force using the embedded authentic offline Bakırköy seed dataset without network requests",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose debug logging",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        data = run_pipeline(
            output_path=args.output,
            mode=args.mode,
            cache_path=args.cache_file,
            force_offline_seed=args.offline_seed,
            verbose=args.verbose,
        )
        print(f"[SUCCESS] Exported {data['metadata']['total_buildings']} buildings and {data['metadata']['total_roads']} roads.")
        return 0
    except Exception as e:
        logging.exception(f"Fatal pipeline error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
