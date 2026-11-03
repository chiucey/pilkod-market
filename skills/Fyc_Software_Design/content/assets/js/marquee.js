/**
 * 跑马灯 - 列表轮播切换
 * @param {Array} list - 待轮播项 [{name, value}]
 * @param {string} containerId - 容器 DOM id
 * @param {number} interval - 切换间隔(ms),默认 2800
 */
(function() {
    'use strict';

    window.startMarquee = function(list, containerId, interval = 2800) {
        if (!Array.isArray(list) || !list.length) return;
        const container = document.getElementById(containerId);
        if (!container) return;

        // 创建 DOM 节点(默认隐藏)
        list.forEach((item, i) => {
            const name = item.name ?? '';
            const value = item.value ?? '';
            const el = document.createElement('div');
            el.className = 'marquee-item';
            el.innerHTML = `<span class="name">${name}</span><span class="value">${value}</span>`;
            container.appendChild(el);
        });

        const items = Array.from(container.querySelectorAll('.marquee-item'));
        if (!items.length) return;

        let idx = 0;
        items[idx].classList.add('active');  // 第一项立即显示

        setInterval(() => {
            // 当前项退出(向上滑出)
            items[idx].classList.remove('active');
            items[idx].classList.add('exit');

            // 下一项进入
            const next = (idx + 1) % items.length;
            items[next].classList.remove('exit');
            items[next].classList.add('active');

            idx = next;
        }, interval);
    };
})();