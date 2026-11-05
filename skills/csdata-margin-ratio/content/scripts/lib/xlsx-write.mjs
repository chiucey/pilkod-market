// xlsx-write.mjs — 纯 Node 生成 .xlsx（OOXML），零依赖
// 只实现本技能需要的样式：表头、日期、两种数字格式、列宽、冻结窗格、自动筛选
import { writeZip } from './zip.mjs';
import { colIndex } from './xlsx-read.mjs';

const esc = (s) => String(s)
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;').replace(/'/g, '&apos;')
  // 去掉 XML 1.0 不允许的控制字符
  .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F]/g, '');

function colName(n) {
  let s = '';
  n += 1;
  while (n > 0) {
    const m = (n - 1) % 26;
    s = String.fromCharCode(65 + m) + s;
    n = Math.floor((n - 1) / 26);
  }
  return s;
}

const STYLES = {
  DEFAULT: 0,
  HEADER: 1,
  DATE: 2,
  RATIO: 3,
  INDEX: 4,
  CENTER: 5,
  NOTE: 6,
};

const STYLE_XML = `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<numFmts count="3">
<numFmt numFmtId="164" formatCode="yyyy\\-mm\\-dd"/>
<numFmt numFmtId="165" formatCode="0.0000"/>
<numFmt numFmtId="166" formatCode="#,##0.00"/>
</numFmts>
<fonts count="4">
<font><sz val="11"/><name val="Calibri"/></font>
<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
<font><b/><sz val="11"/><name val="Calibri"/></font>
<font><sz val="10"/><color rgb="FF833C00"/><name val="Calibri"/></font>
</fonts>
<fills count="4">
<fill><patternFill patternType="none"/></fill>
<fill><patternFill patternType="gray125"/></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FF1F3864"/><bgColor indexed="64"/></patternFill></fill>
<fill><patternFill patternType="solid"><fgColor rgb="FFF1F5F9"/><bgColor indexed="64"/></patternFill></fill>
</fills>
<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="7">
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
<xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
<xf numFmtId="164" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment horizontal="center"/></xf>
<xf numFmtId="165" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment horizontal="right"/></xf>
<xf numFmtId="166" fontId="0" fillId="0" borderId="0" xfId="0" applyNumberFormat="1" applyAlignment="1"><alignment horizontal="right"/></xf>
<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment horizontal="center"/></xf>
<xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1"/>
</cellXfs>
<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>`;

/** 'YYYY-MM-DD' → Excel 日期序列号（1900 日期系统） */
export function dateToSerial(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(iso));
  if (!m) return null;
  const ms = Date.UTC(+m[1], +m[2] - 1, +m[3]) - Date.UTC(1899, 11, 30);
  return Math.round(ms / 86400000);
}

function cellXml(ref, cell) {
  const s = cell.s ?? 0;
  const v = cell.v;
  if (v === null || v === undefined || v === '') {
    return `<c r="${ref}" s="${s}"/>`;
  }
  // 日期样式：写真正的 Excel 日期值（序列号），否则会被当成文本，Excel 里没法做日期运算
  if (s === STYLES.DATE && typeof v === 'string') {
    const serial = dateToSerial(v);
    if (serial !== null) return `<c r="${ref}" s="${s}"><v>${serial}</v></c>`;
  }
  if (typeof v === 'number') {
    return `<c r="${ref}" s="${s}"><v>${v}</v></c>`;
  }
  if (typeof v === 'boolean') {
    return `<c r="${ref}" s="${s}" t="b"><v>${v ? 1 : 0}</v></c>`;
  }
  return `<c r="${ref}" s="${s}" t="inlineStr"><is><t xml:space="preserve">${esc(v)}</t></is></c>`;
}

/**
 * 生成工作表 XML
 * sheet = { name, cols:[{w}], rows:[[cell,...]], freeze:{row,col}, autoFilter:{ref} }
 */
function sheetXml(sheet) {
  const parts = [];
  parts.push(`<?xml version="1.0" encoding="UTF-8" standalone="yes"?>`);
  parts.push(`<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">`);
  if (sheet.cols && sheet.cols.length) {
    parts.push(`<cols>${sheet.cols.map((c, i) => `<col min="${i + 1}" max="${i + 1}" width="${c.w}" customWidth="1"/>`).join('')}</cols>`);
  }
  parts.push('<sheetData>');
  sheet.rows.forEach((row, ri) => {
    if (!row || !row.length) return;
    const cells = row.map((cell, ci) => cellXml(`${colName(ci)}${ri + 1}`, cell || {})).join('');
    parts.push(`<row r="${ri + 1}">${cells}</row>`);
  });
  parts.push('</sheetData>');
  if (sheet.autoFilter) parts.push(`<autoFilter ref="${sheet.autoFilter}"/>`);
  if (sheet.freeze) {
    const topLeft = `${colName(sheet.freeze.col || 0)}${(sheet.freeze.row || 0) + 1}`;
    parts.push(`<sheetViews><sheetView workbookViewId="0"><pane ySplit="${sheet.freeze.row || 0}" xSplit="${sheet.freeze.col || 0}" topLeftCell="${topLeft}" activePane="bottomRight" state="frozen"/></sheetView></sheetViews>`);
  }
  parts.push('</worksheet>');
  return parts.join('');
}

/**
 * 生成 xlsx
 * sheets = [{ name, cols, rows, freeze, autoFilter }]
 */
export function writeXlsx(sheets) {
  const entries = [];

  entries.push({
    name: '[Content_Types].xml',
    data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
${sheets.map((_, i) => `<Override PartName="/xl/worksheets/sheet${i + 1}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>`).join('')}
<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>`,
  });

  entries.push({
    name: '_rels/.rels',
    data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>`,
  });

  entries.push({
    name: 'docProps/core.xml',
    data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:creator>csdata-margin-ratio skill</dc:creator>
<cp:lastModifiedBy>csdata-margin-ratio skill</cp:lastModifiedBy>
<dcterms:created xsi:type="dcterms:W3CDTF">${new Date().toISOString()}</dcterms:created>
</cp:coreProperties>`,
  });

  entries.push({
    name: 'docProps/app.xml',
    data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
<Application>csdata-margin-ratio</Application>
</Properties>`,
  });

  entries.push({
    name: 'xl/workbook.xml',
    data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets>${sheets.map((s, i) => `<sheet name="${esc(s.name)}" sheetId="${i + 1}" r:id="rId${i + 1}"/>`).join('')}</sheets>
</workbook>`,
  });

  entries.push({
    name: 'xl/_rels/workbook.xml.rels',
    data: `<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
${sheets.map((_, i) => `<Relationship Id="rId${i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet${i + 1}.xml"/>`).join('')}
<Relationship Id="rId${sheets.length + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>`,
  });

  entries.push({ name: 'xl/styles.xml', data: STYLE_XML });
  sheets.forEach((s, i) => entries.push({ name: `xl/worksheets/sheet${i + 1}.xml`, data: sheetXml(s) }));

  return writeZip(entries);
}

export { STYLES, colName };
