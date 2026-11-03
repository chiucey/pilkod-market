// @ts-check
// 从 docx / pptx / xlsx（OOXML zip 包）里取纯文本，只用于个股资料的关键词匹配。只读，带大小上限。
import { readFile } from 'node:fs/promises';
import { inflateRawSync } from 'node:zlib';

export const MAX_OFFICE_BYTES = 40 * 1024 * 1024;
const MAX_TEXT_BYTES = 8 * 1024 * 1024;

const PARTS = {
  '.docx': /^word\/(document|footnotes|endnotes|header\d*|footer\d*)\.xml$/,
  '.pptx': /^ppt\/(slides\/slide\d+|notesSlides\/notesSlide\d+)\.xml$/,
  '.xlsx': /^xl\/(sharedStrings|worksheets\/sheet\d+)\.xml$/,
};

/** @param {string} path @param {string} ext */
export async function extractOfficeText(path, ext) {
  const pattern = PARTS[ext];
  if (!pattern) return '';
  const buffer = await readFile(path);
  if (buffer.length > MAX_OFFICE_BYTES) return '';
  return officeTextFromBuffer(buffer, pattern);
}

/** @param {Buffer} buffer @param {RegExp} pattern */
export function officeTextFromBuffer(buffer, pattern) {
  let out = '';
  for (const entry of listZip(buffer)) {
    if (!pattern.test(entry.name)) continue;
    const xml = readEntry(buffer, entry);
    if (xml) out += xmlToText(xml) + '\n';
    if (out.length > MAX_TEXT_BYTES) break;
  }
  return out;
}

function listZip(buffer) {
  const min = Math.max(0, buffer.length - 65_557);
  let eocd = -1;
  for (let i = buffer.length - 22; i >= min; i -= 1) {
    if (buffer.readUInt32LE(i) === 0x06054b50) { eocd = i; break; }
  }
  if (eocd < 0) return [];
  const count = buffer.readUInt16LE(eocd + 10);
  let offset = buffer.readUInt32LE(eocd + 16);
  const entries = [];
  for (let n = 0; n < count && offset + 46 <= buffer.length; n += 1) {
    if (buffer.readUInt32LE(offset) !== 0x02014b50) break;
    const nameLength = buffer.readUInt16LE(offset + 28);
    entries.push({
      method: buffer.readUInt16LE(offset + 10),
      compressedSize: buffer.readUInt32LE(offset + 20),
      localOffset: buffer.readUInt32LE(offset + 42),
      name: buffer.toString('utf8', offset + 46, offset + 46 + nameLength),
    });
    offset += 46 + nameLength + buffer.readUInt16LE(offset + 30) + buffer.readUInt16LE(offset + 32);
  }
  return entries;
}

function readEntry(buffer, entry) {
  const at = entry.localOffset;
  if (at + 30 > buffer.length || buffer.readUInt32LE(at) !== 0x04034b50) return '';
  const start = at + 30 + buffer.readUInt16LE(at + 26) + buffer.readUInt16LE(at + 28);
  const data = buffer.subarray(start, start + entry.compressedSize);
  try {
    if (entry.method === 0) return data.toString('utf8');
    if (entry.method === 8) return inflateRawSync(data, { maxOutputLength: MAX_TEXT_BYTES * 2 }).toString('utf8');
  } catch {
    return '';
  }
  return '';
}

export function xmlToText(xml) {
  return String(xml)
    .replace(/<\/(w:p|a:p|si|row)>/g, '\n')
    .replace(/<(w:tab|w:br|a:br)\b[^>]*\/>/g, ' ')
    .replace(/<[^>]+>/g, '')
    .replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&apos;/g, "'")
    .replace(/&#(\d+);/g, (_, code) => String.fromCodePoint(Number(code)))
    .replace(/&amp;/g, '&');
}
