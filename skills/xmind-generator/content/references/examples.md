# XMind Generator - Usage Examples

## Basic Usage

### 1. Simple Mind Map from Markdown

```bash
python xmind_generator.py \
  --title "项目计划" \
  --markdown "# 项目计划\n## 需求分析\n### 用户调研\n### 竞品分析\n## 设计阶段\n### UI设计\n### 架构设计" \
  --output project_plan.xmind
```

### 2. Complex Structure from JSON

```bash
python xmind_generator.py \
  --title "技术架构" \
  --topics architecture.json \
  --output tech_arch.xmind \
  --structure map
```

## Feature Examples

### Using Relationships (联系)

Connect two topics that aren't directly related:

```python
from xmind_generator import XMindGenerator

gen = XMindGenerator(title="项目分析")
gen.set_root("项目分析", {
    "topics": [
        {"title": "前端开发", "topics": [
            {"title": "React"}
        ]},
        {"title": "后端开发", "topics": [
            {"title": "Node.js"}
        ]},
        {"title": "数据库", "topics": [
            {"title": "PostgreSQL"}
        ]}
    ]
})

# Find topics and add relationship
frontend = gen.find_topic_by_title("前端开发")
backend = gen.find_topic_by_title("后端开发")

gen.add_relationship(
    end1_id=frontend.id,
    end2_id=backend.id,
    control_points={
        "0": {"x": 50, "y": -20},
        "1": {"x": 70, "y": 30}
    }
)

gen.save("project_relationship.xmind")
```

### Using Summaries (概要)

Add summary markers to highlight multiple topics:

```python
gen.add_summary(
    topic_id=summary_topic_id,
    range_str="(0,3)"  # Cover topics 0 to 3
)
```

### Using Notes (备注)

Add detailed notes to topics:

```python
topic = Topic(
    title="重要决策",
    notes={
        "content": "这是决策的详细说明...\n可以包含多行文本。",
        "type": "text"
    }
)
```

### Using Labels (标记)

Add visual labels to topics:

```python
topic = Topic(
    title="紧急任务",
    labels=["priority-high", "deadline-today"]
)
```

### Using Markers

Add task markers:

```python
topic = Topic(
    title="待办事项",
    markers={
        "task": {
            "status": "inProgress",
            "percent": 50
        }
    }
)
```

### Custom Text Formatting

Apply custom formatting to specific topics:

```python
from xmind_generator import TopicStyle, TextStyle

# Create a custom style for important topics
important_style = TopicStyle(
    text=TextStyle(
        font_size="18pt",
        font_weight="bold",
        color="#FF0000"
    ),
    shape_class="org.xmind.topicShape.ellipse",
    fill="#FFE4E1"
)

topic = Topic(title="核心功能", style=important_style)
```

## Layout Structures

### Logic Right (Default)

```python
gen = XMindGenerator(structure="logic.right")
```

### Tree Structure

```python
gen = XMindGenerator(structure="tree.right")
```

### Radial Map

```python
gen = XMindGenerator(structure="map")
```

### Timeline

```python
gen = XMindGenerator(structure="chronological.right")
```

## Theme Presets

### Rainbow (Default)

```python
gen = XMindGenerator(theme="rainbow")
```

### Fresh Green

```python
gen = XMindGenerator(theme="fresh")
```

### Ocean Blue

```python
gen = XMindGenerator(theme="ocean")
```

### Passion Red

```python
gen = XMindGenerator(theme="passion")
```

## Complete Example

```python
from xmind_generator import XMindGenerator

# Create generator with custom settings
gen = XMindGenerator(
    title="产品需求文档",
    structure="map",
    theme="ocean"
)

# Build the structure
gen.set_root("产品需求文档", {
    "topics": [
        {
            "title": "用户需求",
            "notes": {"content": "核心用户群体的需求分析", "type": "text"},
            "topics": [
                {"title": "用户画像"},
                {"title": "使用场景"},
                {"title": "痛点分析"}
            ]
        },
        {
            "title": "功能规划",
            "labels": ["priority-high"],
            "topics": [
                {
                    "title": "核心功能",
                    "markers": {"task": {"status": "inProgress", "percent": 60}},
                    "topics": [
                        {"title": "用户登录"},
                        {"title": "内容管理"}
                    ]
                },
                {"title": "扩展功能"}
            ]
        },
        {
            "title": "技术方案",
            "topics": [
                {"title": "前端架构"},
                {"title": "后端架构"},
                {"title": "数据库设计"}
            ]
        }
    ]
})

# Add a relationship
user_needs = gen.find_topic_by_title("用户需求")
features = gen.find_topic_by_title("功能规划")
gen.add_relationship(
    end1_id=user_needs.id,
    end2_id=features.id
)

# Save the file
gen.save("product_requirements.xmind")
```
