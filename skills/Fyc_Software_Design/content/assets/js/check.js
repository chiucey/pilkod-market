/**
 * 大屏启动时自检 + 自修正
 * 用于自动化测试时加载,生产环境可移除
 */
(function() {
    'use strict';

    window.addEventListener('error', e => {
        console.error('[大屏错误]', e.message, e.filename, e.lineno);
        document.body.classList.add('has-error');
    });

    // ECharts 加载失败检测(空容器)
    setTimeout(() => {
        const mapChart = document.getElementById('mapChart');
        if (mapChart && !echarts.getInstanceByDom(mapChart)) {
            console.warn('[自检] 地图实例未创建');
        }
    }, 3000);

    // 联动 API 存在性
    const required = ['windMap', 'windTop10', 'windTable', 'syncFromMap', 'syncFromTop10'];
    const missing = required.filter(n => !window[n]);
    if (missing.length) {
        console.warn('[自检] 缺失 API:', missing.join(', '));
    } else {
        console.log('[自检] 联动 API 完整');
    }
})();