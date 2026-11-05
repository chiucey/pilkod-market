// xls-read.mjs — 纯 Node 实现的 .xls (BIFF8 / OLE2 复合文档) 解析
// 目的：让技能在没有 LibreOffice 的环境也能读老格式文件（中证数据 2024 年的文件是 .xls）
// 覆盖记录：LABELSST / LABEL / NUMBER / RK / MULRK / FORMULA(+STRING) / BLANK / MULBLANK
import zlib from 'node:zlib';

const SIG = Buffer.from([0xd0, 0xcf, 0x11, 0xe0, 0xa1, 0xb1, 0x1a, 0xe1]);

/** 解析 OLE2 复合文档，返回 { 流名: Buffer } */
function readOle(buf) {
  if (!buf.subarray(0, 8).equals(SIG)) throw new Error('不是 OLE2 复合文档（.xls 头不匹配）');
  const sectorSize = 1 << buf.readUInt16LE(30);
  const miniSectorSize = 1 << buf.readUInt16LE(32);
  const numFatSectors = buf.readUInt32LE(44);
  const dirStart = buf.readUInt32LE(48);
  const miniCutoff = buf.readUInt32LE(56);
  const miniFatStart = buf.readUInt32LE(60);
  const numMiniFat = buf.readUInt32LE(64);
  const difatStart = buf.readUInt32LE(68);
  const numDifat = buf.readUInt32LE(72);

  const sectorOffset = (n) => (n + 1) * sectorSize;
  const sector = (n) => buf.subarray(sectorOffset(n), sectorOffset(n) + sectorSize);

  // DIFAT → FAT 扇区号
  const fatSectors = [];
  for (let i = 0; i < 109 && fatSectors.length < numFatSectors; i++) {
    const s = buf.readUInt32LE(76 + i * 4);
    if (s === 0xffffffff) break;
    fatSectors.push(s);
  }
  let difatSector = difatStart;
  for (let k = 0; k < numDifat && difatSector !== 0xffffffff && difatSector !== 0xfffffffe; k++) {
    const s = sector(difatSector);
    for (let i = 0; i < (sectorSize / 4) - 1; i++) {
      const v = s.readUInt32LE(i * 4);
      if (v === 0xffffffff) break;
      fatSectors.push(v);
    }
    difatSector = s.readUInt32LE(sectorSize - 4);
  }

  // FAT
  const fat = [];
  for (const fs of fatSectors) {
    const s = sector(fs);
    for (let i = 0; i < sectorSize / 4; i++) fat.push(s.readUInt32LE(i * 4));
  }
  const fatChain = (start) => {
    const out = [];
    let cur = start;
    const seen = new Set();
    while (cur !== 0xfffffffe && cur !== 0xffffffff && cur < fat.length && !seen.has(cur)) {
      seen.add(cur); out.push(cur); cur = fat[cur];
    }
    return out;
  };
  const readChain = (start, size) => {
    const parts = fatChain(start).map(sector);
    const all = Buffer.concat(parts);
    return size != null ? all.subarray(0, size) : all;
  };

  // 目录
  const dirBuf = readChain(dirStart);
  const entries = [];
  for (let off = 0; off + 128 <= dirBuf.length; off += 128) {
    const nameLen = dirBuf.readUInt16LE(off + 64);
    if (nameLen === 0) continue;
    const name = dirBuf.toString('utf16le', off, off + Math.max(0, nameLen - 2));
    const type = dirBuf.readUInt8(off + 66);
    const start = dirBuf.readUInt32LE(off + 116);
    const size = Number(dirBuf.readBigUInt64LE(off + 120));
    entries.push({ name, type, start, size });
  }

  // mini stream（根目录条目）
  const root = entries.find((e) => e.type === 5);
  const miniStream = root ? readChain(root.start, root.size) : Buffer.alloc(0);

  // miniFAT
  const miniFat = [];
  if (numMiniFat > 0 && miniFatStart !== 0xfffffffe) {
    const mf = readChain(miniFatStart);
    for (let i = 0; i + 4 <= mf.length; i += 4) miniFat.push(mf.readUInt32LE(i));
  }
  const readMini = (start, size) => {
    const parts = [];
    let cur = start;
    const seen = new Set();
    while (cur !== 0xfffffffe && cur !== 0xffffffff && !seen.has(cur)) {
      seen.add(cur);
      parts.push(miniStream.subarray(cur * miniSectorSize, (cur + 1) * miniSectorSize));
      cur = miniFat[cur];
    }
    return Buffer.concat(parts).subarray(0, size);
  };

  const streams = {};
  for (const e of entries) {
    if (e.type !== 2) continue;
    streams[e.name] = e.size < miniCutoff ? readMini(e.start, e.size) : readChain(e.start, e.size);
  }
  return streams;
}

/**
 * 读 BIFF8 字符串。结构顺序不能错：
 * cch → grbit → [fRichSt: cRun(2) + rgb(cRun*4)] → [fExtSt: cbExtRst(4) + ExtRst] → 字符数据
 * 头部在字符数据之前，跳过偏移算错就会解析越界。
 */
function readUnicodeString(buf, pos, lenBytes) {
  if (pos + lenBytes + 1 > buf.length) return { text: '', next: buf.length };
  const cch = lenBytes === 2 ? buf.readUInt16LE(pos) : buf.readUInt8(pos);
  let p = pos + lenBytes;
  const flags = buf.readUInt8(p); p += 1;
  let richRuns = 0;
  if (flags & 0x08) { if (p + 2 > buf.length) return { text: '', next: buf.length }; richRuns = buf.readUInt16LE(p); p += 2; }
  let extSize = 0;
  if (flags & 0x04) { if (p + 4 > buf.length) return { text: '', next: buf.length }; extSize = buf.readUInt32LE(p); p += 4; }
  const wide = (flags & 0x01) !== 0;
  const need = cch * (wide ? 2 : 1);
  if (p + need > buf.length) return { text: '', next: buf.length };
  let out = '';
  if (wide) { for (let i = 0; i < cch; i++) out += String.fromCharCode(buf.readUInt16LE(p + i * 2)); }
  else { for (let i = 0; i < cch; i++) out += String.fromCharCode(buf.readUInt8(p + i)); }
  p += need;
  if (flags & 0x08) p += richRuns * 4;
  if (flags & 0x04) p += extSize;
  return { text: out, next: Math.min(p, buf.length) };
}

/** RK 编码 → 数值 */
function decodeRK(rk) {
  const isMul100 = rk & 0x01;
  const isInt = rk & 0x02;
  let v;
  if (isInt) {
    v = rk >> 2;                      // 有符号 30 位整数
  } else {
    const b = Buffer.alloc(8);
    b.writeUInt32LE(0, 0);
    b.writeInt32LE(rk & 0xfffffffc, 4);
    v = b.readDoubleLE(0);
  }
  if (isMul100) v /= 100;
  return v;
}

/**
 * 读取 .xls → { sheets: [{ name, cells: Map('r,c' -> {v, t}) }] }
 * t: 'n' 数字 / 's' 文本 / 'b' 布尔
 */
export function readXls(buf) {
  const streams = readOle(buf);
  const wb = streams['Workbook'] || streams['Book'];
  if (!wb) throw new Error('未找到 Workbook 流，可能不是 BIFF8 .xls');

  // 记录流
  const records = [];
  let p = 0;
  while (p + 4 <= wb.length) {
    const type = wb.readUInt16LE(p);
    const len = wb.readUInt16LE(p + 2);
    records.push({ type, data: wb.subarray(p + 4, p + 4 + len) });
    p += 4 + len;
  }

  // SST
  let sst = [];
  const sstRec = records.find((r) => r.type === 0x00fc);
  if (sstRec) {
    const d = sstRec.data;
    const unique = d.readUInt32LE(4);
    let q = 8;
    for (let i = 0; i < unique && q + 3 <= d.length; i++) {
      const r = readUnicodeString(d, q, 2);
      sst.push(r.text);
      q = r.next;
    }
  }

  // BOUNDSHEET → 各 sheet 起始偏移
  const sheetDefs = [];
  for (const r of records) {
    if (r.type !== 0x0085) continue;
    const pos = r.data.readUInt32LE(0);
    const grbit = r.data.readUInt8(4);
    const nm = readUnicodeString(r.data, 6, 1);
    sheetDefs.push({ name: nm.text, pos, hidden: grbit & 0x03 });
  }

  const sheets = [];
  for (const def of sheetDefs) {
    const cells = new Map();
    let i = records.findIndex((r, idx) => idx > 0 && r.type === 0x0809 && r.data.readUInt16LE(0) === 0x0100);
    // 定位到该 sheet 的 BOF：按顺序数 BOF
    let bofCount = 0;
    let startIdx = 0;
    for (let k = 0; k < records.length; k++) {
      if (records[k].type === 0x0809) {
        if (bofCount === sheetDefs.indexOf(def) + 1) { startIdx = k; break; }
        bofCount++;
      }
    }
    let pendingFormula = null;
    for (let k = startIdx; k < records.length; k++) {
      const rec = records[k];
      if (rec.type === 0x000a) break;              // EOF
      const d = rec.data;
      switch (rec.type) {
        case 0x00fd: {                               // LABELSST
          const row = d.readUInt16LE(0), col = d.readUInt16LE(2);
          const idx = d.readUInt32LE(6);
          cells.set(`${row},${col}`, { v: sst[idx] ?? '', t: 's' });
          break;
        }
        case 0x0204: {                               // LABEL
          const row = d.readUInt16LE(0), col = d.readUInt16LE(2);
          const r = readUnicodeString(d, 6, 2);
          cells.set(`${row},${col}`, { v: r.text, t: 's' });
          break;
        }
        case 0x0203: {                               // NUMBER
          const row = d.readUInt16LE(0), col = d.readUInt16LE(2);
          cells.set(`${row},${col}`, { v: d.readDoubleLE(6), t: 'n' });
          break;
        }
        case 0x027e: {                               // RK
          const row = d.readUInt16LE(0), col = d.readUInt16LE(2);
          cells.set(`${row},${col}`, { v: decodeRK(d.readUInt32LE(6)), t: 'n' });
          break;
        }
        case 0x00bd: {                               // MULRK
          const row = d.readUInt16LE(0), colFirst = d.readUInt16LE(2);
          const n = (d.length - 6) / 6;
          for (let k = 0; k < n; k++) {
            const off = 4 + k * 6;
            cells.set(`${row},${colFirst + k}`, { v: decodeRK(d.readUInt32LE(off + 2)), t: 'n' });
          }
          break;
        }
        case 0x0006: {                               // FORMULA
          const row = d.readUInt16LE(0), col = d.readUInt16LE(2);
          const kind = d.readUInt8(12);
          if (kind === 0xff) {                       // 字符串结果，跟随 STRING 记录
            pendingFormula = { row, col };
          } else if (kind === 0x01) {                // 布尔
            cells.set(`${row},${col}`, { v: d.readUInt8(6) !== 0, t: 'b' });
          } else {
            cells.set(`${row},${col}`, { v: d.readDoubleLE(6), t: 'n' });
          }
          break;
        }
        case 0x0207: {                               // STRING（FORMULA 的字符串结果）
          if (pendingFormula) {
            const r = readUnicodeString(d, 0, 2);
            cells.set(`${pendingFormula.row},${pendingFormula.col}`, { v: r.text, t: 's' });
            pendingFormula = null;
          }
          break;
        }
        default: break;
      }
    }
    sheets.push({ name: def.name, cells });
  }

  return { sheets };
}

/** 把 cells Map 转成二维行数组 */
export function xlsRows(sheet) {
  const rows = [];
  for (const [key, cell] of sheet.cells) {
    const [r, c] = key.split(',').map(Number);
    if (!rows[r]) rows[r] = [];
    rows[r][c] = cell;
  }
  return rows;
}
