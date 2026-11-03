# CLI Wrapper Patterns

## Click Python 最小模板

```python
#!/usr/bin/env python3
"""cli-toolname — 工具简短描述"""
import sys
import json
import click

@click.group()
@click.pass_context
def cli(ctx):
    """工具描述（出现在 --help）"""
    ctx.ensure_object(dict)

# === 子命令示例：info ===
@cli.command()
@click.argument("input", type=click.Path(exists=True))
@click.option("--json", "as_json", is_flag=True, help="JSON 输出")
@click.pass_context
def info(ctx, input, as_json):
    """读取文件信息"""
    try:
        size = os.path.getsize(input)
        result = {"path": input, "size": size, "exists": True}
        output = json.dumps(result) if as_json else f"Size: {size}"
        click.echo(output)
    except Exception as e:
        error = {"error": str(e), "code": 1}
        click.echo(json.dumps(error) if as_json else f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli()
```

## Click JSON 输出模板

```python
#!/usr/bin/env python3
"""cli-{tool} — 工具描述，Agent-native CLI"""
import sys
import json
import os
import click

def json_output(data, pretty=False):
    """统一 JSON 序列化"""
    kwargs = {"indent": 2} if pretty else {}
    click.echo(json.dumps(data, **kwargs))

def error_output(msg, code=1):
    click.echo(json.dumps({"error": msg, "code": code}))
    sys.exit(code)

# === 子命令：convert ===
@cli.command("image/convert")
@click.argument("input", type=click.Path(exists=True))
@click.option("--format", "-f", help="目标格式")
@click.option("--output", "-o", type=click.Path(), help="输出路径")
@click.option("--json", is_flag=True, help="JSON 输出")
def convert(input, format, output, json):
    """格式转换"""
    if not format:
        error_output("需要 --format 参数", 1) if json else click.echo("Error: 需要 --format")
        return
    # ... 实际转换逻辑 ...
    result = {"input": input, "output": output, "format": format, "success": True}
    json_output(result) if json else click.echo(f"Converted {input} -> {output}")

# === 子命令：batch ===
@cli.command("batch/process")
@click.argument("inputs", nargs=-1, type=click.Path(exists=True))
@click.option("--pattern", "-p", help="glob 模式")
@click.option("--json", is_flag=True)
def batch(inputs, pattern, json):
    """批量处理"""
    results = []
    for f in inputs:
        results.append({"file": f, "status": "done"})
    json_output({"total": len(results), "results": results})
```

## Shell 包装模板

```bash
#!/usr/bin/env bash
# cli-toolname — 工具描述
set -euo pipefail

JSON_OUTPUT=false
POSITIONAL=()

while [[ $# -gt 0 ]]; do
    case $1 in
        --json) JSON_OUTPUT=true; shift ;;
        --help|-h) cli-toolname --help; exit 0 ;;
        *) POSITIONAL+=("$1"); shift ;;
    esac
done
set -- "${POSITIONAL[@]}"

# 主逻辑
cmd="${1:-}"
case "$cmd" in
    info)
        result=$(tool-info "${2:-}" 2>/dev/null || echo "{\"error\": \"failed\"}")
        if $JSON_OUTPUT; then echo "$result"; else echo "$result" | jq .; fi
        ;;
    *) echo "{\"error\": \"unknown command: $cmd\"}"; exit 1 ;;
esac
```

## 错误处理规范

```
成功：exit 0，JSON 包含 "success": true 或无 error 字段
一般错误：exit 1，JSON 包含 "error": "描述", "code": 1
找不到工具：exit 127，JSON 包含 "error": "tool not found"
参数错误：exit 2，JSON 包含 "error": "invalid argument"
```

## JSON 输出规范

```json
// 成功
{"success": true, "data": {...}, "meta": {"version": "1.0"}}

// 错误
{"error": "描述文字", "code": 1, "details": {}}

// 批量
{"total": 10, "success": 8, "failed": 2, "results": [...]}
```

## 自我发现机制

Agent 可通过以下方式了解 CLI：

1. `--help` 直接读取用法
2. 无参数调用显示简要帮助
3. 子命令 `--help` 显示详细帮助
4. `--version` 显示版本（如果适用）

```bash
cli-tool          # 显示 usage
cli-tool --help   # 显示完整帮助
cli-tool cmd --help  # 显示子命令帮助
```

## 工具检测模板

```python
def ensure_tool(name: str, install_hint: str = "") -> str:
    """检测工具是否存在，不存在则报错"""
    path = shutil.which(name)
    if not path:
        msg = f"工具 '{name}' 未找到。"
        if install_hint:
            msg += f" 安装: {install_hint}"
        raise SystemExit(f"Error: {msg}\n" + json.dumps({"error": msg, "code": 127}))
    return path
```
