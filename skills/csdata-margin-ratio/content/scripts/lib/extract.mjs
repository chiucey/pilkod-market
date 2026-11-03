// extract.mjs — 从源文件里提取「平均维持担保比例」与统计日期
// 中证数据的文件有两种形态，口径必须统一：
//   新格式(.xlsx)：数值 + 百分比格式(2.556273 → 255.6273%)，日期是 Excel 序列号
//   老格式(.xls)  ：文本百分数字符串("239.5%")，日期是 "2024年08月19日" 文本
import { readXlsx } from './xlsx-read.mjs';
import { readXls, xlsRows } from './xls-read.mjs';

const CN_DATE = /(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日/;
const ISO_DATE = /(\d{4})-(\d{1,2})-(\d{1,2})/;

/** Excel 序列号 → YYYY-MM-DD（1900 日期系统，含闰年 bug 修正） */
export function serialToDate(serial) {
  const days = Math.floor(serial);
  const ms = Date.UTC(1899, 11, 30) + days * 86400000;
  const d = new Date(ms);
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getUTCFullYear()}-${p(d.getUTCMonth() + 1)}-${p(d.getUTCDate())}`;
}

/** 数字格式是否是日期/时间格式 */
export function isDateFormat(fmt) {
  if (!fmt) return false;
  let s = String(fmt);
  s = s.replace(/"[^"]*"/g, '').replace(/\\./g, '').replace(/\[[^\]]*\]/g, '');
  if (/[yd]/i.test(s)) return true;
  if (/[hs]/i.test(s)) return true;
  if (/m/i.test(s) && !/%/.test(s)) return true;
  return false;
}

/** 百分比数值归一化 → 统一为「百分数数值」(255.6273 表示 255.6273%) */
export function normalizePercent(value, fmt) {
  if (value === null || value === undefined || value === '') return null;
  if (typeof value === 'number') {
    if (isPercentFormat(fmt)) return value * 100;
    // 没有百分比格式时靠量级判断：比值型(1~10) ×100，百分数型(>10) 原样
    return Math.abs(value) < 10 ? value * 100 : value;
  }
  const s = String(value).trim();
  if (s.endsWith('%')) {
    const n = Number(s.slice(0, -1).replace(/,/g, ''));
    return Number.isFinite(n) ? n : null;
  }
  const n = Number(s.replace(/,/g, ''));
  if (!Number.isFinite(n)) return null;
  return Math.abs(n) < 10 ? n * 100 : n;
}

export function isPercentFormat(fmt) {
  return !!fmt && String(fmt).includes('%');
}

/** 从二维行数组里找「平均维持担保比例」行，并取其右侧第一个非空单元格 */
function findRatio(rows) {
  for (const r of rows) {
    if (!r) continue;
    for (let i = 0; i < r.length; i++) {
      const c = r[i];
      if (c && typeof c.v === 'string' && c.v.includes('平均维持担保比例')) {
        for (let j = i + 1; j < r.length; j++) {
          if (r[j] && r[j].v !== null && r[j].v !== undefined && r[j].v !== '') {
            return { value: r[j].v, fmt: r[j].fmt || 'General', kind: r[j].t === 's' ? 'text' : 'number' };
          }
        }
      }
    }
  }
  return null;
}

/** 从二维行数组里找统计日期 */
function findDate(rows) {
  for (const r of rows.slice(0, 6)) {
    if (!r) continue;
    for (const c of r) {
      if (!c) continue;
      if (typeof c.v === 'string') {
        const m = CN_DATE.exec(c.v) || ISO_DATE.exec(c.v);
        if (m) return `${m[1]}-${String(m[2]).padStart(2, '0')}-${String(m[3]).padStart(2, '0')}`;
      } else if (typeof c.v === 'number') {
        // 有日期格式的按格式识别；没格式的按「合理序列号区间」兜底
        // （部分文件的日期单元格是 General 格式的裸序列号）
        if (isDateFormat(c.fmt) || isPlausibleSerial(c.v)) {
          const s = serialToDate(c.v);
          if (s) return s;
        }
      }
    }
  }
  return null;
}

/** 合理的 Excel 日期序列号区间（约 1954 ~ 2064），用于无格式日期的兜底识别 */
function isPlausibleSerial(v) {
  return Number.isInteger(v) && v >= 20000 && v <= 60000;
}

/** 解析源文件 → {date, ratio, kind, fmt} */
export function extractFromBuffer(buf, filename) {
  const isXls = /\.xls$/i.test(filename) && !/\.xlsx$/i.test(filename);
  const rows = isXls
    ? xlsRows(readXls(buf).sheets[0])
    : readXlsx(buf).sheets[0].rows;

  const ratio = findRatio(rows);
  if (!ratio) throw new Error(`未找到「平均维持担保比例」行: ${filename}`);
  const value = normalizePercent(ratio.value, ratio.fmt);
  if (value === null) throw new Error(`比例值无法解析: ${filename} -> ${JSON.stringify(ratio.value)}`);

  return {
    date: findDate(rows),
    ratio: Math.round(value * 1e4) / 1e4,
    kind: ratio.kind === 'text' ? 'text' : 'number',
    fmt: ratio.fmt,
  };
}
