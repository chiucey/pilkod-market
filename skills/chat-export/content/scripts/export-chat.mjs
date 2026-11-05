#!/usr/bin/env node
/**
 * export-chat.mjs — 把 Mavis 会话消息 JSON 转成 Markdown / HTML / JSON。
 *
 *   node export-chat.mjs --raw <raw.json> --title "标题" --session-id 123 \
 *     --agent Mavis --model MiniMax-M3.1-Flash \
 *     --outdir /workspace/output/chat-export --basename "标题"
 *
 * 输入兼容三种外层包装：
 *   1) {"ok":true,"response":{"messages":[...],"has_more":bool}}
 *   2) {"messages":[...]}
 *   3) {"content":[{"type":"text","text":"<上面任一种的 JSON 字符串>"}]}
 * 也接受直接是 messages 数组。
 */

import fs from "node:fs";
import path from "node:path";

// ------------------------------------------------------------------ 参数

function parseArgs(argv) {
  const a = {
    raw: null, outdir: "/workspace/output/chat-export", basename: null,
    title: null, sessionId: null, agent: null, model: null,
    thinking: false, toolOutput: false, maxToolOutput: 4000,
    formats: "md,html,json",
  };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    const next = () => argv[++i];
    switch (k) {
      case "--raw": a.raw = next(); break;
      case "--outdir": a.outdir = next(); break;
      case "--basename": a.basename = next(); break;
      case "--title": a.title = next(); break;
      case "--session-id": a.sessionId = next(); break;
      case "--agent": a.agent = next(); break;
      case "--model": a.model = next(); break;
      case "--thinking": a.thinking = true; break;
      case "--tool-output": a.toolOutput = true; break;
      case "--max-tool-output": a.maxToolOutput = Number(next()); break;
      case "--formats": a.formats = next(); break;
      case "-h": case "--help":
        console.log(`export-chat.mjs
  --raw <file>              session messages 的原始 JSON 文件（必填）
  --outdir <dir>            输出目录（默认 /workspace/output/chat-export）
  --basename <name>         输出文件名（不含扩展名）
  --title <name>            会话标题，写进文件头
  --session-id <id>         会话 ID，写进文件头
  --agent <name>            智能体名
  --model <id>              模型 ID
  --thinking                包含思考过程
  --tool-output             包含工具调用的原始返回
  --max-tool-output <n>     单条工具输出字符上限（默认 4000）
  --formats md,html,json    要生成哪些格式`);
        process.exit(0);
        break;
      default:
        if (k.startsWith("--")) {
          console.error(`未知参数: ${k}`);
          process.exit(2);
        }
    }
  }
  if (!a.raw) {
    console.error("✗ 缺少 --raw");
    process.exit(2);
  }
  return a;
}

// ------------------------------------------------------------------ 读取

function loadPayload(file) {
  const raw = fs.readFileSync(file, "utf8");
  let obj;
  try {
    obj = JSON.parse(raw);
  } catch {
    obj = null;
  }
  if (obj && typeof obj === "object" && Array.isArray(obj.content)) {
    const part = obj.content.find((p) => p && p.type === "text");
    if (part) {
      try { obj = JSON.parse(part.text); } catch { /* 保持原样 */ }
    }
  }
  if (obj && typeof obj === "object" && obj.response && typeof obj.response === "object") {
    obj = obj.response;
  }
  return obj;
}

function extractMessages(payload) {
  if (Array.isArray(payload)) return { messages: payload, meta: {} };
  if (payload && typeof payload === "object" && Array.isArray(payload.messages)) {
    return { messages: payload.messages, meta: payload };
  }
  throw new Error("输入里找不到 messages 数组——确认文件是 session messages 的返回");
}

// ------------------------------------------------------------------ 工具函数

const TZ_OFFSET_MS = 8 * 3600 * 1000; // UTC+8

function ts(ms, withDate = true) {
  if (typeof ms !== "number") return "";
  const d = new Date(ms + TZ_OFFSET_MS).toISOString();
  return withDate ? d.slice(0, 19).replace("T", " ") : d.slice(11, 19);
}

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function briefArgs(args, limit = 180) {
  if (!args) return "";
  const s = String(args).replace(/\s+/g, " ").trim();
  return s.length > limit ? s.slice(0, limit) + " …" : s;
}

function toolResultText(data) {
  if (!data) return "";
  let d = data;
  if (typeof d === "string") {
    try { d = JSON.parse(d); } catch { return d; }
  }
  if (d && typeof d === "object" && Array.isArray(d.content)) {
    const parts = d.content.filter((p) => p && p.type === "text").map((p) => p.text ?? "");
    if (parts.length) return parts.join("\n");
  }
  if (d && typeof d === "object") return JSON.stringify(d, null, 2);
  return String(d);
}

function cut(text, limit) {
  if (limit && text.length > limit) {
    return text.slice(0, limit) + `\n\n…（已截断，共 ${text.length.toLocaleString()} 字符）`;
  }
  return text;
}

function safeName(s) {
  return String(s).replace(/[\\/:*?"<>|]+/g, "_").trim() || "chat-export";
}

function num(n) {
  return Number(n || 0).toLocaleString("en-US");
}

// ------------------------------------------------------------------ Markdown

function renderMarkdown(messages, meta, a) {
  const title = a.title || meta.title || "未命名会话";
  const sid = a.sessionId || meta.session_id || "?";
  const agent = a.agent || meta.agent_name || "Mavis";
  const model = a.model || (meta.model && meta.model.model_id) || "—";
  const userN = messages.filter((m) => m.role === "user").length;
  const asstN = messages.filter((m) => m.role === "assistant").length;
  const times = messages.map((m) => m.timestamp).filter((t) => typeof t === "number");
  const span = times.length ? `${ts(Math.min(...times))} ~ ${ts(Math.max(...times))}` : "—";

  const out = [];
  out.push(`# ${title}\n`);
  out.push("> **Mavis 聊天记录导出**\n>");
  out.push(`> - 会话标题：${title}`);
  out.push(`> - 会话 ID：\`${sid}\``);
  out.push(`> - 智能体：${agent}　|　模型：${model}`);
  out.push(`> - 时间范围：${span}（UTC+8）`);
  out.push(`> - 消息数：${messages.length}（用户 ${userN} / 助手 ${asstN}）`);
  out.push(`> - 导出时间：${ts(Date.now())}（UTC+8）\n`);
  out.push("---\n");

  messages.forEach((m, i) => {
    const role = m.role || "?";
    const who = role === "user" ? "用户" : role === "assistant" ? "Mavis" : role;
    const icon = role === "user" ? "👤" : "🤖";
    const content = m.msg_content || "";
    out.push(`## ${i + 1}. ${icon} ${who} · ${ts(m.timestamp)}\n`);
    if (content.trim()) out.push(content.trimEnd() + "\n");
    else if (m.tool_calls) out.push("*(本轮为工具调用，无文字回复)*\n");

    if (a.thinking && m.thinking_content) {
      out.push("<details><summary>🧠 思考过程</summary>\n");
      out.push(m.thinking_content.trimEnd().split("\n").map((l) => "> " + l).join("\n"));
      out.push("\n</details>\n");
    }

    const tcs = m.tool_calls || [];
    if (tcs.length) {
      out.push(`<details><summary>🔧 工具调用（${tcs.length}）</summary>\n`);
      for (const tc of tcs) {
        out.push(`- **\`${tc.tool_name || "?"}\`** — ${briefArgs(tc.tool_call_args)}`);
        if (a.toolOutput) {
          const res = toolResultText(tc.tool_call_result_data);
          if (res) out.push(`\n\`\`\`text\n${cut(res, a.maxToolOutput)}\n\`\`\`\n`);
        }
      }
      out.push("</details>\n");
    }

    if (m.usage) {
      const u = m.usage;
      out.push(`<sub>token: 总 ${num(u.total_tokens)} | 输入 ${num(u.input_tokens)} | 输出 ${num(u.output_tokens)} | 缓存读 ${num(u.cache_read)}</sub>\n`);
    }
    out.push("---\n");
  });

  return out.join("\n");
}

// ------------------------------------------------------------------ HTML

const HTML_CSS = `
:root{color-scheme:light dark;--bg:#f6f7f9;--card:#fff;--fg:#1a1d21;--muted:#6b7280;--line:#e5e7eb;--accent:#3b6ef6;--code:#f4f5f7}
@media (prefers-color-scheme:dark){:root{--bg:#14161a;--card:#1c1f25;--fg:#e6e8eb;--muted:#9aa3af;--line:#2b303a;--code:#22262d}}
*{box-sizing:border-box}
body{margin:0;padding:32px 20px;background:var(--bg);color:var(--fg);font:16px/1.75 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif}
.wrap{max-width:880px;margin:0 auto}
header{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px 24px;margin-bottom:22px}
h1{font-size:22px;margin:0 0 12px}
.meta{color:var(--muted);font-size:13px;line-height:1.9;margin:0}
.meta code{background:var(--code);padding:1px 6px;border-radius:5px}
.msg{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 24px;margin-bottom:18px}
.msg.user{border-left:4px solid #22a06b}
.msg.assistant{border-left:4px solid var(--accent)}
.who{font-weight:700;font-size:14px;margin-bottom:12px;display:flex;gap:8px;align-items:center}
.who .t{color:var(--muted);font-weight:400;font-size:12px;margin-left:auto}
.msg .body{overflow-wrap:anywhere}
.msg .body pre{background:var(--code);padding:12px 14px;border-radius:8px;overflow:auto}
.msg .body code{background:var(--code);padding:1px 5px;border-radius:5px;font-size:90%}
.msg .body pre code{background:none;padding:0}
.msg .body table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}
.msg .body th,.msg .body td{border:1px solid var(--line);padding:7px 10px;text-align:left}
.msg .body th{background:var(--code)}
.msg .body blockquote{border-left:3px solid var(--line);margin:10px 0;padding:2px 14px;color:var(--muted)}
details{margin:12px 0;font-size:14px}
summary{cursor:pointer;color:var(--muted)}
details pre{margin:8px 0}
.sub{color:var(--muted);font-size:12px;margin-top:12px}
`;

function inlineHtml(s) {
  let out = esc(s);
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/(?<!\*)\*([^*\n]+)\*(?!\*)/g, "<em>$1</em>");
  out = out.replace(/\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener">$1</a>');
  return out;
}

function mdToHtml(md) {
  const lines = String(md).replace(/\r\n/g, "\n").split("\n");
  const out = [];
  let inCode = false, inList = false, inTable = false;

  const closeList = () => { if (inList) { out.push("</ul>"); inList = false; } };
  const closeTable = () => { if (inTable) { out.push("</table>"); inTable = false; } };

  for (let i = 0; i < lines.length; i++) {
    const ln = lines[i];

    if (ln.startsWith("```")) {
      closeList(); closeTable();
      out.push(inCode ? "</code></pre>" : "<pre><code>");
      inCode = !inCode;
      continue;
    }
    if (inCode) { out.push(esc(ln)); continue; }

    const trimmed = ln.trim();
    if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
      closeList();
      const rows = [];
      while (i < lines.length) {
        const t = lines[i].trim();
        if (!(t.startsWith("|") && t.endsWith("|"))) break;
        rows.push(t.slice(1, -1).split("|").map((c) => c.trim()));
        i++;
      }
      i--;
      const body = rows.filter((r) => !r.every((c) => /^:?-{2,}:?$/.test(c || "-")));
      if (body.length) {
        out.push("<table><tr>" + body[0].map((c) => `<th>${inlineHtml(c)}</th>`).join("") + "</tr>");
        for (const r of body.slice(1)) {
          out.push("<tr>" + r.map((c) => `<td>${inlineHtml(c)}</td>`).join("") + "</tr>");
        }
        out.push("</table>");
      }
      continue;
    }
    closeTable();

    if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(ln)) {
      closeList();
      out.push("<hr>");
      continue;
    }

    const h = ln.match(/^(#{1,6})\s+(.*)$/);
    if (h) {
      closeList();
      out.push(`<h${h[1].length}>${inlineHtml(h[2])}</h${h[1].length}>`);
      continue;
    }

    const li = ln.match(/^\s*(?:[-*]|\d+\.)\s+(.*)$/);
    if (li) {
      if (!inList) { out.push("<ul>"); inList = true; }
      out.push(`<li>${inlineHtml(li[1])}</li>`);
      continue;
    }
    closeList();

    if (trimmed.startsWith(">")) {
      out.push(`<blockquote>${inlineHtml(trimmed.replace(/^>+\s*/, ""))}</blockquote>`);
      continue;
    }
    if (!trimmed) continue;
    out.push(`<p>${inlineHtml(ln)}</p>`);
  }

  if (inCode) out.push("</code></pre>");
  closeList(); closeTable();
  return out.join("\n");
}

function renderHtml(messages, meta, a) {
  const title = a.title || meta.title || "未命名会话";
  const sid = a.sessionId || meta.session_id || "?";
  const agent = a.agent || meta.agent_name || "Mavis";
  const model = a.model || (meta.model && meta.model.model_id) || "—";
  const times = messages.map((m) => m.timestamp).filter((t) => typeof t === "number");
  const span = times.length ? `${ts(Math.min(...times))} ~ ${ts(Math.max(...times))}` : "—";

  const parts = [
    "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>",
    "<meta name='viewport' content='width=device-width,initial-scale=1'>",
    `<title>${esc(title)}</title><style>${HTML_CSS}</style></head><body><div class='wrap'>`,
    "<header>",
    `<h1>${esc(title)}</h1>`,
    `<p class='meta'>会话 ID <code>${esc(String(sid))}</code> · 智能体 ${esc(agent)} · 模型 ${esc(String(model))}<br>` +
    `时间范围 ${esc(span)}（UTC+8） · 消息 ${messages.length} 条 · 导出于 ${ts(Date.now()).slice(0, 16)}</p>`,
    "</header>",
  ];

  messages.forEach((m, i) => {
    const cls = m.role === "user" ? "user" : "assistant";
    const who = m.role === "user" ? "👤 用户" : "🤖 Mavis";
    parts.push(`<div class='msg ${cls}'><div class='who'>${who}<span class='t'>${i + 1} / ${messages.length} · ${ts(m.timestamp)}</span></div>`);
    const body = m.msg_content || "";
    if (body.trim()) parts.push(`<div class='body'>${mdToHtml(body)}</div>`);
    if (a.thinking && m.thinking_content) {
      parts.push(`<details><summary>🧠 思考过程</summary><pre>${esc(cut(m.thinking_content, 20000))}</pre></details>`);
    }
    const tcs = m.tool_calls || [];
    if (tcs.length) {
      parts.push(`<details><summary>🔧 工具调用（${tcs.length}）</summary>`);
      for (const tc of tcs) {
        parts.push(`<p><code>${esc(String(tc.tool_name))}</code> — ${esc(briefArgs(tc.tool_call_args))}</p>`);
        if (a.toolOutput) {
          const res = toolResultText(tc.tool_call_result_data);
          if (res) parts.push(`<pre>${esc(cut(res, a.maxToolOutput))}</pre>`);
        }
      }
      parts.push("</details>");
    }
    if (m.usage) {
      const u = m.usage;
      parts.push(`<p class='sub'>token 总 ${num(u.total_tokens)} · 输入 ${num(u.input_tokens)} · 输出 ${num(u.output_tokens)}</p>`);
    }
    parts.push("</div>");
  });

  parts.push("</div></body></html>");
  return parts.join("\n");
}

// ------------------------------------------------------------------ main

const a = parseArgs(process.argv);
let payload;
try {
  payload = loadPayload(a.raw);
} catch (e) {
  console.error(`✗ 读不到 ${a.raw}: ${e.message}`);
  process.exit(1);
}
let messages, meta;
try {
  ({ messages, meta } = extractMessages(payload));
} catch (e) {
  console.error(`✗ ${e.message}`);
  process.exit(1);
}
if (!messages.length) {
  console.error("✗ 消息列表为空。");
  process.exit(1);
}

fs.mkdirSync(a.outdir, { recursive: true });
const base = safeName(a.basename || a.title || meta.title || "chat-export");
const formats = new Set(a.formats.split(",").map((f) => f.trim().toLowerCase()).filter(Boolean));
const written = [];

if (formats.has("md")) {
  const p = path.join(a.outdir, base + ".md");
  fs.writeFileSync(p, renderMarkdown(messages, meta, a), "utf8");
  written.push(p);
}
if (formats.has("html")) {
  const p = path.join(a.outdir, base + ".html");
  fs.writeFileSync(p, renderHtml(messages, meta, a), "utf8");
  written.push(p);
}
if (formats.has("json")) {
  const p = path.join(a.outdir, base + ".json");
  fs.writeFileSync(p, JSON.stringify({
    exported_at: new Date(Date.now() + TZ_OFFSET_MS).toISOString().replace("Z", "+08:00"),
    title: a.title || meta.title,
    session_id: a.sessionId || meta.session_id,
    agent: a.agent || meta.agent_name,
    model: a.model || (meta.model && meta.model.model_id),
    message_count: messages.length,
    messages,
  }, null, 2), "utf8");
  written.push(p);
}

for (const p of written) {
  console.log(`✓ ${p}  (${fs.statSync(p).size.toLocaleString()} bytes)`);
}
