# Deepseek API 调用参考

## API 概述

Deepseek API 提供强大的自然语言处理能力，可用于文案优化、翻译、内容生成等任务。

## 基本调用方式

### Python 调用示例

```python
import requests
import json

def call_deepseek_api(prompt, api_key, model="deepseek-chat"):
    """
    调用Deepseek API

    Args:
        prompt: 发送给API的提示词
        api_key: 您的API密钥
        model: 使用的模型名称，默认deepseek-chat

    Returns:
        API响应内容
    """
    url = "https://api.deepseek.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    except requests.exceptions.RequestException as e:
        return f"API调用失败: {str(e)}"


def optimize_listing_with_deepseek(original_data, api_key):
    """
    使用Deepseek优化listing文案

    Args:
        original_data: 包含原始listing数据的字典
        api_key: Deepseek API密钥

    Returns:
        优化后的数据字典
    """
    platform = original_data.get('platform', '')
    site = original_data.get('site', '')
    title = original_data.get('title', '')
    bullet_points = '\n'.join(original_data.get('bullet_points', []))
    keywords = original_data.get('keywords', '')
    description = original_data.get('description', '')

    # 构建优化提示词
    prompt = f"""请优化以下{platform} {site}产品的listing文案：

【原标题】
{title}

【原五点描述】
{bullet_points}

【原搜索关键词】
{keywords}

【产品描述】
{description}

请严格按照以下规则进行优化：

1. 标题优化规则：
   - 至少包含2个核心关键词
   - 将其中一个核心关键词前置后加逗号
   - 同样名词和词组不出现2次以上
   - 总字符控制在150左右
   - 如果原标题带括号内容，括号位置不变

2. 五点优化规则：
   - 语句通顺，符合美国人语言习惯
   - 避免重复介词和夸大产品性能
   - 不要有售后相关信息及价格描述
   - 需要埋入主关键词
   - 每一点要有小标题概括，小标题和内容之间用冒号隔开
   - 每一点写在同一行

3. 关键词优化规则：
   - 重复单词需要去重
   - 去重后控制在200-220个字符数（仅计算字母）
   - 关键词用空格隔开

4. 通用规则：
   - 剔除侵权词
   - 不要添加描述中不存在的认证信息
   - 如需换单位，数字需进行相应换算
   - 使用{site}站点语言（English）输出

请分别输出优化后的标题、五点描述和搜索关键词，格式如下：

标题：[优化后的标题]

五点：
1. [五点1]
2. [五点2]
3. [五点3]
4. [五点4]
5. [五点5]

关键词：[优化后的关键词]"""

    response = call_deepseek_api(prompt, api_key)

    # 解析响应
    return parse_optimization_response(response, original_data)


def parse_optimization_response(response_text, original_data):
    """
    解析Deepseek返回的优化结果

    Args:
        response_text: API返回的原始文本
        original_data: 原始数据（用于默认值）

    Returns:
        解析后的优化数据字典
    """
    result = {
        'platform': original_data.get('platform', ''),
        'site': original_data.get('site', ''),
        'title': '',
        'bullet_points': [],
        'keywords': '',
        'original': original_data
    }

    lines = response_text.strip().split('\n')

    current_section = None
    bullet_points = []
    keywords_line = None

    for line in lines:
        line = line.strip()
        if line.startswith('标题：') or line.startswith('Title:'):
            result['title'] = line.split('：')[-1].split(':')[-1].strip()
            current_section = 'title'
        elif line.startswith('五点：') or line.startswith('Bullet Points:'):
            current_section = 'bullets'
        elif line.startswith('关键词：') or line.startswith('Keywords:'):
            result['keywords'] = line.split('：')[-1].split(':')[-1].strip()
            current_section = 'keywords'
        elif line and current_section == 'bullets':
            # 处理五点列表
            clean_line = line.lstrip('0123456789.）) ').strip()
            if clean_line:
                bullet_points.append(clean_line)

    # 如果五点为空，使用原数据
    if not bullet_points and original_data.get('bullet_points'):
        result['bullet_points'] = original_data.get('bullet_points')

    return result
```

## 错误处理

### 常见错误及解决方案

| 错误类型 | 错误信息 | 解决方案 |
|---------|---------|---------|
| 认证失败 | Invalid API key | 检查API密钥是否正确 |
| 限流 | Rate limit exceeded | 等待后重试，或降低请求频率 |
| 超时 | Request timeout | 增加timeout参数值 |
| 内容过滤 | Content filtered | 修改提示词，避免敏感内容 |

### 重试机制

```python
import time

def call_with_retry(prompt, api_key, max_retries=3):
    """带重试机制的API调用"""
    for attempt in range(max_retries):
        try:
            result = call_deepseek_api(prompt, api_key)
            if not result.startswith("API调用失败"):
                return result
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # 指数退避
    return None
```

## 提示词优化技巧

### 1. 结构化提示

将优化规则清晰地分条列出，便于模型理解：
- 使用编号列表
- 明确量化要求（如字符数、关键词数量）
- 提供正面和负面示例

### 2. 上下文丰富

提供足够的产品信息：
- 产品类别和用途
- 目标市场和受众
- 竞争对手参考

### 3. 格式要求明确

指定输出格式：
- 使用什么分隔符
- 每部分内容的顺序
- 是否需要JSON格式

## 成本优化建议

1. **批量处理**：将多个产品的优化请求合并
2. **缓存结果**：避免重复优化相同内容
3. **选择合适模型**：简单任务使用轻量模型
4. **控制token数量**：精简提示词，避免冗余
