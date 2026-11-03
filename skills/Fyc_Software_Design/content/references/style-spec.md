# 视觉样式规范(配色 / 字体 / 交互)

完整记录"风力能源监控"风格的视觉规范,作为大屏默认实现。所有颜色 / 字号 / 间距 / 交互细节按本文档执行。

---

## 一、全局配色

### 主背景
```css
/* 奶油白渐变 */
background: radial-gradient(ellipse at top, #e8f1fa 0%, #f5f9fd 50%, #ffffff 100%);
```
- 顶部 `#e8f1fa`(极淡蓝)
- 中部 `#f5f9fd`(近白)
- 底部 `#ffffff`(纯白)

### 文字色阶(共 4 档)
| 用途 | 颜色 | 示例 |
|---|---|---|
| 主标题 / 大数字 | `#1e3a6e` | 标题"风力能源监控" / 总计数字 |
| 次级文字 | `#3a5a8c` | 面板标题、标签 |
| 描述文字 | `#6b8fc4` | 单位、副标题 |
| 弱化文字 | `#8aa7c9` | 角落标签、占位 |

### 强调色(蓝色 4 档)
| 用途 | 颜色 |
|---|---|
| 主按钮 / 边框 | `#1e3a6e` |
| 图表主色 | `#4a7bb8` |
| 亮蓝 / 光柱 | `#8fbcff` |
| 极浅淡蓝 | `#dde8f5` |

### 警示色
- 警告 / 高亮: `#ff9a3c`(橙色)
- 危险 / 异常: `#f87171`(红色)
- 良好: `#4ade80`(绿色)

### 面板背景
```css
background: rgba(255, 255, 255, 0.78);
backdrop-filter: blur(6px);
border: 1px solid rgba(143, 188, 255, 0.4);
box-shadow: 0 2px 12px rgba(143, 188, 255, 0.15);
```
- 半透明白 + 蓝色边框 + 轻阴影
- 浮在地图背景之上

### 面板四角装饰
```css
.panel::before, .panel::after,
.panel > .corner-tl, .panel > .corner-tr,
.panel > .corner-bl, .panel > .corner-br {
    border-color: #4a7bb8;
    border-width: 2px;  /* 仅角,12x12 */
}
```
- 四角用 `#4a7bb8` 蓝色 2px 实线
- 视觉上像"取景框"

---

## 二、中国地图(默认 2D 满屏模式)

### 地图背景填色(三档渐变,按 value)
```js
const colorBy = v => {
    const ratio = (v - minV) / (maxV - minV);
    if (ratio < 0.33) return '#dde8f5';   // 极浅蓝
    if (ratio < 0.66) return '#a8c8ed';   // 浅蓝
    return '#7aa9e0';                     // 中蓝
};
```

### 地图描边
```js
itemStyle: {
    borderColor: '#bdd5f0',
    borderWidth: 1
}
```

### 4 个高优省份标注点
```js
{
    type: 'effectScatter',
    coordinateSystem: 'geo',
    symbolSize: 8,
    itemStyle: {
        color: '#4a7bb8',
        shadowColor: '#8fbcff',
        shadowBlur: 12,
        borderColor: '#fff',
        borderWidth: 2
    },
    label: {
        backgroundColor: 'rgba(220,235,250,0.95)',
        borderColor: '#7aa9e0',
        borderRadius: 3,
        color: '#1e3a6e',
        padding: [4, 8]
    },
    rippleEffect: { scale: 3, period: 4, color: '#8fbcff' }
}
```

### 光柱(垂直延伸线)
```js
{
    type: 'lines',
    lineStyle: {
        width: 1.5,
        color: { type: 'linear', colorStops: [
            { offset: 0, color: '#4a7bb8' },
            { offset: 1, color: 'rgba(143,188,255,0)' }
        ]}
    },
    effect: {
        show: true, period: 4,
        symbol: 'arrow', symbolSize: 4,
        color: '#8fbcff'
    }
}
```

### 地图交互
| 操作 | 效果 |
|---|---|
| hover 省份 | tooltip 显示"省名 + 装机容量(MW)" |
| click 省份 | 高亮该省(橙色 #ff9a3c)+ 联动到表格/TOP10 |
| hover 高优点 | 显示数字气泡(已经在数据中) |
| click 高优点 | 同 click 省份(联动到所属省) |
| 跑马灯 | 右上角 11 个次优省份 2.8s 切换 |

---

## 三、八大图表配色与样式

### 1. TOP10 排行榜
```js
{
    type: 'bar',
    barWidth: 2,  // 细线
    itemStyle: {
        color: { type: 'linear', x2: 1, colorStops: [
            { offset: 0, color: 'rgba(143,188,255,0)' },     // 起点透明
            { offset: 0.6, color: 'rgba(143,188,255,0.5)' }, // 中段半透明
            { offset: 1, color: '#4a7bb8' }                  // 终点深蓝
        ]}
    },
    markPoint: {
        symbol: 'circle', symbolSize: 9,
        itemStyle: {
            color: '#8fbcff',
            borderColor: '#fff',
            borderWidth: 2
        }
    },
    label: {
        color: '#1e3a6e',
        fontSize: 13,
        fontFamily: 'Consolas, monospace'
    }
}
```
- 高亮态: 线条渐变改成 `rgba(255,154,60,0)` → `#ff9a3c`(橙色)

### 2. 双折线(发电/损耗)
```js
// 发电量(主,带面积)
{
    name: '发电量', type: 'line', smooth: true,
    lineStyle: { width: 2.5, color: '#4a7bb8' },
    symbol: 'circle', symbolSize: 6,
    itemStyle: { color: '#4a7bb8', borderColor: '#fff', borderWidth: 1 },
    areaStyle: {
        color: { type: 'linear', y2: 1, colorStops: [
            { offset: 0, color: 'rgba(143,188,255,0.4)' },
            { offset: 1, color: 'rgba(143,188,255,0)' }
        ]}
    }
},
// 损耗量(次,纯线)
{
    name: '损耗量', type: 'line', smooth: true,
    lineStyle: { width: 2, color: '#ff9a3c' },
    symbol: 'circle', symbolSize: 5,
    itemStyle: { color: '#ff9a3c' }
}
```
- 折线 + 圆点(`#fff` 白边)
- Y 轴标签格式:`{value/10000}w`

### 3. 表格(白底 + 颜色色阶)
```js
// 损耗率颜色映射
const TAG_COLOR = {
    good:    '#4ade80',   // < 10% 绿
    normal:  '#5fb1ff',   // < 30% 蓝
    warning: '#fbbf24',   // < 60% 黄
    danger:  '#f87171'    // > 60% 红
};
```
- 表格 hover: `background: rgba(143,188,255,0.12)`
- active: `background: rgba(255,154,60,0.18) + box-shadow: inset 3px 0 0 #ff9a3c`
- 数字右对齐 + Consolas 字体 + 加粗

### 4. 中国地图
- 已单独规范(见第二节)

### 5. 季度环形图(4 色)
```js
const colors = ['#4a7bb8', '#ff9a3c', '#4ade80', '#a78bfa'];
// 第1季度(深蓝) / 第2季度(橙) / 第3季度(绿) / 第4季度(紫)
```
- 半径: `['52%', '72%']`
- 中心文字: 季度名(浅) + 数值(深)
- 右侧图例: 色块 + 季度名 + 百分比
- 边框: `borderColor: '#fff', borderWidth: 2`

### 6. 柱状图(双系列渐变填充)
```js
// 运行设备(主)
{
    barWidth: 12,
    itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: { type: 'linear', y2: 1, colorStops: [
            { offset: 0, color: '#4a7bb8' },                  // 顶部深蓝
            { offset: 1, color: 'rgba(143,188,255,0.3)' }     // 底部浅蓝透明
        ]}
    }
},
// 新增设备(次)
{
    barWidth: 12,
    itemStyle: {
        borderRadius: [4, 4, 0, 0],
        color: { type: 'linear', y2: 1, colorStops: [
            { offset: 0, color: '#ff9a3c' },
            { offset: 1, color: 'rgba(255,154,60,0.3)' }
        ]}
    }
}
```
- 圆角顶部 4px
- Y 轴标签:`{value/1000}K`

### 7. 总计卡片(大数字 + SVG 图标)
```js
// 总设备 - 风电场 SVG(底座梯形 + 3 杆塔 + 3 风叶)
{
    itemStyle: {
        color: '#a8c8ed → #4a7bb8' 渐变底座
    },
    lineColor: '#3a5a8c' 杆塔
}
// 总员工 - 橙色人形 SVG
{
    headColor: '#ffaa55' 头部
    bodyColor: '#ff9a3c' 身体
}
```
- 卡片: `padding: 14px`
- 图标尺寸: 48px
- 数字: 22px Consolas 加粗
- 滤镜: `filter: drop-shadow(0 2px 4px rgba(143,188,255,0.3))`

### 8. 趋势 sparkline
```js
{
    type: 'line', smooth: true,
    symbol: 'circle', symbolSize: 4,
    lineStyle: { width: 2, color: '#4a7bb8' },
    itemStyle: { color: '#4a7bb8', borderColor: '#fff', borderWidth: 1 },
    areaStyle: {
        color: { type: 'linear', y2: 1, colorStops: [
            { offset: 0, color: 'rgba(143,188,255,0.5)' },
            { offset: 1, color: 'rgba(143,188,255,0)' }
        ]}
    }
}
```

---

## 四、字体规范

### 字号标准(硬性)
```css
.header-title { font-size: 46px; }            /* 主标题 */
.header-time .clock { font-size: 40px; }     /* 时钟 */
.summary-main .total-value { font-size: 38px; }  /* 总计数字 */
.summary-card .info .value { font-size: 22px; }   /* 总设备/总员工 */
.tab-item { font-size: 20px; }                /* Tab 文字 */
.panel-title { font-size: 18px; }            /* 面板标题 */
.header-time .weekday { font-size: 17px; }    /* 星期 */
.header-time .date { font-size: 16px; }       /* 日期 */
.summary-card .info .label { font-size: 14px; } /* 卡片标签 */
.summary-main .label { font-size: 15px; }    /* 总计标签 */
.panel-title .unit { font-size: 13px; }      /* 单位 */
.marquee-item .name { font-size: 15px; }     /* 跑马灯名字 */
.marquee-item .value { font-size: 14px; }   /* 跑马灯数值 */
.marquee-title { font-size: 13px; }          /* 跑马灯标题 */
.summary-card .info .value .unit { font-size: 12px; } /* 总单位 */
```

### 字体栈
```css
/* 主字体:无衬线 */
font-family: 'Microsoft YaHei', 'PingFang SC', 'Helvetica Neue', sans-serif;

/* 等宽字体(数字) */
font-family: 'Consolas', 'Monaco', monospace;
```

### 字重
- 主标题: 700
- 面板标题: 700
- 大数字: 700
- 标签: 600
- 描述: normal

---

## 五、间距 / 圆角 / 阴影

### 间距
- 头部 padding: `0 20px`
- 面板 padding: `14px 12px 12px`
- 面板标题距下: `margin-bottom: 8-10px`
- Tab gap: `80px`
- 跑马灯 padding: `10px 14px`
- 总计卡片 gap: `12px`

### 圆角
- 面板 / 卡片: `4px`
- 跑马灯: `6px`
- Tab 文字容器: `4px`
- 气泡标签: `3px`

### 阴影
```css
/* 卡片轻阴影 */
box-shadow: 0 2px 12px rgba(143, 188, 255, 0.15);

/* 跑马灯加深 */
box-shadow: 0 4px 16px rgba(143, 188, 255, 0.2);

/* 图表图标 drop-shadow */
filter: drop-shadow(0 2px 4px rgba(143, 188, 255, 0.3));
```

---

## 六、交互行为

### 高亮状态
- 地图省份高亮: `#ff9a3c` + 白色边框 + 透明度 1
- 表格行高亮: 浅橙背景 + 左侧橙色 3px 边框
- TOP10 项高亮: 线条变橙渐变

### 联动
```js
// 表格 hover → 地图 + TOP10 联动
tr.onmouseenter = () => {
    windMap.highlight(province);
    windTop10.highlightByProvince(province);
};
// 离开 → 全部清除

// 地图 click → 表格 + TOP10 联动
chart.on('click', params => {
    if (params.seriesType === 'map') {
        windMap.highlight(params.name);
        syncFromMap(params.name);  // 同步表格 + TOP10
    }
});
```

### 跑马灯
- 切换间隔: 2800ms
- 动画: `transition: transform 0.5s ease + opacity 0.5s ease`
- 当前项: `translateY(0) + opacity 1`
- 退出项: `translateY(-100%) + opacity 0`
- 进入项: `translateY(100%) + opacity 0`(再切到 active)

### Esc 键清空
```js
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
        windMap.clear();
        windTop10.clear();
        windTable.clear();
    }
});
```

### Tab 激活态
- 颜色: `#1e3a6e` + 700 字重
- 下方弧形发光:
```css
.tab-item.active::after {
    content: '';
    position: absolute; bottom: -6px;
    left: 50%; transform: translateX(-50%);
    width: 60%; height: 8px;
    background: radial-gradient(ellipse, rgba(143,188,255,0.8) 0%, transparent 70%);
    box-shadow: 0 4px 16px rgba(143,188,255,0.6);
}
```

---

## 七、CSS 变量(主题切换用)

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
    --danger: #f87171;
    --shadow: 0 2px 12px rgba(143, 188, 255, 0.15);
}
```

切换主题只需替换这些变量值即可,不需要改组件代码。

---

## 八、与其他主题对照(参考)

| 项目 | cream(默认) | dark-tech | light-blue |
|---|---|---|---|
| 主背景 | 奶油白渐变 | 深蓝 | 淡蓝 |
| 主文字 | `#1e3a6e` 深蓝近黑 | `#cfe6ff` 浅蓝 | `#1e3a6e` 深蓝 |
| 强调色 | `#4a7bb8` | `#5fb1ff` | `#2c5fb8` |
| 面板 | 半透明白 + 蓝边 | 半透明深蓝 + 浅蓝边 | 半透明白 + 中蓝边 |
| 阴影 | 浅淡蓝 | 深蓝发光 | 中等蓝 |

**默认 cream** 是因为参考图就是 cream。其他主题作为可选。