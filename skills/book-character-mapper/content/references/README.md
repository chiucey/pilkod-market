# 小说人物关系图谱生成器 - 快速开始指南

## 📦 Skill 包内容

```
book-character-mapper/
├── skill.json      # Skill 元数据配置
├── SKILL.md        # 完整说明文档
├── template.html   # 可视化图谱 HTML 模板
└── parser.py       # Python 解析脚本（可选）
```

## 🚀 快速使用

### 方法 1：通过 MiniMax Agent（推荐）

在 MiniMax Agent 对话中直接发送：

```
分析《书名》的人物关系图谱
```

或

```
生成角色关系图
```

系统会自动：
1. 读取你的书籍文件
2. 分析人物和关系
3. 生成可视化图谱
4. 提供在线访问链接

### 方法 2：手动使用 HTML 模板

1. 打开 `template.html`
2. 找到 `CHARACTERS_DATA` 和 `RELATIONSHIPS_DATA` 变量
3. 替换为你的数据
4. 在浏览器中打开

### 方法 3：使用 Python 脚本

```bash
# 安装依赖
pip install ebooklib beautifulsoup4

# 运行解析
python parser.py input.epub output.html "书名"
```

## 📝 数据格式

### 人物数据

```javascript
const characters = [
    {
        id: "grace",           // 唯一标识
        name: "瑞恩·格雷斯",   // 姓名
        emoji: "👤",           // 性别标识: 👤男 👩女 👽外星
        isProtagonist: true,   // 是否主角
        color: "#27ae60",      // 节点颜色
        intro: "美国宇航员...", // 简介
        nationality: "🇺🇸 美国"  // 国籍/身份
    }
];
```

### 关系数据

```javascript
const relationships = [
    {
        from: "grace",              // 起始人物 ID
        to: "rocky",                // 目标人物 ID
        type: "friend",             // 关系类型
        label: "跨种族友谊",        // 关系描述
        direction: "bidirectional"  // single/bidirectional
    }
];
```

## 🎨 配色方案

| 主题 | 背景色 | 风格 |
|------|--------|------|
| 深邃星空 | #0d1117 | 科技感 |
| 经典蓝白 | #1a365d | 商务风 |
| 暗夜紫罗兰 | #1a1a2e | 神秘感 |
| 森林秘境 | #1a2f1a | 自然风 |
| 沙漠黄昏 | #2d1f0f | 复古风 |
| 极简灰白 | #f5f5f5 | 简约风 |
| 复古羊皮 | #f4ecd8 | 古典风 |
| 薄荷清晨 | #e8f5f0 | 清爽风 |
| 天空蓝调 | #e8f4fc | 清新风 |

## ⚙️ 物理参数

| 参数 | 说明 | 范围 |
|------|------|------|
| 斥力 | 节点排斥强度 | 500-8000 |
| 刚度 | 弹簧弹力 | 1-100 |
| 向心 | 中心引力 | 0-100 |
| 阻尼 | 运动衰减 | 0.05-0.99 |

## 📂 发布到技能市场

1. 访问 https://agent.minimaxi.com/skill-creator/
2. 选择"从模板创建"或"导入现有技能"
3. 上传 `skill.json` 和相关文件
4. 填写描述和标签
5. 提交审核

## 📄 许可证

MIT License - 可自由使用、修改和分发

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
