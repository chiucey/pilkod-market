# 微信公众号文章抓取工具

## 目录结构

```
wechat-article-fetcher/
│
├── SKILL.md                    # 技能说明文档（必需）
├── README.md                   # 快速开始指南
├── CHANGELOG.md                # 更新日志
├── package.json                # Node.js 包配置
├── requirements.txt            # Python 依赖
├── .gitignore                  # Git忽略文件
├── install.bat                 # Windows安装脚本
│
├── scripts/                    # 脚本目录
│   ├── fetch_article.py        # 主抓取脚本
│   ├── generate_docx.js        # Word生成脚本
│   └── check_env.py            # 环境检测脚本
│
├── config/                     # 配置目录
│   └── config.yaml             # 配置文件
│
├── examples/                   # 示例代码
│   ├── basic_usage.py          # 基本用法
│   └── batch_fetch.py          # 批量抓取
│
├── references/                 # 参考资料
│   └── wechat_structure.md     # 微信页面结构
│
└── assets/                     # 资源文件（可选）
    └── templates/              # Word模板
```

## 文件说明

### 核心文件

| 文件 | 说明 |
|------|------|
| `SKILL.md` | 技能说明文档，包含完整的使用说明 |
| `scripts/fetch_article.py` | 主抓取脚本，负责抓取文章和图片 |
| `scripts/generate_docx.js` | Word生成脚本，负责生成文档 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `config/config.yaml` | 主配置文件 |
| `package.json` | Node.js依赖配置 |
| `requirements.txt` | Python依赖配置 |

### 工具脚本

| 文件 | 说明 |
|------|------|
| `install.bat` | Windows一键安装脚本 |
| `scripts/check_env.py` | 环境检测脚本 |

### 示例代码

| 文件 | 说明 |
|------|------|
| `examples/basic_usage.py` | 基本使用示例 |
| `examples/batch_fetch.py` | 批量抓取示例 |

## 使用流程

```
1. 安装依赖
   └─> 运行 install.bat 或手动安装

2. 检测环境
   └─> python scripts/check_env.py

3. 抓取文章
   └─> python scripts/fetch_article.py "URL"

4. 查看输出
   └─> output/[文章标题].docx
```

## 输出文件

抓取完成后，`output/` 目录包含：

```
output/
├── [文章标题].docx        # Word文档
├── article_data.json      # 原始数据
├── images/                # 图片文件夹
│   ├── image_01.jpg
│   ├── image_02.jpg
│   └── ...
└── ocr_results.json       # OCR结果（如果启用）
```
