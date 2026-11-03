# deepseek文案优化规则详解

## 一、标题优化规则

### 1.1 核心关键词要求
- **数量要求**：至少包含2个核心关键词
- **前置规则**：将其中一个核心关键词前置后加逗号
- **重复限制**：同样的名词和词组不出现2次以上
- **字符限制**：总字符控制在150左右

### 1.2 特殊处理
- **括号保留**：如果原标题带括号内容，括号位置不变
- **品牌名**：如原标题有品牌名，保留在开头
- **变体信息**：如有多颜色/尺寸变体，保留在括号内

### 1.3 标题结构建议
```
[品牌名] 核心关键词1, 核心关键词2 + 产品名称 + 重要特性 + 规格/数量
```

### 1.4 示例

**原标题**：
```
Wireless Bluetooth Earbuds with Charging Case (Black)
```

**优化后**：
```
Wireless Earbuds, Bluetooth 5.0 In-Ear Headphones with Charging Case - TWS Stereo Sound for Sports & Workout (Black)
```

---

## 二、五点优化规则

### 2.1 语言习惯
- 语句通顺，避免中式英语
- 符合美国消费者的阅读习惯
- 简洁有力，重点突出

### 2.2 禁止内容
- ❌ **夸大性能**：避免"best", "perfect", "amazing"等绝对性词汇
- ❌ **售后信息**：不包含"warranty", "guarantee", "support"等信息
- ❌ **价格描述**：不包含"cheap", "affordable", "discount"等
- ❌ **重复介词**：避免同一个介词出现多次

### 2.3 必需内容
- ✅ **埋入主关键词**：每个五点至少包含1次主关键词
- ✅ **小标题概括**：每一点开头用简短标题概括
- ✅ **格式规范**：小标题和内容之间用冒号隔开

### 2.4 格式要求
```
小标题: 详细内容（写在同一行）
```

### 2.5 五点结构建议
1. **产品简介**：是什么产品，主要用途
2. **核心功能**：主要卖点，区别于竞品的特点
3. **规格参数**：重要技术参数
4. **使用场景**：适用人群或场景
5. **购买理由**：为什么选择这款产品

### 2.6 示例

**原五点**：
```
1. Good quality earbuds
2. Bluetooth headphones
3. Long battery life
4. Easy to use
5. Perfect for sports
```

**优化后**：
```
Premium Sound Quality: Advanced audio drivers deliver crystal-clear highs and deep bass for an immersive music experience
Bluetooth 5.0 Connectivity: Seamless pairing with all Bluetooth-enabled devices; stable connection up to 33 feet
Long Battery Life: Up to 8 hours of playtime on a single charge; extended to 32 hours with the portable charging case
Comfortable Fit: Ergonomic design with soft silicone ear tips ensures a secure and comfortable fit for all-day wear
Sport-Ready Design: Sweat-resistant and lightweight; perfect for workouts, running, and outdoor activities
```

---

## 三、关键词优化规则

### 3.1 去重要求
- 重复单词必须去重
- 只保留唯一关键词

### 3.2 字符限制
- 去重后控制在**200-220个字符**之间
- **仅计算字母字符**
- 空格和换行符不计入

### 3.3 格式要求
- 关键词之间用**空格隔开**
- 方便直接复制粘贴到平台后台

### 3.4 关键词分类建议
1. **核心产品词**：产品主类型
2. **品牌词**：知名品牌相关
3. **功能词**：产品功能特性
4. **用途词**：使用场景
5. **材质词**：产品材质
6. **规格词**：尺寸、颜色等

### 3.5 示例

**原关键词**：
```
wireless earbuds bluetooth earbuds earbuds wireless headphones bluetooth headphones earphones wireless earphones earbuds for women earbuds for men earbuds sports earbuds running earbuds waterproof earbuds
```

**优化后**：
```
wireless earbuds bluetooth earbuds headphones earphones sport running waterproof women men
```

---

## 四、通用优化规则

### 4.1 侵权词过滤
- 去除所有侵权相关词汇
- 不添加未授权的品牌信息
- 不添加虚假的认证标志

### 4.2 信息真实性
- 不添加描述中不存在的认证信息
- 不添加未标注的参数信息
- 如需换单位，必须进行相应换算

### 4.3 单位换算参考
| 类型 | 英制 | 公制换算 |
|------|------|----------|
| 长度 | inch | 2.54 cm |
| 长度 | foot | 30.48 cm |
| 重量 | oz | 28.35 g |
| 重量 | lb | 453.59 g |
| 容量 | fl oz | 29.57 ml |
| 温度 | °F | (°F-32)×5/9 °C |

---

## 五、deepseek API调用模板

### 5.1 系统提示词
```
你是一位专业的[平台]-[站点]跨境电商运营专家，擅长优化Amazon、eBay等平台的产品listing。你需要根据产品信息优化标题、五点描述和搜索关键词，以提升产品曝光率和转化率。
```

### 5.2 用户提示词模板
```
请优化以下[平台名称] [站点名称]产品的listing文案：

【原标题】
[标题内容]

【原五点描述】
[五点内容]

【原搜索关键词】
[关键词内容]

【产品描述】
[描述内容]

请严格按照以下规则进行优化：

1. 标题优化规则：
   - 至少包含2个核心关键词
   - 将其中一个核心关键词前置后加逗号
   - 同样名词和词组不出现2次以上
   - 总字符控制在150左右
   - 如果原标题带括号内容，括号位置不变

2. 五点优化规则：
   - 语句通顺，符合美国人语言习惯
   - 避免重复介词和夸大产品性能
   - 不要有售后相关信息及价格描述
   - 需要埋入主关键词
   - 每一点要有小标题概括，小标题和内容之间用冒号隔开
   - 每一点写在同一行

3. 关键词优化规则：
   - 重复单词需要去重
   - 去重后控制在200-220个字符数（仅计算字母）
   - 关键词用空格隔开

4. 通用规则：
   - 剔除侵权词
   - 不要添加描述中不存在的认证信息
   - 如需换单位，数字需进行相应换算
   - 使用[站点语言，如English]输出

请分别输出优化后的标题、五点描述和搜索关键词。
```

### 5.3 输出格式
```json
{
  "optimized_title": "优化后的标题",
  "optimized_bullet_points": [
    "五点1",
    "五点2",
    "五点3",
    "五点4",
    "五点5"
  ],
  "optimized_keywords": "去重后的关键词"
}
```
