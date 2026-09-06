# NavMesh Guide

## Layer Structure
1. **Ground Layer**: Streets, sidewalks, parks, coastal promenade
2. **Roof Layer**: Building rooftops, terraces (connected via NavMesh Links)
3. **Build Layer**: Dynamic — player-built ramps/floors generate NavMesh at runtime

## Configuration
- Agent Radius: 0.6m (for crowd avoidance)
- Agent Height: 1.8m
- Max Slope: 45° (matches ramp angle)
- Cell Size: 10cm (fine detail for narrow streets)
- Building footprints: Carved from NavMesh entirely (no interior navigation)

## NavMesh Links
- Rooftop access points connected to street level via NavMesh Links
- Each link has a cost modifier (climbing = 2× normal walking cost)
- Links tagged with height for Sniper AI's High Ground Priority skill

## Cover Nodes
- Pre-placed on vehicle wrecks, walls, urban furniture
- Properties: position, cover_direction, height (LOW/MEDIUM/HIGH), destructible flag
- AI queries cover nodes during HIDE and CHASE states
