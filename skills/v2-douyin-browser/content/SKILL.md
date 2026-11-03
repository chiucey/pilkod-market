---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30450220283cc084ee784d7d21553a602ac4903874bab3c5bdda2eefd04d015dec5f5175022100ab72c72006265c91cc70a9b246c452f4f21c51ae8f934d97503e945d73d96797
    ReservedCode2: 304402205c2795d7b59e2c99934468ca95e7beed837622279937cf86b1ee00f6f616836f022005d40e8d07b02de38025286cab2f9e1cf60acfb4ab08622239f0e96b094b3b53
description: Browse Douyin (抖音) with your account via QR code login. Play videos, extract complete data (views, likes, comments), summarize content. Uses real browser automation for full access.
name: v2-douyin-browser
---

# Douyin Video Browser

## 核心定位

这是一个 **"扫码登录 + 浏览器自动化"** 的抖音浏览工具。

**你的账号 → 扫码授权 → 完整浏览抖音**

---

## 只需3步：扫码 → 浏览 → 总结

```
┌─────────────────────────────────────────────────────────┐
│                                                          │
│   第1步：扫码登录                                         │
│   ┌─────────────────────────────────┐                   │
│   │   生成二维码  →  用抖音App扫码  →  授权成功            │ │
│   └─────────────────────────────────┘                   │
│                    ↓                                      │
│   第2步：浏览器自动浏览                                    │
│   ┌─────────────────────────────────┐                   │
│   │   打开抖音  →  访问任意视频/用户/话题                  │ │
│   └─────────────────────────────────┘                   │
│                    ↓                                      │
│   第3步：提取并总结内容                                    │
│   ┌─────────────────────────────────┐                   │
│   │   获取完整数据  →  整理报告  →  呈现给你              │ │
│   └─────────────────────────────────┘                   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 第1步：扫码登录（必须且优先）

### 生成登录二维码

```
用户请求："我想浏览抖音"

助手响应：
┌─────────────────────────────────────────────────┐
│                                                   │
│   📱 请扫码登录抖音账号                             │
│                                                   │
│      ┌─────────────────────┐                       │
│      │                     │                       │
│      │    [二维码图片]      │                       │
│      │                     │                       │
│      └─────────────────────┘                       │
│                                                   │
│   1. 打开抖音App → 我 → 右上角扫一扫                │
│   2. 扫描上方二维码                                 │
│   3. 点击"确认登录"                                 │
│                                                   │
│   ⏳ 等待扫码中...                                  │
│                                                   │
└─────────────────────────────────────────────────┘
```

### 二维码生成代码

```python
from douyin_browser import DouyinBrowser

browser = DouyinBrowser()
qr_result = await browser.get_qr_code_only()

# 返回二维码图片 (base64格式)
# 显示给用户让其扫码
```

### 登录确认

```python
# 等待用户扫码完成
login_result = await browser.login()

if login_result.success:
    print("✅ 登录成功！")
    # session 已保存，后续请求自动使用登录态
else:
    print("❌ 登录失败，需要重试")
```

---

## 第2步：浏览器自动浏览

登录成功后，使用 Playwright 启动真实浏览器，模拟你的账号操作。

### 可执行的操作

| 操作 | 说明 |
|------|------|
| 打开视频页面 | 自动播放，提取完整数据 |
| 滚动页面 | 加载更多内容（评论区等） |
| 搜索内容 | 站内搜索（用你的账号） |
| 访问用户主页 | 查看粉丝、关注、作品列表 |
| 浏览话题页 | 查看话题下的热门视频 |

### 浏览器控制代码

```python
# 打开视频页面
await page.goto("https://www.douyin.com/video/734276823912...")

# 等待视频加载
await page.wait_for_selector('.video-container', timeout=10000)

# 滚动加载评论区
await page.evaluate('window.scrollBy(0, 500)')
await page.wait_for_timeout(2000)

# 等待评论区加载
await page.wait_for_selector('.comment-list', timeout=5000)
```

---

## 第3步：提取并总结内容

登录后可以提取**完整**的视频数据。

### 完整数据字段

| 字段 | 未登录 | 登录后 |
|------|--------|--------|
| 标题 | ✅ | ✅ |
| 作者 | ✅ | ✅ |
| 发布时间 | ⚠️ 可能缺失 | ✅ |
| 视频描述 | ✅ | ✅ |
| 话题标签 | ✅ | ✅ |
| **播放量** | ❌ | ✅ |
| **点赞数** | ❌ | ✅ |
| **评论数** | ❌ | ✅ |
| **转发数** | ❌ | ✅ |
| **评论区内容** | ❌ | ✅ |

### 数据提取代码

```python
# 获取视频完整信息
video_info = await browser.get_video_info("https://www.douyin.com/video/xxx")

print(f"""
📹 视频信息
─────────────────────────────────
标题: {video_info.title}
作者: @{video_info.author}
播放: {video_info.plays}
点赞: {video_info.likes}
评论: {video_info.comments}
转发: {video_info.shares}
话题: {' '.join(video_info.hashtags)}
""")
```

---

## 使用场景示例

### 场景1：查看视频详情

```
用户: "帮我看看这个视频 https://www.douyin.com/video/xxx"

助手:
1. 检查是否已登录
2. 未登录 → 生成二维码让用户扫码
3. 登录后 → 打开视频页面 → 提取完整数据 → 呈现
```

### 场景2：搜索并总结

```
用户: "搜索抖音上的美食教程视频"

助手:
1. 确保已登录
2. 在抖音站内搜索"美食教程"
3. 提取前10个视频的：标题、作者、播放量、点赞数
4. 整理成列表呈现
```

### 场景3：查看用户主页

```
用户: "查看这个抖音用户的主页 https://www.douyin.com/user/xxx"

助手:
1. 确保已登录
2. 打开用户主页
3. 提取：昵称、简介、粉丝数、关注数、作品列表
4. 呈现完整用户画像
```

### 场景4：获取视频评论

```
用户: "看看这个视频的评论 https://www.douyin.com/video/xxx"

助手:
1. 确保已登录
2. 打开视频页
3. 滚动加载评论区
4. 提取：评论内容、点赞数、用户昵称
5. 整理成评论列表
```

---

## 完整Python使用示例

```python
from douyin_browser import DouyinBrowser

async def browse_douyin():
    # 初始化浏览器
    browser = DouyinBrowser()

    # 第1步：扫码登录
    print("正在生成登录二维码...")
    qr = await browser.get_qr_code_only()

    # 展示二维码给用户（在你的界面显示）
    display_qr_code(qr.qr_code_base64)

    # 等待用户扫码
    login_result = await browser.login()

    if not login_result.success:
        print("登录失败，请重试")
        return

    print("🎉 登录成功！")

    # 第2步：浏览视频
    video_info = await browser.get_video_info(
        "https://www.douyin.com/video/734276823912..."
    )

    # 第3步：总结呈现
    summary = f"""
## 📹 视频总结

**标题**: {video_info.title}
**作者**: @{video_info.author}
**发布时间**: {video_info.publish_time}

### 📊 数据统计
| 指标 | 数值 |
|------|------|
| 播放量 | {video_info.plays} |
| 点赞数 | {video_info.likes} |
| 评论数 | {video_info.comments} |
| 转发数 | {video_info.shares} |

### 🏷️ 话题标签
{' '.join(video_info.hashtags)}

### 📝 视频描述
{video_info.description}
"""

    print(summary)

    # 关闭浏览器
    await browser.close()
```

---

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    用户视角                               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   你的手机 (抖音App)  ←── 扫码授权 ──→  助手界面 (二维码)  │
│                                                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    Playwright 浏览器                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   ┌─────────────────────────────────────────────────┐    │
│   │  douyin.com (以你的账号登录)                      │    │
│   │                                                  │    │
│   │   - 视频播放                                     │    │
│   │   - 评论加载                                     │    │
│   │   - 用户主页                                     │    │
│   │   - 话题浏览                                     │    │
│   │   - 站内搜索                                     │    │
│   └─────────────────────────────────────────────────┘    │
│                                                          │
│   Session Cookies (登录态保存)                            │
│                                                          │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                    数据提取层                             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   - 完整视频数据 (播放量、点赞、评论、转发)                 │
│   - 用户信息 (粉丝、关注、作品数)                          │
│   - 评论内容 (评论文本、用户、点赞)                        │
│   - 话题信息 (参与人数、热门视频)                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Session 管理

### 登录状态持久化

```python
# 登录后，cookies 自动保存到 session.json
# 下次使用无需重新扫码

browser = DouyinBrowser()

if browser.is_logged_in():
    print("✅ 已登录，直接使用")
    # 直接开始浏览
else:
    print("❌ 未登录，需要扫码")
    # 生成二维码让用户扫码
```

### 登录状态检查

```python
# 检查是否在有效登录期内
session = browser.check_session()
if session.is_valid():
    # 使用现有 session
    pass
else:
    # session 过期，需要重新扫码
    pass
```

---

## 错误处理

| 情况 | 处理方式 |
|------|----------|
| 二维码生成失败 | 重试或提示用户 |
| 用户未扫码超时 | 重新生成二维码 |
| 页面加载失败 | 重试或换用备用方式 |
| 被抖音风控 | 降低操作频率 |
| Session 过期 | 自动提示重新登录 |

---

## 触发短语

- "我要看抖音" / "I want to browse Douyin"
- "扫码登录抖音" / "scan to login Douyin"
- "帮我看看这个视频" / "check this video"
- "搜索抖音内容" / "search Douyin"
- "抖音视频总结" / "summarize Douyin video"
- "查看抖音评论" / "view comments"
- "抖音用户主页" / "Douyin user profile"

---

## 文件结构

```
douyin-video-browser/
├── SKILL.md                     # 本文件
├── _meta.json                   # {"id": 1731, "version": "2.0.0"}
├── scripts/
│   ├── douyin_browser.py        # Python 浏览器自动化 (推荐)
│   └── douyin-browser.js        # Node.js 版本
└── references/
    └── quick-start.md          # 快速开始指南
```
