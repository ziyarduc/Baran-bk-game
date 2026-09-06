# Handoff Report: UE5-MCP (R3) & Editor Automation (R1) Survey

**Explorer**: Survey Explorer 1  
**Working Directory**: `C:\Users\silver\Desktop\bakirkoy-br\.agents\teamwork_preview_explorer_survey_1`  
**Date**: 2026-09-06  
**Status**: Investigation Complete (Read-Only)

---

## 1. Observation

### 1.1 Local Workspace State (`C:\Users\silver\Desktop\bakirkoy-br`)
1. **UE5 Project File**:
   - File: `C:\Users\silver\Desktop\bakirkoy-br\BakirkoyBR\BakirkoyBR.uproject`
   - Content observed:
     ```json
     {
         "FileVersion": 3,
         "EngineAssociation": "5.5",
         "Category": "",
         "Description": "Bakırköy: Son Çember - 3D Battle Royale",
         "Modules": [
             {
                 "Name": "BakirkoyBR",
                 "Type": "Runtime",
                 "LoadingPhase": "Default",
                 "AdditionalDependencies": [
                     "Engine",
                     "AIModule",
                     "NavigationSystem"
                 ]
             }
         ]
     }
     ```
   - No `"Plugins"` array exists in `BakirkoyBR.uproject`.
2. **Missing Configuration & MCP Folders**:
   - No `Config/` directory or `DefaultEngine.ini` exists under `BakirkoyBR/`.
   - No `mcp-servers/` directory exists anywhere within the workspace.
   - No `package.json` or `node_modules` exists anywhere within the workspace.
3. **Host System Environment**:
   - Running command: `node -v; npm -v; python --version; git --version`
   - Result:
     - Node.js: `v24.19.0`
     - npm: `11.17.0`
     - Python: `3.14.3`
     - Git: `2.53.0.windows.1`

### 1.2 Investigation of `VedantRGosavi/UE5-MCP`
1. **Repository Status & Metadata**:
   - URL: `https://github.com/VedantRGosavi/UE5-MCP` (Created: 2025-03-15, Stars: 426, Forks: 57).
   - In `README.md`:
     > *"UPDATE: unfortunately we didnt move forward with the project due to time constraints. Feel free to use the docs."*
   - The repository is entirely architectural documentation and specifications; it contains no executable TypeScript or C++ source code.
2. **Documented Architecture**:
   - `monorepo_structure.md` outlines a target modular layout (`modules/ue5-mcp/`, `modules/blender-mcp/`, `modules/protocol/`).
   - `research.md` (lines 40–120) describes the mechanics of connecting external agents to Unreal Engine:
     - **Protocol 1 (Native UE5)**: Built-in Python Remote Execution using UDP multicast discovery and a TCP socket server on port `6776`.
     - **Protocol 2**: Unreal Remote Control API (HTTP/WebSocket) via the Remote Control Plugin.
     - **Protocol 3**: In-engine custom TCP socket servers (referencing `kvick-games/UnrealMCP`).
3. **The TypeScript / Node.js UE5 MCP Implementation Landscape**:
   - Production implementations leveraging UE5's native Python Remote Execution (e.g. `sam-david/unreal-mcp`, `aadeshrao123/Unreal-MCP`, `nils-soderman`) rely on the zero-dependency npm package `unreal-remote-execution` (v1.1.0, published by Nils Soderman).
   - Package `unreal-remote-execution`:
     - Implements the complete Unreal Python Remote Execution wire protocol.
     - Multicast discovery on UDP `239.0.0.1:6766`.
     - Command channel on TCP port `6776`.
     - Inverted connection architecture: the client listens and Unreal connects back, or communicates directly via command socket with message framing `ue_py` + UUIDs + JSON payloads (`ExecuteFile`, `EvaluateStatement`, `open_connection`).

### 1.3 Investigation of `believer-oss/Claireon` (R1 Editor Automation)
1. **Repository Metadata**:
   - URL: `https://github.com/believer-oss/Claireon` (The Believer Company, MIT License, C++).
   - Target Engine: Unreal Engine 5.5+.
2. **Architecture**:
   - It is a native C++ editor plugin (`Claireon.uplugin`) embedding a Model Context Protocol (MCP) server directly inside `UnrealEditor.exe`.
   - **Transport**: Streamable HTTP (SSE/HTTP) bound to a deterministic per-worktree port:
     `SHA-256(canonical project root) folded into ephemeral range 49152-65535`.
   - **Proxy Subsystem**: Includes `Content/Python/claireon_proxy.py` and `Scripts/Utilities/Start-MCPProxy.ps1` listening on port `43017` to keep AI agents connected across editor restarts and crashes.
   - **Tool Catalog**: Deliberately exposes a compact root MCP surface:
     - `tool_search`: Queries a catalog of 600+ tools using SQLite FTS5 and a vendored local embedding model (`bge-small-en-v1.5-int8`).
     - `python_execute`: Executes arbitrary editor Python scripts with watchdog timeout and audit logging.
     - `proxy`: Session management and editor launch meta-tool.
   - **Covered Subsystems**: Blueprint graph editing, UMG widget tree authoring, StateTree, BehaviorTree/EQS, Niagara VFX, PCG graphs, DataTables, Level Sequences, Asset Validation/Resave, PIE automation, and Unreal Insights trace analysis.

---

## 2. Logic Chain

```
[Observation 1.1] ──> BakirkoyBR.uproject has no Python plugins; no Config/DefaultEngine.ini exists; no mcp-servers exists.
                            │
                            ▼
[Observation 1.2] ──> VedantRGosavi/UE5-MCP is a specification repo; it specifies TCP port 6776 remote execution.
                      npm package `unreal-remote-execution` provides the exact wire protocol in TypeScript.
                            │
                            ▼
[Deduction 2.1]   ──> Acceptance criteria requires `mcp-servers/unrealengine/build/index.js` exposing:
                      1. `execute_python`
                      2. `spawn_actor`
                      3. `capture_viewport`
                      This server can be cleanly built in Node/TypeScript using `@modelcontextprotocol/sdk` and `unreal-remote-execution`.
                            │
                            ▼
[Observation 1.3] ──> believer-oss/Claireon is an in-engine C++ plugin running a native HTTP MCP server with 600+ tools.
                            │
                            ▼
[Deduction 2.2]   ──> Claireon and UE5-MCP address complementary layers:
                      - UE5-MCP (R3): Zero-compilation, out-of-process lightweight Node.js TCP bridge on port 6776. Ideal for fast script execution, actor spawning, viewport capture.
                      - Claireon (R1): In-process C++ plugin with semantic tool discovery and deep structural Blueprint/UMG/asset editing.
                            │
                            ▼
[Conclusion]      ──> Recommend a Two-Tier Architecture:
                      Tier 1: Implement `mcp-servers/unrealengine` (Node/TypeScript) for R3.
                      Tier 2: Configure UE5 PythonScriptPlugin in DefaultEngine.ini and integrate Claireon plugin for R1.
```

1. **Local Project Readiness**:
   - `BakirkoyBR.uproject` targets UE 5.5 (`EngineAssociation: 5.5`).
   - Python execution will not work until `PythonScriptPlugin` and `EditorScriptingUtilities` are declared in `BakirkoyBR.uproject` and enabled in `Config/DefaultEngine.ini`.
2. **UE5-MCP Architecture & Tool Formulation**:
   - External clients cannot execute Python in UE5 without connecting to UE5's `PythonScriptPlugin` Remote Execution listener on TCP port `6776`.
   - The three tools required by R3 are mapped to Unreal Python APIs:
     - `execute_python(code)`: Directly dispatched to `remoteExecution.runCommand(code)`.
     - `spawn_actor(actor_class, location, rotation)`: Generates Python code invoking `unreal.EditorLevelLibrary.spawn_actor_from_class(...)` or `unreal.load_class` and executes via command channel.
     - `capture_viewport(filename)`: Generates Python code invoking `unreal.AutomationLibrary.take_high_res_screenshot(...)` or `unreal.EditorLevelLibrary.editor_invalidate_viewports()`.
3. **Comparison between UE5-MCP and Claireon**:
   | Feature | UE5-MCP (`mcp-servers/unrealengine`) | believer-oss/Claireon |
   | :--- | :--- | :--- |
   | **Runtime Location** | Out-of-process Node.js process | In-process Unreal Editor C++ module |
   | **Transport** | TCP port 6776 (+ UDP 6766 discovery) | Streamable HTTP (SSE) on dynamic port (49152-65535) |
   | **Dependencies** | Node.js, `@modelcontextprotocol/sdk`, `unreal-remote-execution` | Visual Studio C++ compiler, UBT, Unreal Engine 5.5+ source/header |
   | **Setup Complexity** | Low (instant `npm install && npm run build`) | Medium-High (C++ plugin compilation required) |
   | **Capabilities** | Python execution, actor spawning, viewport captures | 600+ native C++ editor tools, Blueprint node wiring, UMG authoring, asset locking |
   | **Primary Role** | R3 Bridge for external AI agents | R1 Deep Editor Automation & Asset Manipulation |

---

## 3. Caveats

1. **No Running Unreal Editor Instance**:
   - The Unreal Editor was not actively running during this survey. Port `6776` could not be connected to live. Verification commands are provided to test as soon as the editor is launched.
2. **UE 5.5 Multicast Network Binding**:
   - On Windows with multiple network adapters (Hyper-V, WSL, Tailscale, VPNs), Unreal's UDP multicast on `239.0.0.1:6766` can occasionally bind to the wrong network adapter. Explicitly setting `RemoteExecutionMulticastBindAddress="0.0.0.0"` in `DefaultEngine.ini` resolves this issue.
3. **Claireon Compilation Requirements**:
   - Claireon requires compiling C++ code (`Claireon.uplugin`) via UnrealBuildTool. If the user does not have a C++ compiler (Visual Studio 2022 / MSVC toolchain) configured for UE 5.5, Tier 1 (`mcp-servers/unrealengine`) will continue to function independently via Python remote execution without requiring plugin compilation.

---

## 4. Conclusion & Recommended Integration Strategy

### 4.1 Two-Tier Integration Strategy
1. **Tier 1 (Immediate R3 Implementation)**:
   - Build a standalone Node.js / TypeScript MCP server in `C:\Users\silver\Desktop\bakirkoy-br\mcp-servers\unrealengine`.
   - Expose the required tools: `execute_python`, `spawn_actor`, `capture_viewport`.
   - Compile via `npm run build` to generate `mcp-servers/unrealengine/build/index.js`.
   - Register this server in agent MCP configurations (`command: "node"`, `args: ["C:/Users/silver/Desktop/bakirkoy-br/mcp-servers/unrealengine/build/index.js"]`).
2. **Tier 2 (R1 Deep Editor Automation)**:
   - Add `Plugins/Claireon` to `BakirkoyBR` for in-depth Blueprint graph manipulation, UMG widget generation, and asset diffing.
   - Utilize Claireon's `tool_search` and Python proxy when complex C++ automation is required.

### 4.2 Exact UE5 Configuration Requirements (Python Remote Execution Port 6776)

#### A. Modify `BakirkoyBR/BakirkoyBR.uproject`
Add the required editor scripting plugins:
```json
{
    "FileVersion": 3,
    "EngineAssociation": "5.5",
    "Category": "",
    "Description": "Bakırköy: Son Çember - 3D Battle Royale",
    "Modules": [
        {
            "Name": "BakirkoyBR",
            "Type": "Runtime",
            "LoadingPhase": "Default",
            "AdditionalDependencies": [
                "Engine",
                "AIModule",
                "NavigationSystem"
            ]
        }
    ],
    "Plugins": [
        {
            "Name": "PythonScriptPlugin",
            "Enabled": true
        },
        {
            "Name": "EditorScriptingUtilities",
            "Enabled": true
        }
    ]
}
```

#### B. Create `BakirkoyBR/Config/DefaultEngine.ini`
Create this file to enforce Remote Execution on port 6776:
```ini
[URL]
GameName=BakirkoyBR

[/Script/PythonScriptPlugin.PythonScriptPluginSettings]
bDeveloperMode=True
bRemoteExecution=True
bRemoteExecutionEnable=True
RemoteExecutionMulticastGroupEndpoint="239.0.0.1:6766"
RemoteExecutionMulticastBindAddress="0.0.0.0"
RemoteExecutionCommandEndpoint="127.0.0.1:6776"
RemoteExecutionMulticastTTL=0
```

#### C. Editor Preferences / GUI Path
When opening the Unreal Editor:
1. Navigate to **Edit > Project Settings...**
2. Scroll down to **Plugins > Python**.
3. Under **Python Remote Execution**:
   - Check **Enable Remote Execution?** (`bRemoteExecution`).
   - Confirm **Command Endpoint** is set to `127.0.0.1:6776`.
   - Confirm **Multicast Group Endpoint** is set to `239.0.0.1:6766`.
   - Set **Multicast Bind Address** to `0.0.0.0`.

### 4.3 Architecture & Implementation Blueprint for `mcp-servers/unrealengine`

#### Directory Structure
```
C:\Users\silver\Desktop\bakirkoy-br\mcp-servers\unrealengine\
├── package.json
├── tsconfig.json
└── src\
    ├── index.ts
    ├── unrealClient.ts
    └── tools\
        ├── executePython.ts
        ├── spawnActor.ts
        └── captureViewport.ts
```

#### `package.json` Specification
```json
{
  "name": "unreal-mcp-server",
  "version": "1.0.0",
  "description": "MCP Server for Unreal Engine 5 via Python Remote Execution",
  "main": "build/index.js",
  "type": "module",
  "scripts": {
    "build": "tsc",
    "start": "node build/index.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.6.1",
    "unreal-remote-execution": "^1.1.0"
  },
  "devDependencies": {
    "@types/node": "^22.13.0",
    "typescript": "^5.7.0"
  }
}
```

#### Core Tool Specifications
1. **`execute_python`**:
   - Input: `{ "code": string }`
   - Logic: Dispatches raw Python to `RemoteExecution.runCommand(code, true)`. Returns captured stdout and stderr.
2. **`spawn_actor`**:
   - Input:
     ```json
     {
       "actor_class": "/Script/Engine.StaticMeshActor",
       "location": { "x": 0, "y": 0, "z": 100 },
       "rotation": { "pitch": 0, "yaw": 0, "roll": 0 }
     }
     ```
   - Generated Python payload:
     ```python
     import unreal
     actor_cls = unreal.load_class(None, "{actor_class}")
     loc = unreal.Vector({location.x}, {location.y}, {location.z})
     rot = unreal.Rotator({rotation.pitch}, {rotation.yaw}, {rotation.roll})
     actor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_cls, loc, rot)
     print(f"Spawned: {actor.get_name() if actor else 'FAILED'}")
     ```
3. **`capture_viewport`**:
   - Input: `{ "output_path": string (optional), "resolution_x": 1920, "resolution_y": 1080 }`
   - Generated Python payload:
     ```python
     import unreal
     unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "{output_path}")
     print("Viewport screenshot triggered")
     ```

---

## 5. Verification Method

### 5.1 Verification of UE5 Python Remote Execution Port
Once Unreal Editor is running with `BakirkoyBR.uproject`:
```powershell
# Check if port 6776 is actively listening
Get-NetTCPConnection -LocalPort 6776 -State Listen -ErrorAction SilentlyContinue

# Test TCP socket connection to port 6776
Test-NetConnection -ComputerName 127.0.0.1 -Port 6776
```

### 5.2 Standalone Python Verification Script
Test remote execution from the host Python installation (`Python 3.14.3`):
```python
# test_remote_execution.py
import socket
import json

# Test connecting to UE5 Remote Execution port 6776
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3.0)
try:
    sock.connect(("127.0.0.1", 6776))
    print("[SUCCESS] Connected to UE5 Python Remote Execution port 6776!")
    sock.close()
except Exception as e:
    print(f"[ERROR] Could not connect: {e}")
```

### 5.3 MCP Server Build & Run Verification
After the implementer creates `mcp-servers/unrealengine`:
```powershell
cd C:\Users\silver\Desktop\bakirkoy-br\mcp-servers\unrealengine
npm install
npm run build

# Verify build artifact exists
Test-Path build\index.js

# Test launch MCP server (will output JSON-RPC handshake on stdio)
node build/index.js
```

### 5.4 Invalidation Conditions
- If `Get-NetTCPConnection -LocalPort 6776` returns null while the editor is open, Python Remote Execution is disabled or blocked by Windows Defender Firewall.
- If multicast discovery fails due to virtual network interfaces, `RemoteExecutionMulticastBindAddress="0.0.0.0"` must be re-verified in `DefaultEngine.ini`.
