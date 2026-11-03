// Android preview frames: decode raw `adb exec-out screencap` output and turn it
// into a small PNG. Raw capture skips the phone-side PNG compression, which is the
// slow part on real devices; the box downscale and encoder are adapted from the
// zero-dependency PNG helper of the earlier Pilkod mobilerun plugin.

import { deflateSync } from 'node:zlib';

const SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
// HAL pixel formats screencap reports: 1 RGBA_8888, 2 RGBX_8888, 5 BGRA_8888.
const FORMATS = new Map([[1, 'rgba'], [2, 'rgba'], [5, 'bgra']]);
const MAX_SIDE = 8192;

const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n += 1) {
    let c = n;
    for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(buffer) {
  let crc = 0xffffffff;
  for (let i = 0; i < buffer.length; i += 1) crc = CRC_TABLE[(crc ^ buffer[i]) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

/**
 * Parse the raw screencap header. Android 9+ writes width, height, format and a
 * color space (16 bytes); older releases omit the color space (12 bytes).
 * @param {Buffer} raw
 * @returns {{ width: number, height: number, order: string, offset: number } | null}
 */
export function parseRawHeader(raw) {
  if (!Buffer.isBuffer(raw) || raw.length < 16) return null;
  const width = raw.readUInt32LE(0);
  const height = raw.readUInt32LE(4);
  const order = FORMATS.get(raw.readUInt32LE(8));
  if (!order || !width || !height || width > MAX_SIDE || height > MAX_SIDE) return null;
  const pixels = width * height * 4;
  for (const offset of [16, 12]) {
    if (raw.length >= offset + pixels && raw.length - offset - pixels < 4) return { width, height, order, offset };
  }
  return null;
}

function chunk(type, body) {
  const head = Buffer.alloc(8);
  head.writeUInt32BE(body.length, 0);
  head.write(type, 4, 'latin1');
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([head.subarray(4), body])), 0);
  return Buffer.concat([head, body, crc]);
}

/**
 * Downscale a raw screencap by an integer box factor so the width stays within
 * maxWidth, then encode an RGB PNG.
 * @param {Buffer} raw
 * @param {number} [maxWidth]
 * @returns {{ png: Buffer, width: number, height: number, scale: number } | null}
 */
export function rawToPng(raw, maxWidth = 540) {
  const header = parseRawHeader(raw);
  if (!header) return null;
  const factor = Math.max(1, Math.ceil(header.width / maxWidth));
  const width = Math.floor(header.width / factor);
  const height = Math.floor(header.height / factor);
  const red = header.order === 'bgra' ? 2 : 0;
  const blue = 2 - red;
  const stride = width * 3;
  const area = factor * factor;
  const half = area >> 1;
  // One filter byte (Up) per row, then RGB samples stored as differences to the row above.
  const out = Buffer.alloc((stride + 1) * height);
  let previous = Buffer.alloc(stride);
  let current = Buffer.alloc(stride);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      let r = 0;
      let g = 0;
      let b = 0;
      for (let dy = 0; dy < factor; dy += 1) {
        let index = header.offset + ((y * factor + dy) * header.width + x * factor) * 4;
        for (let dx = 0; dx < factor; dx += 1) {
          r += raw[index + red];
          g += raw[index + 1];
          b += raw[index + blue];
          index += 4;
        }
      }
      const target = x * 3;
      current[target] = (r + half) / area;
      current[target + 1] = (g + half) / area;
      current[target + 2] = (b + half) / area;
    }
    const row = y * (stride + 1);
    out[row] = 2;
    for (let i = 0; i < stride; i += 1) out[row + 1 + i] = (current[i] - previous[i]) & 0xff;
    [previous, current] = [current, previous];
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(width, 0);
  ihdr.writeUInt32BE(height, 4);
  ihdr[8] = 8;
  ihdr[9] = 2;
  const png = Buffer.concat([SIGNATURE, chunk('IHDR', ihdr), chunk('IDAT', deflateSync(out, { level: 3 })), chunk('IEND', Buffer.alloc(0))]);
  return { png, width, height, scale: factor };
}
