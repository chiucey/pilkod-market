#!/usr/bin/env bash
#
# zshlpay Spring Cloud 项目生成脚本
# 用法: ./generate.sh [OPTIONS]
#
# 选项:
#   -o, --output DIR      输出目录 (默认: 当前目录)
#   -n, --name NAME       项目名称 (默认: zshlpay-cloud)
#   -m, --mq TYPES        MQ类型列表，用逗号分隔 (默认: kafka)
#                       可选: kafka,rabbitmq,rocketmq,activemq
#   -d, --db TYPE         数据库类型 (默认: mysql)
#                       可选: mysql,dm,kingbase,gaussdb,oceanbase,shentong,postgresql
#   -h, --help            显示帮助信息
#
# 示例:
#   ./generate.sh                              # 生成默认项目
#   ./generate.sh -m kafka,rabbitmq          # 支持Kafka和RabbitMQ
#   ./generate.sh -d dm                       # 使用达梦数据库
#   ./generate.sh -o /tmp -n myproject       # 自定义输出和名称

set -e

# 默认配置
OUTPUT_DIR="."
PROJECT_NAME="zshlpay-cloud"
MQ_TYPES="kafka"
DB_TYPE="mysql"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    head -40 "$0" | tail -30
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -n|--name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        -m|--mq)
            MQ_TYPES="$2"
            shift 2
            ;;
        -d|--db)
            DB_TYPE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            show_help
            exit 1
            ;;
    esac
done

# 转换MQ类型（逗号分隔转换为空格分隔）
MQ_LIST=$(echo "$MQ_TYPES" | tr ',' ' ')

log_info "开始生成项目..."
log_info "输出目录: $OUTPUT_DIR"
log_info "项目名称: $PROJECT_NAME"
log_info "MQ类型: $MQ_TYPES"
log_info "数据库类型: $DB_TYPE"

# 检查Python环境
if command -v python3 &> /dev/null; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    python3 "$SCRIPT_DIR/generate_project.py" \
        --output "$OUTPUT_DIR" \
        --name "$PROJECT_NAME" \
        --mq $MQ_LIST \
        --db "$DB_TYPE"
elif command -v python &> /dev/null; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    python "$SCRIPT_DIR/generate_project.py" \
        --output "$OUTPUT_DIR" \
        --name "$PROJECT_NAME" \
        --mq $MQ_LIST \
        --db "$DB_TYPE"
else
    log_error "未找到Python环境，请安装Python 3.8+"
    exit 1
fi

log_success "项目生成完成!"
