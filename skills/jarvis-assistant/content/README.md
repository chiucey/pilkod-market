# 贾维斯智能助手 - OpenClaw 快速配置指南

## 🚀 快速开始

### 安装贾维斯

```bash
# 克隆或下载贾维斯技能到OpenClaw配置目录
openclaw skill install /path/to/jarvis-assistant

# 或使用npm包（如果有）
npm install @openclaw/skill-jarvis
```

### 激活贾维斯

在OpenClaw中加载技能后，贾维斯将自动激活。您可以通过以下方式唤醒：

```
"贾维斯" / "J.A.R.V.I.S." / "助手" / "帮我"
```

## ⚙️ OpenClaw 配置

### 配置文件结构

```
openclaw.config.js
├── skills/
│   └── jarvis-assistant/
│       ├── SKILL.md           # 主技能文件
│       ├── _meta.json         # 元数据
│       ├── references/        # 参考文献
│       │   ├── prompt-templates.md    # 提示词模板
│       │   ├── best-practices.md      # 最佳实践
│       │   └── capability-modules.md  # 能力模块详解
│       └── assets/            # 资源文件
```

### 环境变量配置

在 `.env` 文件中配置贾维斯的个性化选项：

```bash
# 贾维斯助手配置
JARVIS_LANGUAGE=zh-CN              # 交互语言
JARVIS_TONE=friendly               # 对话风格 (friendly/professional/casual)
JARVIS_DETAIL_LEVEL=balanced       # 详细程度 (concise/balanced/detailed)
JARVIS_MEMORY_ENABLED=true         # 启用记忆功能
JARVIS_PROACTIVE_HINTS=true       # 主动建议功能

# 知识库配置
JARVIS_KNOWLEDGE_BASE=/path/to/knowledge
JARVIS_MAX_MEMORY_ITEMS=1000       # 最大记忆条目数
```

### OpenClaw 配置文件示例

```javascript
// openclaw.config.js
module.exports = {
  skills: [
    {
      name: 'jarvis-assistant',
      path: './skills/jarvis-assistant',
      enabled: true,
      config: {
        // 能力开关
        capabilities: {
          documentProcessing: true,
          knowledgeMemory: true,
          professionalQA: true,
          contentCreation: true,
          codeAssistant: true,
          learningTutor: true,
          translation: true,
          productivityTools: true
        },
        // 个性化设置
        personality: {
          name: '贾维斯',
          greeting: '您好，我是贾维斯。有什么可以帮您的吗？',
          proactiveSuggestions: true
        },
        // 专业领域（可配置多个）
        expertise: [
          'technology',
          'business',
          'productivity'
        ],
        // 记忆配置
        memory: {
          enabled: true,
          maxItems: 1000,
          persistencePath: './data/jarvis-memory.json'
        }
      }
    }
  ],
  plugins: [
    // 推荐插件
    'openclaw-plugin-memory',      // 记忆插件
    'openclaw-plugin-knowledge-base', // 知识库插件
    'openclaw-plugin-web-search'    // 网络搜索插件
  ]
}
```

## 📋 使用方法

### 基础对话

```
用户: 贾维斯，帮我写一份Q2工作总结
贾维斯: [根据您的工作内容和Q2数据生成总结]

用户: 继续完善第三部分
贾维斯: [继续完成内容]

用户: 太正式了，改得轻松一些
贾维斯: [调整语气风格]
```

### 复杂任务

```
用户: 帮我的AI产品做一个完整的上市方案
贾维斯:
这是一个综合任务，我将分模块处理：
- 📊 市场分析 - 了解产品定位和目标市场
- 📄 方案策划 - 制定上市策略
- 📈 PPT制作 - 生成演示材料
- ✍️ 文案撰写 - 准备宣传材料

首先，请告诉我：
1. 产品名称和核心功能？
2. 目标用户群体？
3. 预计上市时间？
```

### 知识记忆

```
用户: 我的公司叫XX科技，主要做B端SaaS产品
贾维斯: 已记录公司信息：
- 公司名称：XX科技
- 产品类型：B端SaaS
- 相关信息将用于后续服务

用户: 下次帮我写东西都用这个背景
贾维斯: 明白，已设置默认背景为XX科技的B端SaaS产品。
```

## 🎯 高级配置

### 自定义提示词模板

在 `references/prompt-templates.md` 中添加您自己的模板：

```markdown
## 我的自定义模板

### 项目启动模板
...
```

### 能力模块开关

```javascript
// 只启用部分能力
config: {
  capabilities: {
    documentProcessing: true,  // 文档处理
    contentCreation: true,     // 内容创作
    // 其他模块关闭
  }
}
```

### 集成外部服务

```javascript
// 集成外部API
config: {
  integrations: {
    slack: {
      enabled: true,
      webhook: process.env.SLACK_WEBHOOK
    },
    notion: {
      enabled: true,
      apiKey: process.env.NOTION_API_KEY
    },
    github: {
      enabled: true,
      token: process.env.GITHUB_TOKEN
    }
  }
}
```

## 🔧 故障排除

### 常见问题

**Q: 贾维斯没有响应？**
```
检查：
1. 技能是否正确安装
2. OpenClaw是否正常运行
3. 环境变量是否配置
```

**Q: 记忆功能不工作？**
```
检查：
1. memory.enabled 是否为 true
2. persistencePath 是否可写
3. 磁盘空间是否充足
```

**Q: 如何重置贾维斯？**
```bash
# 删除记忆数据
rm ./data/jarvis-memory.json

# 重启OpenClaw
openclaw restart
```

## 📞 支持

如有问题或建议，请：
1. 查看 `references/` 中的文档
2. 检查配置文件语法
3. 查看 OpenClaw 日志

---

**版本**: 1.0.0
**作者**: MiniMax Agent
**更新**: 2024-03-23
