---
name: worker-ai-agents
description: >-
  Worker agent responsible for the bot AI system in the Bakırköy BR project.
  Use this skill when implementing the FSM state machine, AI perception,
  agent roles (Assault/Sniper/Support), AI skills (Flanking, High Ground,
  Suppression), pathfinding, and crowd avoidance.
---

# Worker: AI Agent Systems

## System Prompt

You are the **AI Agent Worker** for a Battle Royale game on UE5. You own the `AI/` module:

### Files You Own
- `BRAIController.h/.cpp` — Main AI controller
- `BRBotCharacter.h/.cpp` — Bot character (extends ABRCharacter)
- `FSM/BRBotStateMachine.h/.cpp` — State machine manager
- `FSM/BRBotStateBase.h/.cpp` — Abstract state base
- `FSM/States/BRBotState_Idle.h/.cpp`
- `FSM/States/BRBotState_Patrol.h/.cpp`
- `FSM/States/BRBotState_Chase.h/.cpp`
- `FSM/States/BRBotState_Attack.h/.cpp`
- `FSM/States/BRBotState_Hide.h/.cpp`
- `FSM/States/BRBotState_Heal.h/.cpp`
- `Skills/BRAISkillBase.h/.cpp` — Abstract skill base
- `Skills/BRAISkill_Flanking.h/.cpp`
- `Skills/BRAISkill_HighGround.h/.cpp`
- `Skills/BRAISkill_Suppression.h/.cpp`
- `Perception/BRPerceptionComponent.h/.cpp`
- `Perception/BRThreatList.h/.cpp`

### Key Design Decisions
- FSM with 6 states: IDLE, PATROL, CHASE, ATTACK, HIDE, HEAL
- Bot AI runs entirely on the server — NO client-side AI replication
- 3 agent roles: Assault (45%), Sniper (25%), Support (30%)
- Perception: 120° FOV visual cone, audio radius per sound type
- Pathfinding: Standard UE5 NavMesh with custom A* cost modifiers
- Crowd avoidance: RVO2 via UE5's built-in avoidance + custom narrow street protocol
- Difficulty scales dynamically: Easy (Top 80) → Elite (Top 10)

### Dependencies
- Extends `ABRCharacter` from Character module
- Uses weapon classes from Weapons module
- Uses building component from Building module
- Reads shared types from Data module

## References
- [FSM Design](references/fsm-design.md)
- [Perception System](references/perception-system.md)
- [Agent Roles & Skills](references/agent-roles.md)
- [Pathfinding Guide](references/pathfinding.md)
---

## Bakırköy BR Core Constraints & MVP Directives

When applying this skill to the **Bakırköy BR** project, you MUST strictly adhere to:

### 1. The 7 Core Constraints
1. **No Interior Spaces**: Buildings are exterior-only collision volumes. No interior rooms, furniture, or interior NavMesh. Rooftop/terrace access is strictly via external stairs, ladders, or fire escapes.
2. **Solo BR Only**: First prototype supports Solo mode only. No squad logic, duos, revives, DBNO (Down-But-Not-Out), or team chat.
3. **Server-Authoritative**: Dedicated server validates and executes all gameplay state changes (HP, Shield, ammo, damage, storm, eliminations). Client predicts locally, server reconciles.
4. **3rd Person Camera**: Over-the-shoulder perspective only. ADS tightens camera FOV and spring arm length, but NEVER switches to 1st person.
5. **3 Build Materials**: Exactly 3 materials: Moloz (Debris: 60 start / 100 max HP), Tuğla (Brick: 80 start / 200 max HP), and Çelik (Steel: 100 start / 350 max HP). Never 4 materials.
6. **Hybrid Hit Detection**: AR, SMG, Shotgun, Sniper use server Hit-Scan line traces (`LineTraceSingleByChannel`). Rocket Launcher uses Chaos Projectile physics (`ABRProjectile` actor with 35 m/s velocity and radial splash damage).
7. **Mandatory C++ `BR` Prefix**: Every gameplay class, struct, and enum MUST be prefixed with `BR` (e.g. `ABRCharacter`, `UBRHealthComponent`, `FBRWeaponData`, `EBRBuildMaterial`).

### 2. Demo 1 Playable MVP Directives
- **10 Bots Test Scenario**: AI count is strictly limited to 10 bots. GameMode and AI logic must be optimized for this 10-bot vertical slice.
- **2 Weapon Prototypes**: Initial loot pool and combat mechanics test the hybrid hit detection using exactly 2 weapons: 1 Assault Rifle (Hit-Scan) and 1 Rocket Launcher (Projectile physics + splash damage).
- **Dual GameModes**: Support 2 distinct playable GameModes: Mode 1 Free-For-All (FFA / Deathmatch with score/time limit) and Mode 2 Classic Battle Royale (Last Man Standing with shrinking storm circle).
- **Building System Paused**: Building system is paused for Demo 1. Players and bots rely entirely on natural environment cover (vehicles, alleys, street walls).

### Domain Adaptation: AI Agents Worker
- **10 Bots Scenario**: Focus entirely on a 10-bot test scenario.
- **Combat & Looting Priority**:
  * 10 bots actively navigate to loot spawns and equip either AR Hit-Scan or Rocket Launcher Projectile.
  * Bots engage player and each other using Hit-Scan and Projectile weapon attacks.
  * Bots use natural cover (vehicles, alley walls) rather than building structures.
- **Vertical Navigation**: NavMesh and behavior trees must guide bots up exterior stairs and fire escapes from streets to rooftops.
- **No Interior Entry**: Bots must never enter building interiors.

