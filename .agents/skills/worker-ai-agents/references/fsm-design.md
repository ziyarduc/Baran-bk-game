# FSM State Machine Design

## States and Transitions

### IDLE
- Entry: Game start (after landing) or all threats cleared for 15s
- Behavior: Scan for loot, move to nearest chest
- Exit → PATROL: No loot found for 20s
- Exit → CHASE: Enemy detected within 60m

### PATROL
- Entry: From IDLE or after HEAL complete
- Behavior: Follow NavMesh patrol route, prefer cover-adjacent paths
- Exit → CHASE: Enemy detected within 60m
- Exit → HIDE: HP < 30% and enemy detected
- Exit → HEAL: HP < 50% and no enemy detected

### CHASE
- Entry: Enemy detected, distance 15m–60m
- Behavior: Close distance with cover-to-cover movement every 3s
- Exit → ATTACK: Target within 30m and LoS clear
- Exit → PATROL: Target beyond 90m or LoS lost for 15s
- Exit → HIDE: HP < 25% while under fire

### ATTACK
- Entry: Target in LoS and within 30m
- Behavior: ADS, fire, strafe. Weapon-type-dependent behavior.
- Exit → CHASE: Target moves beyond 30m
- Exit → HIDE: Magazine empty or HP < 20%
- Exit → IDLE: Target eliminated

### HIDE
- Entry: HP critical or mag empty or outnumbered
- Behavior: Sprint to nearest CoverNode, crouch, peek at enemy
- Exit → HEAL: At cover for 2s and HP < 50%
- Exit → ATTACK: Enemy within 15m (forced defense)
- Exit → PATROL: No enemy detected for 20s

### HEAL
- Entry: HP < 50% and no combat for 5s
- Behavior: Use best available heal item. Priority: Medkit → Bandage → Shield
- Exit → ATTACK: Damaged during heal (interrupted)
- Exit → PATROL: Heal complete and HP > 70%
- Exit → HIDE: Heal complete but threats still detected

## Implementation Notes
- Each state is a UObject subclass of UBRBotStateBase
- StateMachine owns all state instances, calls Enter/Tick/Exit
- State transitions are validated by the StateMachine (prevents invalid jumps)
- Tick rate: 5 Hz (every 0.2s) — NOT every frame
