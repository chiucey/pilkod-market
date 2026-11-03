/**
 * 中国地图渲染模式切换(2D / 3D)
 * 默认 2D,可运行时切换到 3D
 *
 * 2D 优势: 稳定、散点位置准确、数字标注正常
 * 3D 优势: 立体感、视觉冲击、适合震撼场景
 * 3D 劣势: 散点位置有 bug,label 不稳定,需 echarts-gl
 */
(function() {
    'use strict';

    /**
     * 2D 模式地图初始化
     */
    function init2DMap(dom, geoJson, data, options = {}) {
        echarts.registerMap('china', geoJson);
        const chart = echarts.init(dom);

        const option = {
            backgroundColor: 'transparent',
            tooltip: { /* ... */ },
            geo: {
                map: 'china',
                layoutCenter: ['50%', '52%'],
                layoutSize: '98%',
                roam: false,
                itemStyle: {
                    borderColor: '#bdd5f0',
                    borderWidth: 1,
                    shadowColor: 'rgba(143,188,255,0.3)',
                    shadowBlur: 12
                }
            },
            series: [
                {
                    type: 'map',
                    map: 'china',
                    geoIndex: 0,
                    data,
                    silent: true,
                    label: {
                        show: options.showLabels !== false,
                        color: '#1e3a6e',
                        fontSize: 10,
                        fontWeight: 'bold'
                    },
                    itemStyle: {
                        color: '#a8c8ed',
                        borderColor: '#bdd5f0',
                        borderWidth: 1
                    }
                },
                {
                    type: 'effectScatter',
                    coordinateSystem: 'geo',
                    data: options.highlights || [],
                    symbolSize: 10,
                    rippleEffect: { brushType: 'stroke', scale: 3, period: 4 },
                    itemStyle: { color: '#ff9a3c', shadowBlur: 12 }
                },
                {
                    type: 'lines',
                    coordinateSystem: 'geo',
                    data: options.lightColumns || [],
                    effect: { show: true, period: 4, symbol: 'arrow', symbolSize: 4 },
                    lineStyle: { width: 1.5, color: '#4a7bb8' }
                }
            ]
        };

        chart.setOption(option);
        return chart;
    }

    /**
     * 3D 模式地图初始化
     */
    function init3DMap(dom, geoJson, data, options = {}) {
        echarts.registerMap('china', geoJson);
        const chart = echarts.init(dom, null, { renderer: 'canvas' });

        const option = {
            backgroundColor: 'transparent',
            tooltip: { /* ... */ },
            geo3D: { map: 'china', show: false },

            visualMap: {
                show: false,
                min: 0,
                max: 50000,
                inRange: { color: ['#dde8f5', '#a8c8ed', '#7aa9e0'] }
            },

            series: [{
                type: 'map3D',
                map: 'china',
                data,
                boxHeight: 5,
                boxWidth: 120,
                boxDepth: 90,
                regionHeight: 4,

                itemStyle: {
                    opacity: 0.95,
                    borderWidth: 0.6,
                    borderColor: '#a0c4f0'
                },

                light: {
                    main: { color: '#5fb1ff', intensity: 1.0, alpha: 60, beta: 10 },
                    ambient: { color: '#f5f9fd', intensity: 0.6 }
                },

                viewControl: {
                    projection: 'orthographic',
                    alpha: 80,    // 接近俯视
                    beta: 0,
                    distance: 150
                },

                label: { show: false }  // map3D label 不可靠,改 tooltip
            }]
        };

        chart.setOption(option);
        return chart;
    }

    /**
     * 地图管理器 - 封装 2D/3D 切换
     */
    class MapManager {
        constructor(domId, geoJson, data) {
            this.dom = document.getElementById(domId);
            this.geoJson = geoJson;
            this.data = data;
            this.mode = '2D';
            this.chart = null;
            this._init();
        }

        _init() {
            if (this.chart) {
                this.chart.dispose();
                this.chart = null;
            }
            echarts.registerMap('china', this.geoJson);

            if (this.mode === '3D') {
                this.chart = init3DMap(this.dom, this.geoJson, this.data);
            } else {
                this.chart = init2DMap(this.dom, this.geoJson, this.data);
            }
        }

        setMode(mode) {
            if (mode !== '2D' && mode !== '3D') return;
            this.mode = mode;
            this._init();
        }

        highlight(name) {
            // 触发已有 chart 的高亮逻辑
            if (this.chart && this.chart._highlight) {
                this.chart._highlight(name);
            }
        }

        clear() {
            if (this.chart && this.chart._clear) {
                this.chart._clear();
            }
        }

        getChart() {
            return this.chart;
        }

        dispose() {
            if (this.chart) {
                this.chart.dispose();
                this.chart = null;
            }
        }
    }

    // 暴露 API
    window.MapManager = MapManager;
    window.init2DMap = init2DMap;
    window.init3DMap = init3DMap;
})();