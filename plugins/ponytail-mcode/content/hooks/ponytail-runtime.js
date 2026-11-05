const fs = require('fs');
const path = require('path');
const { createHash } = require('crypto');
const { getConfigDir } = require('./ponytail-config');

// 本包只有 MiniMax 一条路径：hook 一律由 MiniMax Code 的 runtime 拉起，
// 输出信封统一为 {"hookSpecificOutput":{"hookEventName":…,"additionalContext":…}}。
// 上游那套按宿主（Copilot / Codex / Qoder / CodeBuddy / Cursor / 原生 Claude）
// 分叉的判定在这里一个都不存在 —— 单一路径也意味着不必记住哪个事件该走哪种输出格式。

// 状态目录：优先用 MiniMax 注入的可写数据目录 ${PLUGIN_DATA}，拿不到时退回配置目录。
const stateDir = process.env.PLUGIN_DATA || getConfigDir();

const statePath = path.join(stateDir, '.ponytail-active');

// 按仓隔离的档位：MiniMax 会把本轮工作区注入 CLAUDE_PROJECT_DIR，所以上游那套隔离原样可用 ——
// 不同仓库里的并发会话不会互相覆盖档位（上游 #662、#809）。
// ponytail: 同一个仓库内的会话仍共享同一档位；若这点不能接受，再按 session_id 分键。
const projectDir = (process.env.CLAUDE_PROJECT_DIR || '').trim();
// 把分隔符统一成 '_'，避免 /work/a/b 与 /work/a_b 撞键（上游 #662）。
// 不读旧的去敏键：它们无法安全地归到某一个项目上。
const projectStatePath = projectDir
  ? path.join(stateDir, 'ponytail-modes',
    createHash('sha256').update(path.normalize(projectDir)).digest('hex'))
  : null;

// 共享标记照样写，方便没有 project 目录的场景读取。
function setMode(mode) {
  for (const file of [projectStatePath, statePath]) {
    if (!file) continue;
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, mode);
  }
}

function clearMode() {
  for (const file of [projectStatePath, statePath]) {
    if (file) try { fs.unlinkSync(file); } catch (e) {}
  }
}

// activate / mode-tracker 写入的实时档位。读不到标记 = ponytail 未启用。
function readMode() {
  try {
    return fs.readFileSync(projectStatePath || statePath, 'utf8').trim() || null;
  } catch (e) {
    return null;
  }
}

// 同步写：每个 hook 写完就 process.exit()，而 macOS 上管道写是异步的，
// 异步写会随进程退出一起丢掉（上游 #1043）。
function writeOut(text) {
  fs.writeSync(1, text);
}

// 上游原生 Claude 分支是「SessionStart / UserPromptSubmit 走裸文本、SubagentStart 走 JSON」，
// 用的人得记住哪个事件走哪条路。MiniMax 的 SessionStart / UserPromptSubmit / SubagentStart
// 三个事件都支持 hookSpecificOutput.additionalContext，统一成 JSON 就不用记。
// context 为空时输出 {}。
// mode 只在信封里没有它的位置，保留参数是为了和调用方的签名一致。
function writeHookOutput(event, mode, context = '') {
  const output = {};
  if (context) {
    output.hookSpecificOutput = {
      hookEventName: event,
      additionalContext: context,
    };
  }
  writeOut(JSON.stringify(output));
}

module.exports = {
  clearMode,
  readMode,
  setMode,
  writeHookOutput,
};
