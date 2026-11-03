---
module: self-evolution/maintenance-playbook
title: 维护者手册
cesium_version: N/A (适用范围:全部版本)
last_verified: 2026-09-22
status: stable
---

# 维护者手册(Maintenance Playbook)

> 维护本技能参考文档的**周期性任务清单 + 操作 SOP + 自动化脚本 + GitHub Actions 配置**。
>
> **v1.3.0 升级**:从"维护者驱动"升级为"**脚本驱动 + CI 自动**"。维护者只需审阅 GitHub Issues 即可。

---

## 一、任务总览(自动化版)

| 频率 | 任务 | 自动执行 | 手动兜底 |
|---|---|---|---|
| **每周** | 基础健康检查(structure / frontmatter / 引用数 / 缺口) | `.github/workflows/weekly-health.yml` | `bash scripts/health-check.sh --quick` |
| **每月** | 链接存活批量检测 | `.github/workflows/monthly-links.yml` | `bash scripts/check-links.sh` |
| **每季度** | CesiumJS / Unity / Unreal 最新版本对齐检测 | `.github/workflows/quarterly-baseline.yml` | `bash scripts/check-baseline.sh` |
| **每季度** | 抓 release notes 产 diff | `.github/workflows/quarterly-baseline.yml` | `bash scripts/release-diff.sh` |
| **每半年** | Cesium Forum 高频踩坑 | 手动 | 查 [community.cesium.com](https://community.cesium.com/) |
| **按需** | 新缺口被发现时 | 手动 | 走 `coverage-gap-detector.md` 流程 |
| **按需** | CesiumJS 出现重大架构变化 | 手动 | 整体重生成 |

> ⚠️ **GitHub Actions 需要把仓库推到 GitHub 后才会生效**。本地开发期间可以手动跑 `scripts/*.sh`。

---

## 二、自动化脚本清单

```
scripts/
├── health-check.sh        # 一键 QC(structure + frontmatter + 链接 + 一致性)
├── check-baseline.sh      # 对比 SKILL.md 基线 vs 官方 latest release
├── check-links.sh         # 批量 HEAD 检测所有外链
├── check-coverage.sh      # 主动缺口自检
├── release-diff.sh        # 抓最近 N 个 release notes
└── install.sh             # 一键 git init + 装 git hooks
```

### 2.1 health-check.sh

```bash
bash scripts/health-check.sh                # 跑全部检查
bash scripts/health-check.sh --quick       # 只跑 1-4(快)
bash scripts/health-check.sh --json         # 输出 JSON 报告
```

**输出**:`PASS: X  WARN: Y  FAIL: Z`,有 FAIL 就退出码非零。

### 2.2 check-baseline.sh

```bash
bash scripts/check-baseline.sh              # 全部产品
bash scripts/check-baseline.sh --cesium     # 只查 CesiumJS
bash scripts/check-baseline.sh --unity      # 只查 Cesium for Unity
bash scripts/check-baseline.sh --unreal     # 只查 Cesium for Unreal
```

**对比规则**:基线主版本(如 `1.141`)vs GitHub latest tag(如 `1.145`),不等就报警。

### 2.3 check-links.sh

```bash
bash scripts/check-links.sh                          # 默认 5s 超时
bash scripts/check-links.sh --timeout=10             # 10s 超时
bash scripts/check-links.sh --output=link-check.log # 写到文件
```

**输出**:详细 HTTP 状态码 + 失效 / 重定向分类。

### 2.4 check-coverage.sh

```bash
bash scripts/check-coverage.sh
```

**检查**:
- coverage-gap-detector.md 的待补缺口数量
- 该文件陈旧度(> 90 天报警)
- 核心 recipes 是否齐全
- api-quick-ref.md API 数量是否充足

### 2.5 release-diff.sh

```bash
bash scripts/release-diff.sh --limit=10
```

**输出**:最近 N 个 release 的 tag + 日期。

### 2.6 install.sh

```bash
bash scripts/install.sh
```

**效果**:
- `git init`(若未初始化)
- 所有 `scripts/*.sh` 加可执行权限
- 装 `pre-commit` hook(每次 commit 自动跑 `health-check.sh --quick`)
- 首次 commit

---

## 三、月度任务:链接检查(已自动化)

### 自动路径

`.github/workflows/monthly-links.yml` 每月 1 号跑:
1. 批量 HEAD 检测所有外链
2. 检测到 404 / 5xx 自动创建 GitHub Issue
3. 详细报告作为 artifact 上传

### 手动路径

```bash
bash scripts/check-links.sh --output=link-check.log
# 看失效链接清单 → 更新 references/official-sites.md → 提交
```

### 处理

- `200`:OK
- `301/302`:跳转,手动跟到最终 URL 后更新
- `404`:从文档移除
- `5xx`:可能是临时,稍后重试

---

## 四、季度任务:CesiumJS 版本对齐(已自动化)

### 自动路径

`.github/workflows/quarterly-baseline.yml` 每季度第一天跑:
1. 抓 CesiumJS / Unity / Unreal 最近 10 个 release
2. 对比 SKILL.md 声明基线
3. 检测到版本差异自动创建 Issue 提醒维护者

### 手动路径

```bash
# 1. 看基线对齐
bash scripts/check-baseline.sh

# 2. 看 release notes diff
bash scripts/release-diff.sh --limit=10

# 3. 决策:是否更新基线?

# 4. 跑脚本自动更新(本技能手动改 frontmatter)
# 更新 SKILL.md cesium_baseline / cesium_for_unity_baseline / cesium_for_unreal_baseline
# 更新每个模块的 cesium_version

# 5. 在 changelog.md 加 v1.x.y → v1.x.z 对齐条目

# 6. 跑 health-check.sh 验证
bash scripts/health-check.sh
```

### 输出模板

```markdown
### [日期]:v1.X.Y → v1.X.Z 对齐

- 影响模块:[模块 1, 模块 2, ...]
- 关键变更:[API 新增 / 弃用 / 行为变化]
- 处理:[章节更新 / 标记 deprecated / 新增]
```

---

## 五、季度任务:Sandcastle 新示例检查

### 流程

1. 访问 [sandcastle.cesium.com](https://sandcastle.cesium.com/)
2. 浏览 "Featured" + "Recent" 示例
3. 评估每个新示例:
   - 是否覆盖了本技能还没涉及的场景?
   - 是否展示了本技能未涵盖的高级用法?
4. 命中 → 新建 `recipes/<name>.md` 或更新 `modules/<N>.md`
5. 没命中 → 跳过

### 输出

- 新增 recipes / 更新 modules
- 记录到 `changelog.md`

---

## 六、季度任务:国产封装 release 跟踪

### 监控对象

| 封装 | 仓库 |
|---|---|
| mars3d | [github.com/marsgis/mars3d](https://github.com/marsgis/mars3d) |
| SuperMap iClient3D | [github.com/SuperMap](https://github.com/SuperMap/iClient3D-for-WebGL) |
| DC-SDK | [dvgis.github.io/dc-sdk](http://dvgis.github.io/dc-sdk) |
| CesiumLab | [cesiumlab.com](https://www.cesiumlab.com/) |

### 流程

1. 抓每个仓库的 releases / blog
2. 对比 `modules/08-domestic-alternatives.md` 的描述
3. 更新版本号 / 新功能 / 弃用功能 / 选型建议

### 输出

- 更新 `modules/08-domestic-alternatives.md`
- 记录到 `changelog.md`

---

## 七、半年任务:Cesium Forum 高频踩坑

### 流程

1. 抓 [community.cesium.com](https://community.cesium.com/) 高频问题
2. 识别"反复出现"的话题
3. 对比 `modules/09-pitfalls-and-traps.md`
4. 新增条目 / 更新现有条目

### 输出

- 更新 `modules/09-pitfalls-and-traps.md`
- 记录到 `changelog.md`

---

## 八、按需任务:缺口补齐

走 `coverage-gap-detector.md` 第六节"SOP"的流程。

---

## 九、按需任务:整体重生成

触发条件:

- CesiumJS 出现重大架构变化(类似 ESM 拆分、@cesium/engine 包拆分)
- 3D Tiles 2.0 草案发布且与 1.1 差异巨大
- 国产封装发生重大并购 / 重写(参考 2024 Bentley 收购 Cesium)

操作:

1. 参考 `SKILL.md` 顶部的"生成 Cesium 综合技能参考大全的提示词"
2. 重新跑完整生成流程
3. 用新版本覆盖 `modules/`、`recipes/`、`references/`
4. 保留 `self-evolution/` 中的历史记录

---

## 十、质量检查清单(QC)— 自动化

> v1.3.0 起,QC 由 `scripts/health-check.sh` + GitHub Actions 自动跑。

### 10.1 结构完整性(自动)

由 `health-check.sh` 第 [1] 项检查:
- modules ≥ 11
- recipes ≥ 9
- references ≥ 3
- self-evolution == 4

### 10.2 Frontmatter 合规(自动)

由 `health-check.sh` 第 [2] 项检查:
所有 .md 必须以 `---` 开头。

### 10.3 链接数量(自动)

由 `health-check.sh` 第 [3] 项检查:
>= 50 条外部链接。

### 10.4 version 一致性(自动)

由 `health-check.sh` 第 [4] 项检查:
各模块 cesium_version 与 SKILL.md cesium_baseline 兼容。

### 10.5 过期标记(自动)

由 `health-check.sh` 第 [5] 项检查:
deprecated 状态文件数量。

### 10.6 缺口待办(自动)

由 `health-check.sh` 第 [6] 项检查:
coverage-gap-detector.md 待补缺口数量。

---

## 十一、维护者承诺(简化版)

> v1.3.0 起,大部分工作由脚本 + GitHub Actions 自动完成,维护者只需:
>
> - ✅ **每周**看一眼 GitHub Issues,审阅 weekly-health 创建的提醒
> - ✅ **每月**看 monthly-links 报告,修复失效链接
> - ✅ **每季度**审阅 quarterly-baseline 报告,决策是否升级基线
> - ✅ **按需**响应 coverage-gap-detector 的新缺口
> - ✅ 严格遵守 extension-contract.md 的模块挂载规范
>
> **不再需要**手动跑 curl / grep / 查 release notes。

---

## 十二、GitHub Actions 配置说明

```
.github/workflows/
├── weekly-health.yml         # 每周一 UTC 06:00
├── monthly-links.yml         # 每月 1 号 UTC 05:00
└── quarterly-baseline.yml    # 每季度第一天 UTC 06:00
```

### 12.1 启用条件

把仓库推到 GitHub 后,workflows 自动激活。

### 12.2 触发方式

- **自动**:按 cron 定时跑
- **手动**:GitHub Actions UI → 选择 workflow → "Run workflow"

### 12.3 失败处理

- 创建 GitHub Issue(自动)
- 上传 artifact 日志(可在 Actions 历史查看)
- 维护者审阅 → 修复 → 关闭 Issue

---

## 十三、本地 pre-commit hook

```bash
# 自动安装(由 scripts/install.sh 完成)
# 效果:每次 git commit 前自动跑 health-check.sh --quick
# 阻止条件:FAIL > 0

# 跳过 hook(紧急情况):
git commit --no-verify -m "..."
```

---

## 十四、版本

| 版本 | 日期 | 维护者 | 关键变更 |
|---|---|---|---|
| v1.0 | 2026-09-22 | Mavis | 初版,纯手册式 |
| **v1.3.0** | **2026-09-22** | **Mavis** | **升级为脚本驱动 + GitHub Actions 自动化** |

---

**下次维护日期建议**:2026-12-22(季度,可由 GitHub Actions 提醒)