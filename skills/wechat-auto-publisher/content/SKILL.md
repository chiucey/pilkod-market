---
name: wechat-auto-publisher
description: "全自动微信公众号发布工作流：从选题→内容生成→配图→排版→发布到草稿箱的一站式解决方案。配置凭证后，只需提供选题即可自动化发布公众号文章。"
metadata:
  {
    "openclaw":
      {
        "emoji": "🤖",
        "tags": ["wechat", "公众号", "automation", "publishing", "content-generation"],
        "version": "1.1.0"
      },
  }
---

# wechat-auto-publisher

**全自动微信公众号发布工作流 🤖**

一键自动化：选题 → 内容生成 → 配图 → 排版 → 发布到草稿箱

## ✨ 核心功能

- **🎯 选题到发布全流程** - 只需提供选题，自动完成所有中间步骤
- **🔍 智能素材搜集** - 支持多平台（网页、微信公众号、知乎、B站等）自动搜集相关素材
- **🤖 智能内容生成** - 基于搜集素材或纯AI生成高质量文章（支持多模型）
- **🖼️ 自动配图系统** - 智能匹配章节图片和封面图
- **🎨 专业排版优化** - 自动应用微信公众号最佳排版实践
- **🔧 灵活配置** - 可自定义生成模板、图片风格、发布参数、搜索平台
- **📊 进度追踪** - 实时显示每个步骤的状态和结果
- **🔄 容错重试** - 自动处理网络问题、API限制等异常

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 wenyan-cli（微信公众号发布工具）
npm install -g @wenyan-md/cli

# 验证安装
wenyan --version
```

### 2. 配置微信公众号凭证

**在 TOOLS.md 中添加（必需）：**

```markdown
## 🔐 WeChat Auto Publisher (全自动微信公众号发布)

# 微信公众号API凭证
export WECHAT_APP_ID=你的AppID
export WECHAT_APP_SECRET=你的AppSecret

# 可选：AI生成配置（如使用OpenAI、DeepSeek等）
export OPENAI_API_KEY=sk-xxx  # 如果使用OpenAI生成内容
export DEEPSEEK_API_KEY=sk-xxx  # 如果使用DeepSeek

# 可选：图片生成配置
export UNSPLASH_ACCESS_KEY=xxx  # Unsplash API密钥
# 或使用本地图片目录
export LOCAL_IMAGE_DIR=/path/to/images
```

### 3. 配置IP白名单

**必须步骤：** 将运行服务器的公网IP添加到微信公众号后台白名单

```bash
# 获取你的公网IP
curl ifconfig.me

# 将显示的IP添加到：
# 微信公众平台 → 设置与开发 → 基本配置 → IP白名单
```

### 4. 测试自动化流程

```bash
# 进入skill目录
cd /root/.openclaw/workspace/skills/wechat-auto-publisher

# 测试发布（使用示例选题）
./scripts/auto-publish.sh "未来AI对工作的影响"
```

## 📋 完整工作流程

```
1. 📥 接收选题
   ↓
2. 🧠 智能内容生成
   ├── 文章大纲生成
   ├── 分章节内容扩展
   ├── 标题优化
   └── SEO关键词优化
   ↓
3. 🖼️ 自动配图系统
   ├── 封面图生成/匹配
   ├── 章节配图选择
   ├── 图片尺寸优化
   └── 版权检查
   ↓
4. 📝 文章格式化
   ├── 添加Frontmatter（标题、封面、作者）
   ├── 应用排版模板
   ├── 代码高亮配置
   └── 微信格式优化
   ↓
5. 🚀 发布到公众号
   ├── 图片上传到微信图床
   ├── Markdown转微信公众号格式
   ├── 推送到草稿箱
   └── 返回文章链接
   ↓
6. 📊 结果反馈
   └── 发布状态、草稿链接、预览二维码
```

## 🎯 使用方法

### 方式1：命令行直接使用

```bash
# 基本用法：提供选题
./scripts/auto-publish.sh "未来AI对工作的影响"

# 指定输出目录
./scripts/auto-publish.sh "区块链技术入门" --output ./articles/

# 使用特定模板
./scripts/auto-publish.sh "Python编程技巧" --template tech-article

# 指定AI模型
./scripts/auto-publish.sh "健康饮食指南" --model deepseek

# 只生成不发布（预览）
./scripts/auto-publish.sh "旅游攻略" --dry-run
```

### 方式2：在OpenClaw中使用

**触发短语：**
- "帮我发布一篇关于[选题]的文章"
- "自动化发布公众号：[选题]"
- "生成并发布：[选题]"

**示例对话：**
```
用户：帮我发布一篇关于"未来五年科技趋势"的文章

AI：好的，我将为您自动化发布一篇关于"未来五年科技趋势"的公众号文章。
     正在启动全流程：内容生成 → 配图 → 排版 → 发布...
     
     步骤1/5：生成文章大纲... ✅
     步骤2/5：扩展内容... ✅  
     步骤3/5：匹配配图... ✅
     步骤4/5：格式化排版... ✅
     步骤5/5：发布到草稿箱... ✅
     
     🎉 发布成功！
     📝 标题：《未来五年科技趋势：AI、量子计算与生物科技的融合》
     🔗 草稿链接：https://mp.weixin.qq.com/s/draft/xxxx
     📱 可在公众号后台审核发布
```

### 方式3：批量处理

```bash
# 从文件读取多个选题
cat topics.txt | xargs -I {} ./scripts/auto-publish.sh "{}"

# 定期自动发布（结合cron）
# 每天上午10点发布一篇
0 10 * * * cd /path/to/skill && ./scripts/auto-publish.sh "$(./scripts/generate-topic.sh)"
```

## ⚙️ 配置选项

### 1. 内容生成配置

支持多种AI模型，按优先级选择：

```bash
# 配置优先级（在脚本中设置）
CONTENT_GENERATORS=("openai" "deepseek" "claude" "local-llm")

# 模型特定配置
export OPENAI_MODEL="gpt-4"
export DEEPSEEK_MODEL="deepseek-chat"
export MAX_TOKENS=2000
export TEMPERATURE=0.7
```

### 2. 图片配置

**图片来源优先级：**
1. 本地图片库（配置`LOCAL_IMAGE_DIR`）
2. Unsplash API（免费高质量图库）
3. 占位图片（fallback）

```bash
# 图片风格配置
export IMAGE_STYLE="tech"  # tech/business/lifestyle/creative
export COVER_RATIO="1080x864"  # 微信推荐封面比例
export CHAPTER_IMAGE_SIZE="800x600"
```

### 3. 排版模板

内置多种模板，适合不同内容类型：

| 模板 | 适用场景 | 特点 |
|------|----------|------|
| `tech-article` | 技术教程 | 代码高亮、结构清晰 |
| `business-report` | 商业分析 | 数据突出、专业感强 |
| `lifestyle-blog` | 生活随笔 | 温馨自然、阅读舒适 |
| `news-article` | 新闻资讯 | 时效性强、重点突出 |
| `marketing-post` | 营销推广 | 转化导向、行动号召 |

### 4. 发布配置

```bash
# 发布参数
export WECHAT_THEME="lapis"  # 排版主题
export CODE_HIGHLIGHT="solarized-light"  # 代码高亮主题
export ENABLE_MAC_STYLE=true  # Mac风格代码块
export AUTO_PUBLISH=true  # 生成后自动发布
```

## 🛠️ 核心脚本

### `scripts/auto-publish.sh` - 主流程脚本

```bash
#!/usr/bin/env bash
# 全自动公众号发布主脚本
# 用法：./auto-publish.sh "选题" [选项]

选项：
  --output DIR      指定输出目录
  --template NAME   使用指定模板
  --model NAME      指定AI模型
  --dry-run         只生成不发布
  --verbose         详细输出模式
  --help            显示帮助
```

**流程控制：**
1. 参数解析和验证
2. 环境检查（凭证、依赖）
3. 内容生成（调用AI）
4. 图片匹配/生成
5. 文章格式化
6. 发布到微信公众号
7. 结果反馈

### `scripts/setup.sh` - 环境配置检查

```bash
#!/usr/bin/env bash
# 检查并配置运行环境

功能：
- 检查 wenyan-cli 是否安装
- 验证微信公众号凭证
- 检查IP白名单配置
- 测试网络连接
- 初始化目录结构
```

### `scripts/generate-content.sh` - 内容生成器

```bash
#!/usr/bin/env bash
# 基于选题生成文章内容

输入：选题字符串
输出：完整的Markdown文章

流程：
1. 生成文章大纲（标题、章节结构）
2. 分章节扩展内容
3. 优化标题和摘要
4. 添加SEO元素
5. 输出标准Markdown格式
```

### `scripts/generate-images.sh` - 图片生成器

```bash
#!/usr/bin/env bash
# 为文章匹配/生成图片

输入：文章内容和章节结构
输出：封面图 + 章节配图

流程：
1. 分析文章主题和关键词
2. 从本地库匹配相关图片
3. 或调用API生成/获取图片
4. 优化图片尺寸和格式
5. 生成图片引用Markdown
```

### `scripts/format-article.sh` - 文章格式化

```bash
#!/usr/bin/env bash
# 将原始内容格式化为公众号标准格式

输入：原始Markdown + 图片
输出：带Frontmatter的完整文章

功能：
- 添加Frontmatter（标题、封面、作者、日期）
- 应用排版模板
- 优化段落和标题样式
- 配置代码高亮
- 生成最终发布文件
```

## 📁 项目结构

```
wechat-auto-publisher/
├── SKILL.md                      # 技能主文档
├── README.md                     # 使用说明
├── example-topic.txt             # 示例选题
├── example-output.md             # 示例输出文章
├── scripts/
│   ├── auto-publish.sh           # 主流程脚本
│   ├── setup.sh                  # 环境配置检查
│   ├── generate-content.sh       # 内容生成器
│   ├── generate-images.sh        # 图片生成器
│   ├── format-article.sh         # 文章格式化
│   ├── publish-wechat.sh         # 微信公众号发布
│   └── utils.sh                  # 通用工具函数
├── templates/
│   ├── tech-article.md           # 技术文章模板
│   ├── business-report.md        # 商业分析模板
│   ├── lifestyle-blog.md         # 生活随笔模板
│   ├── news-article.md           # 新闻资讯模板
│   └── marketing-post.md         # 营销推广模板
├── config/
│   ├── generators/               # 内容生成器配置
│   │   ├── openai-config.sh      # OpenAI配置
│   │   ├── deepseek-config.sh    # DeepSeek配置
│   │   └── local-llm-config.sh   # 本地模型配置
│   ├── image-sources/            # 图片来源配置
│   │   ├── unsplash-config.sh    # Unsplash配置
│   │   ├── local-images.sh       # 本地图库配置
│   │   └── fallback-images.sh    # 备用图片配置
│   └── templates-config.sh       # 模板系统配置
├── references/
│   ├── workflow-diagram.md       # 工作流程图
│   ├── api-reference.md          # API参考文档
│   ├── troubleshooting.md        # 故障排查指南
│   └── best-practices.md         # 最佳实践
└── assets/
    ├── default-cover.jpg         # 默认封面图
    ├── tech-images/              # 技术类图片库
    ├── business-images/          # 商业类图片库
    └── lifestyle-images/         # 生活类图片库
```

## 🔌 集成选项

### 1. AI模型集成

**支持的主流AI服务：**
- OpenAI GPT系列（GPT-4, GPT-3.5）
- DeepSeek（免费/付费）
- Claude（Anthropic）
- 本地LLM（通过Ollama等）
- 百度文心、阿里通义等国内模型

### 2. 图片源集成

**多图片来源支持：**
- **Unsplash** - 免费高质量图库
- **Pexels** - 免费商业图片
- **本地图库** - 自定义图片集合
- **AI生成** - DALL-E、Midjourney等
- **CDN缓存** - 提高加载速度

### 3. 内容源扩展

**除了AI生成，还可集成：**
- RSS订阅自动转载
- 知乎、简书等平台文章
- 本地Markdown文档库
- 数据库内容查询

## 🚨 故障排查

### 常见问题及解决

**1. 错误：`WECHAT_APP_ID not set`**
```bash
# 检查TOOLS.md配置
cat ~/.openclaw/workspace/TOOLS.md | grep WECHAT

# 临时设置环境变量
export WECHAT_APP_ID=your_id
export WECHAT_APP_SECRET=your_secret
```

**2. 错误：`45166 IP地址不在白名单中`**
```bash
# 获取当前公网IP
curl ifconfig.me

# 登录微信公众平台添加IP白名单
# 设置与开发 → 基本配置 → IP白名单
```

**3. 内容生成失败**
```bash
# 检查AI API配置
echo $OPENAI_API_KEY  # 或 $DEEPSEEK_API_KEY

# 使用备用模型
./scripts/auto-publish.sh "选题" --model deepseek
```

**4. 图片加载失败**
```bash
# 使用本地图片模式
export IMAGE_SOURCE="local"
export LOCAL_IMAGE_DIR="/path/to/your/images"

# 或使用备用图片
export USE_FALLBACK_IMAGES=true
```

**5. 发布成功但看不到文章**
- 文章在**草稿箱**，需要手动审核发布
- 登录公众号后台：内容管理 → 草稿箱
- 选择文章 → 群发或发布

### 调试模式

```bash
# 启用详细日志
export DEBUG=true
./scripts/auto-publish.sh "测试选题" --verbose

# 查看中间文件
ls -la /tmp/wechat-auto-publish-*
```

## 🔄 更新与维护

### 检查更新
```bash
# 从GitHub拉取最新版本
cd /root/.openclaw/workspace/skills/wechat-auto-publisher
git pull origin main
```

### 备份配置
```bash
# 备份重要配置
cp -r config/ config-backup-$(date +%Y%m%d)
cp scripts/*.sh scripts-backup-$(date +%Y%m%d)
```

### 重置环境
```bash
# 清理临时文件
./scripts/cleanup.sh

# 重新初始化
./scripts/setup.sh --force
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request改进此技能！

### 开发流程
1. Fork本仓库
2. 创建特性分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature`
5. 提交Pull Request

### 代码规范
- Shell脚本使用bash，遵循Google Shell Style Guide
- 配置文件使用JSON或YAML格式
- 文档使用Markdown格式
- 添加适当的错误处理和日志

### 测试要求
- 新功能需要添加测试用例
- 更新文档和示例
- 确保向后兼容性

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [wenyan-cli](https://github.com/caol64/wenyan-cli) - 微信公众号发布工具
- [OpenClaw](https://openclaw.ai) - 强大的AI Agent框架
- 所有贡献者和用户

## 📮 支持与反馈

- **GitHub Issues**: [提交问题或建议](https://github.com/your-repo/issues)
- **文档更新**: 欢迎补充使用经验和最佳实践
- **功能请求**: 描述你的使用场景和需求

---

**如果这个技能对你有帮助，请给个⭐️ Star！**

**自动化程度：** ⭐⭐⭐⭐⭐ (全自动)
**易用性：** ⭐⭐⭐⭐⭐ (配置一次，永久使用)
**稳定性：** ⭐⭐⭐⭐☆ (生产环境可用)