// @ts-check
// 关联文件夹：路径校验、只读扫描、按 (size, mtime) 缓存的 SHA-256。
// 只读用户资料，不跟随符号链接，跳过隐藏目录、依赖目录和本插件写出的 _wiki/。
import { createHash } from 'node:crypto';
import { createReadStream } from 'node:fs';
import { readdir, realpath, stat } from 'node:fs/promises';
import { homedir } from 'node:os';
import { basename, extname, isAbsolute, join, relative, sep } from 'node:path';

export const WIKI_DIR_NAME = '_wiki';

export const ASSET_EXTENSIONS = Object.freeze({
  '.pdf': 'PDF', '.doc': 'Word', '.docx': 'Word', '.ppt': 'PPT', '.pptx': 'PPT',
  '.xls': 'Excel', '.xlsx': 'Excel', '.csv': 'CSV', '.md': 'Markdown', '.markdown': 'Markdown',
  '.txt': '文本', '.html': '网页', '.htm': '网页', '.rtf': '文本',
});

const SKIP_DIRS = new Set([WIKI_DIR_NAME, 'node_modules', '__pycache__', 'venv', 'site-packages', 'dist-packages']);
const SENSITIVE_TOP = new Set(['Library', '.ssh', '.gnupg', '.aws', '.config', '.kube', '.docker', '.Trash']);
export const MAX_HASH_BYTES = 300 * 1024 * 1024;

function folderError(message) {
  const error = new Error(message);
  /** @type {any} */ (error).code = 'INVALID_FOLDER';
  return error;
}

const SYSTEM_ROOTS = ['/System', '/Library', '/usr', '/bin', '/sbin', '/etc', '/private', '/var', '/opt', '/Applications', '/proc', '/sys', '/dev', '/boot', '/root', '/tmp'];

/** 系统文件夹选择框里用户亲自选的位置：允许外接盘等用户目录之外的位置，但不允许磁盘根、卷根和系统目录。 */
function pickerLocationAllowed(real) {
  if (/^[a-zA-Z]:\\?$/.test(real) || real === sep) return false;
  if (/^[a-zA-Z]:\\(windows|program files|program files \(x86\)|programdata)(\\|$)/i.test(real)) return false;
  if (/^\/Volumes\/[^/]+$/.test(real)) return false;
  return !SYSTEM_ROOTS.some((root) => real === root || real.startsWith(root + '/'));
}

/**
 * 校验并解析成真实路径。普通文件夹必须在用户目录下、不能是用户目录本身、~/Library 或顶层隐藏目录；
 * 当前对话文件夹（fromSession）允许 ~/.mavis/workspace 这类顶层隐藏目录，但仍拒绝凭据类目录；
 * 系统文件夹选择框（fromPicker）选中的位置还可以在用户目录之外（例如外接盘），系统目录除外。
 * @param {unknown} input @param {{ fromSession?: boolean, fromPicker?: boolean, home?: string }} [options]
 */
export async function resolveFolder(input, { fromSession = false, fromPicker = false, home = homedir() } = {}) {
  if (typeof input !== 'string' || !input.trim() || input.length > 1024 || input.includes('\0')) throw folderError('请输入文件夹路径');
  let path = input.trim();
  if (path === '~' || path.startsWith('~/')) path = join(home, path.slice(1));
  if (!isAbsolute(path)) throw folderError('请输入绝对路径（可以用 ~/ 开头）');
  const real = await realpath(path).catch(() => null);
  if (!real) throw folderError('这个文件夹不存在');
  const info = await stat(real).catch(() => null);
  if (!info?.isDirectory()) throw folderError('这不是一个文件夹');
  const realHome = await realpath(home).catch(() => home);
  if (real === realHome || real === sep) throw folderError('不能关联整个用户目录或磁盘根目录，请选择具体的资料文件夹');
  if (!real.startsWith(realHome + sep)) {
    if (fromPicker && !realHome.startsWith(real + sep) && pickerLocationAllowed(real)) return real;
    throw folderError(fromPicker ? '不能关联磁盘根目录或系统目录，请选择具体的资料文件夹' : '只能关联用户目录下的文件夹；其他位置请用「选择文件夹」');
  }
  const first = real.slice(realHome.length + 1).split(sep)[0];
  if (SENSITIVE_TOP.has(first)) throw folderError('不能关联系统或凭据目录');
  if (!fromSession && !fromPicker && first.startsWith('.')) throw folderError('不能关联隐藏目录');
  return real;
}

export function folderId(realPath) {
  return createHash('sha1').update(realPath).digest('hex').slice(0, 10);
}

/**
 * 递归列出资料文件。
 * @param {string} root
 * @param {{ maxDepth?: number, maxEntries?: number, maxFiles?: number }} [options]
 */
export async function scanFolder(root, { maxDepth = 8, maxEntries = 30_000, maxFiles = 3_000 } = {}) {
  /** @type {{ rel: string, size: number, mtimeMs: number, ext: string }[]} */
  const files = [];
  let entries = 0;
  let truncated = false;
  /** @param {string} dir @param {number} depth */
  const walk = async (dir, depth) => {
    if (truncated) return;
    let list;
    try {
      list = await readdir(dir, { withFileTypes: true });
    } catch {
      return;
    }
    list.sort((a, b) => a.name.localeCompare(b.name, 'zh-CN'));
    for (const entry of list) {
      entries += 1;
      if (entries > maxEntries || files.length >= maxFiles) { truncated = true; return; }
      if (entry.isSymbolicLink()) continue;
      const name = entry.name;
      if (name.startsWith('.') || name.startsWith('~$')) continue;
      const full = join(dir, name);
      if (entry.isDirectory()) {
        if (SKIP_DIRS.has(name) || depth >= maxDepth) continue;
        await walk(full, depth + 1);
      } else if (entry.isFile()) {
        const ext = extname(name).toLowerCase();
        if (!(ext in ASSET_EXTENSIONS)) continue;
        const info = await stat(full).catch(() => null);
        if (!info) continue;
        files.push({ rel: relative(root, full).split(sep).join('/'), size: info.size, mtimeMs: Math.round(info.mtimeMs), ext });
      }
    }
  };
  await walk(root, 0);
  return { files, truncated };
}

/** @param {string} path */
export function hashFile(path) {
  return new Promise((resolve, reject) => {
    const hash = createHash('sha256');
    const stream = createReadStream(path);
    stream.on('data', (chunk) => hash.update(chunk));
    stream.on('error', reject);
    stream.on('end', () => resolve(hash.digest('hex')));
  });
}

/** 按 path|size|mtime 缓存哈希，避免每次扫描都读全量文件。 */
export function createHashCache(initial = {}) {
  /** @type {Map<string, string>} */
  const map = new Map(Object.entries(initial && typeof initial === 'object' ? initial : {}).filter(([, value]) => typeof value === 'string'));
  let dirty = false;
  return {
    /** @param {string} path @param {number} size @param {number} mtimeMs */
    async get(path, size, mtimeMs) {
      if (size > MAX_HASH_BYTES) return null;
      const key = path + '|' + size + '|' + mtimeMs;
      const cached = map.get(key);
      if (cached) return cached;
      const value = /** @type {string} */ (await hashFile(path));
      map.set(key, value);
      dirty = true;
      if (map.size > 20_000) {
        for (const oldest of map.keys()) { map.delete(oldest); if (map.size <= 15_000) break; }
      }
      return value;
    },
    get dirty() { return dirty; },
    toJSON() { dirty = false; return Object.fromEntries(map); },
  };
}

export function folderLabel(realPath) {
  return basename(realPath) || realPath;
}
