export interface MiniAppContext {
  pluginId: string;
  pluginRoot: string;
  dataDir: string;
  listen: { host: string; port: number };
  signal: AbortSignal;
  logger: { info?: (code: string, fields?: Record<string, unknown>) => void; error?: (code: string, fields?: Record<string, unknown>) => void };
  hostConnector?: unknown;
}
export interface MiniAppLifecycle { dispose: () => Promise<void> | void }
export interface MiniAppModule { start: (context: MiniAppContext) => Promise<MiniAppLifecycle> }
