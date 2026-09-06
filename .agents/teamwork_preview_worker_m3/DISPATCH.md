## 2026-09-06T01:30:20Z

You are Worker M3 (Skills Adaptation & Catalog Worker) for Bakırköy BR project.
Your Working Directory is: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_m3
Project Root: C:\Users\silver\Desktop\bakirkoy-br

MANDATORY INTEGRITY WARNING:
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Inputs:
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\AGENTS.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\PROJECT.md
- Read Spec Miner 2 Handoff: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_spec_miner_survey_2\handoff.md

Your exclusive write boundaries:
- .agents/skills/SKILLS_CATALOG.md
- .agents/skills/scripts/**
- .agents/skills/**/SKILL.md (adaptation injections)
- C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_m3/**

Tasks:
1. Audit and verify the 66+ skills existing in .agents/skills/ (from UnrealXu and kevinpbuckley + agent roles).
2. Generate a comprehensive master catalog at .agents/skills/SKILLS_CATALOG.md detailing every skill, its category, upstream source, key capabilities, and applicable Bakırköy BR constraints.
3. Ensure all skills respect the 7 Bakırköy BR Core Constraints and new MVP directives:
   - No Interior Spaces (exterior only)
   - Solo BR Only
   - Server-Authoritative
   - 3rd Person Camera
   - 3 Build Materials (Moloz, Tuğla, Çelik)
   - Hybrid Hit Detection
   - All C++ classes prefixed with BR
   - MVP directives: 10 bots scenario, 2 weapon prototypes (AR Hit-Scan, Rocket Launcher Projectile), 2 GameModes (FFA, Classic BR), Building paused for Demo 1.
4. Implement or update validation scripts in .agents/skills/scripts/ (e.g. validate_all_skills.py) to verify YAML frontmatters, required fields, and constraint references.
5. Run the validation scripts and verify 100% compliance.
6. Write comprehensive handoff to:
   C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_worker_m3\handoff.md
