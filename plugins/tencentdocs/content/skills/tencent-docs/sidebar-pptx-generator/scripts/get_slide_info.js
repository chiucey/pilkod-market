#!/usr/bin/env node
"use strict";

const { callConnector, parseConnectorResult, assertToolName } = require("../../scripts/connector_call.js");
function die(message) { console.error(`ERROR: ${message}`); process.exit(1); }
const input = process.argv[2];
const fileKey = process.argv[3] === "--file-id" ? "file_id" : "file_url";
const tools = Object.fromEntries((process.env.TENCENTDOCS_SLIDE_TOOLS || "").split(",").filter(Boolean).map((item) => {
  const pivot = item.indexOf("=");
  return pivot < 1 ? ["", ""] : [item.slice(0, pivot), item.slice(pivot + 1)];
}));
if (!input || !tools.info || !tools.page || !tools.design) die("请传入 <file_id|file_url>，并设置 TENCENTDOCS_SLIDE_TOOLS=info=<...>,page=<...>,design=<...>,access=<...>");
for (const key of ["info", "page", "design"]) assertToolName(tools[key]);
const base = { [fileKey]: input };
try {
  const info = parseConnectorResult(callConnector(tools.info, base));
  const slideCount = Number(info.slide_count);
  const w = Number(info.w_pt);
  const h = Number(info.h_pt);
  if (!Number.isInteger(slideCount) || slideCount < 0 || !Number.isFinite(w) || !Number.isFinite(h) || w < 0 || h < 0) die("slide_get_info 返回缺少有效 slide_count/w_pt/h_pt");
  if (slideCount === 0) {
    if (!tools.access) die("slide_count=0 不能判定为空文档；请配置 access 工具验证 VIEW 权限");
    assertToolName(tools.access);
    const fileId = fileKey === "file_url" ? new URL(input).pathname.split("/").filter(Boolean).pop() : input;
    const access = parseConnectorResult(callConnector(tools.access, { file_id: fileId, actions: ["VIEW"] }));
    const granted = Array.isArray(access.granted_actions) && access.granted_actions.includes("VIEW");
    if (!granted) {
      console.log(JSON.stringify({ action: "ask_user", reason: "permission_denied", slide_count: slideCount, w_pt: w, h_pt: h, file_id: fileId, hint: "当前账号无 VIEW 权限，请分享文档或下载到本地后重试" }));
      process.exit(0);
    }
    console.log(JSON.stringify({ action: "write_design_md", reason: "ppt_is_empty", slide_count: slideCount, w_pt: w, h_pt: h }));
    process.exit(0);
  }
  if (w <= 0 || h <= 0) die("slide_get_info 返回的页面尺寸无效，不能判定为 PPT 为空");
  let contentPages = 0;
  for (let i = 0; i < slideCount; i += 1) {
    const page = parseConnectorResult(callConnector(tools.page, { ...base, page_index: i }));
    if (!Array.isArray(page.shapes)) die(`slide_get_page_info 第 ${i} 页返回缺少 shapes 数组`);
    // Pictures, tables, charts and drawings carry no `text` but still make a
    // page non-empty. Only an explicitly marked empty placeholder is ignored.
    if (page.shapes.some((shape) => {
      if (!shape || typeof shape !== "object") return false;
      const text = String(shape.text || "").replace(/\s/g, "");
      return text || !(shape.is_placeholder === true || shape.placeholder === true);
    })) contentPages += 1;
  }
  if (!contentPages) { console.log(JSON.stringify({ action: "write_design_md", reason: "ppt_content_is_empty", slide_count: slideCount, w_pt: w, h_pt: h, content_page_count: 0 })); process.exit(0); }
  const design = parseConnectorResult(callConnector(tools.design, base));
  if (typeof design.exists !== "boolean" || (design.exists && typeof design.design_md !== "string")) die("slide_get_design 返回缺少有效 exists/design_md");
  const exists = design.exists && Boolean(design.design_md.trim());
  console.log(JSON.stringify({ action: exists ? "design_exists" : "write_design_md", reason: exists ? "design_exists" : "design_is_empty", slide_count: slideCount, w_pt: w, h_pt: h, content_page_count: contentPages, design_exists: exists }));
} catch (error) { die(error.stderr || error.message || String(error)); }
