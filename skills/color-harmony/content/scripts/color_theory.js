// 科学色彩搭配核心算法
// Color Harmony Generator

class ColorConverter {
  // HEX to RGB
  static hexToRgb(hex) {
    hex = hex.replace('#', '');
    if (hex.length === 3) {
      hex = hex.split('').map(c => c + c).join('');
    }
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return { r, g, b };
  }

  // RGB to HEX
  static rgbToHex(r, g, b) {
    return '#' + [r, g, b].map(x => {
      const hex = Math.round(Math.max(0, Math.min(255, x))).toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join('').toUpperCase();
  }

  // HEX to HSL
  static hexToHsl(hex) {
    let { r, g, b } = this.hexToRgb(hex);
    r /= 255; g /= 255; b /= 255;

    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
      h = s = 0;
    } else {
      const d = max - min;
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
      switch (max) {
        case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
        case g: h = ((b - r) / d + 2) / 6; break;
        case b: h = ((r - g) / d + 4) / 6; break;
      }
    }

    return {
      h: Math.round(h * 360),
      s: Math.round(s * 100),
      l: Math.round(l * 100)
    };
  }

  // HSL to HEX
  static hslToHex(h, s, l) {
    h = ((h % 360) + 360) % 360;
    s = Math.max(0, Math.min(100, s)) / 100;
    l = Math.max(0, Math.min(100, l)) / 100;

    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs((h / 60) % 2 - 1));
    const m = l - c / 2;

    let r, g, b;
    if (h < 60) { r = c; g = x; b = 0; }
    else if (h < 120) { r = x; g = c; b = 0; }
    else if (h < 180) { r = 0; g = c; b = x; }
    else if (h < 240) { r = 0; g = x; b = c; }
    else if (h < 300) { r = x; g = 0; b = c; }
    else { r = c; g = 0; b = x; }

    return this.rgbToHex(
      Math.round((r + m) * 255),
      Math.round((g + m) * 255),
      Math.round((b + m) * 255)
    );
  }

  // RGB to HSL
  static rgbToHsl(r, g, b) {
    return this.hexToHsl(this.rgbToHex(r, g, b));
  }

  // 计算对比度 (WCAG)
  static getContrastRatio(color1, color2) {
    const getLuminance = (hex) => {
      const rgb = this.hexToRgb(hex);
      const [r, g, b] = [rgb.r, rgb.g, rgb.b].map(v => {
        v /= 255;
        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };

    const l1 = getLuminance(color1);
    const l2 = getLuminance(color2);
    const lighter = Math.max(l1, l2);
    const darker = Math.min(l1, l2);
    return (lighter + 0.05) / (darker + 0.05);
  }
}

// 色彩搭配生成器
class ColorHarmonyGenerator {
  constructor(baseColor) {
    this.baseHsl = ColorConverter.hexToHsl(baseColor);
  }

  // 互补色 (180°)
  complementary() {
    return [
      { ...this.baseHsl },
      { h: (this.baseHsl.h + 180) % 360, s: this.baseHsl.s, l: this.baseHsl.l }
    ];
  }

  // 类似色 (±30°)
  analogous() {
    return [
      { h: (this.baseHsl.h - 30 + 360) % 360, s: this.baseHsl.s, l: this.baseHsl.l },
      { ...this.baseHsl },
      { h: (this.baseHsl.h + 30) % 360, s: this.baseHsl.s, l: this.baseHsl.l }
    ];
  }

  // 三角色 (120° × 3)
  triadic() {
    return [
      { ...this.baseHsl },
      { h: (this.baseHsl.h + 120) % 360, s: this.baseHsl.s, l: this.baseHsl.l },
      { h: (this.baseHsl.h + 240) % 360, s: this.baseHsl.s, l: this.baseHsl.l }
    ];
  }

  // 分裂互补 (180° ± 30°)
  splitComplementary() {
    return [
      { ...this.baseHsl },
      { h: (this.baseHsl.h + 150) % 360, s: this.baseHsl.s, l: this.baseHsl.l },
      { h: (this.baseHsl.h + 210) % 360, s: this.baseHsl.s, l: this.baseHsl.l }
    ];
  }

  // 双分裂互补
  doubleSplitComplementary() {
    return [
      { ...this.baseHsl },
      { h: (this.baseHsl.h + 90) % 360, s: this.baseHsl.s, l: this.baseHsl.l },
      { h: (this.baseHsl.h + 180) % 360, s: this.baseHsl.s, l: this.baseHsl.l },
      { h: (this.baseHsl.h + 270) % 360, s: this.baseHsl.s, l: this.baseHsl.l }
    ];
  }

  // 四色组 (90° × 4)
  tetradic() {
    return [
      { ...this.baseHsl },
      { h: (this.baseHsl.h + 90) % 360, s: this.baseHsl.s, l: this.baseHsl.l },
      { h: (this.baseHsl.h + 180) % 360, s: this.baseHsl.s, l: this.baseHsl.l },
      { h: (this.baseHsl.h + 270) % 360, s: this.baseHsl.s, l: this.baseHsl.l }
    ];
  }

  // 单色搭配 (不同明度饱和度)
  monochromatic() {
    return [
      { h: this.baseHsl.h, s: this.baseHsl.s, l: Math.max(20, this.baseHsl.l - 30) },
      { h: this.baseHsl.h, s: this.baseHsl.s, l: this.baseHsl.l },
      { h: this.baseHsl.h, s: Math.min(100, this.baseHsl.s + 20), l: Math.min(80, this.baseHsl.l + 10) }
    ];
  }

  // 根据数量生成最佳搭配
  generate(count = 5) {
    const typeMap = {
      1: 'complementary',
      2: 'analogous',
      3: 'triadic',
      4: 'tetradic',
      5: 'splitComplementary'
    };

    const method = typeMap[Math.min(count, 5)] || 'triadic';
    const hslColors = this[method]();

    return hslColors.map(hsl => ({
      hex: ColorConverter.hslToHex(hsl.h, hsl.s, hsl.l),
      rgb: ColorConverter.hexToRgb(ColorConverter.hslToHex(hsl.h, hsl.s, hsl.l)),
      hsl: hsl,
      name: this.getColorName(hsl)
    }));
  }

  // 获取颜色名称
  getColorName(hsl) {
    const { h, s, l } = hsl;

    // 无彩色
    if (s < 10) {
      if (l < 20) return '黑色';
      if (l < 40) return '深灰';
      if (l < 60) return '灰色';
      if (l < 80) return '浅灰';
      return '白色';
    }

    // 基础色相名称
    const hueNames = [
      { start: 0, end: 15, name: '红色' },
      { start: 15, end: 45, name: '橙色' },
      { start: 45, end: 75, name: '黄色' },
      { start: 75, end: 105, name: '黄绿色' },
      { start: 105, end: 135, name: '绿色' },
      { start: 135, end: 165, name: '青绿色' },
      { start: 165, end: 195, name: '青色' },
      { start: 195, end: 225, name: '青蓝色' },
      { start: 225, end: 255, name: '蓝色' },
      { start: 255, end: 285, name: '紫蓝色' },
      { start: 285, end: 315, name: '紫色' },
      { start: 315, end: 345, name: '紫红色' },
      { start: 345, end: 360, name: '红色' }
    ];

    let baseName = '未知色';
    for (const range of hueNames) {
      if (h >= range.start && h < range.end) {
        baseName = range.name;
        break;
      }
    }

    // 修饰词
    let modifier = '';
    if (l < 30) modifier = '深';
    else if (l > 70) modifier = '浅';
    if (s > 80 && l > 30 && l < 70) modifier = modifier ? '鲜艳的' : '鲜艳';

    return modifier + baseName;
  }

  // 获取搭配类型描述
  static getHarmonyDescription(type) {
    const descriptions = {
      complementary: { name: '互补色', angle: '180°', desc: '高对比度，适合强调重点', use: 'CTA按钮、重点标注、警示信息' },
      analogous: { name: '类似色', angle: '±30°', desc: '柔和过渡，自然和谐', use: '背景渐变、界面主色调、平静场景' },
      triadic: { name: '三角色', angle: '120°×3', desc: '色彩丰富，视觉平衡', use: '图表配色、图标设计、儿童产品' },
      splitComplementary: { name: '分裂互补', angle: '180°±30°', desc: '互补与类似的完美结合', use: '品牌色、UI设计、创意项目' },
      tetradic: { name: '四色组', angle: '90°×4', desc: '复杂多变，色彩饱满', use: '多状态标识、游戏UI、节日主题' },
      doubleSplitComplementary: { name: '双分裂互补', angle: '90°±30°', desc: '和谐的复杂配色', use: '数据可视化、艺术设计' }
    };
    return descriptions[type] || descriptions.triadic;
  }
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ColorConverter, ColorHarmonyGenerator };
}
