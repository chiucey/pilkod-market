# WeChat Auto Publisher

**全自动微信公众号发布工作流** 🤖

只需一个选题，自动完成：内容生成 → 配图 → 排版 → 发布到公众号草稿箱

## 🚀 5分钟快速开始

### 第1步：安装依赖
```bash
npm install -g @wenyan-md/cli
```

### 第2步：配置凭证
在 `~/.openclaw/workspace/TOOLS.md` 中添加：
```markdown
## 🔐 WeChat Auto Publisher
export WECHAT_APP_ID=你的AppID
export WECHAT_APP_SECRET=你的AppSecret
```

### 第3步：添加IP白名单
```bash
# 获取你的公网IP
curl ifconfig.me
# 将IP添加到公众号后台：设置与开发 → 基本配置 → IP白名单
```

### 第4步：测试发布
```bash
cd /root/.openclaw/workspace/skills/wechat-auto-publisher
./scripts/auto-publish.sh "未来AI对工作的影响"
```

## 📋 核心功能

### 一键自动化
- **选题输入** → 只需提供文章主题
- **智能生成** → AI撰写高质量内容
- **自动配图** → 智能匹配封面和插图
- **专业排版** → 微信公众号优化格式
- **一键发布** → 直达草稿箱

### 灵活配置
- **多AI支持**：OpenAI、DeepSeek、Claude、本地LLM
- **多图源**：Unsplash、本地图库、AI生成
- **多模板**：技术文章、商业报告、生活随笔等
- **可扩展**：支持自定义生成器和处理器

## 🎯 使用方式

### 方式1：命令行（最常用）
```bash
# 基本使用
./scripts/auto-publish.sh "你的选题"

# 高级选项
./scripts/auto-publish.sh "选题" \
  --template tech-article \
  --model deepseek \
  --output ./articles/ \
  --dry-run
```

### 方式2：OpenClaw对话
```
用户：帮我发布一篇关于"Python编程技巧"的文章

AI：好的，正在自动化发布...
     [进度显示]
     ✅ 发布成功！草稿链接：https://mp.weixin.qq.com/s/draft/xxx
```

### 方式3：定时任务
```bash
# 每天自动发布一篇
0 10 * * * cd /path/to/skill && ./scripts/auto-publish.sh "$(date +%Y年%m月%d日科技动态)"
```

## ⚙️ 配置说明

### 必需配置
1. **微信公众号凭证** - AppID和AppSecret
2. **IP白名单** - 服务器公网IP
3. **wenyan-cli** - 发布工具依赖

### 可选配置
- **AI API密钥** - 用于内容生成（OpenAI、DeepSeek等）
- **图片源** - Unsplash密钥或本地图库路径
- **模板选择** - 根据内容类型选择模板

## 📁 文件结构
```
wechat-auto-publisher/
├── scripts/           # 核心脚本
│   ├── auto-publish.sh    # 主流程
│   ├── setup.sh       # 环境检查
│   ├── generate-*.sh  # 各阶段处理器
│   └── utils.sh       # 工具函数
├── templates/         # 文章模板
├── config/           # 配置文件
├── references/       # 参考文档
└── assets/          # 资源文件
```

## 🔧 故障排查

### 常见问题
1. **凭证错误** → 检查TOOLS.md中的WECHAT_APP_ID/SECRET
2. **IP白名单** → 添加服务器IP到公众号后台
3. **内容生成失败** → 检查AI API密钥或切换模型
4. **发布成功但看不到** → 文章在草稿箱，需要审核发布

### 调试模式
```bash
export DEBUG=true
./scripts/auto-publish.sh "测试" --verbose
```

## 🔄 更新维护
```bash
# 更新skill
cd /root/.openclaw/workspace/skills/wechat-auto-publisher
git pull origin main

# 备份配置
cp -r config/ config-backup-$(date +%Y%m%d)
```

## 📞 支持
- 查看详细文档：`SKILL.md`
- 故障排查：`references/troubleshooting.md`
- 提交问题：[GitHub Issues](https://github.com/your-repo/issues)

---

**自动化程度**：★★★★★  
**易用性**：★★★★★  
**稳定性**：★★★★☆  

开始你的公众号自动化之旅吧！ 🚀