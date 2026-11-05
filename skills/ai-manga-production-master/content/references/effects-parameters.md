# 特效参数完整设计表

## 能量类特效

### 冲击波特效模板

| 参数名称 | 数值 | 说明 |
|---------|------|------|
| 形状 | 球形/圆形 | 核心形状 |
| 半径 | 0→200像素 | 扩散范围 |
| 厚度 | 20→5像素 | 边缘锐利程度 |
| 颜色 | #FF6B35→#FFD93D | 渐变色（橙→金） |
| 透明度 | 100%→0% | 随扩散淡化 |
| 时长 | 0.5秒 | 完整动画时长 |
| 帧率 | 60fps | 流畅度要求 |
| 叠加层数 | 3层 | 内外圈+核心 |
| 扰动 | 轻微波动 | 增加真实感 |

**动画曲线**：
```
帧0-15: 快速扩张（半径0→150px）
帧15-25: 减速扩散（半径150→180px）
帧25-30: 淡化消散（透明度100%→0%）
```

---

### 能量弹特效模板

| 参数名称 | 数值 | 说明 |
|---------|------|------|
| 核心 | 圆形/菱形 | 能量核心形状 |
| 核心大小 | 30-50像素 | 主体尺寸 |
| 光晕 | 核心大小×2 | 发光范围 |
| 轨迹长度 | 100像素 | 拖尾效果 |
| 轨迹渐变 | 100%→20% | 透明度递减 |
| 颜色 | 蓝紫渐变 | #00D4FF→#9B59B6 |
| 闪烁频率 | 10Hz | 脉冲效果 |
| 运动模糊 | 方向性模糊 | 速度感 |
| 粒子喷射 | 少量小型粒子 | 能量溢出 |

**动画曲线**：
```
核心：持续脉冲（10Hz）+ 轻微抖动
轨迹：从粗到细渐变
粒子：每10帧喷射3-5个
```

---

### 剑气/刀气特效模板

| 参数名称 | 数值 | 说明 |
|---------|------|------|
| 形状 | 弧形/直线 | 剑气形态 |
| 长度 | 200-500像素 | 切割轨迹长度 |
| 宽度 | 30→5像素 | 从粗到细 |
| 颜色 | 白→青/金 | 边缘到核心 |
| 透明度 | 100%→0% | 逐渐消散 |
| 拖尾 | 3-5层叠加 | 速度感 |
| 边缘 | 锯齿/平滑 | 风格选择 |
| 轨迹 | 轻微曲线 | 弧度10-30度 |

**动画曲线**：
```
帧0-10: 斩出（向前+向上/下）
帧10-20: 轨迹延续
帧20-30: 淡化消散
```

---

### 能量护盾特效模板

| 参数名称 | 数值 | 说明 |
|---------|------|------|
| 形状 | 球形/半球形 | 包裹范围 |
| 半径 | 100-200像素 | 护盾大小 |
| 厚度 | 5-10像素 | 边缘厚度 |
| 颜色 | 能量色 | 蓝/紫/金/红 |
| 透明度 | 70-90% | 半透明 |
| 纹理 | 六边形/电路 | 风格纹理 |
| 闪烁 | 局部闪烁 | 能量流动 |
| 破裂 | 裂纹+碎片 | 破碎效果 |

**动画曲线**：
```
待机：缓慢脉动（0.5Hz）+ 纹理流动
受击：局部亮起+波纹扩散
破裂：裂纹扩散+碎片飞散
```

---

### 能量聚集特效模板

| 参数名称 | 数值 | 说明 |
|---------|------|------|
| 粒子来源 | 360度/指定方向 | 聚集方式 |
| 粒子数量 | 20→100 | 逐渐增加 |
| 粒子大小 | 5→2像素 | 逐渐变小 |
| 速度 | 快→极快 | 加速聚集 |
| 轨迹 | 螺旋/直线 | 运动路径 |
| 颜色 | 边缘→核心 | 渐变汇聚 |
| 光晕 | 中心聚集 | 亮度增加 |
| 音效 | 嗡鸣渐强 | 同步 |

**动画曲线**：
```
帧0-30: 粒子从四周聚集，密度增加
帧30-60: 速度加快，形成漩涡
帧60-90: 高度集中，亮度峰值
```

---

## 物理类特效

### 爆炸特效模板

| 参数名称 | 数值 | 说明 |
|---------|------|------|
| 火球半径 | 0→150像素 | 核心大小 |
| 火焰颜色 | 黄→橙→红 | 温度渐变 |
| 烟雾范围 | 200→400像素 | 扩散 |
| 烟雾颜色 | 灰→深灰 | 浓度变化 |
| 碎片数量 | 30-50个 | 飞散物 |
| 碎片类型 | 岩石/金属/泥土 | 材质 |
| 冲击波 | 同冲击波模板 | 环形扩散 |
| 持续时间 | 2-5秒 | 完全消散 |
| 帧率 | 60fps | 高速摄影可选 |

**分层设计**：
```
Layer 1（核心）: 火球 + 白光核心
Layer 2（中层）: 橙红火焰 + 火星
Layer 3（外层）: 烟雾 + 冲击波
Layer 4（碎屑）: 飞散物体 + 烟尘轨迹
```

---

### 碎片特效模板

| 参数名称 | 数值 | 说明 |
|---------|------|------|
| 碎片数量 | 10-50个 | 根据规模 |
| 碎片大小 | 5-50像素 | 随机 |
| 碎片形状 | 不规则多边形 | 随机生成 |
| 初始速度 | 50-200像素/秒 | 爆发力 |
| 旋转速度 | 10-30 rad/s | 随机 |
| 重力影响 | 0.5-1.0 | 下落加速度 |
| 碰撞地面 | 弹跳1-3次 | 物理效果 |
| 材质颜色 | 根据场景 | 统一调色 |

**分布参数**：
```
80%: 快速下落（重力主导）
15%: 抛物线飞出（初速度主导）
5%: 旋转飘落（空气阻力主导）
```

---

### 水花特效模板

| 参数名称 | 数值 | 说明 |
|---------|------|------|
| 主体水花 | 圆形扩散 | 溅射半径 |
| 水滴数量 | 20-50个 | 飞溅数量 |
| 水滴大小 | 3-15像素 | 随机 |
| 下落速度 | 100-300像素/秒 | 重力 |
| 涟漪数量 | 3-5个 | 扩散圈 |
| 涟漪半径 | 10→100像素 | 扩散 |
| 透明度 | 100%→0% | 淡化 |
| 持续时间 | 1-3秒 | 完全消散 |

---

## 强化类特效

### 变身特效模板

| 参数名称 | 数值 | 说明 |
|---------|------|------|
| 光芒类型 | 球形爆发 | 从角色中心 |
| 光芒半径 | 0→300像素 | 扩张 |
| 能量丝带 | 螺旋缠绕 | 数量5-10条 |
| 碎片悬浮 | 0.5-2秒 | 暂停后释放 |
| 地面裂纹 | 扩散+发光 | 半径0→100px |
| 天空效果 | 云层穿透 | 光柱冲天 |
| 色调变化 | 普通→强化色 | 色彩偏移 |
| 服装变化 | 撕裂→重塑 | 分层动画 |

**时序设计**：
```
帧0-10: 身体僵直，光芒开始
帧10-30: 能量爆发，衣袍撕裂
帧30-50: 碎片悬浮，形态重塑
帧50-60: 光芒收敛，震撼登场
```

---

### 加速特效模板

| 参数名称 | 数值 | 说明 |
|---------|------|------|
| 残像数量 | 5-10个 | 轨迹长度 |
| 残像透明度 | 80%→10% | 递减 |
| 残像延迟 | 50-100ms | 时间差 |
| 速度线 | 放射状 | 背景 |
| 速度线颜色 | 白→透明 | 渐变 |
| 动态模糊 | 方向性 | 主体 |
| 声音效果 | 嗖/破空 | 同步 |
| 空气扭曲 | 身后 | 热浪效果 |

---

### 觉醒特效模板

| 参数名称 | 数值 | 说明 |
|---------|------|------|
| 全屏光芒 | 0→100%→50% | 亮度变化 |
| 能量光环 | 3-5层同心圆 | 脉冲扩散 |
| 光柱 | 地面→天空 | 贯穿画面 |
| 背景变化 | 天空/云层 | 环境升级 |
| 色调偏移 | 冷→暖或反 | 情感色 |
| 能量线条 | 身体纹路 | 流动发光 |
| 气场 | 半透明能量球 | 包裹角色 |
| 粒子爆发 | 500+粒子 | 螺旋扩散 |

---

## AI特效提示词模板

### 通用能量特效提示词

```
Hyper-detailed energy effects, glowing plasma core, electric arcs crackling around edges, inner light pulsing rhythmically, outer aura swirling with power, light rays emanating from center, sparks and particles scattering outward, volumetric light effect, chromatic aberration at edges, motion blur on energy streams, 8K resolution, cinematic particle simulation, energy tendrils extending and retracting, aurora-like color shifting, holographic interference patterns, god rays from energy concentration, ultra-bright core with soft glowing edges, perfect composition, studio-quality VFX, Unreal Engine 5 render quality
```

### 战斗冲击波提示词

```
Massive shockwave expanding outward, circular compression wave front, debris and dust caught in blast trajectory, thermal glow at wave edge, compressed air distortion effect, ground cracking beneath propagation path, objects lifted and thrown, smoke trail following blast, bright orange-white core with yellow edges, volumetric atmosphere distortion, slow-motion cinematic quality, 60fps smooth animation, perfect radial symmetry, secondary smaller waves trailing main blast, reflective debris catching light, ground-level dust cloud kicked up, ultra-detailed impact visualization
```

### 变身/觉醒特效提示词

```
Dramatic transformation sequence, blinding light explosion from character center, energy ribbons spiraling around body, particle vortex forming geometric patterns, light beams piercing through clouds/sky, temporary silhouette with glowing outline, crackling energy tendrils snapping outward, ground beneath character cracking, atmospheric pressure change visible, wind effects pushing surrounding elements, color palette shifting from normal to enhanced (gold/blue/purple glow), slow-motion final reveal, cape/cloth effects with energy trails, eye transformation with light beams, god-tier aura with layered transparent energy rings
```

### 爆炸特效提示词

```
Intense explosion at impact point, fireball expanding with internal swirling flames, thick smoke billowing upward, bright orange-yellow core fading to red edges, secondary smaller explosions triggered, debris flying outward in parabolic trajectories, ground crater forming at epicenter, heat distortion shimmer, sparks and embers floating upward, shockwave ring visible in atmosphere, dust cloud expanding radially, metallic debris glowing red-hot, mushroom cloud formation for large explosions, slow-motion detailed destruction, perfect cinematic composition
```

---

## 特效配色方案

### 能量色系

| 能量类型 | 颜色代码 | 色名 |
|---------|---------|------|
| 冰系 | #00D4FF → #FFFFFF | 冰蓝渐变 |
| 火系 | #FF4500 → #FFD700 | 烈焰橙金 |
| 雷系 | #9400D3 → #FFFFFF | 紫电白 |
| 暗系 | #4B0082 → #000000 | 幽暗紫黑 |
| 光系 | #FFFFFF → #FFD700 | 圣洁白金 |
| 风系 | #E0FFFF → #FFFFFF | 凌风青白 |
| 土系 | #8B4513 → #DAA520 | 大地棕金 |
| 水系 | #006994 → #00CED1 | 深海青蓝 |

### 情绪配色

| 情绪 | 主色 | 辅色 | 效果色 |
|------|------|------|--------|
| 愤怒 | #FF0000 | #8B0000 | #FFD700 |
| 悲伤 | #4169E1 | #000080 | #E0FFFF |
| 恐惧 | #4B0082 | #000000 | #FF00FF |
| 喜悦 | #FFD700 | #FFA500 | #FFFFFF |
| 平静 | #87CEEB | #E0FFFF | #FFFFFF |
| 绝望 | #2F4F4F | #000000 | #696969 |
