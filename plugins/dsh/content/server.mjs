#!/usr/bin/env node

import { spawn, spawnSync } from 'node:child_process';
import { closeSync, existsSync, mkdirSync, openSync, readFileSync, renameSync, rmSync, writeFileSync } from 'node:fs';
import http from 'node:http';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import readline from 'node:readline';

const SERVER_NAME = 'dsh';
const SERVER_VERSION = '0.1.0';
const DSH_VERSION = '0.1.0-rc.8';
const DSH_PACKAGE = `@deepseek-ai/dsh@${DSH_VERSION}`;
const LOOPBACK_HOST = '127.0.0.1';

const activeDataDir =
  process.env.MINIMAX_DATA_DIR || process.env.MAVIS_DATA_DIR || path.join(os.homedir(), '.minimax');
const pluginData = path.resolve(
  process.env.PLUGIN_DATA ||
    path.join(activeDataDir, 'v2', 'plugin-data', 'local-minimax', SERVER_NAME),
);
const runtimeDir = path.join(pluginData, 'runtime');
const dshHome = path.join(pluginData, 'dsh-home');
const stateDir = path.join(pluginData, 'state');
const logDir = path.join(pluginData, 'logs');
const installStatePath = path.join(stateDir, 'install.json');
const harnessStatePath = path.join(stateDir, 'harness.json');
const installLogPath = path.join(logDir, 'install.log');
const harnessLogPath = path.join(logDir, 'harness.log');
const dshBinPath = path.join(runtimeDir, 'node_modules', '@deepseek-ai', 'dsh', 'lib', 'bin.js');

const tools = [
  {
    name: 'deepseek_harness_status',
    description: '检查 DeepSeek Harness 的安装状态、运行状态和本地 URL。',
    inputSchema: { type: 'object', additionalProperties: false, properties: {} },
  },
  {
    name: 'deepseek_harness_install',
    description:
      `下载并安装 ${DSH_PACKAGE} 到本 Plugin 的隔离数据目录。调用前必须获得用户明确同意。`,
    inputSchema: { type: 'object', additionalProperties: false, properties: {} },
  },
  {
    name: 'deepseek_harness_start',
    description: '在 127.0.0.1 的随机空闲端口启动已安装的 DeepSeek Harness Web。',
    inputSchema: { type: 'object', additionalProperties: false, properties: {} },
  },
  {
    name: 'deepseek_harness_stop',
    description: '停止由本 Plugin 启动的 DeepSeek Harness Web 进程。',
    inputSchema: { type: 'object', additionalProperties: false, properties: {} },
  },
  {
    name: 'deepseek_harness_logs',
    description: '读取 DeepSeek Harness 或安装任务的末尾日志，用于排障。',
    inputSchema: {
      type: 'object',
      additionalProperties: false,
      properties: {
        kind: { type: 'string', enum: ['harness', 'install'], default: 'harness' },
        lines: { type: 'integer', minimum: 1, maximum: 200, default: 80 },
      },
    },
  },
];

function ensureDataDirs() {
  for (const directory of [pluginData, runtimeDir, dshHome, stateDir, logDir]) {
    mkdirSync(directory, { recursive: true });
  }
}

function readJson(filePath) {
  try {
    const value = JSON.parse(readFileSync(filePath, 'utf8'));
    return value && typeof value === 'object' && !Array.isArray(value) ? value : null;
  } catch {
    return null;
  }
}

function writeJsonAtomic(filePath, value) {
  const tempPath = `${filePath}.${process.pid}.tmp`;
  writeFileSync(tempPath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
  renameSync(tempPath, filePath);
}

function removeFile(filePath) {
  rmSync(filePath, { force: true });
}

function isPositivePid(value) {
  return Number.isInteger(value) && value > 1 && value !== process.pid && value !== process.ppid;
}

function isProcessAlive(pid) {
  if (!isPositivePid(pid)) return false;
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
}

function hasCommand(command) {
  const result = spawnSync(command, ['--version'], {
    shell: process.platform === 'win32',
    stdio: 'ignore',
    windowsHide: true,
  });
  return result.status === 0;
}

function selectPackageManager() {
  if (hasCommand('pnpm')) return { command: 'pnpm', name: 'pnpm' };
  if (hasCommand('npm')) return { command: 'npm', name: 'npm' };
  return null;
}

function appendMarker(filePath, text) {
  writeFileSync(filePath, `\n[${new Date().toISOString()}] ${text}\n`, { encoding: 'utf8', flag: 'a' });
}

function spawnDetached(command, args, logPath, options = {}) {
  appendMarker(logPath, `${command} ${args.join(' ')}`);
  const logFd = openSync(logPath, 'a');
  try {
    const child = spawn(command, args, {
      cwd: options.cwd || pluginData,
      env: options.env || process.env,
      detached: true,
      shell: options.shell ?? false,
      stdio: ['ignore', logFd, logFd],
      windowsHide: true,
    });
    if (!isPositivePid(child.pid)) throw new Error(`未能启动 ${command}`);
    child.unref();
    return child.pid;
  } finally {
    closeSync(logFd);
  }
}

function tailLog(filePath, lineCount = 80) {
  try {
    const lines = readFileSync(filePath, 'utf8').split(/\r?\n/u);
    return lines.slice(-lineCount).join('\n').trim();
  } catch {
    return '';
  }
}

function requestHealth(url, timeoutMs = 1500) {
  return new Promise((resolve) => {
    let settled = false;
    const finish = (value) => {
      if (settled) return;
      settled = true;
      resolve(value);
    };
    const request = http.get(url, { timeout: timeoutMs }, (response) => {
      response.resume();
      finish(Boolean(response.statusCode && response.statusCode >= 200 && response.statusCode < 500));
    });
    request.on('timeout', () => {
      request.destroy();
      finish(false);
    });
    request.on('error', () => finish(false));
  });
}

async function waitForHealth(url, pid, timeoutMs = 45_000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (!isProcessAlive(pid)) return false;
    if (await requestHealth(url)) return true;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  return false;
}

function reservePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.once('error', reject);
    server.listen(0, LOOPBACK_HOST, () => {
      const address = server.address();
      const port = address && typeof address === 'object' ? address.port : 0;
      server.close((error) => {
        if (error) reject(error);
        else if (!port) reject(new Error('未能分配本地端口'));
        else resolve(port);
      });
    });
  });
}

async function waitForProcessExit(pid, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (!isProcessAlive(pid)) return true;
    await new Promise((resolve) => setTimeout(resolve, 150));
  }
  return !isProcessAlive(pid);
}

async function stopProcessTree(pid) {
  if (!isProcessAlive(pid)) return;
  if (process.platform === 'win32') {
    await new Promise((resolve) => {
      const child = spawn('taskkill', ['/PID', String(pid), '/T', '/F'], {
        shell: false,
        stdio: 'ignore',
        windowsHide: true,
      });
      child.once('error', () => resolve());
      child.once('exit', () => resolve());
    });
    return;
  }

  try {
    process.kill(-pid, 'SIGTERM');
  } catch {
    try {
      process.kill(pid, 'SIGTERM');
    } catch {
      return;
    }
  }
  if (await waitForProcessExit(pid, 5_000)) return;
  try {
    process.kill(-pid, 'SIGKILL');
  } catch {
    try {
      process.kill(pid, 'SIGKILL');
    } catch {
      return;
    }
  }
}

function installSnapshot() {
  const state = readJson(installStatePath);
  if (existsSync(dshBinPath)) {
    const completedAt = state?.completedAt || Date.now();
    if (!state?.completedAt) {
      writeJsonAtomic(installStatePath, {
        manager: state?.manager || null,
        package: DSH_PACKAGE,
        startedAt: state?.startedAt || null,
        completedAt,
      });
    }
    return {
      status: 'installed',
      version: DSH_VERSION,
      package: DSH_PACKAGE,
      runtimeDir,
      completedAt,
    };
  }
  if (state && isProcessAlive(state.pid)) {
    return {
      status: 'installing',
      version: DSH_VERSION,
      package: DSH_PACKAGE,
      manager: state.manager,
      pid: state.pid,
      startedAt: state.startedAt,
    };
  }
  if (state) {
    return {
      status: 'failed',
      version: DSH_VERSION,
      package: DSH_PACKAGE,
      manager: state.manager,
      startedAt: state.startedAt,
      message: '安装进程已经结束，但未找到 DeepSeek Harness 可执行文件。',
      logTail: tailLog(installLogPath, 40),
    };
  }
  return { status: 'requires_install', version: DSH_VERSION, package: DSH_PACKAGE };
}

async function harnessSnapshot() {
  const state = readJson(harnessStatePath);
  if (!state || !isPositivePid(state.pid)) return { status: 'stopped' };
  if (!isProcessAlive(state.pid)) {
    removeFile(harnessStatePath);
    return { status: 'stopped', previousExitDetected: true };
  }
  const healthy = typeof state.url === 'string' && (await requestHealth(state.url));
  return {
    status: healthy ? 'running' : 'starting',
    pid: state.pid,
    url: state.url,
    host: LOOPBACK_HOST,
    port: state.port,
    startedAt: state.startedAt,
  };
}

async function getStatus() {
  ensureDataDirs();
  return {
    install: installSnapshot(),
    harness: await harnessSnapshot(),
    pluginData,
  };
}

async function installHarness() {
  ensureDataDirs();
  const current = installSnapshot();
  if (current.status === 'installed' || current.status === 'installing') return current;

  const manager = selectPackageManager();
  if (!manager) {
    throw new Error('未找到 pnpm 或 npm。请先安装 Node.js 自带的 npm，再重试。');
  }

  writeFileSync(
    path.join(runtimeDir, 'package.json'),
    `${JSON.stringify({ private: true, name: 'dsh-runtime', version: '0.0.0' }, null, 2)}\n`,
    'utf8',
  );

  const args =
    manager.name === 'pnpm'
      ? ['add', '--save-exact', DSH_PACKAGE]
      : ['install', '--save-exact', '--no-audit', '--no-fund', DSH_PACKAGE];
  const pid = spawnDetached(manager.command, args, installLogPath, {
    cwd: runtimeDir,
    shell: process.platform === 'win32',
  });
  const state = {
    pid,
    manager: manager.name,
    package: DSH_PACKAGE,
    startedAt: Date.now(),
  };
  writeJsonAtomic(installStatePath, state);
  return { status: 'installing', version: DSH_VERSION, ...state };
}

async function startHarness() {
  ensureDataDirs();
  if (!existsSync(dshBinPath)) {
    return {
      status: 'requires_install',
      message: `请先在用户明确同意后调用 deepseek_harness_install 安装 ${DSH_PACKAGE}。`,
      package: DSH_PACKAGE,
    };
  }

  const current = await harnessSnapshot();
  if (current.status === 'running' || current.status === 'starting') return current;

  const port = await reservePort();
  const url = `http://${LOOPBACK_HOST}:${port}`;
  const env = {
    ...process.env,
    DSH_HOME: dshHome,
    NO_COLOR: '1',
  };
  const pid = spawnDetached(
    process.execPath,
    [dshBinPath, 'web', '--host', LOOPBACK_HOST, '--port', String(port), '--no-open'],
    harnessLogPath,
    { cwd: pluginData, env },
  );
  const state = { pid, port, url, version: DSH_VERSION, startedAt: Date.now() };
  writeJsonAtomic(harnessStatePath, state);

  if (await waitForHealth(url, pid)) {
    return { status: 'running', host: LOOPBACK_HOST, ...state };
  }

  const logTail = tailLog(harnessLogPath, 60);
  await stopProcessTree(pid);
  removeFile(harnessStatePath);
  throw new Error(`DeepSeek Harness Web 未能在 45 秒内启动。\n${logTail}`.trim());
}

async function stopHarness() {
  ensureDataDirs();
  const state = readJson(harnessStatePath);
  if (!state || !isPositivePid(state.pid) || !isProcessAlive(state.pid)) {
    removeFile(harnessStatePath);
    return { status: 'stopped', alreadyStopped: true };
  }
  await stopProcessTree(state.pid);
  removeFile(harnessStatePath);
  return { status: 'stopped', pid: state.pid };
}

function getLogs(args) {
  ensureDataDirs();
  const kind = args?.kind === 'install' ? 'install' : 'harness';
  const requestedLines = Number.isInteger(args?.lines) ? args.lines : 80;
  const lines = Math.max(1, Math.min(200, requestedLines));
  const filePath = kind === 'install' ? installLogPath : harnessLogPath;
  return { kind, lines, log: tailLog(filePath, lines) };
}

function toolResult(value) {
  return {
    content: [{ type: 'text', text: JSON.stringify(value, null, 2) }],
    structuredContent: value,
  };
}

function toolError(error) {
  const message = error instanceof Error ? error.message : String(error);
  return {
    content: [{ type: 'text', text: message }],
    isError: true,
  };
}

async function callTool(name, args) {
  try {
    switch (name) {
      case 'deepseek_harness_status':
        return toolResult(await getStatus());
      case 'deepseek_harness_install':
        return toolResult(await installHarness());
      case 'deepseek_harness_start':
        return toolResult(await startHarness());
      case 'deepseek_harness_stop':
        return toolResult(await stopHarness());
      case 'deepseek_harness_logs':
        return toolResult(getLogs(args));
      default:
        return toolError(new Error(`未知工具：${name}`));
    }
  } catch (error) {
    return toolError(error);
  }
}

async function handleRequest(message) {
  const id = Object.prototype.hasOwnProperty.call(message, 'id') ? message.id : undefined;
  if (!message || message.jsonrpc !== '2.0' || typeof message.method !== 'string') {
    return id === undefined
      ? null
      : { jsonrpc: '2.0', id, error: { code: -32600, message: 'Invalid Request' } };
  }

  if (id === undefined) return null;

  switch (message.method) {
    case 'initialize':
      return {
        jsonrpc: '2.0',
        id,
        result: {
          protocolVersion: message.params?.protocolVersion || '2024-11-05',
          capabilities: { tools: { listChanged: false } },
          serverInfo: { name: SERVER_NAME, version: SERVER_VERSION },
          instructions:
            '先检查状态；安装需要用户明确同意。启动成功后，使用 Pilkod 内置浏览器打开返回的 loopback URL。',
        },
      };
    case 'ping':
      return { jsonrpc: '2.0', id, result: {} };
    case 'tools/list':
      return { jsonrpc: '2.0', id, result: { tools } };
    case 'tools/call':
      return {
        jsonrpc: '2.0',
        id,
        result: await callTool(message.params?.name, message.params?.arguments || {}),
      };
    default:
      return { jsonrpc: '2.0', id, error: { code: -32601, message: 'Method not found' } };
  }
}

ensureDataDirs();
const input = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
input.on('line', async (line) => {
  if (!line.trim()) return;
  let response;
  try {
    response = await handleRequest(JSON.parse(line));
  } catch (error) {
    response = {
      jsonrpc: '2.0',
      id: null,
      error: { code: -32700, message: error instanceof Error ? error.message : 'Parse error' },
    };
  }
  if (response) process.stdout.write(`${JSON.stringify(response)}\n`);
});
