---
module: self-evolution/coverage-gap-detector
title: 缺口识别
cesium_version: N/A (适用范围:全部版本)
last_verified: 2026-09-22
status: stable
---

# 缺口识别(Coverage Gap Detector)

> 当本参考文档**无法回答你的问题时**,如何处理:
> 1. 识别缺口类型
> 2. 给出**立刻可用的兜底**
> 3. 把缺口登记为待办

---

## 一、缺口分类

| 类型 | 描述 | 兜底策略 |
|---|---|---|
| **API 缺失** | 某 API 没在 `api-quick-ref.md` | 直接查官方 ref-doc |
| **场景缺失** | 某业务场景没在 `modules/07` 或 `recipes/` | 临时组合现有模块 + 官方文档 |
| **版本过期** | CesiumJS 升级后 API 变化 | 跑 `maintenance-playbook.md` 的版本对齐任务 |
| **国产封装细节** | mars3d/SuperMap 的内部 API | 查封装官方文档 |
| **链接失效** | `official-sites.md` 链接 404 | 走 web_archive.org 查快照 |
| **本技能整体过期** | 整个框架过时 | 重新生成(参考 `SKILL.md` 顶部的生成 prompt) |

---

## 二、识别流程

```
用户问题 X
    ↓
搜本技能(modules / recipes / references / self-evolution)
    ↓
找到?→ 加载对应章节 + 实施
    ↓ 没找到
走兜底路径 ↓
```

---

## 三、兜底路径(按推荐度排序)

### 1. 官方文档(必查)

| 用途 | 链接 |
|---|---|
| API 完整参考 | [cesium.com/learn/cesiumjs/ref-doc](https://cesium.com/learn/cesiumjs/ref-doc/) |
| 教程 | [cesium.com/docs/tutorials](https://cesium.com/docs/tutorials/) |
| Sandcastle 示例 | [sandcastle.cesium.com](https://sandcastle.cesium.com/) |
| 官方博客 | [cesium.com/blog](https://cesium.com/blog/) |

### 2. Cesium 论坛

[community.cesium.com](https://community.cesium.com/) — 搜索你的问题,大概率有解答。

### 3. GitHub Issues / Discussions

[github.com/CesiumGS/cesium](https://github.com/CesiumGS/cesium) — Issues 里有大量踩坑记录。

### 4. 中文社区

- [osgeo.cn](https://osgeo.cn/) — 中文 GIS 社区
- CSDN / 掘金 — 搜 "cesium + 你的问题"
- 知乎 — cesium 相关专栏

### 5. Awesome Cesium

[github.com/reed-soul/awesome-cesium](https://github.com/reed-soul/awesome-cesium) — 资源聚合清单。

---

## 四、缺口登记模板

发现缺口时,**立刻登记到下面的待办清单**,不要指望记住。

```markdown
### 缺口:[场景/API 名称]

- **登记日期**:YYYY-MM-DD
- **缺口类型**:API 缺失 / 场景缺失 / 版本过期 / 国产封装细节
- **当前兜底**:用 X API 实现 / 参考 Y 博客
- **建议补齐**:
  - 模块:`modules/NN-xxx.md` 或 `recipes/xxx.md`
  - 关联 API / 文档链接
- **优先级**:高 / 中 / 低
```

---

## 五、当前已登记缺口

> 维护者会在每次会话结束时把"我发现本技能没覆盖的内容"登记到这里。

| 缺口 | 类型 | 优先级 | 状态 |
|---|---|---|---|
| WebGPU 后端配置 | API 缺失 | 中 | 待补 |
| Gaussian Splatting 加载 | 场景缺失 | 中 | 待补 |
| Cesium for Unreal / Unity / Godot 集成 | 场景缺失 | 低 | 待补 |
| Cesium Native(C++ 库)使用 | 场景缺失 | 低 | 待补 |
| 3D Tiles 2.0(草案) | 版本过期 | 高 | 待 3D Tiles 2.0 草案发布 |
| Cesium ion 自托管替代清单 | 场景缺失 | 中 | 部分在 modules/08 |
| mars3d 内部 API 速查 | 国产封装细节 | 中 | 部分在 modules/08 |
| Vue 2 + Cesium 老项目集成 | 场景缺失 | 低 | 待补 |
| 微前端(qiankun/micro-app)集成细节 | 场景缺失 | 低 | 部分在 modules/06 |
| Cesium 国际化(i18n)方案 | 场景缺失 | 低 | 待补 |
| ~~MVT 矢量瓦片加载~~ | ~~场景缺失~~ | ~~高~~ | ✅ **v1.1.0 已补**:`modules/02 § 2.6` + `recipes/load-mvt.md` |
| ~~Cesium for Unreal / Unity / Godot 集成~~ | ~~场景缺失~~ | ~~低~~ | ✅ **v1.2.0 已补**:`modules/10-cesium-for-unity.md` (Unity v1.24.0) + `modules/11-cesium-for-unreal.md` (Unreal v2.28.0)。Godot 集成待补。 |

---

## 六、缺口解决 SOP(给维护者)

当要补一个缺口时:

1. **明确缺口**:从上面的待办清单或新发现的问题
2. **检索权威源**:用 `web_search` + `web_fetch` 查 cesium.com / 论坛 / 博客
4. **选择模块位置**:
   - 单一概念 / API → `references/api-quick-ref.md` 增补 + 模块加章节
   - 完整业务场景 → 新建 `recipes/<name>.md`
   - 通用模式 → 加到 `modules/<N>.md` 对应章节
5. **按 `extension-contract.md` 编写 frontmatter**
6. **更新本文件"已登记缺口"的状态**
7. **在 `changelog.md` 加一条变更记录**

---

## 七、对外"快速回答"模板

当用户问的问题本技能覆盖时,**直接给出答案**;当不覆盖时:

```
"这个问题目前本参考文档未覆盖。建议查 [官方文档链接] / [Sandcastle 示例]。
我先把这个问题登记为待补缺口,下次升级时补上。

要不要我先基于 [相关模块] + [相关官方示例] 给你拼一个临时方案?"
```

不要假装覆盖了,也不要让用户自己 Google。

---

## 八、不能兜底的场景

| 场景 | 说明 |
|---|---|
| 项目级 bug | 走 [Cesium Forum](https://community.cesium.com/) |
| 商业支持 | 联系 [Cesium ion 商业支持](https://cesium.com/contact/) |
| 法律问题 | 走 `pkulaw` skill 或律师 |

---

## 九、主动自检(由脚本驱动)

> v1.3.0 起,本技能已配备**自动缺口自检**机制。

### 9.1 自检脚本

```bash
bash scripts/check-coverage.sh
```

输出:
- 待补缺口数量
- coverage-gap-detector.md 的陈旧度(> 90 天报警)
- 核心 recipes 清单是否齐全
- api-quick-ref.md API 数量
- 三大引擎集成模块是否齐全

### 9.2 自检触发

- **每周**:`.github/workflows/weekly-health.yml` 自动跑(check-coverage.sh 子任务)
- **GitHub Actions UI**:手动触发查看详细输出
- **本地**:跑 `bash scripts/check-coverage.sh` 立即检查

### 9.3 自检发现的"应补未补"

脚本会扫描:
1. `coverage-gap-detector.md` 已登记缺口(§ 五)
2. 本技能实际模块 / recipes 覆盖情况
3. `last_verified` 字段是否过期(> 90 天)
4. 三大引擎集成(Unity / Unreal / Omniverse)是否齐备

**输出**:`WARN: 1 项 — 待补缺口 > 5` / `FAIL: 1 项 — coverage-gap-detector.md 缺失`

---

## 十、重新生成本技能

如果整个技能框架都过期了(例如 CesiumJS 出现重大架构变更),参考 `SKILL.md` 顶部的"生成 Cesium 综合技能参考大全的提示词",重新跑一次完整生成流程。

但**优先**:修补单点缺口,而不是整体重生成。

---

## 十一、与 `scripts/check-coverage.sh` 的协同

| 触发 | 行为 |
|---|---|
| 用户在会话中发现缺口 | 维护者直接登记到 § 五,然后跑 `bash scripts/check-coverage.sh` 验证 |
| GitHub Actions 跑周检查 | `.github/workflows/weekly-health.yml` → 自动跑 check-coverage.sh → 失败时建 Issue |
| 季度 baseline 对齐 | 抓官方最新 release,如果新增功能不在本技能覆盖,自动登记为缺口 |
| 用户问"X 怎么做?"找不到答案 | 维护者:登记 § 五 + 把兜底路径(§ 三)用上,告知用户已登记 |