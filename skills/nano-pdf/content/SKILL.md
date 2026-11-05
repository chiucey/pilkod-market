---
name: nano-pdf
description: 轻量级PDF处理工具。当用户要求提取PDF文本、查看PDF元数据、合并PDF文件、拆分PDF、提取指定页面时使用。
---

# Nano PDF Skill

轻量级、无外部网络依赖的纯本地PDF处理技能，适配Minimax Agent。

## 核心功能

1. **PDF文本内容提取** - 从PDF中提取全部或指定页面的文本
2. **PDF元数据读取** - 获取标题、作者、页数、创建时间等信息
3. **PDF多文件合并** - 将多个PDF合并为一个文件
4. **PDF单文件按页拆分** - 将PDF拆分成单独页面
5. **PDF指定页面提取** - 从大PDF中提取特定页面范围

## 技术特性

- 无OpenClaw依赖
- 无外部网络请求
- 纯Python本地处理
- 基于pypdf官方库
- 支持标准PDF格式

## 使用方式

对话中直接触发：
- "提取这个PDF的文本"
- "查看PDF的元数据"
- "合并这几个PDF文件"
- "把PDF拆分成单独页面"
- "提取PDF的第1-5页"

## 权限说明

- **read:file** - 读取本地PDF文件
- **write:file** - 输出处理后的PDF/文本文件
- **network:false** - 禁止访问外部网络

## 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| max_merge_files | 20 | 最大合并文件数 |
| timeout_seconds | 60 | 处理超时时间 |
| default_output_directory | ./nano_pdf_output | 默认输出目录 |

## 依赖

- Python 3.8+
- pypdf >= 4.0.0
