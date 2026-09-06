## 2026-09-06T01:34:37Z

You are Challenger 2 for Bakırköy BR project.
Working Directory: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_challenger_2
Project Root: C:\Users\silver\Desktop\bakirkoy-br
Mandatory input:
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\ORIGINAL_REQUEST.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\AGENTS.md
- Read C:\Users\silver\Desktop\bakirkoy-br\.agents\PROJECT.md

Objective:
Adversarially challenge the error-prevention rules and constraint retention:
1. Stress-test scripts/verify-rules.ps1 with adversarial negative test cases:
   - Attempt to inject forbidden STL types (std::vector, std::string) into mock code.
   - Attempt to inject a 4th build material (e.g. Wood / Ahşap) or squad logic.
   - Attempt to place #include "Class.generated.h" before other includes.
   - Verify that the rules/linters catch every violation.
2. Test skills validator python .agents/skills/scripts/validate_all_skills.py against edge cases (corrupt YAML frontmatter, missing constraint section).
3. Document all stress test findings and state your verdict (APPROVE or REQUEST_CHANGES) in:
   C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_challenger_2\handoff.md
