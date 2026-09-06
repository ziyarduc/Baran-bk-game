# Worker: AI Agent Systems (Local Copy)

Files You Own:
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

Core Constraints:
- 10 Bots Test Scenario (MAX_BOT_COUNT = 10)
- Never Enter Buildings: Exterior street & rooftop positions only.
- Solo BR only: No squads, DBNO.
- Server-authoritative: AI runs entirely on server.
- Natural Cover: Vehicles, walls, alleys.
- Hybrid Hit Detection: AR Hit-Scan + Rocket Launcher Projectile.
- Mandatory BR prefix for all classes.
