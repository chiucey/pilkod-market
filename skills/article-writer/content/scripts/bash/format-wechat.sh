#!/usr/bin/env bash
#
# format-wechat.sh
# 将 Markdown 文章格式化为微信公众号富文本 HTML
#
# 使用方法:
#   bash format-wechat.sh <input-md-file> [output-html-file] [--base64]
#
# 选项:
#   --base64  将在线图片转换为 base64 编码(方便一键复制)
#
# 示例:
#   bash format-wechat.sh draft.md wechat.html
#   bash format-wechat.sh draft.md wechat.html --base64
#

set -e  # 遇到错误立即退出

# 解析参数
INPUT_FILE=""
OUTPUT_FILE="wechat.html"
CONVERT_TO_BASE64="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base64)
      CONVERT_TO_BASE64="true"
      shift
      ;;
    --help)
      echo "使用方法: bash format-wechat.sh <input-md-file> [output-html-file] [--base64]"
      echo ""
      echo "选项:"
      echo "  --base64  将在线图片转换为 base64 编码(方便一键复制)"
      echo ""
      echo "示例:"
      echo "  bash format-wechat.sh draft.md wechat.html"
      echo "  bash format-wechat.sh draft.md wechat.html --base64"
      exit 0
      ;;
    *)
      if [ -z "$INPUT_FILE" ]; then
        INPUT_FILE="$1"
      elif [ "$OUTPUT_FILE" = "wechat.html" ]; then
        OUTPUT_FILE="$1"
      fi
      shift
      ;;
  esac
done

# 检查输入文件参数
if [ -z "$INPUT_FILE" ]; then
  echo "错误: 缺少输入文件参数"
  echo "使用方法: bash format-wechat.sh <input-md-file> [output-html-file] [--base64]"
  exit 1
fi

# 检查输入文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
  echo "错误: 输入文件不存在: $INPUT_FILE"
  exit 1
fi

# 获取项目根目录(查找 .content 目录)
PROJECT_ROOT=""
CURRENT_DIR="$(pwd)"

while [ "$CURRENT_DIR" != "/" ]; do
  if [ -d "$CURRENT_DIR/.content" ]; then
    PROJECT_ROOT="$CURRENT_DIR"
    break
  fi
  CURRENT_DIR="$(dirname "$CURRENT_DIR")"
done

if [ -z "$PROJECT_ROOT" ]; then
  echo "错误: 无法找到项目根目录(.content目录)"
  exit 1
fi

CONFIG_FILE="$PROJECT_ROOT/.content/config.json"

# 检查配置文件
if [ ! -f "$CONFIG_FILE" ]; then
  echo "警告: 配置文件不存在,使用默认配置"
  THEME="default"
  PRIMARY_COLOR="#3f51b5"
  FONT_SIZE="16px"
  FONT_FAMILY="-apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif"
  IS_USE_INDENT="false"
  IS_USE_JUSTIFY="false"
  IS_SHOW_LINE_NUMBER="false"
  CITE_STATUS="true"
else
  # 读取配置(使用 node 解析 JSON)
  THEME=$(node -p "try { const c = require('$CONFIG_FILE'); c.formatting?.theme || 'default' } catch(e) { 'default' }" 2>/dev/null || echo "default")
  PRIMARY_COLOR=$(node -p "try { const c = require('$CONFIG_FILE'); c.formatting?.primaryColor || '#3f51b5' } catch(e) { '#3f51b5' }" 2>/dev/null || echo "#3f51b5")
  FONT_SIZE=$(node -p "try { const c = require('$CONFIG_FILE'); c.formatting?.fontSize || '16px' } catch(e) { '16px' }" 2>/dev/null || echo "16px")
  FONT_FAMILY=$(node -p "try { const c = require('$CONFIG_FILE'); c.formatting?.fontFamily || '-apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif' } catch(e) { '-apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif' }" 2>/dev/null || echo "-apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif")
  IS_USE_INDENT=$(node -p "try { const c = require('$CONFIG_FILE'); String(c.formatting?.isUseIndent || false) } catch(e) { 'false' }" 2>/dev/null || echo "false")
  IS_USE_JUSTIFY=$(node -p "try { const c = require('$CONFIG_FILE'); String(c.formatting?.isUseJustify || false) } catch(e) { 'false' }" 2>/dev/null || echo "false")
  IS_SHOW_LINE_NUMBER=$(node -p "try { const c = require('$CONFIG_FILE'); String(c.formatting?.isShowLineNumber || false) } catch(e) { 'false' }" 2>/dev/null || echo "false")
  CITE_STATUS=$(node -p "try { const c = require('$CONFIG_FILE'); String(c.formatting?.citeStatus !== false) } catch(e) { 'true' }" 2>/dev/null || echo "true")
fi

# 获取脚本的真实路径（用于查找开发环境的格式化器）
SCRIPT_PATH="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
DEV_PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 获取全局 node_modules 路径
GLOBAL_NODE_MODULES=$(npm root -g 2>/dev/null || echo "")

# 使用 Node.js 调用格式化器
node -e "
const fs = require('fs');
const path = require('path');

let formatMarkdown;
let loadedFrom = '';

// 尝试多种方式加载格式化器
const loadStrategies = [
  // 策略1: 从全局 node_modules 加载（最常用）
  () => {
    const globalNodeModules = '$GLOBAL_NODE_MODULES';
    if (globalNodeModules && fs.existsSync(globalNodeModules)) {
      const formatterPath = path.join(globalNodeModules, 'article-writer-cn', 'dist', 'formatters', 'wechat-formatter.js');
      if (fs.existsSync(formatterPath)) {
        const formatter = require(formatterPath);
        return formatter.exportWechatHtml;
      }
    }
    throw new Error('Formatter not found in global node_modules');
  },
  // 策略2: 从用户项目的 node_modules 加载
  () => {
    const formatterPath = path.join('$PROJECT_ROOT', 'node_modules', 'article-writer-cn', 'dist', 'formatters', 'wechat-formatter.js');
    if (fs.existsSync(formatterPath)) {
      const formatter = require(formatterPath);
      return formatter.exportWechatHtml;
    }
    throw new Error('Formatter not found in local node_modules');
  },
  // 策略3: 从开发环境加载（article-writer 项目本身）
  () => {
    const formatterPath = path.join('$DEV_PROJECT_ROOT', 'dist', 'formatters', 'wechat-formatter.js');
    if (fs.existsSync(formatterPath)) {
      const formatter = require(formatterPath);
      return formatter.exportWechatHtml;
    }
    throw new Error('Formatter not found in development path');
  },
  // 策略4: 通过 require.resolve 查找（兜底）
  () => {
    const pkgPath = require.resolve('article-writer-cn');
    const formatterPath = path.join(path.dirname(pkgPath), 'formatters', 'wechat-formatter.js');
    const formatter = require(formatterPath);
    return formatter.exportWechatHtml;
  }
];

for (let i = 0; i < loadStrategies.length; i++) {
  try {
    formatMarkdown = loadStrategies[i]();
    loadedFrom = 'strategy-' + (i + 1);
    break;
  } catch (err) {
    // 继续尝试下一个策略
    if (i === loadStrategies.length - 1) {
      // 所有策略都失败了
      console.error('错误: 无法加载格式化器');
      console.error('');
      console.error('可能的原因:');
      console.error('  1. article-writer-cn 未安装');
      console.error('  2. 版本不兼容');
      console.error('');
      console.error('解决方案:');
      console.error('  运行: npm install -g article-writer-cn@latest');
      console.error('  或者: npm install article-writer-cn@latest');
      console.error('');
      console.error('详细错误:', err.message);
      process.exit(1);
    }
  }
}

// 读取 Markdown
const markdown = fs.readFileSync('$INPUT_FILE', 'utf-8');

// 获取文章标题(从第一个一级标题提取)
const titleMatch = markdown.match(/^#\s+(.+)$/m);
const title = titleMatch ? titleMatch[1] : '微信文章';

// 格式化选项
const options = {
  theme: '$THEME',
  primaryColor: '$PRIMARY_COLOR',
  fontSize: '$FONT_SIZE',
  fontFamily: '$FONT_FAMILY',
  isUseIndent: '$IS_USE_INDENT' === 'true',
  isUseJustify: '$IS_USE_JUSTIFY' === 'true',
  isShowLineNumber: '$IS_SHOW_LINE_NUMBER' === 'true',
  citeStatus: '$CITE_STATUS' === 'true',
  convertOnlineImagesToBase64: '$CONVERT_TO_BASE64' === 'true'
};

// 格式化并导出
formatMarkdown(markdown, title, options).then(html => {
  fs.writeFileSync('$OUTPUT_FILE', html, 'utf-8');
  console.log('✅ 微信格式化成功!');
  console.log('📄 输出文件:', '$OUTPUT_FILE');
  console.log('🎨 使用主题:', options.theme);
  console.log('🎨 主题色:', options.primaryColor);
}).catch(err => {
  console.error('错误: 格式化失败');
  console.error(err.message);
  process.exit(1);
});
"

# 等待文件写入完成
sleep 0.5

# 检查输出文件是否生成
if [ -f "$OUTPUT_FILE" ]; then
  echo ""
  echo "🌐 正在打开浏览器..."

  # 跨平台打开浏览器
  OPENED=false
  if command -v open >/dev/null 2>&1; then
    # macOS
    open "$OUTPUT_FILE" && OPENED=true
  elif command -v xdg-open >/dev/null 2>&1; then
    # Linux
    xdg-open "$OUTPUT_FILE" 2>/dev/null && OPENED=true
  elif command -v start >/dev/null 2>&1; then
    # Windows (Git Bash)
    start "$OUTPUT_FILE" && OPENED=true
  fi

  if [ "$OPENED" = true ]; then
    echo ""
    echo "💡 使用说明:"
    echo "   1. 点击页面上的'一键复制到微信'按钮"
    echo "   2. 打开微信公众号后台编辑器"
    echo "   3. 按 Ctrl+V (Mac: Cmd+V) 粘贴"
    echo "   4. 检查格式,完成发布!"
    echo ""
    echo "⌨️  快捷键: Ctrl/Cmd + Shift + C"
  else
    echo "⚠️  无法自动打开浏览器,请手动打开: $OUTPUT_FILE"
    echo ""
    echo "💡 下一步:"
    echo "   1. 在浏览器中打开 $OUTPUT_FILE"
    echo "   2. 点击'一键复制到微信'按钮"
    echo "   3. 粘贴到微信公众号编辑器"
  fi
fi

exit 0
