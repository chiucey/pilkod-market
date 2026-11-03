# Token 消耗追踪器

实时监控 AI 资源消耗。

## 安装

```bash
cp -r /workspace/skills/token-tracker ~/.openclaw/skills/
```

## 使用

直接询问：
- "现在用了多少 token?"
- "生成消耗报告"
- "分析 token 消耗"

## 工具

- `scripts/token_tracker.py` - 追踪脚本

## 示例

```bash
# 查看状态
python3 scripts/token_tracker.py

# 生成报告
python3 scripts/token_tracker.py report

# 分析使用
python3 scripts/token_tracker.py analyze
```
