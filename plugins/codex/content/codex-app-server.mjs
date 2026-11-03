import { spawn } from "node:child_process";
import { createInterface } from "node:readline";

// A separate guard holds the Job handle. Attach the supervisor before it spawns
// Codex, so even descendants of an exited npm wrapper remain owned by this call.
// No breakaway flags or policy bypasses: assignment/PowerShell failures stop launch.
const windowsJobGuard = String.raw`
$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
public static class CodexJob {
  [StructLayout(LayoutKind.Sequential)] public struct Basic {
    public long ProcessTime, JobTime;
    public uint Flags;
    public UIntPtr MinWorkingSet, MaxWorkingSet;
    public uint ActiveProcessLimit;
    public UIntPtr Affinity;
    public uint PriorityClass, SchedulingClass;
  }
  [StructLayout(LayoutKind.Sequential)] public struct Io {
    public ulong ReadOps, WriteOps, OtherOps, ReadBytes, WriteBytes, OtherBytes;
  }
  [StructLayout(LayoutKind.Sequential)] public struct Limits {
    public Basic Basic;
    public Io Io;
    public UIntPtr ProcessMemory, JobMemory, PeakProcessMemory, PeakJobMemory;
  }
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
  static extern IntPtr CreateJobObject(IntPtr attributes, string name);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern bool SetInformationJobObject(IntPtr job, int kind, ref Limits limits, uint size);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);
  [DllImport("kernel32.dll", SetLastError=true)]
  static extern IntPtr OpenProcess(uint access, bool inherit, uint pid);
  [DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr handle);
  public static IntPtr Attach(uint pid) {
    IntPtr job = CreateJobObject(IntPtr.Zero, null);
    if (job == IntPtr.Zero) throw new Win32Exception();
    try {
      Limits limits = new Limits();
      limits.Basic.Flags = 0x2000; // JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
      if (!SetInformationJobObject(job, 9, ref limits, (uint)Marshal.SizeOf(typeof(Limits)))) throw new Win32Exception();
      IntPtr process = OpenProcess(0x0101, false, pid); // SET_QUOTA | TERMINATE
      if (process == IntPtr.Zero) throw new Win32Exception();
      try {
        if (!AssignProcessToJobObject(job, process)) throw new Win32Exception();
      } finally { CloseHandle(process); }
      return job;
    } catch { CloseHandle(job); throw; }
  }
}
'@
$job = [CodexJob]::Attach(__SUPERVISOR_PID__)
try {
  [Console]::Out.WriteLine('ready')
  [Console]::Out.Flush()
  [Console]::In.ReadToEnd() | Out-Null
} finally { [CodexJob]::CloseHandle($job) | Out-Null }
`;

const windowsSupervisor = String.raw`
  const { spawn } = require("node:child_process");
  const { join } = require("node:path");
  const { createInterface } = require("node:readline");
  const report = (error) => {
    if (process.connected) process.send({ error: error.message }, () => {});
  };
  const script = process.argv[1].replace("__SUPERVISOR_PID__", String(process.pid));
  const guard = spawn(join(process.env.SystemRoot, "System32", "WindowsPowerShell", "v1.0", "powershell.exe"), [
    "-NoLogo", "-NoProfile", "-NonInteractive", "-EncodedCommand", Buffer.from(script, "utf16le").toString("base64"),
  ], { stdio: ["pipe", "pipe", "inherit"], windowsHide: true });
  let stopping = false;
  const stop = () => { stopping = true; guard.stdin.end(); };
  guard.stdin.on("error", report);
  guard.on("error", (error) => { report(error); process.exitCode = 1; if (process.connected) process.disconnect(); });
  guard.on("exit", () => process.exit(1));
  process.once("disconnect", stop);
  process.on("message", (message) => { if (message?.method === "stop") stop(); });
  const lines = createInterface({ input: guard.stdout });
  let started = false;
  lines.on("line", (line) => {
    if (line !== "ready" || started || stopping) return;
    started = true;
    const child = spawn("codex", ["app-server"], {
      stdio: ["pipe", "inherit", "inherit"], windowsHide: true,
    });
    process.stdin.pipe(child.stdin);
    child.stdin.on("error", report);
    child.on("error", (error) => { report(error); stop(); });
    // Closing the Job kills the tree; owner waits for stdout to drain via close.
    child.on("exit", stop);
  });
`;

async function waitForClose(closed, milliseconds) {
  let timer;
  try {
    return await Promise.race([closed.then(() => true), new Promise((resolve) => { timer = setTimeout(() => resolve(false), milliseconds); })]);
  } finally {
    clearTimeout(timer);
  }
}

const outputSchema = {
  type: "object",
  properties: { threadId: { type: "string" }, content: { type: "string" } },
  required: ["threadId", "content"],
};
const tools = [
  {
    name: "codex",
    title: "Codex",
    description: "Run a Codex task using local configuration. Defaults to read-only and no interactive approvals. Requests requiring approval stop with an error.",
    inputSchema: {
      type: "object",
      additionalProperties: false,
      properties: {
        prompt: { type: "string", description: "The initial user prompt." },
        model: { type: "string", description: "Explicit model override; omit to use local configuration." },
        cwd: { type: "string", description: "Working directory, relative to the server cwd if not absolute." },
        sandbox: { type: "string", enum: ["read-only", "workspace-write", "danger-full-access"] },
        "approval-policy": { type: "string", enum: ["on-request", "never"] },
        "base-instructions": { type: "string" },
        "developer-instructions": { type: "string" },
        "compact-prompt": { type: "string" },
        config: { type: "object", additionalProperties: true },
      },
      required: ["prompt"],
    },
    outputSchema,
  },
  {
    name: "codex-reply",
    title: "Codex Reply",
    description: "Continue a Codex thread using its saved configuration and an incremental prompt.",
    inputSchema: {
      type: "object",
      additionalProperties: false,
      properties: {
        prompt: { type: "string" },
        threadId: { type: "string", description: "Thread identifier returned by codex." },
        conversationId: { type: "string", description: "Deprecated alias for threadId." },
      },
      required: ["prompt"],
    },
    outputSchema,
  },
];

function validateCall(name, args) {
  const tool = tools.find((entry) => entry.name === name);
  if (!tool) throw new Error(`Unknown Codex tool: ${name}`);
  if (!args || typeof args !== "object" || Array.isArray(args)) throw new Error("arguments must be an object");
  for (const [key, value] of Object.entries(args)) {
    const property = tool.inputSchema.properties[key];
    if (!property || typeof value !== property.type || value === null || Array.isArray(value)) {
      throw new Error(`Invalid argument: ${key}`);
    }
    if (property.enum && !property.enum.includes(value)) throw new Error(`Unsupported ${key}`);
  }
  if (!args.prompt?.trim()) throw new Error("prompt must be a non-empty string");
  if (name === "codex-reply") {
    if (!(args.threadId ?? args.conversationId)?.trim()) throw new Error("threadId is required");
    if (args.threadId && args.conversationId && args.threadId !== args.conversationId) {
      throw new Error("threadId and conversationId must identify the same thread");
    }
  }
}

// Each invocation owns a stdio app-server. Persisted threads provide continuity;
// a failed/cancelled invocation never retries a prompt or affects another process.
class AppServerCall {
  constructor(signal, threadSettings) {
    this.threadSettings = threadSettings;
    this.sequence = 0;
    this.pending = new Map();
    this.messages = new Map();
    this.completed = new Map();
    this.outputBytes = 0;
    const windows = process.platform === "win32";
    this.child = spawn(windows ? process.execPath : "codex", windows ? ["-e", windowsSupervisor, windowsJobGuard] : ["app-server"], {
      stdio: windows ? ["pipe", "pipe", "inherit", "ipc"] : ["pipe", "pipe", "inherit"],
      // Own a process group so npm's wrapper and its native child stop together.
      detached: !windows,
      windowsHide: true,
    });
    if (windows) this.child.on("message", (message) => {
      if (message?.error) this.fail(new Error(message.error));
    });
    this.closed = new Promise((resolve) => this.child.once("close", resolve));
    this.turnDone = new Promise((resolve, reject) => {
      this.resolveTurn = resolve;
      this.rejectTurn = reject;
    });
    this.turnDone.catch(() => {});
    this.lines = createInterface({ input: this.child.stdout, crlfDelay: Infinity });
    this.lines.on("line", (line) => {
      try { this.receive(JSON.parse(line)); }
      catch (error) { this.fail(error); }
    });
    this.child.on("error", (error) => this.fail(error));
    this.child.on("close", (code, childSignal) => {
      if (!this.closing) this.fail(new Error(`Codex app-server exited (${childSignal ?? code}) before completing the request`));
    });
    this.child.stdin.on("error", (error) => this.fail(error));
    this.abort = () => this.fail(new Error("Codex request cancelled"));
    this.signal = signal;
    signal.addEventListener("abort", this.abort, { once: true });
    if (signal.aborted) this.abort();
    this.deadline = setTimeout(() => this.fail(new Error("Codex request timed out")), 14 * 60 * 1000);
  }

  write(message) {
    if (this.child.stdin.destroyed) throw new Error("Codex app-server input is closed");
    this.child.stdin.write(JSON.stringify(message) + "\n");
  }

  request(method, params) {
    if (this.failure) return Promise.reject(this.failure);
    const id = ++this.sequence;
    if (method === "turn/start") this.turnStartRequestId = id;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => this.fail(new Error(`Codex ${method} timed out`)), 30000);
      this.pending.set(id, { resolve, reject, timer });
      try { this.write({ id, method, params }); }
      catch (error) { this.fail(error); }
    });
  }

  fail(error) {
    if (this.failure || this.closing) return;
    this.failure = error;
    for (const entry of this.pending.values()) {
      clearTimeout(entry.timer);
      entry.reject(error);
    }
    this.pending.clear();
    this.rejectTurn(error);
  }

  receive(message) {
    if (!message || typeof message !== "object" || Array.isArray(message)) throw new Error("Invalid Codex app-server message");
    if (message.method && message.id !== undefined) {
      // This adapter has no interactive approval UI. Never synthesize consent,
      // answer a user question, or allow an auto-reviewer to approve on our behalf.
      this.write({ id: message.id, error: { code: -32601, message: "Interactive requests are not supported by this Codex MCP adapter." } });
      this.fail(new Error(`Codex requires interactive approval or input (${message.method}); no approval was granted. Continue in Codex interactively.`));
      return;
    }
    if (message.id !== undefined) {
      if (message.id === this.turnStartRequestId && typeof message.result?.turn?.id === "string") {
        this.turnId = message.result.turn.id;
        if (this.failure || this.closing) this.interrupt();
      }
      const entry = this.pending.get(message.id);
      if (!entry) return;
      this.pending.delete(message.id);
      clearTimeout(entry.timer);
      if (message.error) entry.reject(new Error(message.error.message ?? "Codex app-server request failed"));
      else if (Object.hasOwn(message, "result")) entry.resolve(message.result);
      else entry.reject(new Error("Codex app-server response has no result"));
      return;
    }
    const params = message.params;
    if (!this.threadId || params?.threadId !== this.threadId) return;
    if (message.method === "turn/started" && this.turnStartRequestId !== undefined && typeof params.turn?.id === "string") {
      this.turnId = params.turn.id;
      if (this.failure || this.closing) this.interrupt();
    } else if (message.method === "item/completed" && params.item?.type === "agentMessage") {
      if (typeof params.item.text !== "string") throw new Error("Invalid Codex agent message");
      this.outputBytes += Buffer.byteLength(params.item.text);
      if (this.outputBytes > 16 * 1024 * 1024) throw new Error("Codex response exceeds 16 MiB");
      this.messages.set(params.item.id, { ...params.item, turnId: params.turnId });
    } else if (message.method === "turn/completed") {
      if (typeof params.turn?.id !== "string") throw new Error("Invalid Codex completed turn");
      this.completed.set(params.turn.id, params.turn);
      this.finishTurn();
    }
  }

  finishTurn() {
    const turn = this.completed.get(this.turnId);
    if (!turn) return;
    if (turn.status !== "completed") {
      this.rejectTurn(new Error(turn.error?.message ?? `Codex turn ${turn.status}`));
      return;
    }
    const messages = [...this.messages.values()].filter((item) => item.turnId === this.turnId);
    // Final turn payloads may omit items; item/completed is the streaming source.
    for (const item of turn.items ?? []) {
      if (item.type === "agentMessage" && !messages.some((entry) => entry.id === item.id)) messages.push(item);
    }
    const final = messages.filter((item) => item.phase === "final_answer");
    const content = (final.length ? final : messages).map((item) => item.text).join("\n\n");
    if (!content) this.rejectTurn(new Error("Codex completed without a text response"));
    else this.resolveTurn({ threadId: this.threadId, content });
  }

  async run(name, args) {
    try {
      await this.request("initialize", {
        clientInfo: { name: "minimax-codex-mcp", version: "0.2.8" },
        capabilities: { experimentalApi: false },
      });
      this.write({ method: "initialized" });
      const params = { approvalsReviewer: "user" };
      const sandboxModes = { readOnly: "read-only", workspaceWrite: "workspace-write", dangerFullAccess: "danger-full-access" };
      let safety;
      if (name === "codex-reply") {
        const threadId = args.threadId ?? args.conversationId;
        const saved = this.threadSettings.get(threadId);
        Object.assign(params, saved?.overrides ?? {}, { threadId });
        // Codex resume can fall back to config.toml's sandbox instead of the
        // thread's original sandbox. Never inherit a wider local default.
        safety = saved ?? {
          sandbox: { type: "readOnly", networkAccess: false }, approvalPolicy: "never",
        };
        params.sandbox = sandboxModes[safety.sandbox.type];
        params.approvalPolicy = safety.approvalPolicy;
      } else {
        params.sandbox = args.sandbox ?? "read-only";
        params.approvalPolicy = args["approval-policy"] ?? "never";
        for (const [from, to] of Object.entries({
          model: "model", cwd: "cwd", config: "config",
          "base-instructions": "baseInstructions", "developer-instructions": "developerInstructions",
        })) {
          if (Object.hasOwn(args, from)) params[to] = args[from];
        }
        if (Object.hasOwn(args, "compact-prompt")) {
          params.config = { ...params.config, compact_prompt: args["compact-prompt"] };
        }
      }
      const thread = await this.request(name === "codex" ? "thread/start" : "thread/resume", params);
      if (typeof thread?.thread?.id !== "string") throw new Error("Codex did not return a thread id");
      this.threadId = thread.thread.id;
      safety ??= { sandbox: thread.sandbox, approvalPolicy: thread.approvalPolicy, overrides: { ...params } };
      if (!sandboxModes[safety.sandbox?.type] || !safety.approvalPolicy) {
        throw new Error("Codex did not return a supported permission policy");
      }
      this.threadSettings.set(this.threadId, safety);
      const result = await this.request("turn/start", {
        threadId: this.threadId,
        sandboxPolicy: safety.sandbox,
        approvalPolicy: safety.approvalPolicy,
        approvalsReviewer: "user",
        input: [{ type: "text", text: args.prompt }],
      });
      if (typeof result?.turn?.id !== "string") throw new Error("Codex did not return a turn id");
      this.turnId = result.turn.id;
      this.finishTurn(); // Completion may arrive before the turn/start response.
      return await this.turnDone;
    } catch (error) {
      this.fail(error);
      throw error;
    } finally {
      await this.close();
    }
  }

  interrupt() {
    if (!this.threadId || !this.turnId || this.interruptedTurnId === this.turnId || this.completed.has(this.turnId)) return;
    this.interruptedTurnId = this.turnId;
    try { this.write({ id: ++this.sequence, method: "turn/interrupt", params: { threadId: this.threadId, turnId: this.turnId } }); }
    catch { /* The process may have already exited. */ }
  }

  async killTree(signal) {
    if (!this.child.pid) return;
    try {
      if (process.platform === "win32") {
        if (signal === "SIGKILL") this.child.kill("SIGKILL");
        else if (this.child.connected) this.child.send({ method: "stop" }, (error) => { if (error) this.shutdownError = error; });
      } else {
        process.kill(-this.child.pid, signal);
      }
    } catch (error) {
      if (error.code !== "ESRCH") this.shutdownError = error;
    }
  }

  async close() {
    clearTimeout(this.deadline);
    this.signal.removeEventListener("abort", this.abort);
    this.closing = true;
    for (const entry of this.pending.values()) {
      clearTimeout(entry.timer);
      entry.reject(new Error("Codex app-server closed"));
    }
    this.pending.clear();
    this.interrupt();
    if (this.failure) {
      // A turn may already be running before turn/start replies. Do not give an
      // unidentified operation the successful-completion flush grace period.
      if (this.turnId) await waitForClose(this.closed, 150);
      await this.killTree("SIGTERM");
    }
    if (!this.child.stdin.destroyed) this.child.stdin.end();
    let closed = await waitForClose(this.closed, this.failure ? 500 : 2000);
    if (!closed) {
      await this.killTree("SIGTERM");
      closed = await waitForClose(this.closed, 500);
    }
    if (!closed) {
      await this.killTree("SIGKILL");
      closed = await waitForClose(this.closed, 1000);
    }
    // close can wait forever when a descendant holds a pipe after the wrapper
    // exits. Always release local handles after the bounded shutdown attempts.
    this.lines.close();
    this.child.stdin.destroy();
    this.child.stdout.destroy();
    if (!closed) {
      if (this.child.connected) this.child.disconnect();
      this.child.unref();
      throw new Error(`Codex process tree did not close after bounded shutdown${this.shutdownError ? "; process termination failed" : ""}; inspect the workspace before retrying.`);
    }
  }
}

export function serveAppServer() {
  const input = createInterface({ input: process.stdin, crlfDelay: Infinity });
  const jobs = new Map();
  const busyThreads = new Set();
  const threadSettings = new Map();
  let initialized = false;
  let closed = false;
  const send = (message) => { if (!closed) process.stdout.write(JSON.stringify({ jsonrpc: "2.0", ...message }) + "\n"); };
  const stop = () => {
    closed = true;
    for (const controller of jobs.values()) controller.abort();
    input.close();
    process.stdin.pause();
  };
  input.on("close", stop);
  process.once("SIGTERM", stop);
  process.once("SIGINT", stop);
  process.stdout.on("error", stop);
  input.on("line", async (line) => {
    let message;
    try { message = JSON.parse(line); }
    catch { send({ id: null, error: { code: -32700, message: "Invalid JSON" } }); return; }
    if (!message || typeof message !== "object" || Array.isArray(message) || message.jsonrpc !== "2.0" || typeof message.method !== "string") {
      send({ id: null, error: { code: -32600, message: "Invalid MCP request" } });
      return;
    }
    const { id, method, params } = message;
    if (id === undefined) {
      if (method === "notifications/cancelled") jobs.get(params?.requestId)?.abort();
      return;
    }
    if (typeof id !== "string" && typeof id !== "number") {
      send({ id: null, error: { code: -32600, message: "Invalid request id" } });
      return;
    }
    if (method === "initialize") {
      if (initialized) { send({ id, error: { code: -32600, message: "Already initialized" } }); return; }
      initialized = true;
      const versions = ["2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"];
      send({ id, result: {
        protocolVersion: versions.includes(params?.protocolVersion) ? params.protocolVersion : "2024-11-05",
        capabilities: { tools: {} },
        serverInfo: { name: "minimax-codex-app-server", version: "0.2.8" },
      } });
    } else if (method === "ping") send({ id, result: {} });
    else if (!initialized) send({ id, error: { code: -32600, message: "Initialize first" } });
    else if (method === "tools/list") send({ id, result: { tools } });
    else if (method === "tools/call") {
      if (jobs.has(id)) { send({ id, error: { code: -32600, message: "Duplicate active request id" } }); return; }
      const controller = new AbortController();
      let threadId;
      jobs.set(id, controller);
      try {
        validateCall(params?.name, params?.arguments);
        const args = params.arguments;
        if (params.name === "codex-reply") {
          const requestedId = args.threadId ?? args.conversationId;
          if (busyThreads.has(requestedId)) throw new Error("This Codex thread already has an active request");
          threadId = requestedId;
          busyThreads.add(threadId);
        }
        const result = await new AppServerCall(controller.signal, threadSettings).run(params.name, args);
        send({ id, result: { content: [{ type: "text", text: result.content }], structuredContent: result, isError: false } });
      } catch (error) {
        send({ id, result: { content: [{ type: "text", text: error.message }], isError: true } });
      } finally {
        jobs.delete(id);
        if (threadId) busyThreads.delete(threadId);
      }
    } else send({ id, error: { code: -32601, message: `Unsupported MCP method: ${method}` } });
  });
}
