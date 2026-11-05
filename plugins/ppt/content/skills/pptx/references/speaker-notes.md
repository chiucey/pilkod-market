# 演讲者备注

演讲者备注通过 `python-pptx` 直接读写 PPTX 的 `notesSlide` OOXML，不依赖 OfficeCLI 或
其他 Office 可执行程序。

## Sidecar 契约

在最终页序确定后创建 `mavis.ppt_notes.v1`：

```json
{
  "schema": "mavis.ppt_notes.v1",
  "slides": [
    {
      "slideNumber": 1,
      "text": "先说明本页结论，再解释关键证据。"
    },
    {
      "slideNumber": 3,
      "text": "总结影响，并给出下一步行动。"
    }
  ]
}
```

- `slideNumber` 使用最终 PPTX 中从 1 开始的页码，必须唯一且在有效范围内。
- `text` 必须是字符串。
- 未列出的页面保留已有备注。
- `text` 为空字符串时，清空该页备注。
- 备注只写演讲者可直接讲述的内容，不写制作指令。

## 写入与验证

```bash
uv run --with python-pptx <skill_dir>/scripts/pptx_notes_apply.py \
  --input slides/output/deck-static.pptx \
  --notes slides/output/deck.mavis-ppt-notes.json \
  --out slides/output/deck.pptx \
  --report slides/output/deck.notes-report.json
```

写入器必须：

1. 保持输入 PPTX 不变，并要求输出路径与输入路径不同。
2. 先写临时文件，再原子替换输出。
3. 重新打开输出文件，逐页精确回读备注文本。
4. 只有 `writtenSlides == matchedSlides == requestedSlides` 时才报告成功。

失败报告会包含稳定的 `errorCode`，且不会产生输出 PPTX。
