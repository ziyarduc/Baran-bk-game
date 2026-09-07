## 2026-09-06T18:52:00Z
Task:
Implement `fetch_osm_data.py` for requirement R1:
1. Read C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md, SCOPE.md, and survey_explorer_1/handoff.md.
2. Author a production-grade, robust Python pipeline `fetch_osm_data.py`:
   - Queries OpenStreetMap via Overpass API for central Bakırköy (bounds roughly 40.9750 to 40.9880 N, 28.8650 to 28.8830 E).
   - Multi-endpoint failover pool (overpass-api.de, lz4.overpass-api.de, z.overpass-api.de, kumi.systems, maps.mail.ru) with timeouts and exponential retry backoff.
   - Pure standard math local tangent plane projection from WGS84 (lat, lon) to UE Left-Handed Z-Up cm coordinates (+X=North, +Y=East, +Z=Up, 1 UU = 1 cm) with origin datum at Bakırköy Özgürlük Meydanı (40.98186° N, 28.87428° E, alt 25m). No external GIS dependencies (no osmnx/shapely required).
   - 4-tier height synthesis algorithm for buildings (explicit tags -> levels * 3.2m -> semantic heuristics -> deterministic hash).
   - Highway classification with width mapping in cm (motorway/trunk: 1400, primary: 1200, secondary: 900, tertiary: 750, residential: 600, service: 400, pedestrian: 800).
   - Local persistent disk caching (`data/bakirkoy_osm_raw.json`) and an embedded offline synthetic seed dataset of central Bakırköy (Özgürlük Meydanı, İstanbul Caddesi, Carousel, Galleria, Capacity, Cevizlik, Sakızağacı, etc.) so execution succeeds reliably even if public Overpass servers are offline or rate-limited.
   - CLI flags: `--output`, `--mode`, `--cache-file`, `--offline-seed`, `--verbose`.
   - Generates `data/bakirkoy_level_data.json` matching the exact schema in SCOPE.md.
3. Update checkpoint via PowerShell:
   `powershell -ExecutionPolicy Bypass -File scripts/checkpoint-manager.ps1 -Action Save -Milestone "M-OSM-1" -Task "fetch_osm_data" -Details "fetch_osm_data.py authored and verified"`
4. Run verification:
   - `python -m py_compile fetch_osm_data.py`
   - `python fetch_osm_data.py --output data/bakirkoy_level_data.json`
   - Run a Python one-liner to validate the generated JSON schema (buildings > 0, roads > 0, valid coords).
5. Record your results and write your compact handoff report to `C:\Users\silver\Desktop\bakirkoy-br\.agents\worker_osm_fetch\handoff.md` following the compact 4-part schema.
