/**
 * PDF导出模块 - 拼豆十字绣图纸生成器
 * Export Pattern as PDF
 */

class PatternExporter {
    constructor() {
        this.pageSizes = {
            'A4': { width: 210, height: 297 },
            'A3': { width: 297, height: 420 },
            'Letter': { width: 216, height: 279 }
        };
    }

    /**
     * 导出PDF图纸
     */
    async exportPDF(pixelData, options = {}) {
        const {
            pageSize = 'A4',
            showGrid = true,
            showNumbers = true,
            showLegend = true,
            colorPalette = [],
            title = '拼豆图纸'
        } = options;

        // 动态加载jsPDF
        if (typeof jspdf === 'undefined') {
            await this.loadJsPDF();
        }

        const { width, height } = this.pageSizes[pageSize];
        const doc = new jspdf.jsPDF({
            orientation: height > width ? 'portrait' : 'landscape',
            unit: 'mm',
            format: pageSize.toLowerCase()
        });

        // 计算网格尺寸
        const gridWidth = pixelData[0].length;
        const gridHeight = pixelData.length;
        const margin = 15;
        const legendWidth = showLegend ? 50 : 0;
        const availableWidth = width - margin * 2 - legendWidth;
        const availableHeight = height - margin * 2 - 20; // 减去标题区域

        const cellSize = Math.min(
            availableWidth / gridWidth,
            availableHeight / gridHeight
        );

        const patternOffsetX = margin;
        const patternOffsetY = margin + 15;

        // 添加标题
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.text(title, width / 2, margin, { align: 'center' });

        // 添加图纸信息
        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        doc.text(`尺寸: ${gridWidth} x ${gridHeight}`, margin, margin + 8);
        doc.text(`日期: ${new Date().toLocaleDateString()}`, width - margin, margin + 8, { align: 'right' });

        // 绘制网格
        if (showGrid) {
            doc.setDrawColor(200, 200, 200);
            doc.setLineWidth(0.1);

            // 垂直线
            for (let x = 0; x <= gridWidth; x++) {
                const lineX = patternOffsetX + x * cellSize;
                doc.line(lineX, patternOffsetY, lineX, patternOffsetY + gridHeight * cellSize);
            }

            // 水平线
            for (let y = 0; y <= gridHeight; y++) {
                const lineY = patternOffsetY + y * cellSize;
                doc.line(patternOffsetX, lineY, patternOffsetX + gridWidth * cellSize, lineY);
            }
        }

        // 绘制像素
        for (let y = 0; y < gridHeight; y++) {
            for (let x = 0; x < gridWidth; x++) {
                const color = pixelData[y][x] || '#ffffff';
                const rgb = this.hexToRgb(color);

                const cellX = patternOffsetX + x * cellSize;
                const cellY = patternOffsetY + y * cellSize;

                // 填充颜色
                doc.setFillColor(rgb.r, rgb.g, rgb.b);
                doc.rect(cellX, cellY, cellSize, cellSize, 'F');

                // 绘制边框
                doc.setDrawColor(180, 180, 180);
                doc.setLineWidth(0.05);
                doc.rect(cellX, cellY, cellSize, cellSize, 'S');

                // 添加颜色代码（如果启用）
                if (showNumbers && cellSize >= 3) {
                    const colorIndex = colorPalette.findIndex(c => c.hex.toUpperCase() === color.toUpperCase());
                    if (colorIndex >= 0) {
                        const code = colorPalette[colorIndex].code || colorPalette[colorIndex].id;
                        doc.setFontSize(cellSize * 0.8);
                        doc.setTextColor(this.getContrastColor(color));
                        doc.text(code.toString(), cellX + cellSize / 2, cellY + cellSize * 0.7, {
                            align: 'center'
                        });
                    }
                }
            }
        }

        // 绘制颜色图例
        if (showLegend) {
            await this.drawLegend(doc, pixelData, colorPalette, width - margin - legendWidth + 5, margin + 25, legendWidth - 10);
        }

        return doc;
    }

    /**
     * 绘制颜色图例
     */
    async drawLegend(doc, pixelData, palette, startX, startY, width) {
        // 计算颜色统计
        const stats = new Map();
        for (let y = 0; y < pixelData.length; y++) {
            for (let x = 0; x < pixelData[0].length; x++) {
                const color = pixelData[y][x] || '#ffffff';
                stats.set(color, (stats.get(color) || 0) + 1);
            }
        }

        // 排序颜色
        const sortedColors = Array.from(stats.entries())
            .sort((a, b) => b[1] - a[1]);

        let currentY = startY;
        const colorBoxSize = 6;
        const rowHeight = 8;

        doc.setFontSize(8);
        doc.setFont('helvetica', 'bold');
        doc.text('颜色图例', startX, currentY);
        currentY += 5;

        for (const [color, count] of sortedColors) {
            if (currentY > 280) break; // 避免超出页面

            const rgb = this.hexToRgb(color);

            // 颜色方块
            doc.setFillColor(rgb.r, rgb.g, rgb.b);
            doc.rect(startX, currentY - colorBoxSize + 2, colorBoxSize, colorBoxSize, 'F');
            doc.setDrawColor(100, 100, 100);
            doc.setLineWidth(0.2);
            doc.rect(startX, currentY - colorBoxSize + 2, colorBoxSize, colorBoxSize, 'S');

            // 颜色代码
            const paletteItem = palette.find(p => p.hex.toUpperCase() === color.toUpperCase());
            const code = paletteItem ? paletteItem.code || paletteItem.id : color;

            // 颜色值
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(6);
            doc.text(code.toString(), startX + colorBoxSize + 2, currentY - 1);

            // 数量
            doc.text(`${count}`, startX + width - 15, currentY - 1);

            currentY += rowHeight;
        }

        // 添加总计
        const total = sortedColors.reduce((sum, [, count]) => sum + count, 0);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(8);
        doc.text(`总计: ${total} 颗`, startX, currentY + 5);
        doc.text(`颜色: ${sortedColors.length} 种`, startX, currentY + 10);
    }

    /**
     * 导出CSV格式
     */
    exportCSV(pixelData, palette = []) {
        const lines = [];
        lines.push('X,Y,Color,Code');

        for (let y = 0; y < pixelData.length; y++) {
            for (let x = 0; x < pixelData[0].length; x++) {
                const color = pixelData[y][x] || '#ffffff';
                const paletteItem = palette.find(p => p.hex.toUpperCase() === color.toUpperCase());
                const code = paletteItem ? paletteItem.code || paletteItem.id : color;
                lines.push(`${x + 1},${y + 1},${color},${code}`);
            }
        }

        return lines.join('\n');
    }

    /**
     * 导出颜色统计
     */
    exportColorStats(pixelData, palette = []) {
        const stats = new Map();
        for (let y = 0; y < pixelData.length; y++) {
            for (let x = 0; x < pixelData[0].length; x++) {
                const color = pixelData[y][x] || '#ffffff';
                stats.set(color, (stats.get(color) || 0) + 1);
            }
        }

        return Array.from(stats.entries())
            .map(([color, count]) => {
                const paletteItem = palette.find(p => p.hex.toUpperCase() === color.toUpperCase());
                return {
                    color,
                    code: paletteItem ? paletteItem.code || paletteItem.id : color,
                    name: paletteItem ? paletteItem.name || '' : '',
                    count
                };
            })
            .sort((a, b) => b.count - a.count);
    }

    /**
     * 加载jsPDF库
     */
    async loadJsPDF() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
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
        } : { r: 255, g: 255, b: 255 };
    }

    /**
     * 获取对比色（黑或白）
     */
    getContrastColor(hex) {
        const rgb = this.hexToRgb(hex);
        const luminance = (0.299 * rgb.r + 0.587 * rgb.g + 0.114 * rgb.b) / 255;
        return luminance > 0.5 ? '#000000' : '#ffffff';
    }
}

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PatternExporter;
}
