## 2026-09-06T11:15:14Z

<USER_REQUEST>
You are the GameLoop Worker for Bakırköy BR Playable Demo MVP.
Model: gemini-3.8-flash with High Thinking enabled.
Working Directory: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_gameloop
Project Root: C:\Users\silver\Desktop\bakirkoy-br

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

JIT Skill Loading:
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\skills\worker-gameloop-backend\SKILL.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\sequential-thinking.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\error-prevention.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\constraint-retention.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\rules\token-optimization.md

Your exclusive write boundaries:
- BakirkoyBR/Source/BakirkoyBR/GameModes/**
- BakirkoyBR/Source/BakirkoyBR/Storm/**
- C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_gameloop/**

Mandatory 5-Stage Sequential Thinking:
Execute Stages 1-5 before implementing.

Specific Implementation Scope for Demo 1 MVP:
1. Mode 1 — Free-For-All Deathmatch (BRGameMode_FFA.h, BRGameMode_FFA.cpp):
   - ABRGameMode_FFA : public AGameModeBase.
   - Score limit (e.g. 25 eliminations) and Match Time limit (e.g. 600 seconds).
   - Respawn system for player and 10 bots upon elimination at exterior player starts.
   - Leaderboard tracking and match victory celebration.
2. Mode 2 — Classic Battle Royale (BRGameMode_BattleRoyale.h, BRGameMode_BattleRoyale.cpp):
   - ABRGameMode_BattleRoyale : public AGameModeBase.
   - Solo BR only (no squads, no duos, no DBNO).
   - 10 bots + 1 player spawned at match start. Permanent elimination (no respawn in BR mode).
   - Storm circle system integration (BRStormCircle.h, BRStormCircle.cpp):
     * Shrinking circle radius, center point interpolation, damage over time to characters outside safe zone.
   - Win condition: Last Man Standing (when alive count reaches 1, declare winner).
3. Code Standards & Reflection Safety:
   - Wrap all UObject* members in TObjectPtr<>.
   - All headers have #include "ClassName.generated.h" strictly last.
   - Replicated state uses DOREPLIFETIME. No non-Unreal STL containers.
4. Verification:
   - Run pwsh -File scripts/verify-rules.ps1 to ensure all 117+ rules pass without AST or reflection violations.
   - Write compact handoff report with surgical diffs/summaries to:
     C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_gameloop\handoff.md
</USER_REQUEST>
