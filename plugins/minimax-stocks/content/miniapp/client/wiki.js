// 股市 · 资产页：按功能分页签（资料库 = 输入，知识图谱 = 输出；产业链是知识图谱按行业下钻的视图）。
// 依赖 index.html 主脚本的全局：state、loadSnapshot、loadWatchlist、reportViewState、scheduleChart。
(() => {
  'use strict';
  const root = document.getElementById('assets-main');
  if (!root) return;
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const enc = encodeURIComponent;
  const nameKey = (value) => String(value ?? '').normalize('NFKC').trim().toLowerCase().replace(/\s+/g, ' ');
  const TYPES = { industry: '行业', segment: '环节', company: '公司', product: '产品/技术', concept: '概念', event: '事件', source: '资料摘要' };
  const CHAINS = { upstream: '上游', midstream: '中游', downstream: '下游' };
  const OUT_LABELS = { upstream_of: '下游环节', supplies: '客户', belongs_to: '所属', produces: '产品 / 布局', competes: '竞争对手', substitutes: '可替代', drives: '影响对象', related: '相关' };
  const IN_LABELS = { upstream_of: '上游环节', supplies: '供应商', belongs_to: '下属', produces: '生产方', competes: '竞争对手', substitutes: '被它替代', drives: '影响因素', related: '相关' };
  const TYPE_COLOR = { industry: 'var(--mcode-accent)', segment: 'var(--ma-20)', company: 'var(--ma-5)', product: 'var(--ma-10)', concept: 'var(--ma-60)', event: 'var(--ma-120)', source: 'var(--mcode-text-subtle)' };
  const STATUS_TAG = { new: ['待整理', 'accent'], changed: ['有更新', 'warning'], queued: ['整理中', 'accent'], ingested: ['已整理', 'success'], skipped: ['已跳过', 'muted'], too_large: ['文件过大', 'danger'] };
  const agentApi = window.mcode?.miniapp?.agent;
  const store = {
    get(key) { try { return localStorage.getItem(key); } catch { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); } catch {} },
  };
  const ws = {
    page: 'market', status: null, files: null, graph: null, byId: new Map(), names: new Map(), lenses: null,
    selected: null, detail: null, mode: 'graph', industry: 'all', chainIndustry: 'all',
    tab: store.get('assets.tab') || 'files', fileFilter: 'all', fileFolder: 'all', fileSearch: '',
    query: '', hiddenTypes: new Set(['source']), sessionDir: null, loaded: false,
    detailSeq: 0, positions: new Map(), viewBox: null, bounds: null,
  };
  const X = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>';

  // ---------- 骨架 ----------
  // 资产页的功能页签：以后新增的资产功能在这里登记一个页签，并在下面加一个对应的 panel。
  const ASSET_TABS = [
    { id: 'files', label: '资料库' },
    { id: 'graph', label: '知识图谱' },
    { id: 'changes', label: '边际变化' },
  ];
  const SEARCH_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 4.5 4.5"/></svg>';
  root.innerHTML = `
    <div class="assets-head">
      <div class="assets-title"><h1 id="assets-title">资产</h1><p id="wiki-summary" class="assets-status" role="status"></p></div>
      <div class="auto-control" id="auto-control" role="status"></div>
    </div>
    <div class="asset-tabs" role="tablist" aria-label="资产功能">
      ${ASSET_TABS.map((tab) => `<button type="button" role="tab" id="asset-tab-${tab.id}" data-asset-tab="${tab.id}" aria-controls="asset-panel-${tab.id}" aria-selected="false" tabindex="-1">${tab.label}<small id="tab-count-${tab.id}"></small></button>`).join('')}
    </div>
    <section id="wiki-job" class="wiki-job" aria-label="后台任务" hidden></section>

    <section id="asset-panel-files" class="asset-panel" role="tabpanel" aria-labelledby="asset-tab-files" hidden>
      <section class="panel" aria-labelledby="folders-title">
        <div class="panel-head">
          <div><h2 id="folders-title">关联文件夹</h2><p class="panel-sub">只读扫描，子文件夹一起；资料不用事先按股票或行业分类。</p></div>
          <div class="panel-actions">
            <button type="button" class="btn primary" id="folder-pick" hidden>选择文件夹…</button>
            <button type="button" class="btn" id="folder-path-toggle" aria-expanded="false" aria-controls="folder-form">输入路径</button>
          </div>
        </div>
        <form id="folder-form" class="folder-form" hidden>
          <label class="sr-only" for="folder-path">资料文件夹路径</label>
          <input id="folder-path" placeholder="例如 ~/Documents/研报" autocomplete="off" spellcheck="false" />
          <button type="submit" class="btn">关联</button>
        </form>
        <button type="button" id="session-folder" class="link-btn" hidden></button>
        <p id="folder-error" class="field-error" role="alert" hidden></p>
        <ul id="folder-list" class="folder-cards" aria-label="已关联的文件夹"></ul>
      </section>
      <section class="panel" aria-labelledby="files-title">
        <div class="panel-head">
          <div><h2 id="files-title">资料文件</h2><p class="panel-sub" id="files-sub"></p></div>
        </div>
        <div class="files-toolbar">
          <div class="segmented" role="group" aria-label="按整理状态筛选">
            <button type="button" data-file-filter="all" aria-pressed="true">全部<small id="ff-all">0</small></button>
            <button type="button" data-file-filter="pending" aria-pressed="false">待整理<small id="ff-pending">0</small></button>
            <button type="button" data-file-filter="ingested" aria-pressed="false">已整理<small id="ff-ingested">0</small></button>
          </div>
          <select id="files-folder" aria-label="按文件夹筛选"></select>
          <label class="canvas-search">${SEARCH_ICON}<input id="files-search" placeholder="搜索文件名" aria-label="搜索资料文件" autocomplete="off" /></label>
          <button type="button" class="icon-btn" id="files-refresh" aria-label="重新扫描资料文件" title="重新扫描"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M20 10a8 8 0 0 0-14.8-3M4 3v5h5M4 14a8 8 0 0 0 14.8 3M20 21v-5h-5"/></svg></button>
        </div>
        <div class="table-scroll">
          <table class="files-table">
            <thead><tr>
              <th scope="col" class="col-name">名称</th><th scope="col" class="col-status">状态</th><th scope="col" class="col-stocks">关联股票</th><th scope="col" class="col-num">大小</th><th scope="col" class="col-time">修改时间</th>
            </tr></thead>
            <tbody id="file-list"><tr><td colspan="5" class="list-state">载入中…</td></tr></tbody>
          </table>
        </div>
      </section>
    </section>

    <section id="asset-panel-graph" class="asset-panel" role="tabpanel" aria-labelledby="asset-tab-graph" hidden>
      <div class="graph-head">
        <p id="graph-meta" class="graph-meta" role="status"></p>
        <div class="panel-actions">
          <button type="button" class="link-btn" id="wiki-open-folder" hidden>打开知识库文件夹</button>
          <button type="button" class="btn" id="lens-open">分析视角</button>
        </div>
      </div>
      <div id="wiki-notice" class="wiki-notice" role="status" hidden></div>
      <div class="graph-body" id="graph-body">
      <section class="wiki-canvas" aria-labelledby="canvas-title">
        <h2 id="canvas-title" class="sr-only">知识图谱</h2>
        <div class="canvas-toolbar">
          <div class="canvas-left" id="graph-tools">
            <select id="industry-select" aria-label="按行业筛选"></select>
            <button type="button" class="btn small" id="chain-enter" hidden>查看产业链</button>
          </div>
          <nav class="chain-crumb" id="chain-tools" aria-label="当前位置" hidden>
            <button type="button" class="link-btn" id="chain-back">知识图谱</button>
            <span aria-hidden="true">/</span>
            <select id="chain-industry" aria-label="选择行业"></select>
            <span>产业链</span>
          </nav>
          <label class="canvas-search">${SEARCH_ICON}<input id="wiki-search" placeholder="搜索节点" aria-label="搜索知识图谱节点" autocomplete="off" /></label>
        </div>
        <div id="canvas-state" class="canvas-state" role="status" hidden></div>
        <div id="chain-view" class="chain-view" hidden></div>
        <div id="graph-view" class="graph-view" hidden>
          <svg id="graph-svg" role="group" aria-label="知识图谱：节点是资料里的行业、环节、公司等，连线是它们之间的关系"></svg>
          <div class="graph-controls" role="group" aria-label="缩放">
            <button type="button" class="icon-btn" data-zoom="in" aria-label="放大"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg></button>
            <button type="button" class="icon-btn" data-zoom="out" aria-label="缩小"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 12h14"/></svg></button>
            <button type="button" class="icon-btn" data-zoom="fit" aria-label="适配视图"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg></button>
          </div>
        </div>
        <div id="wiki-legend" class="wiki-legend" role="group" aria-label="图例与类型筛选"></div>
      </section>
      <aside class="wiki-detail" id="wiki-detail" aria-label="节点详情" tabindex="-1"></aside>
      </div>
    </section>

    <section id="asset-panel-changes" class="asset-panel" role="tabpanel" aria-labelledby="asset-tab-changes" hidden>
      <div class="graph-head">
        <p id="changes-meta" class="graph-meta" role="status"></p>
        <div class="panel-actions"><span class="hint" id="changes-auto"></span><button type="button" class="btn small" id="changes-scan" hidden>立即扫描</button></div>
      </div>
      <div class="files-toolbar changes-toolbar">
        <div class="segmented" role="group" aria-label="按方向筛选">
          <button type="button" data-change-dir="all" aria-pressed="true">全部<small id="cd-all">0</small></button>
          <button type="button" data-change-dir="improve" aria-pressed="false">改善<small id="cd-improve">0</small></button>
          <button type="button" data-change-dir="weaken" aria-pressed="false">走弱<small id="cd-weaken">0</small></button>
          <button type="button" data-change-dir="unclear" aria-pressed="false">待判断<small id="cd-unclear">0</small></button>
        </div>
        <select id="changes-dimension" aria-label="按维度筛选"><option value="all">全部维度</option></select>
        <select id="changes-source" aria-label="按来源筛选"><option value="all">全部来源</option></select>
        <select id="changes-range" aria-label="时间范围"><option value="all">全部时间</option><option value="30">近 30 天</option><option value="90">近 90 天</option><option value="365">近一年</option></select>
        <label class="canvas-search">${SEARCH_ICON}<input id="changes-search" placeholder="搜索对象或内容" aria-label="搜索边际变化" autocomplete="off" /></label>
      </div>
      <p class="hint changes-note">方向是后台 Agent 依据资料做的判断，仅供参考；每条都附出处，点出处用默认应用或浏览器打开原文。</p>
      <div id="changes-list" class="changes-list"></div>
    </section>`;

  document.body.insertAdjacentHTML('beforeend', `
    <dialog id="lens-dialog" class="wide-dialog" aria-labelledby="lens-title">
      <div class="modal-head"><div><h2 id="lens-title">分析视角</h2><p class="modal-sub">后台 Agent 自动整理资料时，会按启用的视角 Prompt 拆解内容。可以改写、停用、恢复默认，或新建自己的视角；修改后对之后整理的资料生效。</p></div><button type="button" class="icon-btn" id="lens-close" aria-label="关闭分析视角">${X}</button></div>
      <div class="lens-body">
        <label class="field"><span>研究目标（可选）</span><textarea id="lens-purpose" rows="2" maxlength="2000" placeholder="例如：跟踪 AI 算力产业链，重点关注光模块和 HBM 的国产替代机会"></textarea></label>
        <div class="lens-layout">
          <ul id="lens-list" class="lens-list" aria-label="视角列表"></ul>
          <div class="lens-editor">
            <label class="field"><span>名称</span><input id="lens-name" maxlength="30" autocomplete="off" /></label>
            <label class="field grow"><span>Prompt</span><textarea id="lens-prompt" rows="12" maxlength="6000" spellcheck="false"></textarea></label>
            <div class="lens-editor-actions"><button type="button" class="btn" id="lens-reset">恢复默认</button><button type="button" class="btn danger" id="lens-delete">删除视角</button><span id="lens-meta" class="hint"></span></div>
          </div>
        </div>
        <p id="lens-error" class="field-error" role="alert" hidden></p>
      </div>
      <div class="modal-foot"><button type="button" class="btn" id="lens-add">新建视角</button><span class="spacer"></span><button type="button" class="btn" id="lens-cancel">取消</button><button type="button" class="btn primary" id="lens-save">保存</button></div>
    </dialog>
    <dialog id="dup-dialog" class="wide-dialog" aria-labelledby="dup-title">
      <div class="modal-head"><div><h2 id="dup-title">合并重复的公司节点</h2><p class="modal-sub">同一家公司只保留一个页面。选好要保留的主页面后合并：其他页面的别名、股票代码、关系和来源都会并入，原页面文件移到知识库的 archive/，不会删除。</p></div><button type="button" class="icon-btn" id="dup-close" aria-label="关闭">${X}</button></div>
      <div class="modal-body dup-body" id="dup-body"></div>
      <div class="modal-foot"><button type="button" class="btn" id="dup-merge-high">合并全部高置信度</button><span class="spacer"></span><button type="button" class="btn primary" id="dup-done">完成</button></div>
    </dialog>
    <dialog id="permission-dialog" class="small-dialog" aria-labelledby="permission-title">
      <div class="modal-body small-body">
        <h2 id="permission-title">后台整理需要你授权</h2>
        <p id="permission-subject" class="hint"></p>
        <p class="permission-tool"><strong id="permission-tool"></strong></p>
        <p id="permission-reason"></p>
        <details id="permission-details"><summary>查看调用参数</summary><pre id="permission-input"></pre></details>
        <p id="permission-error" class="field-error" role="alert" hidden></p>
      </div>
      <div class="modal-foot"><button type="button" class="btn" id="permission-later" autofocus>稍后</button><span class="spacer"></span><button type="button" class="btn" data-permission="deny">拒绝</button><button type="button" class="btn primary" data-permission="allowOnce">允许一次</button></div>
    </dialog>
    <dialog id="notice-dialog" class="small-dialog" aria-labelledby="notice-title">
      <div class="modal-body small-body"><h2 id="notice-title">需要你处理一下</h2><p id="notice-text"></p></div>
      <div class="modal-foot"><span class="spacer"></span><button type="button" class="btn" id="notice-close" autofocus>稍后</button><button type="button" class="btn primary" id="notice-action"></button></div>
    </dialog>`);


  document.body.insertAdjacentHTML('beforeend', `
    <dialog id="minutes-dialog" class="minutes-dialog" aria-labelledby="minutes-title">
      <div class="modal-head"><div><h2 id="minutes-title">纪要</h2><p id="minutes-meta" class="modal-sub"></p></div><button type="button" class="icon-btn" id="minutes-close" aria-label="关闭纪要">${X}</button></div>
      <div class="modal-body minutes-body">
        <p id="minutes-note" class="minutes-note"></p>
        <blockquote id="minutes-excerpt" class="minutes-excerpt"></blockquote>
        <p id="minutes-reasons" class="hint"></p>
      </div>
      <div class="modal-foot"><button type="button" class="btn" id="minutes-graph" hidden>在知识图谱中查看</button><span class="spacer"></span><button type="button" class="btn primary" id="minutes-open">用默认应用打开</button></div>
    </dialog>
    <div id="wiki-toast" class="wiki-toast" role="status" aria-live="polite" hidden></div>`);

  // ---------- 通用 ----------
  async function api(path, options = {}) {
    const init = { cache: 'no-store', ...options };
    if (options.body !== undefined) init.headers = { 'content-type': 'application/json' };
    const response = await fetch(path, init);
    let payload = null;
    try { payload = await response.json(); } catch {}
    if (!response.ok) {
      const error = new Error(payload?.message || '请求失败，请重试');
      error.code = payload?.error;
      error.status = response.status;
      throw error;
    }
    return payload;
  }
  const typeTag = (type) => `<span class="type-tag" style="--c:${TYPE_COLOR[type] || 'var(--mcode-text-subtle)'}">${esc(TYPES[type] || type || '未建页面')}</span>`;
  const fmtSize = (bytes) => bytes >= 1048576 ? (bytes / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(bytes / 1024)) + ' KB';
  const fmtTime = (iso) => { const d = new Date(iso); return Number.isNaN(d.getTime()) ? '' : d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' }); };
  const resolveName = (name) => ws.names.get(nameKey(name)) ?? null;
  const report = () => { if (typeof reportViewState === 'function') reportViewState(); };
  const FILE_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/></svg>';
  const LINK_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>';
  const CLIP_ICON = '<svg class="folder-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 5h16v14H4z"/><path d="M8 9h8M8 13h8M8 17h5"/></svg>';
  const DIRECTIONS = { improve: ['改善', '▲'], weaken: ['走弱', '▼'], unclear: ['待判断', '·'] };
  const shortName = (path) => String(path ?? '').split('/').pop() || String(path ?? '');
  const hostOf = (url) => { try { return new URL(url).hostname.replace(/^www\./, ''); } catch { return String(url); } };
  /** 出处按钮：文件用默认应用打开，链接用默认浏览器打开，找不到文件的只显示文字。 */
  function refChip(ref, { full = false } = {}) {
    if (!ref) return '';
    const locator = ref.locator ? ' · ' + ref.locator : '';
    if (ref.kind === 'file') return `<button type="button" class="ref-chip file" data-ref-kind="file" data-ref-key="${esc(ref.key)}" title="用默认应用打开：${esc(ref.display)}">${FILE_ICON}<span>${esc(full ? ref.label : shortName(ref.display) + locator)}</span></button>`;
    if (ref.kind === 'url') return `<button type="button" class="ref-chip url" data-ref-kind="url" data-ref-url="${esc(ref.url)}" title="在默认浏览器打开：${esc(ref.url)}">${LINK_ICON}<span>${esc(ref.label && ref.label !== ref.url ? ref.label : hostOf(ref.url))}</span></button>`;
    return `<span class="ref-chip text" title="资料库里没有找到对应的文件">${esc(ref.label)}</span>`;
  }
  function dirTag(direction) {
    const [label, mark] = DIRECTIONS[direction] ?? DIRECTIONS.unclear;
    return `<span class="dir-tag ${esc(DIRECTIONS[direction] ? direction : 'unclear')}" title="Agent 依据资料做的判断"><i aria-hidden="true">${mark}</i>${label}</span>`;
  }
  function recordItem(record, { entity = false } = {}) {
    const delta = record.from || record.to ? `<span class="change-delta-inline">${esc(record.from || '—')} → ${esc(record.to || '—')}</span>` : '';
    const tags = record.kind === 'change' ? `<span class="dim-tag">${esc(record.dimension ?? '其他')}</span>${dirTag(record.direction)}` : '<span class="kind-tag">动态</span>';
    const who = entity ? `<button type="button" class="record-entity" data-open-page="${esc(record.entityId ?? record.entity)}" title="在知识图谱中查看">${esc(record.entity)}</button>` : '';
    return `<li class="record-item ${record.kind === 'change' ? 'change' : 'update'}"><div class="record-meta"><time datetime="${esc(record.date)}">${esc(record.date)}</time>${who}${tags}</div><p>${esc(record.text)}${delta ? ' ' + delta : ''}</p><div class="change-sources">${(record.sources ?? []).map((ref) => refChip(ref)).join('')}</div></li>`;
  }
  let toastTimer = 0;
  function toast(message, isError = false, duration = isError ? 5000 : 2600) {
    const el = $('wiki-toast');
    if (!el) return;
    el.textContent = message;
    el.dataset.tone = isError ? 'danger' : '';
    el.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => { el.hidden = true; }, duration);
  }
  async function openExternal(body, fallbackUrl) {
    try {
      await api('/api/wiki/open', { method: 'POST', body: JSON.stringify(body) });
      toast(body.url ? '已在默认浏览器打开' : body.target === 'wiki' ? '已打开知识库文件夹' : '已用默认应用打开');
    } catch (error) {
      if (fallbackUrl) window.open(fallbackUrl, '_blank', 'noopener');
      else toast(error.message, true);
    }
  }
  // 出处按钮在捕获阶段处理，避免同时触发外层的选中节点等点击逻辑。
  document.addEventListener('click', (event) => {
    const target = event.target.closest('[data-ref-kind]');
    if (!target) return;
    event.preventDefault();
    event.stopPropagation();
    if (target.dataset.refKind === 'url') void openExternal({ url: target.dataset.refUrl }, target.dataset.refUrl);
    else if (target.dataset.refKind === 'file') void openExternal({ key: target.dataset.refKey });
  }, true);


  // ---------- 页面切换 ----------
  function showPage(page) {
    const previous = ws.page;
    ws.page = page === 'assets' || page === 'sources' ? page : 'market';
    $('market-main').hidden = ws.page !== 'market';
    root.hidden = ws.page !== 'assets';
    if ($('sources-main')) $('sources-main').hidden = ws.page !== 'sources';
    if (previous !== ws.page) window.scrollTo?.({ top: 0 });
    document.querySelectorAll('[data-app-page]').forEach((button) => {
      if (button.dataset.appPage === ws.page) button.setAttribute('aria-current', 'page');
      else button.removeAttribute('aria-current');
    });
    store.set('market.page', ws.page);
    if (ws.page === 'assets') { ensureAssetsLoaded(); showAssetTab(ws.tab, { quiet: true }); }
    else if (ws.page === 'sources') window.stockSources?.show();
    else {
      if (typeof scheduleChart === 'function') scheduleChart();
      // 从其他页面回到行情页：股票在别处切换过时补取一次「最新」和「纪要」。
      if (typeof state !== 'undefined' && state.snapshot && state.snapshot.symbol !== feed.symbol) loadFeed(state.snapshot);
    }
    report();
  }
  document.querySelectorAll('[data-app-page]').forEach((button) => button.addEventListener('click', () => showPage(button.dataset.appPage)));
  document.addEventListener('click', (event) => {
    const link = event.target.closest('[data-goto-page]');
    if (!link) return;
    event.preventDefault();
    if ($('detail-dialog')?.open) $('detail-dialog').close();
    showPage(link.dataset.gotoPage);
    if (link.dataset.gotoTab) showAssetTab(link.dataset.gotoTab);
  });

  function showAssetTab(tab, { quiet = false } = {}) {
    ws.tab = ASSET_TABS.some((item) => item.id === tab) ? tab : ASSET_TABS[0].id;
    store.set('assets.tab', ws.tab);
    for (const item of ASSET_TABS) {
      const button = $('asset-tab-' + item.id);
      const selected = item.id === ws.tab;
      button.setAttribute('aria-selected', String(selected));
      button.tabIndex = selected ? 0 : -1;
      $('asset-panel-' + item.id).hidden = !selected;
    }
    if (ws.tab === 'graph' && ws.graph) { renderCanvas(); requestAnimationFrame(redrawCanvasOverlays); }
    if (ws.tab === 'changes') { if (!cw.loaded) { cw.loaded = true; void loadChanges(); } else renderChanges(); }
    if (ws.status) renderJob();
    if (!quiet) report();
  }
  root.querySelector('.asset-tabs').addEventListener('click', (event) => {
    const button = event.target.closest('[data-asset-tab]');
    if (button) showAssetTab(button.dataset.assetTab);
  });
  root.querySelector('.asset-tabs').addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    const index = ASSET_TABS.findIndex((item) => item.id === ws.tab);
    const next = ASSET_TABS[(index + (event.key === 'ArrowRight' ? 1 : ASSET_TABS.length - 1)) % ASSET_TABS.length];
    showAssetTab(next.id);
    $('asset-tab-' + next.id).focus();
  });
  $('symbol-form').addEventListener('submit', () => { if (ws.page !== 'market') showPage('market'); });
  $('search-results').addEventListener('click', (event) => { if (event.target.closest('[data-pick-symbol]')) showPage('market'); });
  $('watchlist-list').addEventListener('click', (event) => { if (event.target.closest('[data-watch-symbol]') && !event.target.closest('[data-remove-symbol]')) showPage('market'); });

  function ensureAssetsLoaded() {
    if (ws.loaded) return;
    ws.loaded = true;
    renderDetail();
    void Promise.allSettled([loadStatus(), loadFiles(), loadGraph(), loadSessionDir()]);
  }

  // ---------- 数据 ----------
  async function loadStatus() {
    try {
      ws.status = await api('/api/wiki/status');
      renderStatus();
    } catch (error) {
      $('wiki-summary').textContent = '资料库暂时无法读取：' + error.message;
    }
  }
  async function loadFiles(refresh = false) {
    try {
      ws.files = await api('/api/wiki/files' + (refresh ? '?refresh=1' : ''));
      renderFiles();
      renderFolders();
    } catch (error) {
      $('file-list').innerHTML = `<tr><td colspan="5" class="list-state error-text" role="alert">资料文件暂时无法读取：${esc(error.message)}</td></tr>`;
    }
  }
  async function loadGraph() {
    try {
      const graph = await api('/api/wiki/graph');
      ws.graph = graph;
      ws.byId = new Map(graph.pages.map((page) => [page.id, page]));
      for (const ghost of graph.ghosts) ws.byId.set(ghost.id, { ...ghost, type: null, relations: [] });
      ws.names = new Map();
      for (const page of graph.pages) ws.names.set(nameKey(page.title), page.id);
      for (const page of graph.pages) for (const alias of page.aliases || []) if (!ws.names.has(nameKey(alias))) ws.names.set(nameKey(alias), page.id);
      if (ws.selected && !ws.byId.has(ws.selected)) { ws.selected = null; ws.detail = null; renderDetail(); }
      renderIndustryOptions();
      renderCanvas();
      if (ws.selected) loadDetail(ws.selected, { quiet: true });
    } catch (error) {
      showCanvasState('知识图谱暂时无法读取：' + error.message, true);
    }
  }
  async function loadSessionDir() {
    if (typeof agentApi?.session !== 'function') return;
    try {
      const session = await Promise.race([agentApi.session(), new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000))]);
      if (session && typeof session.workspaceDir === 'string' && session.workspaceDir) { ws.sessionDir = session.workspaceDir; renderFolders(); }
    } catch {}
  }

  // ---------- 概况、后台任务与自动整理 ----------
  const ACTIVE_JOB = ['queued', 'running', 'approval'];
  const jobSubject = (job) => (job.kind === 'stock' ? '归集「' + (job.stock?.title ?? '') + '」的资料' : job.kind === 'scan' ? '扫描舆情' : '整理资料');
  const fmtClock = (iso) => { const d = new Date(iso); return Number.isNaN(d.getTime()) ? '' : d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }); };
  function renderStatus() {
    const s = ws.status;
    if (!s) return;
    $('wiki-summary').textContent = '';
    const meta = [];
    // 没有节点时由画布里的引导文案说明下一步，头部只留知识库位置，避免同一句话出现两次。
    if (s.pages) {
      meta.push(s.pages + ' 个节点', s.relations + ' 条关系');
      if (s.pendingRelations) meta.push(s.pendingRelations + ' 条待核');
    }
    meta.push('知识库只有一份，固定保存在 Mini App 数据目录');
    $('wiki-open-folder').hidden = !s.openSupported;
    $('wiki-open-folder').title = s.wiki?.path ?? '';
    $('graph-meta').textContent = meta.join(' · ');
    $('tab-count-graph').textContent = s.pages ? String(s.pages) : '';
    $('tab-count-files').textContent = s.files?.total ? String(s.files.total) : '';
    $('tab-count-changes').textContent = s.records?.changes ? String(s.records.changes) : '';
    renderAuto();
    renderScanButton();
    renderFolders();
    renderJob();
    renderChip();
    renderPicker();
    renderNotice();
    handleJobTransitions();
    renderLatest();
    if (ws.files) renderFiles();
    if (!ws.detail) renderDetail();
    // 图谱可能先于状态返回：空图谱的引导文案依赖文件夹和待整理数量，状态到达后再刷新一次。
    if (ws.graph && !ws.graph.pages.length) renderCanvas();
  }

  /** 资产页右上角：自动整理的状态和开关（暂停 / 继续 / 出错后立即重试）。 */
  function renderAuto() {
    const el = $('auto-control');
    const s = ws.status;
    if (!el || !s) return;
    const auto = s.auto ?? {};
    let text = '';
    let action = '';
    if (!auto.available) text = '当前版本不支持后台自动整理（需要 MiniMax Code 3.1.2+）';
    else if (!auto.enabled) { text = '自动整理已暂停'; action = '<button type="button" class="link-btn" data-auto="on">继续</button>'; }
    else if (auto.retryAt) { text = '上次整理没有完成，' + fmtClock(auto.retryAt) + ' 自动重试'; action = '<button type="button" class="link-btn" data-auto="retry">立即重试</button><button type="button" class="link-btn" data-auto="off">暂停</button>'; }
    else { text = '自动整理已开启'; action = '<button type="button" class="link-btn" data-auto="off">暂停</button>'; }
    const on = Boolean(auto.available && auto.enabled && !auto.retryAt);
    el.innerHTML = '<span class="auto-dot' + (on ? ' on' : '') + '" aria-hidden="true"></span><span>' + esc(text) + '</span>' + action;
  }
  $('auto-control').addEventListener('click', async (event) => {
    const button = event.target.closest('[data-auto]');
    if (!button) return;
    button.disabled = true;
    try {
      await api('/api/wiki/auto', { method: 'PUT', body: JSON.stringify({ enabled: button.dataset.auto !== 'off' }) });
      toast(button.dataset.auto === 'off' ? '自动整理已暂停' : '自动整理已开启，后台会接着整理');
      await loadStatus();
    } catch (error) {
      toast(error.message, true);
      button.disabled = false;
    }
  });

  /** 资产页的任务条：只在任务进行中、或上次任务出错还没关掉时显示，一行；完成用提示条通知。 */
  function renderJob() {
    const panel = $('wiki-job');
    const job = ws.status?.job;
    const active = Boolean(job && ACTIVE_JOB.includes(job.status));
    clearTimeout(ws.statusPoll);
    // 兜底：SSE 被代理缓冲或页面被节流时，任务进行中每 5 秒刷新一次状态（所有页面都需要：顶栏标签、授权弹窗）。
    if (active) ws.statusPoll = setTimeout(loadStatus, 5000);
    const showError = Boolean(job && job.status === 'error' && store.get('wiki.job.dismissed') !== job.id);
    if (!job || (!active && !showError)) { panel.hidden = true; panel.innerHTML = ''; return; }
    const done = job.ingested + job.skipped + job.failed;
    const canOpen = Boolean(job.sessionId && typeof agentApi?.open === 'function');
    const title = active
      ? (job.status === 'approval' ? '等待你授权 · ' : job.status === 'queued' ? '排队中 · ' : '') + (job.auto ? '后台正在自动' : '后台正在') + jobSubject(job)
      : jobSubject(job) + '没有完成';
    panel.hidden = false;
    panel.dataset.tone = active ? (job.status === 'approval' ? 'warning' : 'accent') : 'danger';
    panel.innerHTML = `<span class="job-dot" aria-hidden="true"></span>
      <div class="job-text"><strong>${esc(title)}</strong><span>${esc(active ? job.step || '' : job.error || '')}</span></div>
      ${active ? `<span class="job-count">${done}/${job.total} ${job.kind === 'scan' ? '条舆情' : '份资料'}${job.records ? ' · ' + job.records + ' 条记录' : ''}</span>` : ''}
      <div class="job-actions">
        ${job.status === 'approval' ? '<button type="button" class="link-btn" data-job-action="permission">去授权</button>' : ''}
        ${canOpen ? '<button type="button" class="link-btn" data-job-action="open">查看过程</button>' : ''}
        ${active ? '<button type="button" class="link-btn danger" data-job-action="cancel">停止</button>' : '<button type="button" class="link-btn" data-job-action="dismiss">知道了</button>'}
      </div>`;
  }
  $('wiki-job').addEventListener('click', async (event) => {
    const job = ws.status?.job;
    const action = event.target.closest('[data-job-action]')?.dataset.jobAction;
    if (!job || !action) return;
    try {
      if (action === 'open') await agentApi.open(job.sessionId);
      else if (action === 'permission') openPermission(job, true);
      else if (action === 'cancel') {
        await api('/api/wiki/jobs/' + job.id + '/cancel', { method: 'POST', body: '{}' });
        toast('已停止，自动整理已暂停；可以在资产页右上角继续');
        await loadStatus();
      } else if (action === 'dismiss') { store.set('wiki.job.dismissed', job.id); renderJob(); }
    } catch (error) {
      toast(action === 'open' ? '无法在侧栏打开后台会话（需要在对话里打开股市）' : error.message, true);
    }
  });

  /** 顶栏小标签：任何页面都能看到后台在整理什么；等待授权时点它打开授权弹窗。 */
  function renderChip() {
    const chip = $('organize-chip');
    if (!chip) return;
    const job = ws.status?.job;
    const active = Boolean(job && ACTIVE_JOB.includes(job.status));
    chip.hidden = !active;
    if (!active) return;
    const done = job.ingested + job.skipped + job.failed;
    chip.dataset.tone = job.status === 'approval' ? 'warning' : '';
    chip.textContent = job.status === 'approval' ? '后台整理等待授权' : (job.kind === 'scan' ? '扫描舆情 ' : '整理资料 ') + done + '/' + job.total;
    chip.title = job.status === 'approval' ? '点这里查看授权请求' : '后台正在' + jobSubject(job) + '：' + (job.step || '') + '。点这里查看';
  }
  $('organize-chip')?.addEventListener('click', () => {
    const job = ws.status?.job;
    if (job?.status === 'approval') openPermission(job, true);
    else showPage('assets');
  });

  // 需要人处理的事情用小弹窗：授权请求、Agent 停下来提问。
  function openPermission(job, force = false) {
    const dialog = $('permission-dialog');
    if (!dialog || !job?.permission) return;
    if (!force && ws.permissionShown === job.permission.requestId) return;
    ws.permissionShown = job.permission.requestId;
    ws.permissionJob = job.id;
    $('permission-subject').textContent = '后台正在' + jobSubject(job) + '，需要你允许这一步：';
    $('permission-tool').textContent = job.permission.toolName || '工具调用';
    $('permission-reason').textContent = job.permission.reason || '';
    $('permission-reason').hidden = !job.permission.reason;
    $('permission-input').textContent = job.permission.toolInput || '';
    $('permission-details').hidden = !job.permission.toolInput;
    $('permission-error').hidden = true;
    dialog.querySelectorAll('[data-permission]').forEach((button) => { button.disabled = false; });
    if (!dialog.open) dialog.showModal();
  }
  $('permission-dialog').addEventListener('click', async (event) => {
    if (event.target.closest('#permission-later')) { $('permission-dialog').close(); return; }
    const decision = event.target.closest('[data-permission]')?.dataset.permission;
    if (!decision || !ws.permissionJob) return;
    $('permission-dialog').querySelectorAll('[data-permission]').forEach((button) => { button.disabled = true; });
    try {
      await api('/api/wiki/jobs/' + ws.permissionJob + '/permission', { method: 'POST', body: JSON.stringify({ decision }) });
      $('permission-dialog').close();
      await loadStatus();
    } catch (error) {
      $('permission-error').textContent = error.message;
      $('permission-error').hidden = false;
      $('permission-dialog').querySelectorAll('[data-permission]').forEach((button) => { button.disabled = false; });
    }
  });
  let noticeAction = null;
  function openNotice(message, label, action) {
    $('notice-text').textContent = message;
    $('notice-action').textContent = label;
    noticeAction = action;
    if (!$('notice-dialog').open) $('notice-dialog').showModal();
  }
  $('notice-close').addEventListener('click', () => $('notice-dialog').close());
  $('notice-action').addEventListener('click', async () => {
    $('notice-dialog').close();
    try { await noticeAction?.(); } catch (error) { toast(error.message, true); }
  });

  /** 任务状态变化：等待授权弹窗；这次打开页面之后完成的任务用提示条告诉一声；需要回答问题的错误用弹窗。 */
  function handleJobTransitions() {
    const job = ws.status?.job;
    if (!job) return;
    if (job.status === 'approval' && job.permission) openPermission(job);
    if (!['done', 'error'].includes(job.status) || ws.toasted === job.id) return;
    ws.toasted = job.id;
    if (!job.finishedAt || Date.parse(job.finishedAt) < ws.bootAt) return;
    if (job.status === 'done') {
      const parts = job.kind === 'scan'
        ? ['扫描了 ' + job.ingested + ' 条舆情', job.records ? '新增 ' + job.records + ' 条边际变化' : '没有新的边际变化']
        : ['整理了 ' + job.ingested + ' 份资料', job.records ? '新增 ' + job.records + ' 条动态和变化' : '', job.pagesTouched ? '更新 ' + job.pagesTouched + ' 个节点' : ''];
      toast((job.kind === 'scan' ? '舆情扫描完成：' : '资料整理完成：') + parts.filter(Boolean).join('，'), false, 5000);
    } else if (/提了一个问题/.test(job.error || '') && job.sessionId && typeof agentApi?.open === 'function') {
      openNotice(job.error, '查看过程', () => agentApi.open(job.sessionId));
    } else {
      toast(jobSubject(job) + '没有完成：' + (job.error || ''), true);
    }
  }

  // ---------- 文件夹 ----------
  function renderFolders() {
    const folders = ws.status?.folders ?? [];
    const scanned = new Map((ws.files?.folders ?? []).map((folder) => [folder.id, folder]));
    $('folder-list').innerHTML = folders.length ? folders.map((folder) => {
      const files = scanned.get(folder.id)?.files ?? [];
      const pending = files.filter((file) => ['new', 'changed'].includes(file.status)).length;
      return `<li class="folder-card">
        <svg class="folder-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M3 7.5A1.5 1.5 0 0 1 4.5 6h4l2 2h9A1.5 1.5 0 0 1 21 9.5v8A1.5 1.5 0 0 1 19.5 19h-15A1.5 1.5 0 0 1 3 17.5z"/></svg>
        <div class="folder-main"><strong title="${esc(folder.path)}">${esc(folder.label)}</strong><small title="${esc(folder.path)}">${esc(folder.path)}</small>
          <span class="folder-tags"><span class="folder-count">${files.length} 份资料${pending ? ' · ' + pending + ' 份待整理' : ''}</span>${folder.exists ? '' : '<span class="tag danger">文件夹不存在</span>'}</span></div>
        <button type="button" class="icon-btn small" data-folder-remove="${esc(folder.id)}" aria-label="取消关联 ${esc(folder.label)}" title="取消关联（不删除文件）">${X}</button>
      </li>`;
    }).join('') + clipsCard() : '<li class="list-state">还没有关联文件夹。选一个放研报、纪要、笔记的文件夹就行，支持 PDF、Word、Excel、PPT、Markdown、文本和网页。</li>';
    const sessionButton = $('session-folder');
    const linked = ws.sessionDir && folders.some((folder) => folder.path === ws.sessionDir);
    sessionButton.hidden = !ws.sessionDir || linked;
    if (ws.sessionDir) sessionButton.textContent = '+ 关联当前对话文件夹 · ' + (ws.sessionDir.split('/').filter(Boolean).pop() || ws.sessionDir);
  }
  /** 从行情页存入的舆情：保存在知识库的 clips/，作为虚拟文件夹显示，不能取消关联。 */
  function clipsCard() {
    const clips = (ws.files?.folders ?? []).find((folder) => folder.virtual);
    if (!clips) return '';
    const pending = clips.files.filter((item) => ['new', 'changed'].includes(item.status)).length;
    return `<li class="folder-card virtual">${CLIP_ICON}<div class="folder-main"><strong>${esc(clips.label)}</strong><small title="${esc(clips.path)}">从行情页存入的舆情 · 保存在知识库里</small><span class="folder-tags"><span class="folder-count">${clips.files.length} 条${pending ? ' · ' + pending + ' 条待整理' : ''}</span></span></div><span aria-hidden="true"></span></li>`;
  }
  function folderError(message) { const el = $('folder-error'); el.textContent = message || ''; el.hidden = !message; }
  function renderPicker() {
    const button = $('folder-pick');
    const kind = ws.status?.picker;
    button.hidden = !kind;
    if (!button.dataset.busy) button.textContent = kind === 'finder' ? '在访达中选择文件夹…' : '选择文件夹…';
    // 没有系统选择框时，手动输入路径是唯一入口，直接展开。
    if (ws.status && !kind) { $('folder-form').hidden = false; $('folder-path-toggle').hidden = true; }
  }
  $('folder-path-toggle').addEventListener('click', () => {
    const form = $('folder-form');
    form.hidden = !form.hidden;
    $('folder-path-toggle').setAttribute('aria-expanded', String(!form.hidden));
    if (!form.hidden) $('folder-path').focus();
  });
  $('folder-pick').addEventListener('click', async () => {
    const button = $('folder-pick');
    folderError('');
    button.dataset.busy = '1';
    button.disabled = true;
    button.textContent = '请在弹出的窗口里选择文件夹…';
    try {
      const result = await api('/api/wiki/folders/pick', { method: 'POST', body: '{}' });
      if (!result.cancelled) await Promise.allSettled([loadStatus(), loadFiles(true), loadGraph()]);
    } catch (error) {
      folderError(error.message);
    } finally {
      delete button.dataset.busy;
      button.disabled = false;
      renderPicker();
    }
  });

  // ---------- 重复节点 ----------
  function renderNotice() {
    const el = $('wiki-notice');
    const count = ws.status?.duplicates ?? 0;
    el.hidden = !count;
    el.innerHTML = count ? `<span>发现 ${count} 组可能重复的公司节点（同一股票代码、全称与简称、以代码命名的页面等）。</span><button type="button" class="link-btn" id="dup-open">查看并合并</button>` : '';
  }
  $('wiki-notice').addEventListener('click', (event) => { if (event.target.closest('#dup-open')) openDuplicates(); });
  let dupGroups = [];
  async function openDuplicates() {
    $('dup-body').innerHTML = '<p class="detail-note" role="status">载入中…</p>';
    if (!$('dup-dialog').open) $('dup-dialog').showModal();
    try {
      dupGroups = (await api('/api/wiki/duplicates')).groups;
      renderDuplicates();
    } catch (error) {
      $('dup-body').innerHTML = `<p class="error-text" role="alert">${esc(error.message)}</p>`;
    }
  }
  function renderDuplicates() {
    $('dup-merge-high').disabled = !dupGroups.some((group) => group.confidence === 'high');
    $('dup-body').innerHTML = dupGroups.length ? dupGroups.map((group, index) => `
      <fieldset class="dup-group">
        <legend><span class="tag ${group.confidence === 'high' ? 'success' : 'warning'}">${group.confidence === 'high' ? '高置信度' : '需要确认'}</span><span>${esc(group.reasons.join('、'))}</span></legend>
        ${group.pages.map((page) => `<label class="dup-row"><input type="radio" name="dup-${index}" value="${esc(page.id)}" ${page.id === group.primary ? 'checked' : ''} /><span class="dup-title">${esc(page.title)}</span><small>${esc([TYPES[page.type] || page.type, page.tickers.join(' '), page.relations + ' 条关系', page.aliases.length ? '别名：' + page.aliases.slice(0, 4).join('、') : ''].filter(Boolean).join(' · '))}</small></label>`).join('')}
        <div class="dup-actions"><button type="button" class="btn small" data-dup-merge="${index}">保留选中的页面，合并其余</button></div>
      </fieldset>`).join('') : '<p class="detail-note">没有发现重复的公司节点。</p>';
  }
  async function afterMerge() {
    await Promise.allSettled([loadGraph(), loadStatus()]);
    dupGroups = (await api('/api/wiki/duplicates').catch(() => ({ groups: [] }))).groups;
    renderDuplicates();
  }
  $('dup-body').addEventListener('click', async (event) => {
    const button = event.target.closest('[data-dup-merge]');
    if (!button) return;
    const group = dupGroups[Number(button.dataset.dupMerge)];
    const into = $('dup-body').querySelector('input[name="dup-' + button.dataset.dupMerge + '"]:checked')?.value;
    if (!group || !into) return;
    button.disabled = true;
    try {
      await api('/api/wiki/merge', { method: 'POST', body: JSON.stringify({ into, from: group.pages.map((page) => page.id).filter((id) => id !== into) }) });
      await afterMerge();
    } catch (error) {
      button.disabled = false;
      button.insertAdjacentHTML('afterend', `<span class="error-text" role="alert">${esc(error.message)}</span>`);
    }
  });
  $('dup-merge-high').addEventListener('click', async () => {
    $('dup-merge-high').disabled = true;
    try { await api('/api/wiki/merge', { method: 'POST', body: JSON.stringify({ auto: 'high' }) }); await afterMerge(); }
    catch (error) { $('dup-body').insertAdjacentHTML('afterbegin', `<p class="error-text" role="alert">${esc(error.message)}</p>`); }
  });
  $('dup-close').addEventListener('click', () => $('dup-dialog').close());
  $('dup-done').addEventListener('click', () => $('dup-dialog').close());
  async function addFolder(path, fromSession = false) {
    folderError('');
    try {
      await api('/api/wiki/folders', { method: 'POST', body: JSON.stringify({ path, fromSession }) });
      $('folder-path').value = '';
      await Promise.allSettled([loadStatus(), loadFiles(true), loadGraph()]);
    } catch (error) { folderError(error.message); }
  }
  $('folder-form').addEventListener('submit', (event) => { event.preventDefault(); const value = $('folder-path').value.trim(); if (value) addFolder(value); });
  $('session-folder').addEventListener('click', () => { if (ws.sessionDir) addFolder(ws.sessionDir, true); });
  $('folder-list').addEventListener('click', async (event) => {
    const remove = event.target.closest('[data-folder-remove]');
    folderError('');
    try {
      if (remove) {
        if (remove.dataset.confirm !== 'true') {
          remove.dataset.confirm = 'true';
          remove.classList.add('confirm');
          remove.setAttribute('aria-label', '再点一次确认取消关联（不会删除文件）');
          remove.title = '再点一次确认（不会删除文件）';
          setTimeout(() => { if (remove.isConnected) { remove.dataset.confirm = ''; remove.classList.remove('confirm'); remove.title = '取消关联（不删除文件）'; } }, 3500);
          return;
        }
        await api('/api/wiki/folders/' + enc(remove.dataset.folderRemove), { method: 'DELETE' });
        await Promise.allSettled([loadStatus(), loadFiles(true), loadGraph()]);
      }
    } catch (error) { folderError(error.message); }
  });

  // ---------- 文件 ----------
  const PENDING_STATUS = ['new', 'changed', 'queued'];
  function visibleFiles() {
    const folders = ws.files?.folders ?? [];
    const query = nameKey(ws.fileSearch);
    const base = folders
      .filter((folder) => ws.fileFolder === 'all' || folder.id === ws.fileFolder)
      .flatMap((folder) => folder.files.map((file) => ({ ...file, folder })))
      .filter((file) => !query || nameKey(file.rel).includes(query) || (file.stocks ?? []).some((stock) => nameKey(stock.name).includes(query)));
    const groups = {
      all: base,
      pending: base.filter((file) => PENDING_STATUS.includes(file.status)),
      ingested: base.filter((file) => ['ingested', 'skipped'].includes(file.status)),
    };
    return { folders, groups, list: groups[ws.fileFilter] ?? base };
  }
  function renderFiles() {
    const { folders, groups, list } = visibleFiles();
    for (const key of Object.keys(groups)) $('ff-' + key).textContent = groups[key].length;
    const options = '<option value="all">全部文件夹</option>' + folders.map((folder) => `<option value="${esc(folder.id)}">${esc(folder.label)}</option>`).join('');
    if ($('files-folder').innerHTML !== options) $('files-folder').innerHTML = options;
    if (ws.fileFolder !== 'all' && !folders.some((folder) => folder.id === ws.fileFolder)) ws.fileFolder = 'all';
    $('files-folder').value = ws.fileFolder;
    $('files-folder').hidden = folders.length < 2;
    const total = folders.reduce((sum, folder) => sum + folder.files.length, 0);
    const pendingAll = folders.reduce((sum, folder) => sum + folder.files.filter((file) => PENDING_STATUS.includes(file.status)).length, 0);
    const truncated = folders.some((folder) => folder.truncated);
    const auto = ws.status?.auto;
    const job = ws.status?.job;
    const organizing = Boolean(job && ACTIVE_JOB.includes(job.status) && job.kind !== 'scan');
    const pendingText = !pendingAll ? '都已整理进知识图谱'
      : organizing ? '后台正在整理，还剩 ' + pendingAll + ' 份'
      : auto && auto.available && auto.enabled ? pendingAll + ' 份等后台自动整理'
      : pendingAll + ' 份待整理（自动整理' + (auto?.available ? '已暂停' : '不可用') + '）';
    $('files-sub').textContent = folders.length ? '共 ' + total + ' 份 · ' + pendingText + (truncated ? ' · 文件夹内容过多，只扫描了前 3000 个文件' : '') : '支持 PDF、Word、Excel、PPT、Markdown、文本和网页';
    // 还没有关联文件夹时只留「关联文件夹」一块，资料文件表格等有了文件夹再出现。
    $('files-title').closest('.panel').hidden = !folders.length;
    const row = (text) => `<tr><td colspan="5" class="list-state">${text}</td></tr>`;
    if (!folders.length) { $('file-list').innerHTML = row('关联文件夹后，这里列出其中的资料文件。'); return; }
    if (!list.length) {
      $('file-list').innerHTML = row(ws.fileSearch ? '没有匹配的文件。' : ws.fileFilter === 'pending' ? (total ? '没有待整理的文件，资料都已整理进知识图谱。' : '文件夹里还没有可整理的资料文件。') : '暂无文件。');
      return;
    }
    const shown = list.slice(0, 300);
    $('file-list').innerHTML = shown.map((file) => {
      const [label, tone] = STATUS_TAG[file.status] || [file.status, 'muted'];
      const name = file.rel.split('/').pop();
      const dir = file.rel.includes('/') ? file.rel.slice(0, file.rel.lastIndexOf('/')) : '';
      const summary = file.summaryPage ? resolveName(file.summaryPage) : null;
      const stocks = (file.stocks ?? []).slice(0, 4).map((stock) => `<button type="button" class="mini-tag${stock.relevance === 'core' ? ' core' : ''}${stock.by === 'agent' ? ' agent' : ''}" data-open-page="${esc(stock.name)}" title="${stock.by === 'agent' ? 'Agent 读过后标注 · ' : ''}在知识图谱中查看 ${esc(stock.name)}（${esc(stock.symbol)}）">${esc(stock.name)}</button>`).join('');
      const nameCell = summary
        ? `<button type="button" class="file-name link" data-open-page="${esc(summary)}" title="在知识图谱中查看这份资料的摘要">${esc(name)}</button>`
        : `<span class="file-name" title="${esc(file.rel)}">${esc(name)}</span>`;
      const docBadge = file.docType && file.docType !== '舆情' && (file.docType === '纪要' || file.docTypeBy === 'agent') ? `<span class="doc-badge" title="${file.docTypeBy === 'agent' ? 'Agent 读过后标注' : '按文件名识别'}">${esc(file.docType)}</span>` : '';
      return `<tr class="files-row">
        <td class="col-name"><div class="file-cell"><span class="file-kind">${esc(file.kind)}</span><span class="file-main">${nameCell}<small title="${esc(file.folder.path + '/' + file.rel)}">${esc(file.folder.label + (dir ? '/' + dir : ''))}${file.note ? ' · ' + esc(file.note) : ''}</small></span>${docBadge}<button type="button" class="icon-btn small file-open" data-ref-kind="file" data-ref-key="${esc(file.key)}" aria-label="用默认应用打开 ${esc(name)}" title="用默认应用打开">${LINK_ICON}</button></div></td>
        <td class="col-status"><span class="tag ${tone}">${label}</span></td>
        <td class="col-stocks">${stocks ? `<div class="stock-tags">${stocks}</div>` : '<span class="hint">—</span>'}</td>
        <td class="col-num">${fmtSize(file.size)}</td>
        <td class="col-time">${file.mtimeMs ? esc(fmtTime(new Date(file.mtimeMs).toISOString())) : ''}</td>
      </tr>`;
    }).join('') + (list.length > shown.length ? row('还有 ' + (list.length - shown.length) + ' 个文件未显示，可以用搜索或文件夹筛选缩小范围') : '');
  }
  $('files-folder').addEventListener('change', () => { ws.fileFolder = $('files-folder').value; renderFiles(); });
  $('files-search').addEventListener('input', () => { ws.fileSearch = $('files-search').value.trim(); renderFiles(); });
  document.querySelectorAll('[data-file-filter]').forEach((button) => button.addEventListener('click', () => {
    ws.fileFilter = button.dataset.fileFilter;
    document.querySelectorAll('[data-file-filter]').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    renderFiles();
  }));
  $('files-refresh').addEventListener('click', async () => {
    $('files-refresh').setAttribute('aria-busy', 'true');
    try { await api('/api/wiki/reload', { method: 'POST', body: '{}' }); } catch {}
    await Promise.allSettled([loadFiles(true), loadStatus(), loadGraph()]);
    $('files-refresh').setAttribute('aria-busy', 'false');
  });
  $('file-list').addEventListener('click', (event) => { const target = event.target.closest('[data-open-page]'); if (target) openPage(target.dataset.openPage); });

  // ---------- 视角编辑 ----------
  let lensDraft = null;
  let lensSelected = null;
  async function openLenses() {
    $('lens-error').hidden = true;
    try {
      ws.lenses = await api('/api/wiki/lenses');
    } catch (error) {
      $('lens-error').textContent = error.message;
      $('lens-error').hidden = false;
    }
    lensDraft = ws.lenses ? { purpose: ws.lenses.purpose, lenses: ws.lenses.lenses.map((lens) => ({ ...lens })) } : { purpose: '', lenses: [] };
    lensSelected = lensDraft.lenses[0]?.id ?? null;
    $('lens-purpose').value = lensDraft.purpose || '';
    renderLensList();
    renderLensEditor();
    $('lens-dialog').showModal();
  }
  function currentLens() { return lensDraft?.lenses.find((lens) => lens.id === lensSelected) ?? null; }
  function isLensModified(lens) {
    const base = ws.lenses?.defaults?.[lens.id];
    return Boolean(base && (base.prompt !== lens.prompt || base.name !== lens.name));
  }
  function renderLensList() {
    $('lens-list').innerHTML = lensDraft.lenses.map((lens) => `
      <li class="lens-item${lens.id === lensSelected ? ' selected' : ''}">
        <input type="checkbox" data-lens-toggle="${esc(lens.id)}" ${lens.enabled ? 'checked' : ''} aria-label="启用 ${esc(lens.name)}" />
        <button type="button" data-lens-pick="${esc(lens.id)}" aria-current="${lens.id === lensSelected}"><span>${esc(lens.name || '未命名视角')}</span><small>${lens.builtin ? (isLensModified(lens) ? '内置 · 已修改' : '内置') : '自定义'}</small></button>
      </li>`).join('');
  }
  function renderLensEditor() {
    const lens = currentLens();
    for (const id of ['lens-name', 'lens-prompt']) $(id).disabled = !lens;
    $('lens-name').value = lens?.name ?? '';
    $('lens-prompt').value = lens?.prompt ?? '';
    $('lens-reset').hidden = !lens?.builtin;
    $('lens-reset').disabled = !lens || !isLensModified(lens);
    $('lens-delete').hidden = !lens || lens.builtin;
    $('lens-meta').textContent = lens ? lens.prompt.length + ' / 6000 字' : '';
  }
  $('wiki-open-folder').addEventListener('click', () => { void openExternal({ target: 'wiki' }); });
  $('lens-open').addEventListener('click', openLenses);
  $('lens-list').addEventListener('click', (event) => {
    const pick = event.target.closest('[data-lens-pick]');
    if (pick) { lensSelected = pick.dataset.lensPick; renderLensList(); renderLensEditor(); }
  });
  $('lens-list').addEventListener('change', (event) => {
    const toggle = event.target.closest('[data-lens-toggle]');
    const lens = lensDraft?.lenses.find((item) => item.id === toggle?.dataset.lensToggle);
    if (lens) lens.enabled = toggle.checked;
  });
  $('lens-name').addEventListener('input', () => { const lens = currentLens(); if (lens) { lens.name = $('lens-name').value; renderLensList(); $('lens-reset').disabled = !isLensModified(lens); } });
  $('lens-prompt').addEventListener('input', () => { const lens = currentLens(); if (lens) { lens.prompt = $('lens-prompt').value; $('lens-meta').textContent = lens.prompt.length + ' / 6000 字'; $('lens-reset').disabled = !isLensModified(lens); } });
  $('lens-reset').addEventListener('click', () => {
    const lens = currentLens();
    const base = lens && ws.lenses?.defaults?.[lens.id];
    if (!base) return;
    lens.name = base.name;
    lens.prompt = base.prompt;
    renderLensList();
    renderLensEditor();
  });
  $('lens-delete').addEventListener('click', () => {
    const lens = currentLens();
    if (!lens || lens.builtin) return;
    lensDraft.lenses = lensDraft.lenses.filter((item) => item.id !== lens.id);
    lensSelected = lensDraft.lenses[0]?.id ?? null;
    renderLensList();
    renderLensEditor();
  });
  $('lens-add').addEventListener('click', () => {
    if (lensDraft.lenses.length >= 12) { $('lens-error').textContent = '最多 12 个视角'; $('lens-error').hidden = false; return; }
    const id = 'custom-' + Date.now().toString(36);
    lensDraft.lenses.push({ id, name: '新视角', prompt: '从……视角整理资料：\n- \n- ', enabled: true, builtin: false });
    lensSelected = id;
    renderLensList();
    renderLensEditor();
    $('lens-name').focus();
    $('lens-name').select();
  });
  const closeLenses = () => $('lens-dialog').close();
  $('lens-close').addEventListener('click', closeLenses);
  $('lens-cancel').addEventListener('click', closeLenses);
  $('lens-save').addEventListener('click', async () => {
    $('lens-error').hidden = true;
    $('lens-save').disabled = true;
    try {
      ws.lenses = await api('/api/wiki/lenses', { method: 'PUT', body: JSON.stringify({ purpose: $('lens-purpose').value, lenses: lensDraft.lenses.map(({ id, name, prompt, enabled }) => ({ id, name, prompt, enabled })) }) });
      closeLenses();
      loadStatus();
    } catch (error) {
      $('lens-error').textContent = error.message;
      $('lens-error').hidden = false;
    } finally {
      $('lens-save').disabled = false;
    }
  });

  // ---------- 画布 ----------
  function showCanvasState(message, isError = false, action = null) {
    const el = $('canvas-state');
    el.hidden = !message;
    el.innerHTML = message ? `<p class="${isError ? 'error-text' : ''}">${esc(message)}</p>${action ? `<button type="button" class="btn small" data-goto-page="assets" data-goto-tab="${esc(action.tab)}">${esc(action.label)}</button>` : ''}` : '';
    el.setAttribute('role', isError ? 'alert' : 'status');
  }
  function industryOf(page) { return page.industry || (page.type === 'industry' ? page.title : null); }
  function industryList() {
    const counts = new Map();
    for (const page of ws.graph?.pages ?? []) {
      const name = industryOf(page);
      if (!name) continue;
      const key = nameKey(name);
      const entry = counts.get(key) ?? { name, count: 0 };
      entry.count += 1;
      if (page.type === 'industry') entry.name = page.title;
      counts.set(key, entry);
    }
    return [...counts.values()].sort((a, b) => b.count - a.count || a.name.localeCompare(b.name, 'zh-CN'));
  }
  function renderIndustryOptions() {
    const list = industryList();
    // 节点上的 industry 写法可能和行业页标题略有出入：统一成列表里的规范名称，下拉框才能选中。
    const canonical = (value) => list.find((item) => nameKey(item.name) === nameKey(value))?.name ?? null;
    if (ws.industry !== 'all') ws.industry = canonical(ws.industry) ?? 'all';
    if (ws.chainIndustry !== 'all') ws.chainIndustry = canonical(ws.chainIndustry) ?? (list[0]?.name ?? 'all');
    const options = '<option value="all">全部行业</option>' + list.map((item) => `<option value="${esc(item.name)}">${esc(item.name)}（${item.count}）</option>`).join('');
    $('industry-select').innerHTML = options;
    $('industry-select').value = ws.industry;
    $('industry-select').disabled = !list.length;
    // 面包屑里的行业下拉不带节点数，读起来是「知识图谱 / 光通信 / 产业链」。
    $('chain-industry').innerHTML = '<option value="all">全部行业</option>' + list.map((item) => `<option value="${esc(item.name)}">${esc(item.name)}</option>`).join('');
    $('chain-industry').value = ws.chainIndustry;
  }
  $('industry-select').addEventListener('change', () => { ws.industry = $('industry-select').value; ws.userViewport = false; renderCanvas(); report(); });
  $('chain-industry').addEventListener('change', () => { ws.chainIndustry = $('chain-industry').value; renderCanvas(); report(); });

  /** 产业链是知识图谱的下钻视图：从行业节点、节点详情或行业筛选进入，面包屑返回图谱。 */
  function chainIndustryKeys() {
    const keys = new Set();
    for (const page of ws.graph?.pages ?? []) if (page.chain && industryOf(page)) keys.add(nameKey(industryOf(page)));
    return keys;
  }
  /** 「查看产业链」去哪个行业：图谱按行业筛选时用该行业；否则用选中节点所属的行业；再否则用节点最多、且标注了上中下游的行业。 */
  function chainTargetIndustry() {
    if (ws.industry !== 'all') return ws.industry;
    const keys = chainIndustryKeys();
    const selected = ws.selected ? ws.byId.get(ws.selected) : null;
    const own = selected ? industryOf(selected) : null;
    if (own && keys.has(nameKey(own))) return own;
    const list = industryList();
    return (list.find((item) => keys.has(nameKey(item.name))) ?? list[0])?.name ?? 'all';
  }
  function syncChainEnter() {
    const button = $('chain-enter');
    const available = ws.mode === 'graph' && Boolean(ws.graph?.pages?.some((page) => page.chain));
    button.hidden = !available;
    if (!available) return;
    const target = chainTargetIndustry();
    button.textContent = target === 'all' ? '查看产业链' : '查看「' + target + '」产业链';
  }
  function enterChain(industry, focusId) {
    ws.mode = 'chain';
    ws.chainIndustry = industry || chainTargetIndustry();
    renderIndustryOptions();
    renderCanvas();
    report();
    if (focusId) { ws.selected = focusId; markSelection(); }
    // 入口按钮（工具栏 / 详情）切换后会被隐藏或重绘：焦点移到产业链里选中的节点，没有就移到面包屑。
    requestAnimationFrame(() => {
      drawChainEdges();
      const target = document.querySelector('#chain-view [data-selected]');
      target?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
      const focusable = target ? (target.matches('button') ? target : target.querySelector('button')) : null;
      (focusable ?? $('chain-back')).focus({ preventScroll: true });
    });
  }
  function exitChain() {
    ws.mode = 'graph';
    renderCanvas();
    report();
    ($('chain-enter').hidden ? $('wiki-search') : $('chain-enter')).focus({ preventScroll: true });
  }
  $('chain-enter').addEventListener('click', () => enterChain(chainTargetIndustry(), ws.selected));
  $('chain-back').addEventListener('click', exitChain);
  root.querySelector('.wiki-canvas').addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && ws.mode === 'chain' && !document.querySelector('dialog[open]')) { event.preventDefault(); exitChain(); }
  });
  $('wiki-search').addEventListener('input', () => { ws.query = $('wiki-search').value.trim(); applySearch(); });
  $('wiki-search').addEventListener('keydown', (event) => {
    if (event.key !== 'Enter') return;
    event.preventDefault();
    const hit = searchHits()[0];
    if (hit) openPage(hit);
  });
  function searchHits() {
    const q = nameKey(ws.query);
    if (!q || !ws.graph) return [];
    const exact = [], partial = [];
    for (const page of ws.graph.pages) {
      const names = [page.title, ...(page.aliases || []), ...(page.tickers || [])].map(nameKey);
      if (names.includes(q)) exact.push(page.id);
      else if (names.some((name) => name.includes(q))) partial.push(page.id);
    }
    return [...exact, ...partial];
  }

  function renderCanvas() {
    const s = ws.status;
    const pages = ws.graph?.pages ?? [];
    const chain = ws.mode === 'chain';
    $('chain-view').hidden = !chain;
    $('graph-view').hidden = chain;
    $('graph-tools').hidden = chain;
    $('chain-tools').hidden = !chain;
    syncChainEnter();
    renderLegend();
    // 空图谱只保留引导文案：工具栏、图例和节点详情都没有可操作的内容。
    $('graph-body').classList.toggle('empty', Boolean(ws.graph) && !pages.length);
    if (!ws.graph) { showCanvasState('载入中…'); $('chain-view').innerHTML = ''; return; }
    if (!pages.length) {
      const pending = s?.files?.pending ?? 0;
      showCanvasState(!s || !s.folders.length
        ? '还没有知识图谱。关联资料文件夹后，后台会自动把研报、纪要整理成知识图谱；行情页的舆情也会被自动扫描。'
        : pending ? (s.auto?.available && s.auto.enabled ? '后台正在自动整理 ' + pending + ' 份资料，整理好后知识图谱会出现在这里。' : '还有 ' + pending + ' 份资料待整理（自动整理' + (s.auto?.available ? '已暂停，可以在右上角继续' : '需要 MiniMax Code 3.1.2+') + '）。') : '还没有知识图谱，文件夹里也没有可整理的资料。', false, !s || !s.folders.length ? { label: '去资料库', tab: 'files' } : null);
      $('chain-view').innerHTML = '';
      $('graph-svg').innerHTML = '';
      $('graph-view').hidden = true;
      return;
    }
    showCanvasState('');
    if (chain) renderChain();
    else renderGraph();
  }

  function renderLegend() {
    const hasPages = Boolean(ws.graph?.pages?.length);
    $('wiki-legend').hidden = !hasPages;
    if (!hasPages) return;
    $('wiki-legend').innerHTML = ws.mode === 'graph'
      ? Object.keys(TYPES).map((type) => `<button type="button" class="legend-item" data-legend-type="${type}" aria-pressed="${!ws.hiddenTypes.has(type)}" style="--c:${TYPE_COLOR[type]}"><i aria-hidden="true"></i>${TYPES[type]}</button>`).join('')
        + `<button type="button" class="legend-item ghost" data-legend-type="ghost" aria-pressed="${!ws.hiddenTypes.has('ghost')}"><i aria-hidden="true"></i>未建页面</button><span class="legend-note">实线：结构化关系 · 虚线：正文提及 / 待核</span>`
      : '<span class="legend-note"><i class="line accent" aria-hidden="true"></i>供货</span><span class="legend-note"><i class="line" aria-hidden="true"></i>上游供给</span><span class="legend-note"><i class="line dashed" aria-hidden="true"></i>待核</span><span class="legend-note">卡片里是属于该环节的公司与产品</span>';
    if (ws.mode === 'graph' && ws.graph?.pages?.some((page) => page.chain)) $('wiki-legend').insertAdjacentHTML('beforeend', '<span class="legend-note">双击节点进入所属行业的产业链</span>');
  }
  $('wiki-legend').addEventListener('click', (event) => {
    const item = event.target.closest('[data-legend-type]');
    if (!item) return;
    const type = item.dataset.legendType;
    if (ws.hiddenTypes.has(type)) ws.hiddenTypes.delete(type); else ws.hiddenTypes.add(type);
    ws.userViewport = false;
    renderCanvas();
  });

  // 产业链：上游 / 中游 / 下游三列，环节卡片里挂公司与产品，连线为 upstream_of / supplies。
  function chainModel() {
    const pages = ws.graph.pages;
    const industry = ws.chainIndustry;
    const target = nameKey(industry);
    const core = pages.filter((page) => industry === 'all' || nameKey(industryOf(page)) === target);
    const ids = new Set(core.map((page) => page.id));
    const segmentIds = new Set(core.filter((page) => page.type === 'segment').map((page) => page.id));
    const parentOf = new Map();
    for (const page of pages) {
      if (['segment', 'industry', 'source'].includes(page.type)) continue;
      for (const rel of page.relations || []) {
        if (rel.type !== 'belongs_to') continue;
        const id = resolveName(rel.target);
        if (id && segmentIds.has(id)) { parentOf.set(page.id, id); ids.add(page.id); break; }
      }
    }
    const list = pages.filter((page) => ids.has(page.id));
    const chainOf = (page) => page.chain || (parentOf.has(page.id) ? ws.byId.get(parentOf.get(page.id))?.chain : null) || null;
    const columns = { upstream: [], midstream: [], downstream: [] };
    const loose = { upstream: [], midstream: [], downstream: [] };
    const cards = new Map();
    for (const page of list) {
      if (page.type !== 'segment') continue;
      const chain = chainOf(page);
      if (!chain) continue;
      const card = { page, members: [] };
      cards.set(page.id, card);
      columns[chain].push(card);
    }
    for (const page of list) {
      if (['segment', 'industry', 'source'].includes(page.type)) continue;
      const parent = parentOf.get(page.id);
      if (parent && cards.has(parent)) cards.get(parent).members.push(page);
      else { const chain = chainOf(page); if (chain) loose[chain].push(page); }
    }
    const order = { company: 0, product: 1, concept: 2, event: 3 };
    const byWeight = (a, b) => (order[a.type] ?? 9) - (order[b.type] ?? 9) || (b.relations?.length ?? 0) - (a.relations?.length ?? 0) || a.title.localeCompare(b.title, 'zh-CN');
    for (const card of cards.values()) card.members.sort(byWeight);
    for (const key of Object.keys(loose)) loose[key].sort(byWeight);
    for (const key of Object.keys(columns)) columns[key].sort((a, b) => b.members.length - a.members.length || a.page.title.localeCompare(b.page.title, 'zh-CN'));
    const placed = new Set([...cards.keys(), ...[...cards.values()].flatMap((card) => card.members.map((page) => page.id)), ...Object.values(loose).flat().map((page) => page.id)]);
    const unplaced = list.filter((page) => !['industry', 'source'].includes(page.type) && !placed.has(page.id));
    const industryPage = industry === 'all' ? null : pages.find((page) => page.type === 'industry' && nameKey(page.title) === target) ?? null;
    return { columns, loose, unplaced, industryPage, empty: !placed.size };
  }

  function chip(page) {
    const ticker = (page.tickers || [])[0];
    return `<button type="button" class="chip" data-node="${esc(page.id)}" data-open-page="${esc(page.id)}" style="--c:${TYPE_COLOR[page.type]}" title="${esc(TYPES[page.type] + ' · ' + page.title)}"><i class="dot" aria-hidden="true"></i>${esc(page.title)}${ticker ? `<small>${esc(ticker.split('.')[0])}</small>` : ''}</button>`;
  }

  function renderChain() {
    const model = chainModel();
    const view = $('chain-view');
    if (model.empty) {
      view.innerHTML = `<div class="chain-empty"><p>${ws.chainIndustry === 'all' ? '还没有标注上中下游位置的节点。' : '「' + esc(ws.chainIndustry) + '」还没有标注上中下游位置的环节或公司。'}</p><p class="hint">在「分析视角」里启用产业链视角后重新整理资料，或返回知识图谱查看全部节点。</p></div>`;
      return;
    }
    const col = (key) => {
      const cards = model.columns[key];
      const loose = model.loose[key];
      const count = cards.length + loose.length;
      return `<section class="chain-col" aria-labelledby="col-${key}"><h3 id="col-${key}">${CHAINS[key]}<small>${cards.length ? cards.length + ' 个环节' : ''}${loose.length ? (cards.length ? ' · ' : '') + loose.length + ' 个未归类' : ''}</small></h3>
        ${cards.map(({ page, members }) => `<article class="seg-card" data-node="${esc(page.id)}">
          <button type="button" class="seg-title" data-open-page="${esc(page.id)}">${esc(page.title)}</button>
          ${page.excerpt ? `<p>${esc(page.excerpt)}</p>` : ''}
          ${members.length ? `<div class="chips">${members.map(chip).join('')}</div>` : ''}
        </article>`).join('')}
        ${loose.length ? `<article class="seg-card loose"><span class="seg-title muted">未归类到环节</span><div class="chips">${loose.map(chip).join('')}</div></article>` : ''}
        ${!count ? '<p class="col-empty">资料里还没有这一层的环节</p>' : ''}
      </section>`;
    };
    view.innerHTML = `
      ${model.industryPage ? `<div class="industry-strip"><button type="button" class="industry-title" data-open-page="${esc(model.industryPage.id)}">${typeTag('industry')}<span>${esc(model.industryPage.title)}</span></button>${model.industryPage.excerpt ? `<p>${esc(model.industryPage.excerpt)}</p>` : ''}</div>` : ''}
      <div class="chain-board" id="chain-board">
        <svg class="chain-edges" id="chain-edges" aria-hidden="true"><defs>
          <marker id="arrow-accent" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L8,4 L0,8 z" class="arrow-accent"/></marker>
          <marker id="arrow-muted" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L8,4 L0,8 z" class="arrow-muted"/></marker>
        </defs><g id="chain-edge-paths"></g></svg>
        ${col('upstream')}${col('midstream')}${col('downstream')}
      </div>
      ${model.unplaced.length ? `<p class="chain-foot">另有 ${model.unplaced.length} 个页面没有标注产业链位置：${model.unplaced.slice(0, 12).map((page) => `<button type="button" class="link-btn" data-open-page="${esc(page.id)}">${esc(page.title)}</button>`).join('、')}${model.unplaced.length > 12 ? ' 等' : ''}</p>` : ''}`;
    markSelection();
    applySearch();
    requestAnimationFrame(drawChainEdges);
  }

  function drawChainEdges() {
    const board = $('chain-board');
    const group = $('chain-edge-paths');
    if (!board || !group || board.offsetParent === null) return;
    const svg = $('chain-edges');
    const box = board.getBoundingClientRect();
    svg.setAttribute('width', String(board.scrollWidth));
    svg.setAttribute('height', String(board.scrollHeight));
    svg.setAttribute('viewBox', `0 0 ${board.scrollWidth} ${board.scrollHeight}`);
    const els = new Map();
    board.querySelectorAll('[data-node]').forEach((el) => { if (!els.has(el.dataset.node)) els.set(el.dataset.node, el); });
    const paths = [];
    let anyActive = false;
    for (const edge of ws.graph?.edges ?? []) {
      if (edge.type !== 'upstream_of' && edge.type !== 'supplies') continue;
      const from = els.get(edge.from), to = els.get(edge.to);
      if (!from || !to || from === to || from.contains(to) || to.contains(from)) continue;
      const a = from.getBoundingClientRect(), b = to.getBoundingClientRect();
      const y1 = a.top + a.height / 2 - box.top, y2 = b.top + b.height / 2 - box.top;
      let x1, x2, c1, c2;
      if (b.left < a.right && b.right > a.left) { x1 = a.right - box.left; x2 = b.right - box.left; c1 = c2 = Math.max(x1, x2) + 32; }
      else if (b.left >= a.right) { x1 = a.right - box.left; x2 = b.left - box.left; const d = Math.max(20, (x2 - x1) / 2); c1 = x1 + d; c2 = x2 - d; }
      else { x1 = a.left - box.left; x2 = b.right - box.left; const d = Math.max(20, (x1 - x2) / 2); c1 = x1 - d; c2 = x2 + d; }
      const active = Boolean(ws.selected) && (edge.from === ws.selected || edge.to === ws.selected);
      anyActive ||= active;
      const cls = ['edge', edge.type, edge.status === 'pending' ? 'pending' : '', active ? 'active' : ''].filter(Boolean).join(' ');
      const label = (ws.byId.get(edge.from)?.title ?? '') + ' → ' + (ws.byId.get(edge.to)?.title ?? '') + (edge.note ? '：' + edge.note : '');
      paths.push(`<path class="${cls}" d="M${x1.toFixed(1)},${y1.toFixed(1)} C${c1.toFixed(1)},${y1.toFixed(1)} ${c2.toFixed(1)},${y2.toFixed(1)} ${x2.toFixed(1)},${y2.toFixed(1)}" marker-end="url(#arrow-${edge.type === 'supplies' ? 'accent' : 'muted'})"><title>${esc(label)}</title></path>`);
    }
    group.innerHTML = paths.join('');
    svg.classList.toggle('has-active', anyActive);
  }

  // 知识图谱：力导向布局；节点 = 页面 + 尚未建页的关系目标（虚线圈）。
  function graphData() {
    const g = ws.graph;
    const hidden = ws.hiddenTypes;
    let nodes = g.pages.filter((page) => !hidden.has(page.type)).map((page) => ({ id: page.id, title: page.title, type: page.type, ghost: false }));
    if (!hidden.has('ghost')) nodes = nodes.concat(g.ghosts.map((ghost) => ({ id: ghost.id, title: ghost.title, type: null, ghost: true })));
    if (ws.industry !== 'all') {
      const target = nameKey(ws.industry);
      const core = new Set(g.pages.filter((page) => nameKey(industryOf(page)) === target).map((page) => page.id));
      const keep = new Set(core);
      for (const edge of g.edges) { if (core.has(edge.from)) keep.add(edge.to); if (core.has(edge.to)) keep.add(edge.from); }
      nodes = nodes.filter((node) => keep.has(node.id));
    }
    const set = new Set(nodes.map((node) => node.id));
    const edges = g.edges.filter((edge) => set.has(edge.from) && set.has(edge.to));
    const linked = new Set(edges.flatMap((edge) => [edge.from, edge.to]));
    nodes = nodes.filter((node) => !node.ghost || linked.has(node.id));
    const degree = new Map();
    for (const edge of edges) { degree.set(edge.from, (degree.get(edge.from) ?? 0) + 1); degree.set(edge.to, (degree.get(edge.to) ?? 0) + 1); }
    return { nodes, edges, degree };
  }
  function hash(text) { let h = 2166136261; for (const ch of String(text)) { h ^= ch.codePointAt(0); h = Math.imul(h, 16777619); } return (h >>> 0) / 4294967295; }
  function layout(nodes, edges) {
    const n = nodes.length;
    const k = Math.sqrt((900 * 640) / Math.max(1, n)) * 0.85;
    const pos = new Map();
    let fresh = 0;
    for (const node of nodes) {
      const cached = ws.positions.get(node.id);
      if (cached) pos.set(node.id, { x: cached.x, y: cached.y });
      else { fresh += 1; const angle = hash(node.id) * Math.PI * 2, r = 120 + hash(node.id + '#') * 260; pos.set(node.id, { x: Math.cos(angle) * r, y: Math.sin(angle) * r }); }
    }
    const iterations = fresh === 0 ? 30 : n < 120 ? 320 : n < 400 ? 200 : 120;
    let temp = fresh === 0 ? 10 : 90;
    const list = nodes.map((node) => pos.get(node.id));
    const index = new Map(nodes.map((node, i) => [node.id, i]));
    const links = edges.map((edge) => [index.get(edge.from), index.get(edge.to)]).filter(([a, b]) => a !== undefined && b !== undefined);
    const dx = new Float64Array(n), dy = new Float64Array(n);
    for (let it = 0; it < iterations; it += 1) {
      dx.fill(0); dy.fill(0);
      for (let i = 0; i < n; i += 1) for (let j = i + 1; j < n; j += 1) {
        let x = list[i].x - list[j].x, y = list[i].y - list[j].y;
        let d2 = x * x + y * y;
        if (d2 < 0.01) { x = hash(i + ':' + j) - 0.5; y = hash(j + ':' + i) - 0.5; d2 = x * x + y * y + 0.01; }
        if (d2 > 9 * k * k) continue;
        const f = (k * k) / d2;
        dx[i] += x * f; dy[i] += y * f; dx[j] -= x * f; dy[j] -= y * f;
      }
      for (const [a, b] of links) {
        const x = list[a].x - list[b].x, y = list[a].y - list[b].y;
        const f = (Math.sqrt(x * x + y * y) || 0.01) / k;
        dx[a] -= x * f; dy[a] -= y * f; dx[b] += x * f; dy[b] += y * f;
      }
      for (let i = 0; i < n; i += 1) {
        dx[i] -= list[i].x * 0.03; dy[i] -= list[i].y * 0.03;
        const d = Math.sqrt(dx[i] * dx[i] + dy[i] * dy[i]) || 1;
        const step = Math.min(d, temp);
        list[i].x += (dx[i] / d) * step; list[i].y += (dy[i] / d) * step;
      }
      temp = Math.max(1.5, temp * 0.975);
    }
    for (const node of nodes) ws.positions.set(node.id, pos.get(node.id));
    return pos;
  }
  function renderGraph() {
    const svg = $('graph-svg');
    const data = graphData();
    if (!data.nodes.length) { svg.innerHTML = ''; showCanvasState('当前筛选下没有节点。'); return; }
    const pos = layout(data.nodes, data.edges);
    const xs = [...pos.values()].map((p) => p.x), ys = [...pos.values()].map((p) => p.y);
    const pad = 70;
    ws.bounds = { x: Math.min(...xs) - pad * 1.6, y: Math.min(...ys) - pad, w: Math.max(...xs) - Math.min(...xs) + pad * 3.2, h: Math.max(...ys) - Math.min(...ys) + pad * 2 };
    if (!ws.viewBox || !ws.userViewport) ws.viewBox = { ...ws.bounds };
    const radius = (node) => node.ghost ? 4 : Math.min(18, 5 + Math.sqrt(data.degree.get(node.id) ?? 0) * 2.4 + (node.type === 'industry' ? 4 : node.type === 'segment' ? 2 : 0));
    const many = data.nodes.length > 60;
    const edgesSvg = data.edges.map((edge) => {
      const a = pos.get(edge.from), b = pos.get(edge.to);
      return `<line class="gedge ${esc(edge.type)}${edge.status === 'pending' ? ' pending' : ''}" data-from="${esc(edge.from)}" data-to="${esc(edge.to)}" x1="${a.x.toFixed(1)}" y1="${a.y.toFixed(1)}" x2="${b.x.toFixed(1)}" y2="${b.y.toFixed(1)}"/>`;
    }).join('');
    const nodesSvg = data.nodes.map((node) => {
      const p = pos.get(node.id);
      const deg = data.degree.get(node.id) ?? 0;
      const r = radius(node);
      const labeled = !many || deg >= 3 || node.type === 'industry' || node.type === 'segment';
      return `<g class="gnode${node.ghost ? ' ghost' : ''}${labeled ? ' labeled' : ''}" data-node="${esc(node.id)}" transform="translate(${p.x.toFixed(1)},${p.y.toFixed(1)})" tabindex="0" role="button" aria-label="${esc(node.title + '（' + (node.ghost ? '未建页面' : TYPES[node.type]) + '，' + deg + ' 条关系）')}"><circle r="${r.toFixed(1)}" style="fill:${node.ghost ? 'transparent' : TYPE_COLOR[node.type]}"/><text y="${(r + 13).toFixed(1)}" text-anchor="middle">${esc(node.title)}</text></g>`;
    }).join('');
    svg.innerHTML = `<g class="gedges">${edgesSvg}</g><g class="gnodes">${nodesSvg}</g>`;
    applyViewBox();
    markSelection();
    applySearch();
  }
  function applyViewBox() {
    const vb = ws.viewBox;
    if (vb) $('graph-svg').setAttribute('viewBox', `${vb.x.toFixed(1)} ${vb.y.toFixed(1)} ${vb.w.toFixed(1)} ${vb.h.toFixed(1)}`);
  }
  function zoom(factor, cx, cy) {
    const vb = ws.viewBox;
    if (!vb) return;
    const w = Math.max(80, Math.min(vb.w * factor, 8000)), h = vb.h * (w / vb.w);
    const px = cx ?? vb.x + vb.w / 2, py = cy ?? vb.y + vb.h / 2;
    ws.viewBox = { x: px - (px - vb.x) * (w / vb.w), y: py - (py - vb.y) * (h / vb.h), w, h };
    applyViewBox();
  }
  document.querySelectorAll('[data-zoom]').forEach((button) => button.addEventListener('click', () => {
    if (button.dataset.zoom === 'fit') { ws.userViewport = false; ws.viewBox = ws.bounds ? { ...ws.bounds } : null; applyViewBox(); }
    else { ws.userViewport = true; zoom(button.dataset.zoom === 'in' ? 0.8 : 1.25); }
  }));
  const graphSvg = $('graph-svg');
  function svgPoint(event) {
    const rect = graphSvg.getBoundingClientRect();
    const vb = ws.viewBox;
    const scale = Math.max(vb.w / rect.width, vb.h / rect.height);
    const offX = (rect.width * scale - vb.w) / 2, offY = (rect.height * scale - vb.h) / 2;
    return { x: vb.x - offX + (event.clientX - rect.left) * scale, y: vb.y - offY + (event.clientY - rect.top) * scale, scale };
  }
  graphSvg.addEventListener('wheel', (event) => {
    if (!ws.viewBox) return;
    event.preventDefault();
    ws.userViewport = true;
    const p = svgPoint(event);
    zoom(Math.exp(event.deltaY * 0.0015), p.x, p.y);
  }, { passive: false });
  let pan = null;
  graphSvg.addEventListener('pointerdown', (event) => {
    if (event.target.closest('.gnode') || !ws.viewBox) return;
    pan = { x: event.clientX, y: event.clientY, vb: { ...ws.viewBox }, scale: svgPoint(event).scale };
    graphSvg.setPointerCapture(event.pointerId);
    graphSvg.classList.add('panning');
  });
  graphSvg.addEventListener('pointermove', (event) => {
    if (!pan) return;
    ws.userViewport = true;
    ws.viewBox = { ...pan.vb, x: pan.vb.x - (event.clientX - pan.x) * pan.scale, y: pan.vb.y - (event.clientY - pan.y) * pan.scale };
    applyViewBox();
  });
  const endPan = () => { pan = null; graphSvg.classList.remove('panning'); };
  graphSvg.addEventListener('pointerup', endPan);
  graphSvg.addEventListener('pointercancel', endPan);
  graphSvg.addEventListener('click', (event) => { const node = event.target.closest('.gnode'); if (node) select(node.dataset.node); });
  graphSvg.addEventListener('dblclick', (event) => {
    const node = event.target.closest('.gnode');
    const page = node ? ws.byId.get(node.dataset.node) : null;
    const industry = page ? industryOf(page) : null;
    if (industry && ws.graph.pages.some((item) => item.chain)) enterChain(industry, page.type === 'industry' ? null : page.id);
  });
  graphSvg.addEventListener('keydown', (event) => {
    const node = event.target.closest('.gnode');
    if (node && (event.key === 'Enter' || event.key === ' ')) { event.preventDefault(); select(node.dataset.node); }
  });
  graphSvg.addEventListener('pointerover', (event) => { const node = event.target.closest('.gnode'); if (node) focusGraph(node.dataset.node); });
  graphSvg.addEventListener('pointerout', (event) => { if (event.target.closest('.gnode')) focusGraph(ws.selected); });
  function focusGraph(id) {
    graphSvg.querySelectorAll('.near').forEach((el) => el.classList.remove('near'));
    graphSvg.classList.toggle('focus', Boolean(id));
    if (!id) return;
    const near = new Set([id]);
    graphSvg.querySelectorAll('.gedge').forEach((line) => {
      if (line.dataset.from === id || line.dataset.to === id) { line.classList.add('near'); near.add(line.dataset.from); near.add(line.dataset.to); }
    });
    graphSvg.querySelectorAll('.gnode').forEach((g) => { if (near.has(g.dataset.node)) g.classList.add('near'); });
  }

  function markSelection() {
    document.querySelectorAll('#chain-view [data-selected]').forEach((el) => el.removeAttribute('data-selected'));
    graphSvg.querySelectorAll('.gnode.selected').forEach((el) => el.classList.remove('selected'));
    if (ws.selected) {
      document.querySelectorAll('#chain-view [data-node]').forEach((el) => { if (el.dataset.node === ws.selected) el.setAttribute('data-selected', 'true'); });
      graphSvg.querySelectorAll('.gnode').forEach((el) => { if (el.dataset.node === ws.selected) el.classList.add('selected'); });
    }
    if (ws.mode === 'graph') focusGraph(ws.selected);
  }
  function applySearch() {
    const hits = new Set(searchHits());
    const active = Boolean(ws.query);
    document.querySelectorAll('#chain-view [data-node]').forEach((el) => el.classList.toggle('match', active && hits.has(el.dataset.node)));
    $('chain-view').classList.toggle('searching', active);
    graphSvg.querySelectorAll('.gnode').forEach((el) => el.classList.toggle('match', active && hits.has(el.dataset.node)));
    graphSvg.classList.toggle('searching', active);
  }
  function redrawCanvasOverlays() { if (ws.mode === 'chain' && ws.page === 'assets' && ws.tab === 'graph') drawChainEdges(); }
  const canvasObserver = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(() => requestAnimationFrame(redrawCanvasOverlays)) : null;
  canvasObserver?.observe($('chain-view'));
  $('chain-view').addEventListener('click', (event) => { const target = event.target.closest('[data-open-page]'); if (target) select(target.dataset.openPage); });

  // ---------- 详情 ----------
  async function select(idOrName) {
    let id = ws.byId.has(idOrName) ? idOrName : resolveName(idOrName);
    if (!id) id = String(idOrName).startsWith('ghost:') ? idOrName : 'ghost:' + nameKey(idOrName);
    if (ws.selected !== id) ws.allRecords = false;
    ws.selected = id;
    markSelection();
    if (ws.mode === 'chain') drawChainEdges();
    if (ws.mode === 'graph') syncChainEnter();
    report();
    await loadDetail(id);
  }
  async function loadDetail(id, { quiet = false } = {}) {
    const seq = ++ws.detailSeq;
    if (!quiet) { ws.detail = { loading: true }; renderDetail(); }
    try {
      const node = ws.byId.get(id);
      const payload = id.startsWith('ghost:')
        ? await api('/api/wiki/page?title=' + enc(node?.title ?? id.slice(6)))
        : await api('/api/wiki/page?id=' + enc(id));
      if (seq !== ws.detailSeq) return;
      ws.detail = payload;
    } catch (error) {
      if (seq !== ws.detailSeq) return;
      ws.detail = { error: error.message };
    }
    renderDetail();
    if (!quiet && window.matchMedia('(max-width: 900px)').matches) $('wiki-detail').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  function relationItem(entry) {
    const id = entry.targetId ?? entry.id ?? null;
    const title = entry.target ?? entry.title;
    return `<li><button type="button" class="wikilink" data-page-name="${esc(id ?? title)}">${esc(title)}</button>${entry.status === 'pending' ? ' <span class="tag warning">待核</span>' : ''}${entry.note ? `<span class="rel-note">${esc(entry.note)}</span>` : ''}${entry.sourceRef ? `<span class="rel-source">${refChip(entry.sourceRef)}</span>` : entry.source ? `<small class="rel-source">来源：${esc(entry.source)}</small>` : ''}</li>`;
  }
  function groupRelations(items, key, labels) {
    const groups = new Map();
    for (const item of items) { const label = labels[item[key]] ?? item[key]; if (!groups.has(label)) groups.set(label, []); groups.get(label).push(item); }
    return [...groups.entries()].map(([label, list]) => `<div class="rel-group"><dt>${esc(label)}</dt><dd><ul>${list.map(relationItem).join('')}</ul></dd></div>`).join('');
  }
  function renderDetail() {
    const panel = $('wiki-detail');
    const d = ws.detail;
    if (!d) {
      const s = ws.status;
      panel.innerHTML = `<div class="detail-empty"><h2>节点详情</h2><p>点选节点，查看它的内容、上下游关系和来源。双击节点进入所属行业的产业链。</p>${s && s.pages ? `<dl class="detail-stats">${Object.entries(s.byType || {}).map(([type, count]) => `<div><dt>${esc(TYPES[type] || type)}</dt><dd>${count}</dd></div>`).join('')}</dl>` : ''}</div>`;
      return;
    }
    if (d.loading) { panel.innerHTML = '<div class="detail-empty" role="status" aria-label="载入页面"><div class="state-row" style="width:60%"></div><div class="state-row" style="width:85%"></div><div class="state-row" style="width:40%"></div></div>'; return; }
    if (d.error) { panel.innerHTML = `<div class="detail-empty"><p class="error-text" role="alert">${esc(d.error)}</p></div>`; return; }
    if (d.ghost) {
      panel.innerHTML = `<article class="detail-page"><div class="detail-tags">${typeTag(null)}</div><h2 id="detail-heading">${esc(d.title)}</h2><p class="detail-note">资料里提到了它，但还没有独立页面。之后整理相关资料时，Agent 可能会补建。</p>
        ${d.backlinks?.length ? `<section><h3>提到它的页面</h3><dl class="rel-list">${groupRelations(d.backlinks, 'relation', IN_LABELS)}</dl></section>` : ''}</article>`;
      return;
    }
    const p = d.page;
    const tickers = (p.tickers || []).map((ticker) => `<div class="ticker-row"><code>${esc(ticker)}</code>${/\.(SH|SZ|BJ)$/.test(ticker) ? `<button type="button" class="btn small" data-goto-symbol="${esc(ticker)}">看行情</button><button type="button" class="btn small" data-watch-add="${esc(ticker)}">加自选</button>` : ''}</div>`).join('');
    panel.innerHTML = `<article class="detail-page">
      <div class="detail-tags">${typeTag(p.type)}${p.chain ? `<span class="tag">${CHAINS[p.chain]}</span>` : ''}${p.industry ? `<span class="tag">${esc(p.industry)}</span>` : ''}</div>
      <h2 id="detail-heading">${esc(p.title)}</h2>
      ${chainAction(p)}
      ${p.aliases?.length ? `<p class="detail-note">别名：${esc(p.aliases.join('、'))}</p>` : ''}
      ${tickers ? `<div class="tickers">${tickers}</div>` : ''}
      <p id="detail-action-status" class="detail-note" role="status"></p>
      ${latestSection(p)}
      ${p.records?.length ? '<h3 class="body-title">综述</h3>' : ''}
      <div class="md">${renderBody(p) || '<p class="detail-note">（正文为空）</p>'}</div>
      ${p.type === 'company' || p.tickers?.length ? stockFilesSection(p) : ''}
      ${p.relations?.length ? `<section><h3>关系</h3><dl class="rel-list">${groupRelations(p.relations, 'type', OUT_LABELS)}</dl></section>` : ''}
      ${p.backlinks?.length ? `<section><h3>被其他页面关联</h3><dl class="rel-list">${groupRelations(p.backlinks, 'relation', IN_LABELS)}</dl></section>` : ''}
      ${p.sourceRefs?.length ? `<section><h3>来源</h3><ul class="source-list refs">${p.sourceRefs.map((ref) => `<li>${refChip(ref, { full: true })}</li>`).join('')}</ul></section>` : p.sources?.length ? `<section><h3>来源</h3><ul class="source-list">${p.sources.map((source) => `<li>${esc(source)}</li>`).join('')}</ul></section>` : ''}
      <p class="detail-foot">${p.updated ? '更新于 ' + esc(fmtTime(p.updated)) : ''}${p.tags?.length ? ' · ' + esc(p.tags.map((tag) => '#' + tag).join(' ')) : ''}</p>
    </article>`;
  }
  /** 节点详情最上面：按日期倒序的最新动态与边际变化，每条带可打开的出处。 */
  function latestSection(p) {
    const list = p.records ?? [];
    if (!list.length) return '';
    const shown = ws.allRecords ? list : list.slice(0, 4);
    return `<section class="latest-block" aria-labelledby="latest-title"><div class="section-head"><h3 id="latest-title">最新</h3>${list.length > 4 ? `<button type="button" class="link-btn" data-toggle-records>${ws.allRecords ? '收起' : '全部 ' + list.length + ' 条'}</button>` : ''}</div><ol class="record-list">${shown.map(recordItem).join('')}</ol></section>`;
  }
  function chainAction(p) {
    const industry = p.type === 'industry' ? p.title : p.industry;
    if (!industry || !ws.graph?.pages?.some((page) => page.chain && nameKey(industryOf(page)) === nameKey(industry))) return '';
    if (ws.mode === 'chain' && nameKey(ws.chainIndustry) === nameKey(industry)) return '';
    return `<div class="detail-actions"><button type="button" class="btn small" data-chain-enter="${esc(industry)}" data-chain-focus="${p.type === 'industry' ? '' : esc(p.id)}">${p.type === 'industry' ? '查看产业链' : '在产业链中定位'}</button></div>`;
  }
  function stockFilesSection(p) {
    const files = p.stockFiles || [];
    const symbol = (p.tickers || []).find((ticker) => /\.(SH|SZ|BJ)$/.test(ticker));
    const list = files.length
      ? `<ul class="stock-files">${files.slice(0, 40).map((file) => `<li><span class="tag ${file.relevance === 'core' ? 'success' : ''}">${file.relevance === 'core' ? '核心' : '提及'}</span><span class="sf-main">${file.openable ? `<button type="button" class="sf-name link" data-ref-kind="file" data-ref-key="${esc(file.key)}" title="用默认应用打开：${esc(file.display)}">${esc(file.display.split('/').pop())}</button>` : `<span class="sf-name" title="${esc(file.display)}">${esc(file.display.split('/').pop())}</span>`}${file.note ? `<span class="rel-note">${esc(file.note)}</span>` : ''}</span></li>`).join('')}</ul>`
      : '<p class="detail-note">资料库里还没有标注和它相关的资料，后台整理时会自动补上。</p>';
    return `<section><div class="section-head"><h3>相关资料</h3></div>${list}</section>`;
  }
  $('wiki-detail').addEventListener('click', async (event) => {
    if (event.target.closest('[data-toggle-records]')) { ws.allRecords = !ws.allRecords; renderDetail(); return; }
    const link = event.target.closest('[data-page-name]');
    if (link) { openPage(link.dataset.pageName); return; }
    const chainButton = event.target.closest('[data-chain-enter]');
    if (chainButton) { enterChain(chainButton.dataset.chainEnter, chainButton.dataset.chainFocus || null); renderDetail(); return; }
    const goto = event.target.closest('[data-goto-symbol]');
    if (goto) { showPage('market'); $('symbol-search').value = goto.dataset.gotoSymbol; if (typeof loadSnapshot === 'function') loadSnapshot(goto.dataset.gotoSymbol); return; }
    const add = event.target.closest('[data-watch-add]');
    if (add) {
      add.disabled = true;
      const status = $('detail-action-status');
      try {
        await api('/api/watchlist', { method: 'POST', body: JSON.stringify({ symbol: add.dataset.watchAdd }) });
        if (status) status.textContent = add.dataset.watchAdd + ' 已加入自选股';
        if (typeof loadWatchlist === 'function') loadWatchlist();
      } catch (error) { if (status) status.textContent = '加入自选失败：' + error.message; }
      finally { add.disabled = false; }
    }
  });

  // 轻量 Markdown：标题、段落、列表、引用、代码、表格、粗体/斜体、[[wikilink]]、http(s) 链接。
  let bodyLinks = [];
  const escapeRegex = (text) => text.replace(/[.*+?^$(){}|[\]\\]/g, '\\$&');
  /** 正文里出现的资料文件名换成可打开的按钮，裸链接换成用默认浏览器打开的按钮。 */
  function linkPlain(segment) {
    let out = segment;
    if (bodyLinks.length) {
      const pattern = new RegExp(bodyLinks.map((item) => escapeRegex(esc(item.text))).join('|'), 'g');
      out = out.replace(pattern, (match) => {
        const item = bodyLinks.find((entry) => esc(entry.text) === match);
        return item ? '<button type="button" class="md-file" data-ref-kind="file" data-ref-key="' + esc(item.key) + '" title="用默认应用打开">' + match + '</button>' : match;
      });
    }
    return out.replace(/https?:\/\/[^\s<>"'）)」，。]+/g, (url) => '<button type="button" class="md-link" data-ref-kind="url" data-ref-url="' + url + '">' + url + '</button>');
  }
  function inline(text) {
    let out = esc(text);
    out = out.split(/(\[\[[^\]]+\]\]|\[[^\]]+\]\(https?:\/\/[^)\s"]+\))/).map((part, index) => (index % 2 ? part : linkPlain(part))).join('');
    out = out.replace(/`([^`]+)`/g, '<code>$1</code>');
    out = out.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    out = out.replace(/(^|[^*\w])\*([^*\s][^*]*?)\*(?!\*)/g, '$1<em>$2</em>');
    out = out.replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, target, label) => `<button type="button" class="wikilink" data-page-name="${target.trim()}">${label || target}</button>`);
    out = out.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s"]+)\)/g, '<button type="button" class="md-link" data-ref-kind="url" data-ref-url="$2">$1</button>');
    return out;
  }
  function renderBody(p) {
    bodyLinks = [...(p.linkables ?? [])].sort((a, b) => b.text.length - a.text.length);
    try { return renderMarkdown(p.body); } finally { bodyLinks = []; }
  }
  function renderMarkdown(source) {
    const lines = String(source ?? '').replace(/\r\n?/g, '\n').split('\n');
    const out = [];
    const fence = /^\s*```/;
    const bullet = /^\s*[-*+]\s+/, numbered = /^\s*\d+[.)]\s+/;
    const isTableSep = (line) => /^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$/.test(line);
    const cells = (line) => line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((cell) => cell.trim());
    const tableStart = (i) => lines[i].includes('|') && i + 1 < lines.length && isTableSep(lines[i + 1]);
    let i = 0;
    while (i < lines.length) {
      const line = lines[i];
      if (fence.test(line)) {
        const buf = [];
        i += 1;
        while (i < lines.length && !fence.test(lines[i])) { buf.push(lines[i]); i += 1; }
        i += 1;
        out.push(`<pre><code>${esc(buf.join('\n'))}</code></pre>`);
        continue;
      }
      const heading = line.match(/^(#{1,6})\s+(.*)$/);
      if (heading) { const level = Math.min(6, heading[1].length + 2); out.push(`<h${level}>${inline(heading[2])}</h${level}>`); i += 1; continue; }
      if (tableStart(i)) {
        const head = cells(line);
        i += 2;
        const rows = [];
        while (i < lines.length && lines[i].includes('|') && lines[i].trim()) { rows.push(cells(lines[i])); i += 1; }
        out.push(`<div class="table-wrap"><table><thead><tr>${head.map((cell) => `<th>${inline(cell)}</th>`).join('')}</tr></thead><tbody>${rows.map((row) => `<tr>${head.map((_, c) => `<td>${inline(row[c] ?? '')}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`);
        continue;
      }
      if (bullet.test(line) || numbered.test(line)) {
        const pattern = numbered.test(line) ? numbered : bullet;
        const tag = pattern === numbered ? 'ol' : 'ul';
        const items = [];
        while (i < lines.length && pattern.test(lines[i])) { items.push(lines[i].replace(pattern, '')); i += 1; }
        out.push(`<${tag}>${items.map((item) => `<li>${inline(item)}</li>`).join('')}</${tag}>`);
        continue;
      }
      if (/^\s*>/.test(line)) {
        const buf = [];
        while (i < lines.length && /^\s*>/.test(lines[i])) { buf.push(lines[i].replace(/^\s*>\s?/, '')); i += 1; }
        out.push(`<blockquote>${inline(buf.join(' '))}</blockquote>`);
        continue;
      }
      if (!line.trim()) { i += 1; continue; }
      const buf = [];
      while (i < lines.length && lines[i].trim() && !/^#{1,6}\s/.test(lines[i]) && !bullet.test(lines[i]) && !numbered.test(lines[i]) && !/^\s*>/.test(lines[i]) && !fence.test(lines[i]) && !tableStart(i)) { buf.push(lines[i]); i += 1; }
      out.push(`<p>${inline(buf.join(' '))}</p>`);
    }
    return out.join('');
  }

  // ---------- 边际变化 ----------
  const cw = { data: null, loaded: false, dir: 'all', dimension: 'all', source: 'all', range: 'all', query: '' };
  async function loadChanges() {
    try { cw.data = await api('/api/wiki/changes'); }
    catch (error) { cw.data = { changes: [], total: 0, updates: 0, error: error.message }; }
    renderChanges();
  }
  const daysAgo = (days) => new Date(Date.now() - days * 86400000).toISOString().slice(0, 10);
  function changeMatches(item, { ignoreDir = false } = {}) {
    if (!ignoreDir && cw.dir !== 'all' && item.direction !== cw.dir) return false;
    if (cw.dimension !== 'all' && item.dimension !== cw.dimension) return false;
    if (cw.source !== 'all' && !(item.sourceKinds ?? []).includes(cw.source)) return false;
    if (cw.range !== 'all' && String(item.date) < daysAgo(Number(cw.range))) return false;
    if (cw.query) { const q = nameKey(cw.query); if (![item.entity, item.text, item.from, item.to, ...(item.tickers ?? [])].some((value) => nameKey(value).includes(q))) return false; }
    return true;
  }
  function renderChanges() {
    const list = $('changes-list');
    if (!list) return;
    renderScanButton();
    const data = cw.data;
    if (!data) { list.innerHTML = '<p class="list-state">载入中…</p>'; return; }
    if (data.error) { list.innerHTML = `<p class="list-state error-text" role="alert">边际变化暂时无法读取：${esc(data.error)}</p>`; return; }
    const all = data.changes ?? [];
    const recent = all.filter((item) => String(item.date) >= daysAgo(30)).length;
    $('changes-meta').textContent = all.length ? all.length + ' 条变化 · 近 30 天 ' + recent + ' 条' + (data.updates ? ' · 另有 ' + data.updates + ' 条最新动态在节点详情里' : '') : '';
    const base = all.filter((item) => changeMatches(item, { ignoreDir: true }));
    for (const key of ['all', 'improve', 'weaken', 'unclear']) $('cd-' + key).textContent = String(key === 'all' ? base.length : base.filter((item) => item.direction === key).length);
    const dimOptions = '<option value="all">全部维度</option>' + (data.dimensions ?? []).map((dim) => `<option value="${esc(dim)}">${esc(dim)}</option>`).join('');
    if ($('changes-dimension').innerHTML !== dimOptions) $('changes-dimension').innerHTML = dimOptions;
    $('changes-dimension').value = cw.dimension;
    const kinds = [...new Set(all.flatMap((item) => item.sourceKinds ?? []))];
    if (cw.source !== 'all' && !kinds.includes(cw.source)) cw.source = 'all';
    const srcOptions = '<option value="all">全部来源</option>' + kinds.map((kind) => `<option value="${esc(kind)}">${esc(kind)}</option>`).join('');
    if ($('changes-source').innerHTML !== srcOptions) $('changes-source').innerHTML = srcOptions;
    $('changes-source').value = cw.source;
    if (!all.length) {
      list.innerHTML = '<div class="changes-empty"><h3>还没有边际变化</h3><p>后台 Agent 整理资料库、扫描行情页抓到的舆情（Alpha派、知识星球、进门财经、腾讯文档）时，会把相对此前资料的变化记在这里，每条都附出处。全部自动进行，不需要手动操作。</p></div>';
      return;
    }
    const items = base.filter((item) => cw.dir === 'all' || item.direction === cw.dir);
    if (!items.length) { list.innerHTML = '<p class="list-state">当前筛选下没有变化。</p>'; return; }
    let month = '';
    list.innerHTML = items.slice(0, 400).map((item) => {
      const current = String(item.date).slice(0, 7);
      const head = current !== month ? `<h3 class="changes-month">${esc(current.replace('-', ' 年 ') + ' 月')}</h3>` : '';
      month = current;
      return head + changeRow(item);
    }).join('') + (items.length > 400 ? `<p class="list-state">还有 ${items.length - 400} 条，缩小筛选范围查看</p>` : '');
  }
  function changeRow(item) {
    return `<article class="change-row">
      <time class="change-date" datetime="${esc(item.date)}">${esc(String(item.date).slice(5) || item.date)}</time>
      <div class="change-main">
        <div class="change-head"><button type="button" class="change-entity" data-open-page="${esc(item.entityId ?? item.entity)}" title="在知识图谱中查看">${typeTag(item.entityType)}<span>${esc(item.entity)}</span></button><span class="dim-tag">${esc(item.dimension ?? '其他')}</span>${dirTag(item.direction)}</div>
        <p class="change-text">${esc(item.text)}</p>
        ${item.from || item.to ? `<p class="change-delta"><span>${esc(item.from || '—')}</span><span aria-hidden="true">→</span><span>${esc(item.to || '—')}</span></p>` : ''}
        <div class="change-sources">${(item.sources ?? []).map((ref) => refChip(ref)).join('')}</div>
      </div>
    </article>`;
  }
  function renderScanButton() {
    const button = $('changes-scan');
    const note = $('changes-auto');
    if (!button || !note) return;
    const s = ws.status;
    const auto = s?.auto;
    const job = s?.job;
    const running = Boolean(job && ACTIVE_JOB.includes(job.status));
    const snapshot = typeof state !== 'undefined' ? state.snapshot : null;
    note.textContent = !s ? ''
      : !auto?.available ? '当前版本不支持自动扫描'
      : !auto.enabled ? '自动整理已暂停'
      : running && job.kind === 'scan' ? '正在扫描舆情…'
      : auto.unscanned ? auto.unscanned + ' 条新舆情等待自动扫描'
      : '后台自动扫描当前股票和自选股的新舆情';
    button.hidden = !(s && auto?.available && auto.unscanned && !running);
    button.disabled = false;
    button.title = '现在就扫描当前股票和自选股的新舆情，不用等后台排队';
  }
  $('changes-scan').addEventListener('click', async () => {
    const snapshot = typeof state !== 'undefined' ? state.snapshot : null;
    $('changes-scan').disabled = true;
    try {
      const job = await api('/api/wiki/jobs', { method: 'POST', body: JSON.stringify({ kind: 'scan', scope: 'all', symbol: snapshot?.symbol ?? '' }) });
      toast('开始扫描 ' + job.total + ' 条舆情');
      await loadStatus();
    } catch (error) {
      toast(error.message, true);
      renderScanButton();
    }
  });
  document.querySelectorAll('[data-change-dir]').forEach((button) => button.addEventListener('click', () => {
    cw.dir = button.dataset.changeDir;
    document.querySelectorAll('[data-change-dir]').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    renderChanges();
  }));
  $('changes-dimension').addEventListener('change', () => { cw.dimension = $('changes-dimension').value; renderChanges(); });
  $('changes-source').addEventListener('change', () => { cw.source = $('changes-source').value; renderChanges(); });
  $('changes-range').addEventListener('change', () => { cw.range = $('changes-range').value; renderChanges(); });
  $('changes-search').addEventListener('input', () => { cw.query = $('changes-search').value.trim(); renderChanges(); });
  $('changes-list').addEventListener('click', (event) => { const target = event.target.closest('[data-open-page]'); if (target) void openPage(target.dataset.openPage, { mode: 'graph' }); });

  // ---------- 行情页：最新 / 舆情 / 纪要并列板块 ----------
  const FEEDS = ['latest', 'sentiment', 'minutes'];
  const storedFeed = store.get('market.feed');
  const feed = { tab: FEEDS.includes(storedFeed) ? storedFeed : 'latest', latest: null, minutes: null, seq: 0, symbol: null, detailId: null, minutesKey: null };
  function showFeed(tab, { quiet = false } = {}) {
    feed.tab = FEEDS.includes(tab) ? tab : 'latest';
    if (!quiet) store.set('market.feed', feed.tab);
    for (const id of FEEDS) {
      const button = $('feed-tab-' + id);
      const panel = $('feed-panel-' + id);
      if (!button || !panel) continue;
      button.setAttribute('aria-selected', String(id === feed.tab));
      button.tabIndex = id === feed.tab ? 0 : -1;
      panel.hidden = id !== feed.tab;
    }
    const search = $('sentiment-search');
    if (search) { search.placeholder = { latest: '检索最新', sentiment: '检索舆情', minutes: '检索纪要' }[feed.tab]; search.setAttribute('aria-label', search.placeholder); }
    renderLatest();
    renderMinutes();
    renderScope();
    if (!quiet) report();
  }
  document.querySelector('.feed-tabs')?.addEventListener('click', (event) => { const button = event.target.closest('[data-feed]'); if (button) showFeed(button.dataset.feed); });
  document.querySelector('.feed-tabs')?.addEventListener('keydown', (event) => {
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return;
    const index = FEEDS.indexOf(feed.tab);
    const next = FEEDS[(index + (event.key === 'ArrowRight' ? 1 : FEEDS.length - 1)) % FEEDS.length];
    showFeed(next);
    $('feed-tab-' + next)?.focus();
  });
  const feedQuery = () => (typeof state !== 'undefined' ? String(state.query ?? '') : '').trim().toLowerCase();
  /** 搜索词：输入对得上知识图谱的节点时，带上它的别名（环节、产品再带上下属节点），由 /api/wiki/expand 给出。 */
  const feedTerms = () => {
    const q = feedQuery();
    if (!q) return [];
    const expanded = typeof state !== 'undefined' ? state.queryTerms : null;
    return expanded && expanded.q === q ? expanded.terms : [q];
  };
  const matchesTerms = (text, terms) => !terms.length || terms.some((term) => text.includes(term));
  let expandTimer = 0;
  let expandSeq = 0;
  async function expandSearch() {
    const raw = typeof state !== 'undefined' ? String(state.query ?? '').trim() : '';
    const seq = ++expandSeq;
    if (!raw) { renderExpandHint(null); return; }
    try {
      const data = await api('/api/wiki/expand?q=' + enc(raw));
      if (seq !== expandSeq || raw.toLowerCase() !== feedQuery()) return;
      state.queryTerms = { q: raw.toLowerCase(), terms: data.terms.map((term) => String(term).toLowerCase()) };
      renderExpandHint(data);
      if (typeof renderSentiments === 'function') renderSentiments();
      renderLatest();
      renderMinutes();
    } catch {}
  }
  function renderExpandHint(data) {
    const el = $('search-expand');
    if (!el) return;
    const extra = (data?.terms ?? []).slice(1);
    el.hidden = !extra.length;
    el.textContent = extra.length ? '同时检索' + (data.node ? '「' + data.node.title + '」在知识图谱里的' : '') + '别名和下属节点：' + extra.join('、') : '';
  }
  $('sentiment-search')?.addEventListener('input', () => {
    clearTimeout(expandTimer);
    expandTimer = setTimeout(expandSearch, 220);
    if (!feedQuery()) renderExpandHint(null);
    if (feed.tab === 'latest') renderLatest(); else if (feed.tab === 'minutes') renderMinutes();
  });

  // 舆情、纪要按知识图谱扩展检索：说明用了哪些词；可以只看直接提及这家公司的。
  feed.scope = store.get('market.scope') === 'direct' ? 'direct' : 'all';
  if (typeof state !== 'undefined') state.scope = feed.scope;
  function renderScope() {
    const el = $('feed-scope');
    if (!el) return;
    const scope = typeof state !== 'undefined' ? state.snapshot?.searchScope : null;
    const aliases = scope?.aliases ?? [];
    const related = scope?.related ?? [];
    el.hidden = !(feed.tab === 'sentiment' || feed.tab === 'minutes') || (!aliases.length && !related.length);
    if (el.hidden) return;
    const parts = [];
    if (aliases.length) parts.push('别名 ' + aliases.slice(0, 3).join('、'));
    if (related.length) parts.push('相邻节点 ' + related.slice(0, 5).map((item) => item.term).join('、') + (related.length > 5 ? ' 等 ' + related.length + ' 个' : ''));
    const detail = related.map((item) => item.term + '（' + item.relation + '）').join('、');
    el.innerHTML = '<span class="scope-text" title="' + esc(detail) + '">按知识图谱扩展检索：' + esc(parts.join('；')) + '</span><button type="button" class="scope-toggle" aria-pressed="' + String(feed.scope === 'direct') + '" title="只看直接提及这家公司名称、别名或代码的">只看直接提及</button>';
  }
  $('feed-scope')?.addEventListener('click', (event) => {
    if (!event.target.closest('.scope-toggle')) return;
    feed.scope = feed.scope === 'direct' ? 'all' : 'direct';
    store.set('market.scope', feed.scope);
    if (typeof state !== 'undefined') state.scope = feed.scope;
    renderScope();
    if (typeof renderSentiments === 'function') renderSentiments();
    renderMinutes();
  });

  /** 当前股票的「最新」和「纪要」：股票切换、资料库或知识图谱更新时重新取。 */
  async function loadFeed(snapshot) {
    if (!snapshot?.symbol || !$('feed-panel-latest')) return;
    const seq = ++feed.seq;
    feed.symbol = snapshot.symbol;
    const name = snapshot.shortName || snapshot.symbol;
    const query = 'symbol=' + enc(snapshot.symbol) + '&name=' + enc(snapshot.shortName ?? '');
    try {
      const data = await api('/api/wiki/latest?' + query);
      if (seq === feed.seq) feed.latest = { ...data, name };
    } catch (error) {
      if (seq === feed.seq) feed.latest = { records: [], error: error.message, name };
    }
    if (seq === feed.seq) renderLatest();
    try {
      const data = await api('/api/wiki/minutes?' + query);
      if (seq === feed.seq) feed.minutes = { ...data, name };
    } catch (error) {
      if (seq === feed.seq) feed.minutes = { items: [], total: 0, folders: null, error: error.message, name };
    }
    if (seq === feed.seq) renderMinutes();
  }

  /** 后台正在做什么，用一句话放在「最新」上面；没有在做就不显示。 */
  function latestStatus() {
    const s = ws.status;
    const job = s?.job;
    if (job && ACTIVE_JOB.includes(job.status)) {
      const done = job.ingested + job.skipped + job.failed;
      return esc((job.status === 'approval' ? '后台整理等待你授权' : '后台正在' + jobSubject(job)) + ' · ' + done + '/' + job.total);
    }
    if (s?.auto?.available && !s.auto.enabled) return '自动整理已暂停 · <button type="button" class="link-btn" data-goto-page="assets">去资产页继续</button>';
    return '';
  }
  function emptyLatest(data) {
    const s = ws.status;
    const name = esc(data.name ?? '');
    if (s?.job && ACTIVE_JOB.includes(s.job.status)) return '后台正在' + jobSubject(s.job) + '，整理出和「' + name + '」有关的动态后会出现在这里。';
    if (s && s.auto && !s.auto.available) return '暂时没有「' + name + '」的最新动态。当前版本的 MiniMax Code 不支持后台自动整理。';
    if (s?.auto && !s.auto.enabled) return '暂时没有「' + name + '」的最新动态。自动整理已暂停，可以在资产页继续。';
    if (!(data.folders ?? s?.folders?.length)) return '暂时没有「' + name + '」的最新动态。后台会自动扫描它和自选股的舆情，记下边际变化；关联资料文件夹后，研报、纪要里的新事实也会出现在这里。';
    return '暂时没有「' + name + '」的最新动态。资料库和舆情里出现新的事实或边际变化时，后台会自动记在这里。';
  }
  function renderLatest() {
    const panel = $('feed-panel-latest');
    if (!panel) return;
    const data = feed.latest;
    const all = data?.records ?? [];
    if ($('latest-caption')) $('latest-caption').textContent = data && !data.error ? all.length + ' 条' : '';
    if (feed.tab !== 'latest') return;
    if (!data) { panel.innerHTML = '<div class="state" role="status">载入中…</div>'; return; }
    if (data.error) { panel.innerHTML = `<div class="state error-text" role="alert">最新动态暂时无法读取：${esc(data.error)}</div>`; return; }
    const status = latestStatus();
    if (!all.length) {
      panel.innerHTML = (status ? `<p class="feed-status">${status}</p>` : '') + `<div class="minutes-empty"><p>${emptyLatest(data)}</p>${!(data.folders ?? ws.status?.folders?.length) ? '<button type="button" class="btn small" data-goto-page="assets" data-goto-tab="files">去关联文件夹</button>' : ''}</div>`;
      return;
    }
    const terms = feedTerms();
    const items = terms.length ? all.filter((record) => matchesTerms([record.text, record.entity, record.from, record.to].join(' ').toLowerCase(), terms)) : all;
    panel.innerHTML = (status ? `<p class="feed-status">${status}</p>` : '')
      + (items.length ? `<ol class="record-list feed-records">${items.map((record) => recordItem(record, { entity: record.related })).join('')}</ol>` : '<p class="minutes-empty">没有匹配的动态。</p>')
      + '<p class="feed-foot"><button type="button" class="link-btn" data-latest-all>在资产 · 边际变化里查看全部</button></p>';
  }
  $('feed-panel-latest')?.addEventListener('click', (event) => {
    if (event.target.closest('[data-latest-all]')) {
      showPage('assets');
      showAssetTab('changes');
      const title = feed.latest?.company?.title ?? '';
      cw.query = title;
      $('changes-search').value = title;
      renderChanges();
      return;
    }
    const entity = event.target.closest('[data-open-page]');
    if (entity) void openPage(entity.dataset.openPage, { mode: 'graph' });
  });

  function renderMinutes() {
    const panel = $('feed-panel-minutes');
    if (!panel) return;
    const data = feed.minutes;
    const all = data?.items ?? [];
    if ($('minutes-caption')) $('minutes-caption').textContent = data && !data.error ? all.length + ' 份' : '';
    if (feed.tab !== 'minutes') return;
    const query = feedQuery();
    const terms = feedTerms();
    const scoped = feed.scope === 'direct' ? all.filter((item) => !item.related) : all;
    const items = terms.length ? scoped.filter((item) => matchesTerms([item.title, item.note, item.excerpt, item.display].join(' ').toLowerCase(), terms)) : scoped;
    if (!data) { panel.innerHTML = '<div class="state" role="status">载入中…</div>'; return; }
    if (data.error) { panel.innerHTML = `<div class="state error-text" role="alert">纪要暂时无法读取：${esc(data.error)}</div>`; return; }
    if (!data.folders) {
      panel.innerHTML = '<div class="minutes-empty"><p>纪要来自「资产」里的资料库。关联放纪要的文件夹后，这里会列出和当前股票相关的纪要。</p><button type="button" class="btn small" data-goto-page="assets" data-goto-tab="files">去关联文件夹</button></div>';
      return;
    }
    if (!items.length) {
      panel.innerHTML = `<div class="minutes-empty"><p>${query ? '没有匹配的纪要。' : feed.scope === 'direct' && all.length ? '没有直接提及「' + esc(data.name ?? '') + '」的纪要；关掉「只看直接提及」能看到 ' + all.length + ' 份通过相邻节点找到的。' : '资料库里还没有和「' + esc(data.name ?? '') + '」相关的纪要。'}</p><p class="hint">文件名带“纪要、调研、交流、电话会、路演、专家”等字样的会自动识别；名字对不上的纪要，后台整理时 Agent 读完会标到对应的股票上。</p></div>`;
      return;
    }
    panel.innerHTML = items.map(minutesRow).join('') + (data.partial ? '<p class="hint minutes-caption">部分文件还没检索完，稍后会补全</p>' : '');
  }
  function minutesRow(item) {
    const dateTitle = { agent: 'Agent 从资料里识别的日期', filename: '文件名里的日期', mtime: '没有找到资料日期，这是文件修改时间' }[item.dateSource] ?? '';
    const tags = [item.relevance === 'core' ? '核心' : item.relevance === 'mentioned' ? '提及' : '', item.tagged ? 'Agent 标注' : '', item.summaryPage ? '' : '待整理'].filter(Boolean);
    const folder = item.display.split('/').slice(0, -1).join('/');
    // 只靠相邻节点匹配上的纪要：标出是通过哪个环节 / 产品 / 竞争对手找到的。
    const via = item.related ? [...new Set(item.reasons.map((reason) => String(reason).split('· ').slice(1).join('· ')).filter(Boolean))] : [];
    const matchTag = item.related ? `<span class="match-tag" title="通过知识图谱扩展检索到：${esc(item.reasons.join('；'))}">关联 · ${esc(via[0] ?? '相邻节点')}</span>` : '';
    return `<article class="news-item"><button type="button" class="news-entry" data-minutes-key="${esc(item.key)}" aria-label="查看纪要 ${esc(item.title)}"><span class="news-meta"><span class="source-name minutes">纪要</span>${matchTag}${folder ? `<span class="minutes-path" title="${esc(item.display)}">${esc(folder)}</span>` : ''}<time datetime="${esc(item.date)}" title="${esc(dateTitle)}">${esc(item.date)}${item.dateSource === 'mtime' ? ' · 修改时间' : ''}</time></span><span class="news-title">${esc(item.title)}</span>${item.note || item.excerpt ? `<span class="news-summary">${esc(item.note || item.excerpt)}</span>` : ''}${tags.length ? `<span class="news-tags">${tags.map((tag) => `<span>${esc(tag)}</span>`).join('')}</span>` : ''}</button></article>`;
  }
  $('feed-panel-minutes')?.addEventListener('click', (event) => {
    const entry = event.target.closest('[data-minutes-key]');
    if (entry) openMinutes(entry.dataset.minutesKey);
  });
  function openMinutes(key) {
    const item = feed.minutes?.items?.find((entry) => entry.key === key);
    if (!item) return;
    feed.minutesKey = key;
    $('minutes-title').textContent = item.title;
    $('minutes-meta').textContent = ['纪要', item.date + (item.dateSource === 'mtime' ? '（修改时间）' : ''), item.display].join(' · ');
    $('minutes-note').textContent = item.note || '';
    $('minutes-note').hidden = !item.note;
    $('minutes-excerpt').textContent = item.excerpt || '';
    $('minutes-excerpt').hidden = !item.excerpt;
    $('minutes-reasons').textContent = (item.reasons.length ? '对应依据：' + item.reasons.join('、') : '') + (item.summaryPage ? '' : (item.reasons.length ? '。' : '') + '还没整理进知识图谱，后台会自动整理');
    $('minutes-graph').hidden = !item.summaryPage;
    $('minutes-dialog').showModal();
  }
  $('minutes-close').addEventListener('click', () => $('minutes-dialog').close());
  $('minutes-open').addEventListener('click', () => { if (feed.minutesKey) void openExternal({ key: feed.minutesKey }); });
  $('minutes-graph').addEventListener('click', () => {
    const item = feed.minutes?.items?.find((entry) => entry.key === feed.minutesKey);
    $('minutes-dialog').close();
    if (item?.summaryPage) void openPage(item.summaryPage.id, { mode: 'graph' });
  });

  // 舆情存入资料库：在详情里单条存入；只传 id，原文由 Node 从已抓取的舆情里取，存入后后台自动整理。
  async function importSentiments(ids) {
    const symbol = typeof state !== 'undefined' ? state.snapshot?.symbol : null;
    if (!symbol || !ids.length) return null;
    const result = await api('/api/wiki/clips', { method: 'POST', body: JSON.stringify({ symbol, ids }) });
    const set = new Set(ids);
    for (const item of state.snapshot?.sentiments ?? []) if (set.has(item.id)) item.clipped = true;
    if (typeof renderSentiments === 'function') renderSentiments();
    return result;
  }
  function onSentimentDetail(item) {
    const row = $('detail-import-row');
    if (!row || !item) return;
    feed.detailId = item.id;
    row.hidden = false;
    $('detail-import').hidden = Boolean(item.clipped);
    $('detail-import').disabled = false;
    $('detail-import-status').innerHTML = item.clipped ? '已存入资料库，后台会自动整理进知识图谱 · <button type="button" class="link-btn" data-goto-page="assets" data-goto-tab="files">查看</button>' : '';
  }
  $('detail-import')?.addEventListener('click', async () => {
    if (!feed.detailId) return;
    $('detail-import').disabled = true;
    try {
      await importSentiments([feed.detailId]);
      const item = state.snapshot?.sentiments?.find((entry) => entry.id === feed.detailId);
      if (item) onSentimentDetail(item);
    } catch (error) {
      $('detail-import-status').textContent = error.message;
      $('detail-import').disabled = false;
    }
  });
  $('detail-link')?.addEventListener('click', (event) => {
    const href = $('detail-link').href;
    if (!href) return;
    event.preventDefault();
    void openExternal({ url: href }, href);
  });

  /** 打开知识图谱里的一个节点；mode 指定在图谱中还是产业链中定位，不指定时沿用当前视图。 */
  async function openPage(idOrName, { mode } = {}) {
    if (ws.page !== 'assets') showPage('assets');
    if (ws.tab !== 'graph') showAssetTab('graph');
    if (!ws.graph) await loadGraph();
    const id = ws.byId.has(idOrName) ? idOrName : resolveName(idOrName);
    const page = id ? ws.byId.get(id) : null;
    const industry = page ? industryOf(page) : null;
    const wantChain = mode === 'chain' || (mode === undefined && ws.mode === 'chain');
    if (wantChain && industry) {
      if (ws.mode !== 'chain' || nameKey(industry) !== nameKey(ws.chainIndustry)) { ws.mode = 'chain'; ws.chainIndustry = industry; renderIndustryOptions(); renderCanvas(); }
    } else if (ws.mode === 'chain') {
      ws.mode = 'graph';
      renderCanvas();
    }
    await select(id ?? idOrName);
    const el = document.querySelector('#chain-view [data-selected]') ?? graphSvg.querySelector('.gnode.selected');
    el?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
  }

  // ---------- 事件 ----------
  const pendingKinds = new Set();
  let eventTimer = 0;
  function onEvent(data) {
    pendingKinds.add(data?.kind || 'all');
    clearTimeout(eventTimer);
    eventTimer = setTimeout(flushEvents, 300);
  }
  async function flushEvents() {
    const kinds = new Set(pendingKinds);
    pendingKinds.clear();
    const has = (kind) => kinds.has(kind) || kinds.has('all');
    const tasks = [];
    // 后台任务进度、授权请求、自动整理状态在所有页面都要更新（顶栏标签、弹窗、提示条）。
    if (kinds.size) tasks.push(loadStatus());
    const snapshot = typeof state !== 'undefined' ? state.snapshot : null;
    if (snapshot && (has('records') || has('pages') || has('files') || has('folders'))) tasks.push(loadFeed(snapshot));
    if (ws.loaded) {
      if (has('pages') || has('folders')) tasks.push(loadGraph());
      if (has('files') || has('folders')) tasks.push(loadFiles());
      if ((has('records') || has('pages')) && cw.loaded) tasks.push(loadChanges());
      if (has('records') && ws.selected && !has('pages')) tasks.push(loadDetail(ws.selected, { quiet: true }));
    }
    await Promise.allSettled(tasks);
  }
  // 后台标签页的定时器会被浏览器节流：页面重新可见时立刻处理积压的更新。
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) return;
    if (pendingKinds.size) { clearTimeout(eventTimer); void flushEvents(); }
    else void loadStatus();
  });
  window.addEventListener('resize', () => requestAnimationFrame(redrawCanvasOverlays));
  window.addEventListener('pagehide', () => canvasObserver?.disconnect(), { once: true });

  window.stockWiki = {
    showPage,
    openPage,
    onEvent,
    onSnapshot(snapshot) { renderScope(); if (snapshot?.symbol && snapshot.symbol !== feed.symbol) loadFeed(snapshot); },
    refreshRelated() { if (typeof state !== 'undefined' && state.snapshot) loadFeed(state.snapshot); },
    onSentimentDetail,
    onSentimentsRendered() {},
    viewState() { return { page: ws.page, assetsTab: ws.tab, marketFeed: feed.tab, wikiView: ws.mode, wikiPage: ws.selected ?? '', wikiIndustry: ws.mode === 'chain' ? (ws.chainIndustry === 'all' ? '' : ws.chainIndustry) : (ws.industry === 'all' ? '' : ws.industry) }; },
  };

  ws.bootAt = Date.now();
  if (typeof state !== 'undefined' && state.snapshot) loadFeed(state.snapshot);
  showFeed(feed.tab, { quiet: true });
  void loadStatus();
  showPage(store.get('market.page') || 'market');
})();
