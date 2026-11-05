# 使用示例

## 示例1：初始项目分析

**用户输入**：
```
帮我分析 /path/to/python-project 这个项目
```

**系统响应流程**：
1. 扫描项目目录结构
2. 读取README.md文件
3. 解析setup.py/pyproject.toml
4. 识别主入口点
5. 分析核心模块
6. 生成结构化分析报告

## 示例2：代码问答

**用户输入**：
```
这个项目中的DataProcessor类在哪里？它是做什么的？
```

**系统响应流程**：
1. 在项目中搜索`class DataProcessor`
2. 读取相关文件内容
3. 分析类的docstring和方法
4. 解释类的作用和主要方法
5. 展示关键代码片段

## 示例3：结合网络搜索

**用户输入**：
```
这个项目用了requests库，它是怎么处理HTTP请求的？
```

**系统响应流程**：
1. 在本地项目中搜索requests的使用方式
2. 分析代码中如何调用requests
3. 搜索requests官方文档获取API说明
4. 结合本地代码和网络资源给出完整解答

## 示例4：深度代码追踪

**用户输入**：
```
main.py中的process_data函数调用了哪些其他函数？
```

**系统响应流程**：
1. 读取main.py文件
2. 定位process_data函数
3. 分析函数体中的函数调用
4. 对每个被调用的函数进行递归追踪
5. 生成调用链图或列表

## 项目结构识别模式

### 常见Python项目结构

```
# 标准库项目
project/
├── README.md
├── setup.py
├── package/
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
└── tests/
    └── test_main.py

# Django项目
project/
├── manage.py
├── README.md
├── project/
│   ├── settings.py
│   └── urls.py
└── app_name/
    ├── models.py
    ├── views.py
    └── urls.py

# Flask项目
project/
├── README.md
├── app.py
├── requirements.txt
├── static/
└── templates/

# FastAPI项目
project/
├── README.md
├── main.py
├── requirements.txt
├── routers/
├── models/
└── schemas/
```

### 入口点识别

| 项目类型 | 入口文件 |
|----------|----------|
| CLI工具 | `__main__.py`, `cli.py`, `main.py` |
| Web应用 | `app.py`, `main.py`, `wsgi.py` |
| 库/包 | `__init__.py`, `__main__.py` |
| Django | `manage.py` |
| Flask | `app.py` 或 `__init__.py` |
| FastAPI | `main.py` |

### 依赖识别

**从代码中提取**：
```python
import pandas as pd
import numpy as np
from fastapi import FastAPI
```

**从配置中提取**：
- `requirements.txt`
- `setup.py` → `install_requires`
- `pyproject.toml` → `dependencies`
- `environment.yml`
