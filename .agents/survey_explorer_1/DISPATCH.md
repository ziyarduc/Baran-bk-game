# Dispatch for Survey Explorer 1: OSM Overpass Data Pipeline

**Working Directory**: `C:\Users\silver\Desktop\bakirkoy-br\.agents\survey_explorer_1\`
**Task**: Survey OpenStreetMap / Overpass API querying, GIS data structures, and Python requirements for `fetch_osm_data.py`.

## 2026-09-06T18:47:03Z
You are Survey Explorer 1 (teamwork_preview_explorer).
Your assigned working directory is: C:\Users\silver\Desktop\bakirkoy-br\.agents\survey_explorer_1\
The authoritative user request is at: C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md
The project root is: C:\Users\silver\Desktop\bakirkoy-br

Your task:
Survey the requirements and technical architecture for requirement R1: `fetch_osm_data.py` (OpenStreetMap / Overpass API data acquisition pipeline).
1. Read C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md.
2. Investigate the geographic boundaries and Overpass API query syntax for Bakirkoy, Istanbul (e.g. area query for district Bakirkoy or bounding box, fetching nodes, ways, and relations tagged with 'building' and 'highway').
3. Investigate data extraction requirements: building heights (or estimating heights from building:levels or default heights), building footprint polygon coordinates, road network types (primary, secondary, residential, service) with centerlines/coordinates.
4. Investigate coordinate projection from WGS84 (lat, lon) to local Cartesian coordinates (meters, and converting to Unreal Engine units where 1 UU = 1 cm) with a defined reference datum/origin in Bakirkoy (e.g., Freedom Square / Özgürlük Meydanı or district center).
5. Address robustness: caching mechanism (saving raw/parsed JSON to disk to avoid hitting rate limits or when offline), error handling for Overpass endpoints (fallback endpoints like overpass-api.de, kumi.systems, etc.), timeouts, and formatting output for `build_osm_level.py`.
6. Adhere to token optimization rules and produce a comprehensive technical specification in your working directory: `C:\Users\silver\Desktop\bakirkoy-br\.agents\survey_explorer_1\handoff.md`.
7. Once done, send a message to orchestrator with your report location.
