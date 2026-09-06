# Storm Circle Design

## Phase Table
| Phase | Wait | Shrink | Area% | DMG/s |
|-------|------|--------|-------|-------|
| 0 | 60s | — | 100% | 0 |
| 1 | 90s | 120s | 70% | 1 |
| 2 | 75s | 90s | 45% | 2 |
| 3 | 60s | 75s | 25% | 5 |
| 4 | 45s | 60s | 12% | 8 |
| 5 | 30s | 45s | 5% | 10 |
| 6 | 20s | 30s | 1% | 15 |

## Smart Circle Engine

### Street Avoidance Algorithm
- Use a Street Graph (pre-baked) to check if circle wall intersects narrow streets
- If street width < 4m at intersection point, shift wall ±3m to fully include or exclude the street
- Never cut a narrow street in half

### Dynamic Center Weighting
- Phase 3+: Center biased 60% toward high-density POI areas
- Prevents end-game in empty parks

### Corridor Widening
- When circle wall passes through a street < 4m wide:
  - Option A: Shift wall to include entire street in safe zone
  - Option B: Shift wall to place entire street in storm
  - Choose option that keeps more POIs in safe zone

## Implementation Notes
- `FVector2D CircleCenter` — replicated
- `float CircleRadius` — replicated
- `int32 CurrentPhase` — replicated
- Use `FTimerHandle` for phase transitions
- Damage applied per-tick to players outside circle via overlap check
