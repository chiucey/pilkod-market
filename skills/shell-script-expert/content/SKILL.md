---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100d418330477e84a679fb52e81449479cb06f0f0ff065af14f94a26d92865c4c77022100e971056d2562aa8e57749557a3533b83846850a41ede2d42ac092848dc943b11
    ReservedCode2: 3045022001554d13618e476e6aa7174ed4065481bd8b89a865fa384e1676016ce17a11be022100eae8b5d106e436510cb6101ef90c294449a2e1102b2fd190d193a6038ba612ca
description: Expert skill for writing professional Shell scripts with strict coding standards. Use when users ask to write Shell scripts, create Shell tools, write automation scripts, create command-line tools, or generate bash/zsh scripts. Includes standard usage functions, error handling, logging output, and complete documentation.
name: shell-script-expert
---

# Shell Script Expert

专业的Shell脚本编写技能，生成符合行业规范的Shell脚本，包含完整的usage文档和错误处理。

## 工作流程

### 1. 需求分析

收集脚本需求信息：
- **脚本目的**：脚本要完成什么功能
- **输入参数**：需要哪些命令行参数
- **输出格式**：结果输出到哪里（文件/stdout/stderr）
- **错误处理**：需要哪些错误检查
- **目标Shell**：bash / zsh / POSIX sh

### 2. 生成脚本

每个生成的脚本必须包含以下标准结构：

#### 2.1 标准头部注释

```bash
#!/usr/bin/env bash
#
# Script Name: [script-name].sh
# Description: [简要描述脚本功能]
# Author: [作者名]
# Created: [日期]
# Last Modified: [日期]
# Version: [版本号]
#
# Usage: ./[script-name].sh [OPTIONS] ARGUMENTS
#
# Options:
#   -h, --help        显示帮助信息
#   -v, --verbose    启用详细输出
#   -f, --force       强制执行
#   ...
#
# Examples:
#   ./[script-name].sh -v input.txt
#   ./[script-name].sh --force /path/to/dir
#
# Exit Codes:
#   0   成功
#   1   一般错误
#   2   无效参数
#   3   文件不存在
#   4   权限不足
#
```

#### 2.2 Usage函数（必需）

```bash
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] ARGUMENTS

Description: 详细描述脚本的功能和用途

OPTIONS:
    -h, --help              显示帮助信息并退出
    -v, --verbose           启用详细输出模式
    -f, --force             跳过确认提示，强制执行
    -o, --output FILE       指定输出文件（必需）
    -c, --config FILE       指定配置文件
    -n, --dry-run           仅显示将要执行的操作，不实际执行
    -q, --quiet             静默模式，抑制非错误信息

ARGUMENTS:
    INPUT_FILE              输入文件（必需）
    TARGET_DIR              目标目录（可选）

EXAMPLES:
    # 基本用法
    $(basename "$0") -o result.txt input.txt

    # 详细模式
    $(basename "$0") -v -o output.log data.csv

    # 强制执行
    $(basename "$0") -f -o results.txt input.txt

    # 预览模式
    $(basename "$0") -n -o test.txt sample.dat

NOTES:
    - INPUT_FILE必须存在且可读
    - 使用--force会覆盖已存在的输出文件

Report bugs to: [email@example.com]
EOF
}
```

#### 2.3 核心功能模块

```bash
# ========== 常量定义 ==========
readonly SCRIPT_NAME="$(basename "$0")"
readonly SCRIPT_VERSION="1.0.0"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ========== 日志函数 ==========
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# ========== 工具函数 ==========
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

is_root() {
    [[ $EUID -eq 0 ]]
}

validate_file() {
    if [[ ! -e "$1" ]]; then
        log_error "文件不存在: $1"
        exit 3
    fi
    if [[ ! -r "$1" ]]; then
        log_error "文件不可读: $1"
        exit 4
    fi
}

confirm() {
    local prompt="${1:-确定要继续吗?}"
    [[ "$FORCE" == "true" ]] && return 0
    read -rp "$prompt [y/N]: " yn
    [[ "$yn" =~ ^[Yy]$ ]]
}

# ========== 主逻辑 ==========
main() {
    # 脚本主要逻辑
}

trap 'cleanup' EXIT
main "$@"
```

### 3. 参数解析规范

```bash
# 默认值设置
VERBOSE=false
FORCE=false
DRY_RUN=false
QUIET=false
OUTPUT_FILE=""
INPUT_FILE=""

# 参数解析
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -*)
            log_error "未知选项: $1"
            echo "使用 '$(basename "$0") --help' 查看帮助。" >&2
            exit 2
            ;;
        *)
            INPUT_FILE="$1"
            shift
            ;;
    esac
done

# 必需参数验证
if [[ -z "$INPUT_FILE" ]]; then
    log_error "缺少必需参数: INPUT_FILE"
    echo "使用 '$(basename "$0") --help' 查看帮助。" >&2
    exit 2
fi
```

## 输出要求

### 脚本必须包含

1. **完整的头部注释**：描述、功能、用法示例、退出码
2. **usage()函数**：详细的使用说明和示例
3. **日志函数**：log_info、log_success、log_warning、log_error
4. **错误处理**：set -eE、trap错误捕获、cleanup函数
5. **参数验证**：必需参数检查、选项验证
6. **可执行权限提示**：说明如何添加执行权限

### 示例脚本输出格式

生成的每个脚本应该类似：

```bash
#!/usr/bin/env bash
#
# Script Name: example.sh
# Description: 示例脚本演示标准结构
# ...
#

set -eE -o pipefail
trap 'error_handler $? $LINENO $BASH_LINENO' ERR

# ... [完整脚本内容]
```

## 质量标准

- 符合Shell脚本编写规范
- 包含完整的usage文档
- 有清晰的使用示例
- 适当的错误处理
- 规范的日志输出
- 正确的退出码
- POSIX兼容的语法（除非指定特定Shell）
