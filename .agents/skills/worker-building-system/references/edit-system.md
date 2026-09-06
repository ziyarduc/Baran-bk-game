# Build Edit System

## Edit Rules
- Only the piece owner can edit
- Enemy pieces cannot be edited (only destroyed)
- Edit animation: 0.4s
- Player must be within 5m of the piece to edit

## Edit Types
| Edit | Applicable To | Result |
|------|--------------|--------|
| Door | Wall | Creates a door-sized opening in the wall |
| Window | Wall | Creates a window-sized opening (peek hole) |
| Half-Cut | Wall, Floor | Removes the top/bottom half |
| Arch | Wall | Creates an arch opening |

## Implementation Notes
- Edit types stored as enum on ABRBuildPiece
- Each edit type changes the collision mesh and visual mesh
- Use mesh swapping (pre-made meshes for each edit variant)
- Edited pieces retain their current HP
- Edits are replicated to all clients

## Quick Edit Technique
- Select piece → choose edit type → confirm
- Total time: 0.4s (animation only, no cast bar)
- Can be chained with weapon swap for "edit-peek-shoot" combos
