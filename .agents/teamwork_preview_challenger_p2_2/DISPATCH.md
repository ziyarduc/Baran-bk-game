## 2026-09-06T16:19:14Z

You are Challenger P2-2.
Working Directory: C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_challenger_p2_2\
Project Root: C:\Users\silver\Desktop\bakirkoy-br\
Target File to Challenge: C:\Users\silver\Desktop\bakirkoy-br\package_game.ps1
Authoritative Request: C:\Users\silver\Desktop\bakirkoy-br\ORIGINAL_REQUEST.md
Scope Document: C:\Users\silver\Desktop\bakirkoy-br\.agents\PROJECT.md

## CRITICAL DIRECTIVES
- Unreal Engine 5 is NOT installed on this machine. Execution of RunUAT.bat live is explicitly WAIVED. DO NOT attempt to run RunUAT.bat live.
- Static and empirical verification is required: Write and execute adversarial PowerShell tests.

## Challenge Mandate
Adversarially challenge and stress-test `package_game.ps1`:
1. Write and execute an adversarial PowerShell test script in your working directory that asserts:
   - Parser AST integrity (0 errors, correct parameter count and types).
   - ValidateSet enforcement: verify valid configurations ('Shipping', 'Development') pass, and invalid configuration strings are rejected.
   - Parameter combinations: test `-Clean`, `-NoCompileEditor`, `-ValidateOnly`, `-DryRun`, `-OutputDir`.
   - Drive-letter robustness: simulate non-existent drives (e.g. `X:\Engine`, `Z:\Projects`) and confirm no unhandled DriveNotFoundException is thrown.
   - Command-line synthesis: verify generated RunUAT command line contains all required flags (`-project`, `-platform=Win64`, `-cook`, `-allmaps`, `-build`, `-stage`, `-pak`, `-iostore`, `-archive`, `-archivedirectory`).
   - Turkish-I culture test: verify script execution when `$CurrentCulture` is forced to `tr-TR`.
2. Capture test outputs and verify 100% pass.
3. Record your verdict (APPROVE or REQUEST_CHANGES) in `handoff.md`. Update `progress.md` and send completion message.
