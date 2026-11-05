#!/usr/bin/env node
/**
 * 微博内容 → Excel报表
 * 依赖：npm install xlsx
 */

const XLSX = require("xlsx");
const fs = require("fs");
const path = require("path");

// 传入日期字符串，如 "2026-05-12"
const dateStr = process.argv[2] || new Date(Date.now() - 86400000).toISOString().slice(0, 10);

// 向上两级到skill根目录，再进data
const SKILL_DIR = path.dirname(path.dirname(__dirname));
const DATA_DIR = path.join(SKILL_DIR, "data");
const jsonFile = path.join(DATA_DIR, `${dateStr}.json`);
const xlsxFile = path.join(DATA_DIR, `${dateStr}.xlsx`);

function parseJson(jsonStr) {
  try {
    const data = JSON.parse(jsonStr);
    if (Array.isArray(data)) return data;
    if (data.data && Array.isArray(data.data)) return data.data;
    return [];
  } catch {
    return [];
  }
}

function main() {
  if (!fs.existsSync(jsonFile)) {
    console.log(`JSON文件不存在：${jsonFile}（0条）`);
    process.exit(1);
  }

  const raw = fs.readFileSync(jsonFile, "utf8");
  const records = parseJson(raw);

  if (!records.length) {
    console.log(`无记录：${jsonFile}（0条）`);
    return;
  }

  // 工作表1：原始数据
  const ws = XLSX.utils.json_to_sheet(records);

  // 宽度自适应
  const maxLen = {};
  records.forEach(r => {
    Object.keys(r).forEach(k => {
      const v = String(r[k] || "");
      maxLen[k] = Math.max(maxLen[k] || 10, Math.min(v.length, 80));
    });
  });
  ws["!cols"] = Object.keys(maxLen).map(k => ({ wch: maxLen[k] }));

  // 工作表2：汇总
  const summary = [
    { "统计项": "抓取日期", "数值": dateStr },
    { "统计项": "总记录数", "数值": records.length },
    { "统计项": "账号数量", "数值": [...new Set(records.map(r => r["账号名称"]))].length },
    { "统计项": "有视频微博", "数值": records.filter(r => r["视频链接"] && r["视频链接"] !== "").length },
    { "统计项": "有图片微博", "数值": records.filter(r => r["图片链接"] && r["图片链接"] !== "").length },
    { "统计项": "话题微博", "数值": records.filter(r => r["微博正文"] && r["微博正文"].includes("#")).length },
    { "统计项": "数据文件", "数值": `${dateStr}.json` },
  ];

  // 账号分类统计
  const cats = {};
  records.forEach(r => {
    const cat = r["账号分类"] || "未知";
    cats[cat] = (cats[cat] || 0) + 1;
  });
  Object.keys(cats).forEach(cat => {
    summary.push({ "统计项": `账号分类【${cat}】`, "数值": cats[cat] });
  });

  const wsSummary = XLSX.utils.json_to_sheet(summary);
  wsSummary["!cols"] = [{ wch: 20 }, { wch: 30 }];

  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "微博内容");
  XLSX.utils.book_append_sheet(wb, wsSummary, "汇总统计");

  XLSX.writeFile(wb, xlsxFile);
  console.log(`Excel已输出：${xlsxFile}（${records.length}条）`);
}

main();
