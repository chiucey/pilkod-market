---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: e828c155a563c1c2abffe75b96bd22c9
    PropagateID: e828c155a563c1c2abffe75b96bd22c9
    ReservedCode1: 304502204546b07fb57a2aaf9aef20eb87ad151bf31d0926dc00db997fbd593a4ac188ce022100965aaba03e8e5c9a663dae6ce0045ba21948d077f416d29ada7a14f48bd54736
    ReservedCode2: 3044022031ef0e81823ec5407c4c276abe3bace6632a9e1a4dabc65148c81b78a48f9801022047bbe214f7b87231e71b65a87159b180f1caf298952c5b2fe0136f66c4e7147c
description: 公众号文章排版与发布助手。当用户发送文章内容、博客链接或主题，要求排版并发布到微信公众号时使用。支持自动配图、HTML排版、微信公众号API发布。
name: wechat-article-publisher
---

# 公众号文章排版与发布助手

## 工作流程

### 1. 内容获取与解析

**触发条件**：用户投喂以下任一形式：
- 纯文本文章内容
- 博客/网页链接
- 文章主题和要点
- Markdown 格式内容

**执行步骤**：
1. 如果是链接，使用 `extract_content_from_websites` 获取内容
2. 如果是纯文本/主题，直接进入排版阶段
3. 提取标题、正文、关键段落

### 2. 智能配图

**规则**：
- 根据文章主题使用 `images_search_and_download` 搜索相关配图
- 优先选择高质量、无版权争议的图片
- 为文章生成封面图（可使用 `image_synthesize` 生成）
- 在适当位置插入文章配图

**图片处理**：
- 图片下载后使用 `images_understand` 确认内容相关性
- 统一图片格式为 jpg/png，大小优化

### 3. HTML 排版转换

**公众号排版规范**：
- 封面图尺寸：900 x 500 像素（或 2:1 比例）
- 正文章节标题使用 `h2`、`h3` 标签
- 段落之间留有适当间距
- 支持引用块、列表、代码高亮
- 字体大小建议：标题 18-20px，正文 16px

**排版模板**：
```html
<!-- 封面图 -->
<mpv type="cover" src="封面图片URL" />

<!-- 标题 -->
<h1>文章标题</h1>

<!-- 摘要 -->
<p class="summary">文章摘要...</p>

<!-- 正文章节 -->
<h2>章节标题</h2>
<p>正文内容...</p>

<!-- 配图 -->
<figure>
  <img src="图片URL" />
  <figcaption>图片说明</figcaption>
</figure>
```

### 4. 微信公众号发布

#### 4.1 前置准备

**获取凭证**：
1. 调用 `get_all_secrets` 检查是否已有微信公众号凭证
2. 必要凭证：`WECHAT_APP_ID`、`WECHAT_APP_SECRET`
3. 如无凭证，需要用户提供

**IP 白名单**：
- 微信公众号平台需要配置服务器 IP 白名单
- 获取当前出口 IP 并告知用户配置

#### 4.2 API 发布流程

**步骤一：获取 Access Token**
```
GET https://api.weixin.qq.com/cgi-bin/token
参数：grant_type=client_credential&appid={APPID}&secret={APPSECRET}
```

**步骤二：上传封面图**
```
POST https://api.weixin.qq.com/cgi-bin/media/uploadimg
参数：access_token={TOKEN}
表单：media (图片文件, ≤2MB, jpg/png)
返回：{ "url": "图片URL" }
```

**步骤三：创建草稿**
```
POST https://api.weixin.qq.com/cgi-bin/draft/add
参数：access_token={TOKEN}
```

**草稿 JSON 结构**：
```json
{
  "articles": [
    {
      "title": "文章标题",
      "author": "作者（可选）",
      "digest": "摘要，不超过54个字",
      "content": "<p>HTML格式的正文内容</p>",
      "content_source_url": "原文链接（可选）",
      "thumb_media_id": "封面图media_id",
      "need_open_comment": 1,
      "only_fans_can_comment": 0
    }
  ]
}
```

**步骤四：发布草稿**
```
POST https://api.weixin.qq.com/cgi-bin/freepublish/submit
参数：access_token={TOKEN}
表单：{ "media_id": "草稿media_id" }
```

#### 4.3 完整发布脚本

参考 `references/wechat_publish_script.py` 中的完整实现，包含：
- Access Token 自动刷新机制
- 图片上传与 URL 提取
- 草稿创建与发布
- 错误处理与重试机制

### 5. 发布确认

**成功反馈**：
- 展示文章预览链接
- 告知用户可在草稿箱中编辑
- 提醒发布后需微信审核（非即时生效）

**失败处理**：
- Token 失效：提示刷新凭证
- 接口限流：建议稍后重试
- 图片过大：提示压缩图片

## 输出格式

技能完成后，输出：
1. 排版后的 HTML 内容预览
2. 已上传的图片 URL 列表
3. 微信公众号草稿箱链接或发布状态

## 依赖工具

- `extract_content_from_websites`：网页内容提取
- `images_search_and_download`：配图搜索下载
- `image_synthesize`：封面图生成
- `images_understand`：图片内容验证
- `get_all_secrets`：凭证获取
- `mcp__matrix__bash`：执行 Python 发布脚本
