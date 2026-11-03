// @ts-check
// Minimal Streamable HTTP MCP dispatcher for the Mini App Node runtime.
// Supports: initialize, notifications/*, ping, tools/list, tools/call.
// Stateless (no session ids); single messages and batches; notifications get no reply.

const PROTOCOL_VERSION = '2025-03-26';

/**
 * @param {{ serverInfo: { name: string, version: string },
 *           tools: Array<{ name: string, description: string, inputSchema: object,
 *                          handler: (args: any) => Promise<any> | any }> }} options
 */
export function createMcpDispatcher({ serverInfo, tools }) {
  const toolIndex = new Map(tools.map((tool) => [tool.name, tool]));

  async function dispatchOne(message) {
    if (!isRecord(message) || message.jsonrpc !== '2.0' || typeof message.method !== 'string') {
      return errorResponse(isRecord(message) ? message.id ?? null : null, -32600, 'invalid request');
    }
    const { id, method, params } = message;
    const isNotification = id === undefined || id === null;
    if (method.startsWith('notifications/')) return null;
    try {
      if (method === 'initialize') {
        return result(id, {
          protocolVersion: typeof params?.protocolVersion === 'string' ? params.protocolVersion : PROTOCOL_VERSION,
          capabilities: { tools: {} },
          serverInfo,
        });
      }
      if (method === 'ping') return result(id, {});
      if (method === 'tools/list') {
        return result(id, {
          tools: tools.map(({ name, description, inputSchema }) => ({ name, description, inputSchema })),
        });
      }
      if (method === 'tools/call') {
        const tool = toolIndex.get(String(params?.name ?? ''));
        if (!tool) return errorResponse(id, -32602, `unknown tool: ${String(params?.name)}`);
        try {
          const value = await tool.handler(isRecord(params?.arguments) ? params.arguments : {});
          return result(id, { content: [{ type: 'text', text: JSON.stringify(value, null, 2) }] });
        } catch (error) {
          return result(id, {
            content: [{ type: 'text', text: JSON.stringify({ error: error?.code ?? 'TOOL_FAILED', message: String(error?.message ?? error) }) }],
            isError: true,
          });
        }
      }
      return isNotification ? null : errorResponse(id, -32601, `method not found: ${method}`);
    } catch (error) {
      return isNotification ? null : errorResponse(id, -32603, String(error?.message ?? error));
    }
  }

  /**
   * Dispatch a parsed POST body. Returns { payload } where payload === null means
   * "no response body" (respond 202 Accepted).
   */
  return async function dispatch(body) {
    if (Array.isArray(body)) {
      const responses = (await Promise.all(body.map(dispatchOne))).filter((entry) => entry !== null);
      return { payload: responses.length > 0 ? responses : null };
    }
    return { payload: await dispatchOne(body) };
  };
}

function result(id, value) {
  return { jsonrpc: '2.0', id: id ?? null, result: value };
}

function errorResponse(id, code, message) {
  return { jsonrpc: '2.0', id: id ?? null, error: { code, message } };
}

function isRecord(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
