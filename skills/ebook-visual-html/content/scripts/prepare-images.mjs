#!/usr/bin/env node
/**
 * prepare-images.mjs — 把扫描页/配图缩到网页尺寸
 *
 * 按 sips → magick → ffmpeg → python3+Pillow 顺序探测工具，逐张缩放为 JPEG。
 * 关键约束：必须校验产物是否真的落盘。sips 在受限环境里可能返回成功却没写文件，
 * 这种情况下直接换下一个工具，不重复跑同一条失败命令。
 *
 * 用法：
 *   node prepare-images.mjs <文件或目录…> --out assets/img [--max 1600] [--prefix p] [--name cover] [--force]
 *
 *   --out      输出目录（默认 assets/img）
 *   --max      长边上限像素，默认 1600
 *   --prefix   输出名前缀，默认 p（p001.jpg、p002.jpg…，编号 = 输入排序序号）
 *   --name     固定输出文件名，给单图/封面用（给了 --name 就不编号）
 *   --force    覆盖已存在的目标文件
 *   --quality  JPEG 质量，默认 82
 *   --dry-run  只打印将执行的命令
 */
import { readdirSync, statSync, mkdirSync, existsSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { join, resolve, basename, extname } from 'node:path';

const IMG_EXT = new Set(['.jpg', '.jpeg', '.png', '.webp', '.gif', '.tif', '.tiff', '.bmp', '.heic']);

const args = process.argv.slice(2);
const flagVal = (name, dflt) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : dflt;
};
const VAL_FLAGS = ['--out', '--max', '--prefix', '--name', '--quality'];
const inputs = [];
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (VAL_FLAGS.includes(a)) { i++; continue; }   // 跳过该 flag 的取值
  if (a.startsWith('--')) continue;               // --force / --dry-run 等布尔开关
  inputs.push(a);
}

const outDir = resolve(flagVal('--out', 'assets/img'));
const max = parseInt(flagVal('--max', '1600'), 10);
const prefix = flagVal('--prefix', 'p');
const fixedName = flagVal('--name', null);
const quality = parseInt(flagVal('--quality', '82'), 10);
const force = args.includes('--force');
const dryRun = args.includes('--dry-run');

if (!inputs.length) {
  console.error('用法: node prepare-images.mjs <文件或目录…> --out <目录> [--max 1600] [--name cover] [--force] [--dry-run]');
  process.exit(2);
}

/* ── 工具探测 ────────────────────────────────────── */

/** 二进制是否存在：ENOENT 说明没装，其他退出码说明装了（只是参数/用法不对） */
function canRun(cmd, probeArgs = []) {
  try { execFileSync(cmd, probeArgs, { stdio: 'ignore' }); return true; }
  catch (e) { return e.code !== 'ENOENT'; }
}

/** 探测命令必须成功返回（Pillow 这类靠 import 检测的情况） */
function probeOk(cmd, probeArgs) {
  try { execFileSync(cmd, probeArgs, { stdio: 'ignore' }); return true; }
  catch { return false; }
}

const TOOLS = [];
if (canRun('sips')) TOOLS.push('sips');
if (canRun('magick')) TOOLS.push('magick');
if (canRun('ffmpeg')) TOOLS.push('ffmpeg');
if (canRun('python3') && probeOk('python3', ['-c', 'import PIL'])) TOOLS.push('pillow');

if (!TOOLS.length) {
  console.error('[FAIL] 没找到可用的图像工具。');
  console.error('  macOS 自带 sips；跨平台可用 ImageMagick(brew install imagemagick) / ffmpeg / python3 + Pillow。');
  console.error('  不想装工具：可以跳过这一步直接用原图，但要在交付时告诉用户页面会偏重。');
  process.exit(1);
}
console.log('可用工具：' + TOOLS.join(' → '));

/* ── 收集输入 ────────────────────────────────────── */

function collect(p) {
  const abs = resolve(p);
  if (!existsSync(abs)) { console.error(`[WARN] 输入不存在：${p}`); return []; }
  const st = statSync(abs);
  if (st.isFile()) return [abs];
  return readdirSync(abs)
    .filter((f) => IMG_EXT.has(extname(f).toLowerCase()))
    .sort((a, b) => a.localeCompare(b, 'en', { numeric: true }))
    .map((f) => join(abs, f));
}

const files = inputs.flatMap(collect);
if (!files.length) { console.error('[FAIL] 没有找到图片'); process.exit(1); }

/* ── 缩放 ────────────────────────────────────────── */

mkdirSync(outDir, { recursive: true });

const PY = `import sys
from PIL import Image
im = Image.open(sys.argv[1])
im.thumbnail((int(sys.argv[3]), int(sys.argv[3])))
im.convert("RGB").save(sys.argv[2], "JPEG", quality=int(sys.argv[4]))
`;

function tryTool(tool, src, dst) {
  const run = (cmd, a) => {
    if (dryRun) { console.log('  [dry-run]', cmd, a.join(' ')); return; }
    execFileSync(cmd, a, { stdio: ['ignore', 'ignore', 'pipe'] });
  };
  try {
    if (tool === 'sips') {
      run('sips', ['-s', 'format', 'jpeg', '-s', 'formatOptions', String(quality),
        '--resampleWidth', String(max), src, '--out', dst]);
    } else if (tool === 'magick') {
      run('magick', [src, '-resize', `${max}x>`, '-quality', String(quality), dst]);
    } else if (tool === 'ffmpeg') {
      run('ffmpeg', ['-y', '-loglevel', 'error', '-i', src, '-vf',
        `scale='min(${max},iw)':-2`, '-q:v', String(Math.max(8, Math.round((100 - quality) / 6))), dst]);
    } else {
      run('python3', ['-c', PY, src, dst, String(max), String(quality)]);
    }
    // sips 在受限环境里可能「返回成功但没写文件」，所以这里必须验产物
    if (!dryRun && (!existsSync(dst) || statSync(dst).size === 0)) return false;
    return true;
  } catch (e) {
    const msg = (e.stderr || e.message || '').toString().split('\n')[0].slice(0, 160);
    if (dryRun) return true;
    console.error(`  ${tool} 失败：${msg}`);
    return false;
  }
}

const pad = String(Math.max(3, String(files.length).length));
let done = 0, skipped = 0;
const failed = [];

for (const [i, src] of files.entries()) {
  const name = fixedName ? `${fixedName}.jpg` : `${prefix}${String(i + 1).padStart(pad, '0')}.jpg`;
  const dst = join(outDir, name);

  if (!force && existsSync(dst) && statSync(dst).mtimeMs >= statSync(src).mtimeMs) {
    console.log(`跳过（已是最新）${name}`);
    skipped++;
    continue;
  }

  let okFlag = false;
  for (const tool of TOOLS) {
    if (tryTool(tool, src, dst)) { okFlag = true; break; }
  }

  if (okFlag) {
    const kb = dryRun ? '?' : (statSync(dst).size / 1024).toFixed(0);
    console.log(`✓ ${name}  ${kb}KB  ← ${basename(src)}`);
    done++;
  } else {
    console.error(`✗ ${basename(src)}：所有工具都没产出文件`);
    failed.push(src);
  }
}

console.log('');
console.log(`完成：${done} 张转换，${skipped} 张跳过${failed.length ? `，${failed.length} 张失败` : ''}`);
console.log(`输出目录：${outDir}`);
if (failed.length) {
  console.error('');
  console.error('失败的图没有替代品时，在 content.json 里用 {"type":"slot"} 占位，别把原图直链。');
  process.exit(1);
}
