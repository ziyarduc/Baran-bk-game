# Server Architecture

## Server-Authoritative Model
- Dedicated server (UE5 headless build)
- Server tick rate: 60 Hz
- Client sends input only — server validates everything
- All HP/Shield changes, eliminations, storm movement are server-authoritative

## Client-Server Communication
- Transport: UDP (reliable + unreliable channels)
- Client → Server: Input packets (movement, aim direction, fire command)
- Server → Client: State replication (positions, health, storm data)
- Client prediction: predict local movement, reconcile on server correction
- Entity interpolation: smooth other players' positions between server updates

## Match Flow
1. LOBBY: Wait for players (100 max, timeout 120s)
2. PRE_GAME: Warm-up island (60s)
3. SKYDIVE: Battle bus + drop (30s bus traverse)
4. ACTIVE: Gameplay with storm phases
5. POST_GAME: Results screen (15s)

## Anti-Cheat Basics
- Server validates all damage (never trust client hit results)
- Movement speed validation (flag teleporting)
- Fire rate validation (flag impossible fire rates)
- Server rewind capped at 200ms (prevents lag exploitation)
