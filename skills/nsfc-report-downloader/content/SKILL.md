---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 7a7df895d7ec903033681d537cfc10f4
    PropagateID: 7a7df895d7ec903033681d537cfc10f4
    ReservedCode1: 304502200d2fb5897f1ffd5e7f25b5680fe286dd3e29276f041df93c5601f5e03a2fc985022100da0bf06b3a85ec5162c0feaea67eb77688bedc49663a66d8f72b6fc1a681f916
    ReservedCode2: 3045022100a2f55162edc722bfa58a27658f8c699fd0b4a35464ffd3b3c88031e297e0e6380220092103429c4820da7a45305e2160ceddac19339ab2341e34a26f19e65e370ee2
description: 下载国自然（NSFC）结题报告并合成 PDF。当用户提供 NSFC 结题报告链接（如 https://kd.nsfc.cn/finalDetails?id=xxx）时使用此技能。自动处理 API 请求、图片下载、断点续传和 PDF 合成。
name: nsfc-report-downloader
---

# NSFC 结题报告下载器

自动下载国家自然科学基金委员会（NSFC）结题报告图片并合成 PDF 文件。

## 工作流程

### 1. 接收用户输入

接收 NSFC 结题报告链接或纯 ID：
- 链接格式：`https://kd.nsfc.cn/finalDetails?id={32位字符串}`
- 也支持直接提供 32 位 ID

### 2. 执行下载脚本

调用内置的 `nsfc_downloader.py` 脚本：

```bash
python3 scripts/nsfc_downloader.py <URL_OR_ID>
```

脚本功能：
- 自动解析链接中的 ID
- 创建分层目录结构 `/tmp/nsfc_download/{id}/{api,img}/`
- 调用 NSFC API 获取报告信息
- 按页下载报告图片（支持断点续传）
- 使用 img2pdf 无损合成 PDF
- 忽略 SSL 证书错误
- 自动处理 503 服务器繁忙状态

### 3. 返回结果

脚本执行完成后：
- 显示 PDF_GENERATION_COMPLETE 埋点日志
- 汇报：文件名、总页数、文件大小、存储路径
- 尝试将 PDF 移动到用户可访问的工作目录

## 脚本说明

- **路径**：`scripts/nsfc_downloader.py`
- **依赖**：requests, img2pdf（脚本自动安装）
- **缓存**：API 响应和图片文件会缓存到 `/tmp/nsfc_download/{id}/`
- **断点续传**：已下载的页面会自动跳过

## 触发短语

- "下载国自然结题报告"
- "下载 NSFC 报告"
- "下载基金结题报告"
- "帮我下载这个结题报告"
