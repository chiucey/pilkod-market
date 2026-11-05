# Amazon Style Finder Examples

## Example 1: Portable Air Compressor (US)

### Data Collection
- Amazon search "portable air compressor": autocomplete shows "12v", "tire inflator", "cordless", "for car", "mini"
- Best Sellers: 60% are 12V DC car-powered, 25% cordless lithium, 15% dual-cylinder heavy duty
- Price bands: 12V ($20-50), Cordless ($40-90), Dual Cylinder ($60-150)

### Dimension Decision
**Primary Dimension**: Core Function + Power Source
**Rationale**: Power source determines use case (car vs outdoor vs heavy duty) and creates >3x price variance

### Style Cards

#### 1. 车载点烟器款 | 12V DC Tire Inflator
- **Scene**: 汽车应急、日常补胎
- **Core Function**: 点烟器供电，预设胎压自动停机
- **Differentiation**: 无需充电，随插随用，车内常备
- **Market Coverage**: 高
- **Excludes**: 不含无线锂电款
- **Amazon Evidence**: BS前10占6席，均价$35，评论数5000+

#### 2. 无线锂电款 | Cordless Tire Inflator
- **Scene**: 户外无电源、球类/自行车多用途
- **Core Function**: 内置锂电池，车胎球类通用充气
- **Differentiation**: 摆脱电源限制，便携性最强
- **Market Coverage**: 高
- **Excludes**: 不含需接点烟器款
- **Amazon Evidence**: BS前10占3席，均价$65，评论数增速最快(+200% YoY)

#### 3. 双缸大功率款 | Dual Cylinder Air Pump
- **Scene**: SUV/卡车大胎径、专业维修
- **Core Function**: 双缸压缩，充气速度比单缸快50%
- **Differentiation**: 高压大流量，专业级效率
- **Market Coverage**: 中
- **Excludes**: 不含单缸便携款
- **Amazon Evidence**: BS前50占5席，均价$100，评论数500-2000

---

## Example 2: Insulated Water Bottle (US)

### Data Collection
- Amazon search "insulated water bottle": autocomplete shows "for kids", "sports", "straw", "with handle", "large"
- Best Sellers: 40% standard narrow-mouth, 30% sports straw, 20% kids, 10% large jug
- Reddit r/BuyItForLife discussion: users distinguish by "daily carry" vs "workout" vs "kids lunchbox"

### Dimension Decision
**Primary Dimension**: Target User + Use Case
**Rationale**: User type (adult commuter / athlete / child) creates completely different feature requirements

### Style Cards

#### 1. 标准通勤款 | Classic Insulated Bottle
- **Scene**: 办公室、车载、日常通勤
- **Core Function**: 窄口旋盖，适配标准杯架，12-24小时保温
- **Differentiation**: 极简设计，不挑场景，复购率最高
- **Market Coverage**: 高
- **Excludes**: 不含运动吸嘴款
- **Amazon Evidence**: Hydro Flask / Yeti主导，BS前20占8席

#### 2. 户外运动款 | Sports Water Bottle
- **Scene**: 跑步、骑行、健身房
- **Core Function**: 单手开盖，吸管或挤压出水，配挂扣
- **Differentiation**: 运动中无需停步即可补水，防漏抗震
- **Market Coverage**: 高
- **Excludes**: 不含窄口旋盖款
- **Amazon Evidence**: CamelBak / Under Armour主导，BS前20占6席

#### 3. 儿童吸管款 | Kids Insulated Tumbler
- **Scene**: 学校、幼儿园、儿童背包
- **Core Function**: 防呛吸管，双壁防烫，卡通外观
- **Differentiation**: 安全设计优先，适配儿童手部力量
- **Market Coverage**: 中
- **Excludes**: 不含500ml以上大容量款
- **Amazon Evidence**: Thermos Funtainer主导，BS前50占5席，季节性波动大

---

## Example 3: Bad Output (What to Avoid)

### Input: Phone Case

**Bad Styles**:
- "硅胶软壳 / Silicone Case" — Error: material, not mindset style
- "红色手机壳 / Red Case" — Error: pure aesthetic
- "带摄像头保护款 / Camera Protection" — Error: now standard

**Why Bad**: These are not decision criteria. Users don't search "I want a silicone phone case"; they search "iPhone 15 case" then filter by features. The real dimension is "Protection Level" (slim / rugged / wallet) or "Function Add-on" (MagSafe / kickstand / card holder).

---

## Example 4: Edge Case — Homogeneous Category

### Input: AA Batteries (US)

**Analysis**:
- Amazon autocomplete: "rechargeable", "lithium", "alkaline", "bulk"
- Best Sellers: 90% are alkaline or rechargeable; lithium is <5%
- Price variance: alkaline ($0.30/cell) vs rechargeable ($2/cell) vs lithium ($3/cell) — >5x

**Dimension Decision**: Technology Type (技术类型)
**Styles**:
1. 碱性一次性款 | Alkaline Battery — 高
2. 镍氢充电款 | NiMH Rechargeable — 中
3. 锂电高性能款 | Lithium Battery — 低

**Note**: Only 3 styles because the category is highly commoditized. This is correct — do not force 5+ styles where they don't exist.
