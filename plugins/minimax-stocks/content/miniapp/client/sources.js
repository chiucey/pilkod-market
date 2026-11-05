// 股市 · 数据源页：第三方数据源（Host Connector / 本机 CLI / API Key）与本地能力的连接状态，支持逐个或全部检测。
// 按 API Key 接入的来源（Alpha派）在卡片里填 Key：保存前由服务端校验，页面上不显示 Key 原文。
(() => {
  'use strict';
  const root = document.getElementById('sources-main');
  if (!root) return;
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const STATUS = {
    connected: ['已连接', 'success'], ready: ['可用', 'accent'], degraded: ['部分可用', 'warning'],
    error: ['读取失败', 'danger'], unavailable: ['未连接', 'muted'], checking: ['检测中', 'muted'],
  };
  const fmtTime = (iso) => { const d = new Date(iso); return iso && !Number.isNaN(d.getTime()) ? d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }) : '—'; };
  let data = null;
  const testing = new Set();
  /** 按 API Key 接入的来源：正在保存的、上次保存失败的原因。 */
  const keySaving = new Set();
  /** @type {Record<string, string>} */
  const keyErrors = {};
  let clearing = null;

  root.innerHTML = `
    <div class="assets-head">
      <div class="assets-title"><h1 id="sources-title">数据源</h1><p id="sources-summary" role="status">载入中…</p></div>
      <div class="assets-actions"><button type="button" class="btn primary" id="sources-test-all">全部检测</button></div>
    </div>
    <section class="sources-section" aria-labelledby="sources-third-title">
      <h2 id="sources-third-title">第三方数据源</h2>
      <div id="sources-third" class="source-grid"></div>
    </section>
    <section class="sources-section" aria-labelledby="sources-local-title">
      <h2 id="sources-local-title">本地能力</h2>
      <div id="sources-local" class="source-grid"></div>
    </section>
    <p class="hint sources-note">「检测」只做一次只读调用：代码搜索、简称解析、文档检索、星球列表、鉴权检查、模型列表，不写入任何数据。</p>`;

  document.body.insertAdjacentHTML('beforeend', `
    <dialog id="key-clear-dialog" class="small-dialog" aria-labelledby="key-clear-title">
      <div class="modal-body small-body">
        <h2 id="key-clear-title">清除 API Key？</h2>
        <p id="key-clear-text"></p>
        <p id="key-clear-error" class="field-error" role="alert" hidden></p>
      </div>
      <div class="modal-foot"><span class="spacer"></span><button type="button" class="btn" id="key-clear-cancel" autofocus>取消</button><button type="button" class="btn danger" id="key-clear-confirm">清除</button></div>
    </dialog>`);

  async function api(path, options = {}) {
    const response = await fetch(path, { cache: 'no-store', ...options, ...(options.body ? { headers: { 'content-type': 'application/json' } } : {}) });
    const payload = await response.json().catch(() => null);
    if (!response.ok) throw new Error(payload?.message || '请求失败');
    return payload;
  }

  async function load() {
    try {
      data = await api('/api/sources');
      render();
    } catch (error) {
      $('sources-summary').textContent = '数据源状态暂时无法读取：' + error.message;
    }
  }

  async function test(id) {
    testing.add(id);
    render();
    try {
      data = await api('/api/sources/test', { method: 'POST', body: JSON.stringify({ id }) });
    } catch (error) {
      $('sources-summary').textContent = '检测失败：' + error.message;
    } finally {
      if (id === 'all') testing.clear(); else testing.delete(id);
      render();
    }
  }

  function row(label, value) {
    return `<div><dt>${label}</dt><dd>${value}</dd></div>`;
  }

  function testLine(test, busy) {
    if (busy) return '<span class="test-line">检测中…</span>';
    if (!test) return '<span class="test-line muted">还没有检测</span>';
    return `<span class="test-line ${test.ok ? 'ok' : 'fail'}"><b>${test.ok ? '通过' : '失败'}</b>${esc(test.message)} · ${test.ms} ms · ${fmtTime(test.at)}</span>`;
  }

  /** API Key 表单：没保存时「保存并校验」，保存过可以替换或清除。 */
  function keyForm(source, busy) {
    const key = source.apiKey;
    if (!key) return '';
    const saving = keySaving.has(source.id);
    const error = keyErrors[source.id] ?? '';
    const tail = key.masked ? key.masked.slice(-4) : '';
    const placeholder = key.configured ? '已保存，输入新的 Key 可替换' : '粘贴 ' + source.name + ' API Key';
    return `<form class="key-form" data-key-form="${esc(source.id)}" autocomplete="off" novalidate>
      <label class="field"><span>API Key</span><input type="password" name="apiKey" autocomplete="off" spellcheck="false" placeholder="${esc(placeholder)}" aria-describedby="key-note-${esc(source.id)}" ${saving ? 'disabled' : ''} /></label>
      <p class="field-error" role="alert" ${error ? '' : 'hidden'}>${esc(error)}</p>
      <p class="hint" id="key-note-${esc(source.id)}">保存前会先校验。Key 只存在本机 Mini App 的数据目录，页面上不显示原文。${key.savedAt ? '上次保存于 ' + fmtTime(key.savedAt) + '。' : ''}</p>
      <div class="key-actions">
        ${key.configured ? `<button type="button" class="btn small" data-source-test="${esc(source.id)}" ${busy || saving ? 'disabled' : ''}>${busy ? '检测中…' : '检测'}</button><span class="spacer"></span>` : ''}
        ${key.configured ? `<button type="button" class="btn small danger" data-key-clear="${esc(source.id)}" ${saving ? 'disabled' : ''}>清除 Key</button>` : ''}
        <button type="submit" class="btn small primary" ${saving ? 'disabled' : ''}>${saving ? '校验中…' : key.configured ? '替换并校验' : '保存并校验'}</button>
      </div>
    </form>`;
  }

  function card(source, testableKind) {
    const [label, tone] = STATUS[source.status] ?? [source.status, 'muted'];
    const busy = testing.has(source.id) || testing.has('all');
    // 按 Key 接入的来源，没填 Key 之前不显示「检测」。
    const testable = testableKind && (!source.apiKey || source.apiKey.configured);
    const tools = (source.tools || []).map((tool) => `<span class="tool-chip${tool.present ? ' present' : ' missing'}" title="${tool.required ? '必需' : '可选'}">${esc(tool.name)}${tool.required ? '' : '<small>可选</small>'}</span>`).join('');
    const extra = source.extraTools?.length ? `<p class="hint">另有 ${source.extraTools.length} 个工具：${esc(source.extraTools.slice(0, 8).join('、'))}${source.extraTools.length > 8 ? ' 等' : ''}</p>` : '';
    return `<article class="source-card" aria-labelledby="src-${esc(source.id)}" data-status="${esc(source.status)}">
      <div class="source-card-head"><h3 id="src-${esc(source.id)}">${esc(source.name)}</h3><span class="tag ${tone}">${label}</span></div>
      <p class="source-usage">${esc(source.usage)}</p>
      <dl class="source-meta">
        ${source.access ? row('接入方式', esc(source.access)) : ''}
        ${row('状态', esc(source.detail || label))}
        ${'lastOkAt' in source ? row('最近成功', fmtTime(source.lastOkAt)) : ''}
        ${'lastErrorAt' in source && source.lastErrorAt ? row('最近失败', fmtTime(source.lastErrorAt) + (source.lastError ? ' · ' + esc(source.lastError) : '')) : ''}
        ${testable ? row('上次检测', testLine(source.test, busy)) : ''}
      </dl>
      ${tools ? `<div class="tool-chips" aria-label="Connector 工具">${tools}</div>` : ''}
      ${extra}
      ${source.hint ? `<p class="source-hint">${esc(source.hint)}</p>` : ''}
      ${keyForm(source, busy)}
      ${testable && !source.apiKey ? `<div class="source-actions"><button type="button" class="btn small" data-source-test="${esc(source.id)}" ${busy ? 'disabled' : ''}>${busy ? '检测中…' : '检测'}</button></div>` : ''}
    </article>`;
  }

  function render() {
    if (!data) return;
    const connected = data.thirdParty.filter((source) => source.status === 'connected' || source.status === 'ready').length;
    $('sources-summary').textContent = data.thirdParty.length + ' 个第三方数据源中 ' + connected + ' 个可用' + (data.connector === 'available' ? '' : ' · Mini App 没有获得 Connector 授权') + ' · 更新于 ' + fmtTime(data.checkedAt);
    $('sources-third').innerHTML = data.thirdParty.map((source) => card(source, true)).join('');
    $('sources-local').innerHTML = data.local.map((source) => card(source, source.id === 'agent')).join('');
    $('sources-test-all').disabled = testing.size > 0;
    $('sources-test-all').textContent = testing.has('all') ? '检测中…' : '全部检测';
  }

  root.addEventListener('click', (event) => {
    const button = event.target.closest('[data-source-test]');
    if (button) test(button.dataset.sourceTest);
  });
  $('sources-test-all').addEventListener('click', () => test('all'));

  // 保存 Key：成功后整页重画（卡片状态变了）；失败时保留输入，只在表单里显示原因。
  root.addEventListener('submit', async (event) => {
    const form = event.target.closest('[data-key-form]');
    if (!form) return;
    event.preventDefault();
    const id = form.dataset.keyForm;
    const input = form.querySelector('input[name="apiKey"]');
    const submit = form.querySelector('button[type="submit"]');
    const errorLine = form.querySelector('.field-error');
    const apiKey = input.value.trim();
    const showError = (message) => {
      keyErrors[id] = message;
      errorLine.textContent = message;
      errorLine.hidden = false;
    };
    if (!apiKey) { showError('先粘贴 API Key'); input.focus(); return; }
    const original = submit.textContent;
    keySaving.add(id);
    delete keyErrors[id];
    errorLine.hidden = true;
    form.querySelectorAll('input, button').forEach((element) => { element.disabled = true; });
    submit.textContent = '校验中…';
    try {
      data = await api('/api/sources/' + encodeURIComponent(id), { method: 'PUT', body: JSON.stringify({ apiKey }) });
      keySaving.delete(id);
      render();
      $('sources-summary').textContent = '已保存并通过校验，正在按当前股票拉取舆情';
    } catch (error) {
      keySaving.delete(id);
      form.querySelectorAll('input, button').forEach((element) => { element.disabled = false; });
      submit.textContent = original;
      showError(error.message);
      input.focus();
    }
  });

  // 清除 Key：先用小对话框确认。
  root.addEventListener('click', (event) => {
    const button = event.target.closest('[data-key-clear]');
    if (!button) return;
    clearing = button.dataset.keyClear;
    const name = data?.thirdParty.find((source) => source.id === clearing)?.name ?? clearing;
    $('key-clear-title').textContent = '清除 ' + name + ' 的 API Key？';
    $('key-clear-text').textContent = '清除后不再从 ' + name + ' 检索舆情，行情页里已经抓到的 ' + name + ' 舆情也会移除；已存入资料库的不受影响。之后可以重新填写。';
    $('key-clear-error').hidden = true;
    $('key-clear-confirm').disabled = false;
    $('key-clear-dialog').showModal();
  });
  $('key-clear-cancel').addEventListener('click', () => $('key-clear-dialog').close());
  $('key-clear-confirm').addEventListener('click', async () => {
    if (!clearing) return;
    $('key-clear-confirm').disabled = true;
    try {
      data = await api('/api/sources/' + encodeURIComponent(clearing), { method: 'DELETE' });
      delete keyErrors[clearing];
      clearing = null;
      $('key-clear-dialog').close();
      render();
    } catch (error) {
      $('key-clear-error').textContent = '清除失败：' + error.message;
      $('key-clear-error').hidden = false;
      $('key-clear-confirm').disabled = false;
    }
  });

  window.stockSources = { show: load };
})();
