// ponytail — 规则集构建（MiniMax Code 插件版）
//
// 规则正文优先读本包的 skills/ponytail/SKILL.md；读不到时用本文件里的中文兜底，
// 保证任何情况下 agent 都能拿到一份自洽可读的规则集。

const fs = require('fs');
const path = require('path');
const { DEFAULT_MODE, normalizeMode, normalizePersistedMode } = require('./ponytail-config');

const INDEPENDENT_MODES = new Set(['review']);
const SKILL_PATH = path.join(__dirname, '..', 'skills', 'ponytail', 'SKILL.md');

function filterSkillBodyForMode(body, mode) {
  const effectiveMode = normalizeMode(mode) || DEFAULT_MODE;
  const withoutFrontmatter = String(body || '').replace(/^---[\s\S]*?---\s*/, '');

  // Only the intensity table rows and worked examples are mode-specific, and
  // both are keyed by a mode name (lite/full/ultra). A bullet whose label is
  // not a mode — e.g. "No unrequested abstractions: ..." — is a normal rule
  // and must be kept verbatim.
  return withoutFrontmatter
    .split(/\r?\n/)
    .filter((line) => {
      const tableLabel = line.match(/^\|\s*\*\*(.+?)\*\*\s*\|/);
      if (tableLabel) {
        const labelMode = normalizeMode(tableLabel[1].trim());
        if (labelMode) return labelMode === effectiveMode;
      }

      // Require a quoted value: every worked example is `- lite: "..."`. Without
      // this, an ordinary rule bullet that happens to start with a mode word
      // (e.g. "- Full: ...") is silently dropped in every other mode — it looks
      // like a worked example but is really prose meant to survive verbatim.
      const exampleLabel = line.match(/^-\s*([^:]+):\s*"/);
      if (exampleLabel) {
        const labelMode = normalizeMode(exampleLabel[1].trim());
        if (labelMode) return labelMode === effectiveMode;
      }

      return true;
    })
    .join('\n');
}

// 中文兜底正文：与上游英文兜底同结构（同样的两节标题、6 步必要性阶梯、
// 同样那几条 bullet、同样最后的「永不砍」清单），逐段译成中文。
const FALLBACK_BODY = `你是一个懒得写代码的资深工程师。最好的代码是从没写过的代码。你用最少的**新**代码把问题完整解决。回复结尾用一两行说明：跳过了什么或没检查什么，以及用户必须知道的风险。

## 动手之前

读任务本身，以及它会碰到的代码。列出这次改动必须触达的所有位置：调用方、测试、fixtures、配置、导出。检查改动可能对用户造成什么破坏：会销毁或暴露的数据、会失效的调用方。**这就是范围。多余的功能不是。**

## 最小且完整的改动

按顺序，取第一个能完整成立的选项：

1. **这东西需要存在吗？** 砍掉没人要的功能、选项和扩展性，并用一行说明砍了什么。含糊的需求（"帮我做个 X"）只做能完成核心工作的最小版本。
2. **代码库里已经有了吗？** 已有 helper、组件、服务或既有模式，就按周围代码的用法用它。
3. **标准库或平台原生能力能做吗？** 就用它——除非项目有自己的实现。自家组件优于原生控件。
4. **已经装了的依赖能做吗？** 就用它。**绝不为几行代码新增依赖。**
5. **能写成读者一眼看懂的一行吗？** 那就一行。
6. **否则**：写能跑通的最小代码。

- **对方案偷懒，对改动本身不偷懒**：任务需要触及的每一部分都要做完，包括被你的改动弄坏的调用方、测试和 fixtures。
- 不要抽象层、包装函数、类型转换、可选参数、配置项、样板代码或"以后可能用得上"的代码。保持平台给你的数据形态。**删除优于新增。** 沿用代码库已有的结构：它的分层、接口和约定。
- 最短的 diff 获胜——前提是你已经知道它必须触及什么。**需要解码的一行不叫短。**
- 只注释代码表达不了的"为什么"，一行说清。
- **修 bug**：动手前先 grep 所有调用你要改的函数的地方，然后在共享代码里一次性修根因。
- 被移动或合并的代码，保留它原有的错误处理和校验。
- 大小相同的选项之间，取在边界情况下正确的那个。
- **没有配套检查的偷懒代码等于没写完**：新增的非平凡逻辑（分支、循环、解析器、金额或安全相关，或者整个新脚本、新应用）要留下一个小测试或基于 assert 的自检。琐碎改动不需要。
- 有已知上限的取舍，用这种格式写注释：\`shortcut: <上限>, <何时该升级>\`。

**永远不砍**：信任边界上的校验、防止数据丢失的错误处理、安全性、可访问性、真实硬件需要的标定，以及用户明确要求的一切。
`;

// 中文头：当前档位 + 怎么切档、怎么关闭。规则正文之前先放这两行。
function buildInstructions(mode, body) {
  return 'PONYTAIL 模式已启用 —— 档位：' + mode + '\n' +
    '切换档位：直接说「ponytail 切到 lite 档」「用 ultra 模式」。关闭：说「关掉 ponytail」或「恢复正常模式」。\n' +
    '\n' +
    body;
}

function getFallbackInstructions(mode) {
  // 只在 SKILL.md 读不到时用：规则与 SKILL.md 一致（上游英文兜底的中文版）。
  return buildInstructions(mode, FALLBACK_BODY);
}

function getPonytailInstructions(mode) {
  const configuredMode = normalizePersistedMode(mode) || DEFAULT_MODE;

  if (INDEPENDENT_MODES.has(configuredMode)) {
    // review 是一次性 skill，不是会话档位：行为由对应的 skill 定义。
    return 'PONYTAIL 模式已启用 —— 档位：' + configuredMode +
      '。行为由 /ponytail-' + configuredMode + ' skill 定义。';
  }

  const effectiveMode = normalizeMode(configuredMode) || DEFAULT_MODE;

  try {
    return buildInstructions(
      effectiveMode,
      filterSkillBodyForMode(fs.readFileSync(SKILL_PATH, 'utf8'), effectiveMode)
    );
  } catch (e) {
    return getFallbackInstructions(effectiveMode);
  }
}

module.exports = {
  filterSkillBodyForMode,
  getFallbackInstructions,
  getPonytailInstructions,
};
