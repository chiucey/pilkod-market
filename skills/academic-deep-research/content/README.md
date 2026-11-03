# academic-deep-research

适配 Minimax Agent | 无 OpenClaw 依赖 | 轻量化学术深度调研专用技能

## 核心简介

复刻 ClawHub kesslerio/academic-deep-research 原版学术深度研究核心逻辑，剥离所有OpenClaw私有依赖，纯原生Python开发，可一键导入Minimax Agent使用，适配学术开题、文献综述、课题深挖、前沿趋势分析等场景。

## 核心功能

- 多层级学术主题智能拆解（基础/中层/深度3级调研）
- 全学科通用结构化学术报告生成
- 研究背景/流派/痛点/未来趋势一站式梳理
- 支持自定义调研深度、多格式成果导出
- 原生网络权限，可对接公开学术数据源拓展

## 权限说明

- `read:file`：读取本地学术参考文件
- `write:file`：保存调研后的学术成果文档
- `network:true`：联网整合权威公开学术资料

## 环境依赖

- Python 3.8+
- requests >= 2.31.0
- pytest >= 7.4.0
- json5 >= 0.9.14

## 环境变量配置

| 变量名 | 说明 |
|--------|------|
| ACADEMIC_RESEARCH_API_KEY | 拓展学术检索接口密钥(可选) |
| RESEARCH_MAX_DEPTH | 全局最大调研深度(默认3) |

## 安装 & Minimax Agent导入

1. 完整下载 `academic-deep-research` 整个文件夹；
2. 在 Minimax Agent 后台 → 自定义技能 → 导入本地技能目录；
3. 按需修改 `config/settings.yaml` 配置参数；
4. 对话触发关键词：`学术深度研究`/`文献调研`/`课题深挖` 即可调用。

## 单元测试

```bash
cd academic-deep-research/tests
python test_main.py
```

## 适配场景

- 高校师生论文开题
- 科研工作者文献综述
- 企业研发行业学术调研
- 交叉学科前沿趋势分析
