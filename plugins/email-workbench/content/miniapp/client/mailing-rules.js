import { t, tt } from './i18n.js';
function invalid(message) {
  throw new Error(message);
}

/** Bounded RFC-style CSV parsing; cell contents remain text and never become executable code. */
export function parseMailingCsv(source, delimiter = ',') {
  if (source.length > 512 * 1024) invalid(t('名单不能超过 512 KiB。'));
  const text = source.replace(/^\uFEFF/u, '');
  const records = [];
  const sourceLines = [];
  let physicalLine = 1;
  let recordLine = 1;
  let record = [];
  let cell = '';
  let quoted = false;
  let endedQuote = false;
  const pushCell = () => {
    record.push(cell.trim());
    cell = '';
    endedQuote = false;
    if (record.length > 30) invalid(t('名单最多支持 30 列。'));
  };
  const pushRecord = () => {
    pushCell();
    records.push(record); sourceLines.push(recordLine);
    record = [];
    if (records.length > 101) invalid(t('每批最多 100 位收件人。'));
  };
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') {
        cell += '"';
        i += 1;
      } else if (char === '"') {
        quoted = false;
        endedQuote = true;
      } else {
        cell += char;
        if (char === '\n' || (char === '\r' && text[i + 1] !== '\n')) physicalLine += 1;
      }
    } else if (char === delimiter) pushCell();
    else if (char === '\r' || char === '\n') {
      if (char === '\r' && text[i + 1] === '\n') i += 1;
      pushRecord(); physicalLine += 1; recordLine = physicalLine;
    } else if (char === '"' && !cell && !endedQuote) quoted = true;
    else if (endedQuote || char === '"')
      invalid(t('CSV 引号格式不正确，请检查包含逗号或换行的单元格。'));
    else cell += char;
  }
  if (quoted) invalid(t('CSV 有未闭合的引号。'));
  if (cell || record.length || endedQuote) pushRecord();
  const headers = records.shift(); sourceLines.shift();
  if (!headers?.length || !records.length) invalid(t('请提供首行列名和至少一行收件人。'));
  if (
    headers.some((key) => !key || key.length > 60 || /[{}\r\n\0]/u.test(key)) ||
    new Set(headers).size !== headers.length
  )
    invalid(t('列名不能为空、重复或包含花括号。'));
  if (records.some((row) => row.length !== headers.length)) invalid(t('每行列数必须与首行列名一致。'));
  return { headers, records, sourceLines };
}

export function tableMailingRows(table, emailColumn) {
  const column = table.headers.indexOf(emailColumn);
  if (column < 0) invalid(t('请选择实际收件地址列。'));
  return table.records.map((record, index) => ({
    rowId: table.rowIds?.[index] ?? String(index + 2), sourceLine: table.sourceLines?.[index] ?? index + 2,
    address: record[column], fields: Object.fromEntries(table.headers.map((key, at) => [key, record[at]])),
  }));
}
export function prepareMailingRows(table, emailColumn, subject, body) {
  const analyzed = analyzeMailingRows(table, emailColumn, subject, body);
  if (analyzed.errors.length) invalid(tt`第 ${analyzed.errors[0].line} 行的${analyzed.errors[0].message}`);
  return analyzed.rows;
}
export function analyzeMailingRows(table, emailColumn, subject, body) {
  const inputs = tableMailingRows(table, emailColumn);
  const result = validateMailingList(inputs, { subject, text: body });
  const bad = new Set(result.errors.map((error) => error.rowId));
  return { rows: result.rows.filter((row) => !bad.has(row.rowId)).map((row) => ({
    ...row, line: row.sourceLine, fields: table.records[inputs.findIndex((input) => input.rowId === row.rowId)],
  })), errors: result.errors };
}

export function mailingFields(row) {
  const name = row.name ?? row.fields?.name ?? row.fields?.['姓名'] ?? '';
  return { ...row.fields, name, '姓名': name, email: row.address, '邮箱': row.address };
}
export function expandMailingTemplate(template, fields, html = false) {
  const escape = (value) => String(value).replace(/[&<>"']/gu, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
  const result = template.replace(/\{\{\s*([^{}]+?)\s*\}\}/gu, (_match, name) => {
    const key = name.trim();
    if (!Object.hasOwn(fields, key)) invalid(tt`模板引用了不存在的列：${key}`);
    if (!fields[key]?.trim()) invalid(tt`${key} 为空，请补齐后预览。`);
    return html ? escape(fields[key]) : fields[key];
  });
  if (/\{\{|\}\}/u.test(result)) invalid(t('仍有未替换的模板变量。'));
  return result;
}

/** The structured list rule is shared by the browser, Node and MCP adapters. */
export function validateMailingList(rows, template) {
  const errors = [];
  const expanded = [];
  if (!rows.length || rows.length > 100) errors.push({ rowId: '', line: 0, code: 'count', message: t('每批需要 1 至 100 位收件人。') });
  const seen = new Map();
  const ids = new Set();
  rows.forEach((row, index) => {
    const line = row.sourceLine ?? index + 1;
    const fail = (code, message) => errors.push({ rowId: row.rowId, line, code, message });
    if (ids.has(row.rowId)) fail('row_id', t('行标识重复。'));
    ids.add(row.rowId);
    const address = row.address.trim();
    if (!/^[^\s@<>,;]+@[^\s@<>,;]+\.[^\s@<>,;]+$/u.test(address) || address.length > 254)
      fail('address', t('收件地址格式不正确。'));
    const normalized = address.toLowerCase();
    if (seen.has(normalized)) fail('duplicate', tt`收件地址与第 ${seen.get(normalized)} 行重复。`);
    else seen.set(normalized, line);
    try {
      const fields = mailingFields({ ...row, address });
      const subject = expandMailingTemplate(template.subject, fields);
      const text = expandMailingTemplate(template.text, fields);
      const html = template.html === undefined ? undefined : expandMailingTemplate(template.html, fields, true);
      if (!subject.trim() || subject.length > 998 || /[\r\n\0]/u.test(subject)) invalid(t('主题为空、过长或含换行。'));
      if (!text.trim() || text.length > 200000 || /\0/u.test(text)) invalid(t('正文为空、过长或含无效字符。'));
      expanded.push({ ...row, address, subject, text, ...(html === undefined ? {} : { html }) });
    } catch (error) { fail('template', error.message); }
  });
  return { valid: errors.length === 0, errors, rows: expanded };
}

export function parseMailingImport(source) {
  const first = source.replace(/^\uFEFF/u, '').split(/\r?\n/u)[0];
  if (!first.includes(',') && !first.includes('\t') && first.includes('@')) {
    const table = parseMailingCsv(`邮箱\n${source}`);
    table.sourceLines = table.sourceLines.map((line) => line - 1);
    return table;
  }
  return parseMailingCsv(source, first.includes('\t') ? '\t' : ',');
}
