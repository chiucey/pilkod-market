// ponytail — UserPromptSubmit hook：追踪当前生效的档位
//
// 隐私边界（官方规范明令「不要收集或上传对话内容」）：
//   prompt 只用于识别档位命令，不写入任何文件、不发送到外部，输出里也不包含用户原文。
// 除了判定「这条消息是不是切档命令」之外，prompt 不被读、不被存、不被传，
// 输出的 additionalContext 里只有我们自己的固定文案和规则集正文。
//
// 本包只有 MiniMax 一条路径：没有按宿主分叉的分支，不 spawn 子进程，不联网。

const { getDefaultMode, isDeactivationCommand, writeDefaultMode } = require('./ponytail-config');
const { clearMode, readMode, setMode, writeHookOutput } = require('./ponytail-runtime');
const { getPonytailInstructions } = require('./ponytail-instructions');

// 会话档位 lite/full/ultra；ultra 只比 full 多一层「质疑需求」，不引入新能力。
// 可持久化的默认档位比会话档位多一个 off（review 是一次性 skill，不能当默认值，上游 #377）。

let input = '';
let done = false;

// 整条 prompt 归一化：trim → 转小写 → 去掉插件限定前缀（ponytail:ponytail → ponytail）。
function normalizePrompt(text) {
  return String(text || '')
    .trim()
    .toLowerCase()
    .replace(/^[\w.-]*ponytail:/, 'ponytail');
}

// 命令短语必须出现在消息开头（对齐上游 `/ponytail` 的前缀语义）：
// 用户常在同一条消息里先切档、再接着提需求，所以命令后面允许跟别的内容。
// 但也不能子串命中 ——「给这个文件加个 ponytail lite 注释」这种普通请求不能被误切档。
//
// 中文形态要求带「档 / 模式」后缀：否则「用 full 备份」会被当成「切到 full」。
// 英文形态（ponytail lite）用 \b 收尾：lite 后面直接接中文也算完整短语。
const RE_DEFAULT = /^[@$/]*ponytail[:\s]+default[:\s]+(off|lite|full|ultra)\b/;
const RE_CHINESE = /^[@$/]*(?:ponytail[:\s]+)?(?:用|切换到|切到)[:\s]*(lite|full|ultra)[:\s]*(?:档|模式)([\s\S]*)$/;
const RE_LEVEL = /^[@$/]*ponytail[:\s]+(off|lite|full|ultra)\b/;
const RE_BARE = /^[@$/]*ponytail[.!?。！？；，、]*$/;

// 中文形态是自然语言片段，后面很容易跟一句疑问（「用 ultra 模式吗？」）。
// 用户是在提问，不是在下指令 —— 问一句就把档位静默改掉是不能接受的。
// 只拦中文形态：ponytail 前缀形态本身就是明确的指令写法，不需要猜语气。
// 「吧」不在表里 ——「用 ultra 模式吧」是发话，不是提问。
const INTERROGATIVE_START = /^\s*(吗|呢|是不是|会不会|能不能|行不行|好不好|合适|如何|怎么|[?？])/;

function isInterrogative(tail) {
  if (INTERROGATIVE_START.test(tail)) return true;
  return /[?？]\s*$/.test(tail);
}

// 判定档位命令。返回 null = 这条 prompt 不是命令（普通请求，保持静默）。
function detect(prompt) {
  const normalized = normalizePrompt(prompt);
  if (!normalized) return null;

  // 停用词：只在整条消息就是这条命令时才停用（见 ponytail-config 里的说明）——
  // 停用是破坏性的，宁可漏判也不能在普通句子里误伤。
  if (isDeactivationCommand(normalized)) return { kind: 'off' };

  let m;
  if ((m = RE_DEFAULT.exec(normalized))) return { kind: 'default', mode: m[1] };
  if ((m = RE_CHINESE.exec(normalized))) {
    if (isInterrogative(m[2])) return null;
    return { kind: 'switch', mode: m[1] };
  }
  if ((m = RE_LEVEL.exec(normalized))) {
    return m[1] === 'off' ? { kind: 'off' } : { kind: 'switch', mode: m[1] };
  }
  if (RE_BARE.test(normalized)) return { kind: 'report' };

  return null;
}

// 切档时，旧档位的规则集还留在上下文里（SessionStart 注入的那份不会被撤回），
// 所以显式说一句「以本条为准」，避免同轮两档并存。
function switchHeader(mode) {
  return 'PONYTAIL 档位已切换 —— ' + mode + '（以本条为准，忽略此前的档位说明）';
}

function apply(action) {
  if (action.kind === 'switch') {
    setMode(action.mode);
    // 关键：MiniMax 的 Skill 调用不接参数 → 切档后只能由 hook 把新档位的规则集投进本轮。
    // 上游只在 Codex/Cursor 下这么做，本包没有宿主分支，一律做。
    writeHookOutput('UserPromptSubmit', action.mode, switchHeader(action.mode) + '\n\n' + getPonytailInstructions(action.mode));
    return;
  }

  if (action.kind === 'off') {
    clearMode();
    writeHookOutput('UserPromptSubmit', 'off', 'PONYTAIL 模式已关闭');
    return;
  }

  if (action.kind === 'default') {
    writeDefaultMode(action.mode);
    writeHookOutput('UserPromptSubmit', action.mode, 'PONYTAIL 默认档位已设为 ' + action.mode + '，新会话会从这里开始。');
    return;
  }

  if (action.kind === 'report') {
    const live = readMode();
    if (live && live !== 'off') {
      // 已经开着：只报当前档位，不动状态（上游 #639）。
      writeHookOutput('UserPromptSubmit', live, 'PONYTAIL 模式已启用 —— 档位：' + live);
      return;
    }
    // 没开或已关：开启到默认档位。默认档位本身是 off 时退回 full（上游同款）。
    const def = getDefaultMode();
    const mode = def === 'off' ? 'full' : def;
    setMode(mode);
    writeHookOutput('UserPromptSubmit', mode, switchHeader(mode) + '\n\n' + getPonytailInstructions(mode));
  }
}

// 从 stdin 里取 prompt。MiniMax runtime 永远发 JSON（{"prompt":"…"}），
// 解析失败时把 stdin 原文当 prompt —— 只为让「echo 'ponytail lite' | node hooks/…」
// 这类手工验证能跑通。原文依旧只在内存里用于匹配，不落盘、不外传。
function readPrompt(raw) {
  try {
    // 剥掉某些 shell 管道会加的 UTF-8 BOM，否则 JSON.parse 会失败。
    const data = JSON.parse(raw.replace(/^\uFEFF/, ''));
    return (data && typeof data.prompt === 'string') ? data.prompt : '';
  } catch (e) {
    return raw;
  }
}

function finish() {
  if (done) return;
  done = true;
  try {
    const action = detect(readPrompt(input));
    if (action) apply(action);
  } catch (e) {
    // 静默降级：hook 出错绝不能让会话报错。
  }
}

process.stdin.on('data', chunk => { input += chunk; });
// 在 'end' 退出，而不只是 finish()：下面的兜底定时器必须保持 ref'd（见 #790），
// 这样 stdin 卡住时它才能真的被调度；而这个 ref'd 定时器在这条正常快路径上
// 又会把进程多留 1000ms，所以正常路径要在 'end' 里直接退出。
process.stdin.on('end', () => { finish(); process.exit(0); });

// 绝不让会话卡住。出错时、或短暂等待后，都处理已经收到的内容
// （数据到了但没有 EOF 也能恢复档位）然后退出。
// 兜底定时器必须保持 ref'd：Windows 上卡住的 ref'd stdin 句柄会让事件循环一直活着，
// 而 unref 掉的定时器根本轮不到调度 —— 兜底恰好在它该生效的场景里变成了死代码，
// hook 会一直挂到外部看门狗超时才被杀（上游 #790/#443）。
// 这和其它生命周期 hook「尽力而为、绝不阻塞」的约定一致。
process.stdin.on('error', () => { finish(); process.exit(0); });
setTimeout(() => { finish(); process.exit(0); }, 1000);

// ---------------------------------------------------------------------------
// 自检：PONYTAIL_SELFTEST=1 node hooks/ponytail-mode-tracker.js
//
// 命令识别是一个带正则的解析器，属于「不能只靠肉眼确认」的那类逻辑，所以自带
// 一张判定表。运行时永远注入不了 PONYTAIL_SELFTEST（它不在 hook 环境白名单里），
// 所以生产路径不会走到这里 —— 这段只在人手主动跑时执行。
//
// 用例来源：真实 MiniMax Code 会话抓下来的 stdin payload（prompt 是多行的，
// 用户常在同一条消息里先切档、再接着提需求）+ 中文口语形态 + 必须静默的普通请求。
// ---------------------------------------------------------------------------
function runSelfTest() {
  const cases = [
    // [prompt, 期望 kind, 期望 mode]
    ['ponytail 切到 ultra 档', 'switch', 'ultra'],
    ['ponytail 切到 ultra 档\n\n帮我把这段代码重构一下', 'switch', 'ultra'],
    ['用 ultra 模式', 'switch', 'ultra'],
    ['用 ultra 模式，重新设计这个 API', 'switch', 'ultra'],
    ['用 ultra 模式重新设计这个 API', 'switch', 'ultra'],
    ['用 ultra 模式吧', 'switch', 'ultra'],
    ['切到 full 档', 'switch', 'full'],
    ['ponytail lite', 'switch', 'lite'],
    ['ponytail default lite', 'default', 'lite'],
    ['ponytail default off', 'default', 'off'],
    ['ponytail', 'report', undefined],
    ['ponytail off', 'off', undefined],
    ['关掉 ponytail', 'off', undefined],
    ['恢复正常模式', 'off', undefined],
    // 疑问句是在提问，不是在下指令 —— 静默
    ['用 ultra 模式吗？', null, undefined],
    ['用 ultra 模式会不会太夸张？', null, undefined],
    ['用 ultra 模式行不行', null, undefined],
    ['用 ultra 模式吧？', null, undefined],
    ['切到 full 档合适吗？', null, undefined],
    // 普通请求不能被误切档
    ['给这个文件加个 ponytail lite 注释', null, undefined],
    ['add a normal mode toggle', null, undefined],
    ['帮我看下这段代码', null, undefined],
    ['用 full 备份', null, undefined],
    ['别用 ultra 模式', null, undefined],
    ['ponytail-review 审一下当前改动', null, undefined],
    ['我想用 ultra 模式', null, undefined],
  ];

  let failed = 0;
  for (const [prompt, kind, mode] of cases) {
    const got = detect(prompt);
    // kind 为 null = 期望「不识别」（普通请求静默）
    const ok = kind === null
      ? !got
      : (!!got && got.kind === kind && (mode === undefined || got.mode === mode));
    if (!ok) {
      failed++;
      console.error('FAIL: ' + JSON.stringify(prompt) + ' → ' + JSON.stringify(got) +
        '（期望 ' + kind + (mode ? '/' + mode : '') + '）');
    }
  }
  console.log(failed
    ? '自检失败：' + failed + ' / ' + cases.length
    : '自检通过：' + cases.length + ' / ' + cases.length);
  process.exit(failed ? 1 : 0);
}

if (process.env.PONYTAIL_SELFTEST === '1') runSelfTest();
