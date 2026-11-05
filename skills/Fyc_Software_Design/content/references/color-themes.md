# 三档配色方案(CSS 变量驱动)

切换主题只需要替换 CSS 变量。所有组件都引用变量。

## Theme 1: cream (奶油白,默认)
适合: 业务大屏、数据看板、参考图就是奶油白风格的场景
```css
:root {
    --bg-primary: #ffffff;
    --bg-gradient: radial-gradient(ellipse at top, #e8f1fa 0%, #f5f9fd 50%, #ffffff 100%);
    --panel-bg: rgba(255, 255, 255, 0.78);
    --panel-border: rgba(143, 188, 255, 0.4);
    --text-primary: #1e3a6e;
    --text-secondary: #3a5a8c;
    --text-muted: #6b8fc4;
    --text-faint: #8aa7c9;
    --accent: #4a7bb8;
    --accent-light: #8fbcff;
    --accent-pale: #dde8f5;
    --warning: #ff9a3c;
    --success: #4ade80;
    --shadow: 0 2px 12px rgba(143, 188, 255, 0.15);
}
```

## Theme 2: dark-tech (深色科技蓝)
适合: 经典大屏、数据中心、监控场景
```css
:root {
    --bg-primary: #050b1f;
    --bg-gradient: radial-gradient(ellipse at top, #0a1f4a 0%, #050b1f 50%, #02061a 100%);
    --panel-bg: linear-gradient(180deg, rgba(10, 30, 70, 0.6) 0%, rgba(5, 15, 45, 0.4) 100%);
    --panel-border: rgba(95, 177, 255, 0.2);
    --text-primary: #cfe6ff;
    --text-secondary: #cfe6ff;
    --text-muted: #7faed9;
    --text-faint: #8aa7c9;
    --accent: #5fb1ff;
    --accent-light: #a8d4ff;
    --accent-pale: #1e4ba8;
    --warning: #ff9a3c;
    --success: #4ade80;
    --shadow: 0 0 20px rgba(95, 177, 255, 0.4);
}
```

## Theme 3: light-blue (淡蓝主调)
适合: 比 cream 更冷,需要蓝色主导感的场景
```css
:root {
    --bg-primary: #c4dcf5;
    --bg-gradient: linear-gradient(180deg, #a8c8ed 0%, #c4dcf5 50%, #e8f0fa 100%);
    --panel-bg: rgba(255, 255, 255, 0.65);
    --panel-border: rgba(74, 123, 184, 0.4);
    --text-primary: #1e3a6e;
    --text-secondary: #2c5fb8;
    --text-muted: #4a7bb8;
    --text-faint: #7aa9e0;
    --accent: #2c5fb8;
    --accent-light: #5fb1ff;
    --accent-pale: #a8c8ed;
    --warning: #ff9a3c;
    --success: #4ade80;
    --shadow: 0 2px 12px rgba(44, 95, 184, 0.2);
}
```

## 切换方式
1. 把上面的 `--*` 变量应用到 `:root`
2. 在需要切换时,改 `document.documentElement` 的 classList
3. 或者用更彻底的方案:把变量定义在 `:root` 然后所有组件都用 `var(--xxx)`

## 默认样式组件引用变量

```css
body {
    color: var(--text-primary);
    background: var(--bg-gradient);
}

.panel {
    background: var(--panel-bg);
    border: 1px solid var(--panel-border);
    box-shadow: var(--shadow);
}

.panel-title {
    color: var(--text-primary);
}

.panel-title::before {
    color: var(--accent);
}
```

## 选择指南
| 场景 | 推荐 |
|---|---|
| 业务驾驶舱(汇报) | **cream**(清爽阅读) |
| 数据中心监控 | **dark-tech**(科技感) |
| 工业能源 | **light-blue**(冷色调) |
| 金融银行 | **dark-tech**(高级感) |
| 政府公共 | **cream**(正式感) |
| 户外大屏 | **cream**(亮度高) |
| 用户问"参考图就这样" | 必须 match 参考图 |

## 混合使用
```css
/* cream 背景 + dark-tech 强调色(混合) */
:root {
    --bg-primary: #ffffff;       /* cream 底 */
    --accent: #5fb1ff;          /* 但用 dark 的强调色 */
}
```

实际项目里参考图是单一风格,不要混搭,会很乱。

## 颜色 token 检查清单
- 主背景 + 渐变
- 面板半透明背景
- 面板边框
- 标题文字主色
- 标题文字次色
- 描述/单位文字
- 主强调色(图表主色)
- 主强调色浅(图表次色)
- 主强调色背景(图表区域底)
- 警告色(数字气泡、active 状态)
- 成功色(可选)
- 阴影

把这 12 个 token 全部齐了就是一套完整配色。

