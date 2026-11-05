# 微信设计系统

微信的设计语言代表中国移动互联网的最高水准。

## 设计理念

微信追求**简洁**、**高效**、**连接一切**。设计以用户为中心，注重实用性和流畅体验。

## 色彩系统

### 品牌色
- Primary: `#07C160` (微信绿)
- Primary Dark: `#06AD56`
- Primary Light: `#10D174`

### 辅助色
- Success: `#07C160`
- Warning: `#FFCD00`
- Error: `#FA5151`
- Info: `#10AEFC`

### 背景色
- Background: `#FFFFFF`
- Background Gray: `#F7F7F7`
- Background Dark: `#1F1F1F`

### 文字色
- Text Primary: `#000000`
- Text Secondary: `#576B95`
- Text Tertiary: `#C7C7C7`
- Text Disabled: `#B2B2B2`

### 边框色
- Border: `#E5E5E5`
- Border Dark: `#3A3A3C`

## 微信小程序色板

```css
--weui-BRAND: #07C160;
--weui-BLUE: #10AEFC;
--weui-ORANGE: #FF991A;
--weui-RED: #FA5151;
--weui-YELLOW: #FFC117;
--weui-GREEN: #07C160;
--weui-BACKGROUND: #F7F7F7;
--weui-TEXT: #000000;
--weui-TEXT-SECONDARY: #576B95;
```

## 字体

### 字体栈
```
-apple-system, BlinkMacSystemFont, 'Helvetica Neue', Helvetica, Arial, sans-serif
```

### 字号 (小程序)
- Display: 34px / 600 weight
- Title: 22px / 600 weight
- Subtitle: 18px / 600 weight
- Body: 17px / 400 weight
- Caption: 14px / 400 weight
- Small: 12px / 400 weight

### 字号 (iOS 微信)
- Title: 17px / Semibold
- Content: 15px / Regular
- Caption: 12px / Regular

## 间距系统

基于 4px 网格：
- xs: 4px
- sm: 8px
- md: 12px
- lg: 16px
- xl: 24px
- 2xl: 32px

## 圆角

- xs: 2px
- sm: 4px
- md: 8px
- lg: 12px
- xl: 16px
- full: 9999px (胶囊)

## 阴影

### 轻阴影
```css
box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
```

### 卡片阴影
```css
box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
```

### 导航栏
```css
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
```

## 组件样式

### 按钮

**主按钮**
- Background: `#07C160`
- Color: `#FFFFFF`
- Border Radius: 4px
- Height: 88rpx (44px)
- Font Size: 17px

**次要按钮**
- Background: `#FFFFFF`
- Color: `#07C160`
- Border: 1px solid `#07C160`
- Border Radius: 4px

**文本按钮**
- Color: `#576B95`
- 无背景

**操作菜单**
- Background: rgba(255, 255, 255, 0.95)
- Border Radius: 12px
- Item Height: 50px
- Border Top: 0.5px solid `#E5E5E5`

### 输入框

- Background: `#F7F7F7`
- Border Radius: 4px
- Height: 72rpx (36px)
- Padding: 0 16rpx
- Font Size: 15px
- Focus Background: `#FFFFFF`
- Focus Border: `#07C160`

### 卡片

- Background: `#FFFFFF`
- Border Radius: 8px
- Padding: 16px
- Margin: 12px

### 列表

- Item Height: 44px
- Item Padding: 12px 16px
- Separator: 0.5px solid `#E5E5E5`
- Separator Left: 16px
- Arrow Color: `#C7C7C7`

### 标签页

- Active Color: `#07C160`
- Inactive Color: `#7A7A7A`
- Indicator Color: `#07C160`
- Height: 44px

### 底部导航栏

- Background: `#F7F7F7`
- Height: 56px + safe-area
- Item Icon Size: 24px
- Item Text Size: 10px
- Active Color: `#07C160`
- Inactive Color: `#999999`

### Toast 提示

- Background: rgba(0, 0, 0, 0.8)
- Color: `#FFFFFF`
- Border Radius: 8px
- Padding: 12px 24px
- Font Size: 14px

### 对话气泡

**发送 (右侧)**
- Background: `#07C160`
- Color: `#FFFFFF`
- Border Radius: 4px
- Arrow: 指向右侧

**接收 (左侧)**
- Background: `#FFFFFF`
- Color: `#000000`
- Border Radius: 4px
- Border: 0.5px solid `#E5E5E5`
- Arrow: 指向左侧

## 微信小程序组件

```css
/* 主题色变量 */
page {
  --weui-theme: #07C160;
  --weui-bg-color: #F7F7F7;
  --weui-text-color: #000000;
}
```

### 按钮样式
```css
.weui-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  font-size: 17px;
  border-radius: 4px;
}

.weui-btn_primary {
  background-color: #07C160;
  color: #FFFFFF;
}
```

### 输入框样式
```css
.weui-input {
  height: 72rpx;
  padding: 0 16rpx;
  background-color: #F7F7F7;
  border-radius: 4px;
  font-size: 15px;
}
```

## 设计注意事项

1. **轻量设计** - 不要过度装饰
2. **品牌一致性** - 保持微信绿的使用
3. **适配安全区** - iOS 刘海屏适配
4. **触摸友好** - 最小点击区域 44px
5. **简洁清晰** - 避免过多层级

## 适用场景

- 💬 社交应用
- 🛒 小程序商城
- 📱 移动端页面
- 🏢 企业微信应用
- 🔗 微信生态产品

## 组件示例 HTML 结构

```html
<!-- 主按钮 -->
<button class="weui-btn weui-btn_primary">确定</button>

<!-- 次要按钮 -->
<button class="weui-btn weui-btn_default">取消</button>

<!-- 输入框 -->
<input class="weui-input" type="text" placeholder="请输入">

<!-- 卡片 -->
<div class="weui-card">
  <div class="weui-card-hd">标题</div>
  <div class="weui-card-bd">内容</div>
</div>

<!-- 列表 -->
<div class="weui-cells">
  <div class="weui-cell">
    <div class="weui-cell-bd">标题</div>
    <div class="weui-cell-ft weui-cell_access">›</div>
  </div>
</div>

<!-- 对话气泡 -->
<div class="weui-chat">
  <div class="weui-chat bubble-left">你好</div>
  <div class="weui-chat bubble-right">你好呀</div>
</div>
```
