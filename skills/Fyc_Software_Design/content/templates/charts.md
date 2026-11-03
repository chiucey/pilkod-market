# 八大图表模块速查

## 1. TOP10 排行榜(细线 + 圆点)
```js
{
    type: 'bar',
    barWidth: 2,  // ← 细线
    itemStyle: {
        color: { type: 'linear', colorStops: [
            { offset: 0, color: 'rgba(143,188,255,0)' },
            { offset: 1, color: '#4a7bb8' }
        ]}
    },
    markPoint: {
        symbol: 'circle', symbolSize: 9,
        data: [...],
        itemStyle: { color: '#8fbcff', borderColor: '#fff', borderWidth: 2 }
    }
}
```

## 2. 双折线对比(发电/损耗)
```js
{
    name: '发电量',
    type: 'line',
    smooth: true,
    data: [...],
    lineStyle: { width: 2.5, color: '#4a7bb8' },
    areaStyle: {  // ← 一根带面积,一根线
        color: { type: 'linear', colorStops: [
            { offset: 0, color: 'rgba(143,188,255,0.4)' },
            { offset: 1, color: 'rgba(143,188,255,0)' }
        ]}
    }
}
```

## 3. 表格(自渲染 HTML)
```js
// 不要用 echarts 表格,直接 DOM 渲染更灵活
const rows = data.map(r => `
    <tr data-province="${r.province}">
        <td>${r.province}</td>
        <td class="num">${r.generated}</td>
        <td class="num">${r.lost}</td>
        <td class="rate" style="color:${tagColor[r.tag]}">${r.rate}%</td>
    </tr>
`).join('');
container.innerHTML = `<table class="loss-table">...${rows}...</table>`;
```

## 4. 中国地图(2D geo + 高优 + 跑马灯)
```js
// 关键: 2D geo(避开 echarts-gl 散点 bug)
{
    geo: {
        map: 'china', roam: false,
        layoutCenter: ['50%', '52%'],
        layoutSize: '98%',
        itemStyle: { borderColor: '#bdd5f0' }
    },
    series: [
        // 主体地图填充
        { type: 'map', map: 'china', geoIndex: 0, data: mapData, silent: true },
        // 4个高优省份光柱
        { type: 'lines', coordinateSystem: 'geo', data: linesData,
          lineStyle: { color: ..., width: 1.5 } },
        // 4个高优省份标注点(带数字气泡)
        { type: 'effectScatter', coordinateSystem: 'geo', data: highlights,
          label: { show: true, formatter: p => `${p.value[2]}MW\n${p.name}` } }
    ]
}
```

## 5. 季度环形图(用 graphic 自定义图例)
```js
{
    type: 'pie',
    radius: ['52%', '72%'],
    label: { show: false },
    data: [
        { name: 'Q1', value: 48.28, itemStyle: { color: '#4a7bb8' } },
        { name: 'Q2', value: 18.97, itemStyle: { color: '#ff9a3c' } },
        ...
    ]
},
// 用 graphic 画右侧图例 + 中心文字
{
    graphic: [
        { type: 'rect', shape: { width: 10, height: 10 }, style: { fill: '#4a7bb8' } },
        { type: 'text', style: { text: '第一季度' } },
        ...
    ]
}
```

## 6. 柱状图(双系列)
```js
[
    { name: '运行设备', type: 'bar', barWidth: 12, data: [...],
      itemStyle: { color: { type: 'linear', x2: 0, y2: 1, colorStops: [...] } } },
    { name: '新增设备', type: 'bar', barWidth: 12, data: [...],
      itemStyle: { color: { type: 'linear', ... } } }
]
```

## 7. 总计卡片 + SVG 图标
```html
<div class="summary-card">
    <svg class="icon icon-wind" viewBox="0 0 64 64">
        <path d="M8 50 L20 32 L44 32 L56 50 Z" fill="url(#windGrad)"/>
        <line x1="22" y1="32" x2="22" y2="14" stroke="#3a5a8c"/>
        <!-- 风车叶片 -->
    </svg>
    <div class="info">
        <div class="label">总设备</div>
        <div class="value">21,789 <span class="unit">台</span></div>
    </div>
</div>
```

## 8. 趋势小图(sparkline)
```js
{
    type: 'line',
    smooth: true,
    showSymbol: false,
    data: trend,
    lineStyle: { width: 2, color: '#4a7bb8' },
    areaStyle: { color: { type: 'linear', y2: 1, colorStops: [...] } }
}
```

## 联动 API 标准模式
```js
// 图表 1(地图)暴露 API
window.windMap = {
    highlight(name) { /* 改 data 内联 itemStyle */ },
    clear() { /* 恢复 base */ }
};

// 在 main.js 提供桥接
window.syncFromMap = (prov, siteName) => {
    window.windTable.highlight(prov);
    window.windTop10.highlightByProvince(prov);
};

// 点击事件
chart.on('click', params => {
    if (params.seriesType === 'map') {
        window.windMap.highlight(params.name);
        window.syncFromMap(params.name);
    }
});
```

## 数据结构模板
```js
window.DATA = {
    province: [{ name, value, coord, highlighted }],
    top10: [{ rank, name, value, coord, province }],
    table: [{ province, generated, lost, rate, tag }],
    quarter: [{ name, value }],
    equipment: [{ month, running, newAdd }],
    summary: { totalPower, totalDevices, totalEmployees, trend }
};
```

