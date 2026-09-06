# No Interior Spaces Rule

> [!CAUTION]
> This is an ABSOLUTE constraint. No exceptions.

## Rule
Buildings in the Bakırköy map are **exterior-only**. This means:

1. **No interior geometry**: Buildings are solid collision volumes. Players cannot enter them.
2. **No interior NavMesh**: AI agents pathfind only on streets, sidewalks, rooftops, and terraces.
3. **No doors or windows**: Buildings have no openable doors or windows.
4. **Rooftops ARE accessible**: Players can reach rooftops via external staircases, ramps, or player-built structures.
5. **Terraces ARE accessible**: Balconies and terraces that are architecturally part of the exterior are playable.

## Why This Exists
- Drastically reduces NavMesh complexity (no indoor pathfinding)
- Eliminates interior lighting/rendering cost
- Simplifies level design (no room layouts)
- Focuses gameplay on outdoor combat and building mechanics

## Implementation Impact
- NavMesh: Carve building footprints entirely. Only street-level and roof-level NavMesh.
- Collision: Buildings use simple box/convex collision. No interior mesh needed.
- AI Pathfinding: A* operates on street graph + roof nodes connected by NavMesh Links.
- Cover System: Cover nodes placed on exterior walls, vehicles, and urban furniture only.
