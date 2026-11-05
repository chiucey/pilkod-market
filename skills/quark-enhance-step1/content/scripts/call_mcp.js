#!/usr/bin/env node
/**
 * call_mcp.js  —  第一步 ② 夸克扫描 MCP 调用器（计费：每图 1 次）
 *
 * 特性：
 *   - MCP Streamable HTTP 三步握手（initialize → notifications/initialized → tools/call）
 *   - JSON / SSE 双格式响应解析
 *   - 大 base64 走 @args.json 文件传参（命令行上限约 32KB，直接传必截断）
 *   - 返回图像与"原始响应 JSON"双落盘（成本纪律：结果可复用，永不重调）
 *   - stdout 输出一行机器可读 JSON，便于上层脚本消费
 *
 * 用法：
 *   node call_mcp.js --list
 *   node call_mcp.js scan_certificate_invoice_enhance @_out/x.args.json --outdir ./_out --name x
 *
 * 密钥来源（优先级）：环境变量 QUARK_AI_API_KEY > 同目录 config.json > 环境变量 QUARK_KEY_FILE 指向的文件
 */

const fs = require('fs');
const path = require('path');

const ENDPOINT = process.env.QUARK_ENDPOINT || 'https://scan-mcp.quark.cn/mcp';

function loadKey() {
  if (process.env.QUARK_AI_API_KEY) return process.env.QUARK_AI_API_KEY.trim();
  const cfgPath = process.env.QUARK_CONFIG || path.join(__dirname, '..', 'config.json');
  try {
    if (fs.existsSync(cfgPath)) {
      const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
      const k = cfg?.quark?.aiApiKey;
      if (k && !k.startsWith('<')) return String(k).trim();
    }
  } catch (e) { /* ignore */ }
  const keyFile = process.env.QUARK_KEY_FILE;
  if (keyFile && fs.existsSync(keyFile)) return fs.readFileSync(keyFile, 'utf8').trim();
  return '';
}

function parseArgs(argv) {
  const out = { positional: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const v = (argv[i + 1] && !argv[i + 1].startsWith('--')) ? argv[++i] : true;
      out.flags[k] = v;
    } else out.positional.push(a);
  }
  return out;
}

const SESSION = { id: null };
async function rpc(id, method, params) {
  const headers = { 'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream' };
  if (SESSION.id) headers['mcp-session-id'] = SESSION.id;
  const res = await fetch(BASE, { method: 'POST', headers, body: JSON.stringify({ jsonrpc: '2.0', id, method, params }) });
  const sid = res.headers.get('mcp-session-id');
  if (sid) SESSION.id = sid;
  const ct = res.headers.get('content-type') || '';
  const body = await res.text();
  let payload = null;
  if (ct.includes('text/event-stream')) {
    for (const line of body.split('\n')) {
      if (line.startsWith('data:')) { try { payload = JSON.parse(line.slice(5).trim()); } catch (e) { } }
    }
  } else { try { payload = JSON.parse(body); } catch (e) { } }
  return { status: res.status, payload, raw: body };
}

const args = parseArgs(process.argv.slice(2));
const apiKey = loadKey();
if (!apiKey) {
  console.error('缺少密钥：请设置环境变量 QUARK_AI_API_KEY，或准备 config.json / QUARK_KEY_FILE。');
  process.exit(2);
}
const BASE = ENDPOINT + '?aiApiKey=' + encodeURIComponent(apiKey);

const tool = args.positional[0] || (args.flags.list ? '--list' : null);
if (!tool) { console.error('用法: node call_mcp.js <工具名|--list> [@args.json|json] [--outdir DIR] [--name BASE]'); process.exit(1); }

const outdir = typeof args.flags.outdir === 'string' ? args.flags.outdir : './_out';
const baseName = typeof args.flags.name === 'string' ? args.flags.name : ('call_' + Date.now());
if (outdir) fs.mkdirSync(outdir, { recursive: true });          // 成本纪律：先建目录，避免存盘失败重调
const rawDir = path.join(outdir, 'mcp_raw');
if (args.flags['keep-raw'] !== false) fs.mkdirSync(rawDir, { recursive: true });

function readArgsFile(v) {
  if (typeof v !== 'string') return {};
  if (v.startsWith('@')) return JSON.parse(fs.readFileSync(v.slice(1), 'utf8'));
  return JSON.parse(v);
}

(async () => {
  const init = await rpc(1, 'initialize', {
    protocolVersion: '2025-03-26', capabilities: {}, clientInfo: { name: 'quark-enhance-step1', version: '1.0' }
  });
  if (init.status !== 200 || !init.payload || init.payload.error) {
    console.error('INIT_FAIL:', init.status, String(init.raw).slice(0, 500));
    process.exit(1);
  }
  await fetch(BASE, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream', ...(SESSION.id ? { 'mcp-session-id': SESSION.id } : {}) },
    body: JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' })
  });

  if (tool === '--list') {
    const r = await rpc(2, 'tools/list', {});
    const tools = (r.payload && r.payload.result && r.payload.result.tools) || [];
    console.log('TOOLS (' + tools.length + '):');
    tools.forEach(t => console.log('·', t.name, '—', String(t.description || '').slice(0, 80)));
    return;
  }

  const t0 = Date.now();
  const r = await rpc(2, 'tools/call', { name: tool, arguments: readArgsFile(args.positional[1]) });
  const elapsed = Date.now() - t0;

  if (!r.payload) { console.error('BAD_RESPONSE:', r.status, String(r.raw).slice(0, 500)); process.exit(1); }
  if (r.payload.error) { console.error('ERROR:', JSON.stringify(r.payload.error)); process.exit(1); }
  const content = r.payload.result;
  if (content && content.isError) {
    console.error('TOOL_ERROR:', (content.content || []).map(x => x.text || '').join('\n'));
    process.exit(1);
  }

  // 原始响应落盘（成本纪律：留档，可复用、可事后分析）
  const rawPath = path.join(rawDir, baseName + '.json');
  fs.writeFileSync(rawPath, JSON.stringify(r.payload, null, 1), 'utf8');

  // 提取内容
  let info = null;
  const txt = (content && content.content || []).find(x => x.type === 'text');
  if (txt) { try { info = JSON.parse(txt.text); } catch (e) { info = { _text: txt.text }; } }
  const data = (info && info.data) || {};
  const imgB64 = data.ImageInfo && data.ImageInfo[0] && data.ImageInfo[0].ImageBase64;
  const pdfB64 = data.TypesetInfo && data.TypesetInfo[0] && data.TypesetInfo[0].FileBase64;
  const ocrTxt = data.OcrInfo && data.OcrInfo[0] && data.OcrInfo[0].Text;

  let imgPath = null, pdfPath = null, imgSize = null;
  if (imgB64) {
    imgPath = path.join(outdir, 'enhanced', baseName + '.jpg');
    fs.mkdirSync(path.dirname(imgPath), { recursive: true });
    const buf = Buffer.from(imgB64, 'base64');
    fs.writeFileSync(imgPath, buf);
    imgSize = buf.length;
    if (data.ImageInfo[0].Width) imgSize = imgSize; // 尺寸另记于 dimensions
  }
  if (pdfB64) {
    pdfPath = path.join(outdir, 'enhanced', baseName + '.pdf');
    fs.mkdirSync(path.dirname(pdfPath), { recursive: true });
    const buf = Buffer.from(pdfB64, 'base64');
    fs.writeFileSync(pdfPath, buf);
  }

  console.log(JSON.stringify({
    ok: true,
    tool,
    elapsed_ms: elapsed,
    billing_calls: 1,
    image: imgPath,
    pdf: pdfPath,
    image_bytes: imgB64 ? Buffer.from(imgB64, 'base64').length : null,
    dimensions: data.ImageInfo && data.ImageInfo[0]
      ? { width: data.ImageInfo[0].Width, height: data.ImageInfo[0].Height, angle: data.ImageInfo[0].Angle }
      : null,
    ocr_chars: ocrTxt ? String(ocrTxt).length : null,
    raw_response: rawPath
  }, null, 2));
})().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
