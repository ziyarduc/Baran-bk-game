#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
  type Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { UnrealClient } from './unreal-client.js';

const SERVER_NAME = 'unreal-mcp-server';
const SERVER_VERSION = '1.0.0';

export const TOOLS: Tool[] = [
  {
    name: 'execute_python',
    description:
      'Executes Python code directly inside the Unreal Engine 5 editor via Remote Execution (port 6776) and returns console output, logs, or error traceback.',
    inputSchema: {
      type: 'object',
      properties: {
        code: {
          type: 'string',
          description: 'The Python code string to execute in Unreal Engine 5 editor.',
        },
        unattended: {
          type: 'boolean',
          description: 'Whether to run unattended without modal dialogs. Defaults to true.',
          default: true,
        },
        exec_mode: {
          type: 'string',
          description:
            'Execution mode: "ExecuteFile" (default), "ExecuteStatement", or "EvaluateStatement".',
          enum: ['ExecuteFile', 'ExecuteStatement', 'EvaluateStatement'],
          default: 'ExecuteFile',
        },
        timeout_ms: {
          type: 'number',
          description: 'Execution timeout in milliseconds. Defaults to 10000.',
          default: 10000,
        },
      },
      required: ['code'],
    },
  },
  {
    name: 'spawn_actor',
    description:
      'Spawns an actor in the active Unreal Engine 5 editor world by class or blueprint asset path at the specified 3D vector location (X, Y, Z) and optional rotation (Pitch, Yaw, Roll).',
    inputSchema: {
      type: 'object',
      properties: {
        actor_class: {
          type: 'string',
          description:
            'C++ class path (e.g. "/Script/Engine.StaticMeshActor", "/Script/BakirkoyBR.BRAICharacter") or Blueprint asset path (e.g. "/Game/Blueprints/BP_BotCharacter").',
        },
        location: {
          type: 'object',
          description: 'World location vector (in Unreal units/cm).',
          properties: {
            x: { type: 'number', description: 'X coordinate' },
            y: { type: 'number', description: 'Y coordinate' },
            z: { type: 'number', description: 'Z coordinate' },
          },
          required: ['x', 'y', 'z'],
        },
        rotation: {
          type: 'object',
          description:
            'World rotation in degrees (Pitch, Yaw, Roll). Defaults to (0, 0, 0).',
          properties: {
            pitch: { type: 'number', description: 'Pitch rotation in degrees' },
            yaw: { type: 'number', description: 'Yaw rotation in degrees' },
            roll: { type: 'number', description: 'Roll rotation in degrees' },
          },
        },
      },
      required: ['actor_class', 'location'],
    },
  },
  {
    name: 'capture_viewport',
    description:
      'Captures a high-resolution screenshot from the active Unreal Engine 5 editor viewport and saves it to disk.',
    inputSchema: {
      type: 'object',
      properties: {
        output_path: {
          type: 'string',
          description:
            'Destination file path for the screenshot image (.png). If omitted, saves to Project Saved/Screenshots directory.',
        },
        resolution_x: {
          type: 'number',
          description: 'Screenshot width in pixels. Defaults to 1920.',
          default: 1920,
        },
        resolution_y: {
          type: 'number',
          description: 'Screenshot height in pixels. Defaults to 1080.',
          default: 1080,
        },
      },
    },
  },
  {
    name: 'ping_editor',
    description:
      'Pings the Unreal Engine 5 editor Python Remote Execution endpoint (port 6776) and checks UDP discovery to verify connection, latency, and status.',
    inputSchema: {
      type: 'object',
      properties: {
        host: {
          type: 'string',
          description: 'Host IP address to ping. Defaults to "127.0.0.1".',
          default: '127.0.0.1',
        },
        port: {
          type: 'number',
          description: 'TCP port for Python Remote Execution. Defaults to 6776.',
          default: 6776,
        },
        timeout_ms: {
          type: 'number',
          description: 'Socket timeout in milliseconds. Defaults to 2000.',
          default: 2000,
        },
      },
    },
  },
];

export function createServer(customClient?: UnrealClient): Server {
  const client = customClient ?? new UnrealClient();

  const server = new Server(
    {
      name: SERVER_NAME,
      version: SERVER_VERSION,
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: TOOLS,
    };
  });

  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    try {
      switch (name) {
        case 'execute_python': {
          if (!args || typeof args.code !== 'string') {
            throw new McpError(
              ErrorCode.InvalidParams,
              'Missing required argument "code" (string)'
            );
          }

          const result = await client.executePython(args.code, {
            unattended: typeof args.unattended === 'boolean' ? args.unattended : true,
            execMode: args.exec_mode as any,
            timeoutMs: typeof args.timeout_ms === 'number' ? args.timeout_ms : 10000,
          });

          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2),
              },
            ],
            isError: !result.success,
          };
        }

        case 'spawn_actor': {
          if (!args || typeof args.actor_class !== 'string') {
            throw new McpError(
              ErrorCode.InvalidParams,
              'Missing required argument "actor_class" (string)'
            );
          }
          if (
            !args.location ||
            typeof (args.location as any).x !== 'number' ||
            typeof (args.location as any).y !== 'number' ||
            typeof (args.location as any).z !== 'number'
          ) {
            throw new McpError(
              ErrorCode.InvalidParams,
              'Missing or invalid required argument "location" ({ x, y, z } numbers)'
            );
          }

          const result = await client.spawnActor({
            actor_class: args.actor_class,
            location: args.location as any,
            rotation: args.rotation as any,
          });

          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2),
              },
            ],
            isError: !result.success,
          };
        }

        case 'capture_viewport': {
          const result = await client.captureViewport({
            output_path: typeof args?.output_path === 'string' ? args.output_path : undefined,
            resolution_x: typeof args?.resolution_x === 'number' ? args.resolution_x : 1920,
            resolution_y: typeof args?.resolution_y === 'number' ? args.resolution_y : 1080,
          });

          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2),
              },
            ],
            isError: !result.success,
          };
        }

        case 'ping_editor': {
          const timeoutMs = typeof args?.timeout_ms === 'number' ? args.timeout_ms : 2000;
          const result = await client.pingEditor(timeoutMs);

          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify(result, null, 2),
              },
            ],
            isError: false,
          };
        }

        default:
          throw new McpError(
            ErrorCode.MethodNotFound,
            `Unknown tool: ${name}`
          );
      }
    } catch (err: any) {
      if (err instanceof McpError) {
        throw err;
      }
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(
              {
                success: false,
                error: err.message || String(err),
              },
              null,
              2
            ),
          },
        ],
        isError: true,
      };
    }
  });

  return server;
}

export async function runServer(): Promise<void> {
  const client = new UnrealClient();
  const server = createServer(client);
  const transport = new StdioServerTransport();

  process.on('SIGINT', () => {
    client.stop();
    process.exit(0);
  });
  process.on('SIGTERM', () => {
    client.stop();
    process.exit(0);
  });

  await server.connect(transport);
  console.error(`[${SERVER_NAME}] MCP server running on stdio (v${SERVER_VERSION})`);
}

// Only auto-run if this file is executed directly
if (import.meta.url === `file:///${process.argv[1].replace(/\\/g, '/')}`) {
  runServer().catch((error) => {
    console.error('Fatal error running server:', error);
    process.exit(1);
  });
}
