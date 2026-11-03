---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 582513ee1f288e1ccd04b0cf7df30036
    PropagateID: 582513ee1f288e1ccd04b0cf7df30036
    ReservedCode1: 3045022100a25871a30900175d4c6e1cafaeb7ebfee6292679dc8d72983d3d2f0bb44f5e4d022058fc882b73074c925f6a03da562eabdff63762041b6a9cbd7ea4caa05173fe84
    ReservedCode2: 3044022043a26e27e41e4b2e73f75eedff0b2ab36a433d8d9211aa8030115f0890ef32db02205e855768007e1ced0db4a922ff75c33412926da7371a53f64d8954b4b859786a
description: 通用网页爬虫技能。当用户要求爬取网页内容、提取正文、获取链接图片、分析HTML结构、下载网页数据时使用。支持模式：full（完整）、content（仅正文）、links（仅链接）、images（仅图片）。
name: browser-crawler
---

# 通用浏览器爬虫技能

## 能力概述

本技能支持公开网页的内容爬取与解析，具备以下核心能力：

### 功能列表
- **URL 访问与页面获取** - 支持任意公开可访问网页
- **请求头伪装（UA）** - 自动构造浏览器请求头，模拟真实访问
- **超时与重试** - 可配置超时时间和重试次数，保证稳定性
- **正文智能提取** - 自动识别并提取页面主体内容
- **链接与图片采集** - 按需提取页面中的链接和图片资源
- **内容清洗与摘要** - 自动清洗HTML标签，生成内容摘要
- **结构化输出** - 返回标准化JSON格式结果

## 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| url | string | 是 | - | 目标网页地址 |
| mode | string | 否 | content | 提取模式：full/content/links/images |
| retry | number | 否 | 1 | 重试次数 |
| timeout | number | 否 | 10 | 超时时间（秒） |

### 模式说明
- **full** - 返回完整信息（标题、正文、链接、图片、摘要）
- **content** - 仅返回标题和正文内容
- **links** - 仅返回页面中的链接列表
- **images** - 仅返回页面中的图片列表

## 执行流程

```
1. URL 合法性校验
   ├── 检查协议（仅支持 http/https）
   ├── 检查域名格式
   └── 拒绝内网/敏感地址（localhost、127.0.0.1、192.168.x.x、10.x.x.x 等）

2. 构造浏览器请求头
   ├── User-Agent 伪装
   ├── Accept 头
   ├── Accept-Language 头
   └── Connection 头

3. 发起请求（自动重试）
   ├── 使用 extract_content_from_websites 工具
   ├── 等待响应或超时
   └── 记录状态码

4. HTML 结构解析
   ├── 提取 <title> 标签
   ├── 提取 <meta> 描述
   ├── 定位正文区域（<article>、<main> 或最大文本块）
   └── 收集链接和图片

5. 内容处理
   ├── 清洗 HTML 标签
   ├── 去除脚本和样式
   ├── 合并空白字符
   └── 生成摘要（取前200字符）

6. 返回结构化结果
```

## 输出格式

```json
{
  "title": "页面标题",
  "url": "原始URL",
  "content": "清洗后的正文内容",
  "summary": "内容摘要（前200字符）",
  "links": [
    {
      "text": "链接文本",
      "href": "绝对URL"
    }
  ],
  "images": [
    {
      "alt": "图片描述",
      "src": "图片URL"
    }
  ],
  "status": "success|fail",
  "msg": "状态消息或错误信息"
}
```

## 安全约束

### 允许访问
- 公开可访问的 HTTP/HTTPS 网页
- 无需认证的公开资源

### 禁止访问
- 需要登录的页面
- 包含个人隐私信息的页面
- 内网地址（localhost、127.0.0.1、192.168.x.x、10.x.x.x、172.16.x.x 等）
- 政府/军事内部系统
- localhost 及任何本地回环地址

### 反爬检测
- 遇到 403、503 等限制状态码
- 检测到验证码或登录页面
- 连续请求被拒绝

**处理方式**：遇到反爬措施立即停止，返回失败状态。

## 调用示例（实际场景）

### 场景 1：获取页面正文和摘要
```
获取 https://baike.baidu.com/item/Gitee/56133127  获取页面正文和摘要
```
**说明**：提取百度百科Gitee词条的完整正文内容和摘要

### 场景 2：获取指定章节内容并下载
```
获取 https://baike.baidu.com/item/Gitee/56133127  只获取发展历程正文，返回文档可以下载
```
**说明**：提取Gitee词条中"发展历程"章节的内容，保存为可下载文档

### 场景 3：获取榜单数据
```
获取 酷狗音乐排行榜top10，返回给我
```
**说明**：爬取酷狗音乐排行榜前10名歌曲信息，以列表形式返回

### 场景 4：获取表格数据并下载
```
爬取 https://config.net.cn/tools/ProvinceCityZipCode.html 只获取地区编码/地区名称数据，返回表格文件可以下载
```
**说明**：提取省市县区与邮政编码对照表，转换为CSV格式下载

---

**提示**：安装技能后，使用时可参考以上示例格式进行调用。

## 错误处理

| 错误类型 | 状态码 | 处理方式 |
|---------|--------|---------|
| URL 格式错误 | fail | 返回错误消息 |
| 连接超时 | fail | 根据 retry 重试 |
| HTTP 错误 | fail | 返回状态码 |
| 反爬限制 | fail | 立即停止 |
| 内容解析失败 | fail | 返回原始错误 |

## 技术依赖

- **extract_content_from_websites** - 网页内容提取（主要）
- **mcp__matrix__bash** - 辅助文件处理
- **mcp__matrix__html_to_pdf** - 可选：转换为PDF

## 约束规则

1. **仅支持公开页面** - 不能爬取需要认证的页面
2. **遵守 robots.txt** - 尊重网站爬虫协议
3. **禁止暴力爬取** - 控制请求频率
4. **遇到反爬停止** - 不强行突破限制
5. **返回可下载格式** - 支持 CSV、JSON、TXT 格式导出
