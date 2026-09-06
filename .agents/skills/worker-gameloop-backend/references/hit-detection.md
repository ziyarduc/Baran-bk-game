# Hit Detection System

## Hybrid Approach
| Weapon | Method | Reason |
|--------|--------|--------|
| SMG | Hit-Scan | High fire rate, projectile sim too expensive |
| AR | Hit-Scan | Mid fire rate, sufficient accuracy |
| Sniper | Hit-Scan + Drop | Hit-scan with server-side gravity offset >100m |
| Shotgun | Hit-Scan (×9) | 9 rays in cone, each independent |
| Rocket | Projectile | Slow projectile, player must be able to dodge |

## Server Rewind
1. Server stores position history: ring buffer, 15ms snapshots, 300ms window
2. Client sends fire command + client timestamp
3. Server calculates ping, rewinds world to client's perceived time
4. Performs raycast against rewound hitbox positions
5. Hit → apply damage. Miss → return miss.
6. Max rewind: 200ms (high-ping players are disadvantaged)

## Hitbox Setup
- Head bone: "head" → ×2.0 multiplier (×1.5 for shotgun)
- Body capsule: torso, arms, legs → ×1.0 multiplier
- No limb-specific damage in v1 (simplification)
