---
name: shoe-ai-photography
description: 
  运动鞋品牌AI摄影与苍绿色彩后期处理技能。激活场景：(1) 用户需要运动鞋产品摄影 (2) 用户需要对运动鞋进行色彩后期处理 (3) 用户需要制作运动鞋品牌对比页面 (4) 用户提到Nike/Adidas/New Balance等运动鞋品牌。核心理念：每一种运动鞋品牌都有对应的苍绿色彩代码，色彩即品牌灵魂。
---

# 运动鞋AI摄影 · 苍绿色彩体系

 色彩即品牌灵魂。苍绿14色 × 运动鞋 = 全新视觉语言。

## 核心流程

1. 调研品牌：搜索目标品牌市场定位、代表色、目标用户
2. 获取素材：下载品牌官方产品图（透明PNG优先）
3. AI后期：用苍绿色彩体系对图片进行重着色
4. 前后对比：制作可滑动的before/after对比展示页面
5. 部署：deploy工具生成可分享链接

## 苍绿14色 × 运动鞋品牌

| 苍绿色 | 代表品牌 | 情感 |
|--------|---------|------|
| 苍绿 | UA / Brooks / 安踏 / 鸿星尔克 | 意志/幸福/国民 |
| 金棕 | Adidas / Puma / Hoka / 匹克 | 信任/速度/厚实 |
| 天青 | Asics / Saucony / Mizuno / 361° | 冷静/耐力/新锐 |
| 砖红 | Nike / Kappa / Li-Ning / 特步 | 行动/能量/可能 |
| 墨绿 | Vans / Salomon | 叛逆/山野 |
| 雾青 | New Balance / Fila / Lotto | 留白/优雅/简约 |

## 工具链

1. `images_search_and_download` — 下载品牌产品图
2. `image_synthesize` — AI后期重着色
3. `upload_to_cdn` — 上传处理后图片
4. `write` + `deploy` — 构建前后对比HTML页面

## 龙宫参考

| 产品 | URL |
|------|-----|
| 苍绿影像 | e8w4agymwxjb.space.minimaxi.com |
| 30品牌图谱 | q7qr15ohsmfv.space.minimaxi.com |
| 色彩对比 | t410dpwl6jck.space.minimaxi.com |

## 注意事项

- 图片优先透明PNG（品牌官网/CDN）
- AI后期prompt：pure white background + 目标颜色 + 运动鞋
- 页面背景统一：#030308
- 滑块对比：CSS clip-path + mousedown/mousemove
