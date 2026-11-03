// Live preview for the Mini App panel.
// iPhone: the Python MCP server keeps the WDA control session and the operation
// lock. This process is the only MJPEG consumer while the page is polling: it
// writes a short lease the MCP server honors, and it never creates a WDA session.
// Android: while the page is polling, this process runs raw `adb exec-out
// screencap` in a loop and encodes a downscaled PNG. It sends no input.
// The panel shows whichever phone the MCP servers used most recently.

import { spawn } from 'node:child_process';
import { randomBytes } from 'node:crypto';
import { closeSync, existsSync, fsyncSync, openSync, readFileSync, renameSync, statSync, unlinkSync, writeSync } from 'node:fs';
import { homedir, platform } from 'node:os';
import path from 'node:path';

import { rawToPng } from './android-frame.mjs';

const MAX_FRAME_BYTES = 4 * 1024 * 1024;
const LEASE_MS = 5000;
const EVENT_AGE_MS = 10_000;
const BUSY_AGE_MS = 15_000;
const ACTIVITY_GRACE_MS = 650;
const ANDROID_MIN_INTERVAL_MS = 300;
// screencap spends most of its time in device-side latency, so a few staggered
// captures in flight raise the frame rate (real phone ~1.3 fps serial, ~2.6 fps with 3).
const ANDROID_PARALLEL = 3;
const ANDROID_CAPTURE_TIMEOUT_MS = 6000;
const ANDROID_MAX_RAW_BYTES = 8192 * 8192 * 4 + 64;
const ANDROID_PREVIEW_WIDTH = 540;
const SOF_MARKERS = new Set([0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF]);

export function resolveStateDir() {
  const configured = process.env.IPHONE_USE_STATE_DIR || process.env.WDA_STATE_DIR;
  if (configured && configured.trim()) return path.resolve(configured);
  const current = path.join(homedir(), '.local', 'share', 'iphone-use');
  const previous = path.join(homedir(), '.local', 'share', 'iphone-use-wda');
  if (!existsSync(current) && existsSync(path.join(previous, 'config.json'))) return previous;
  return current;
}

export function resolveAndroidStateDir() {
  const configured = process.env.PHONE_USE_ANDROID_STATE_DIR;
  if (configured && configured.trim()) return path.resolve(configured);
  return path.join(homedir(), '.local', 'share', 'phone-use', 'android');
}

export function jpegDimensions(raw) {
  if (raw.length < 4 || raw[0] !== 0xFF || raw[1] !== 0xD8) return null;
  let offset = 2;
  while (offset + 1 < raw.length) {
    if (raw[offset] !== 0xFF) return null;
    while (offset < raw.length && raw[offset] === 0xFF) offset += 1;
    if (offset >= raw.length) return null;
    const marker = raw[offset];
    offset += 1;
    if (marker === 0xD9 || marker === 0xDA) return null;
    if (marker === 0x01 || (marker >= 0xD0 && marker <= 0xD8)) continue;
    if (offset + 2 > raw.length) return null;
    const length = raw.readUInt16BE(offset);
    if (length < 2 || offset + length > raw.length) return null;
    if (SOF_MARKERS.has(marker)) {
      if (length < 8) return null;
      const height = raw.readUInt16BE(offset + 3);
      const width = raw.readUInt16BE(offset + 5);
      return width > 0 && width <= 16384 && height > 0 && height <= 16384 ? { width, height } : null;
    }
    offset += length;
  }
  return null;
}

export class MJPEGParser {
  constructor(maxBytes = MAX_FRAME_BYTES) {
    this.maxBytes = maxBytes;
    this.buffer = Buffer.alloc(0);
  }

  feed(data) {
    const frames = [];
    let incoming = Buffer.from(data);
    while (incoming.length) {
      let room = this.maxBytes - this.buffer.length;
      if (room <= 0) {
        this.buffer = this.buffer.length && this.buffer[this.buffer.length - 1] === 0xFF ? Buffer.from([0xFF]) : Buffer.alloc(0);
        room = this.maxBytes - this.buffer.length;
      }
      const count = Math.min(room, incoming.length, 65536);
      this.buffer = Buffer.concat([this.buffer, incoming.subarray(0, count)]);
      incoming = incoming.subarray(count);
      while (this.buffer.length) {
        const start = this.buffer.indexOf(Buffer.from([0xFF, 0xD8]));
        if (start < 0) {
          this.buffer = this.buffer[this.buffer.length - 1] === 0xFF ? Buffer.from([0xFF]) : Buffer.alloc(0);
          break;
        }
        if (start) this.buffer = this.buffer.subarray(start);
        const end = this.buffer.indexOf(Buffer.from([0xFF, 0xD9]), 2);
        if (end < 0) break;
        const raw = Buffer.from(this.buffer.subarray(0, end + 2));
        this.buffer = this.buffer.subarray(end + 2);
        const dimensions = jpegDimensions(raw);
        if (dimensions) frames.push({ raw, ...dimensions });
      }
    }
    return frames;
  }
}

function nowMs() {
  return Date.now();
}

function finiteNumber(value, maximum = 100_000) {
  if (typeof value !== 'number' || !Number.isFinite(value) || value < 0 || value > maximum) return null;
  return value;
}

function point(value) {
  if (!value || typeof value !== 'object') return null;
  const x = finiteNumber(value.x);
  const y = finiteNumber(value.y);
  return x == null || y == null ? null : { x, y };
}

function viewport(value) {
  if (!value || typeof value !== 'object') return null;
  const width = finiteNumber(value.width);
  const height = finiteNumber(value.height);
  return width && height ? { width, height } : null;
}

function readJson(file) {
  try {
    const value = JSON.parse(readFileSync(file, 'utf8'));
    return value && typeof value === 'object' ? value : null;
  } catch {
    return null;
  }
}

export function readPreviewState(stateDir) {
  const raw = readJson(path.join(stateDir, 'screen-state.json')) ?? {};
  const now = nowMs();
  const actors = {};
  if (raw.actors && typeof raw.actors === 'object') {
    for (const [key, at] of Object.entries(raw.actors)) {
      if (/^[0-9a-f]{32}$/.test(key) && typeof at === 'number' && at >= 0 && now - at >= 0 && now - at < BUSY_AGE_MS) {
        actors[key] = at;
      }
    }
  }
  const events = [];
  const list = Array.isArray(raw.events) ? raw.events.slice(-32) : [];
  for (const event of list) {
    if (!event || (event.kind !== 'tap' && event.kind !== 'drag')) continue;
    if (typeof event.at !== 'number' || typeof event.id !== 'number' || now - event.at < 0 || now - event.at >= EVENT_AGE_MS) continue;
    const clean = { id: event.id, kind: event.kind, at: event.at };
    if (event.kind === 'tap') {
      const where = point(event.point);
      if (!where) continue;
      clean.point = where;
    } else {
      const origin = point(event.from);
      const destination = point(event.to);
      const duration = finiteNumber(event.duration_ms, 5000);
      if (!origin || !destination || duration == null) continue;
      Object.assign(clean, { from: origin, to: destination, duration_ms: duration });
    }
    const frame = viewport(event.viewport);
    if (frame) clean.viewport = frame;
    events.push(clean);
  }
  const paused = raw.paused === true;
  let reason = paused ? raw.pause_reason : null;
  if (paused && reason !== 'device_locked' && reason !== 'authentication') reason = 'unknown';
  const lastId = typeof raw.last_event_id === 'number' && raw.last_event_id >= 0 ? raw.last_event_id : 0;
  const finished = typeof raw.finished_at === 'number' && now - raw.finished_at >= 0 && now - raw.finished_at < ACTIVITY_GRACE_MS
    ? raw.finished_at : 0;
  return {
    paused,
    pause_reason: reason,
    actors,
    events,
    last_event_id: lastId,
    finished_at: finished,
    viewport: viewport(raw.viewport),
    busy: (Object.keys(actors).length > 0 || finished > 0) && !paused,
  };
}

function readConfig(stateDir) {
  const raw = readJson(path.join(stateDir, 'config.json'));
  if (!raw || typeof raw.udid !== 'string' || !/^[A-Za-z0-9-]{8,64}$/.test(raw.udid)) return null;
  const mjpeg = raw.mjpeg_device_port ?? 9100;
  if (typeof mjpeg !== 'number' || !Number.isInteger(mjpeg) || mjpeg < 1024 || mjpeg > 65535) return null;
  const local = raw.local_port ?? 18100;
  const localPort = typeof local === 'number' && Number.isInteger(local) && local >= 1024 && local <= 65535 ? local : 18100;
  return { udid: raw.udid, mjpegPort: mjpeg, localPort };
}

function readModel(stateDir, udid) {
  const known = readJson(path.join(stateDir, 'device.json'));
  if (known && known.udid === udid && typeof known.model === 'string' && known.model.trim()) {
    return known.model.slice(0, 60);
  }
  return null;
}

export function readAndroidConfig(stateDir) {
  const raw = readJson(path.join(stateDir, 'config.json'));
  if (!raw || typeof raw.serial !== 'string' || !/^[A-Za-z0-9._:-]{1,128}$/.test(raw.serial)) return null;
  let adb = 'adb';
  if (typeof raw.adb === 'string' && path.isAbsolute(raw.adb) && /^adb(\.exe)?$/.test(path.basename(raw.adb)) && existsSync(raw.adb)) adb = raw.adb;
  const model = typeof raw.model === 'string' && raw.model.trim() ? raw.model.trim().slice(0, 60) : null;
  const used = typeof raw.last_used_at === 'number' && Number.isFinite(raw.last_used_at) && raw.last_used_at > 0 ? raw.last_used_at : 0;
  return { serial: raw.serial, adb, model, lastUsedAt: used };
}

function modified(file) {
  try {
    return statSync(file).mtimeMs;
  } catch {
    return 0;
  }
}

/** Pick the phone to show: the one an MCP server touched last. */
export function choosePlatform(iosDir, iosConfig, androidDir, androidConfig) {
  if (!androidConfig) return iosConfig ? 'ios' : null;
  if (!iosConfig) return 'android';
  const ios = Math.max(modified(path.join(iosDir, 'config.json')), modified(path.join(iosDir, 'screen-state.json')));
  const android = Math.max(androidConfig.lastUsedAt, modified(path.join(androidDir, 'screen-state.json')));
  return android > ios ? 'android' : 'ios';
}

function writeLease(stateDir, until) {
  const directory = stateDir;
  if (!existsSync(directory)) return;
  const target = path.join(directory, 'miniapp-screen-lease.json');
  const temporary = path.join(directory, `.miniapp-lease-${process.pid}.tmp`);
  const payload = JSON.stringify({ owner: 'miniapp', until });
  let fd;
  try {
    fd = openSync(temporary, 'w', 0o600);
    writeSync(fd, payload);
    fsyncSync(fd);
    closeSync(fd);
    fd = undefined;
    renameSync(temporary, target);
  } catch {
    if (fd !== undefined) {
      try { closeSync(fd); } catch { /* already closed */ }
    }
  } finally {
    try { unlinkSync(temporary); } catch { /* replaced or never created */ }
  }
}

export function createScreenHub({ pluginRoot, logger }) {
  const stateDir = resolveStateDir();
  const androidDir = resolveAndroidStateDir();
  const bundle = path.join(pluginRoot, 'miniapp', 'node', 'usb.bundle.cjs');
  let child = null;
  let parser = new MJPEGParser();
  let frame = null;
  let seq = 0;
  let streamId = randomBytes(16).toString('hex');
  let leaseUntil = 0;
  let nextStart = 0;
  let backoff = 500;
  let lastLeaseWrite = 0;
  let stopped = false;
  let active = null;
  const captures = new Set();
  let captureTimer = null;
  let captureNext = 0;
  let captureBackoff = 0;
  let publishedStart = 0;
  let androidTarget = null;
  const pending = new Set();

  function stopChild(clearFrame) {
    const current = child;
    child = null;
    if (current && current.exitCode == null && !current.killed) {
      current.kill('SIGTERM');
      const timer = setTimeout(() => {
        if (current.exitCode == null) current.kill('SIGKILL');
      }, 500);
      timer.unref?.();
    }
    if (clearFrame) frame = null;
  }

  function stopCapture(clearFrame) {
    if (captureTimer) clearTimeout(captureTimer);
    captureTimer = null;
    for (const current of captures) {
      if (current.exitCode == null && !current.killed) current.kill('SIGKILL');
    }
    captures.clear();
    if (clearFrame) frame = null;
  }

  function publish(item) {
    if (stopped || !frameLive()) return;
    if (frame && frame.raw.equals(item.raw)) return;
    seq += 1;
    frame = { seq, raw: item.raw, width: item.width, height: item.height, mimeType: item.mimeType ?? 'image/jpeg', data: null };
    backoff = 500;
  }

  function frameLive() {
    return !stopped && Date.now() < leaseUntil;
  }

  function ensureStream(config, paused) {
    if (stopped || paused || platform() !== 'darwin' || !config || !existsSync(bundle)) return;
    leaseUntil = Date.now() + LEASE_MS;
    if (Date.now() - lastLeaseWrite > 1000) {
      lastLeaseWrite = Date.now();
      writeLease(stateDir, leaseUntil);
    }
    if (child || Date.now() < nextStart) return;
    nextStart = Date.now() + backoff;
    parser = new MJPEGParser();
    const spawned = spawn(process.execPath, [bundle, 'stream', config.udid, String(config.mjpegPort)], {
      stdio: ['ignore', 'pipe', 'ignore'],
      windowsHide: true,
    });
    child = spawned;
    logger.info('screen.stream.started');
    spawned.stdout.on('data', (chunk) => {
      if (child !== spawned || !frameLive()) return;
      for (const item of parser.feed(chunk)) publish(item);
    });
    spawned.on('error', () => {
      if (child === spawned) child = null;
    });
    spawned.on('exit', () => {
      if (child === spawned) child = null;
      backoff = Math.min(2000, backoff * 2);
      nextStart = Date.now() + backoff;
      logger.info('screen.stream.stopped');
    });
  }

  // Android: up to ANDROID_PARALLEL staggered screencaps, starting at most every
  // ANDROID_MIN_INTERVAL_MS, only while the page keeps polling and the preview is
  // not paused. A result is shown only if it started after the frame on screen.
  function ensureCapture(config) {
    if (stopped || !config) return;
    leaseUntil = Date.now() + LEASE_MS;
    androidTarget = config;
    scheduleCapture();
  }

  function scheduleCapture() {
    if (stopped || captureTimer || captures.size >= ANDROID_PARALLEL || !frameLive() || active !== 'android' || !androidTarget) return;
    const wait = Math.max(0, captureNext - Date.now());
    captureTimer = setTimeout(() => {
      captureTimer = null;
      if (!frameLive() || active !== 'android' || captures.size >= ANDROID_PARALLEL || readPreviewState(androidDir).paused) return;
      captureOnce(androidTarget);
      scheduleCapture();
    }, wait);
    captureTimer.unref?.();
  }

  function captureOnce(config) {
    const started = Date.now();
    captureNext = started + Math.max(ANDROID_MIN_INTERVAL_MS, captureBackoff);
    const chunks = [];
    let size = 0;
    let overflow = false;
    const spawned = spawn(config.adb, ['-s', config.serial, 'exec-out', 'screencap'], {
      stdio: ['ignore', 'pipe', 'ignore'],
      windowsHide: true,
    });
    captures.add(spawned);
    const killer = setTimeout(() => spawned.kill('SIGKILL'), ANDROID_CAPTURE_TIMEOUT_MS);
    killer.unref?.();
    spawned.stdout.on('data', (chunk) => {
      size += chunk.length;
      if (size > ANDROID_MAX_RAW_BYTES) {
        overflow = true;
        spawned.kill('SIGKILL');
        return;
      }
      chunks.push(chunk);
    });
    let finished = false;
    const done = (code) => {
      if (finished) return;
      finished = true;
      clearTimeout(killer);
      if (!captures.delete(spawned)) return;
      let encoded = null;
      if (code === 0 && !overflow && started > publishedStart && frameLive() && active === 'android') {
        try {
          encoded = rawToPng(Buffer.concat(chunks, size), ANDROID_PREVIEW_WIDTH);
        } catch {
          encoded = null;
        }
      }
      if (encoded) {
        captureBackoff = 0;
        if (started > publishedStart && !readPreviewState(androidDir).paused) {
          publishedStart = started;
          publish({ raw: encoded.png, width: encoded.width, height: encoded.height, mimeType: 'image/png' });
        }
      } else if (code !== 0 || overflow) {
        captureBackoff = Math.min(2000, captureBackoff ? captureBackoff * 2 : 500);
        captureNext = Math.max(captureNext, Date.now() + captureBackoff);
      }
      scheduleCapture();
    };
    spawned.on('error', () => done(-1));
    spawned.on('close', (code) => done(code));
  }

  function switchTo(next) {
    if (next === active) return;
    if (active) logger.info(`screen.platform.${next ?? 'none'}`);
    active = next;
    stopChild(true);
    stopCapture(true);
    streamId = randomBytes(16).toString('hex');
    backoff = 500;
    nextStart = 0;
    captureBackoff = 0;
    captureNext = 0;
    publishedStart = 0;
  }

  const timer = setInterval(() => {
    if (Date.now() >= leaseUntil) {
      stopChild(false);
      stopCapture(false);
    }
  }, 400);
  timer.unref?.();

  function wire(state, afterSeq, lastEventId, current) {
    const config = current.config;
    let connection = 'no_device';
    if (!config) connection = 'no_device';
    else if (state.paused) connection = 'paused';
    else if (frame) connection = 'live';
    else connection = 'offline';
    let wireFrame = null;
    if (frame && !state.paused && frame.seq !== afterSeq) {
      if (!frame.data) frame.data = frame.raw.toString('base64');
      wireFrame = { seq: frame.seq, data: frame.data, mimeType: frame.mimeType, width: frame.width, height: frame.height };
    }
    let model = null;
    if (current.platform === 'ios' && config) model = readModel(stateDir, config.udid);
    else if (current.platform === 'android' && config) model = config.model;
    return {
      server_time: nowMs(),
      stream_id: streamId,
      platform: current.platform,
      frame: wireFrame,
      frame_available: Boolean(frame) && !state.paused,
      viewport: state.viewport,
      busy: state.busy,
      paused: state.paused,
      pause_reason: state.pause_reason,
      events: state.paused ? [] : state.events.filter((event) => event.id > lastEventId),
      device: model ? { model } : null,
      connection,
      detail: config ? null : platform() !== 'darwin' ? 'needs_macos' : 'no_config',
    };
  }

  function resolveCurrent() {
    const iosConfig = platform() === 'darwin' ? readConfig(stateDir) : null;
    const androidConfig = readAndroidConfig(androidDir);
    const chosen = choosePlatform(stateDir, iosConfig, androidDir, androidConfig);
    switchTo(chosen);
    if (chosen === 'android') return { platform: chosen, config: androidConfig, dir: androidDir };
    return { platform: chosen, config: iosConfig, dir: stateDir };
  }

  return {
    stateDir,
    androidDir,
    platform() {
      return resolveCurrent().platform;
    },
    poll(afterSeq, lastEventId) {
      const current = resolveCurrent();
      const state = readPreviewState(current.dir);
      if (current.platform === 'android') {
        if (state.paused) stopCapture(true);
        else ensureCapture(current.config);
      } else if (state.paused) stopChild(true);
      else ensureStream(current.config, false);
      return wire(state, afterSeq, lastEventId, current);
    },
    restart() {
      stopChild(true);
      stopCapture(true);
      seq = 0;
      frame = null;
      streamId = randomBytes(16).toString('hex');
      parser = new MJPEGParser();
      backoff = 500;
      nextStart = 0;
      captureBackoff = 0;
      captureNext = 0;
      publishedStart = 0;
    },
    track(childProcess) {
      pending.add(childProcess);
      const forget = () => pending.delete(childProcess);
      childProcess.on('exit', forget);
      childProcess.on('error', forget);
    },
    dispose() {
      if (stopped) return;
      stopped = true;
      clearInterval(timer);
      stopChild(true);
      stopCapture(true);
      for (const childProcess of pending) {
        if (childProcess.exitCode == null) childProcess.kill('SIGTERM');
      }
      pending.clear();
    },
  };
}
