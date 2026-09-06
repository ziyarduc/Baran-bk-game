# Agent Roles & AI Skills

## Role Distribution
- Assault: 45% of bots
- Sniper: 25% of bots
- Support: 30% of bots

## Assault Agent
**Preferred Weapons**: SMG (primary), AR (secondary)

### Skill: Flanking
1. Calculate Agent→Target vector
2. Find perpendicular directions (Left-Flank, Right-Flank)
3. Search NavMesh for cover node 20-30m away in flank direction
4. Selection: prefer cover behind target's facing direction (×2 weight)
5. Move cover-to-cover to flank position
6. Engage from side angle
- Cancel if HP drops below 30%

### Skill: Rush
- Trigger: Target not firing for 3+ seconds AND distance < 25m
- Behavior: Sprint + hip-fire SMG, switch to shotgun at 8m

## Sniper Agent
**Preferred Weapons**: Sniper (primary), Pistol (secondary)

### Skill: High Ground Priority
1. Query NavMesh nodes sorted by Z-height
2. Candidates: nodes ≥3m above current position
3. Score by: FOV coverage, escape routes (min 2), storm circle compatibility
4. Navigate to best high point
5. Enter Scope Hold: crouch + ADS + 180° slow pan

### Skill: Reposition
- Trigger: After 2 shots OR taking fire
- Move 10-20m to alternative cover
- Re-enter Scope Hold from new position

## Support Agent
**Preferred Weapons**: AR (primary), SMG (secondary)

### Skill: Suppression Fire
1. Identify target's cover position
2. Fire 3-round bursts at cover edges (left, right, top)
3. Pattern: burst → 0.4s pause → burst → 0.4s pause
4. Duration: max 6s, then 3s assess pause
5. Success = target stays in cover for full 6s → flanking window for allies

### Skill: Revive Priority (Squad mode only — NOT for Solo)
- Deprioritized since Solo mode is the first prototype

## Difficulty Scaling
| Level | Accuracy | Reaction | Movement | Trigger |
|-------|----------|----------|----------|---------|
| Easy | 25% | 0.8s | Linear, no cover | Top 80 |
| Medium | 45% | 0.5s | Cover-to-cover | Top 50 |
| Hard | 65% | 0.3s | Flank, strafe, peek | Top 25 |
| Elite | 80% | 0.15s | Full skill set, builds | Top 10 |
