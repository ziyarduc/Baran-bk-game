import { spawn } from 'node:child_process';
import * as path from 'node:path';
import * as net from 'node:net';

const MCP_PATH = path.resolve('mcp-servers/unrealengine/build/index.js');

async function testStdioMcpServer() {
  console.log('--- Testing MCP stdio process directly ---');
  const child = spawn('node', [MCP_PATH], {
    stdio: ['pipe', 'pipe', 'pipe'],
  });

  let msgId = 1;
  const pendingRequests = new Map();
  let buffer = '';

  child.stderr.on('data', (data) => {
    console.log('[STDERR]', data.toString().trim());
  });

  child.stdout.on('data', (chunk) => {
    buffer += chunk.toString('utf-8');
    const lines = buffer.split('\n');
    buffer = lines.pop(); // Keep last incomplete line

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const json = JSON.parse(line.trim());
        if (json.id && pendingRequests.has(json.id)) {
          const resolve = pendingRequests.get(json.id);
          pendingRequests.delete(json.id);
          resolve(json);
        }
      } catch (err) {
        console.error('Failed to parse stdout line:', line, err);
      }
    }
  });

  function sendRequest(method, params = {}) {
    const id = msgId++;
    const payload = JSON.stringify({
      jsonrpc: '2.0',
      id,
      method,
      params,
    }) + '\n';

    return new Promise((resolve, reject) => {
      pendingRequests.set(id, resolve);
      child.stdin.write(payload);
    });
  }

  function sendNotification(method, params = {}) {
    const payload = JSON.stringify({
      jsonrpc: '2.0',
      method,
      params,
    }) + '\n';
    child.stdin.write(payload);
  }

  // 1. Initialize
  const initRes = await sendRequest('initialize', {
    protocolVersion: '2024-11-05',
    capabilities: {},
    clientInfo: { name: 'reviewer-test', version: '1.0.0' },
  });
  console.log('[INIT RESULT]', initRes.result.serverInfo);

  // 2. Initialized Notification
  sendNotification('notifications/initialized');

  // 3. List Tools
  const listRes = await sendRequest('tools/list');
  const tools = listRes.result.tools;
  console.log('[TOOLS LIST]', tools.map((t) => t.name));

  const toolNames = tools.map((t) => t.name);
  const expected = ['execute_python', 'spawn_actor', 'capture_viewport', 'ping_editor'];
  const allFound = expected.every((name) => toolNames.includes(name));
  console.log('[TOOLS CHECK]', allFound ? 'PASS - All 4 tools present' : 'FAIL - Missing tools');

  // 4. Call ping_editor (Offline state)
  const pingRes = await sendRequest('tools/call', {
    name: 'ping_editor',
    arguments: { timeout_ms: 500 },
  });
  console.log('[PING_EDITOR OFFLINE RESULT]', JSON.parse(pingRes.result.content[0].text));

  // 5. Call execute_python (Offline state)
  const execRes = await sendRequest('tools/call', {
    name: 'execute_python',
    arguments: { code: 'print("hello")' },
  });
  console.log('[EXECUTE_PYTHON OFFLINE RESULT]', JSON.parse(execRes.result.content[0].text));

  // 6. Test invalid arguments handling (e.g. missing required code)
  const invalidRes = await sendRequest('tools/call', {
    name: 'execute_python',
    arguments: {},
  });
  console.log('[INVALID ARGS RESULT]', invalidRes);

  child.kill();
  console.log('--- Stdio process test complete ---\n');
}

import { pathToFileURL } from 'node:url';

async function testWithSimulatedUe5Server() {
  console.log('--- Testing with Simulated UE5 TCP Server on 127.0.0.1:6776 ---');

  // Create dummy TCP server on 6776
  const server = net.createServer((socket) => {
    socket.on('data', (data) => {
      const str = data.toString('utf-8');
      console.log('[SIMULATED UE5 RECEIVED]', str.substring(0, 80) + '...');
      try {
        const req = JSON.parse(str);
        if (req.magic === 'ue_py' && req.type === 'command') {
          // Respond with UE5 remote execution JSON
          const resp = JSON.stringify({
            version: 1,
            magic: 'ue_py',
            type: 'command_output',
            data: {
              success: true,
              output: [{ output: 'Simulated UE5 Python Execution OK' }],
              result: 'Success',
            },
          });
          socket.write(resp);
        }
      } catch (e) {
        console.error('[SIMULATED UE5 ERROR]', e);
      }
    });
  });

  await new Promise((resolve) => server.listen(6776, '127.0.0.1', resolve));
  console.log('[SIMULATED UE5] Listening on 127.0.0.1:6776');

  // Import UnrealClient directly
  const clientUrl = pathToFileURL(path.resolve('mcp-servers/unrealengine/build/unreal-client.js')).href;
  const { UnrealClient } = await import(clientUrl);
  const client = new UnrealClient('127.0.0.1', 6776);

  const ping = await client.pingEditor(1000);
  console.log('[SIMULATED PING]', ping);

  const exec = await client.executePython('unreal.log("test")', { timeoutMs: 2000 });
  console.log('[SIMULATED EXECUTE PYTHON]', exec);

  const spawn = await client.spawnActor({
    actor_class: '/Script/Engine.StaticMeshActor',
    location: { x: 100, y: 200, z: 300 },
  });
  console.log('[SIMULATED SPAWN ACTOR]', spawn);

  client.stop();
  await new Promise((resolve) => server.close(resolve));
  console.log('[SIMULATED UE5] Server closed.');
}

async function run() {
  await testStdioMcpServer();
  await testWithSimulatedUe5Server();
}

run().catch((e) => {
  console.error('FATAL TEST ERROR:', e);
  process.exit(1);
});
