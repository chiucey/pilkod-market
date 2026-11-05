// @ts-check
// 用系统默认应用打开本地资料文件或网页（macOS open / Windows explorer / Linux xdg-open）。
// 只由服务端调用；调用方负责先校验目标：文件必须在关联的资料文件夹里，链接只能是 http(s)。
import { execFile } from 'node:child_process';

/**
 * @param {{ platform?: string, run?: (file: string, args: string[], options: { ignoreExitCode: boolean }) => Promise<void> }} [options]
 */
export function createOpener({ platform = process.platform, run = runCommand } = {}) {
  const supported = platform === 'darwin' || platform === 'win32' || platform === 'linux';
  const command = (target) => (platform === 'darwin' ? ['open', [target]] : platform === 'win32' ? ['explorer.exe', [target]] : ['xdg-open', [target]]);
  return {
    supported,
    /** @param {string} target 绝对路径或 http(s) 链接 */
    async open(target) {
      if (!supported) throw Object.assign(new Error('当前系统不支持用默认应用打开'), { code: 'OPEN_UNSUPPORTED' });
      if (typeof target !== 'string' || !target || target.startsWith('-')) throw Object.assign(new Error('无效的打开目标'), { code: 'OPEN_INVALID' });
      const [file, args] = command(target);
      // explorer.exe 打开成功也可能返回非零退出码。
      await run(file, args, { ignoreExitCode: platform === 'win32' });
    },
  };
}

function runCommand(file, args, { ignoreExitCode }) {
  return new Promise((resolve, reject) => {
    execFile(file, args, { timeout: 15_000, windowsHide: true }, (error) => {
      if (error && !(ignoreExitCode && typeof error.code === 'number')) {
        reject(Object.assign(new Error(error.code === 'ENOENT' ? '找不到系统的打开命令' : '系统没有能打开它的应用'), { code: 'OPEN_FAILED' }));
      } else resolve();
    });
  });
}
