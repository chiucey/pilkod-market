/**
 * 实时时速表应用
 * 使用 Geolocation API 获取 GPS 速度数据
 */

class SpeedMeter {
    constructor() {
        // DOM 元素
        this.settingsPanel = document.getElementById('settings-panel');
        this.speedDisplay = document.getElementById('speed-display');
        this.permissionOverlay = document.getElementById('permission-overlay');

        // 状态
        this.currentSpeed = 0;
        this.currentStyle = 'classic-pointer';
        this.currentUnit = 'kmh';
        this.currentSize = 'medium';
        this.currentColor = '#0a0a0f';
        this.watchId = null;
        this.isRunning = false;

        // 速度元素映射
        this.speedElements = {
            'classic-pointer': document.getElementById('speed-value'),
            'neon-digital': document.getElementById('neon-speed-value'),
            'minimal-digital': document.getElementById('minimal-speed-value'),
            'mechanical': document.getElementById('mech-speed'),
            'gradient-digital': document.getElementById('gradient-speed-value'),
            'holographic': document.getElementById('holo-speed-value'),
            'retro-pointer': document.getElementById('retro-speed'),
            'sci-fi': document.getElementById('scifi-speed'),
            'sport': document.getElementById('sport-speed'),
            'ink-wash': document.getElementById('ink-speed')
        };

        // 指针元素映射
        this.needleElements = {
            'classic-pointer': document.getElementById('needle'),
            'mechanical': document.getElementById('mech-needle'),
            'retro-pointer': document.getElementById('retro-needle'),
            'sport': document.getElementById('sport-needle')
        };

        // 初始化
        this.loadSettings();
        this.bindEvents();
    }

    // 加载保存的设置
    loadSettings() {
        const settings = JSON.parse(localStorage.getItem('speedMeterSettings') || '{}');
        if (settings.style) this.currentStyle = settings.style;
        if (settings.unit) this.currentUnit = settings.unit;
        if (settings.size) this.currentSize = settings.size;
        if (settings.color) this.currentColor = settings.color;

        // 应用设置到UI
        this.applySettingsToUI();
    }

    // 应用设置到UI
    applySettingsToUI() {
        // 样式
        document.querySelectorAll('.style-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.style === this.currentStyle);
        });

        // 单位
        document.querySelectorAll('.unit-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.unit === this.currentUnit);
        });

        // 大小
        document.querySelectorAll('.size-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.size === this.currentSize);
        });

        // 颜色
        document.querySelectorAll('.color-preset').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.color === this.currentColor);
        });
        document.getElementById('custom-color').value = this.currentColor;

        // 背景颜色
        document.body.style.background = this.currentColor;
        this.speedDisplay.style.background = this.currentColor;
        document.documentElement.style.setProperty('--bg-color', this.currentColor);

        // 字体大小
        this.applyFontSize();
    }

    // 应用字体大小
    applyFontSize() {
        document.body.classList.remove('font-small', 'font-medium', 'font-large', 'font-xlarge');
        document.body.classList.add(`font-${this.currentSize}`);
    }

    // 绑定事件
    bindEvents() {
        // 样式选择
        document.querySelectorAll('.style-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.style-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentStyle = btn.dataset.style;
                this.saveSettings();
                this.updateStyleDisplay();
            });
        });

        // 单位切换
        document.querySelectorAll('.unit-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.unit-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentUnit = btn.dataset.unit;
                this.saveSettings();
                this.updateUnitLabels();
                this.displaySpeed(this.currentSpeed);
            });
        });

        // 大小切换
        document.querySelectorAll('.size-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.size-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentSize = btn.dataset.size;
                this.saveSettings();
                this.applyFontSize();
            });
        });

        // 颜色预设
        document.querySelectorAll('.color-preset').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.color-preset').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.setBackgroundColor(btn.dataset.color);
                this.saveSettings();
            });
        });

        // 自定义颜色
        document.getElementById('custom-color').addEventListener('input', (e) => {
            document.querySelectorAll('.color-preset').forEach(b => b.classList.remove('active'));
            this.setBackgroundColor(e.target.value);
        });

        document.getElementById('custom-color').addEventListener('change', (e) => {
            this.saveSettings();
        });

        // 关闭设置
        document.getElementById('close-settings').addEventListener('click', () => {
            this.settingsPanel.classList.add('hidden');
        });

        // 开始测速
        document.getElementById('start-speed').addEventListener('click', () => {
            this.startSpeedMeter();
        });

        // 打开设置
        document.getElementById('open-settings').addEventListener('click', () => {
            this.stopSpeedMeter();
            this.settingsPanel.classList.remove('hidden');
        });

        // 权限请求
        document.getElementById('request-permission').addEventListener('click', () => {
            this.requestLocationPermission();
        });

        document.getElementById('cancel-permission').addEventListener('click', () => {
            this.permissionOverlay.classList.add('hidden');
            this.settingsPanel.classList.remove('hidden');
        });

        // 网络状态
        window.addEventListener('online', () => this.updateNetworkStatus(true));
        window.addEventListener('offline', () => this.updateNetworkStatus(false));
    }

    // 设置背景颜色
    setBackgroundColor(color) {
        this.currentColor = color;
        document.body.style.background = color;
        this.speedDisplay.style.background = color;
        document.documentElement.style.setProperty('--bg-color', color);
    }

    // 保存设置
    saveSettings() {
        const settings = {
            style: this.currentStyle,
            unit: this.currentUnit,
            size: this.currentSize,
            color: this.currentColor
        };
        localStorage.setItem('speedMeterSettings', JSON.stringify(settings));
    }

    // 开始测速
    startSpeedMeter() {
        this.settingsPanel.classList.add('hidden');
        this.speedDisplay.classList.remove('hidden');
        this.updateStyleDisplay();

        // 检查定位支持
        if (!navigator.geolocation) {
            this.showError('您的设备不支持定位功能');
            return;
        }

        // 检查网络状态
        this.updateNetworkStatus(navigator.onLine);

        // 请求权限或直接开始
        if (this.needsPermission()) {
            this.permissionOverlay.classList.remove('hidden');
        } else {
            this.beginTracking();
        }

        // 尝试全屏
        this.requestFullscreen();
    }

    // 是否需要请求权限
    needsPermission() {
        // iOS 13+ 需要明确请求
        if (typeof DeviceMotionEvent !== 'undefined' &&
            typeof DeviceMotionEvent.requestPermission === 'function') {
            return true;
        }
        return false;
    }

    // 请求定位权限
    async requestLocationPermission() {
        this.permissionOverlay.classList.add('hidden');

        try {
            if (typeof DeviceMotionEvent !== 'undefined' &&
                typeof DeviceMotionEvent.requestPermission === 'function') {
                const permission = await DeviceMotionEvent.requestPermission();
                if (permission !== 'granted') {
                    this.showError('定位权限被拒绝');
                    return;
                }
            }

            navigator.geolocation.getCurrentPosition(
                () => this.beginTracking(),
                (error) => {
                    this.showError('无法获取定位权限: ' + error.message);
                },
                { enableHighAccuracy: true }
            );
        } catch (error) {
            this.showError('权限请求失败: ' + error.message);
        }
    }

    // 开始追踪
    beginTracking() {
        this.isRunning = true;
        this.updateGpsStatus(true);

        const options = {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        };

        // 使用 watchPosition 持续更新
        this.watchId = navigator.geolocation.watchPosition(
            (position) => this.handlePositionSuccess(position),
            (error) => this.handlePositionError(error),
            options
        );
    }

    // 处理定位成功
    handlePositionSuccess(position) {
        const speed = position.coords.speed; // m/s

        if (speed !== null) {
            this.currentSpeed = speed;
            this.displaySpeed(speed);
            this.updateNeedle(speed);
            this.updateGpsStatus(true);
        } else {
            // GPS 速度不可用，可能是因为移动不够快
            this.currentSpeed = 0;
            this.displaySpeed(0);
            this.updateNeedle(0);
        }
    }

    // 处理定位错误
    handlePositionError(error) {
        console.warn('定位错误:', error.message);
        this.updateGpsStatus(false);

        switch (error.code) {
            case error.PERMISSION_DENIED:
                this.showGpsWarning('定位权限被拒绝');
                break;
            case error.POSITION_UNAVAILABLE:
                this.showGpsWarning('位置信息不可用');
                break;
            case error.TIMEOUT:
                this.showGpsWarning('定位请求超时');
                break;
        }
    }

    // 显示速度
    displaySpeed(speedMs) {
        // 转换速度
        let displayValue;
        if (this.currentUnit === 'kmh') {
            displayValue = Math.round(speedMs * 3.6); // m/s -> km/h
        } else {
            displayValue = Math.round(speedMs * 2.237); // m/s -> mph
        }

        // 更新所有速度显示元素
        Object.values(this.speedElements).forEach(el => {
            if (el) el.textContent = displayValue;
        });

        // 更新渐变进度条
        const speedBar = document.getElementById('speed-bar');
        if (speedBar) {
            const maxSpeed = this.currentUnit === 'kmh' ? 200 : 124;
            const percentage = Math.min((displayValue / maxSpeed) * 100, 100);
            speedBar.style.width = percentage + '%';
        }

        // 更新运动样式进度
        const sportProgress = document.getElementById('sport-progress');
        if (sportProgress) {
            const maxSpeed = this.currentUnit === 'kmh' ? 240 : 149;
            const percentage = Math.min((displayValue / maxSpeed) * 100, 100);
            sportProgress.style.background = `conic-gradient(
                from 150deg,
                #ff4444 0deg,
                #ff8800 ${percentage * 1.8}deg,
                #00ff88 ${percentage * 1.8}deg,
                #00d4ff ${Math.min(percentage * 1.8, 180)}deg,
                transparent ${Math.min(percentage * 1.8, 180)}deg
            )`;
        }
    }

    // 更新指针角度
    updateNeedle(speedMs) {
        let speed = this.currentUnit === 'kmh'
            ? speedMs * 3.6
            : speedMs * 2.237;

        const maxSpeed = this.currentUnit === 'kmh' ? 200 : 124;
        const percentage = Math.min(speed / maxSpeed, 1);
        const angle = -135 + (percentage * 270); // -135deg 到 135deg

        Object.entries(this.needleElements).forEach(([style, needle]) => {
            if (needle && this.currentStyle === style) {
                needle.style.transform = `translateX(-50%) rotate(${angle}deg)`;
            }
        });
    }

    // 更新样式显示
    updateStyleDisplay() {
        // 隐藏所有样式
        document.querySelectorAll('.speed-style').forEach(el => {
            el.classList.remove('active');
        });

        // 显示当前样式
        const currentStyleEl = document.getElementById(`style-${this.currentStyle}`);
        if (currentStyleEl) {
            currentStyleEl.classList.add('active');
        }

        // 更新指针
        this.updateNeedle(this.currentSpeed);
    }

    // 更新单位标签
    updateUnitLabels() {
        const unitText = this.currentUnit === 'kmh' ? 'km/h' : 'mph';
        const unitElements = document.querySelectorAll('.unit-label, .neon-unit, .minimal-unit, .mech-digital span:last-child, .gradient-unit, .holo-unit, .retro-digital small, .scifi-unit, .sport-unit, .ink-unit');

        // 更新显示的速度值
        this.displaySpeed(this.currentSpeed);
    }

    // 更新 GPS 状态
    updateGpsStatus(active) {
        const gpsStatus = document.getElementById('gps-status');
        if (gpsStatus) {
            gpsStatus.classList.toggle('active', active);
            gpsStatus.querySelector('span').textContent = active ? 'GPS' : 'GPS离线';
        }
    }

    // 更新网络状态
    updateNetworkStatus(online) {
        const networkStatus = document.getElementById('network-status');
        if (networkStatus) {
            networkStatus.classList.toggle('active', online);
            networkStatus.querySelector('span').textContent = online ? '网络' : '离线';
        }
    }

    // 显示 GPS 警告
    showGpsWarning(message) {
        // 创建一个临时提示
        const warning = document.createElement('div');
        warning.className = 'gps-warning';
        warning.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <span>${message}</span>
        `;
        warning.style.cssText = `
            position: fixed;
            top: 80px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(255, 68, 68, 0.9);
            color: white;
            padding: 12px 20px;
            border-radius: 30px;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 1000;
            animation: fadeIn 0.3s ease;
        `;

        document.body.appendChild(warning);

        setTimeout(() => {
            warning.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => warning.remove(), 300);
        }, 3000);
    }

    // 显示错误
    showError(message) {
        alert(message);
    }

    // 停止测速
    stopSpeedMeter() {
        this.isRunning = false;
        if (this.watchId !== null) {
            navigator.geolocation.clearWatch(this.watchId);
            this.watchId = null;
        }
        this.speedDisplay.classList.add('hidden');
        this.updateGpsStatus(false);
    }

    // 请求全屏
    requestFullscreen() {
        const elem = document.documentElement;
        if (elem.requestFullscreen) {
            elem.requestFullscreen().catch(() => {});
        } else if (elem.webkitRequestFullscreen) {
            elem.webkitRequestFullscreen();
        } else if (elem.msRequestFullscreen) {
            elem.msRequestFullscreen();
        }
    }
}

// 添加动画样式
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateX(-50%) translateY(-10px); }
        to { opacity: 1; transform: translateX(-50%) translateY(0); }
    }
    @keyframes fadeOut {
        from { opacity: 1; transform: translateX(-50%) translateY(0); }
        to { opacity: 0; transform: translateX(-50%) translateY(-10px); }
    }
`;
document.head.appendChild(styleSheet);

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    window.speedMeter = new SpeedMeter();
});

// 页面可见性变化时处理
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden' && window.speedMeter?.isRunning) {
        // 页面隐藏时可以继续追踪，但降低频率
    } else if (document.visibilityState === 'visible') {
        // 页面显示时恢复正常
    }
});
