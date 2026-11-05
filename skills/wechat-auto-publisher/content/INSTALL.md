# WeChat Auto Publisher 安装指南

## 🚀 一键安装

### 方法1：使用安装脚本（推荐）
```bash
# 1. 下载技能包
# （假设你已经下载了 wechat-auto-publisher-v1.0.0.tar.gz）

# 2. 解压并安装
tar -xzf wechat-auto-publisher-v1.0.0.tar.gz
cd wechat-auto-publisher
./install.sh
```

### 方法2：手动安装
```bash
# 1. 解压到OpenClaw技能目录
tar -xzf wechat-auto-publisher-v1.0.0.tar.gz -C ~/.openclaw/workspace/skills/

# 2. 设置执行权限
chmod +x ~/.openclaw/workspace/skills/wechat-auto-publisher/scripts/*.sh

# 3. 安装依赖
npm install -g @wenyan-md/cli
```

## 📋 前置要求

### 系统依赖
```bash
# 必需
npm install -g @wenyan-md/cli  # 微信公众号发布工具
curl                           # HTTP请求工具

# 可选但推荐
jq                             # JSON处理工具
ImageMagick                    # 图片生成工具（convert命令）
```

### 微信公众号准备
1. **获取API凭证**
   - 登录[微信公众平台](https://mp.weixin.qq.com/)
   - 进入「设置与开发」→「基本配置」
   - 获取「开发者ID(AppID)」和「开发者密码(AppSecret)」

2. **配置IP白名单**
   ```bash
   # 获取你的公网IP
   curl ifconfig.me
   ```
   - 将IP添加到公众号后台：设置与开发 → 基本配置 → IP白名单

## ⚙️ 配置步骤

### 1. 配置微信公众号凭证
编辑 `~/.openclaw/workspace/TOOLS.md`，添加以下内容：

```markdown
## 🔐 WeChat Auto Publisher (全自动微信公众号发布)

# 微信公众号API凭证 (必需)
export WECHAT_APP_ID=你的AppID
export WECHAT_APP_SECRET=你的AppSecret

# AI生成配置 (可选)
export OPENAI_API_KEY=sk-xxx        # 如果使用OpenAI
export DEEPSEEK_API_KEY=sk-xxx      # 如果使用DeepSeek

# 图片配置 (可选)
export UNSPLASH_ACCESS_KEY=xxx      # Unsplash API密钥
export LOCAL_IMAGE_DIR=/path/to/images  # 本地图片目录
```

### 2. 验证环境配置
```bash
cd ~/.openclaw/workspace/skills/wechat-auto-publisher
./scripts/setup.sh
```

## 🧪 测试安装

### 1. 运行完整性测试
```bash
./test-skill.sh
```

### 2. 测试预览模式（不实际发布）
```bash
./scripts/auto-publish.sh "测试主题" --dry-run
```

### 3. 测试完整流程
```bash
# 使用测试凭证（不会实际发布）
WECHAT_APP_ID=test WECHAT_APP_SECRET=test \
./scripts/auto-publish.sh "未来AI对工作的影响" --dry-run
```

## 🎯 开始使用

### 基本使用
```bash
# 一键自动化发布
./scripts/auto-publish.sh "你的选题"

# 示例：发布技术文章
./scripts/auto-publish.sh "Python编程技巧" --template tech-article

# 示例：发布商业分析
./scripts/auto-publish.sh "市场趋势分析" --template business-report
```

### 高级选项
```bash
# 指定AI模型
./scripts/auto-publish.sh "健康饮食指南" --model deepseek

# 只生成不发布（预览）
./scripts/auto-publish.sh "旅游攻略" --dry-run

# 指定输出目录
./scripts/auto-publish.sh "区块链技术" --output ./articles/
```

## 🔧 模块化使用

如果你只需要部分功能，可以单独使用各个模块：

```bash
# 1. 仅生成内容
./scripts/generate-content.sh "你的选题" --output article.md

# 2. 仅生成图片
./scripts/generate-images.sh "你的选题" --output ./images/

# 3. 格式化文章
./scripts/format-article.sh --input content.md --cover cover.jpg

# 4. 仅发布到微信公众号
./scripts/publish-wechat.sh formatted-article.md
```

## 🚨 故障排除

### 常见问题

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

**3. wenyan-cli未安装**
```bash
npm install -g @wenyan-md/cli
wenyan --version  # 验证安装
```

**4. 发布成功但看不到文章**
- 文章在**草稿箱**，需要手动审核发布
- 登录公众号后台：内容管理 → 草稿箱
- 选择文章 → 群发或发布

### 调试模式
```bash
# 启用详细日志
export DEBUG=true
./scripts/auto-publish.sh "测试选题" --verbose

# 查看中间文件
find /tmp/wechat-auto-publish-* -type f 2>/dev/null | head -10
```

## 🔄 更新与维护

### 检查更新
```bash
cd ~/.openclaw/workspace/skills/wechat-auto-publisher
git pull origin main  # 如果使用Git管理
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
./scripts/cleanup.sh 2>/dev/null || true

# 重新初始化
./scripts/setup.sh --force
```

## 📞 支持与反馈

### 文档资源
- **完整文档**：`SKILL.md` (详细技能说明)
- **快速开始**：`README.md` (使用指南)
- **脚本帮助**：`./scripts/auto-publish.sh --help`

### 问题反馈
1. 查看详细日志文件
2. 运行 `./scripts/setup.sh --verbose` 检查环境
3. 查阅 `references/troubleshooting.md` (如有)

### 功能建议
欢迎提出改进建议和新功能需求！

## 📄 许可证信息

本项目基于 MIT 许可证发布，详见 `LICENSE` 文件。

## 🙏 致谢

- [wenyan-cli](https://github.com/caol64/wenyan-cli) - 微信公众号发布工具
- [OpenClaw](https://openclaw.ai) - AI Agent框架
- 所有贡献者和用户

---

**安装完成！现在你可以开始你的公众号自动化之旅了！** 🚀

**自动化程度**：★★★★★  
**易用性**：★★★★★  
**稳定性**：★★★★☆  

有任何问题，请查阅相关文档或运行测试脚本验证安装。