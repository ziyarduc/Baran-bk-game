## 2026-09-06T11:15:14Z
You are the AIAgents Worker for Bakırköy BR Playable Demo MVP.
Model: gemini-3.8-flash with High Thinking enabled.
Working Directory: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_ai_agents
Project Root: C:\Users\silver\Desktop\bakirkoy-br

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

JIT Skill Loading:
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\skills\worker-ai-agents\SKILL.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\sequential-thinking.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\error-prevention.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\constraint-retention.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\token-optimization.md

Your exclusive write boundaries:
- BakirkoyBR/Source/BakirkoyBR/AI/** (and root Source/BakirkoyBR/AI/** if mirrors exist)
- C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_ai_agents/**

Mandatory 5-Stage Sequential Thinking:
Execute Stages 1-5 before implementing.

Specific Implementation Scope for Demo 1 MVP:
1. Limit total AI count to exactly 10 bots (enforce constant MAX_BOT_COUNT = 10).
2. BRAIController.h & BRAIController.cpp:
   - ABRAIController : public AAIController.
   - Uses UAIPerceptionComponent (Sight & Hearing config) for spotting players and opposing bots.
   - State machine / Decision logic:
     * LootSeeking: Detect nearest weapon/loot pickup, navigate along NavMesh to pickup location, equip weapon.
     * CombatEngagement: Aim and fire equipped Hit-Scan weapon at target within range, using natural cover (vehicles, walls, corners).
     * Wandering / ZoneMove: Navigate along exterior-only streets, alleys, and external stairs/fire escapes to rooftops.
   - Strict Constraint Check: NEVER enter buildings. NavMesh goals must be exterior street or rooftop positions only.
3. BRAIBotCharacter.h & BRAIBotCharacter.cpp (or AI integration with ABRCharacter):
   - Bot character inheriting from ABRCharacter or modular AI bot actor.
   - Health component integration (UBRHealthComponent), death/elimination event dispatch.
   - Server-authoritative weapon firing trigger.
   - Wrap all UObject* members in TObjectPtr<>. #include "BRAIController.generated.h" strictly last.
4. Verification:
   - Run pwsh -File scripts/verify-rules.ps1 to ensure all 117+ rules pass without AST or reflection violations.
   - Write compact handoff report with surgical diffs/summaries to:
     C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_ai_agents\handoff.md
