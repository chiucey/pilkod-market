---
module: self-evolution/extension-contract
title: 模块挂载契约
cesium_version: N/A (适用范围:全部版本)
last_verified: 2026-09-22
status: stable
---

# 模块挂载契约(Extension Contract)

> 新增 / 修改任何模块文件时,**必须遵守的元数据 + 命名规范**。
> 违反契约的模块在加载时给出警告。

---

## 一、Frontmatter 标准

每个 `.md` 文件**必须**以 YAML frontmatter 开头:

```yaml
---
module: <编号>           # 模块编号,如 01、02、ref-01、recipe-01
title: <标题>            # 一行标题
cesium_version: <范围>    # 对应 CesiumJS 版本,如 1.124+ / 1.106+
last_verified: <YYYY-MM-DD>
source_url: [<url1>, <url2>, ...]   # 引用来源(数组)
status: stable | experimental | deprecated
---
```

---

## 二、字段说明

### `module`(必填,唯一)

格式:
- 数字编号:`01`、`02` ... `09`(对应 `modules/`)
- `ref-` 前缀:`ref-01`、`ref-02`(对应 `references/`)
- `recipe-` 前缀:`recipe-01`、`recipe-02`(对应 `recipes/`)
- `self-` 前缀:`self-changelog`、`self-coverage-gap-detector` 等(对应 `self-evolution/`)

### `title`(必填)

一行,简洁,不要句号。

✅ `距离 / 面积测量`
❌ `距离和面积测量`

### `cesium_version`(必填)

对应本模块涉及的 CesiumJS 版本范围:

- `1.124+` — 该版本及以上
- `1.106-1.123` — 版本区间
- `1.124+ (CesiumJS)` — 标注全名
- `N/A` — 不涉及特定版本(如架构图)

### `last_verified`(必填)

格式 `YYYY-MM-DD`,代表最近一次核验日期。

### `source_url`(可选但强烈推荐)

数组,引用本模块的主要权威源。原则:
- 至少 1 个官方源(cesium.com / GitHub / OGC)
- 国内源可选(mars3d / SuperMap)
- 失效链接按 `coverage-gap-detector.md` 处理

### `status`(必填)

| 值 | 含义 | 加载建议 |
|---|---|---|
| `stable` | 稳定,可信赖 | 直接加载 |
| `experimental` | 实验性,可能变更 | 谨慎参考,标注风险 |
| `deprecated` | 已过时 | 仅作历史参考 |

---

## 三、模块内容规范

### 章节结构

每个模块**建议**包含:

1. **元信息**(frontmatter)
2. **本模块覆盖** + **何时加载**(1 段)
3. **主要内容**(按主题分章节,使用 `##` 或 `###`)
4. **关键点**(⚠️ 注意事项)
5. **进一步阅读**(可选)
6. **下一步**(指向其他模块)

### 代码示例

```js
// ✅ 推荐:可独立运行的最小示例
viewer.entities.add({
  position: Cesium.Cartesian3.fromDegrees(116.4, 39.9),
  point: { pixelSize: 10 }
})

// ❌ 不推荐:省略关键部分
viewer.entities.add(...)
```

### 引用规范

```markdown
> 数据来源:[Corvus 100k tracks](https://corvusintell.com/blog/c2-systems/battlefield-visualization-performance)
```

引用必须可追溯到 `references/official-sites.md` 的链接。

---

## 四、命名规范

### 文件名

- `kebab-case.md`(全小写 + 短横线)
- `01-foundation.md` — 模块编号 + 主题
- `measure-distance.md` — recipes 用动词短语
- `ion-token-rotation.md` — recipes 用连字符

### 章节标题

- 标题层级 `##` > `###` > `####`,不要跳级
- 不要用纯数字标题

---

## 五、新模块挂载流程

### 步骤

1. **确认必要性**:检查 `coverage-gap-detector.md` 是否已登记,或新场景必要性
2. **选择路径**:
   - 业务场景 → `recipes/<name>.md`
   - 通用模式 → `modules/<N>.md`
   - 速查 → `references/`
   - 维护流程 → `self-evolution/`
3. **编写 frontmatter**(本契约第一节)
4. **编写内容**(本契约第三节)
5. **交叉引用**:在新模块的"下一步"中指向相关模块
6. **更新 `changelog.md`**:加变更记录
7. **更新 `coverage-gap-detector.md`**:把缺口状态改为"已补"

### 路径决策树

```
新内容是?
│
├─ 一个完整的业务场景(可运行代码)
│  └─ → recipes/
│
├─ 一个通用模式 / 决策框架
│  └─ → modules/
│
├─ 速查 / 术语 / 链接
│  └─ → references/
│
└─ 维护 / 自扩展机制
   └─ → self-evolution/
```

---

## 六、修改现有模块

修改时:

1. **保持 frontmatter**;若版本变化,更新 `cesium_version` 和 `last_verified`
2. **不要删除未过期章节**;标记为 deprecated 而非删除
3. **增加章节时**:在文件末尾追加,不要插队(保持 git diff 友好)
4. **更新 `changelog.md`**

---

## 七、版本升级时

当 CesiumJS 升 minor 版本时:

1. 检查每个模块是否受影响
2. 跑一次 `maintenance-playbook.md` 的"版本对齐"任务
3. 更新 `changelog.md` 的"版本对齐矩阵"
4. 标注已过期章节 `status: deprecated`

---

## 八、违规警告

加载时,如果发现:

- 缺 frontmatter → 警告
- `status: deprecated` → 提醒用户谨慎使用
- `cesium_version` 范围过期 → 提示升级到最新

### 8.1 自动违规检测(v1.3.0+)

```bash
# scripts/health-check.sh 已包含 frontmatter 检测
# pre-commit hook 每次 commit 跑 health-check.sh --quick
# .github/workflows/weekly-health.yml 每周跑完整版
```

触发条件:
- 缺 frontmatter → `FAIL`
- frontmatter 字段缺值 → `WARN`
- `status: deprecated` 出现在 stable 路径 → `WARN`
- `last_verified` 距今 > 365 天 → `WARN`

---

## 九、最佳实践示例

```yaml
---
module: 07
title: 典型场景 — 测量、剖面、淹没、轨迹回放、地下模式
cesium_version: 1.141+
last_verified: 2026-09-22
source_url: [https://cesium.com/learn, https://blog.csdn.net/pz890123/article/details/153009796, https://blog.csdn.net/sam99/article/details/154221315]
status: stable
---
```

这是一个**正确**的 frontmatter:
- ✅ `module` 数字编号
- ✅ `title` 简洁
- ✅ `cesium_version` 明确
- ✅ `last_verified` 日期格式正确
- ✅ `source_url` 数组,3 个来源
- ✅ `status: stable`

---

## 十、契约的演进

本契约本身也在 `self-evolution/` 下,如果未来需要修订:

1. 在 `changelog.md` 加变更
2. 同时更新 `maintenance-playbook.md` 的相关任务
3. 不要破坏现有模块的兼容性(frontmatter 字段要向后兼容)

---

**本契约版本**:v1.0(2026-09-22 初始)