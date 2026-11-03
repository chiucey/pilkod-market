const root = document.getElementById('app');
const device = document.getElementById('device');
const screen = document.getElementById('screen');
const image = document.getElementById('image');
const emptyState = document.getElementById('empty-state');
const emptyText = document.getElementById('empty-state-text');
const emptyDetail = document.getElementById('empty-detail');
const cursor = document.getElementById('cursor');
const stage = document.getElementById('stage');
const model = document.getElementById('model');
const liveText = document.getElementById('live-text');
const toast = document.getElementById('toast');
const tools = {
  refresh: document.getElementById('tool-refresh'),
  home: document.getElementById('tool-home'),
  screenshot: document.getElementById('tool-screenshot'),
};
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
let disposed = false;
let inFlight = false;
let frameSeq = 0;
let frameGeneration = 0;
let streamId;
let eventId = 0;
let dimensions;
let viewport;
let timer;
let failures = 0;
const cursorEffects = new Set();
let suspended = false;
let lastGoodFrame;
let acting = false;
let toastTimer;
const FRAME_INTERVAL = 250;
const LIVE_TEXT = { connecting: '连接中', live: 'Live', paused: '已暂停', offline: '未连接' };
const EMPTY_TEXT = {
  connecting: '正在连接',
  offline: '未连接',
  no_device: '未连接',
  locked: '等待解锁',
  authentication: '请完成认证',
  paused: '预览已暂停',
  unavailable: '画面暂不可用',
};
const EMPTY_DETAIL = {
  no_device: 'No phone connected',
  needs_macos: 'No phone connected. iPhone preview needs macOS, Xcode, and a USB iPhone; Android needs adb and finished setup in chat.',
  no_config: 'No phone connected. Finish iPhone or Android setup in chat, then press refresh.',
  offline: 'The phone is configured, but the preview has not produced a frame yet.',
  locked: 'Unlock the phone, then press refresh.',
  authentication: 'Finish the prompt on the phone. Refresh resumes the preview.',
  paused: 'Preview is paused. Press refresh after you finish on the phone.',
};
const DEFAULT_MODEL = { ios: 'iPhone', android: 'Android' };
const DONE = { refresh: '已刷新连接', home: '已回到主屏幕', screenshot: '截图已复制到剪贴板' };
const FAILED = {
  device_busy: '手机正在执行操作，请稍后再试',
  preview_paused: '认证接管期间已暂停',
  clipboard_unavailable: '截图未能写入剪贴板',
  screen_action_failed: '未连接到手机',
  pua_unreachable: '未连接到手机',
};

const validSize = (value) => !!value && Number.isFinite(value.width) && Number.isFinite(value.height) && value.width > 0 && value.height > 0;
const validPoint = (value) => !!value && Number.isFinite(value.x) && Number.isFinite(value.y);

function syncTools() {
  const paused = root.dataset.live === 'paused';
  const missing = root.dataset.connection === 'no_device';
  tools.refresh.disabled = acting;
  tools.home.disabled = tools.screenshot.disabled = acting || paused || missing;
}

function showEmpty(state, detail) {
  emptyState.dataset.state = state;
  emptyText.textContent = EMPTY_TEXT[state] || EMPTY_TEXT.offline;
  emptyDetail.textContent = detail || EMPTY_DETAIL[state] || '';
}

function setLive(state) {
  if (!image.src) {
    const empty = state === 'paused' ? 'paused' : state === 'offline' ? 'offline' : 'connecting';
    if (!emptyState.dataset.state || emptyState.dataset.state === 'connecting') showEmpty(empty);
  }
  if (root.dataset.live === state) return;
  root.dataset.live = state;
  liveText.textContent = LIVE_TEXT[state];
  liveText.title = '';
  syncTools();
}

function notify(text, failed = false) {
  toast.textContent = text;
  toast.dataset.tone = failed ? 'error' : 'ok';
  toast.hidden = false;
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { toastTimer = undefined; toast.hidden = true; }, 1800);
}

function finishCursor(effect) {
  if (!cursorEffects.delete(effect)) return;
  effect.animation?.cancel();
  if (effect.timer) clearTimeout(effect.timer);
  effect.node.hidden = true;
  if (effect.node !== cursor) effect.node.remove();
}

function hideCursor() {
  for (const effect of cursorEffects) finishCursor(effect);
}

function clearFrame(resetOperating = true) {
  const hadDimensions = !!dimensions;
  frameGeneration += 1;
  hideCursor();
  image.removeAttribute('src');
  image.hidden = true;
  emptyState.hidden = false;
  device.hidden = screen.hidden = disposed;
  dimensions = undefined;
  lastGoodFrame = undefined;
  frameSeq = 0;
  root.dataset.frameSeq = '0';
  root.dataset.busy = 'false';
  if (resetOperating) root.dataset.operating = 'false';
  if (!disposed && hadDimensions) fitFrame();
}

function retainFrame() {
  hideCursor();
  root.dataset.busy = 'false';
}

const visible = () => !disposed && !suspended && !document.hidden;

function glowMask(width, height, radius, band, bridge) {
  const round = (value) => Math.round(value * 100) / 100;
  const bloom = Math.min(width, height) * 0.27;
  const corners = [[0, 0], [width, 0], [0, height], [width, height]]
    .map(([x, y]) => `<circle cx='${round(x)}' cy='${round(y)}' r='${round(bloom)}'/>`).join('');
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='${round(width)}' height='${round(height)}'>`
    + `<defs><linearGradient id='x'><stop stop-color='#fff'/><stop offset='.16' stop-color='#fff' stop-opacity='.85'/><stop offset='.36' stop-color='#fff' stop-opacity='${bridge}'/><stop offset='.64' stop-color='#fff' stop-opacity='${bridge}'/><stop offset='.84' stop-color='#fff' stop-opacity='.85'/><stop offset='1' stop-color='#fff'/></linearGradient>`
    + `<linearGradient id='y' x2='0' y2='1'><stop stop-color='#fff'/><stop offset='.1' stop-color='#fff' stop-opacity='.85'/><stop offset='.28' stop-color='#fff' stop-opacity='0'/><stop offset='.72' stop-color='#fff' stop-opacity='0'/><stop offset='.9' stop-color='#fff' stop-opacity='.85'/><stop offset='1' stop-color='#fff'/></linearGradient>`
    + `<mask id='ends'><rect width='100%' height='100%' fill='url(#y)'/></mask><mask id='corners'><rect width='100%' height='100%' fill='url(#x)' mask='url(#ends)'/></mask></defs>`
    + `<filter id='f' x='-30%' y='-30%' width='160%' height='160%'><feGaussianBlur stdDeviation='${round(band * .3)}'/></filter>`
    + `<filter id='g' x='-60%' y='-60%' width='220%' height='220%'><feGaussianBlur stdDeviation='${round(bloom * .42)}'/></filter>`
    + `<g mask='url(#corners)'><g fill='#fff' fill-opacity='.46' filter='url(#g)'>${corners}</g>`
    + `<rect width='${round(width)}' height='${round(height)}' rx='${round(radius)}' fill='none' stroke='#fff' stroke-width='${round(band * .9)}' filter='url(#f)'/>`
    + `<rect x='.75' y='.75' width='${round(width - 1.5)}' height='${round(height - 1.5)}' rx='${round(Math.max(0, radius - .75))}' fill='none' stroke='#fff' stroke-opacity='.9' stroke-width='1.5'/></g></svg>`;
  return `url("data:image/svg+xml,${encodeURIComponent(svg)}")`;
}

function glowDots(step, phase) {
  const count = 16;
  const round = (value) => Math.round(value * 100) / 100;
  const size = round(count * step);
  const dots = [];
  for (let row = 0; row < count; row++) {
    for (let col = 0; col < count; col++) {
      const diagonal = (col + row) / count * Math.PI * 2;
      const bend = Math.sin((col - row) / count * Math.PI * 2) * 0.8;
      const wave = (1 + Math.sin(diagonal + bend + phase)) / 2;
      dots.push(`<circle cx='${round((col + .5) * step)}' cy='${round((row + .5) * step)}' r='${round(step * (.04 + .23 * wave))}' fill-opacity='${round(.25 + .65 * wave)}'/>`);
    }
  }
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='${size}' height='${size}' viewBox='0 0 ${size} ${size}'><g fill='#fff'>${dots.join('')}</g></svg>`;
  return `url("data:image/svg+xml,${encodeURIComponent(svg)}")`;
}

function fitFrame() {
  const size = dimensions ?? viewport ?? { width: 440, height: 956 };
  const width = stage.clientWidth;
  const height = stage.clientHeight;
  const shortSide = Math.min(size.width, size.height);
  const bezel = shortSide * 0.024;
  const outerWidth = size.width + 2 * bezel;
  const outerHeight = size.height + 2 * bezel;
  const scale = 0.96 * Math.min(width / outerWidth, height / outerHeight);
  device.style.width = `${outerWidth * scale}px`;
  device.style.height = `${outerHeight * scale}px`;
  device.style.setProperty('--bezel', `${bezel * scale}px`);
  const radius = shortSide * 0.12 * scale;
  device.style.setProperty('--screen-radius', `${radius}px`);
  const band = Math.min(bezel * scale * 3.8, radius);
  for (const [phase, bridge] of [0.12, 0.32, 0.62].entries()) {
    device.style.setProperty(phase === 0 ? '--glow-mask' : `--glow-mask-${phase}`, glowMask(size.width * scale, size.height * scale, radius, band, bridge));
  }
  const dotStep = Math.max(5, bezel * scale * 0.95);
  for (let phase = 0; phase < 3; phase++) device.style.setProperty(`--glow-dots-${phase}`, glowDots(dotStep, phase * Math.PI * 2 / 3));
  device.dataset.orientation = size.width > size.height ? 'landscape' : 'portrait';
}

function pointStyle(point, size) {
  return {
    left: `${Math.max(0, Math.min(1, point.x / size.width)) * 100}%`,
    top: `${Math.max(0, Math.min(1, point.y / size.height)) * 100}%`,
  };
}

function showGesture(gesture) {
  if (screen.hidden || image.hidden) return;
  const size = validSize(gesture.viewport) ? gesture.viewport : viewport;
  if (!size) return;
  if (dimensions && Math.abs((size.width / size.height) / (dimensions.width / dimensions.height) - 1) > 0.08) return;
  const point = gesture.kind === 'tap' ? gesture.point : gesture.from;
  if (!validPoint(point)) return;
  if (gesture.kind === 'drag' && !validPoint(gesture.to)) return;
  const marker = cursor.hidden ? cursor : cursor.cloneNode(false);
  if (marker !== cursor) {
    marker.removeAttribute('id');
    screen.appendChild(marker);
  }
  Object.assign(marker.style, pointStyle(point, size));
  marker.hidden = false;
  const effect = { node: marker };
  cursorEffects.add(effect);
  const movement = Math.max(600, Math.min(1000, gesture.duration_ms || 650));
  const duration = gesture.kind === 'drag' ? movement + 1000 : 1600;
  if (reducedMotion.matches) {
    if (gesture.kind === 'drag') Object.assign(marker.style, pointStyle(gesture.to, size));
    effect.timer = setTimeout(() => finishCursor(effect), duration);
    return;
  }
  const delta = gesture.kind === 'drag'
    ? `translate(${(gesture.to.x - point.x) / size.width * screen.clientWidth}px, ${(gesture.to.y - point.y) / size.height * screen.clientHeight}px)`
    : '';
  const frames = gesture.kind === 'drag'
    ? [
      { transform: 'translate(0, 0) scale(.96)', opacity: 0 },
      { transform: 'translate(0, 0) scale(1)', opacity: 1, offset: 80 / duration },
      { transform: 'translate(0, 0) scale(.92)', opacity: 1, offset: 200 / duration, easing: 'cubic-bezier(.3,0,.2,1)' },
      { transform: `${delta} scale(.92)`, opacity: 1, offset: (movement + 200) / duration },
      { transform: `${delta} scale(1.06)`, opacity: 1, offset: (movement + 380) / duration },
      { transform: `${delta} scale(1)`, opacity: 1, offset: (duration - 350) / duration },
      { transform: `${delta} scale(1)`, opacity: 1, offset: (duration - 200) / duration },
      { transform: `${delta} scale(.98)`, opacity: 0 },
    ]
    : [
      { transform: 'scale(.96)', opacity: 0 },
      { transform: 'scale(1)', opacity: 1, offset: 0.06 },
      { transform: 'scale(.9)', opacity: 1, offset: 0.16 },
      { transform: 'scale(1.06)', opacity: 1, offset: 0.28 },
      { transform: 'scale(1)', opacity: 1, offset: 0.4 },
      { transform: 'scale(1)', opacity: 1, offset: 0.875 },
      { transform: 'scale(.98)', opacity: 0 },
    ];
  effect.animation = marker.animate(frames, { duration, easing: 'linear' });
  effect.animation.onfinish = () => finishCursor(effect);
}

function applyConnection(preview) {
  root.dataset.connection = preview.connection || '';
  if (preview.connection === 'no_device') {
    clearFrame();
    setLive('offline');
    liveText.textContent = LIVE_TEXT.offline;
    const detail = preview.detail === 'needs_macos' ? EMPTY_DETAIL.needs_macos : EMPTY_DETAIL.no_config;
    showEmpty('no_device', detail);
    return true;
  }
  return false;
}

function consume(value) {
  if (disposed || !value || typeof value !== 'object') return;
  if (typeof value.stream_id === 'string' && value.stream_id !== streamId) {
    streamId = value.stream_id;
    frameSeq = 0;
    eventId = 0;
    root.dataset.operating = 'false';
    retainFrame();
  }
  if ((value.platform === 'ios' || value.platform === 'android') && root.dataset.platform !== value.platform) {
    if (root.dataset.platform) clearFrame();
    root.dataset.platform = value.platform;
    model.textContent = DEFAULT_MODEL[value.platform];
  }
  if (typeof value.device?.model === 'string' && value.device.model) model.textContent = value.device.model;
  if (validSize(value.viewport) && (viewport?.width !== value.viewport.width || viewport?.height !== value.viewport.height)) {
    viewport = value.viewport;
    if (!dimensions) fitFrame();
  }
  if (applyConnection(value)) return;
  if (value.paused === true) {
    clearFrame();
    setLive('paused');
    liveText.textContent = value.pause_reason === 'device_locked' ? '等待解锁' : LIVE_TEXT.paused;
    liveText.title = value.pause_reason === 'device_locked'
      ? '解锁手机后继续任务，或点击刷新恢复预览'
      : '预览已暂停；完成手机认证后继续任务或点击刷新恢复画面';
    showEmpty(value.pause_reason === 'device_locked' ? 'locked' : value.pause_reason === 'authentication' ? 'authentication' : 'paused');
    return;
  }
  if (value.frame_available === false) {
    retainFrame();
    setLive('offline');
    if (!image.src) showEmpty('offline', EMPTY_DETAIL.offline);
  } else if (value.frame_available === true || value.frame) setLive('live');
  const frame = value.frame;
  if (frame && validSize(frame) && Number.isInteger(frame.seq) && frame.seq > frameSeq
      && typeof frame.data === 'string' && frame.data.length > 0
      && ['image/jpeg', 'image/png', 'image/webp'].includes(frame.mimeType)) {
    frameSeq = frame.seq;
    root.dataset.frameSeq = String(frame.seq);
    if (!dimensions || dimensions.width !== frame.width || dimensions.height !== frame.height) {
      dimensions = { width: frame.width, height: frame.height };
      fitFrame();
    }
    image.src = `data:${frame.mimeType};base64,${frame.data}`;
    image.hidden = false;
    emptyState.hidden = true;
    device.hidden = false;
    screen.hidden = false;
  }
  if (typeof value.busy === 'boolean') root.dataset.busy = String(value.busy);
  if (value.busy === true) root.dataset.operating = 'true';
  if (Array.isArray(value.events)) {
    for (const gesture of value.events) {
      if (!Number.isInteger(gesture.id) || gesture.id <= eventId) continue;
      eventId = gesture.id;
      const age = (value.server_time || Date.now()) - gesture.at;
      if (Number.isFinite(age) && age >= -1000 && age <= 2500 && (gesture.kind === 'tap' || gesture.kind === 'drag')) {
        root.dataset.operating = 'true';
        showGesture(gesture);
      }
    }
  }
}

function schedule(delay) {
  if (!visible() || timer) return;
  timer = setTimeout(() => { timer = undefined; void poll(); }, delay);
}

async function poll() {
  if (!visible() || inFlight) return;
  inFlight = true;
  const started = performance.now();
  let nextDelay = FRAME_INTERVAL;
  try {
    const generation = frameGeneration;
    const response = await fetch(`/api/screen/frame?after_seq=${frameSeq}&last_event_id=${eventId}`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(3000),
    });
    if (!response.ok) throw new Error('preview unavailable');
    const data = await response.json();
    if (!visible() || generation !== frameGeneration) return;
    consume(data);
    failures = 0;
    nextDelay = data.paused || data.connection === 'no_device' || data.frame_available === false
      ? 1000 : Math.max(0, FRAME_INTERVAL - (performance.now() - started));
  } catch {
    failures += 1;
    nextDelay = Math.min(2000, 500 * failures);
    retainFrame();
    if (failures > 1 && root.dataset.live !== 'paused') setLive('offline');
  } finally {
    inFlight = false;
    schedule(nextDelay);
  }
}

async function act(name) {
  if (acting || disposed || tools[name].disabled) return;
  const previousEmptyState = emptyState.dataset.state;
  if (name === 'refresh') {
    frameGeneration += 1;
    if (!image.src) showEmpty('connecting');
  }
  acting = true;
  tools[name].dataset.busy = 'true';
  syncTools();
  try {
    const response = await fetch('/api/screen/action', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ action: name }),
      signal: AbortSignal.timeout(16000),
    });
    const data = await response.json();
    if (!response.ok || data.error) {
      if (name === 'refresh' && !image.src) showEmpty(previousEmptyState);
      notify(FAILED[data.error?.code ?? ''] ?? '操作未完成，请重试', true);
      if (name === 'refresh') consume(data);
    } else {
      if (name === 'refresh') consume(data);
      const missing = name === 'refresh' && data.service_ready === false;
      notify(missing ? '未连接到手机，请确认连接后重试' : DONE[name], missing);
      if (timer) clearTimeout(timer);
      timer = undefined;
      schedule(0);
    }
  } catch {
    if (name === 'refresh' && !image.src) showEmpty(previousEmptyState);
    notify('操作未完成，请重试', true);
  } finally {
    acting = false;
    delete tools[name].dataset.busy;
    syncTools();
  }
}

for (const name of Object.keys(tools)) tools[name].addEventListener('click', () => { void act(name); });

function visibilityChanged() {
  root.dataset.pageVisible = String(visible());
  if (timer) clearTimeout(timer);
  timer = undefined;
  if (visible()) schedule(0);
  else retainFrame();
}

const resizeObserver = new ResizeObserver(fitFrame);
resizeObserver.observe(stage);
image.addEventListener('load', () => {
  if (dimensions && image.src) lastGoodFrame = { source: image.src, size: dimensions };
});
image.addEventListener('error', () => {
  if (disposed || root.dataset.live === 'paused' || !image.src) return;
  if (lastGoodFrame && image.src !== lastGoodFrame.source) {
    image.src = lastGoodFrame.source;
    dimensions = lastGoodFrame.size;
    fitFrame();
  } else if (!lastGoodFrame) {
    clearFrame();
    setLive('offline');
    showEmpty('unavailable');
  }
  frameSeq = 0;
  retainFrame();
});
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) suspended = false;
  visibilityChanged();
});
window.addEventListener('pagehide', () => { suspended = true; visibilityChanged(); });
window.addEventListener('pageshow', () => { suspended = false; visibilityChanged(); });
window.addEventListener('focus', () => { if (!document.hidden) { suspended = false; visibilityChanged(); } });

root.dataset.pageVisible = String(visible());
device.hidden = screen.hidden = false;
image.hidden = true;
emptyState.hidden = false;
showEmpty('connecting');
fitFrame();
syncTools();
schedule(0);
