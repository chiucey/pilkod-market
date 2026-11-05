// ponytail — 共享配置解析
//
// 默认档位（default mode）的解析顺序：
//   1. 环境变量 PONYTAIL_DEFAULT_MODE
//   2. 配置文件 config.json 的 defaultMode 字段：
//      - ${PLUGIN_DATA}/config.json           （MiniMax 注入的可写数据目录，优先）
//      - $XDG_CONFIG_HOME/ponytail/config.json（任意平台，设置了就用）
//      - ~/.config/ponytail/config.json       （macOS / Linux 兜底）
//      - %APPDATA%\ponytail\config.json       （Windows 兜底）
//   3. 'full'
//
// 本包只有 MiniMax 一条路径：不带任何「如果是 X 宿主则…」的分支。

const fs = require('fs');
const path = require('path');
const os = require('os');

const DEFAULT_MODE = 'full';
const VALID_MODES = ['off', 'lite', 'full', 'ultra', 'review'];
const RUNTIME_MODES = ['off', 'lite', 'full', 'ultra'];

function normalizeMode(mode) {
  if (typeof mode !== 'string') return null;
  const normalized = mode.trim().toLowerCase();
  return RUNTIME_MODES.includes(normalized) ? normalized : null;
}

function normalizeConfigMode(mode) {
  if (typeof mode !== 'string') return null;
  const normalized = mode.trim().toLowerCase();
  return VALID_MODES.includes(normalized) ? normalized : null;
}

function normalizePersistedMode(mode) {
  return normalizeMode(mode) || normalizeConfigMode(mode);
}

// 「stop ponytail」/「normal mode」以及中文同义句会关掉 ponytail，但只作为
// 独立的一条命令。句子中间出现这些词就把任务中途关掉，会误伤普通请求
// （比如「add a normal mode toggle」）—— 所以要求整条消息就是这条命令，
// 忽略大小写和结尾标点。
function isDeactivationCommand(text) {
  // ponytail: 中文停用词也带结尾标点，所以标点集合里同时收半角和全角符号。
  const t = String(text || '').trim().toLowerCase().replace(/[.!?。！？；，、\s]+$/, '');
  return t === 'stop ponytail' || t === 'normal mode' ||
    t === '关掉 ponytail' || t === '关闭 ponytail' ||
    t === '关掉 ponytail 模式' || t === '关闭 ponytail 模式' ||
    t === '恢复正常模式' || t === '恢复普通模式' || t === '正常模式';
}

function getConfigDir() {
  // ponytail: MiniMax 注入 PLUGIN_DATA 指向插件自己的可写数据目录，
  // 官方规范要求需要持久化的状态写到 ${PLUGIN_DATA}，所以优先用它。
  if (process.env.PLUGIN_DATA) {
    return process.env.PLUGIN_DATA;
  }
  if (process.env.XDG_CONFIG_HOME) {
    return path.join(process.env.XDG_CONFIG_HOME, 'ponytail');
  }
  if (process.platform === 'win32') {
    return path.join(
      process.env.APPDATA || path.join(os.homedir(), 'AppData', 'Roaming'),
      'ponytail'
    );
  }
  return path.join(os.homedir(), '.config', 'ponytail');
}

function getConfigPath() {
  return path.join(getConfigDir(), 'config.json');
}

function getDefaultMode() {
  // 1. 环境变量（最高优先级）
  // ponytail: 默认档位只能是运行时档位（off/lite/full/ultra）；review 是一次性
  // 会话模式，永远不能作为默认值（#377）。在这里做归一化，带空白或大小写混写
  // 的值也能正确解析。
  const envMode = normalizeMode(process.env.PONYTAIL_DEFAULT_MODE);
  if (envMode) {
    return envMode;
  }

  // 2. 配置文件
  try {
    const configPath = getConfigPath();
    // 剥掉 UTF-8 BOM（Windows 保存的文件常见），否则 JSON.parse 会失败
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8').replace(/^\uFEFF/, ''));
    const configMode = normalizeMode(config.defaultMode);
    if (configMode) {
      return configMode;
    }
  } catch (e) {
    // 配置文件不存在或格式非法 —— 继续往下走
  }

  // 3. 默认值
  return DEFAULT_MODE;
}

function writeDefaultMode(mode) {
  // ponytail: 只有运行时档位能当默认值；review 仅限当前会话（#377）。
  const normalized = normalizeMode(mode);
  if (!normalized) return null;

  const configPath = getConfigPath();
  fs.mkdirSync(path.dirname(configPath), { recursive: true });
  let config = {};
  try {
    config = JSON.parse(fs.readFileSync(configPath, 'utf8').replace(/^\uFEFF/, ''));
    if (!config || typeof config !== 'object' || Array.isArray(config)) config = {};
  } catch (_) {}
  config.defaultMode = normalized;
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf8');
  return normalized;
}

module.exports = {
  DEFAULT_MODE,
  VALID_MODES,
  RUNTIME_MODES,
  getDefaultMode,
  getConfigDir,
  getConfigPath,
  isDeactivationCommand,
  normalizeMode,
  normalizeConfigMode,
  normalizePersistedMode,
  writeDefaultMode,
};
