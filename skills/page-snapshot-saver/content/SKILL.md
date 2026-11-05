---
name: page-snapshot-saver
description: |
  Add a "Save current page as standalone HTML" button to any single-file HTML deliverable (报告/贺卡/邀请函/dashboard/落地页/活动页). Use when the user wants a 保存/save/snapshot/下载 button that turns the current DOM into a self-contained .html file via Blob + <a download>, or says things like "把整个页面保存下来", "我要把这个页面发给同事", "页面单独发出去", "下载当前页面为 HTML", "做成可独立打开的 HTML". Produces a self-contained file (no external assets inlined, but inlined base64/JS/CSS rides along) with polished idle → saving → saved UI, re-entrancy guard, optional Ctrl/Cmd+S shortcut, file-size feedback, and a snapshot metadata comment. Do NOT use for: saving values to localStorage (state persistence, not file export), server-side file uploads, PDF/PNG export, or pages where the user only wants to save specific form values.
---

# Page Snapshot Saver

把"保存当前页面为独立 HTML"这件事做对的小工具，零依赖、单 IIFE、drop-in。

## Inputs to collect
- 注入位置：默认在 `</body>` 之前；按钮样式默认 `position:fixed` 右上角浮动
- 文件名前缀：默认用 `<title>` 净化为安全文件名；想自定义就在按钮上加 `data-snapshot-saver-prefix="my-report"`
- 是否启用 Ctrl/Cmd+S 快捷键（默认开）；要关闭加 `data-snapshot-saver-keyboard="false"`
- 是否自动关掉弹窗/灯箱再保存（默认开，关闭 `.flow-lightbox.show`、`.modal.show`、`.lightbox.show` 三种常见类）；要自定义关哪些加 `data-snapshot-saver-cleanup-selectors=".a.show,.b.open"`
- 颜色/字体：在 `body` 上覆盖 CSS 变量 `--pss-bg / --pss-fg / --pss-border / --pss-shadow / --pss-shadow-hover / --pss-radius / --pss-font`

## Procedure

### 1. 把按钮 + 状态机 + 快捷键整段塞进目标 HTML 的 `</body>` 之前
用下面这一整块（含 CSS + 按钮 DOM + JS）。零外部依赖，IIFE 查找 `[data-snapshot-saver]` 自动接管，不需要改 HTML 其它部分。

```html
<!-- === Page Snapshot Saver — drop-in === -->
<style>
.pss-btn{position:fixed;top:14px;right:14px;z-index:9999;
  display:inline-flex;align-items:center;gap:7px;
  padding:9px 18px;font-size:13px;font-weight:800;letter-spacing:.5px;
  color:var(--pss-fg,#3B1E0E);
  background:var(--pss-bg,linear-gradient(135deg,#FFE066,#FFB800));
  border:2px solid var(--pss-border,#E09000);
  border-radius:var(--pss-radius,12px);cursor:pointer;
  box-shadow:var(--pss-shadow,0 6px 20px rgba(255,150,0,.4));
  transition:transform .15s,box-shadow .15s,opacity .15s;
  font-family:var(--pss-font,inherit)}
.pss-btn:hover{transform:translateY(-1px);box-shadow:var(--pss-shadow-hover,0 10px 26px rgba(255,150,0,.5))}
.pss-btn:active{transform:translateY(0)}
.pss-btn[data-state="saving"]{opacity:.7;pointer-events:none}
.pss-btn .pss-icon{font-size:15px;line-height:1}
@media print{.pss-btn{display:none}}
</style>
<button class="pss-btn" type="button" data-snapshot-saver>
  <span class="pss-icon">💾</span><span class="pss-label">保存</span>
</button>
<script>
(function(){
  'use strict';
  var btn = document.querySelector('[data-snapshot-saver]');
  if (!btn) return;

  function p2(n){return n<10?'0'+n:''+n}
  function fmtStamp(d){
    return d.getFullYear()+p2(d.getMonth()+1)+p2(d.getDate())+
           '-'+p2(d.getHours())+p2(d.getMinutes())+p2(d.getSeconds());
  }
  function fmtSize(b){
    if(b<1024)return b+' B';
    if(b<1048576)return(b/1024).toFixed(1)+' KB';
    return(b/1048576).toFixed(2)+' MB';
  }
  function cleanFilename(s){
    return (s||'page').replace(/[\/\\:*?"<>|\r\n\t]+/g,'_').slice(0,60)||'page';
  }

  var prefix   = btn.getAttribute('data-snapshot-saver-prefix') ||
                 cleanFilename(document.title||'page');
  var useKbd   = btn.getAttribute('data-snapshot-saver-keyboard') !== 'false';
  var useClean = btn.getAttribute('data-snapshot-saver-cleanup')  !== 'false';
  var cleanSel = (btn.getAttribute('data-snapshot-saver-cleanup-selectors') ||
                  '.flow-lightbox.show,.modal.show,.lightbox.show').split(',');
  var labelIdle = btn.getAttribute('data-snapshot-saver-label') || '保存';

  var busy = false, resetTimer = null;
  var IDLE_HTML = '<span class="pss-icon">💾</span><span class="pss-label">'+labelIdle+'</span>';

  function setLabel(text){
    btn.querySelector('.pss-label').textContent = text;
  }
  function setState(s, label){
    btn.setAttribute('data-state', s);
    setLabel(label);
  }
  function finishSave(success, size){
    busy = false;
    if (success && size != null)      setState('saved',  '已保存 · ' + fmtSize(size));
    else if (success)                 setState('saved',  '已保存');
    else                              setState('failed', '保存失败');
    if (resetTimer) clearTimeout(resetTimer);
    resetTimer = setTimeout(function(){
      btn.setAttribute('data-state', 'idle');
      btn.innerHTML = IDLE_HTML;
      resetTimer = null;
    }, 1600);
  }
  function cleanupTransientUI(){
    if (!useClean) return;
    cleanSel.forEach(function(sel){
      var s = sel.trim(); if (!s) return;
      try { document.querySelectorAll(s).forEach(function(el){
        el.classList.remove('show','open','active');
      }); } catch(e){}
    });
    if (document.body.style.overflow === 'hidden') document.body.style.overflow = '';
    if (document.activeElement && document.activeElement.blur) document.activeElement.blur();
  }
  function doSave(){
    cleanupTransientUI();
    var now = new Date();
    var stamp = now.toISOString();
    var head = '<!DOCTYPE html>\n<!-- snapshot-saved: '+stamp+' -->\n';
    var blob = new Blob([head + document.documentElement.outerHTML],
                        { type:'text/html;charset=utf-8' });
    var filename = prefix + '-' + fmtStamp(now) + '.html';
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = filename; a.style.display = 'none';
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    // 延迟 revoke，部分浏览器立即 revoke 会导致下载到 0 字节
    setTimeout(function(){ URL.revokeObjectURL(url); }, 1000);
    return { size: blob.size, filename: filename };
  }
  function save(){
    if (busy) return;
    busy = true;
    setState('saving', '保存中…');
    // 让 UI 先渲染一帧再干重活（大页面避免点击瞬间卡死）
    setTimeout(function(){
      try { var r = doSave(); finishSave(true, r.size); }
      catch(err){ console.error('[snapshot-saver]', err); finishSave(false); }
    }, 30);
  }

  btn.addEventListener('click', save);

  if (useKbd) {
    document.addEventListener('keydown', function(e){
      if (!(e.ctrlKey || e.metaKey) || e.shiftKey || e.altKey) return;
      if (e.key !== 's' && e.key !== 'S') return;
      var ae = document.activeElement, tag = ae && ae.tagName;
      // 输入框/可编辑元素里让浏览器原生的"保存网页"走默认
      if (tag === 'INPUT' || tag === 'TEXTAREA' || (ae && ae.isContentEditable)) return;
      e.preventDefault();
      save();
    });
  }
})();
</script>
<!-- === /Page Snapshot Saver === -->
```

### 2. 验证 4 件事
- 点击按钮 → 浏览器下载 `<title净化>-YYYYMMDD-HHMMSS.html`，按钮先 ⏳ 保存中… → ✓ 已保存 · 12.3 KB → 💾 保存（1.6s 内）
- 反复点 → 每次都成功下载，按钮状态不会卡在"保存中"
- Ctrl/Cmd+S → 同样触发（input/textarea/contenteditable 聚焦时除外）
- 打开流程图灯箱后保存 → 灯箱在下载前被关掉，保存出来的 HTML 是干净状态

### 3. 告诉用户 3 个限制
- 保存的 HTML 仍依赖原服务器/CDN 上的**外部资源**（`<img src="https://...">`、`<link href="/css/...">` 这些 URL 不会变），只是 HTML 字符串本身被独立打包
- 已经 inlined 的资源（base64 图片、内联 `<style>`/`<script>`）会**完整随行**，离线打开正常
- 文件顶部会带一行 `<!-- snapshot-saved: <ISO 时间戳> -->` 注释，方便追溯"这文件是哪天哪秒从哪页存的"

## Output contract
- 一个**自包含**的 `.html` 文件下载到用户本地
- 按钮在 1.6s 内完成一次 `idle → saving → saved → idle` 循环
- 并发保护：`busy` 变量确保 save 逻辑同时只有一份在跑，rapid click 不会产生半成品文件
- 文件名格式：`<prefix>-YYYYMMDD-HHMMSS.html`，秒级精度避免同一前缀在同一天被覆盖
- 已保存状态会带文件大小反馈（B / KB / MB）

## Failure handling
- `document.documentElement.outerHTML` 抛错（极少见，循环引用 / Proxy 死循环）→ 按钮显示 ⚠ 保存失败，1.6s 后回 idle，控制台打 `[snapshot-saver] <err>`
- `URL.createObjectURL` 不存在（极老浏览器）→ 走 catch 路径同上
- 保存过程中用户又点了一次 → 第二次点击被 `busy=true` 挡住，无副作用
- 用户在 textarea/input 聚焦时按 Ctrl+S → 不拦截，让浏览器原生的"另存为"走默认
- 页面很大（>20MB）→ UI 短暂转圈；Chrome 可能弹"是否保留下载"提示

## Examples

**例 1：用户拿一份单文件 HTML 报告说"加个保存按钮，我要把它单独发同事"**

在 `</body>` 之前整段插入「drop-in」片段，`<title>` 是 "麦麦人情味-感恩有你 V5"，下载自动得到 `麦麦人情味-感恩有你-V5-20260827-153012.html`，按钮在 1.6s 内显示"已保存 · 177.2 KB"。

**例 2：用户说"按钮别放右上角，嵌进我现有的工具栏里；颜色也跟着我的主题"**

```html
<!-- 容器：用户自己的工具栏 -->
<div class="my-toolbar">
  <button class="pss-btn" type="button" data-snapshot-saver
          style="position:static">
    <span class="pss-icon">💾</span><span class="pss-label">下载</span>
  </button>
</div>
<style>body{--pss-bg:#1f6feb;--pss-border:#1657b8;--pss-fg:#fff;
  --pss-shadow:0 4px 14px rgba(31,111,235,.4);}</style>
```

按钮就内嵌进工具栏、跟着蓝色主题走，文件名/快捷键/状态机逻辑不变。
