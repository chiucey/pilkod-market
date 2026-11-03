---
name: 作品简介
description: SJTU 论文排版助手的课程项目作品简介，包含作品信息、核心价值、团队分工、引擎架构。
---

# SJTU 论文排版助手 — 作品简介

## 作品信息

| 项目 | 内容 |
|------|------|
| 作品名 | SJTU 论文排版助手（ThesisFormatter） |
| 所属赛道 | 赛道二：SJTU 专属大模型技能定制（SkillJTU） |
| 适用场景 | 科研辅助支持 —— 论文格式规范 |
| 课程 | 人工智能基础(A)-AI1201-10 |

## 作品简介

本作品是一款专为上海交通大学学生设计的**智能论文排版技能**。核心定位是"**粘贴+交互，论文自动生成**"——用户通过渐进式对话提供论文信息，AI 即可自动按照《上海交通大学学位论文撰写要求》排版并生成 **Word (.docx)** 或 **LaTeX (.tex)** 实际文件。

### 核心价值

- **渐进式信息披露**：分轮对话收集信息，不一次性骚扰用户，用户体验流畅
- **实际文档生成**：不再只输出"样式指导"，而是直接生成可打印/可提交的 Word 或 LaTeX 文件
- **零学习成本**：无需学习 Word/LaTeX 排版操作，全程对话式交互
- **智能结构识别**：自动识别章、节、子节、图表、公式、参考文献
- **标准规范**：严格遵循 SJTU 学位论文撰写要求
- **双格式支持**：同时支持 Word (.docx) 和 LaTeX (.tex) 输出
- **迭代修正**：用户可随时提出修改要求，AI 实时响应

### 目标用户

正在撰写学位论文的上海交通大学本科生、硕士研究生、博士研究生，尤其是：
- 不了解论文格式规范的低年级本科生
- 希望节省排版时间的高年级学生
- 需要使用 LaTeX 但经验不足的研究生

## 引擎架构

本技能包含完整的 Python 引擎，可实现实际文档生成：

```
my-skill/
├── SKILL.md                     # 技能定义 + 渐进式工作流 + 格式规范
├── template.md                  # 完整系统 Prompt（7 部分分层架构）
├── sjtuthesis_engine.py         # 🆕 CLI 入口（doctor/info/render-word/render-latex/validate）
├── requirements.txt             # 🆕 Python 依赖
├── modules/
│   ├── __init__.py
│   ├── thesis_info.py           # 🆕 渐进式信息收集模型
│   ├── word_renderer.py         # 🆕 Word 文档生成（python-docx）
│   ├── latex_renderer.py        # 🆕 LaTeX 文档生成
│   └── validator.py             # 🆕 格式合规验证
├── examples/
│   ├── sample.md
│   └── feedback.md
└── scripts/
    └── validate.sh              # 结构验证脚本
```

### 快速开始

```bash
# 1. 安装依赖
pip install python-docx tqdm

# 2. 查看引擎功能
python sjtuthesis_engine.py help

# 3. 环境诊断
python sjtuthesis_engine.py doctor

# 4. 全流程引导（信息收集 + 文档生成）
python sjtuthesis_engine.py interactive

# 5. 分步操作
python sjtuthesis_engine.py info                    # 收集信息
python sjtuthesis_engine.py render-word info.json output.docx   # 生成 Word
python sjtuthesis_engine.py render-latex info.json output.tex   # 生成 LaTeX
python sjtuthesis_engine.py validate output.docx    # 验证格式
```

## 渐进式工作流

本技能采用 4 轮渐进式信息披露，引导用户逐步提供论文信息：

| 轮次 | 收集内容 | 说明 |
|------|---------|------|
| 第1轮 | 论文草稿/标题、学位类型、学院、输出格式 | 基本信息 |
| 第2轮 | 姓名、学号、专业、导师、论文题目 | 个人信息 |
| 第3轮 | 页眉偏好、编号体系、关键词、摘要 | 排版偏好 |
| 第4轮 | 信息汇总确认 → 生成文档 | 确认生成 |

## 团队分工

| 角色 | 职责 |
|------|------|
| （填写姓名） | 技能设计与 Prompt 工程 |
| （填写姓名） | 试用测试与反馈收集 |
| （填写姓名） | 文档撰写与演示制作 |

## 参考资料

1. 上海交通大学研究生院. 上海交通大学博士、硕士学位论文撰写指南. https://gs.sjtu.edu.cn/post/detail/Z3MzNDA0
2. GB/T 7714-2015 信息与文献 参考文献著录规则
3. SJTUThesis 项目. https://github.com/learningforbetter/SJTUThesis
4. minimax-docx-pro 项目（架构参考）
