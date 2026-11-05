---
name: academic-mind
description: 基于 Claude Code 源码架构的未来版 AI 学术写作工具。当用户需要创建学术写作助手、设计 AI 研究工具、构建论文辅助系统、进行学术写作辅助（语法检查、润色、审稿、翻译）、或需要集成 Kairos/Ultraplan/Buddy 等多模式 AI 架构时使用。
---

# AcademicMind - 未来版 AI 学术写作套件

## 核心概念

**AcademicMind** 是一款基于 Claude Code 模块化架构设计的 AI 学术写作助手，融合三大 AI 人格模式：

| 模式 | 标识色 | 功能定位 |
|------|--------|----------|
| **Kairos** | 蓝色 | 持久化研究伴侣 - 跨会话记忆、冲突检测、一致性检查 |
| **Ultraplan** | 紫色 | 深度思考引擎 - 多阶段分析、复杂任务推演 |
| **Buddy** | 绿色 | 情感写作伙伴 - 进度激励、情绪支持 |

## 技术架构 (Claude Code 风格)

### 后端模块 (Python FastAPI)

```
backend/
├── main.py           # FastAPI 应用入口
├── query_engine.py   # 查询引擎 - 分段加载、优先级排序、主动压缩
├── memory_store.py   # 记忆存储 - 自修复记忆结构、一致性检查
├── workflows.py       # 工作流引擎 - 学术写作任务处理
└── models.py         # 数据模型
```

### 前端模块 (React + TypeScript)

```
src/
├── App.tsx           # 主应用组件
├── components/
│   ├── ModeSelector.tsx    # 模式选择器
│   ├── SidePanel.tsx       # 侧边栏（项目/工作流）
│   ├── MainWorkspace.tsx   # 主工作区
│   ├── ContextPanel.tsx    # 上下文面板（记忆管理）
│   ├── Header.tsx          # 顶部导航
│   └── StatusBar.tsx       # 状态栏
├── lib/
│   ├── types.ts      # TypeScript 类型定义
│   └── api.ts        # API 客户端
└── App.css           # 样式文件
```

## Claude Code 核心机制实现

### 1. Query Engine (查询引擎)

```python
class AcademicQueryEngine:
    """
    Claude Code 风格的分段处理：
    - 分段加载 (Segmented Loading)
    - 优先级排序 (Priority Sorting)
    - 主动压缩 (Active Compression)
    """

    HIGH_PRIORITY_KEYWORDS = [
        "hypothesis", "conclusion", "findings",
        "methodology", "evidence", "significant"
    ]

    def _segment_input(self, text: str):
        """按段落分割长文本"""
        # 逐段处理，而非一次性读取
        pass

    def _prioritize_chunks(self, chunks):
        """高优先级标记核心论点"""
        pass
```

### 2. Memory Store (记忆存储)

```python
class MemoryStore:
    """
    Claude Code 的自修复记忆结构：
    - 记忆整合 (Memory Integration)
    - 一致性检查 (Consistency Checking)
    """

    def check_consistency(self, new_content: str) -> list:
        """检测与现有记忆的冲突"""
        pass

    def integrate_memory(self, memory_id: str, integration_text: str):
        """整合新信息到已有记忆"""
        pass
```

## 集成的工作流

### 1. 语法检查
- 输入：原始文本
- 输出：Markdown 表格（原句 | 修正 | 高亮关键词）

### 2. 学术润色
- 支持中英双语
- 输出：润色版本 + 修改原因表格

### 3. 逻辑分析
- 段落连贯性检查
- 输出：改进文本 + 中文改进建议

### 4. 翻译
- 中译英 / 英译中
- 提供两个翻译版本

### 5. 同行评审
- 五阶段深度审稿：
  1. 获取目标期刊要求
  2. 理解文章结构
  3. 逐节全面审稿
  4. 问题分级排序
  5. 总体评价建议

### 6. 文献分析 (菲利普阅读法)
- WTD / ROF / SPL / CPL/GAP / RFW / POC

### 7. 引用搜索
- 自动拆分句子查找引用

### 8. 深度研究
- 多阶段综合研究分析

## 设计规范

### 配色方案
```css
:root {
  --bg-primary: #0a0e14;      /* 深空黑 */
  --kairos: #58a6ff;          /* 蓝色 */
  --ultraplan: #a371f7;       /* 紫色 */
  --buddy: #7ee787;           /* 绿色 */
}
```

### 字体
- 标题：Space Grotesk
- 正文：IBM Plex Sans
- 代码/引用：JetBrains Mono

## 使用示例

### 启动后端
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### 构建前端
```bash
cd frontend
pnpm install
pnpm add framer-motion
pnpm build
```

### 部署
```bash
# 前端
deploy --dist_dir=frontend/dist

# 后端 (需要配置 API 密钥)
```

## 核心原则

1. **AI 是辅助，不是替代** - 学术写作的核心能力必须保持
2. **上下文管理** - 长文本分段处理，关键信息优先保留
3. **记忆持久化** - 跨会话保持研究上下文
4. **渐进式思考** - 复杂任务拆分为多阶段处理
