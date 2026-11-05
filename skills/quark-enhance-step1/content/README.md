# 第一步 · 图像增强服务包

一个**可整体复制**的工作包，交给任意具备命令行能力的 AI Agent（Claude Code / Cursor / Cline / Codex 等），
让它独立完成归档工作流的**第一步**：把原始图片或扫描 PDF 处理成「档案级可用」的增强结果。

> 第二步（归档：分类、命名、索引、台账、事件链）**不在本包范围**，也不在本包中留下任何档案信息。
> 每次收到输入即是一次性处理，处理完把结果目录交回即可。

---

## 5 分钟上手

**1. 准备密钥**（不要写进任何文件）

```bash
export QUARK_AI_API_KEY=<你的夸克扫描王 aiApiKey>
```

或写入本机一个**不在版本控制内**的文件，运行时用 `QUARK_KEY_FILE` 指过去。

**2. 检查环境**

```bash
node -v                       # 需要 >= 18（内置 fetch）
python -c "import PIL, numpy" # 需要 Pillow + numpy
python -c "import pypdf"      # 需要 pypdf（可选，读 PDF 用）
```

**3. 跑一份**

```bash
python scripts/run_step1.py --input "C:/path/图.jpg" --outdir "./_out" --purpose 证件卡
```

跑完看 `_out/result.json`（标准化报告）和 `_out/run.log`。

**4. 先自检调用链**（强烈建议首次部署时做）

```bash
node scripts/call_mcp.js --list                     # 应列出 36 个工具，验证握手与鉴权
```

---

## 目录

```
第一步-增强服务包/
├── SKILL.md               Agent 规则文件（判据、红线、接口契约）—— 先读这个
├── README.md              本文件
├── config.example.json    配置模板（复制成 config.json 后填 Key）
├── scripts/
│   ├── probe.py           ⓪ 源件体检（件体/DPI/四缘/比例/EXIF/锐度/判重）
│   ├── prepare.py         ① 免费预处理（摆正、剥 EXIF、压缩、生成 @args.json）
│   ├── call_mcp.js        ② 夸克 MCP 调用器（图像与响应双落盘）
│   ├── verify.py          ③ 结果核验（几何变化率、尺寸、四缘、锐度）
│   └── run_step1.py       ④ 一站式编排 → result.json + run.log
└── docs/
    ├── 操作手册.md         分步命令与参数说明
    ├── 工具选择表.md       36 个工具的用途与选择规则
    └── 坑位摘要.md         与图像处理相关的实测坑位（去隐私版）
```

---

## 核心判据（详见 SKILL.md）

1. **先分扫描件 / 拍摄件，再谈 DPI**。拍摄件无论分辨率多高都要上云做几何校正。
2. **四缘纯白（rgb ≥ 252）＋ 比例 ≈ 标准纸幅 ⇒ 文档类图像**，可走本地 0 计费。
3. **含人像 / 国徽 / 防伪底纹 / 印章 / 手写签名 → 禁止用 OCR 重建类工具**（`scan_image_to_pdf`）。
4. **先免费后付费**：摆正 → 压缩 → 校验 → 上云 → 核验。
5. **上云前必剥 EXIF**，且不得按 EXIF 的 Orientation 旋正（它可能是错的）。

---

## 成本参考

| 动作 | 计费 |
|---|---|
| 体检、预处理、压缩、剥 EXIF、核验、报告 | 0 |
| `scan_general_ocr`（整图取文字） | **0**（免费通道） |
| `scan_certificate_invoice_enhance`、`scan_image_to_pdf` 等 | **每图 1 次** |
| 跨页图（一页含多件） | 合并为 **1 次**，不拆分 |

> 一套 95 份材料的实测统计：累计仅 26 次计费，其中 84 份走本地 0 计费路径。
> **先判断再调用**是省钱的关键——盲调会把成本放大数倍。

---

## 已验证范围

方法来源为一份经 95 份真实材料（证件、房产、医疗、票据、履历）验证的归档工作流，含约 64 条实测坑位。
本包装配其中与「图像处理」直接相关的部分，并已剥离全部档案数据（无姓名、无证件号、无住址）。
