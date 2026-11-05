# 技术栈规范(2026-07-07 确认)

> **核心规则: Three.js 默认不启用,开始前必须询问用户是否应用"3D"模式,默认用纯 ECharts(2D)。**

---

## 一、推荐技术栈(可视化大屏 / 类似软件界面数据模块)

| 层级 | 技术 | 默认 |
|---|---|---|
| **核心框架** | React 19 + TypeScript | ✅ 默认 |
| **构建工具** | Vite (Rolldown 版本) | ✅ 默认 |
| **3D 可视化** | Three.js + @react-three/fiber + @react-three/drei | ⚠️ **默认禁用,需询问** |
| **数据可视化** | ECharts (5.x) + echarts-gl | ✅ 默认 |
| **地图/地理** | D3-geo + topojson / DataV GeoJSON | ✅ 默认 |
| **动画** | GSAP | ✅ 默认 |
| **样式** | Styled-components (或 Tailwind / 原生 CSS) | ✅ 默认 |
| **调试** | Leva (控制面板) | 可选 |
| **自适应** | autofit.js (基于容器尺寸的等比缩放) | ✅ 默认 |

---

## 二、**Three.js 启用规则**(硬性)

> **绝对禁止自作主张启用 Three.js**

### 默认行为
- **只用 ECharts + echarts-gl**(实现 8 大图表 + 中国地图 2D + 浮层面板)
- **不引入 React-Three-Fiber 等 3D 框架**
- 大屏纯 SVG/DOM/CSS 渲染,3D 效果靠 CSS transform

### 必须询问的触发点
当用户说以下任何一种话,**立即询问**:
- "要有 3D 立体感"
- "用 three.js 做"
- "做 3D 地球/3D 模型/3D 折线图"
- "想要酷炫的 3D 效果"
- "界面要有层次感的 3D 视差"

询问模板:
> "需要应用 3D 渲染吗?
> - 是 → 引入 React-Three-Fiber,会有立体感但稍重
> - 否 → 默认 2D(ECharts + CSS transform),轻量 + 全浏览器兼容
> 你选哪个?"

### 询问后处理
- **用户选"是"** → 加依赖 `@react-three/fiber @react-three/drei three`,加 WebGL 容器,注意性能
- **用户选"否"** → 保持纯 ECharts,2D 模式(见本技能 v1.x 默认实现)
- **用户没回答 / 不明确** → 默认 2D,在最终交付时再确认一次

---

## 三、为什么默认禁 Three.js

| 风险 | 描述 |
|---|---|
| **性能成本** | WebGL 上下文占用内存,移动端卡顿 |
| **兼容性** | 老浏览器 / iOS Safari 偶发白屏 |
| **复杂度** | 3D 灯光 / 相机 / 材质 / OrbitControls,代码量翻倍 |
| **测试困难** | 截图断言(Playwright)3D 比 2D 慢 3 倍 |
| **数据驱动难** | ECharts 已经覆盖了大部分 2.5D 视觉(透视、伪 3D) |

**结论**:95% 的数据可视化场景,**ECharts + CSS transform + 渐变 + 阴影** 已经足够表现出"高级感",不必动用真正的 3D 引擎。

---

## 四、技术栈备选清单

### 框架层
- **首选**: React 19 + TypeScript
- **备选**: Vue 3 + TypeScript / SvelteKit / Solid.js
- **禁用**: jQuery / 旧版 Backbone.js(技术债)

### 构建
- **首选**: Vite (5.x)
- **备选**: Rsbuild / Turbopack / Webpack 5

### 2D 图表(默认)
- **首选**: ECharts 5.4.3 + echarts-gl 2.0.9
- **备选**: Chart.js / Recharts / D3 / AntV G2

### 地图
- **首选**: ECharts geo + DataV china.json(本地)
- **备选**: Mapbox GL / Leaflet / OpenLayers

### 3D(询问后才启用)
- Three.js + r3f + drei
- **禁止**: Babylon.js(过重) / Three.js 原生(无 React 集成)

### 动画
- **首选**: GSAP (轻量 + 强可控)
- **备选**: Framer Motion / react-spring
- **纯 CSS transform**: 简单场景用 CSS 即可,不引入动画库

### 样式
- **首选**: Styled-components (组件级封装)
- **备选**: Tailwind CSS (开发快但 CSS 类多) / 原生 CSS (本技能默认)
- **避免**: Sass/Less(冗余,现代 CSS 已够)

### 自适应
- **首选**: autofit.js (基于容器尺寸,1920×1080 缩放)
- **备选**: react-resize-detector / ResizeObserver

### 调试
- **Leva**: 数据调试面板(可拖动调整)
- **Vite Inspector**: 开发期组件调试

---

## 五、项目结构(基于 Vite + React + TS)

```
wind-dashboard/
├── index.html
├── vite.config.ts
├── package.json
├── tsconfig.json
├── src/
│   ├── main.tsx                      # 入口
│   ├── App.tsx
│   ├── components/                   # 业务组件
│   │   ├── Dashboard.tsx             # 总布局
│   │   ├── Header.tsx                # 头部
│   │   ├── MapPanel.tsx              # 中国地图
│   │   ├── Top10Chart.tsx            # 排行榜
│   │   ├── LineChart.tsx             # 双折线
│   │   ├── PowerLossTable.tsx        # 表格
│   │   ├── SummaryCards.tsx          # 总计 / 总设备 / 总员工
│   │   ├── QuarterChart.tsx          # 环形
│   │   ├── EquipmentChart.tsx        # 柱状
│   │   ├── Tabs.tsx                  # 底部 Tab
│   │   └── Marquee.tsx               # 跑马灯
│   ├── hooks/                        # 自定义 hooks
│   │   ├── useAutoFit.ts             # autofit.js 封装
│   │   ├── useChartLinkage.ts        # 联动逻辑
│   │   └── useMarquee.ts             # 跑马灯
│   ├── data/
│   │   └── province.ts               # 省份数据
│   ├── lib/
│   │   ├── echarts-theme.ts          # 注册 FYC theme
│   │   ├── linkage.ts                # 联动 API
│   │   └── fit-scale.ts              # 缩放脚本
│   └── styles/
│       ├── tokens.css                # CSS 变量
│       ├── theme.css                 # 全局样式
│       └── panel.css                 # 面板样式
├── public/
│   └── assets/
│       ├── echarts.min.js            # 本地化
│       ├── echarts-gl.min.js
│       ├── china.json
│       └── icons/                    # SVG 图标
└── scripts/
    └── self-check.ts                 # 自检脚本(可选)
```

---

## 六、依赖清单(package.json 范例)

```json
{
  "name": "fyc-wind-dashboard",
  "private": true,
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "self-check": "node scripts/self-check.ts"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "echarts": "^5.4.3",
    "echarts-gl": "^2.0.9",
    "gsap": "^3.12.0",
    "styled-components": "^6.1.0",
    "autofit.js": "^3.0.0",
    "leva": "^0.9.0"
    // ❌ 不要默认加 three / @react-three/fiber
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.3.0",
    "typescript": "^5.5.0",
    "@types/react": "^19.0.0"
  }
  // 询问后才加 @react-three/fiber / three
}
```

---

## 七、本项目稳定决策(可作为模板)

按本项目风格,首次交付可决策清单:

- ✅ React 19 + TypeScript + Vite
- ✅ ECharts 5.4.3 + echarts-gl 2.0.9(本地化)
- ✅ Styled-components(组件级 CSS-in-JS)
- ✅ GSAP(动画)
- ✅ autofit.js(自适应)
- ✅ Leva(开发期调试面板)
- ⚠️ D3-geo(可选,本项目用 ECharts geo 替代)
- ⚠️ Three.js(**默认不启用**)

---

## 八、ECharts vs Three.js 决策树

```
用户要 3D 立体感?
├── 否 → 默认 ECharts(2D + CSS transform)
└── 是 → 是真 3D 模型/场景/相机视角?
    ├── 否(只是视觉立体感) → ECharts map3D / bar3D / surface 即可
    └── 是 → Three.js(但**先确认**用户)
            ├─ 用户确认 → 加 r3f + drei
            └─ 用户拒绝 → 退而求其次用 ECharts 3D 系列
```

**重要**:ECharts 的 `map3D` / `bar3D` / `scatter3D` 跟 Three.js 是两回事。
- ECharts 3D 是**简化版 3D** (基于 WebGL,但只用 ECharts 自己的 API)
- Three.js 是**完整 3D 引擎**
- 默认配置里 **echarts-gl 已经是 ECharts 自带的 3D 能力**了,无需额外 Three.js

---

## 九、用户偏好速查

| 用户说 | 我的反应 |
|---|---|
| "做个大屏" | 默认 2D + ECharts,不加 Three.js |
| "复刻这张图" | 默认 2D + ECharts |
| "要 3D 立体感" | 询问: 是 ECharts 3D 还是 Three.js 真 3D? |
| "3D 地球" | 必须用 Three.js,告知是真正的 3D 引擎 |
| "粒子效果/动画" | 默认 GSAP,不动 Three.js |
| "做个数据可视化" | 默认 ECharts |
| "做个 Three.js demo" | 直接用 Three.js(用户明确指定) |

---

## 十、未来扩展(可加)

如果技术栈需要扩展,以下都"询问后才加":

- ⏳ React-Three-Fiber(必须 Three.js 才考虑)
- ⏳ WebGPU(替代 WebGL,目前兼容性差)
- ⏳ Web Worker(性能优化,大数据流时才考虑)
- ⏳ WebSocket / SSE(实时数据流,需用户场景需要)
- ⏳ Tauri(桌面化打包,仅当用户要本地桌面)

默认**不加**这些。每加一层,复杂度 + 兼容性测试工作量都翻倍。