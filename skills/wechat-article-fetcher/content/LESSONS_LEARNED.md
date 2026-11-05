# 微信公众号文章抓取工具 - 经验教训总结

## 问题复盘

### 问题1：正文内容无法提取

**现象**：生成的Word文档只有标题和图片，没有正文文字

**根因分析**：
- 脚本只尝试获取图片文章描述（`#js_image_desc`）
- 没有优先获取普通文章正文（`#js_content`）

**解决方案**：
```python
# 优先获取普通文章正文
try:
    content_el = self.driver.find_element(By.CSS_SELECTOR, '#js_content, .rich_media_content')
    content_text = content_el.text.strip()
    content_html = content_el.get_attribute('innerHTML')
except NoSuchElementException:
    # 再尝试图片文章描述
    pass
```

**教训**：
- 微信文章有两种类型：普通文章（`#js_content`）和图片文章（`#js_image_content`）
- 应该优先检测普通文章，再回退到图片文章

---

### 问题2：图片数量不对

**现象**：文章有20张图片，但只下载了1张

**根因分析**：
1. 获取图片属性顺序错误：`src or data-src`，但微信图片主要通过 `data-src` 加载
2. 过滤条件过于严格：`/mmbiz_png/0` 误伤了正常图片
3. 没有限定在正文区域获取图片

**解决方案**：
```python
# 1. 优先获取 data-src
img_url = img.get_attribute('data-src') or img.get_attribute('src')

# 2. 只从正文区域获取图片
content_el = self.driver.find_element(By.CSS_SELECTOR, '#js_content, .rich_media_content')
img_elements = content_el.find_elements(By.TAG_NAME, 'img')

# 3. 放宽过滤条件，只过滤明确的非正文图片
if 'emoji' in img_url.lower() or '/0?' in img_url:
    continue
```

**教训**：
- 微信图片主要通过 `data-src` 懒加载，`src` 可能是空的或占位图
- 应该在正文区域内查找图片，避免获取头像、图标等
- 过滤条件要精确，避免误伤

---

### 问题3：图片位置不对

**现象**：图片全部堆在文档末尾，没有穿插在正文中

**根因分析**：
1. Word生成脚本没有分析HTML结构
2. URL匹配算法不健壮，导致图片匹配失败
3. 没有根据图片在HTML中的位置排序

**解决方案**：
```javascript
// 1. 找出每个<img>标签在HTML中的位置
const imgRegex = /<img[^>]*>/gi;
const imgPositions = [];
while ((match = imgRegex.exec(html)) !== null) {
    imgPositions.push({ position: match.index, tag: match[0] });
}

// 2. 找出每段文字在HTML中的位置
const pos = html.indexOf(text.substring(0, 30));

// 3. 合并并按位置排序
const contentItems = [...textItems, ...imageItems].sort((a, b) => a.position - b.position);
```

**教训**：
- 微信文章是HTML结构，图片和文字混合排列
- 应该根据HTML中的位置来决定渲染顺序
- URL匹配不精确时，可以用顺序匹配（HTML顺序=下载顺序）

---

## 最佳实践

### 1. 抓取阶段

```python
# ✅ 正确做法
# 1. 先等待页面完全加载
time.sleep(8)

# 2. 从正文区域获取图片
content_el = driver.find_element(By.CSS_SELECTOR, '#js_content')
imgs = content_el.find_elements(By.TAG_NAME, 'img')

# 3. 优先使用 data-src
for img in imgs:
    img_url = img.get_attribute('data-src') or img.get_attribute('src')
```

### 2. 过滤策略

```python
# ✅ 精确过滤
# 保留：微信图床图片
if 'mmbiz.qpic.cn' not in img_url:
    continue

# 过滤：表情包、小图标
if 'emoji' in img_url.lower():
    continue

# ❌ 错误的过滤（太严格）
if '/mmbiz_png/0' in img_url:  # 这会误伤正常图片
    continue
```

### 3. Word生成策略

```javascript
// ✅ 根据HTML位置排序
const items = [];
// 添加文字（记录HTML位置）
items.push({ type: 'text', position: html.indexOf(text), text });
// 添加图片（记录HTML位置）
items.push({ type: 'image', position: imgMatch.index, img });
// 按位置排序
items.sort((a, b) => a.position - b.position);
```

---

## 常见陷阱

| 陷阱 | 表现 | 解决方案 |
|------|------|----------|
| 只获取src属性 | 图片URL为空 | 优先获取data-src |
| 全局查找图片 | 下载了头像/图标 | 限定在#js_content区域内 |
| 过滤条件太严 | 正常图片被过滤 | 只过滤emoji/表情包 |
| URL精确匹配 | 图片匹配失败 | 用位置排序或顺序匹配 |
| 图片堆在末尾 | 位置不对 | 分析HTML位置再排序 |

---

## 检查清单

抓取完成后，验证以下内容：

- [ ] 正文长度是否合理？（应该有实质内容）
- [ ] 图片数量是否正确？（对比原文）
- [ ] 图片是否穿插在正文中？（不应该全在末尾）
- [ ] 图片比例是否正确？（不应变形）
- [ ] 是否过滤了水印/推广文字？

---

## 更新日志

**v1.3.0 (2026-04-09)**
- 新增：智能正文边界检测 - 自动识别正文结束位置，排除广告推广内容
- 新增：多种检测策略（关键词定位、结构分析、内容密度分析）
- 优化：OCR水印过滤 - 动态获取公众号名称作为过滤词
- 优化：支持公众号名称的多种写法变体（加后缀、去空格、大小写）

**v1.2.0 (2026-04-09)**
- 优化：OCR水印过滤 - 动态获取公众号名称作为过滤词
- 优化：支持公众号名称的多种写法变体（加后缀、去空格、大小写）
- 新增：过滤更多常见推广文字（转载需注明、来源、阅读数等）

**v1.1.0 (2026-04-07)**
- 修复：正文内容无法提取（优先#js_content）
- 修复：图片数量不对（优先data-src，放宽过滤）
- 修复：图片位置不对（按HTML位置排序）
- 新增：图片穿插在正文中

**v1.0.0 (2026-04-07)**
- 初始版本
