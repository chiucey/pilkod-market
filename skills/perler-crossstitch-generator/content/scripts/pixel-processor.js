/**
 * 拼豆十字绣图纸生成器 - 核心处理器
 * Pixel Art to Perler Beads / Cross-Stitch Pattern Converter
 */

class PixelPatternGenerator {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.pixelData = null;
        this.currentPalette = [];
        this.gridSize = { width: 32, height: 32 };
        this.history = [];
        this.historyIndex = -1;
        this.currentTool = 'brush';
        this.currentColor = '#000000';
        this.zoom = 1;
    }

    /**
     * 初始化画布
     */
    initCanvas(containerId, width, height) {
        this.canvas = document.createElement('canvas');
        this.canvas.id = 'pixelCanvas';
        this.gridSize = { width, height };

        const container = document.getElementById(containerId);
        container.innerHTML = '';
        container.appendChild(this.canvas);

        this.ctx = this.canvas.getContext('2d');
        this.canvas.width = width;
        this.canvas.height = height;

        this.setupCanvas();
        return this.canvas;
    }

    /**
     * 设置画布样式
     */
    setupCanvas() {
        this.ctx.imageSmoothingEnabled = false;
        this.canvas.style.width = `${this.gridSize.width * 20}px`;
        this.canvas.style.height = `${this.gridSize.height * 20}px`;
        this.canvas.style.cursor = 'crosshair';
        this.canvas.style.border = '2px solid #333';
        this.canvas.style.backgroundColor = '#fff';
    }

    /**
     * 从图片生成像素化图案
     */
    async generateFromImage(imageFile, options = {}) {
        const {
            targetWidth = 32,
            targetHeight = 32,
            dither = 'floyd-steinberg',
            colorCount = 64,
            scaleMode = 'nearest'
        } = options;

        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                // 创建临时画布处理图片
                const tempCanvas = document.createElement('canvas');
                const tempCtx = tempCanvas.getContext('2d');

                tempCanvas.width = targetWidth;
                tempCanvas.height = targetHeight;

                // 缩放图片
                tempCtx.imageSmoothingEnabled = scaleMode !== 'nearest';
                tempCtx.drawImage(img, 0, 0, targetWidth, targetHeight);

                // 获取像素数据
                const imageData = tempCtx.getImageData(0, 0, targetWidth, targetHeight);
                const pixels = this.quantizeColors(imageData, colorCount, dither);

                // 更新画布
                this.gridSize = { width: targetWidth, height: targetHeight };
                this.pixelData = pixels;
                this.updateCanvasDisplay();

                resolve({
                    pixels: this.pixelData,
                    dimensions: this.gridSize,
                    colorCount: this.getUsedColorCount()
                });
            };
            img.onerror = reject;
            img.src = URL.createObjectURL(imageFile);
        });
    }

    /**
     * 颜色量化处理
     */
    quantizeColors(imageData, maxColors, ditherMethod) {
        const data = imageData.data;
        const width = imageData.width;
        const height = imageData.height;
        const pixels = [];

        // 获取所有颜色
        const colorMap = new Map();
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            const hex = this.rgbToHex(r, g, b);
            colorMap.set(hex, (colorMap.get(hex) || 0) + 1);
        }

        // 选择最常用的颜色
        const sortedColors = [...colorMap.entries()]
            .sort((a, b) => b[1] - a[1])
            .slice(0, maxColors)
            .map(([hex]) => hex);

        // 创建颜色映射表
        const palette = sortedColors;

        // 应用抖动算法并量化颜色
        for (let y = 0; y < height; y++) {
            pixels[y] = [];
            for (let x = 0; x < width; x++) {
                const i = (y * width + x) * 4;
                let r = data[i];
                let g = data[i + 1];
                let b = data[i + 2];

                // Floyd-Steinberg 抖动
                if (ditherMethod === 'floyd-steinberg') {
                    const oldPixel = { r, g, b };
                    const newPixel = this.findClosestColor(oldPixel, palette);
                    pixels[y][x] = newPixel;

                    const error = {
                        r: oldPixel.r - newPixel.r,
                        g: oldPixel.g - newPixel.g,
                        b: oldPixel.b - newPixel.b
                    };

                    // 传播误差
                    this.addError(data, width, height, x + 1, y, error, 7 / 16);
                    this.addError(data, width, height, x - 1, y + 1, error, 3 / 16);
                    this.addError(data, width, height, x, y + 1, error, 5 / 16);
                    this.addError(data, width, height, x + 1, y + 1, error, 1 / 16);
                } else {
                    pixels[y][x] = this.findClosestColor({ r, g, b }, palette);
                }
            }
        }

        return pixels;
    }

    /**
     * 添加抖动误差
     */
    addError(data, width, height, x, y, error, factor) {
        if (x < 0 || x >= width || y < 0 || y >= height) return;
        const i = (y * width + x) * 4;
        data[i] = Math.max(0, Math.min(255, data[i] + error.r * factor));
        data[i + 1] = Math.max(0, Math.min(255, data[i + 1] + error.g * factor));
        data[i + 2] = Math.max(0, Math.min(255, data[i + 2] + error.b * factor));
    }

    /**
     * 查找最接近的颜色
     */
    findClosestColor(pixel, palette) {
        let closest = palette[0];
        let minDist = Infinity;

        for (const hex of palette) {
            const rgb = this.hexToRgb(hex);
            const dist = this.colorDistance(pixel, rgb);
            if (dist < minDist) {
                minDist = dist;
                closest = hex;
            }
        }

        return closest;
    }

    /**
     * 计算颜色距离
     */
    colorDistance(c1, c2) {
        return Math.sqrt(
            Math.pow(c1.r - c2.r, 2) +
            Math.pow(c1.g - c2.g, 2) +
            Math.pow(c1.b - c2.b, 2)
        );
    }

    /**
     * RGB转HEX
     */
    rgbToHex(r, g, b) {
        return '#' + [r, g, b].map(x => {
            const hex = x.toString(16);
            return hex.length === 1 ? '0' + hex : hex;
        }).join('');
    }

    /**
     * HEX转RGB
     */
    hexToRgb(hex) {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : { r: 0, g: 0, b: 0 };
    }

    /**
     * 更新画布显示
     */
    updateCanvasDisplay() {
        if (!this.pixelData) return;

        this.canvas.width = this.gridSize.width;
        this.canvas.height = this.gridSize.height;

        for (let y = 0; y < this.gridSize.height; y++) {
            for (let x = 0; x < this.gridSize.width; x++) {
                const color = this.pixelData[y][x];
                this.ctx.fillStyle = color || '#ffffff';
                this.ctx.fillRect(x, y, 1, 1);
            }
        }
    }

    /**
     * 获取使用的颜色数量
     */
    getUsedColorCount() {
        if (!this.pixelData) return 0;
        const colors = new Set();
        for (let y = 0; y < this.gridSize.height; y++) {
            for (let x = 0; x < this.gridSize.width; x++) {
                if (this.pixelData[y][x]) {
                    colors.add(this.pixelData[y][x]);
                }
            }
        }
        return colors.size;
    }

    /**
     * 获取颜色统计
     */
    getColorStatistics() {
        if (!this.pixelData) return [];
        const stats = new Map();

        for (let y = 0; y < this.gridSize.height; y++) {
            for (let x = 0; x < this.gridSize.width; x++) {
                const color = this.pixelData[y][x] || '#ffffff';
                stats.set(color, (stats.get(color) || 0) + 1);
            }
        }

        return Array.from(stats.entries())
            .map(([color, count]) => ({ color, count }))
            .sort((a, b) => b.count - a.count);
    }

    /**
     * 绘制像素点
     */
    drawPixel(x, y, color) {
        if (!this.pixelData || x < 0 || x >= this.gridSize.width || y < 0 || y >= this.gridSize.height) return;
        this.pixelData[y][x] = color;
        this.updateCanvasDisplay();
    }

    /**
     * 填充连续区域
     */
    floodFill(startX, startY, newColor) {
        if (!this.pixelData) return;
        const targetColor = this.pixelData[startY][startX];
        if (targetColor === newColor) return;

        const stack = [[startX, startY]];
        const visited = new Set();

        while (stack.length > 0) {
            const [x, y] = stack.pop();
            const key = `${x},${y}`;

            if (visited.has(key)) continue;
            if (x < 0 || x >= this.gridSize.width || y < 0 || y >= this.gridSize.height) continue;
            if (this.pixelData[y][x] !== targetColor) continue;

            visited.add(key);
            this.pixelData[y][x] = newColor;

            stack.push([x + 1, y], [x - 1, y], [x, y + 1], [x, y - 1]);
        }

        this.updateCanvasDisplay();
    }

    /**
     * 替换所有相同颜色
     */
    replaceColor(oldColor, newColor) {
        if (!this.pixelData) return;
        for (let y = 0; y < this.gridSize.height; y++) {
            for (let x = 0; x < this.gridSize.width; x++) {
                if (this.pixelData[y][x] === oldColor) {
                    this.pixelData[y][x] = newColor;
                }
            }
        }
        this.updateCanvasDisplay();
    }

    /**
     * 保存历史状态
     */
    saveHistory() {
        const state = JSON.parse(JSON.stringify(this.pixelData));
        this.history = this.history.slice(0, this.historyIndex + 1);
        this.history.push(state);
        this.historyIndex = this.history.length - 1;
        if (this.history.length > 50) {
            this.history.shift();
            this.historyIndex--;
        }
    }

    /**
     * 撤销
     */
    undo() {
        if (this.historyIndex > 0) {
            this.historyIndex--;
            this.pixelData = JSON.parse(JSON.stringify(this.history[this.historyIndex]));
            this.updateCanvasDisplay();
        }
    }

    /**
     * 重做
     */
    redo() {
        if (this.historyIndex < this.history.length - 1) {
            this.historyIndex++;
            this.pixelData = JSON.parse(JSON.stringify(this.history[this.historyIndex]));
            this.updateCanvasDisplay();
        }
    }
}

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PixelPatternGenerator;
}
