---
name: id-card-cropper
description: |
  从中国居民身份证照片中自动提取身份证区域，做透视矫正和裁切，
  输出标准 1.586:1 比例图片，去除原背景，可选白边留白。
  触发场景：用户给一张身份证照片，要求"裁切身份证"、"矫正身份证照片"、
  "提取身份证"、"去除背景"、"把身份证摆正"、"证件照处理"、
  "拼接身份证正反面"、"上下拼接身份证"。
  适用：身份证基本完整可见（不是残缺遮挡）、背景是桌面/墙/布料等非人物场景。
  不适用：身份证信息 OCR 提取（用 OCR 工具）、人脸比对/身份核验、护照/驾照等其他证件、
  完全模糊看不清的图、身份证只占图像极小一部分（<5%）需要先放大的情况。
---

# ID Card Cropper

## Inputs to collect
- 输入图片路径（从 attachment / 用户指定）
- 可选：白边比例（默认 5%）
- 可选：输出身份证宽度（默认 1600px）
- 可选：检测 strategy（默认 auto）

## Procedure
1. 把图缩到 1500 宽处理
   原因：GrabCut 是 O(n²)，原图（4032×3024 之类）跑几分钟，缩小后几秒
2. **如果身份证在原图是"横排"放置**（文字侧着），先 `cv2.rotate 90° CCW` 翻正
   原因：用户经常竖拍（相机拿竖了），身份证"宽"在垂直方向，文字侧着
   适用：人像面、国徽面常常都是这样
3. 默认 auto 模式：先跑 GrabCut，看最大连通区域占图比例
   - **< 35%**：身份证在图中央（背景复杂），用 GrabCut 结果
   - **≥ 35%**：身份证几乎填满图，GrabCut 容易漏边缘，fallback 到 V>180 边缘检测
   原因：GrabCut 基于颜色聚类分离前景/背景；身份证几乎填满图时，初始框太大导致聚类失败
4. LLM 也可以显式指定 strategy：
   - `auto`（默认）：自动判断
   - `grabcut`：强制用 GrabCut
   - `edges`：强制用 V>180 + minAreaRect
   - `fullimage`：假设身份证填满图（无检测）
5. 找 4 角点：凸包 → 多边形近似到 4 顶点
   - 兜底：minAreaRect 给旋转矩形（mask 噪声大时仍稳定）
   - 检测到 4 顶点边长比 > 5x 时也 fallback 到 minAreaRect
   原因：多边形近似在 mask 噪声大时会指向错误的"角点"（边缘噪声而非身份证角）
6. 透视变换把身份证映射到 1600×1008 标准比例矩形
   原因：身份证标准宽高 85.6×54mm = 1.586:1
7. 加白色留白（**按比例加**，保持整体 1.586 比例）
   原因：白边加在 4 边相同会让比例偏移；按比例加 = 水平 80px、垂直 50px（按身份证比例）
8. **拼接模式**（stitch.py）：把人像面 + 国徽面 vstack 上下拼接
   - 两张都先做上面 1-7 步
   - 输出文件名 `61-<身份证号>.png`（中国身份证常见命名约定）
   - 输出比例 1.260（h/w）= 2 × 单张比例，符合真实身份证正反面对折的样子

## Output contract
- 单张模式（process.py）：
  - `<stem>_corrected.png` — 矫正后的身份证（无白边）
  - `<stem>_with_border.png` — 矫正 + 5% 白边
  - 输出比例严格 1.586:1
- 拼接模式（stitch.py）：
  - `61-<身份证号>.png` — 人像面 + 国徽面上下拼接
  - 输出比例 1.260（h/w）
- 身份证内容（姓名/性别/出生/住址/身份证号/头像）保持完整可读
- 通过 `deliver-assets` 标签把文件发给用户（不能只给路径）

## Failure handling
- 找不到 4 角点 → minAreaRect 兜底
- GrabCut 在"身份证几乎填满图"场景失败 → auto 模式自动 fallback 到 V>180 边缘检测
- 多边形近似给 4 顶点但形状不接近矩形（边长比 > 5x）→ minAreaRect 兜底
- 身份证只占图 < 5% → 提示用户拍更近一点再试
- 拼接时单张处理失败 → 报错并返回到单张模式
- 实在搞不定 → 建议用户换 strategy 参数手动指定

## Examples

### 单张裁切
```bash
python3 /workspace/.skills/id-card-cropper/scripts/process.py <image_path> -o <output_dir> -b 0.05
```
输入：`attachments/id_card.jpg`（身份证在米色墙面上，有透视变形）
输出：`id_card_corrected.png` + `id_card_with_border.png`

### 正反面拼接
```bash
python3 /workspace/.skills/id-card-cropper/scripts/stitch.py \
  --portrait attachments/portrait.jpg \
  --guohui attachments/guohui.jpg \
  --id 532927199612271924
```
输入：人像面 + 国徽面两张图
输出：`61-532927199612271924.png`（上下拼接，比例 1.260）

## 依赖
opencv-python-headless、numpy（沙箱已预装）。
