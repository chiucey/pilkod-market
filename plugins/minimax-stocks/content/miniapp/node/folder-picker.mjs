// @ts-check
// 系统文件夹选择框：macOS 访达（osascript choose folder）、Windows FolderBrowserDialog（PowerShell）、
// Linux zenity / kdialog。只把用户选中的路径交回；关联前仍由 resolveFolder 按规则校验。
import { execFile } from 'node:child_process';
import { existsSync } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';

const PICK_TIMEOUT_MS = 10 * 60_000;

export const MAC_PICK_SCRIPT = Object.freeze([
  'on run argv',
  'activate',
  'set chosen to choose folder with prompt (item 1 of argv) default location (POSIX file (item 2 of argv))',
  'return POSIX path of chosen',
  'end run',
]);

const WINDOWS_PICK_SCRIPT = [
  'Add-Type -AssemblyName System.Windows.Forms',
  '$owner = New-Object System.Windows.Forms.Form',
  '$owner.TopMost = $true',
  '$owner.ShowInTaskbar = $false',
  '$dialog = New-Object System.Windows.Forms.FolderBrowserDialog',
  '$dialog.Description = $env:MM_PICK_PROMPT',
  '$dialog.ShowNewFolderButton = $false',
  'if ($env:MM_PICK_DEFAULT) { $dialog.SelectedPath = $env:MM_PICK_DEFAULT }',
  '$result = $dialog.ShowDialog($owner)',
  '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8',
  'if ($result -eq [System.Windows.Forms.DialogResult]::OK) { [Console]::Out.Write($dialog.SelectedPath) } else { exit 3 }',
].join('; ');

export function folderPickerKind(platform = process.platform) {
  return platform === 'darwin' ? 'finder' : platform === 'win32' ? 'windows' : platform === 'linux' ? 'linux' : null;
}

function pickerError(code, message) {
  const error = new Error(message);
  /** @type {any} */ (error).code = code;
  return error;
}

/**
 * @param {{ platform?: string, home?: string, run?: (command: string, args: string[], options?: object) => Promise<{ code: number | string, stdout: string, stderr: string }> }} [options]
 */
export function createFolderPicker({ platform = process.platform, home = homedir(), run } = {}) {
  /** @type {Set<import('node:child_process').ChildProcess>} */
  const children = new Set();
  const exec = run ?? ((command, args, options = {}) => new Promise((resolve) => {
    const child = execFile(command, args, { timeout: PICK_TIMEOUT_MS, maxBuffer: 1024 * 1024, windowsHide: false, ...options }, (error, stdout, stderr) => {
      children.delete(child);
      resolve({ code: error ? (/** @type {any} */ (error).code ?? 1) : 0, stdout: String(stdout ?? ''), stderr: String(stderr ?? '') });
    });
    children.add(child);
  }));
  let busy = false;
  const kind = folderPickerKind(platform);

  /** @param {{ prompt?: string, defaultPath?: string }} [options] @returns {Promise<{ path: string } | { cancelled: true }>} */
  async function pick({ prompt = '选择要关联到「股市」资产页的资料文件夹', defaultPath } = {}) {
    if (!kind) throw pickerError('PICKER_UNSUPPORTED', '当前系统不支持文件夹选择框，请输入路径');
    if (busy) throw pickerError('PICKER_BUSY', '文件夹选择框已经打开，请先在弹出的窗口里选择或取消');
    busy = true;
    try {
      const start = [defaultPath, join(home, 'Documents'), home].find((path) => typeof path === 'string' && path && existsSync(path)) ?? home;
      if (kind === 'finder') {
        const result = await exec('osascript', [...MAC_PICK_SCRIPT.flatMap((line) => ['-e', line]), prompt, start]);
        if (result.code === 0) return { path: cleanPath(result.stdout) };
        if (/-128/.test(result.stderr)) return { cancelled: true };
        throw pickerError('PICKER_FAILED', '无法打开访达选择框：' + result.stderr.trim().slice(0, 160));
      }
      if (kind === 'windows') {
        const result = await exec('powershell.exe', ['-NoProfile', '-NonInteractive', '-STA', '-ExecutionPolicy', 'Bypass', '-Command', WINDOWS_PICK_SCRIPT], {
          env: { ...process.env, MM_PICK_PROMPT: prompt, MM_PICK_DEFAULT: start },
        });
        if (result.code === 0 && result.stdout.trim()) return { path: cleanPath(result.stdout) };
        if (result.code === 3 || (result.code === 0 && !result.stdout.trim())) return { cancelled: true };
        throw pickerError('PICKER_FAILED', '无法打开文件夹选择框：' + result.stderr.trim().slice(0, 160));
      }
      const zenity = await exec('zenity', ['--file-selection', '--directory', '--title=' + prompt, '--filename=' + start + '/']);
      if (zenity.code === 0) return { path: cleanPath(zenity.stdout) };
      if (zenity.code === 1) return { cancelled: true };
      if (zenity.code !== 'ENOENT') throw pickerError('PICKER_FAILED', '无法打开文件夹选择框');
      const kdialog = await exec('kdialog', ['--getexistingdirectory', start, '--title', prompt]);
      if (kdialog.code === 0) return { path: cleanPath(kdialog.stdout) };
      if (kdialog.code === 1) return { cancelled: true };
      throw pickerError('PICKER_UNSUPPORTED', '没有找到 zenity 或 kdialog，请输入路径');
    } finally {
      busy = false;
    }
  }

  return {
    kind,
    pick,
    dispose() {
      for (const child of children) child.kill('SIGTERM');
      children.clear();
    },
  };
}

function cleanPath(stdout) {
  const value = String(stdout).replace(/\r?\n$/, '').trim();
  return value.length > 1 ? value.replace(/[\\/]+$/, '') : value;
}
