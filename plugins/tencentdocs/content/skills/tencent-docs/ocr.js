#!/usr/bin/env node
"use strict";

const fs = require("node:fs");
const path = require("node:path");
const { assertToolName, callConnector, parseConnectorResult } = require("./scripts/connector_call.js");

const supported = new Set(["png", "jpg", "jpeg", "bmp", "webp"]);
const maxSingle = 10 * 1024 * 1024;
const maxTotal = 50 * 1024 * 1024;
const maxCount = 9;

function die(message) { console.error(`ERROR: ${message}`); process.exit(1); }
function checkImage(file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) die(`文件不存在或不是文件: ${file}`);
  const ext = path.extname(file).slice(1).toLowerCase();
  const size = fs.statSync(file).size;
  if (!supported.has(ext)) die(`不支持的格式 .${ext}`);
  if (size === 0 || size > maxSingle) die(`图片大小必须在 1B 到 10MB 之间: ${file}`);
  return size;
}
function usage() {
  console.error("用法: node ocr.js <extract|toword|toexcel> <图片...> --tool <connector__tencentdocs__...> [选项]");
  process.exit(1);
}
function parse(argv) {
  if (!argv.length) usage();
  const action = argv.shift();
  if (!["extract", "toword", "toexcel"].includes(action)) die(`未知操作: ${action}`);
  let tool = "";
  let title = "";
  let extractType = "basic";
  let positions = false;
  const images = [];
  function valueAt(index, option) {
    const value = argv[index];
    if (!value || value.startsWith("--")) die(`${option} 需要值`);
    return value;
  }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--tool") tool = valueAt(++i, arg);
    else if (arg === "--title") title = valueAt(++i, arg);
    else if (arg === "--accurate" || arg === "--efficient") extractType = arg.slice(2);
    else if (arg === "--positions") positions = true;
    else if (arg.startsWith("-")) die(`未知选项: ${arg}`);
    else images.push(arg);
  }
  if (!tool) die("必须传入 Connector 工具名 --tool；先用 mcode-tools connector tools 查看当前 tencentdocs 工具");
  assertToolName(tool);
  if (action === "extract" && title) die("--title 仅用于 toword/toexcel");
  if (action !== "extract" && (extractType !== "basic" || positions)) die("--accurate、--efficient 和 --positions 仅用于 extract");
  if (action === "extract" && images.length !== 1) die("extract 需要一张图片");
  if (action !== "extract" && (images.length < 1 || images.length > maxCount)) die(`图片数量必须为 1-${maxCount}`);
  const total = images.reduce((sum, image) => sum + checkImage(image), 0);
  if (total > maxTotal) die("图片总大小超过 50MB");
  return { action, tool, title, extractType, positions, images };
}
function main() {
  const p = parse(process.argv.slice(2));
  const encoded = p.images.map((file) => ({ image_base64: fs.readFileSync(file).toString("base64") }));
  const args = p.action === "extract"
    ? { image_base64: encoded[0].image_base64, extract_type: p.extractType, with_positions: p.positions }
    : { images: encoded, ...(p.title ? { title: p.title } : {}) };
  try {
    const result = parseConnectorResult(callConnector(p.tool, args));
    if (p.action === "extract") {
      if (!Array.isArray(result.texts) || !result.texts.every((text) => typeof text === "string")) throw new Error("OCR 返回缺少有效 texts 数组");
    } else if (typeof result.file_id !== "string" || !result.file_id || typeof result.file_url !== "string" || !result.file_url) {
      throw new Error("OCR 转换返回缺少 file_id 或 file_url");
    }
    console.log(JSON.stringify(result));
  }
  catch (error) { die(error.stderr || error.message || String(error)); }
}
try { main(); }
catch (error) { die(error.message || String(error)); }
