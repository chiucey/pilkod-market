#!/usr/bin/env python3
"""
网页/HTML转图片工具
使用Playwright将网页URL或本地HTML文件转换为图片格式
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(json.dumps({
        "success": False,
        "error": "Playwright未安装，请运行: pip install playwright && playwright install chromium",
        "code": "DEPENDENCY_NOT_FOUND"
    }))
    sys.exit(1)


def parse_arguments() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='将网页URL或HTML文件转换为图片'
    )
    parser.add_argument(
        '--source', '-s',
        required=True,
        help='网页URL或本地HTML文件路径'
    )
    parser.add_argument(
        '--output', '-o',
        help='输出图片路径 (默认自动生成)'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['png', 'jpg', 'jpeg', 'webp'],
        default='png',
        help='输出格式 (默认: png)'
    )
    parser.add_argument(
        '--full-page',
        action='store_true',
        default=True,
        help='截取完整页面 (默认: True)'
    )
    parser.add_argument(
        '--viewport-width',
        type=int,
        default=1920,
        help='视口宽度像素 (默认: 1920)'
    )
    parser.add_argument(
        '--viewport-height',
        type=int,
        default=0,
        help='视口高度像素 (0表示自适应, 默认: 0)'
    )
    parser.add_argument(
        '--quality',
        type=int,
        default=90,
        help='图片质量1-100,仅jpg/webp有效 (默认: 90)'
    )
    parser.add_argument(
        '--background-color',
        default='#ffffff',
        help='背景颜色 (默认: #ffffff)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30000,
        help='超时时间毫秒 (默认: 30000)'
    )
    parser.add_argument(
        '--wait-until',
        choices=['load', 'domcontentloaded', 'networkidle'],
        default='networkidle',
        help='等待加载状态 (默认: networkidle)'
    )

    return parser.parse_args()


def is_url(source: str) -> bool:
    """判断source是否为URL"""
    return source.startswith(('http://', 'https://', 'file://'))


def generate_output_path(source: str, output_dir: str = None, format: str = 'png') -> str:
    """生成输出文件路径"""
    if output_dir and os.path.dirname(output_dir):
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        return output_dir

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    if is_url(source):
        from urllib.parse import urlparse
        parsed = urlparse(source)
        filename = parsed.netloc.replace('.', '_') or ' webpage'
        if not output_dir:
            output_dir = '.'
    else:
        filename = Path(source).stem
        if not output_dir:
            output_dir = '.'

    timestamp = os.path.getmtime(source) if os.path.exists(source) else None
    if timestamp:
        import time
        time_str = time.strftime('%Y%m%d_%H%M%S', time.localtime(timestamp))
        filename = f"{filename}_{time_str}"

    return os.path.join(output_dir, f"{filename}.{format}")


def render_to_image(
    source: str,
    output_path: Optional[str] = None,
    format: str = 'png',
    full_page: bool = True,
    viewport_width: int = 1920,
    viewport_height: int = 0,
    quality: int = 90,
    background_color: str = '#ffffff',
    timeout: int = 30000,
    wait_until: str = 'networkidle'
) -> Dict[str, Any]:
    """
    将网页或HTML文件渲染为图片

    Args:
        source: 网页URL或本地HTML文件路径
        output_path: 输出图片路径
        format: 输出格式 (png, jpg, jpeg, webp)
        full_page: 是否截取完整页面
        viewport_width: 视口宽度
        viewport_height: 视口高度 (0表示自适应)
        quality: 图片质量 (1-100)
        background_color: 背景颜色
        timeout: 超时时间(毫秒)
        wait_until: 等待加载状态

    Returns:
        包含成功状态和图片信息的字典
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            context = browser.new_context(
                viewport={'width': viewport_width, 'height': viewport_height or 1080},
                ignore_https_errors=True
            )

            page = context.new_page()

            # 设置背景颜色
            page.evaluate(f'''
                document.body.style.backgroundColor = "{background_color}";
            ''')

            # 加载页面内容
            if is_url(source):
                if source.startswith('http'):
                    page.goto(source, timeout=timeout, wait_until=wait_until)
                else:
                    # 本地文件
                    with open(source, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    page.set_content(html_content, timeout=timeout)
            else:
                # 本地HTML文件
                if not os.path.exists(source):
                    return {
                        "success": False,
                        "error": f"文件不存在: {source}",
                        "code": "SOURCE_NOT_FOUND"
                    }
                with open(source, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                page.set_content(html_content, timeout=timeout)

            # 等待内容稳定
            page.wait_for_load_state('networkidle', timeout=timeout)

            # 等待一点时间让动态内容加载
            page.wait_for_timeout(1000)

            # 更新视口高度(如果设置为自适应)
            if viewport_height == 0:
                content_height = page.evaluate('''
                    Math.max(
                        document.body.scrollHeight,
                        document.documentElement.scrollHeight,
                        document.body.offsetHeight,
                        document.documentElement.offsetHeight,
                        document.body.clientHeight,
                        document.documentElement.clientHeight
                    )
                ''')
                page.set_viewport_size({'width': viewport_width, 'height': content_height})

            # 生成输出路径
            if not output_path:
                output_path = generate_output_path(source, format=format)
            else:
                os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)

            # 确保输出格式正确
            if format == 'jpeg':
                format = 'jpg'

            # 截取图片
            screenshot_options = {
                'full_page': full_page,
                'type': format,
            }

            if format in ['jpg', 'jpeg', 'webp']:
                screenshot_options['quality'] = quality

            page.screenshot(path=output_path, **screenshot_options)

            # 获取图片信息
            file_size = os.path.getsize(output_path)

            # 获取实际截图尺寸
            if full_page:
                dimensions = {
                    'width': page.viewport_size['width'],
                    'height': page.viewport_size['height']
                }
            else:
                dimensions = {
                    'width': page.viewport_size['width'],
                    'height': page.viewport_size['height']
                }

            browser.close()

            return {
                "success": True,
                "output_path": output_path,
                "format": format,
                "dimensions": dimensions,
                "file_size": file_size
            }

    except Exception as e:
        error_message = str(e)
        error_code = "RENDER_FAILED"

        if "net::ERR" in error_message or "Failed to navigate" in error_message:
            error_code = "SOURCE_NOT_FOUND"
        elif "Timeout" in error_message:
            error_code = "TIMEOUT"
        elif "No such file" in error_message or "Cannot find" in error_message:
            error_code = "SOURCE_NOT_FOUND"

        return {
            "success": False,
            "error": error_message,
            "code": error_code
        }


def main():
    """主函数"""
    args = parse_arguments()

    # 处理视口高度
    viewport_height = args.viewport_height if args.viewport_height > 0 else 0

    result = render_to_image(
        source=args.source,
        output_path=args.output,
        format=args.format,
        full_page=args.full_page,
        viewport_width=args.viewport_width,
        viewport_height=viewport_height,
        quality=args.quality,
        background_color=args.background_color,
        timeout=args.timeout,
        wait_until=args.wait_until
    )

    # 输出JSON结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 根据结果返回退出码
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
