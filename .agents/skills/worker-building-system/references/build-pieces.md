# Build Pieces

## Piece Types
| Piece | Cost | Size | Use |
|-------|------|------|-----|
| Wall | 10 | 3m × 3m | Cover, LoS blocking |
| Ramp | 10 | 3m × 3m × 45° | Height advantage |
| Floor | 10 | 3m × 3m | Bridge, platform |
| Half-Wall | 5 | 3m × 1.5m | Peek cover |

## Placement Rules
- Pieces snap to a 3m grid
- Pieces must be supported (connected to ground or another piece)
- Floating pieces not allowed (if support destroyed, piece falls and takes damage)
- Max build height: 10 pieces (30m) above ground
- Pieces cannot overlap with existing static geometry (buildings, terrain)
- Preview ghost mesh shows placement validity (green = valid, red = invalid)

## Destruction
- All pieces are destructible actors
- Damage reduces CurrentHP
- At 0 HP: piece is destroyed, plays destruction VFX
- Shotgun: ×250% damage bonus vs build pieces
- Rocket: destroys all pieces in splash radius (including Steel)
- Pieces above a destroyed piece lose support → cascading destruction
