# 视频生成与连贯性维护技术规格

## 1. 角色一致性 (Character ID) 技术

### 特征提取
- **面部特征**：提取关键面部向量，锁定眼睛、鼻子、嘴巴相对位置
- **体型轮廓**：保持身高比例、体型特征
- **服装配饰**：锁定服装颜色、款式、配饰特征
- **特殊标记**：疤痕、纹身、独特饰品

### 实现机制
```json
{
  "character_id": {
    "face_vector": "128dim_embedding",
    "body_proportions": {
      "height_ratio": 1.0,
      "shoulder_width": "medium",
      "build": "athletic"
    },
    "clothing": {
      "base_color": "dark_black",
      "jacket_style": "hooded",
      "accessories": ["face_mask", "goggles"]
    },
    "motion_style": "agile_running"
  }
}
```

### 常见问题解决方案

| 问题 | 原因 | 解决策略 |
|-----|------|---------|
| 角色"换脸" | 特征向量不稳定 | 在每帧Prompt中注入面部描述 |
| 服装变色 | 光照Prompt冲突 | 固定服装颜色关键词 |
| 体型变化 | 透视角度误导 | 使用固定身高比例描述 |
| 饰品消失 | 生成自由度太高 | 明确列出所有饰品 |

---

## 2. 场景连贯性 (Scene Consistency) 技术

### 场景锚点系统
```json
{
  "scene_anchor": {
    "location": "cyberpunk_alley",
    "time": "night_rainy",
    "lighting": {
      "main_source": "neon_sign_blue",
      "direction": "top_right_45deg",
      "intensity": "high"
    },
    "weather": {
      "type": "heavy_rain",
      "effects": ["wet_surfaces", "puddle_reflection", "rain_particles"]
    },
    "color_palette": {
      "primary": "neon_blue",
      "secondary": "neon_pink",
      "accent": "white_rain"
    }
  }
}
```

### 元素一致性矩阵

| 元素类别 | 锚点关键词 | 避免冲突 |
|---------|-----------|---------|
| 建筑风格 | `futuristic_skyscrapers`, `holographic_signs` | 不混用 `medieval_castle` |
| 天气状态 | `heavy_rain`, `wet_streets` | 不混用 `sunny_clear` |
| 光照方向 | `side_lighting_neon` | 不混用 `overhead_sunlight` |
| 时间设定 | `night_scene` | 不混用 `daytime_bright` |

---

## 3. 物理模拟优化

### 水/雨 模拟
```
rain_effects:
  - rain_droplets (particle_count: high)
  - splash_effects (on surfaces)
  - puddle_ripples (expanding circles)
  - wet_reflections (mirror_like surfaces)
  - mist_layer (atmospheric depth)
```

**Prompt注入**：
```
, heavy rain with visible droplets, realistic splash effects,
puddles reflecting neon lights, wet cobblestone streets,
atmospheric mist, cinematic rain atmosphere
```

### 火/烟 模拟
```
fire_effects:
  - flame_particles (orange_red_gradient)
  - smoke_diffusion (soft_translucent)
  - ember_sparks (floating particles)
  - light_cast (dynamic orange glow)
  - shadow_movement (flickering)
```

**Prompt注入**：
```
, roaring flames with flickering light, thick smoke rising,
glowing embers floating upward, dramatic fire lighting on faces,
intense heat atmosphere
```

### 毛发/布料 模拟
```
soft_body:
  - hair_flow (gravity + wind influence)
  - cloth_drapery (gravity_weighted folds)
  - cape_movement (dramatic billowing)
  - fabric_texture (realistic material)
```

**Prompt注入**：
```
, flowing hair moved by wind, realistic fabric physics,
draping cloth with natural folds, cape billowing dramatically,
silk texture catching light
```

---

## 4. 智能配乐系统

### 情感分析 → 音乐风格 映射

| 画面情感 | 音乐风格 | 节奏 | 乐器 |
|---------|---------|-----|-----|
| 欢快 | Pop, Upbeat Electronic | 120-140 BPM | 合成器、吉他 |
| 忧郁 | Ambient, Piano Ballad | 60-80 BPM | 钢琴、弦乐 |
| 紧张 | Suspense, Thriller | 90-110 BPM | 低音提琴、鼓点 |
| 史诗 | Orchestral, Epic | 80-100 BPM | 管弦乐、铜管 |
| 温馨 | Acoustic, Soft Pop | 70-90 BPM | 木吉他、钢琴 |
| 恐怖 | Drones, Atonal | 40-60 BPM | 电子音效、低频 |

### 环境音效库

| 场景 | 环境音 |
|-----|-------|
| 城市雨夜 | 雨声、远处雷声、汽车经过、脚步溅水 |
| 森林 | 鸟鸣、风声、树叶沙沙、溪流 |
| 办公室 | 键盘敲击、空调嗡嗡、咖啡机 |
| 海边 | 海浪拍打、海鸥叫声、海风呼啸 |
| 室内温馨 | 壁炉噼啪、时钟滴答、轻声交谈 |

### 配乐生成参数
```json
{
  "soundtrack": {
    "mood": "tense",
    "style": "cinematic_suspense",
    "bpm": 100,
    "duration": 30,
    "instruments": ["piano", "strings", "drums"],
    "ambient_sounds": ["rain", "thunder_distant"],
    "dynamics": {
      "intro": "soft",
      "build": "gradual_increase",
      "climax": "loud_tension",
      "outro": "fade_out"
    }
  }
}
```

---

## 5. 生成参数配置

### 分辨率选项
| 选项 | 分辨率 | 适用场景 |
|-----|-------|---------|
| 480P | 854×480 | 快速预览、草稿 |
| 720P | 1280×720 | 社交媒体分享 |
| 1080P | 1920×1080 | 高质量输出 |
| 4K | 3840×2160 | 专业级制作 |

### 帧率选项
| 帧率 | 适用场景 | 慢动作兼容性 |
|-----|---------|-------------|
| 24fps | 电影感 | 需要120fps拍摄 |
| 30fps | 标准视频 | 需要60fps拍摄 |
| 60fps | 平滑运动 | 可直接放慢2x |
| 120fps | 电影慢动作 | 可直接放慢4x |

### 时长 → 分镜数 映射

| 总时长 | 分镜数 | 每镜平均时长 | 场景切换数 |
|-------|-------|-------------|-----------|
| 5s | 2-3 | 1.5-2.5s | 1-2 |
| 10s | 3-4 | 2-3s | 2-3 |
| 30s | 6-8 | 3-5s | 3-4 |
| 60s | 10-12 | 5-6s | 5-6 |
| 120s | 15-20 | 5-7s | 6-8 |

---

## 6. 质量保障检查清单

### 生成前检查
- [ ] 角色描述完整（面部、服装、饰品）
- [ ] 场景锚点明确（地点、时间、光照、天气）
- [ ] 分镜数量与时长匹配
- [ ] 风格参数一致性（无风格冲突）
- [ ] Prompt长度优化（避免过长被截断）

### 生成后检查
- [ ] 角色一致性（第1帧 vs 最后1帧）
- [ ] 场景连贯性（建筑、光照、天气）
- [ ] 物理合理性（重力、流体、光影）
- [ ] 音频同步（配乐与画面节奏匹配）
- [ ] 画面质量（无闪烁、无崩坏、无伪影）
