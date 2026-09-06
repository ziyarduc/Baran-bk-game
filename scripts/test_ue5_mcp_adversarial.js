import * as cp from 'node:child_process';
import * as net from 'node:net';
import * as path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const MCP_BUILD_PATH = path.resolve(__dirname, '../mcp-servers/unrealengine/build/index.js');
const CONNECTION_SCRIPT_PATH = path.resolve(__dirname, 'test_ue5_mcp_connection.js');

let totalTests = 0;
let passedTests = 0;
let failedTests = 0;
const testRecords = [];

function recordResult(category, testName, passed, details = '') {
  totalTests++;
  if (passed) {
    passedTests++;
    console.log(`[PASS] [${category}] ${testName}`);
  } else {
    failedTests++;
    console.error(`[FAIL] [${category}] ${testName} - Details: ${details}`);
  }
  testRecords.push({ category, testName, passed, details });
}

// ---------------------------------------------------------------------------
// Helper: JSON-RPC Client over Stdio
// ---------------------------------------------------------------------------
class McpProcessClient {
  constructor(scriptPath) {
    this.scriptPath = scriptPath;
    this.process = null;
    this.buffer = '';
    this.responseWaiters = new Map();
    this.stderrLogs = [];
    this.isDead = false;
  }

  start() {
    this.process = cp.spawn(process.execPath, [this.scriptPath], {
      stdio: ['pipe', 'pipe', 'pipe'],
    });

    this.process.stdout.on('data', (data) => {
      this.buffer += data.toString('utf-8');
      const lines = this.buffer.split('\n');
      this.buffer = lines.pop(); // keep remainder

      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) continue;
        try {
          const parsed = JSON.parse(trimmed);
          if (parsed.id !== undefined && this.responseWaiters.has(parsed.id)) {
            const waiter = this.responseWaiters.get(parsed.id);
            this.responseWaiters.delete(parsed.id);
            waiter.resolve(parsed);
          }
        } catch {
          // not valid JSON-RPC, or fragmented
        }
      }
    });

    this.process.stderr.on('data', (data) => {
      this.stderrLogs.push(data.toString('utf-8'));
    });

    this.process.on('exit', (code, signal) => {
      this.isDead = true;
      for (const [, waiter] of this.responseWaiters.entries()) {
        waiter.reject(new Error(`Process exited with code ${code} (${signal}) before responding`));
      }
      this.responseWaiters.clear();
    });
  }

  sendRaw(data) {
    if (this.isDead) throw new Error('Process is dead');
    this.process.stdin.write(data);
  }

  sendRequest(method, params, id = Date.now() + Math.floor(Math.random() * 1000)) {
    return new Promise((resolve, reject) => {
      if (this.isDead) return reject(new Error('Process is dead'));
      const req = { jsonrpc: '2.0', id, method, params };
      const timeout = setTimeout(() => {
        if (this.responseWaiters.has(id)) {
          this.responseWaiters.delete(id);
          reject(new Error(`Timeout waiting for response to ${method} (id=${id})`));
        }
      }, 5000);

      this.responseWaiters.set(id, {
        resolve: (val) => {
          clearTimeout(timeout);
          resolve(val);
        },
        reject: (err) => {
          clearTimeout(timeout);
          reject(err);
        },
      });

      this.process.stdin.write(JSON.stringify(req) + '\n');
    });
  }

  sendNotification(method, params) {
    if (this.isDead) throw new Error('Process is dead');
    const notif = { jsonrpc: '2.0', method, params };
    this.process.stdin.write(JSON.stringify(notif) + '\n');
  }

  stop() {
    if (this.process && !this.isDead) {
      try {
        this.process.kill();
      } catch {}
    }
  }
}

// ---------------------------------------------------------------------------
// SUITE 1: Connection Script Testing (Offline vs Normal/Online)
// ---------------------------------------------------------------------------
async function testConnectionScriptOfflineAndOnline() {
  console.log('\n--- Running SUITE 1: scripts/test_ue5_mcp_connection.js Verification ---');

  // Test 1.1: Offline run
  const offlineResult = await new Promise((resolve) => {
    cp.exec(`node "${CONNECTION_SCRIPT_PATH}"`, (err, stdout, stderr) => {
      resolve({
        code: err ? err.code : 0,
        stdout,
        stderr,
      });
    });
  });

  const offlinePass =
    offlineResult.code === 0 &&
    offlineResult.stdout.includes('TCP Socket: 127.0.0.1:6776 is currently OFFLINE') &&
    offlineResult.stdout.includes('Status: OFFLINE') &&
    offlineResult.stdout.includes('VERIFICATION RESULT: ALL MCP TOOL SCHEMAS AND CLIENT METHODS VERIFIED');

  recordResult(
    'ConnectionScript',
    'Offline execution returns code 0 with informative OFFLINE status',
    offlinePass,
    offlineResult.stdout.slice(-300)
  );

  // Test 1.2: Normal (Online) run with a mock TCP server on 127.0.0.1:6776
  const mockServer = net.createServer((sock) => {
    // Basic mock connection
    sock.on('data', (d) => {
      // Respond to direct TCP commands if received
      sock.write(JSON.stringify({
        data: { success: true, output: [{ output: 'Mock executed' }], result: 'OK' }
      }));
    });
  });

  let serverListening = false;
  try {
    await new Promise((res, rej) => {
      mockServer.listen(6776, '127.0.0.1', () => {
        serverListening = true;
        res();
      });
      mockServer.on('error', rej);
    });

    const onlineResult = await new Promise((resolve) => {
      cp.exec(`node "${CONNECTION_SCRIPT_PATH}"`, (err, stdout, stderr) => {
        resolve({
          code: err ? err.code : 0,
          stdout,
          stderr,
        });
      });
    });

    const onlinePass =
      onlineResult.code === 0 &&
      onlineResult.stdout.includes('TCP Socket: 127.0.0.1:6776 is ACTIVE') &&
      onlineResult.stdout.includes('Status: CONNECTED') &&
      onlineResult.stdout.includes('Reachable: true') &&
      onlineResult.stdout.includes('VERIFICATION RESULT: ALL MCP TOOL SCHEMAS AND CLIENT METHODS VERIFIED');

    recordResult(
      'ConnectionScript',
      'Normal/Online execution returns code 0 with ACTIVE and CONNECTED status',
      onlinePass,
      onlineResult.stdout.slice(-300)
    );
  } catch (err) {
    recordResult('ConnectionScript', 'Normal/Online execution test failed to start mock server', false, err.message);
  } finally {
    if (serverListening) {
      await new Promise((res) => mockServer.close(res));
    }
  }
}

// ---------------------------------------------------------------------------
// SUITE 2: Standard JSON-RPC Flow via Stdio
// ---------------------------------------------------------------------------
async function testStdioJsonRpcFlow() {
  console.log('\n--- Running SUITE 2: Standard JSON-RPC Flow via Stdio ---');
  const client = new McpProcessClient(MCP_BUILD_PATH);
  client.start();

  try {
    // 2.1 Initialize
    const initRes = await client.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'adversarial-test', version: '1.0.0' },
    }, 1);

    const initValid =
      initRes &&
      initRes.result &&
      initRes.result.serverInfo &&
      initRes.result.serverInfo.name === 'unreal-mcp-server' &&
      initRes.result.capabilities &&
      initRes.result.capabilities.tools;

    recordResult('StdioJsonRpc', 'Initialize handshake returns valid serverInfo and capabilities', initValid);

    // 2.2 Initialized notification
    client.sendNotification('notifications/initialized', {});
    recordResult('StdioJsonRpc', 'Sent notifications/initialized without crash', !client.isDead);

    // 2.3 tools/list
    const toolsRes = await client.sendRequest('tools/list', {}, 2);
    const tools = toolsRes?.result?.tools || [];
    const expectedNames = ['execute_python', 'spawn_actor', 'capture_viewport', 'ping_editor'];
    const allToolsPresent = expectedNames.every((n) => tools.some((t) => t.name === n));

    recordResult(
      'StdioJsonRpc',
      `tools/list returns all 4 expected tools: [${expectedNames.join(', ')}]`,
      allToolsPresent && tools.length === 4
    );

    // 2.4 tools/call ping_editor
    const pingRes = await client.sendRequest('tools/call', {
      name: 'ping_editor',
      arguments: {},
    }, 3);

    const pingValid =
      pingRes &&
      pingRes.result &&
      Array.isArray(pingRes.result.content) &&
      pingRes.result.isError === false;

    let pingContent = null;
    try {
      pingContent = JSON.parse(pingRes.result.content[0].text);
    } catch {}

    const pingContentValid =
      pingContent &&
      pingContent.status !== undefined &&
      pingContent.host === '127.0.0.1' &&
      pingContent.port === 6776;

    recordResult(
      'StdioJsonRpc',
      'tools/call ping_editor returns valid tool result content with status and host info',
      pingValid && pingContentValid
    );

    // 2.5 tools/call execute_python under offline condition
    const execOfflineRes = await client.sendRequest('tools/call', {
      name: 'execute_python',
      arguments: { code: 'print("adversarial test")' },
    }, 4);

    const execOfflineValid =
      execOfflineRes &&
      execOfflineRes.result &&
      execOfflineRes.result.isError === true &&
      Array.isArray(execOfflineRes.result.content);

    let execOfflineText = execOfflineRes?.result?.content?.[0]?.text || '';
    const containsUnreachable = execOfflineText.includes('unreachable') || execOfflineText.includes('OFFLINE');

    recordResult(
      'StdioJsonRpc',
      'tools/call execute_python when offline returns isError: true with unreachable diagnostic',
      execOfflineValid && containsUnreachable
    );

    // Verify process is still alive and responsive after offline failure
    const pingPostExec = await client.sendRequest('tools/call', {
      name: 'ping_editor',
      arguments: {},
    }, 5);
    recordResult('StdioJsonRpc', 'Server remains alive and responsive after execution failure', !!pingPostExec?.result);

  } finally {
    client.stop();
  }
}

// ---------------------------------------------------------------------------
// SUITE 3: Parameter Validation & Tool Edge Cases
// ---------------------------------------------------------------------------
async function testParameterValidation() {
  console.log('\n--- Running SUITE 3: Parameter Validation & Tool Edge Cases ---');
  const client = new McpProcessClient(MCP_BUILD_PATH);
  client.start();

  try {
    await client.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'param-tester', version: '1.0.0' },
    }, 100);

    // 3.1 execute_python: missing 'code'
    const missingCodeRes = await client.sendRequest('tools/call', {
      name: 'execute_python',
      arguments: {},
    }, 101);
    const missingCodeRejected =
      (missingCodeRes.error && missingCodeRes.error.code === -32602) ||
      (missingCodeRes.result && missingCodeRes.result.isError);
    recordResult(
      'Validation',
      'execute_python rejects missing "code" parameter (InvalidParams / isError)',
      missingCodeRejected
    );

    // 3.2 execute_python: non-string 'code' (number)
    const numberCodeRes = await client.sendRequest('tools/call', {
      name: 'execute_python',
      arguments: { code: 12345 },
    }, 102);
    const numberCodeRejected =
      (numberCodeRes.error && numberCodeRes.error.code === -32602) ||
      (numberCodeRes.result && numberCodeRes.result.isError);
    recordResult(
      'Validation',
      'execute_python rejects non-string "code" parameter (number)',
      numberCodeRejected
    );

    // 3.3 execute_python: null 'code'
    const nullCodeRes = await client.sendRequest('tools/call', {
      name: 'execute_python',
      arguments: { code: null },
    }, 103);
    const nullCodeRejected =
      (nullCodeRes.error && nullCodeRes.error.code === -32602) ||
      (nullCodeRes.result && nullCodeRes.result.isError);
    recordResult(
      'Validation',
      'execute_python rejects null "code" parameter',
      nullCodeRejected
    );

    // 3.4 spawn_actor: missing actor_class
    const missingClassRes = await client.sendRequest('tools/call', {
      name: 'spawn_actor',
      arguments: { location: { x: 0, y: 0, z: 0 } },
    }, 104);
    const missingClassRejected =
      (missingClassRes.error && missingClassRes.error.code === -32602) ||
      (missingClassRes.result && missingClassRes.result.isError);
    recordResult(
      'Validation',
      'spawn_actor rejects missing "actor_class" parameter',
      missingClassRejected
    );

    // 3.5 spawn_actor: missing location
    const missingLocRes = await client.sendRequest('tools/call', {
      name: 'spawn_actor',
      arguments: { actor_class: '/Script/Engine.StaticMeshActor' },
    }, 105);
    const missingLocRejected =
      (missingLocRes.error && missingLocRes.error.code === -32602) ||
      (missingLocRes.result && missingLocRes.result.isError);
    recordResult(
      'Validation',
      'spawn_actor rejects missing "location" parameter',
      missingLocRejected
    );

    // 3.6 spawn_actor: malformed location (missing z coordinate)
    const malformedLocRes = await client.sendRequest('tools/call', {
      name: 'spawn_actor',
      arguments: { actor_class: '/Script/Engine.StaticMeshActor', location: { x: 100, y: 200 } },
    }, 106);
    const malformedLocRejected =
      (malformedLocRes.error && malformedLocRes.error.code === -32602) ||
      (malformedLocRes.result && malformedLocRes.result.isError);
    recordResult(
      'Validation',
      'spawn_actor rejects incomplete location (missing z coordinate)',
      malformedLocRejected
    );

    // 3.7 spawn_actor: non-numeric location coordinate
    const nonNumericLocRes = await client.sendRequest('tools/call', {
      name: 'spawn_actor',
      arguments: {
        actor_class: '/Script/Engine.StaticMeshActor',
        location: { x: 100, y: '200', z: 300 },
      },
    }, 107);
    const nonNumericLocRejected =
      (nonNumericLocRes.error && nonNumericLocRes.error.code === -32602) ||
      (nonNumericLocRes.result && nonNumericLocRes.result.isError);
    recordResult(
      'Validation',
      'spawn_actor rejects non-numeric location coordinate (string "200")',
      nonNumericLocRejected
    );

    // 3.8 Unknown tool call
    const unknownToolRes = await client.sendRequest('tools/call', {
      name: 'non_existent_tool_xyz',
      arguments: {},
    }, 108);
    const unknownToolRejected =
      (unknownToolRes.error && (unknownToolRes.error.code === -32601 || unknownToolRes.error.message.includes('Unknown tool'))) ||
      (unknownToolRes.result && unknownToolRes.result.isError);
    recordResult(
      'Validation',
      'tools/call rejects unknown tool name with MethodNotFound or McpError',
      unknownToolRejected
    );

    // 3.9 Unknown RPC method
    const unknownMethodRes = await client.sendRequest('random/unsupported_method', {}, 109);
    const unknownMethodRejected = unknownMethodRes.error !== undefined;
    recordResult(
      'Validation',
      'Unknown RPC method returns JSON-RPC error',
      unknownMethodRejected
    );

    // Server must still be alive
    recordResult('Validation', 'Server remains alive after all parameter validation rejections', !client.isDead);

  } finally {
    client.stop();
  }
}

// ---------------------------------------------------------------------------
// SUITE 4: Malformed Input & Stdio Resilience
// ---------------------------------------------------------------------------
async function testMalformedInputResilience() {
  console.log('\n--- Running SUITE 4: Malformed Input & Stdio Stream Resilience ---');
  const client = new McpProcessClient(MCP_BUILD_PATH);
  client.start();

  try {
    await client.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'fuzz-tester', version: '1.0.0' },
    }, 200);

    // 4.1 Send non-JSON text on stdin
    client.sendRaw('THIS_IS_DEFINITELY_NOT_JSON_GARBAGE\n');
    await new Promise((r) => setTimeout(r, 200));

    // Verify process did not crash
    let aliveAfterRawGarbage = !client.isDead;
    recordResult('Resilience', 'Server does not crash when raw non-JSON text is sent to stdin', aliveAfterRawGarbage);

    // 4.2 Send incomplete JSON syntax
    client.sendRaw('{"jsonrpc": "2.0", "method": "unclosed_json\n');
    await new Promise((r) => setTimeout(r, 200));

    let aliveAfterIncompleteJson = !client.isDead;
    recordResult('Resilience', 'Server does not crash on unclosed JSON syntax on stdin', aliveAfterIncompleteJson);

    // 4.3 Send valid JSON-RPC request immediately after malformed input
    const followUpPing = await client.sendRequest('tools/call', {
      name: 'ping_editor',
      arguments: {},
    }, 203);

    const followUpRecovered = followUpPing && followUpPing.result && !followUpPing.result.isError;
    recordResult(
      'Resilience',
      'Server successfully recovers and processes subsequent valid requests after syntax errors',
      followUpRecovered
    );

  } finally {
    client.stop();
  }
}

// ---------------------------------------------------------------------------
// SUITE 5: Port Edge Cases, Timeouts, and Socket Disconnects
// ---------------------------------------------------------------------------
async function testPortEdgeCasesAndDisconnects() {
  console.log('\n--- Running SUITE 5: Port Edge Cases, Timeouts & Sockets ---');
  const client = new McpProcessClient(MCP_BUILD_PATH);
  client.start();

  try {
    await client.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'socket-tester', version: '1.0.0' },
    }, 300);

    // 5.1 Test ping_editor with an unreachable IP / closed port
    const unreachablePing = await client.sendRequest('tools/call', {
      name: 'ping_editor',
      arguments: { host: '127.0.0.1', port: 59999, timeout_ms: 300 },
    }, 301);

    let unreachableContent = null;
    try {
      unreachableContent = JSON.parse(unreachablePing?.result?.content?.[0]?.text);
    } catch {}

    const unreachableHandled =
      unreachableContent &&
      unreachableContent.reachable === false &&
      unreachableContent.status === 'OFFLINE';

    recordResult(
      'Sockets',
      'ping_editor handles non-existent port (59999) gracefully with OFFLINE status',
      unreachableHandled
    );

    // 5.2 Abrupt RST / Disconnect: mock server closes connection immediately on accept
    let resetServer = net.createServer((sock) => {
      sock.destroy(); // immediately drop/destroy connection
    });

    let resetPort = 6789;
    await new Promise((res) => resetServer.listen(resetPort, '127.0.0.1', res));

    try {
      // ping_editor pointing to a server that resets connection
      const resetPing = await client.sendRequest('tools/call', {
        name: 'ping_editor',
        arguments: { host: '127.0.0.1', port: resetPort, timeout_ms: 500 },
      }, 302);

      recordResult(
        'Sockets',
        'ping_editor handles immediate socket reset without throwing uncaughtException',
        !!resetPing?.result
      );
    } finally {
      await new Promise((res) => resetServer.close(res));
    }

    // 5.3 Hanging TCP server on port 6776: accepts connection but never transmits command response
    let hangingServer = net.createServer((sock) => {
      // Accepts connection and swallows written command without sending response
      sock.on('data', () => {});
    });

    await new Promise((res) => hangingServer.listen(6776, '127.0.0.1', res));

    try {
      const startTime = Date.now();
      const timeoutExec = await client.sendRequest('tools/call', {
        name: 'execute_python',
        arguments: { code: 'print("hang test")', timeout_ms: 800 },
      }, 303);
      const elapsed = Date.now() - startTime;

      let content = null;
      try {
        content = JSON.parse(timeoutExec?.result?.content?.[0]?.text);
      } catch {}

      const timedOutProperly =
        timeoutExec?.result?.isError === true &&
        (content?.error?.includes('timed out') || elapsed >= 750);

      recordResult(
        'Sockets',
        `execute_python command timeout is enforced properly when remote host hangs (elapsed: ${elapsed}ms for 800ms timeout)`,
        timedOutProperly && !client.isDead
      );
    } finally {
      await new Promise((res) => hangingServer.close(res));
    }

  } finally {
    client.stop();
  }
}

// ---------------------------------------------------------------------------
// SUITE 6: End-to-End Mock UE5 Python Execution
// ---------------------------------------------------------------------------
async function testMockUe5Execution() {
  console.log('\n--- Running SUITE 6: Mock UE5 Direct TCP Python Execution ---');

  let mockUe5Server = net.createServer((sock) => {
    let buf = '';
    sock.on('data', (chunk) => {
      buf += chunk.toString('utf-8');
      try {
        const parsed = JSON.parse(buf);
        if (parsed.magic === 'ue_py' && parsed.type === 'command') {
          const cmd = parsed.data?.command || '';
          // Send back simulated UE5 Python response
          const resp = {
            version: 1,
            magic: 'ue_py',
            type: 'command_output',
            source: 'UE5Editor',
            data: {
              success: true,
              output: [
                { type: 'Info', output: `Simulated Executed: ${cmd.slice(0, 30)}` },
                { type: 'Info', output: 'Actor count: 10' }
              ],
              result: 'SUCCESS_MOCK'
            }
          };
          sock.write(JSON.stringify(resp));
        }
      } catch {}
    });
  });

  await new Promise((res) => mockUe5Server.listen(6776, '127.0.0.1', res));

  const client = new McpProcessClient(MCP_BUILD_PATH);
  client.start();

  try {
    await client.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'mock-ue5-client', version: '1.0.0' },
    }, 400);

    // Test execute_python with mock UE5 server responding
    const execRes = await client.sendRequest('tools/call', {
      name: 'execute_python',
      arguments: { code: 'print("Testing BakirkoyBR 10-bot spawner")' },
    }, 401);

    const isSuccess = execRes?.result?.isError === false;
    let contentObj = null;
    try {
      contentObj = JSON.parse(execRes?.result?.content?.[0]?.text);
    } catch {}

    const outputMatches = contentObj?.output?.includes('Simulated Executed') || contentObj?.result === 'SUCCESS_MOCK';

    recordResult(
      'MockExecution',
      'execute_python successfully executes and parses output from UE5 Remote Execution protocol',
      isSuccess && outputMatches
    );

    // Test spawn_actor with mock UE5 server
    const spawnRes = await client.sendRequest('tools/call', {
      name: 'spawn_actor',
      arguments: {
        actor_class: '/Script/BakirkoyBR.BRAICharacter',
        location: { x: 100, y: 200, z: 50 },
        rotation: { pitch: 0, yaw: 90, roll: 0 },
      },
    }, 402);

    recordResult(
      'MockExecution',
      'spawn_actor invokes direct TCP execution and handles response without error',
      spawnRes?.result?.isError === false
    );

  } finally {
    client.stop();
    await new Promise((res) => mockUe5Server.close(res));
  }
}

// ---------------------------------------------------------------------------
// SUITE 7: Concurrency & Rapid Requests
// ---------------------------------------------------------------------------
async function testConcurrencyAndStress() {
  console.log('\n--- Running SUITE 7: Concurrency & Rapid Request Stress ---');
  const client = new McpProcessClient(MCP_BUILD_PATH);
  client.start();

  try {
    await client.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'stress-tester', version: '1.0.0' },
    }, 500);

    // Send 15 concurrent ping_editor requests
    const promises = [];
    for (let i = 0; i < 15; i++) {
      promises.push(
        client.sendRequest('tools/call', {
          name: 'ping_editor',
          arguments: { timeout_ms: 500 },
        }, 600 + i)
      );
    }

    const results = await Promise.all(promises);
    const allSucceeded = results.every((r) => r && r.result && !r.result.isError);

    recordResult(
      'Stress',
      '15 concurrent tool calls handled simultaneously without dropping or corrupting stdio frames',
      allSucceeded
    );
  } finally {
    client.stop();
  }
}

// ---------------------------------------------------------------------------
// SUITE 8: Bakırköy BR Domain-Specific Tests (UTF-8 Turkish, Multi-line, Viewport)
// ---------------------------------------------------------------------------
async function testDomainSpecificAndViewport() {
  console.log('\n--- Running SUITE 8: Bakırköy BR Domain-Specific Tests (UTF-8, Viewport) ---');

  let mockUe5Server = net.createServer((sock) => {
    let buf = '';
    sock.on('data', (chunk) => {
      buf += chunk.toString('utf-8');
      try {
        const parsed = JSON.parse(buf);
        if (parsed.magic === 'ue_py' && parsed.type === 'command') {
          const cmd = parsed.data?.command || '';
          let outputText = 'Simulated Executed';
          if (cmd.includes('Bakırköy')) {
            outputText = 'SUCCESS: Bakırköy BR Türkce Karakterler: Tuğla, Moloz, Çelik, Şehir';
          } else if (cmd.includes('take_high_res_screenshot')) {
            outputText = "SUCCESS: Viewport screenshot scheduled to 'C:/Project/Saved/Screenshots/EditorViewport.png' at 1920x1080";
          }
          const resp = {
            version: 1,
            magic: 'ue_py',
            type: 'command_output',
            source: 'UE5Editor',
            data: {
              success: true,
              output: [{ type: 'Info', output: outputText }],
              result: 'SUCCESS_DOMAIN'
            }
          };
          sock.write(JSON.stringify(resp));
        }
      } catch {}
    });
  });

  await new Promise((res) => mockUe5Server.listen(6776, '127.0.0.1', res));

  const client = new McpProcessClient(MCP_BUILD_PATH);
  client.start();

  try {
    await client.sendRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'domain-tester', version: '1.0.0' },
    }, 700);

    // 8.1 Turkish UTF-8 strings & multi-line code
    const turkishCode = `
# Bakırköy BR Harita & İnşaat Testi
materyaller = ["Tuğla", "Moloz", "Çelik"]
alan = "Bakırköy Meydanı & Sahil"
print(f"Başlatıldı: {alan}, Materyaller: {materyaller}")
`;
    const turkishRes = await client.sendRequest('tools/call', {
      name: 'execute_python',
      arguments: { code: turkishCode },
    }, 701);

    let turkishContent = null;
    try {
      turkishContent = JSON.parse(turkishRes?.result?.content?.[0]?.text);
    } catch {}

    const turkishSuccess =
      turkishRes?.result?.isError === false &&
      turkishContent?.output?.includes('Bakırköy BR Türkce');

    recordResult(
      'DomainUTF8',
      'execute_python handles Turkish UTF-8 characters and multi-line script correctly',
      turkishSuccess
    );

    // 8.2 capture_viewport with mock UE5 server
    const viewportRes = await client.sendRequest('tools/call', {
      name: 'capture_viewport',
      arguments: { resolution_x: 2560, resolution_y: 1440 },
    }, 702);

    let viewportContent = null;
    try {
      viewportContent = JSON.parse(viewportRes?.result?.content?.[0]?.text);
    } catch {}

    const viewportSuccess =
      viewportRes?.result?.isError === false &&
      viewportContent?.file_path?.includes('EditorViewport.png');

    recordResult(
      'DomainUTF8',
      'capture_viewport returns file_path when UE5 responds successfully',
      viewportSuccess
    );

    // 8.3 Large payload script (64 KB)
    const largeComment = '# ' + 'A'.repeat(64 * 1024) + '\n';
    const largeScript = largeComment + 'print("Large payload survived")\n';

    const largeRes = await client.sendRequest('tools/call', {
      name: 'execute_python',
      arguments: { code: largeScript },
    }, 703);

    recordResult(
      'DomainUTF8',
      'Large 64KB Python script payload transmitted and handled without buffer corruption',
      largeRes?.result?.isError === false
    );

  } finally {
    client.stop();
    await new Promise((res) => mockUe5Server.close(res));
  }
}

// ---------------------------------------------------------------------------
// Main Runner
// ---------------------------------------------------------------------------
async function main() {
  console.log('='.repeat(70));
  console.log('Adversarial Test Suite for Bakırköy BR UE5-MCP Server');
  console.log('='.repeat(70));

  await testConnectionScriptOfflineAndOnline();
  await testStdioJsonRpcFlow();
  await testParameterValidation();
  await testMalformedInputResilience();
  await testPortEdgeCasesAndDisconnects();
  await testMockUe5Execution();
  await testConcurrencyAndStress();
  await testDomainSpecificAndViewport();

  console.log('\n' + '='.repeat(70));
  console.log(`TOTAL TESTS: ${totalTests}`);
  console.log(`PASSED:      ${passedTests}`);
  console.log(`FAILED:      ${failedTests}`);
  console.log('='.repeat(70));

  if (failedTests > 0) {
    process.exit(1);
  } else {
    process.exit(0);
  }
}

main().catch((err) => {
  console.error('Fatal error in test harness:', err);
  process.exit(1);
});
