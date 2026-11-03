---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 6a6b337abbc402f16158b39a6ae98762
    PropagateID: 6a6b337abbc402f16158b39a6ae98762
    ReservedCode1: 3046022100e113756f21b3a3a46cf89eda5c9f4b7464805b097273377ff8b334ccd85257c3022100f31482e6e4f48c13ca745a9ba2336dba56409cc10beea1c03bbd0d40e6e42ba2
    ReservedCode2: 3045022100e076cbc8035e2b65e6b394de52a3340796b73ee4eb5d19ed51ce474f44afeb7d0220190bbcf52892135d66af5cc902d87d1021f85a697c5f5fd5a734bad3cd4c32b5
description: 技能安全检查与风险扫描。当用户要求扫描技能、安全审计、技能安全、扫描技能风险、批量检查技能、技能安全审计、技能风险分析、技能查漏洞、安装前扫描、或任何涉及技能文件安全检查的请求时自动触发。支持安装前扫描和存量技能扫描，给出风险评分和详细报告。
name: skill-vetter-scan
---
# 技能安全检查器 (Skill-Vetter-Scan)

## 核心能力

自动扫描技能目录，对所有 Skill 文件进行安全审计、风险评分和安装建议。

## 扫描模式

### 1. 安装前扫描
在安装技能命令执行之前执行，检查目标技能目录，给出审查报告，阻止任何潜在的技能风险。

### 2. 存量技能扫描
对已安装的技能进行扫描，给出审查报告。

## 执行流程

### 第一步：定位技能目录

1. 首先检查 `/workspace/.minimax/skills/` 是否存在
2. 如果不存在，自动查找最新的技能安装目录
3. 如果找不到技能目录，输出提示并放弃执行

### 第二步：扫描文件

扫描以下文件类型：
- `.py` / `.json` / `.js` / `.yaml` / `.yml` / `.sh`

### 第三步：关键词匹配与评分

#### 可疑关键词库（分级扣分）

| 等级 | 关键词 | 扣分 |
|------|--------|------|
| 严重 | `eval(`, `exec(`, `os.system`, `subprocess.call`, `subprocess.run`, `__import__`, `importlib`, `pty.spawn` | -25 |
| 高危 | `requests.get`, `requests.post`, `urllib.request`, `http.client`, `socket.create_connection`, `curl`, `wget` | -20 |
| 中危 | `chmod`, `chown`, `sudo`, `chattr`, `ACL`, `passwd`, `shadow`, `/etc/passwd`, `.bashrc`, `.ssh/` | -15 |
| 低危 | `open(`+`write`, `base64`+`gzip`, `base64`+`zlib` 组合出现 | -5 |

#### 评分标准

| 风险评分 | 风险等级 | 颜色标记 | 建议 |
|----------|----------|----------|------|
| 81-100 | 低风险 | 绿色 | 允许安装 |
| 61-80 | 中风险 | 浅黄 | 谨慎安装，运行时监控 |
| 41-60 | 较高风险 | 黄色 | 沙箱测试，限制权限 |
| 21-40 | 高风险 | 橙色 | 禁止安装，查看源码 |
| 0-20 | 严重风险 | 红色 | 立即删除 |

### 第四步：生成报告

报告保存至：`/workspace/.minimax/技能安全检查报告.md`

## 输出格式

### 总览摘要
```
📊 安全检查报告 | 扫描时间: YYYY-MM-DD HH:MM
目录: /workspace/.minimax/skills/
共扫描: N 个文件 | 绿色 低风险: X | 浅黄 中风险: Y | 红色 高风险: Z

总体建议: [允许安装 / 需人工审核 / 建议撤下]
```

### 分文件结果
```
--- [文件名] ---
类型: [.py / .json / ...]
风险评分: XX/100 [颜色标记]
风险点:
  • [具体风险描述]
  • 若无风险则写: "未发现可疑代码"
建议: [允许安装 / 需审核 / 禁止]
```

### 汇总表
| 文件名 | 类型 | 风险分 | 等级 | 建议 |
|--------|------|--------|------|------|
| skill.md | markdown | 95 | 🟢 绿色 | 允许 |

## 安全原则

1. **零误报不拦截安装** — 仅提示风险，不自动禁止
2. **先审计后安装** — 风险分<40的文件，不输出任何安装指引
3. **不修改原文件** — 只读扫描，不触碰 skills 目录
4. **日志可追溯** — 每次扫描记录时间和结果

## 执行方式

使用 `/workspace/temp-skills/skill-vetter-scan/scripts/scan_skills.py` 执行扫描：

```bash
python /workspace/temp-skills/skill-vetter-scan/scripts/scan_skills.py [目标目录]
```

如果未指定目标目录，默认扫描 `/workspace/.minimax/skills/`
