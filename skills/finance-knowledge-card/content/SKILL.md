# 财务知识卡片生成 · SKILL.md

> 将任意财务/投资知识点生成为一张精美的卡片图片，风格统一：深蓝渐变 + 金色点缀。
> 只需修改 `cardsData.ts` 中的数据，重新构建部署，即可生成新知识点卡片。

---

## 适用场景

- 用户想生成某个财务/投资知识的卡片（如：杜邦分析、ROE、现金流折现、PE/PB 等）
- 需要生成小红书配图、公众号封面、分享图

---

## 已有项目

```
/workspace/finance-card/          ← React + Vite 项目（卡片源码）
/workspace/finance-card/dist/     ← 构建产物（已部署可直接访问）
```

---

## 如何生成新卡片（完整流程）

### 第一步：修改数据文件

编辑 `/workspace/finance-card/src/cardsData.ts`，替换 `cardData` 对象内容：

```typescript
export interface CardContent {
  badge: string          // 左上角标签，如"财务进阶"
  title: string          // 主标题，如"一张图读懂杜邦分析"
  subtitle: string       // 副标题
  formula: {
    items: { main: string; sub: string }[]   // 公式因子，如净利率、周转率、权益乘数
    result: { main: string; sub: string }    // 公式结果，如 ROE
  }
  columns: {
    icon: string
    title: string
    formula: string
    desc: string
  }[]
  example: {
    title: string
    leftCompany: { name: string; bars: { label: string; w: string }[]; roe: string }
    rightCompany: { name: string; bars: { label: string; w: string }[]; roe: string }
    insight: string
  }
  takeaway: { title: string; text: string }
}
```

**注意事项：**
- `columns` 固定 3 栏，对应公式三个因子
- `bars.w` 是百分比宽度（0%~100%）
- 保持金色风格：`badge`、`title`、图标数字等使用 `#d4a843` 金色
- 深蓝背景：`#0d1b2a` ~ `#1a2a4a`

### 第二步：构建项目

```bash
cd /workspace/finance-card
npm run build
```

### 第三步：部署

部署 dist 目录，生成公开 URL：

```bash
npx openclaw deploy /workspace/finance-card/dist
```

> 部署命令会自动上传并返回公开访问链接。

### 第四步：截图或分享

- 将部署后的链接发送给用户即可在浏览器查看
- 如需生成图片，可用 `canvas` tool 截图，或让用户截图保存

---

## 卡片视觉规范（设计师参考）

| 元素 | 颜色 / 样式 |
|------|------------|
| 背景 | `linear-gradient(160deg, #0d1b2a 0%, #1a2a4a 50%, #0d1b2a 100%)` |
| 主色调 | `#d4a843`（金色） |
| 强调文字 | `#fff`（白色） |
| 辅助文字 | `#8ba3c4`（灰蓝） |
| 卡片边框 | `rgba(212,168,67,0.3)` 半透明金色 |
| 圆角 | 卡片 `border-radius: 16px`；内元素 `border-radius: 10-14px` |
| 字体 | PingFang SC / Microsoft YaHei / sans-serif |

---

## 模板结构说明

每张卡片分为 5 个区块（从上到下）：

```
┌─────────────────────────────────┐
│  [badge]  标签（左上角金色标签）     │
│  主标题（大字金色）                 │
│  副标题（灰蓝小字）                │
├─────────────────────────────────┤
│  公式区：三因子 = 结果              │
├─────────────────────────────────┤
│  三栏解析（图标+名称+公式+描述）     │
├─────────────────────────────────┤
│  实战对比：两家公司/两种路径对比      │
├─────────────────────────────────┤
│  核心理念（金色边框高亮区）          │
└─────────────────────────────────┘
```

---

## 快速问答

**Q：字段数量不固定可以吗？**  
A：`columns` 目前硬编码为 3 栏，如需改数量需同步改 `DupontCard.tsx` 布局。如需更灵活的设计，可以修改 DupinCard.tsx 支持动态数量。

**Q：可以换颜色主题吗？**  
A：可以，只需在 `DupontCard.tsx` 中替换金色 `#d4a843` 为其他颜色，同时更新背景渐变。

**Q：卡片尺寸？**  
A：当前设计宽度 540px，最小高度 960px，适配手机端展示。
