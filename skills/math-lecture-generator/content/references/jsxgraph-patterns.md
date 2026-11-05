---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100bec602540571fd7ca8282b59c667728d8df0d78ac9fa8973885b2c496b6fa824022100ceb2d6017b92c1b00b59b055dc7dda2f499f1cc7736ca304d28cfe07d30a960c
    ReservedCode2: 304502207244a038eb8e888e00c79f97e1f02efc57dcb14e2100975d4f146c9b0c976fb2022100ceef6d3e1c5b4ccc82854412aba000dfe2256d4c05381855f6061a0a153fbb09
---

# JSXGraph 常用模式参考

## 基础坐标轴设置

```javascript
// 创建画布
var board = JXG.JSXGraph.initBoard('jxgbox', {
    boundingbox: [-5, 5, 5, -5],
    axis: true,
    grid: true,
    showNavigation: true,
    showCopyright: false
});
```

## 常见交互模式

### 1. 可拖拽点 (Drag Point)

```javascript
// 创建可拖拽点
var p1 = board.create('point', [1, 2], {
    name: 'P',
    size: 5,
    color: 'blue',
    draggable: true
});
```

### 2. 滑动条控制器 (Slider)

```javascript
// 创建滑动条控制参数
var a = board.create('slider', [[-4, 3], [4, 3], [0, 1, 5]], {
    name: 'a',
    snapWidth: 0.1,
    digits: 2,
    baseline: { strokeColor: 'blue' },
    highline: { strokeColor: 'blue' }
});

// 使用滑动条值创建函数
var curve = board.create('functiongraph', [
    function(x) { return a.Value() * x + b.Value(); }
]);
```

### 3. 函数图像 (Function Graph)

```javascript
// 绘制函数图像
var f = board.create('functiongraph', [
    function(x) { return Math.sin(x); },
    -Math.PI, Math.PI
], {
    strokeColor: 'red',
    strokeWidth: 2
});
```

### 4. 参数曲线 (Parametric Curve)

```javascript
// 参数方程曲线（如星形线）
var curve = board.create('curve', [
    function(t) { return Math.cos(t) * Math.cos(t) * Math.cos(t); },
    function(t) { return Math.sin(t) * Math.sin(t) * Math.sin(t); },
    0, 2 * Math.PI
], {
    strokeColor: 'green',
    strokeWidth: 2
});
```

### 5. 三角函数相位演示

```javascript
// 创建多个控制滑动条
var A = board.create('slider', [[-4, 4], [4, 4], [0.5, 2, 3]], {
    name: '振幅 A'
});
var omega = board.create('slider', [[-4, 3], [4, 3], [0.5, 1, 3]], {
    name: '频率 ω'
});
var phi = board.create('slider', [[-4, 2], [4, 2], [-Math.PI, 0, Math.PI]], {
    name: '相位 φ'
});

// 动态正弦函数
var sineWave = board.create('functiongraph', [
    function(x) {
        return A.Value() * Math.sin(omega.Value() * x + phi.Value());
    }
], { strokeColor: 'blue', strokeWidth: 3 });
```

### 6. 解析几何动点轨迹

```javascript
// 创建椭圆上的动点
var ellipse = board.create('ellipse', [[0, 0], 4, 2]);

var movingPoint = board.create('point', [
    function() {
        var t = tParam.Value();
        return ellipse.center.X() + 4 * Math.cos(t);
    },
    function() {
        var t = tParam.Value();
        return ellipse.center.Y() + 2 * Math.sin(t);
    }
], { color: 'red', size: 5 });

// 角度滑动条
var tParam = board.create('slider', [[-4, -3], [4, -3], [0, 0, 2 * Math.PI]], {
    name: '参数 t'
});
```

### 7. 向量绘制

```javascript
var tail = board.create('point', [0, 0], { name: 'O' });
var head = board.create('point', [3, 2], { name: 'P' });

var vec = board.create('arrow', [tail, head], {
    strokeColor: 'darkblue',
    strokeWidth: 3
});

// 向量标签
var label = board.create('text', [
    function() { return (tail.X() + head.X()) / 2 + 0.2; },
    function() { return (tail.Y() + head.Y()) / 2; },
    function() { return '(' + head.X().toFixed(1) + ', ' + head.Y().toFixed(1) + ')'; }
], { fontSize: 14 });
```

### 8. 几何图形

```javascript
// 三角形
var vertices = board.create('polygon', [
    [0, 0], [4, 0], [2, 3]
], {
    fillColor: 'lightblue',
    lines: { strokeColor: 'blue' }
});

// 圆
var circle = board.create('circle', [[2, 2], 3], {
    strokeColor: 'red',
    fillColor: 'rgba(255,0,0,0.2)'
});

// 直线
var line = board.create('line', [[1, 1], [3, 3]], {
    strokeColor: 'green',
    dash: 2
});
```

## 完整示例：二次函数顶点式

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>二次函数顶点式演示</title>
    <script src="https://cdn.jsdelivr.net/npm/jsxgraph@1.4.6/distrib/jsxgraphcore.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jsxgraph@1.4.6/distrib/jsxgraph.css">
</head>
<body>
    <div id="jxgbox" class="jxgbox" style="width:600px; height:500px;"></div>
    <script>
        var board = JXG.JSXGraph.initBoard('jxgbox', {
            boundingbox: [-10, 10, 10, -10],
            axis: true,
            grid: true
        });

        // 滑动条控制参数
        var h = board.create('slider', [[-8, 8], [8, 8], [-5, 0, 5]], {
            name: 'h（顶点横坐标）'
        });
        var k = board.create('slider', [[-8, 6], [8, 6], [-5, 0, 5]], {
            name: 'k（顶点纵坐标）'
        });
        var a = board.create('slider', [[-8, 4], [8, 4], [-2, 1, 2]], {
            name: 'a（开口方向）'
        });

        // 动态函数图像
        var parabola = board.create('functiongraph', [
            function(x) {
                return a.Value() * Math.pow(x - h.Value(), 2) + k.Value();
            }
        ], { strokeColor: 'blue', strokeWidth: 3 });

        // 顶点标记
        var vertex = board.create('point', [
            function() { return h.Value(); },
            function() { return k.Value(); }
        ], { name: '顶点', color: 'red', size: 5 });
    </script>
</body>
</html>
```

## 样式配置参考

| 属性 | 用途 | 示例值 |
|------|------|--------|
| `strokeColor` | 线条颜色 | `'blue'`, `'#FF0000'` |
| `strokeWidth` | 线条宽度 | `2`, `3` |
| `fillColor` | 填充颜色 | `'lightyellow'` |
| `fillOpacity` | 填充透明度 | `0.3` |
| `dash` | 线型（虚线）| `1-6` 的数字 |
| `size` | 点的大小 | `3-8` |
| `fontSize` | 字体大小 | `12-20` |
| `visible` | 是否可见 | `true`, `false` |

## CDN 引入方式

```html
<!-- JSXGraph -->
<script src="https://cdn.jsdelivr.net/npm/jsxgraph@1.4.6/distrib/jsxgraphcore.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jsxgraph@1.4.6/distrib/jsxgraph.css">
```