# 微信公众号文章抓取工具 - 参考资料

## 微信公众号文章结构

### 普通文章
```
#js_content / .rich_media_content
├── 标题: #activity-name / .rich_media_title
├── 作者: #js_name / .rich_media_meta_nickname
├── 时间: #publish_time
├── 正文: #js_content
│   ├── 文字段落
│   ├── 图片 img[data-src] 或 img[src]
│   └── 其他元素
└── 评论: #js_cmt_area / .discuss_container
```

### 图片文章
```
#js_image_content / .image_content
├── 标题: .rich_media_title
├── 描述: #js_image_desc / .share_notice
└── 图片: img[src]
```

## 常用CSS选择器

### 文章信息
```css
/* 标题 */
#activity-name
.rich_media_title

/* 作者/公众号 */
#js_name
.rich_media_meta_nickname

/* 发布时间 */
#publish_time
.rich_media_meta_date

/* 正文 */
#js_content
.rich_media_content
#js_image_content

/* 图片描述 */
#js_image_desc
.share_notice
```

### 评论区
```css
/* 评论区容器 */
#js_cmt_area
.discuss_container

/* 单条评论 */
.discuss_item
.comment_item

/* 评论者 */
.discuss_sender
.comment_nickname

/* 评论内容 */
.discuss_message
.comment_content

/* 点赞数 */
.discuss_extra
.comment_like_num

/* 回复 */
.reply_item
```

## 图片URL格式

微信图片URL格式：
```
https://mmbiz.qpic.cn/mmbiz_jpg/.../0?wx_fmt=jpg
https://mmbiz.qpic.cn/sz_mmbiz_jpg/...
https://mmbiz.qpic.cn/mmbiz_png/...
https://mmbiz.qpic.cn/mmbiz_gif/...
```

参数说明：
- `mmbiz_jpg` - JPEG格式
- `mmbiz_png` - PNG格式
- `mmbiz_gif` - GIF格式
- `sz_mmbiz_jpg` - 深色模式图片
- `wx_fmt=jpg` - 指定输出格式

## 反爬机制与应对

### 1. User-Agent检测
使用真实浏览器的User-Agent：
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}
```

### 2. JavaScript渲染
使用Selenium/Playwright等工具渲染页面。

### 3. 动态加载
图片使用`data-src`属性，需要等待加载或触发滚动。

### 4. 频率限制
两次请求间隔 >= 2秒，避免触发限制。

## OCR工具对比

| 工具 | 中文支持 | 速度 | 准确率 | 安装难度 |
|------|---------|------|--------|----------|
| EasyOCR | ★★★★★ | ★★★ | ★★★★ | ★★★ |
| PaddleOCR | ★★★★★ | ★★★★ | ★★★★★ | ★★★★ |
| Tesseract | ★★★ | ★★★★★ | ★★★ | ★★ |
| Windows OCR | ★★★★ | ★★★★ | ★★★★ | ★ |

## Word文档结构

```
文档
├── 标题 (Heading 1)
├── 元信息表格
│   ├── 发布时间
│   ├── 作者
│   └── 原文链接
├── 文章标签 (Heading 2)
├── 正文内容 (Heading 2)
│   ├── 图片 (ImageRun)
│   ├── 图片编号
│   └── OCR文字
│   └── 分隔符
├── 评论区 (Heading 2)
│   ├── 评论者
│   ├── 评论内容
│   └── 回复
└── 文档信息
    ├── 抓取时间
    └── 生成工具
```

## 常见问题

### Q: 图片下载失败
A: 检查网络连接，尝试添加Referer头：
```python
headers = {'Referer': 'https://mp.weixin.qq.com/'}
```

### Q: OCR识别效果差
A: 尝试：
1. 使用更高清的图片
2. 尝试不同的OCR引擎
3. 对图片进行预处理（增强对比度等）

### Q: 评论获取不到
A: 部分文章评论需要登录，或评论区在页面下方需要滚动触发。

### Q: Word文档打开乱码
A: 确保使用UTF-8编码，字体设置为Microsoft YaHei。

## 相关资源

- [Selenium文档](https://selenium-python.readthedocs.io/)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
- [docx库](https://docx.js.org/)
- [微信公众号开发文档](https://developers.weixin.qq.com/doc/)
