# Claireon Editor Automation Integration Roadmap — Bakırköy BR

## Executive Overview
**Claireon** (`believer-oss/Claireon`, The Believer Company, MIT License) is an in-engine Model Context Protocol (MCP) server running directly inside `UnrealEditor.exe` (Unreal Engine 5.5+).

In the Bakırköy BR project architecture, editor automation is organized into a **Two-Tier System**:
1. **Tier 1 (Implemented — R3)**: `mcp-servers/unrealengine` — Lightweight out-of-process Node.js/TypeScript bridge communicating with Unreal's native `PythonScriptPlugin` over TCP port `6776` and UDP multicast `239.0.0.1:6766`. Handles rapid script execution, actor placement, and viewport capture with zero compilation overhead.
2. **Tier 2 (Roadmap — R1)**: `Plugins/Claireon` — In-process C++ editor plugin exposing 600+ native editor tools, Blueprint node generation, UMG UI authoring, StateTree editing, and SQLite FTS5 semantic tool discovery.

---

## Technical Comparison: Tier 1 vs. Tier 2

| Dimension | Tier 1: UE5-MCP (`mcp-servers/unrealengine`) | Tier 2: Claireon (`Plugins/Claireon`) |
| :--- | :--- | :--- |
| **Execution Environment** | External Node.js process | In-process Unreal Editor C++ module |
| **Communication Transport** | TCP port `6776` (command) + UDP `6766` (discovery) | Streamable HTTP (SSE) on dynamic port (49152–65535) |
| **Proxy Daemon** | Direct client retry / TCP ping | `claireon_proxy.py` / `Start-MCPProxy.ps1` (port `43017`) |
| **Compilation Requirements** | None (Node.js & TypeScript `tsc`) | UnrealBuildTool (UBT), Visual Studio 2022 / MSVC |
| **Tool Surface** | 4 Core Tools (`execute_python`, `spawn_actor`, `capture_viewport`, `ping_editor`) | 3 Root Meta-Tools (`tool_search`, `python_execute`, `proxy`) + 600+ internal tools |
| **Subsystem Reach** | Python API (`unreal.EditorLevelLibrary`, `unreal.AutomationLibrary`) | C++ Editor Subsystems: Blueprint Graphs, UMG, StateTree, Niagara, PCG, PIE, Unreal Insights |
| **Primary Use Cases** | Prototyping, bot placement, viewport screenshots, fast Python automation | Deep graph manipulation, UMG widget tree generation, StateTree authoring, asset validation |

---

## Architectural Deep-Dive: Claireon Subsystem

### 1. Dynamic Port Binding Formula
Claireon binds its in-editor HTTP server to a deterministic port calculated from the project directory hash to avoid collisions across multiple open projects or worktrees:
```
Port = 49152 + (SHA-256(canonical_project_root_path) mod (65535 - 49152))
```

### 2. The Persistent Proxy Subsystem (`Port 43017`)
When Unreal Editor restarts, hot-reloads, or crashes during asset compilation:
- External AI agents lose connection if connected directly to the editor's ephemeral HTTP port.
- Claireon provides `Content/Python/claireon_proxy.py` and `Scripts/Utilities/Start-MCPProxy.ps1`.
- The proxy listens on fixed port `43017`, maintains agent sessions across editor restarts, and buffers commands until the editor HTTP listener resumes.

### 3. Semantic Tool Discovery (`tool_search`)
Instead of overwhelming the LLM context with 600+ JSON schemas simultaneously:
- Claireon exposes only `tool_search`, `python_execute`, and `proxy` as root tools.
- `tool_search` queries an internal SQLite FTS5 index and vendored vector embeddings (`bge-small-en-v1.5-int8`).
- Agents query tools on demand (e.g. `tool_search("spawn bot actor with EQS")`), receiving exact parameters only when needed.

---

## Integration Roadmap: 5-Phase Deployment

### Phase 1: Tier 1 Operationalization (COMPLETED — Milestone M1)
- [x] Configure `BakirkoyBR.uproject` with `PythonScriptPlugin` and `EditorScriptingUtilities` (`Enabled: true`).
- [x] Configure `Config/DefaultEngine.ini` with `[/Script/PythonScriptPlugin.PythonScriptPluginSettings]` (port `6776`).
- [x] Build and verify `mcp-servers/unrealengine` with TypeScript MCP server exposing `execute_python`, `spawn_actor`, `capture_viewport`, `ping_editor`.
- [x] Create verification test suite `scripts/test_ue5_mcp_connection.js`.

### Phase 2: Claireon Source Ingestion & Plugin Build
- **Target Location**: `BakirkoyBR/Plugins/Claireon/`
- **Actions**:
  1. Clone or vendor `believer-oss/Claireon` repository into `BakirkoyBR/Plugins/Claireon`.
  2. Verify dependencies: Visual Studio 2022 with C++ Game Development workload, Windows SDK, Unreal Engine 5.5 source/headers.
  3. Add `Claireon` to `BakirkoyBR.uproject`:
     ```json
     {
       "Name": "Claireon",
       "Enabled": true
     }
     ```
  4. Build editor target via UnrealBuildTool:
     ```powershell
     & "$UE5_ROOT\Engine\Build\BatchFiles\Build.bat" BakirkoyBREditor Win64 Development "C:\Users\silver\Desktop\bakirkoy-br\BakirkoyBR\BakirkoyBR.uproject" -waitmutex
     ```

### Phase 3: Proxy Daemon Configuration & Agent Routing
- **Actions**:
  1. Configure PowerShell launch daemon in `scripts/start_claireon_proxy.ps1`:
     ```powershell
     python "C:\Users\silver\Desktop\bakirkoy-br\BakirkoyBR\Plugins\Claireon\Content\Python\claireon_proxy.py" --port 43017
     ```
  2. Add Claireon SSE HTTP configuration to Claude/Antigravity MCP settings:
     ```json
     {
       "mcpServers": {
         "claireon": {
           "url": "http://127.0.0.1:43017/sse"
         },
         "ue5-mcp": {
           "command": "node",
           "args": ["C:/Users/silver/Desktop/bakirkoy-br/mcp-servers/unrealengine/build/index.js"]
         }
       }
     }
     ```

### Phase 4: Project-Specific Constraint Enforcers (Bakırköy BR)
Claireon's `tool_search` and execution hooks must enforce the Bakırköy BR core constraints:
1. **No Interior Spaces Enforcer**:
   - Filter out tools creating interior NavMesh, interior collision volumes, or interior door actors.
   - Direct level building tools exclusively to exterior alleys, streets, external stairs, and rooftops.
2. **10-Bot Vertical Slice Automation**:
   - Automate placement of 10 `ABRAICharacter` bot spawn anchors across Bakırköy urban zones.
   - Validate rooftop external fire escape NavLink proxies using Claireon NavMesh inspection tools.
3. **Weapon Prototype Rigging**:
   - Inspect Blueprint nodes for AR (Hit-Scan logic) and Rocket Launcher (Projectile physics + splash radius).

### Phase 5: CI/CD & Headless Test Automation
- Automate editor launch in commandlet mode with Claireon enabled.
- Run automated Play-In-Editor (PIE) smoke tests:
  * Spawn 10 bots via MCP tool.
  * Verify bot pathfinding from street level to rooftop.
  * Trigger weapon firing tests and verify hit registration logs.
- Export Unreal Insights performance trace via Claireon and analyze frametime metrics.

---

## Fallback & Coexistence Policy
- If C++ compilation of `Claireon.uplugin` fails due to environment constraints (e.g. MSVC compiler version mismatch), the **Tier 1 UE5-MCP server** remains 100% operational and authoritative.
- All core editor automation tasks (Python code execution, bot spawning, viewport inspection) run unhindered via `mcp-servers/unrealengine` without requiring C++ compilation.
