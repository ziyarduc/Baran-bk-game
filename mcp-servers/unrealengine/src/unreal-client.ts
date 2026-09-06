import * as net from 'node:net';
import * as path from 'node:path';
import {
  RemoteExecution,
  RemoteExecutionConfig,
  EExecMode,
  type IRemoteExecutionMessageCommandOutputData,
} from 'unreal-remote-execution';

export interface TcpCheckResult {
  reachable: boolean;
  host: string;
  port: number;
  latencyMs?: number;
  error?: string;
}

export interface PythonExecutionResult {
  success: boolean;
  output: string;
  result?: string;
  error?: string;
}

export interface SpawnActorParams {
  actor_class: string;
  location: { x: number; y: number; z: number };
  rotation?: { pitch?: number; yaw?: number; roll?: number };
}

export interface CaptureViewportParams {
  output_path?: string;
  resolution_x?: number;
  resolution_y?: number;
}

export class UnrealClient {
  private remoteExec: RemoteExecution | null = null;
  private isStarted = false;
  private host: string;
  private port: number;
  private multicastGroup: string;
  private multicastPort: number;

  constructor(
    host: string = '127.0.0.1',
    port: number = 6776,
    multicastGroup: string = '239.0.0.1',
    multicastPort: number = 6766
  ) {
    this.host = host;
    this.port = port;
    this.multicastGroup = multicastGroup;
    this.multicastPort = multicastPort;
  }

  /**
   * Initializes the RemoteExecution instance.
   */
  private async ensureRemoteExecStarted(): Promise<RemoteExecution | null> {
    if (this.remoteExec && this.isStarted) {
      return this.remoteExec;
    }

    try {
      const config = new RemoteExecutionConfig(
        0,
        [this.multicastGroup, this.multicastPort],
        '0.0.0.0',
        [this.host, this.port]
      );
      this.remoteExec = new RemoteExecution(config);
      await this.remoteExec.start();
      this.isStarted = true;
      return this.remoteExec;
    } catch (err: any) {
      // If UDP multicast cannot bind, log warning and return null
      console.error(`[UnrealClient] Failed to initialize UDP multicast remote execution: ${err.message}`);
      return null;
    }
  }

  /**
   * Tests direct TCP connectivity to UE5 Python Remote Execution endpoint.
   */
  public async testTcpConnection(timeoutMs = 2000): Promise<TcpCheckResult> {
    const startTime = Date.now();

    return new Promise((resolve) => {
      const socket = new net.Socket();
      let resolved = false;

      const finish = (result: TcpCheckResult) => {
        if (!resolved) {
          resolved = true;
          socket.destroy();
          resolve(result);
        }
      };

      socket.setTimeout(timeoutMs);

      socket.on('connect', () => {
        const latencyMs = Date.now() - startTime;
        finish({
          reachable: true,
          host: this.host,
          port: this.port,
          latencyMs,
        });
      });

      socket.on('timeout', () => {
        finish({
          reachable: false,
          host: this.host,
          port: this.port,
          error: `Connection timed out after ${timeoutMs}ms`,
        });
      });

      socket.on('error', (err: any) => {
        finish({
          reachable: false,
          host: this.host,
          port: this.port,
          error: err.code || err.message,
        });
      });

      socket.connect(this.port, this.host);
    });
  }

  /**
   * Pings editor port 6776 and checks discovery status.
   */
  public async pingEditor(timeoutMs = 2000): Promise<{
    reachable: boolean;
    host: string;
    port: number;
    latencyMs?: number;
    remoteNodesCount: number;
    remoteNodes: any[];
    status: string;
    message: string;
  }> {
    const tcpCheck = await this.testTcpConnection(timeoutMs);
    let remoteNodes: any[] = [];

    try {
      const rExec = await this.ensureRemoteExecStarted();
      if (rExec) {
        remoteNodes = rExec.remoteNodes.map((n) => ({
          nodeId: n.nodeId,
          data: n.data,
        }));
      }
    } catch {
      // Ignore discovery errors during ping
    }

    if (tcpCheck.reachable) {
      return {
        reachable: true,
        host: this.host,
        port: this.port,
        latencyMs: tcpCheck.latencyMs,
        remoteNodesCount: remoteNodes.length,
        remoteNodes,
        status: 'CONNECTED',
        message: `Successfully reached Unreal Engine Python Remote Execution on ${this.host}:${this.port}. Latency: ${tcpCheck.latencyMs}ms.`,
      };
    }

    return {
      reachable: false,
      host: this.host,
      port: this.port,
      remoteNodesCount: remoteNodes.length,
      remoteNodes,
      status: 'OFFLINE',
      message: `Unreal Engine Python Remote Execution on ${this.host}:${this.port} is unreachable (${tcpCheck.error || 'OFFLINE'}). Verify Unreal Editor is running with Python Remote Execution enabled.`,
    };
  }

  /**
   * Direct TCP execution fallback for UE5 remote execution protocol.
   */
  private async executePythonDirectTcp(code: string, timeoutMs = 5000): Promise<PythonExecutionResult> {
    return new Promise((resolve) => {
      const socket = new net.Socket();
      let resolved = false;
      let buffer = '';

      const finish = (res: PythonExecutionResult) => {
        if (!resolved) {
          resolved = true;
          socket.destroy();
          resolve(res);
        }
      };

      socket.setTimeout(timeoutMs);

      socket.on('connect', () => {
        const payload = JSON.stringify({
          version: 1,
          magic: 'ue_py',
          type: 'command',
          source: 'unreal-mcp-server',
          data: {
            command: code,
            unattended: true,
            exec_mode: 'ExecuteFile',
          },
        });
        socket.write(payload);
      });

      socket.on('data', (data) => {
        buffer += data.toString('utf-8');
        try {
          const parsed = JSON.parse(buffer);
          if (parsed && parsed.data) {
            const outLines = Array.isArray(parsed.data.output)
              ? parsed.data.output.map((o: any) => o.output || '').join('\n')
              : (parsed.data.output || '');
            finish({
              success: parsed.data.success !== false,
              output: outLines,
              result: parsed.data.result || '',
            });
          }
        } catch {
          // Continue buffering if JSON is fragmented
        }
      });

      socket.on('timeout', () => {
        finish({
          success: false,
          output: buffer,
          error: `Direct TCP execution timed out after ${timeoutMs}ms`,
        });
      });

      socket.on('error', (err: any) => {
        finish({
          success: false,
          output: buffer,
          error: `Direct TCP execution error: ${err.message || err.code}`,
        });
      });

      socket.connect(this.port, this.host);
    });
  }

  /**
   * Executes Python code inside Unreal Engine 5 editor.
   */
  public async executePython(
    code: string,
    options: {
      unattended?: boolean;
      execMode?: 'ExecuteFile' | 'ExecuteStatement' | 'EvaluateStatement';
      timeoutMs?: number;
    } = {}
  ): Promise<PythonExecutionResult> {
    const unattended = options.unattended ?? true;
    const timeoutMs = options.timeoutMs ?? 10000;
    const execMode = options.execMode === 'EvaluateStatement'
      ? EExecMode.EVALUATE_STATEMENT
      : options.execMode === 'ExecuteStatement'
      ? EExecMode.EXECUTE_STATEMENT
      : EExecMode.EXECUTE_FILE;

    // First, verify TCP port reachability
    const tcpCheck = await this.testTcpConnection(1500);
    if (!tcpCheck.reachable) {
      return {
        success: false,
        output: '',
        error: `Cannot execute Python: UE5 Editor Python Remote Execution endpoint ${this.host}:${this.port} is unreachable (${tcpCheck.error || 'OFFLINE'}). Please start Unreal Editor with BakirkoyBR.`,
      };
    }

    // Try through unreal-remote-execution SDK
    try {
      const rExec = await this.ensureRemoteExecStarted();
      if (rExec) {
        if (!rExec.hasCommandConnection()) {
          const node = await rExec.getFirstRemoteNode(500, 3000);
          if (node) {
            await rExec.openCommandConnection(node, true, 3000);
          }
        }

        if (rExec.hasCommandConnection()) {
          const result: IRemoteExecutionMessageCommandOutputData = await rExec.runCommand(
            code,
            unattended,
            execMode,
            false
          );

          const outputText = result.output.map((item) => item.output).join('\n');
          return {
            success: result.success,
            output: outputText,
            result: result.result,
          };
        }
      }
    } catch (sdkError: any) {
      // SDK discovery/connection failed, attempt direct TCP fallback
      console.warn(`[UnrealClient] SDK execution failed (${sdkError.message}), attempting direct TCP execution fallback.`);
    }

    // Direct TCP fallback
    return await this.executePythonDirectTcp(code, timeoutMs);
  }

  /**
   * Spawns an actor by class or asset path at specified world location and rotation.
   */
  public async spawnActor(params: SpawnActorParams): Promise<PythonExecutionResult & { actor_name?: string }> {
    const { actor_class, location, rotation } = params;
    const rotPitch = rotation?.pitch ?? 0;
    const rotYaw = rotation?.yaw ?? 0;
    const rotRoll = rotation?.roll ?? 0;

    const pythonScript = `
import unreal
import json

actor_class_str = ${JSON.stringify(actor_class)}
loc = unreal.Vector(${Number(location.x)}, ${Number(location.y)}, ${Number(location.z)})
rot = unreal.Rotator(${Number(rotPitch)}, ${Number(rotYaw)}, ${Number(rotRoll)})

actor_cls = unreal.load_class(None, actor_class_str)
if not actor_cls:
    try:
        actor_cls = unreal.EditorAssetLibrary.load_blueprint_class(actor_class_str)
    except Exception:
        pass

if not actor_cls:
    print(f"ERROR: Could not find or load class '{actor_class_str}'")
else:
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_cls, loc, rot)
    if actor:
        name = actor.get_name()
        print(f"SUCCESS: Spawned actor '{name}' at ({loc.x}, {loc.y}, {loc.z})")
    else:
        print(f"ERROR: Failed to spawn actor '{actor_class_str}' at ({loc.x}, {loc.y}, {loc.z})")
`;

    const result = await this.executePython(pythonScript.trim());
    let actor_name: string | undefined;

    if (result.success && result.output.includes("SUCCESS: Spawned actor '")) {
      const match = result.output.match(/SUCCESS: Spawned actor '([^']+)'/);
      if (match) {
        actor_name = match[1];
      }
    }

    return {
      ...result,
      actor_name,
    };
  }

  /**
   * Captures a high-resolution screenshot from the active UE5 editor viewport.
   */
  public async captureViewport(params?: CaptureViewportParams): Promise<PythonExecutionResult & { file_path?: string }> {
    const resX = params?.resolution_x ?? 1920;
    const resY = params?.resolution_y ?? 1080;
    const rawPath = params?.output_path ?? '';
    const normPath = rawPath ? path.resolve(rawPath).replace(/\\/g, '/') : '';

    const pythonScript = `
import unreal
import os

res_x = ${resX}
res_y = ${resY}
custom_path = ${JSON.stringify(normPath)}

if custom_path:
    save_path = custom_path
else:
    proj_saved = unreal.Paths.project_saved_dir()
    save_path = os.path.join(proj_saved, "Screenshots", "EditorViewport.png").replace("\\\\", "/")

save_dir = os.path.dirname(os.path.abspath(save_path))
os.makedirs(save_dir, exist_ok=True)

unreal.AutomationLibrary.take_high_res_screenshot(res_x, res_y, save_path)
print(f"SUCCESS: Viewport screenshot scheduled to '{save_path}' at {res_x}x{res_y}")
`;

    const result = await this.executePython(pythonScript.trim());
    let file_path: string | undefined;

    if (result.success && result.output.includes("SUCCESS: Viewport screenshot scheduled to '")) {
      const match = result.output.match(/SUCCESS: Viewport screenshot scheduled to '([^']+)'/);
      if (match) {
        file_path = match[1];
      }
    }

    return {
      ...result,
      file_path,
    };
  }

  /**
   * Closes connections and cleans up sockets.
   */
  public stop(): void {
    if (this.remoteExec) {
      try {
        this.remoteExec.stop();
      } catch (err) {
        // Ignore cleanup errors
      }
      this.remoteExec = null;
      this.isStarted = false;
    }
  }
}
