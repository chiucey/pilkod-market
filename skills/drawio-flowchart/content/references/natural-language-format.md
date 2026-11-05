# Natural Language Input

The fastest workflow is now:

1. Write a short natural-language outline.
2. Run `text_to_spec.py` if you want to inspect the intermediate spec.
3. Run `text_to_drawio.py` if you want the final `.drawio` file directly.

## Recommended Format

Use compact line-oriented natural language. It is more forgiving than JSON, but still structured enough to parse well.

```text
标题：请假审批流程
泳道：员工 | 主管 | 人事 | 系统

员工: 提交请假申请
主管: 审批
通过 -> 人事: 登记备案 -> 系统: 发送审批通过通知 -> 结束
驳回 -> 系统: 发送驳回通知 -> 结束
```

## What the Parser Understands Well

- `标题：...`
- `泳道：A | B | C`
- `角色: 动作`
- Sequential chains such as `A: 提交 -> B: 审批 -> C: 归档`
- Branches such as `通过 -> 财务: 付款` and `驳回 -> 申请人: 修改`
- Common approval words like `审批`, `审核`, `判断`, `确认`, which are upgraded to BPMN gateway nodes when they branch

## Best-Effort Free Prose

Simple prose like this often works:

```text
退款审批流程。用户提交申请，客服审批，通过则财务退款，驳回则系统发送通知。
```

But the parser is more reliable when each branch is written on its own line.

## Commands

Generate only the JSON spec:

```bash
python3 /Users/zhuhan/Desktop/朱朱/skills/drawio-flowchart/scripts/text_to_spec.py \
  --input /absolute/path/to/process.txt \
  --output /absolute/path/to/process.spec.json
```

Generate the `.drawio` file directly:

```bash
python3 /Users/zhuhan/Desktop/朱朱/skills/drawio-flowchart/scripts/text_to_drawio.py \
  --input /absolute/path/to/process.txt \
  --output /absolute/path/to/process.drawio \
  --spec-output /absolute/path/to/process.spec.json
```
