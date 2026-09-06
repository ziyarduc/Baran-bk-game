## 2026-09-06T01:30:20Z

You are Worker M2 (Error-Prevention & Rules Worker) for Bakırköy BR project.
Your Working Directory is: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_m2
Project Root: C:\Users\silver\Desktop\bakirkoy-br

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Inputs:
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\AGENTS.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\PROJECT.md
- Read Explorer 3 Handoff: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_explorer_survey_3\handoff.md

Your exclusive write boundaries:
- .agents/rules/**
- scripts/verify-rules.ps1
- .agents/AGENTS.md
- C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_m2/**

Tasks:
1. Implement the 4 rule files in .agents/rules/:
   - .agents/rules/error-prevention.md: Comprehensive anti-patterns catalogue (reflection macros, #include "Class.generated.h" strictly last, GC pointer safety using TObjectPtr<> vs raw pointers, replication boilerplate with DOREPLIFETIME, avoidance of non-Unreal STL types).
   - .agents/rules/constraint-retention.md: Formal 7 Core Constraints + new MVP directives (No interiors, Solo BR, Server-Authoritative, 3rd Person, 3 Materials, Hybrid Hit Detection, BR Prefix, 10-Bot MVP test scenario, 2 Weapon Prototypes: AR Hit-Scan + Rocket Launcher Projectile splash, 2 GameModes: FFA + Classic BR, Building paused for Demo 1).
   - .agents/rules/sequential-thinking.md: Mandatory 5-stage sequential reasoning protocol required for all agents before implementation.
   - .agents/rules/unreal-analyzer-validation.md: AST inspection rules, Clang checks, header hygiene, and reflection validation.
2. Update .agents/AGENTS.md to reference the rule files and incorporate the latest MVP constraints.
3. Create scripts/verify-rules.ps1 (PowerShell test script) that checks rule files existence, validates that all 7 constraints + MVP directives are specified, and tests AST/regex validation rules against sample C++ patterns.
4. Run the validation script and verify all checks pass.
5. Write comprehensive handoff to:
   C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_m2\handoff.md
