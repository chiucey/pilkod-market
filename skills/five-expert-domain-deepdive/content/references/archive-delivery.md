# 学习考核档案：结构与交付验证

用户说"输出 md 文件 / 把文件发给我 / docx 交付 / 简报 V1.1 发给我"时进入本阶段。

## 档案章节结构（验证过的骨架）

```markdown
# 《{主题}学习考核档案》/《{主题}简报V{x.y}》
> 整理日期：YYYY-MM-DD（绝对日期）
> 内容构成 / 用途说明（复习底稿 + 速查手册）

# 第一部分：研究报告精要
## 1. 一句话总结
## 2. 五大关键发现（按证据硬度排序，表格：#|发现|置信度|关键来源）
## 3. 隐藏关联
## 4. 实操方法（命名化清单，如「三表一测」）
## 5. 技术路线全景表（可选，视主题）
## 6. 新手十坑（速查）
## 7. 关键决策十问
## 8. 预测与反转测试

# 第二部分：考核全记录
## 第 N 题（维度）—— 题目 / 用户原话作答 / 评分 / 点评 / 内行视角
（5 题完整留痕，用户作答保留原话，用于复盘）

# 第三部分：总评与医嘱
## 成绩单（表格，含总分 X/50）
## 能力画像（稳定优点 + 一致短板）
## 医嘱（按优先级 2~3 条）
## 总评一句话

## 附：关键术语（会话中用户追问过的术语必须收录，如 波形/协议）
```

要点：全程讲过的 citation 在档案中转为"来源列/脚注"形式；用户 mid-session 的版本号（V1.1 等）保留在文件名里。

## 交付流程与验证（勿跳步）

1. **先写 md**：`write_file` 输出完整档案 md。
2. **用户说"文件格式不对"时**：不要盲改——先自查文件本身（编码/大小/内容完整性），
   再用 ask_user 确认是要 Word 版、排版坏了、打不开、还是结构要调（2026-09-10 验证：
   真实原因是"打不开/无法预览"，即要 docx/pdf）。
3. **转 docx**：

   ```bash
   pandoc 档案.md -o 档案.docx --from gfm
   ```

   **禁止加 `--toc --metadata title=...`**：实测该组合生成的 docx 在 Word/WPS 打开只剩目录视图，
   用户判为"没有其他内容"（2026-09-10 踩坑）。
   需要精细排版（中文字体、层级、封面）时改用 python-docx 编程生成（正文字体设
   `w:eastAsia` 微软雅黑，标题深色加粗）。
4. **交付前程序化验证**（两步都要做）：

   ```python
   # 验证 docx 正文完整
   from docx import Document
   d = Document('档案.docx')
   paras = [p.text for p in d.paragraphs if p.text.strip()]
   print('段落数:', len(paras), '表格数:', len(d.tables))
   ```

   ```bash
   # 再转 PDF 交叉验证（LibreOffice 需可写 HOME）
   export HOME=/tmp/lohome && mkdir -p $HOME
   libreoffice --headless --convert-to pdf 档案.docx --outdir /mnt/agents/output
   python3 -c "import pypdf; r=pypdf.PdfReader('档案.pdf'); print(len(r.pages), r.pages[0].extract_text()[:60], r.pages[-1].extract_text()[-80:])"
   ```

   段落数/表格数与 md 一致、PDF 首页是标题末页是附录，才算通过。
5. **交付话术**：同时给 md + docx（+pdf），说明各自适用场景（手机阅读用 pdf、编辑用 docx、电脑复习用 md）。
