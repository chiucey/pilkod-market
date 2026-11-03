# 微信公众号爬取方法详解

## 为什么微信PC端反爬但手机端放行？

### PC端防护机制
1. **JS渲染**：内容通过JavaScript动态加载，无法直接获取HTML
2. **UA检测**：识别非主流浏览器
3. **Cookie/Session**：需要微信登录态
4. **行为检测**：鼠标轨迹、访问频率等

### 手机端特点
1. **轻量级HTML**：手机版优先考虑加载速度
2. **Header校验**：主要检查UA和Referer
3. **SEO友好**：部分内容直接嵌入HTML利于搜索引擎索引
4. **历史兼容性**：保持对老旧设备的兼容性

## 核心技术：HTTP请求头伪装

### 关键Header

| Header | 作用 | 示例 |
|--------|------|------|
| `User-Agent` | 模拟iPhone Safari | Mozilla/5.0 (iPhone; CPU iPhone OS 17_0...) |
| `Accept` | 声明可接受的响应类型 | text/html,application/xhtml+xml |
| `Accept-Language` | 声明语言偏好 | zh-CN,zh;q=0.9 |
| `Referer` | 模拟从搜索引擎跳转 | https://weixin.sogou.com/ |

### 多UA轮换策略

```python
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 ...",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 ...",
    "Mozilla/5.0 (Linux; U; Android 13; zh-cn; Pixel 7 Build/TP1A.220624.014) ...",
]
```

## og标签解析

微信文章会在HTML头部嵌入Open Graph元数据：

```html
<head>
    <meta property="og:title" content="文章标题" />
    <meta property="og:description" content="文章摘要" />
    <meta property="og:image" content="封面图URL" />
    <meta name="author" content="作者名称" />
    <meta name="publish_time" content="发布时间" />
</head>
```

## 常见问题与解决方案

### 1. 返回空白内容

**原因**：文章需要关注公众号才能阅读

**解决**：更换其他可公开访问的文章链接

### 2. 被拦截（返回页面不存在）

**原因**：请求频率过高或IP被封

**解决**：
- 添加延时：`time.sleep(2)`
- 使用代理IP池
- 更换网络环境

### 3. 编码问题

**原因**：微信返回的编码可能不标准

**解决**：
```python
# 自动检测编码
content = response.read()
charset = response.headers.get_content_charset() or "utf-8"
html = content.decode(charset, errors="replace")
```

## 进阶：批量爬取

```python
import time

def batch_scrape(urls):
    results = []
    for url in urls:
        try:
            article = scrape_wechat_article(url)
            results.append(article)
            time.sleep(3)  # 延时避免被封
        except Exception as e:
            print(f"失败: {url} - {e}")
    return results
```

## 法律与伦理提醒

1. **仅用于个人学习研究**，不要大规模商业爬取
2. **遵守robots.txt**和服务条款
3. **尊重版权**：爬取内容仅供学习，商用需授权
4. **保护隐私**：不要收集用户个人信息
