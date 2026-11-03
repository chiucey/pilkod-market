#!/usr/bin/env python3
"""
浏览器指纹伪装脚本
用于绕过浏览器指纹检测，伪装浏览器指纹特征
"""

import random
import json
from typing import Dict, List, Optional


class BrowserFingerprint:
    """浏览器指纹伪装类"""

    def __init__(self):
        self.canvas_noise = random.uniform(0.0001, 0.001)
        self.webgl_vendor = self._get_webgl_vendor()
        self.webgl_renderer = self._get_webgl_renderer()
        self.audio_fingerprint = random.uniform(0.9999, 1.0001)

    def _get_webgl_vendor(self) -> str:
        """获取随机化的 WebGL vendor"""
        vendors = [
            "Intel Inc.",
            "NVIDIA Corporation",
            "AMD",
            "Apple Inc.",
            "Google Inc. (Intel)"
        ]
        return random.choice(vendors)

    def _get_webgl_renderer(self) -> str:
        """获取随机化的 WebGL renderer"""
        renderers = [
            "Intel Iris OpenGL Engine",
            "NVIDIA GeForce GTX 1060 6GB/PCIe/SSE2",
            "AMD Radeon RX 580 Series",
            "Apple GPU",
            "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)"
        ]
        return random.choice(renderers)

    def get_canvas_injection_script(self) -> str:
        """
        获取 Canvas 指纹伪装注入脚本

        Returns:
            JavaScript 注入脚本
        """
        return f"""
        (() => {{
            // 保存原始方法
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;

            // 修改 toDataURL 方法
            HTMLCanvasElement.prototype.toDataURL = function() {{
                const context = this.getContext('2d');
                const imageData = originalGetImageData.call(context, 0, 0, this.width, this.height);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] += {self.canvas_noise * 255};
                    imageData.data[i + 1] += {self.canvas_noise * 255};
                    imageData.data[i + 2] += {self.canvas_noise * 255};
                }}
                context.putImageData(imageData, 0, 0);
                return originalToDataURL.apply(this, arguments);
            }};

            // 修改 getImageData 方法
            CanvasRenderingContext2D.prototype.getImageData = function() {{
                const imageData = originalGetImageData.apply(this, arguments);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] += {self.canvas_noise * 255};
                    imageData.data[i + 1] += {self.canvas_noise * 255};
                    imageData.data[i + 2] += {self.canvas_noise * 255};
                }}
                return imageData;
            }};
        }})();
        """

    def get_webgl_injection_script(self) -> str:
        """
        获取 WebGL 指纹伪装注入脚本

        Returns:
            JavaScript 注入脚本
        """
        return f"""
        (() => {{
            // 保存原始方法
            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;

            // 修改 getParameter 方法
            WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) {{ // UNMASKED_VENDOR_WEBGL
                    return "{self.webgl_vendor}";
                }}
                if (parameter === 37446) {{ // UNMASKED_RENDERER_WEBGL
                    return "{self.webgl_renderer}";
                }}
                return originalGetParameter.apply(this, arguments);
            }};
        }})();
        """

    def get_audio_injection_script(self) -> str:
        """
        获取 AudioContext 指南伪装注入脚本

        Returns:
            JavaScript 注入脚本
        """
        return f"""
        (() => {{
            // 修改 AudioContext 创建
            const originalAudioContext = window.AudioContext || window.webkitAudioContext;

            window.AudioContext = function() {{
                const context = new originalAudioContext();
                const originalCreateAnalyser = context.createAnalyser;

                context.createAnalyser = function() {{
                    const analyser = originalCreateAnalyser.apply(this, arguments);
                    const originalGetFloatFrequencyData = analyser.getFloatFrequencyData;

                    analyser.getFloatFrequencyData = function(array) {{
                        originalGetFloatFrequencyData.apply(this, arguments);
                        for (let i = 0; i < array.length; i++) {{
                            array[i] *= {self.audio_fingerprint};
                        }}
                    }};

                    return analyser;
                }};

                return context;
            }};
        }})();
        """

    def get_navigator_injection_script(self) -> str:
        """
        获取 Navigator 对象伪装注入脚本

        Returns:
            JavaScript 注入脚本
        """
        return """
        (() => {
            // 修改 navigator.plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    return [
                        {
                            0: {type: 'application/x-google-chrome-pdf', suffixes: 'pdf', description: 'Portable Document Format'},
                            description: 'Portable Document Format',
                            filename: 'internal-pdf-viewer',
                            length: 1,
                            name: 'Chrome PDF Plugin'
                        }
                    ];
                }
            });

            // 修改 navigator.languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-CN', 'zh', 'en-US', 'en']
            });

            // 修改 navigator.hardwareConcurrency
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 4
            });

            // 修改 navigator.deviceMemory
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8
            });
        })();
        """

    def get_all_injection_scripts(self) -> str:
        """
        获取所有指纹伪装注入脚本

        Returns:
            合并的 JavaScript 注入脚本
        """
        scripts = [
            self.get_canvas_injection_script(),
            self.get_webgl_injection_script(),
            self.get_audio_injection_script(),
            self.get_navigator_injection_script()
        ]
        return "\n".join(scripts)

    def get_injection_config(self) -> Dict:
        """
        获取注入配置（用于 Playwright）

        Returns:
            配置字典
        """
        return {
            "scripts": [self.get_all_injection_scripts()],
            "type": "javascript"
        }


def main():
    """命令行入口"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="浏览器指纹伪装工具")
    parser.add_argument(
        "--output",
        type=str,
        default="fingerprint.js",
        help="输出文件路径"
    )
    parser.add_argument(
        "--type",
        type=str,
        choices=["canvas", "webgl", "audio", "navigator", "all"],
        default="all",
        help="指纹类型"
    )

    args = parser.parse_args()

    # 创建指纹伪装实例
    fingerprint = BrowserFingerprint()

    # 根据类型获取注入脚本
    if args.type == "canvas":
        script = fingerprint.get_canvas_injection_script()
    elif args.type == "webgl":
        script = fingerprint.get_webgl_injection_script()
    elif args.type == "audio":
        script = fingerprint.get_audio_injection_script()
    elif args.type == "navigator":
        script = fingerprint.get_navigator_injection_script()
    else:
        script = fingerprint.get_all_injection_scripts()

    # 输出脚本
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(script)

    print(f"✓ 指纹伪装脚本已生成: {args.output}")
    print(f"✓ 指纹类型: {args.type}")


if __name__ == "__main__":
    main()
