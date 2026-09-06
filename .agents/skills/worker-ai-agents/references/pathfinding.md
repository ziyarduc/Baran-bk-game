# Pathfinding Guide

## A* Cost Modifiers

### 1. Cover Proximity Heuristic
- Paths near cover nodes get cost reduction
- Cover within 5m of path segment: cost ×0.8
- Active during CHASE state

### 2. Threat-Aware Pathfinding
- Known enemy positions add cost to nearby paths
- Path segment within enemy LoS: cost ×3.0
- Agent routes around instead of through danger zones

### 3. Storm-Aware Pathfinding
- Paths toward safe zone get cost reduction
- Path toward storm: cost ×2.0
- Path toward safe zone: cost ×0.5

## RVO2 Crowd Avoidance

### Agent Capsule
- Personal space radius: 0.6m
- Capsules cannot overlap

### Velocity Obstacle
- Each agent reads nearby agents' velocities
- RVO2 computes new preferred velocity to avoid collision
- Built into UE5's UCharacterMovementComponent avoidance

### Narrow Street Protocol
- Streets < 3m wide: max 2 agents simultaneously
- 3rd agent waits 0.5–1.5s (random jitter) at street entrance
- Priority: lower HP agent goes first

### Disperse Command
- Triggered when Rocket Launcher detected within 10m
- All agents within 5m radius sprint in different directions
- Uses radial distribution (360° / agent_count) for spread angles
