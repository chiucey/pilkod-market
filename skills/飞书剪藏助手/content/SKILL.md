---
name: 飞书剪藏助手
description: 无论打开小红书、微信、微博还是B站，复制链接后发送给我，自动保存到飞书多维表格，自动分类打标签，智能分析爆款要素。
---

# 飞书剪藏助手 - Feishu Clipper

## 功能描述

当你对我说「**收藏飞书**」+ 任意链接时，自动执行以下流程：

1. **识别来源平台**（小红书/B站/微信/微博/抖音/其他）
2. **抓取内容**：标题、正文、标签、作者
3. **智能分析**：
   - 爆款要素分析
   - 未被满足的需求洞察
   - 评论特征分析
   - 内容缺陷/待优化点
4. **自动分类打标签**：根据内容特征自动分类
5. **幂等性检查**：基于链接URL去重，避免重复写入
6. **写入飞书多维表格**：包含所有分析字段

## ⚠️ 重要：防重复机制

**写入前必须检查链接是否已存在！**

检查逻辑：
1. 从链接中提取 note_id（如小红书的 `69edca56000000003601f40b`）
2. 查询飞书表格中所有记录的「链接」字段
3. 如果链接已存在，直接返回「已收藏」并显示原记录
4. 只有确认无重复后才写入

## 飞书配置

- **Base ID**: UBjfwr5agiiwl4k4dSzcx1vCnGg（Wiki Node Token）
- **App Token**: YnqrbN6w7axnhwsa6qxcH4fRnGh（真实多维表格Token）
- **Table ID**: tbl4hO51NKTZWZJ3
- **App ID**: cli_a97acba61dba9bde

## 飞书字段映射

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 剪藏标题 | 文本 | 文章标题 |
| 原始文案 | 文本 | 来源/作者/摘要 |
| 链接 | URL | 原始链接 |
| 分类标签 | 多选 | 平台/领域分类 |
| 话题标签 | 文本 | #话题标签 |
| 爆款要素 | 文本 | 爆款原因分析 |
| 未被满足的需求 | 文本 | 内容中挖掘的需求点 |
| 评论洞察 | 文本 | 评论特征/高赞评论类型 |
| 内容缺陷/待优化 | 文本 | 不足之处分析 |

## 执行步骤

### Step 1: 提取链接并识别平台

从用户消息中提取 URL，识别平台类型：

- `xiaohongshu.com` → 小红书
- `bilibili.com` → B站
- `weixin.qq.com` → 微信
- `weibo.com` → 微博
- `douyin.com` → 抖音

### Step 2: 抓取内容

**首选方案**：使用 `extract_content_from_websites` 工具提取网页内容

**备选方案**：
- B站视频：使用 `videos_understand` 工具
- 小红书：使用 `batch_web_search` 搜索补充信息

### Step 3: 智能分析

基于抓取到的内容，按爆款分析框架生成：
- 情绪价值 / 身份共鸣 / 信息密度 / 传播设计 / 视觉冲击

### Step 4: 幂等性检查（关键！）

**必须执行！** 使用 Python 脚本检查链接是否已存在：

```python
def check_duplicate(token, url):
    """检查链接是否已存在"""
    # 提取 note_id 或唯一标识
    note_id = extract_note_id(url)
    
    # 获取所有记录
    resp = requests.get(..., headers=headers)
    items = resp.json()['data']['items']
    
    # 检查链接字段
    for item in items:
        existing_link = item['fields'].get('链接', {}).get('link', '')
        if note_id in existing_link:
            return True, item['record_id']
    return False, None
```

### Step 5: 写入飞书

只有 `check_duplicate` 返回 `(False, None)` 时才写入。

## 技术要点

### Python 写入脚本模板

```python
import requests

def clip_to_feishu(title, summary, url, categories, tags, analysis):
    # 获取 token
    resp = requests.post(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
        json={'app_id': 'cli_a97acba61dba9bde', 'app_secret': 'dK1HZEbAaSWjCQYSsjap1cVVcWZssbFs'}
    )
    token = resp.json()['tenant_access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json; charset=utf-8'}
    
    # === 幂等性检查 ===
    note_id = extract_note_id(url)  # 提取唯一ID
    resp = requests.get(
        'https://open.feishu.cn/open-apis/bitable/v1/apps/YnqrbN6w7axnhwsa6qxcH4fRnGh/tables/tbl4hO51NKTZWZJ3/records?page_size=100',
        headers={'Authorization': 'Bearer ' + token}
    )
    items = resp.json()['data']['items']
    for item in items:
        existing_link = item['fields'].get('链接', {}).get('link', '')
        if note_id and note_id in existing_link:
            print(f'已存在: {title}')
            return False, item['record_id']
    
    # === 写入 ===
    data = {
        'fields': {
            '剪藏标题': title,
            '原始文案': summary,
            '链接': {'link': url, 'text': '点击查看'},
            '分类标签': categories,
            '话题标签': tags,
            '爆款要素': analysis['爆款要素'],
            '未被满足的需求': analysis['未被满足的需求'],
            '评论洞察': analysis['评论洞察'],
            '内容缺陷/待优化': analysis['内容缺陷/待优化']
        }
    }
    
    resp = requests.post(
        'https://open.feishu.cn/open-apis/bitable/v1/apps/YnqrbN6w7axnhwsa6qxcH4fRnGh/tables/tbl4hO51NKTZWZJ3/records',
        headers=headers,
        json=data
    )
    result = resp.json()
    if result['code'] == 0:
        return True, result['data']['record']['record_id']
    return False, None

def extract_note_id(url):
    """从URL提取唯一ID"""
    import re
    # 小红书: /discovery/item/xxxxxxxxxxxx
    match = re.search(r'/discovery/item/([a-zA-Z0-9]+)', url)
    if match:
        return match.group(1)
    # 其他平台类似处理
    return url  # 如果无法提取，用完整URL
```

## 平台说明

| 平台 | 链接特征 | 注意 |
|------|----------|------|
| 小红书 | `xiaohongshu.com/discovery/item/{note_id}` | 部分笔记需App访问，链接本身有效 |
| B站 | `bilibili.com/video/{bv_id}` | 可能有412风控 |
| 微信 | `weixin.qq.com/r/...` | 部分文章需登录 |

## 使用示例

```
用户: 收藏飞书 https://www.xiaohongshu.com/discovery/item/xxx

助手:
1. 识别：小红书笔记
2. 提取note_id: xxx
3. 幂等检查：查询飞书表格...
4. 如果已存在 → 返回「已收藏」
5. 如果不存在 → 抓取 → 分析 → 写入
6. ✅ 收藏成功
```
