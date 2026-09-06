# Skydiving Mechanics

## Phase 1: Free Fall
- Max vertical speed: 60 m/s
- Max horizontal speed: 25 m/s
- Wind reading: +15% horizontal speed with wind, -10% against
- Wind direction displayed on HUD

## Phase 2: Glide (Parachute)
- Auto-trigger: 100m above ground OR manual trigger
- Vertical speed: 8 m/s
- Horizontal speed: 15 m/s
- Quick Drop skill: close parachute for 2s free fall burst (not below 30m)

## Phase 3: Landing
- Landing animation: 0.5s (no weapon, no fire)
- Post-landing inertia: 0.3s movement delay
- Spawn protection: 3s immunity (only from other skydivers)

## Implementation
- UBRSkydiveComponent attached to character during skydive phase
- Component handles movement override, parachute state, wind calculation
- Removed after landing (or pooled)
