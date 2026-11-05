#!/usr/bin/env node

import { execFile, spawn } from "node:child_process";
import { promisify } from "node:util";
import { serveAppServer } from "./codex-app-server.mjs";

// A removed subcommand is parsed as a TUI prompt. Inspect the root command list,
// not the exit code of `codex mcp-server --help` (which also succeeds after removal).
try {
  const { stdout } = await promisify(execFile)("codex", ["--help"], {
    timeout: 5000,
    maxBuffer: 256 * 1024,
    windowsHide: true,
  });
  const commands = new Set();
  let inCommands = false;
  for (const line of stdout.split(/\r?\n/u)) {
    if (line === "Commands:") inCommands = true;
    else if (/^\S/u.test(line)) inCommands = false;
    if (inCommands) {
      const match = /^ {2}([a-z][a-z0-9-]*)(?: {2,}|\t)/u.exec(line);
      if (match) commands.add(match[1]);
    }
  }
  if (commands.has("mcp-server")) startLegacyServer();
  else if (commands.has("app-server")) serveAppServer();
  else throw new Error("Codex exposes neither mcp-server nor app-server; check `codex --help`.");
} catch (error) {
  process.stderr.write(`codex proxy error: ${error.message}\n`);
  process.exitCode = 1;
}

function startLegacyServer() {
  const child = spawn("codex", ["mcp-server"], {
    stdio: ["pipe", "pipe", "inherit"],
  });
  let finished = false;
  function finish(code, signal) {
    if (finished) return;
    finished = true;
    process.stdin.unpipe(child.stdin);
    process.stdin.pause();
    child.stdin.destroy();
    if (signal) process.kill(process.pid, signal);
    else process.exitCode = code ?? 1;
  }
  // Keep the legacy MCP protocol and parameters byte-for-byte unchanged.
  process.stdin.pipe(child.stdin);
  child.stdout.pipe(process.stdout);
  child.stdin.on("error", (error) => {
    if (error.code === "EPIPE") return;
    process.stderr.write(`codex proxy input error: ${error.message}\n`);
    child.kill();
    finish(1);
  });
  child.on("error", (error) => {
    process.stderr.write(`codex proxy error: ${error.message}\n`);
    finish(1);
  });
  child.on("close", finish);
}
