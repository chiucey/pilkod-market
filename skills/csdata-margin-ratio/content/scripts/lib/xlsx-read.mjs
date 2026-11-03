// xlsx-read.mjs — 解析 .xlsx（zip + OOXML），零依赖
// 只取需要的信息：单元格值、类型、数字格式（判断百分比/日期要用）
import { readZip } from './zip.mjs';

function parseAttrs(tag) {
  const attrs = {};
  const re = /([\w:]+)\s*=\s*"([^"]*)"/g;
  let m;
  while ((m = re.exec(tag))) attrs[m[1]] = m[2];
  return attrs;
}

function xmlEscape(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function unescapeXml(s) {
  return String(s)
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"').replace(/&apos;/g, "'")
    .replace(/&amp;/g, '&');
}

function parseSharedStrings(xml) {
  const out = [];
  if (!xml) return out;
  const siRe = /<si\b[^>]*>([\s\S]*?)<\/si>/g;
  let m;
  while ((m = siRe.exec(xml))) {
    let text = '';
    const tRe = /<t\b[^>]*>([\s\S]*?)<\/t>/g;
    let t;
    while ((t = tRe.exec(m[1]))) text += unescapeXml(t[1]);
    out.push(text);
  }
  return out;
}

/** 数字格式表：numFmtId -> format code */
function parseStyles(xml) {
  const custom = {};
  if (xml) {
    const nfRe = /<numFmt\b([^>]*)\/>/g;
    let m;
    while ((m = nfRe.exec(xml))) {
      const a = parseAttrs(m[1]);
      if (a.numFmtId != null) custom[Number(a.numFmtId)] = a.formatCode;
    }
  }
  const BUILTIN = {
    0: 'General', 1: '0', 2: '0.00', 3: '#,##0', 4: '#,##0.00',
    9: '0%', 10: '0.00%', 11: '0.00E+00', 12: '# ?/?', 13: '# ??/??',
    14: 'mm-dd-yy', 15: 'd-mmm-yy', 16: 'd-mmm', 17: 'mmm-yy',
    18: 'h:mm AM/PM', 19: 'h:mm:ss AM/PM', 20: 'h:mm', 21: 'h:mm:ss',
    22: 'm/d/yy h:mm', 37: '#,##0 ;(#,##0)', 38: '#,##0 ;[Red](#,##0)',
    39: '#,##0.00;(#,##0.00)', 40: '#,##0.00;[Red](#,##0.00)',
    45: 'mm:ss', 46: '[h]:mm:ss', 47: 'mmss.0', 48: '##0.0E+0', 49: '@',
  };
  const xfFmtIds = [];
  if (xml) {
    // 单元格 s= 索引对应的是 <cellXfs> 里的顺序；
    // <cellStyleXfs> 里的 xf 是另一组，混进来会让所有索引错位。
    const cellXfsBlock = /<cellXfs\b[^>]*>([\s\S]*?)<\/cellXfs>/.exec(xml);
    const block = cellXfsBlock ? cellXfsBlock[1] : '';
    const xfRe = /<xf\b([^>]*?)(?:\/>|>[\s\S]*?<\/xf>)/g;
    let m;
    while ((m = xfRe.exec(block))) {
      const a = parseAttrs(m[1]);
      xfFmtIds.push(a.numFmtId != null ? Number(a.numFmtId) : 0);
    }
  }
  return { custom, BUILTIN, xfFmtIds };
}

/**
 * 读取 xlsx → { sheets: [{ name, rows: [[cell,...]] }] }
 * cell = { v: 值, t: 类型('n'|'s'|'b'|'str'|'e'), fmt: 数字格式代码 }
 */
export function readXlsx(buf) {
  const files = readZip(buf);
  const sst = parseSharedStrings(files['xl/sharedStrings.xml']?.toString('utf8'));
  const styles = parseStyles(files['xl/styles.xml']?.toString('utf8'));

  // 工作表名映射
  const wbXml = files['xl/workbook.xml']?.toString('utf8') || '';
  const relsXml = files['xl/_rels/workbook.xml.rels']?.toString('utf8') || '';
  const relMap = {};
  const relRe = /<Relationship\b([^>]*)\/>/g;
  let rm;
  while ((rm = relRe.exec(relsXml))) {
    const a = parseAttrs(rm[1]);
    if (a.Id && a.Target) relMap[a.Id] = a.Target.replace(/^\/?xl\//, '').replace(/^\//, '');
  }
  const sheetDefs = [];
  const shRe = /<sheet\b([^>]*)\/>/g;
  let sm;
  while ((sm = shRe.exec(wbXml))) {
    const a = parseAttrs(sm[1]);
    const rid = a['r:id'] || a.id;
    sheetDefs.push({ name: a.name || 'Sheet', path: relMap[rid] ? 'xl/' + relMap[rid] : null });
  }

  const sheets = [];
  const paths = sheetDefs.length
    ? sheetDefs.map((s) => s.path).filter(Boolean)
    : Object.keys(files).filter((k) => /^xl\/worksheets\/sheet\d+\.xml$/.test(k)).sort();

  const names = sheetDefs.length ? sheetDefs.map((s) => s.name) : paths.map((_, i) => `Sheet${i + 1}`);

  paths.forEach((p, idx) => {
    const xml = files[p]?.toString('utf8');
    if (!xml) return;
    const rows = [];
    const rowRe = /<row\b([^>]*)>([\s\S]*?)<\/row>/g;
    let r;
    while ((r = rowRe.exec(xml))) {
      const rAttr = parseAttrs(r[1]);
      const rIdx = rAttr.r ? Number(rAttr.r) : rows.length + 1;
      const cells = [];
      const cRe = /<c\b([^>]*?)(?:\/>|>([\s\S]*?)<\/c>)/g;
      let c;
      while ((c = cRe.exec(r[2]))) {
        const ca = parseAttrs(c[1]);
        const body = c[2] || '';
        const ref = ca.r || '';
        const col = ref ? colIndex(ref) : cells.length;
        const t = ca.t || 'n';
        const sIdx = ca.s != null ? Number(ca.s) : -1;
        const fmtId = sIdx >= 0 && styles.xfFmtIds[sIdx] != null ? styles.xfFmtIds[sIdx] : 0;
        const fmt = styles.custom[fmtId] || styles.BUILTIN[fmtId] || 'General';
        let v = null;
        const vm = /<v\b[^>]*>([\s\S]*?)<\/v>/.exec(body);
        if (t === 'inlineStr') {
          const im = /<is\b[^>]*>([\s\S]*?)<\/is>/.exec(body);
          if (im) {
            let txt = '';
            const tr = /<t\b[^>]*>([\s\S]*?)<\/t>/g;
            let tm;
            while ((tm = tr.exec(im[1]))) txt += unescapeXml(tm[1]);
            v = txt;
          }
        } else if (vm) {
          const raw = unescapeXml(vm[1]);
          if (t === 's') v = sst[Number(raw)] ?? '';
          else if (t === 'str') v = raw;
          else if (t === 'b') v = raw === '1';
          else if (t === 'e') v = raw;
          else v = raw === '' ? null : Number(raw);
        }
        cells[col] = { v, t, fmt };
      }
      rows[rIdx - 1] = cells;
    }
    sheets.push({ name: names[idx] || `Sheet${idx + 1}`, rows });
  });

  return { sheets };
}

function colIndex(ref) {
  const m = /^([A-Z]+)/.exec(ref);
  if (!m) return 0;
  let n = 0;
  for (const ch of m[1]) n = n * 26 + (ch.charCodeAt(0) - 64);
  return n - 1;
}

export { colIndex, xmlEscape, parseAttrs };
