# Token Optimization & Context Compression Protocol

## Objective
Minimize unnecessary token consumption across all agent operations, subagent dispatches, and inter-agent messaging, extending available quota and reducing latency without sacrificing reasoning depth or code quality.

---

## 1. Just-In-Time (JIT) Context Loading (Anti-Bloat)
- **Never Ingest the Full Catalog**: Never dump all 66+ skills or large catalog files (`SKILLS_CATALOG.md`) into a single agent prompt.
- **Selective Injection**: Pass ONLY the specific skill folder path (e.g., `.agents/skills/ue5-cpp-gameplay/SKILL.md`) relevant to the current task.
- **Reference on Demand**: Instruct workers to read sub-references only if a specific compile issue or API uncertainty arises.

---

## 2. Surgical File Operations (Diff-First Policy)
- **Prohibit Full-File Rewrites for Small Changes**: When fixing 1-10 lines (e.g. changing `AActor*` to `TObjectPtr<AActor>`), use targeted substring or line replacement (`replace_file_content`).
- **Never Echo Entire Files in Chat**: In handoff documents and status reports, only include the modified diff or line snippet, never the entire file content.

---

## 3. Log & Terminal Output Compression
- **Summary Over Raw Streams**: When executing test scripts or builds (e.g., `verify-rules.ps1`), summarize output to `Passed / Failed / Total` and only output the exact failing lines and stack traces.
- **Cap Test Logs**: Do not pipe 500+ lines of stdout into agent messages. Pipe to disk (`task.log`) and read only error lines using `Select-String` or regex.

---

## 4. Handoff & Inter-Agent Communication Minification
- **Standardized Compact Handoff Format**:
  All subagent `handoff.md` files must follow the compact 4-part schema:
  ```markdown
  ## Handoff: [TaskID]
  - **Verdict**: [DONE | BLOCKED]
  - **Modified Files**: [list of paths]
  - **Verification**: [Test command + exit code + summary]
  - **Next Action**: [Single sentence instruction]
  ```
- **Ban Conversational Filler**: Subagents must omit introductory, celebratory, or polite boilerplate in internal logs and handoffs.

---

## 5. Model Tier Efficiency
- Keep **Gemini 3.1 Pro** reserved exclusively for high-leverage architectural gating (Orchestrator, QA, Integrator, Challengers).
- Utilize **Gemini 3.8 Flash (High Thinking)** for all implementation workers (high throughput, low cost per token).
