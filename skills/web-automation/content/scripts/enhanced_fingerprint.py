#!/usr/bin/env python3
"""
增强浏览器指纹伪装
支持 WebGL、Canvas、AudioContext、字体等多种指纹伪装
"""

import json
from typing import Dict, List, Optional
from pathlib import Path


class EnhancedFingerprint:
    """增强浏览器指纹伪装"""

    def __init__(self):
        """初始化增强指纹"""
        self.fingerprint_config = {
            "webgl": {
                "vendor": "Intel Inc.",
                "renderer": "Intel Iris OpenGL Engine",
                "shading_language_version": "WebGL GLSL ES 3.00"
            },
            "canvas": {
                "noise": True,
                "noise_level": 0.1
            },
            "audio": {
                "sample_rate": 48000,
                "channel_count": 2
            },
            "fonts": {
                "spoof_fonts": True,
                "font_list": [
                    "Arial",
                    "Times New Roman",
                    "Courier New",
                    "Georgia",
                    "Verdana",
                    "Helvetica"
                ]
            },
            "navigator": {
                "platform": "Win32",
                "hardware_concurrency": 8,
                "device_memory": 8,
                "max_touch_points": 0
            },
            "screen": {
                "width": 1920,
                "height": 1080,
                "color_depth": 24,
                "pixel_ratio": 1
            },
            "timezone": {
                "offset": -480,  # UTC+8
                "timezone": "Asia/Shanghai"
            },
            "permissions": {
                "notifications": "prompt",
                "geolocation": "prompt",
                "camera": "prompt",
                "microphone": "prompt"
            }
        }

    def generate_webgl_script(self) -> str:
        """
        生成 WebGL 指纹伪装脚本

        Returns:
            JavaScript 代码
        """
        config = self.fingerprint_config["webgl"]

        script = f"""
// WebGL 指纹伪装
(function() {{
    const getParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(parameter) {{
        // UNMASKED_VENDOR_WEBGL
        if (parameter === 37445) {{
            return '{config["vendor"]}';
        }}
        // UNMASKED_RENDERER_WEBGL
        if (parameter === 37446) {{
            return '{config["renderer"]}';
        }}
        // SHADING_LANGUAGE_VERSION
        if (parameter === 35724) {{
            return '{config["shading_language_version"]}';
        }}
        return getParameter.apply(this, arguments);
    }};

    // WebGL2 同样处理
    if (typeof WebGL2RenderingContext !== 'undefined') {{
        const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
        WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{config["vendor"]}';
            }}
            if (parameter === 37446) {{
                return '{config["renderer"]}';
            }}
            if (parameter === 35724) {{
                return '{config["shading_language_version"]}';
            }}
            return getParameter2.apply(this, arguments);
        }};
    }}
}})();
"""
        return script

    def generate_canvas_script(self) -> str:
        """
        生成 Canvas 指纹伪装脚本

        Returns:
            JavaScript 代码
        """
        config = self.fingerprint_config["canvas"]

        if not config["noise"]:
            return ""

        script = f"""
// Canvas 指纹伪装
(function() {{
    const noise = {config["noise_level"]};

    const toDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function() {{
        const context = this.getContext('2d');
        if (context) {{
            const imageData = context.getImageData(0, 0, this.width, this.height);
            const data = imageData.data;
            for (let i = 0; i < data.length; i += 4) {{
                // 添加随机噪声
                data[i] = Math.min(255, Math.max(0, data[i] + (Math.random() - 0.5) * noise * 255));
                data[i + 1] = Math.min(255, Math.max(0, data[i + 1] + (Math.random() - 0.5) * noise * 255));
                data[i + 2] = Math.min(255, Math.max(0, data[i + 2] + (Math.random() - 0.5) * noise * 255));
            }}
            context.putImageData(imageData, 0, 0);
        }}
        return toDataURL.apply(this, arguments);
    }};
}})();
"""
        return script

    def generate_audio_script(self) -> str:
        """
        生成 AudioContext 指纹伪装脚本

        Returns:
            JavaScript 代码
        """
        config = self.fingerprint_config["audio"]

        script = f"""
// AudioContext 指纹伪装
(function() {{
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    const originalCreateAnalyser = AudioContext.prototype.createAnalyser;

    AudioContext.prototype.createAnalyser = function() {{
        const analyser = originalCreateAnalyser.apply(this, arguments);
        const getFloatFrequencyData = analyser.getFloatFrequencyData;

        analyser.getFloatFrequencyData = function(array) {{
            getFloatFrequencyData.apply(this, arguments);
            // 添加微小噪声
            for (let i = 0; i < array.length; i++) {{
                array[i] += (Math.random() - 0.5) * 0.0001;
            }}
        }};
        return analyser;
    }};
}})();
"""
        return script

    def generate_font_script(self) -> str:
        """
        生成字体指纹伪装脚本

        Returns:
            JavaScript 代码
        """
        config = self.fingerprint_config["fonts"]

        if not config["spoof_fonts"]:
            return ""

        font_list = '", "'.join(config["font_list"])

        script = f"""
// 字体指纹伪装
(function() {{
    // 模拟常用字体
    const mockFonts = ["{font_list}"];

    const measureText = CanvasRenderingContext2D.prototype.measureText;
    CanvasRenderingContext2D.prototype.measureText = function(text) {{
        const result = measureText.apply(this, arguments);
        // 添加微小变化
        result.width += (Math.random() - 0.5) * 0.01;
        return result;
    }};
}})();
"""
        return script

    def generate_navigator_script(self) -> str:
        """
        生成 Navigator 指纹伪装脚本

        Returns:
            JavaScript 代码
        """
        config = self.fingerprint_config["navigator"]

        script = f"""
// Navigator 指纹伪装
(function() {{
    // 硬件并发数
    Object.defineProperty(navigator, 'hardwareConcurrency', {{
        get: function() {{ return {config["hardware_concurrency"]}; }}
    }});

    // 设备内存
    if ('deviceMemory' in navigator) {{
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: function() {{ return {config["device_memory"]}; }}
        }});
    }}

    // 触摸点数
    Object.defineProperty(navigator, 'maxTouchPoints', {{
        get: function() {{ return {config["max_touch_points"]}; }}
    }});

    // 平台
    Object.defineProperty(navigator, 'platform', {{
        get: function() {{ return '{config["platform"]}'; }}
    }});
}})();
"""
        return script

    def generate_screen_script(self) -> str:
        """
        生成 Screen 指纹伪装脚本

        Returns:
            JavaScript 代码
        """
        config = self.fingerprint_config["screen"]

        script = f"""
// Screen 指纹伪装
(function() {{
    Object.defineProperty(screen, 'width', {{
        get: function() {{ return {config["width"]}; }}
    }});

    Object.defineProperty(screen, 'height', {{
        get: function() {{ return {config["height"]}; }}
    }});

    Object.defineProperty(screen, 'colorDepth', {{
        get: function() {{ return {config["color_depth"]}; }}
    }});

    Object.defineProperty(window, 'devicePixelRatio', {{
        get: function() {{ return {config["pixel_ratio"]}; }}
    }});
}})();
"""
        return script

    def generate_timezone_script(self) -> str:
        """
        生成时区指纹伪装脚本

        Returns:
            JavaScript 代码
        """
        config = self.fingerprint_config["timezone"]

        script = f"""
// 时区指纹伪装
(function() {{
    // Date.prototype.getTimezoneOffset
    const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
    Date.prototype.getTimezoneOffset = function() {{
        return {config["offset"]};
    }};

    // Intl.DateTimeFormat
    const originalDateTimeFormat = Intl.DateTimeFormat;
    Intl.DateTimeFormat = function() {{
        const formatter = originalDateTimeFormat.apply(this, arguments);
        const originalResolvedOptions = formatter.resolvedOptions;
        formatter.resolvedOptions = function() {{
            const options = originalResolvedOptions.apply(this, arguments);
            options.timeZone = '{config["timezone"]}';
            return options;
        }};
        return formatter;
    }};
}})();
"""
        return script

    def generate_permissions_script(self) -> str:
        """
        生成权限指纹伪装脚本

        Returns:
            JavaScript 代码
        """
        config = self.fingerprint_config["permissions"]

        script = f"""
// 权限指纹伪装
(function() {{
    const query = navigator.permissions.query;
    navigator.permissions.query = function(permissionDesc) {{
        return new Promise((resolve) => {{
            const result = {{
                state: '{config["notifications"]}',
                onchange: null
            }};
            resolve(result);
        }});
    }};
}})();
"""
        return script

    def generate_complete_script(self, modules: Optional[List[str]] = None) -> str:
        """
        生成完整的指纹伪装脚本

        Args:
            modules: 要启用的模块列表，None 表示全部启用

        Returns:
            完整的 JavaScript 代码
        """
        if modules is None:
            modules = [
                "webgl", "canvas", "audio", "font",
                "navigator", "screen", "timezone", "permissions"
            ]

        scripts = []

        if "webgl" in modules:
            scripts.append(self.generate_webgl_script())

        if "canvas" in modules:
            scripts.append(self.generate_canvas_script())

        if "audio" in modules:
            scripts.append(self.generate_audio_script())

        if "font" in modules:
            scripts.append(self.generate_font_script())

        if "navigator" in modules:
            scripts.append(self.generate_navigator_script())

        if "screen" in modules:
            scripts.append(self.generate_screen_script())

        if "timezone" in modules:
            scripts.append(self.generate_timezone_script())

        if "permissions" in modules:
            scripts.append(self.generate_permissions_script())

        return "\n".join(scripts)

    def save_script(self, output_path: str, modules: Optional[List[str]] = None) -> bool:
        """
        保存指纹伪装脚本到文件

        Args:
            output_path: 输出文件路径
            modules: 要启用的模块列表

        Returns:
            是否保存成功
        """
        try:
            script = self.generate_complete_script(modules)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(script)

            print(f"✅ 指纹伪装脚本已保存: {output_path}")
            return True
        except Exception as e:
            print(f"❌ 保存脚本失败: {e}")
            return False

    def update_config(self, module: str, config: Dict) -> None:
        """
        更新模块配置

        Args:
            module: 模块名称
            config: 新配置
        """
        if module in self.fingerprint_config:
            self.fingerprint_config[module].update(config)
            print(f"✅ 已更新 {module} 配置")

    def get_config(self) -> Dict:
        """
        获取当前配置

        Returns:
            配置字典
        """
        return self.fingerprint_config.copy()


def main():
    """主函数 - 生成指纹伪装脚本"""
    import argparse

    parser = argparse.ArgumentParser(description="增强浏览器指纹伪装")
    parser.add_argument("--output", "-o", default="fingerprint.js", help="输出文件路径")
    parser.add_argument("--modules", nargs="+", help="启用的模块列表")
    parser.add_argument("--list-modules", action="store_true", help="列出可用模块")

    args = parser.parse_args()

    fingerprint = EnhancedFingerprint()

    if args.list_modules:
        print("\n可用模块:")
        for module in fingerprint.fingerprint_config.keys():
            print(f"  - {module}")
        return

    # 生成脚本
    modules = args.modules if args.modules else None
    fingerprint.save_script(args.output, modules)


if __name__ == "__main__":
    main()
