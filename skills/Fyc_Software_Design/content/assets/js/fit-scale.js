/**
 * 大屏等比缩放(1920x1080 设计稿)
 * 适配任意视口大小,系统 DPI 缩放不影响
 */
(function() {
    'use strict';

    const DESIGN_W = 1920;
    const DESIGN_H = 1080;

    function fitScale() {
        const sw = document.documentElement.clientWidth;
        const sh = document.documentElement.clientHeight;
        const scale = Math.min(sw / DESIGN_W, sh / DESIGN_H);
        document.documentElement.style.setProperty('--scale', String(scale));
    }

    window.addEventListener('resize', fitScale);
    window.addEventListener('orientationchange', fitScale);
    fitScale();

    // 提供外部调用,用户可手动触发(比如 ECharts 重渲染前)
    window.fitScreen = fitScale;
})();