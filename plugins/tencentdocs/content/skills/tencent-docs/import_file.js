#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const { callConnector, parseConnectorResult } = require("./scripts/connector_call.js");

function die(message) { console.error(`ERROR: ${message}`); process.exit(1); }
async function main() {
  const file = process.argv[2];
  const tool = process.argv[3] || process.env.TENCENTDOCS_PRE_IMPORT_TOOL;
  if (!file || !tool) die("用法: node import_file.js <文件路径> <工具发现结果中的预导入 Connector 工具名>");
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) die(`文件不存在: ${file}`);
  const body = fs.readFileSync(file);
  const fileName = path.basename(file);
  const fileSize = body.length;
  const fileMd5 = crypto.createHash("md5").update(body).digest("hex");
  let result;
  try { result = parseConnectorResult(callConnector(tool, { file_name: fileName, file_size: fileSize, file_md5: fileMd5 })); }
  catch (error) { die(error.stderr || error.message || String(error)); }
  if (!["upload_url", "file_key", "task_id"].every((key) => typeof result[key] === "string" && result[key])) die("预导入返回缺少有效 upload_url、file_key 或 task_id");
  const uploadUrl = new URL(result.upload_url);
  if (uploadUrl.protocol !== "https:" || uploadUrl.username || uploadUrl.password) die("预导入返回的上传地址必须是 HTTPS URL");
  const response = await fetch(uploadUrl, { method: "PUT", headers: { "content-type": "application/octet-stream" }, body, redirect: "error", signal: AbortSignal.timeout(120000) });
  if (!response.ok) die(`文件上传失败: HTTP ${response.status}`);
  console.log(`IMPORT_READY\nFILE_KEY:${result.file_key}\nFILE_NAME:${fileName}\nFILE_MD5:${fileMd5}\nTASK_ID:${result.task_id}\nFILE_SIZE:${fileSize}`);
}
main().catch((error) => die(error.message || String(error)));
