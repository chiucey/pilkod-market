// ponytail — MiniMax Code SubagentStart hook
//
// SessionStart 的上下文只给父线程，不会传到子代理；少了这一步，
// 每个被派发的子代理都不知道 ponytail 的规则（上游 #252）。
// 档位没开（读不到状态文件）或已关掉 → 不注入任何东西。
//
// 同步执行，不读 stdin：上游那套 PONYTAIL_SUBAGENT_MATCHER 分支在本包里读不到
// （环境变量白名单里没有），只会是死代码，删掉也顺带避开上游 #443
// （Windows 管道吞 JSON 导致子代理 spawn 卡死）。

const { getPonytailInstructions } = require('./ponytail-instructions');
const { readMode, writeHookOutput } = require('./ponytail-runtime');

const mode = readMode();

// 没有状态标记或已关闭 → ponytail 没启用，不注入。
if (!mode || mode === 'off') {
  process.exit(0);
}

try {
  writeHookOutput('SubagentStart', mode, getPonytailInstructions(mode));
} catch (e) {
  // 静默兜底：进程退出时 stdout 出错不该变成 hook 失败
}

process.exit(0);
