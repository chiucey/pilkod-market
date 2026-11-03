---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: acdaf7c2c7297bb2c237ed67f02fcdd2
    PropagateID: acdaf7c2c7297bb2c237ed67f02fcdd2
    ReservedCode1: 3046022100988a39910cecbb3c2c58ee5563f70c0d11c3001a73269ea84f210594918a93f30221008bd0660cdca1e958fbb2a75ec13af5b48334d3d2134b3953c6c5d5aae6d628e0
    ReservedCode2: 304502207f4490f9d3d79c476c7b0fb3e750f55f991278784e5c9e71abb2da0028be4831022100d80194c4346c8fec49fcec1665df7732da266431551b73d772a96ae85642248f
---

# emf-research 东方财富研报搜索

## 功能说明

基于东方财富公开接口的研报数据搜索工具，纯Node.js实现，无需登录/付费/Selenium。

## 文件说明

- `scripts/research_emf.js` — 主工具，支持关键词搜索+多页抓取+结果保存
- `scripts/research_downloader_v2.js` — 扩展版（含萝卜/慧博/东方财富三合一，降级方案）

## 使用方法

### 基本搜索（推荐）
```bash
node /workspace/skills/emf-research/scripts/research_emf.js <关键词> [最大页数]
```

示例：
```bash
node /workspace/skills/emf-research/scripts/research_emf.js 光模块 2
node /workspace/skills/emf-research/scripts/research_emf.js AI算力 3
node /workspace/skills/emf-research/scripts/research_emf.js 中际旭创 1
```

### 输出
- 搜索结果同时输出到终端
- JSON格式保存到 `/workspace/emf_search_results.json`
- 每条记录包含：标题、机构名、发布日期、链接

## 注意事项
- 仅限东方财富平台公开数据
- 关键词搜索精度受页面JS限制，建议精确到个股名称或细分行业
- 最多5页，每页约50条记录

## 来源
数据来源：东方财富（eastmoney.com）公开研报页面，2026-05-12验证可用。
