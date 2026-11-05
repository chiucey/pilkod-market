// ponytail — MiniMax Code SessionStart 激活 hook
//
// 每次会话启动时：
//   1. 按 stdin 的 source 决定档位
//   2. 把档位写进状态文件（${PLUGIN_DATA}/.ponytail-active），子代理 hook 读它
//   3. 以 SessionStart 上下文注入当前档位的规则集
//
// 本包只有 MiniMax 一条路径：没有 Cursor/Codex/Copilot 分支，也没有状态栏检测。

const { DEFAULT_MODE, getDefaultMode } = require('./ponytail-config');
const { getPonytailInstructions } = require('./ponytail-instructions');
const { clearMode, readMode, setMode, writeHookOutput } = require('./ponytail-runtime');

// 沿用当前档位、不重置的 source：会话恢复 / 压缩 / 分叉都不是新会话，
// 用户已经选好的档位不该被悄悄打回默认档。
// ponytail: 上游只认 compact，resume/fork 会掉回默认档 —— ultra 会掉成 full。
// 这是上游行为、不是我们的目标，所以按 MiniMax 的取值补齐这三种。
const RESUME_SOURCES = ['resume', 'compact', 'fork'];

function resolveMode(source) {
  if (RESUME_SOURCES.indexOf(source) !== -1) {
    // 读不到现场档位（比如从没激活过）就用默认档
    return readMode() || getDefaultMode();
  }
  // startup / clear / 解析失败 —— 一律当作新会话，从默认档开始
  return getDefaultMode();
}

function activate(mode) {
  // off 档：完全不激活 —— 不写状态、不注入规则。
  if (mode === 'off') {
    clearMode();
    process.exit(0);
  }

  // 写状态：子代理 hook 靠它判断 ponytail 是否启用
  try {
    setMode(mode);
  } catch (e) {
    // 静默兜底：状态写失败不该让会话起不来
  }

  // 注入当前档位的规则集
  try {
    writeHookOutput('SessionStart', mode, getPonytailInstructions(mode));
  } catch (e) {
    // 静默兜底：进程退出时 stdout 关闭/EPIPE 不该变成 hook 失败
  }
}

let input = '';
let done = false;

function finish() {
  if (done) return;
  done = true;

  let source = '';
  try {
    // 剥掉 UTF-8 BOM：某些 shell 管道会加，会让 JSON.parse 直接失败
    source = JSON.parse(input.replace(/^\uFEFF/, '')).source;
  } catch (e) {
    // 没有 payload 或解析失败 —— 当作新会话
  }

  // mode 先给一个一定合法的值：resolveMode 再抛异常也不会把非法档位带进 activate
  let mode = DEFAULT_MODE;
  try {
    mode = resolveMode(source);
  } catch (e) {
    // 静默兜底：档位解析失败就留在默认档
  }
  activate(mode);
}

process.stdin.on('data', chunk => { input += chunk; });
// 绝不让会话卡住（上游 #443、#790）：stdin 出错或超时都要恢复。
// 兜底定时器保持 ref'd —— Windows 上卡住的 ref'd stdin 会让事件循环活着，
// 而未 ref 的定时器压根不会被调度，hook 就会一直挂到外部看门狗超时。
process.stdin.on('end', () => { finish(); process.exit(0); });
process.stdin.on('error', () => { finish(); process.exit(0); });
setTimeout(() => { finish(); process.exit(0); }, 1000);
