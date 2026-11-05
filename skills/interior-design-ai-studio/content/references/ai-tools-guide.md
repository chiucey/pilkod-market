# AI工具完整指南

## 一、AI绘图工具矩阵

### 1. Midjourney (专业级)
**适用场景**：商业级效果图、高端项目展示
**优点**：
- 风格一致性极强
- 细节表现优秀
- 社区参考丰富

**核心参数**：
```
--ar 16:9 (横版16:9)
--ar 3:4 (竖版3:4)
--ar 1:1 (方形)
--v 6 (版本6)
--style raw (写实风格)
--s 250 (风格化强度)
```

### 2. Stable Diffusion (开源免费)
**适用场景**：批量生成、风格微调、本地部署
**推荐模型**：
- Realistic Vision (写实风格)
- SDXL (高质量基础模型)
- Pony Diffusion (动漫/插画风格)

### 3. DALL-E 3 (GPT集成)
**适用场景**：快速原型、与ChatGPT联动
**优点**：
- 文字理解准确
- 与GPT生态无缝衔接
- 无需复杂提示词

### 4. Bing Image Creator (免费)
**适用场景**：初稿预览、快速灵感激发
**优点**：完全免费，基于DALL-E技术

## 二、AI视频生成工具

### 1. Runway Gen-4.5
**功能**：文字转视频、图片转视频、视频延伸
**参数**：
- Motion Strength (运动强度)
- Camera Motion (镜头运动)

### 2. Kling (可灵) - 国产
**适用场景**：中文提示词、国内平台适配
**优点**：中文支持好、生成速度快

### 3. Pika Labs
**适用场景**：创意短视频、动画制作

## 三、文案创作AI

### 1. Claude (Anthropic)
**优势**：
- 长文本理解能力强
- 结构化输出稳定
- 中文表达自然

### 2. ChatGPT-4o
**优势**：
- 多模态能力强
- 插件生态丰富
- 联网搜索实时

### 3. Kimi (国产)
**优势**：
- 长文本处理(20万字)
- 中文语境理解好
- 文件解读能力强

## 四、知识管理工具

### 1. Notion
**用途**：灵感库、项目管理、内容库
**AI功能**：
- Notion AI (总结、写作)
- 数据库自动归类

### 2. Obsidian
**用途**：知识图谱、个人知识库
**插件**：
- Dataview (数据查询)
- Templater (模板自动化)

## 五、提示词模板库

### 效果图生成模板

#### 奶油风客厅
```
室内设计效果图，奶油风格客厅，轻法式复古元素
色调：奶油白 #FFF8E7、燕麦色 #E8DFD0、浅木色 #C4A77D
材质：羊羔绒沙发、拱形门洞、哑光地砖
光线：下午自然光，柔和阴影
视角：30度俯视，广角镜头
--ar 16:9 --v 6 --style raw --s 200
```

#### 侘寂风卧室
```
Wabi-sabi风格卧室设计，极简主义
色调：米灰 #D4C5B0、原木 #8B7355、苔藓绿 #6B7B5C
材质：微水泥、藤编、亚麻织物
光线：散射光，温暖氛围
--ar 3:4 --v 6 --style raw
```

### 视频脚本模板

#### 前后对比视频
```
风格：装修前后对比
时长：15秒
节奏：
- 0-3秒：问题展示（旧貌）
- 3-6秒：过渡转场
- 6-12秒：解决方案展示（新貌）
- 12-15秒：品牌植入
运镜：推拉结合、特写细节
音乐：轻快正能量
```

#### 设计理念讲解
```
风格：知识分享型
时长：60秒
结构：
- 开头：痛点引入（5秒）
- 中间：设计理念讲解（45秒）
- 结尾：总结+互动引导（10秒）
要点：专业但不晦涩、图文配合、节奏适当
```

## 六、工作流串联方案

### 方案1：Zapier/Make自动化
```
触发：Notion添加新灵感
↓
动作1：自动生成标签分类
↓
动作2：同步到灵感素材库
↓
动作3：通知设计师审核
```

### 方案2：本地脚本串联
```python
# 示例：批量生成文案
import openai

def batch_copywrite(designs: list, style: str) -> list:
    """批量生成文案"""
    results = []
    for design in designs:
        prompt = f"""
        为以下设计方案生成小红书文案：
        {design['description']}

        要求：
        - 风格：{style}
        - 字数：400字左右
        - 包含热门话题标签
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        results.append(response.choices[0].message.content)
    return results
```

## 七、成本优化方案

### 免费工具组合（月成本：0元）
- Notion Free (知识管理)
- Bing Image Creator (绘图)
- CapCut (视频剪辑)
- Canva (平面设计)

### 专业套餐（月成本：约$50）
- Midjourney Basic ($10)
- Runway Pro ($35)
- Notion Plus ($8)
- Claude Pro ($20)

### 全功能套餐（月成本：约$150）
- Midjourney Pro ($30)
- Runway Unlimited ($95)
- Adobe Creative Cloud ($60)
- 专业知识管理工具
