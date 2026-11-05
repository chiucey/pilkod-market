// @ts-check

import { spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { join } from 'node:path';

import { createScreenHub } from './screen-hub.mjs';

/** @typedef {import('./miniapp-api.js').MiniAppContext} MiniAppContext */
/** @typedef {import('./miniapp-api.js').MiniAppLifecycle} MiniAppLifecycle */

const SURFACE = '/screen';
const ACTIONS = new Set(['refresh', 'home', 'screenshot']);

/**
 * Serve the live phone screen (iPhone or Android) on the host-assigned port.
 * @param {MiniAppContext} context
 * @returns {Promise<MiniAppLifecycle>}
 */
export async function start(context) {
  const root = context.pluginRoot;
  const [html, script, style] = await Promise.all([
    readFile(join(root, 'miniapp/client/index.html')),
    readFile(join(root, 'miniapp/client/app.js')),
    readFile(join(root, 'miniapp/client/style.css')),
  ]);
  const files = new Map([
    [SURFACE, { body: html, type: 'text/html; charset=utf-8' }],
    [`${SURFACE}/`, { body: html, type: 'text/html; charset=utf-8' }],
    [`${SURFACE}/app.js`, { body: script, type: 'text/javascript; charset=utf-8' }],
    [`${SURFACE}/style.css`, { body: style, type: 'text/css; charset=utf-8' }],
  ]);
  const hub = createScreenHub({ pluginRoot: root, logger: context.logger });
  const helpers = {
    ios: { script: join(root, 'server', 'iphone_use.py'), env: { IPHONE_USE_ANALYTICS: '0', IPHONE_USE_SCREEN_OWNER: 'miniapp' } },
    android: { script: join(root, 'server', 'android_use.py'), env: { PHONE_USE_ANDROID_STATE_DIR: hub.androidDir } },
  };

  const server = createServer((request, response) => {
    const url = new URL(request.url ?? '/', 'http://miniapp.local');
    const file = request.method === 'GET' ? files.get(url.pathname) : undefined;
    if (file) {
      response.writeHead(200, { 'content-type': file.type, 'cache-control': 'no-store' });
      response.end(file.body);
      return;
    }
    if (request.method === 'GET' && url.pathname === '/api/screen/frame') {
      const afterSeq = queryInt(url, 'after_seq');
      const lastEvent = queryInt(url, 'last_event_id');
      if (afterSeq == null || lastEvent == null) {
        json(response, 400, { error: { code: 'invalid_argument', message: 'Frame cursors must be non-negative integers.' } });
        return;
      }
      json(response, 200, hub.poll(afterSeq, lastEvent));
      return;
    }
    if (request.method === 'POST' && url.pathname === '/api/screen/action') {
      void action(request, response);
      return;
    }
    json(response, 404, { error: { code: 'not_found', message: 'Not found.' } });
  });

  async function action(request, response) {
    const body = await readBody(request);
    if (body == null) {
      json(response, 400, { error: { code: 'invalid_argument', message: 'Action body must be a small JSON object.' } });
      return;
    }
    let payload;
    try {
      payload = JSON.parse(body);
    } catch {
      json(response, 400, { error: { code: 'invalid_argument', message: 'Action body must be JSON.' } });
      return;
    }
    const name = payload && typeof payload.action === 'string' ? payload.action : '';
    if (!ACTIONS.has(name)) {
      json(response, 400, { error: { code: 'invalid_argument', message: 'Action must be refresh, home, or screenshot.' } });
      return;
    }
    context.logger.info(`screen.action.${name}`);
    const result = await runAction(name, hub.platform() === 'android' ? helpers.android : helpers.ios);
    if (name === 'refresh') hub.restart();
    const preview = hub.poll(0, 0);
    const failed = !result || result.ok === false || result.error;
    json(response, failed ? 409 : 200, {
      ...result,
      ...preview,
      action: name,
      ok: Boolean(result && result.ok !== false && !result.error),
      service_ready: result ? result.service_ready : undefined,
      error: result ? result.error : { code: 'screen_action_failed', message: 'The preview helper did not return a result.' },
    });
  }

  function runAction(name, helper) {
    return new Promise((resolve) => {
      let settled = false;
      const child = spawn('python3', ['-B', helper.script, '--screen-action', name], {
        cwd: root,
        env: { ...process.env, ...helper.env },
        stdio: ['ignore', 'pipe', 'pipe'],
        windowsHide: true,
      });
      hub.track(child);
      const out = [];
      let bytes = 0;
      child.stdout.on('data', (chunk) => {
        bytes += chunk.length;
        if (bytes <= 1024 * 1024) out.push(chunk);
      });
      child.stderr.on('data', () => {});
      const timer = setTimeout(() => {
        child.kill('SIGTERM');
      }, 15000);
      const finish = (value) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        resolve(value);
      };
      child.on('error', () => {
        finish({ ok: false, error: { code: 'screen_action_failed', message: 'The preview helper could not start.' } });
      });
      child.on('exit', () => {
        const text = Buffer.concat(out).toString('utf8').trim();
        try {
          const parsed = JSON.parse(text);
          finish(parsed && typeof parsed === 'object' ? parsed : { ok: false, error: { code: 'screen_action_failed', message: 'The preview helper returned an unexpected result.' } });
        } catch {
          finish({ ok: false, error: { code: 'screen_action_failed', message: 'The preview helper did not return a result. Connect the phone and finish setup first.' } });
        }
      });
    });
  }

  await listen(server, context.listen.host, context.listen.port);
  context.logger.info('miniapp.runtime.listening');

  let disposed = false;
  const dispose = async () => {
    if (disposed) return;
    disposed = true;
    context.signal.removeEventListener('abort', onAbort);
    hub.dispose();
    await close(server);
  };
  const onAbort = () => { void dispose(); };
  context.signal.addEventListener('abort', onAbort, { once: true });
  if (context.signal.aborted) await dispose();
  return { dispose };
}

function queryInt(url, key) {
  const value = url.searchParams.get(key);
  if (value == null || value === '') return 0;
  if (!/^\d+$/.test(value)) return null;
  const number = Number(value);
  return Number.isSafeInteger(number) ? number : null;
}

function readBody(request) {
  return new Promise((resolve) => {
    const chunks = [];
    let size = 0;
    let failed = false;
    request.on('data', (chunk) => {
      size += chunk.length;
      if (size > 4096) {
        failed = true;
        request.destroy();
        resolve(null);
        return;
      }
      chunks.push(chunk);
    });
    request.on('end', () => {
      if (!failed) resolve(Buffer.concat(chunks).toString('utf8'));
    });
    request.on('error', () => resolve(null));
  });
}

function json(response, status, body) {
  response.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' });
  response.end(JSON.stringify(body));
}

function listen(server, host, port) {
  return new Promise((resolve, reject) => {
    const onError = (error) => reject(error);
    server.once('error', onError);
    server.listen(port, host, () => {
      server.off('error', onError);
      resolve();
    });
  });
}

function close(server) {
  return new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
}
