# 13 个常见踩坑(已踩过 + 解决)

## 1. ECharts CDN 被墙 → 页面 empty
**症状**: 打开本地 HTML 图表不显示,控制台 `Failed to load resource`
**原因**: jsDelivr/cdnjs 在某些网络环境下无法访问
**解决**: 
```bash
curl -sSL "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js" -o assets/echarts.min.js
curl -sSL "https://cdn.jsdelivr.net/npm/echarts-gl@2.0.9/dist/echarts-gl.min.js" -o assets/echarts-gl.min.js
```
index.html 用本地引用:
```html
<script src="assets/echarts.min.js"></script>
<script src="assets/echarts-gl.min.js"></script>
```

## 2. echarts-gl 2.x 的 3D 散点位置漂移
**症状**: scatter3D / effectScatter 用 `coordinateSystem: 'geo3D'` 时,点位置飞到地图外部
**原因**: echarts-gl 2.0.9 在 geo3D 坐标系下对 [lng, lat] 转屏幕坐标的算法有 bug
**解决**: 改用 2D geo,放弃 3D 散点/光柱
```js
option: {
    geo: {
        map: 'china',
        roam: false,
        layoutCenter: ['50%', '52%'],
        layoutSize: '98%'
    },
    series: [{
        type: 'effectScatter',
        coordinateSystem: 'geo',  // ← 用 2D geo 而非 geo3D
        data: [{ name, value: [lng, lat, val] }]
    }]
}
```

## 3. visualMap 覆盖 per-item itemStyle.color
**症状**: 高亮想用 `data[i].itemStyle.color: '#ff9a3c'`,但视觉上没变化
**原因**: map3D/map 系列里,visualMap 的 inRange.color 优先级高于 itemStyle
**解决 A — 去掉 visualMap,每个数据项自带颜色**:
```js
const colorBy = v => {
    const ratio = (v - minV) / (maxV - minV);
    if (ratio < 0.33) return '#dde8f5';
    if (ratio < 0.66) return '#a8c8ed';
    return '#7aa9e0';
};
data: provinceData.map(p => ({
    name: p.name, value: p.value,
    itemStyle: { color: colorBy(p.value) }  // ← 直接给
}))
```
**解决 B — 高亮时显式覆盖所有项的 itemStyle(不用 color: null)**:
```js
data.map(d => d.name === activeName ? {...d, itemStyle: {color:'#ff9a3c',...}} : {...d, itemStyle: {color: colorBy(d.value),...}})
```

## 4. map3D label 渲染不出来
**症状**: 设了 `label.show: true`,实际看不到任何 label
**原因**: echarts-gl 2.0.9 的 map3D label 有 bug,某些版本直接不渲染
**解决**: 
- 用 `label.show: false` 关闭 map3D 自带 label
- 改用 tooltip 显示详细信息(hover 时)
- 重要省份用单独的 effectScatter + label 显示

## 5. setOption 默认是 merge,改 itemStyle 会残留
**症状**: 改某个 item 的 itemStyle 后,其他 item 的同名字段也变了
**原因**: ECharts 默认 merge 模式,新 setOption 的部分字段会和旧的合并
**解决**:
- 每次 setOption 都明确写出所有相关 itemStyle(避免部分更新)
- 或者用 `{...d, itemStyle: {...全部字段...}}` 整体替换
- 极端情况用 `notMerge: true` 强制整体重置(慎用,会丢其他配置)

## 6. flex: 1 撑满压缩重要 panel
**症状**: 总计卡片用 `flex: 1`,被 flex: 1 的图表挤到看不见
**原因**: flex 容器里多个 flex: 1 子项会等分空间
**解决**: 关键 panel 用 `flex: 0 0 auto`(固定高度),其他用 `flex: 1` 撑满剩余
```css
.summary-main { flex: 0 0 auto; }   /* 固定高度 */
.summary-grid { flex: 0 0 auto; }
.quarter-panel, .equipment-panel { flex: 1 1 0; }  /* 撑满剩余 */
```

## 7. 写死像素不响应 200% 系统缩放
**症状**: 用户设了"放大到 200%",所有内容显得更大但布局错位
**原因**: CSS 用 `100vw/100vh` 或写死 px,但 Windows 的"放大"不改变 viewport,改变的是 DPI
**解决 — 用 transform scale 而不是重写 vw/vh**:
```css
#app {
    width: 1920px; height: 1080px;
    position: absolute; left: 50%; top: 50%;
    transform: translate(-50%,-50%) scale(var(--scale));
}
```
```js
function fitScale() {
    const scale = Math.min(innerWidth/1920, innerHeight/1080);
    document.documentElement.style.setProperty('--scale', scale);
}
window.addEventListener('resize', fitScale);
fitScale();
```

## 8. coordinateSystem 选错
**症状**: 用 `coordinateSystem: 'cartesian3D'` 配 geo3D 数据,地图完全不显示
**原因**: cartesian3D 是立方体坐标系,geo3D 是经纬度坐标系,两者不能混用
**解决**: 根据 series 类型选:
- `map3D` → 内部自带 geo3D 坐标系,data 用 `{name, value}`
- `effectScatter/bar/scatter3D` → 必须指定 `coordinateSystem: 'geo3D'`,data 用 [lng, lat, val]
- 2D 模式 → `coordinateSystem: 'geo'`,配 `geo` 组件

## 9. fetch 加载 CDN 地图静默失败
**症状**: 控制台没报错,但地图一直不显示
**原因**: fetch 失败 catch 里啥也不做
**解决**: 同时加载本地 + CDN,本地失败回退 CDN:
```js
async function loadChinaMap() {
    const sources = ['./assets/china.json', 'https://geo.datav.aliyun.com/...'];
    for (const url of sources) {
        try {
            const res = await fetch(url);
            if (res.ok) return await res.json();
        } catch (e) { /* 试下一个 */ }
    }
    throw new Error('所有源都失败');
}
```

## 10. SVG `<symbol use>` 不能外部引用
**症状**: `<use href="icons.svg#wind">` 无效,console warning 找不到 fragment
**原因**: 浏览器对外部 SVG 的 use 引用支持不一致
**解决**: 把 SVG 直接 inline 到 HTML:
```html
<div class="summary-card">
    <svg class="icon" viewBox="0 0 64 64">
        <path d="..."/>
    </svg>
</div>
```

## 11. setOption notMerge 误用丢配置
**症状**: 用 `notMerge: true` 想重置,但其他 series 也没了
**原因**: notMerge 强制整体替换,会丢所有未指定的 series 配置
**解决**: 99% 情况用默认 merge,只在"完全重置"时用 notMerge:
```js
// 改一两个 series,用 merge(默认)
chart.setOption({ series: [{ data: newData }] });

// 完全重置(例如切换主题),才用 notMerge
chart.setOption(newOption, true);
```

## 12. map3D 默认视角是侧视
**症状**: alpha: 25 默认值,地图看起来像 45 度侧视,不是俯视
**原因**: echarts-gl map3D viewControl.alpha 默认 25(俯角),用户要的是接近 90 度俯视
**解决**:
```js
viewControl: {
    alpha: 80,           // ← 接近 90 是正俯视
    beta: 0,
    minAlpha: 60,        // 限制最小俯角
    maxAlpha: 90,
    projection: 'orthographic'  // ← 用正交投影避免透视变形
}
```

## 13. "字体偏小"几乎永远是
**症状**: 用户说"字体小了点"几乎每次都成立
**原因**: 默认字号偏保守,大屏场景下要更大才显得不空
**解决**:
- 头部标题: 38-46px
- 面板标题: 16-18px
- 总计大数字: 32-40px
- 表格文字: 12-14px
- 用 `min-height` 防止被 flex 压缩时字号也变形

## 总结:避坑口诀
**离线 / 2D / inline / merge / scale(1920) / transform / 自检**
- 离线优先(本地资源)
- 2D 替代 3D(避开 echarts-gl bug)
- inline SVG(避免外部引用)
- merge 模式改 itemStyle(避免残留)
- scale 1920(自适应)
- transform(布局核心)
- 自检截图(最后一步)

