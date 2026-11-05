"""
复杂页面处理器 - 使用 PaddleOCR 3.x 对付复杂页面和反爬

支持场景：
- Canvas 渲染的页面（截图 + OCR 提取）
- SVG 图片解析
- 动态内容加载（滚动触发）
- 混淆的 DOM 结构（版面分析）
- 图片形式的文本内容
- 复杂表格布局

参考：https://www.paddleocr.ai/latest/version3.x/pipeline_usage/PP-StructureV3.html
"""

import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import asyncio


class ComplexPageProcessor:
    """复杂页面处理器"""

    def __init__(self, browser, use_gpu: bool = False):
        """
        初始化复杂页面处理器

        Args:
            browser: AsyncPlaywrightBrowser 实例
            use_gpu: 是否使用 GPU
        """
        self.browser = browser
        self.use_gpu = use_gpu

        try:
            from paddleocr import PaddleOCR
            from paddleocr import PPStructure

            # 初始化 OCR
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang='ch',
                use_gpu=use_gpu,
                show_log=False,
                ocr_version='PP-OCRv5',
                det=True,
                rec=True
            )

            # 初始化版面分析引擎（PP-StructureV3）
            if use_gpu:
                self.layout_engine = PaddleOCR(
                    use_angle_cls=True,
                    lang='ch',
                    use_gpu=use_gpu,
                    show_log=False,
                    det=True,
                    rec=True,
                    table=True,
                    layout=True
                )
            else:
                self.layout_engine = None

            # 初始化 PP-StructureV3（用于表格和版面分析）
            self.structure_engine = PPStructure(
                show_log=False,
                table=True,
                ocr=True,
                layout=True,
                structure_version='PP-StructureV3',
                image_orientation=True
            )

            self._initialized = True
        except Exception as e:
            print(f"初始化复杂页面处理器失败: {e}")
            self._initialized = False

    async def extract_from_canvas(self, selector: str,
                                   scroll_to_load: bool = True) -> Dict[str, Any]:
        """
        从 Canvas 元素中提取内容

        方法：
        1. 滚动到 Canvas 元素
        2. 截图 Canvas 区域
        3. 使用 OCR 提取文本
        4. 版面分析识别结构

        Args:
            selector: Canvas 元素选择器
            scroll_to_load: 是否滚动加载完整内容

        Returns:
            提取的内容（文本、版面结构、表格等）
        """
        if not self._initialized:
            return {'success': False, 'error': '处理器未初始化'}

        try:
            # 1. 滚动到 Canvas 元素
            await self.browser.scroll_to_element(selector)

            # 2. 等待元素可见
            await self.browser.wait_for_selector(selector, state='visible')

            # 3. 如果需要，滚动加载完整内容
            if scroll_to_load:
                await self._scroll_canvas_content(selector)

            # 4. 截图 Canvas 区域
            screenshot_path = f"temp_canvas_{Path(selector).replace('/', '_')}.png"
            await self.browser.screenshot_element(selector, screenshot_path)

            # 5. 使用 OCR 提取文本
            ocr_result = self.ocr.ocr(screenshot_path)

            # 6. 使用 PP-StructureV3 进行版面分析
            if self.structure_engine:
                layout_result = self.structure_engine(screenshot_path)
            else:
                layout_result = []

            # 7. 清理临时文件
            import os
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)

            # 8. 处理结果
            text = self._extract_text_from_ocr(ocr_result)
            tables = self._extract_tables_from_layout(layout_result)

            return {
                'success': True,
                'text': text,
                'layout': layout_result,
                'tables': tables
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'提取 Canvas 内容失败: {str(e)}'
            }

    async def _scroll_canvas_content(self, selector: str):
        """滚动 Canvas 内容以加载完整内容"""
        # 模拟用户滚动行为
        for _ in range(5):
            await self.browser.page.keyboard.press('PageDown')
            await asyncio.sleep(0.5)

    async def extract_from_images(self, image_selectors: List[str],
                                   pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        从页面中的图片提取文本

        Args:
            image_selectors: 图片选择器列表
            pattern: 正则表达式模式（用于提取特定格式的文本）

        Returns:
            每个图片的提取结果
        """
        results = []

        for i, selector in enumerate(image_selectors):
            try:
                # 截图图片
                screenshot_path = f"temp_image_{i}.png"
                await self.browser.screenshot_element(selector, screenshot_path)

                # OCR 识别
                ocr_result = self.ocr.ocr(screenshot_path)

                # 提取文本
                text = self._extract_text_from_ocr(ocr_result)

                # 应用正则表达式
                if pattern:
                    import re
                    matches = re.findall(pattern, text)
                    text = ' '.join(matches)

                results.append({
                    'selector': selector,
                    'text': text,
                    'success': True
                })

                # 清理临时文件
                import os
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)

            except Exception as e:
                results.append({
                    'selector': selector,
                    'text': '',
                    'success': False,
                    'error': str(e)
                })

        return results

    async def analyze_complex_layout(self, url: str,
                                      full_page: bool = True) -> Dict[str, Any]:
        """
        分析复杂页面布局（混淆的 DOM 结构）

        方法：
        1. 访问页面并等待加载
        2. 滚动触发懒加载
        3. 截取整个页面或指定区域
        4. 使用 PP-StructureV3 进行版面分析
        5. 识别标题、段落、图片、表格等区域
        6. 提取各区域的文本内容

        Args:
            url: 页面 URL
            full_page: 是否截取整个页面

        Returns:
            页面版面分析结果
        """
        if not self._initialized:
            return {'success': False, 'error': '处理器未初始化'}

        try:
            # 1. 访问页面
            await self.browser.goto(url, wait_until='networkidle')

            # 2. 滚动触发懒加载
            await self._scroll_to_load_content()

            # 3. 截图
            screenshot_path = "temp_page_layout.png"
            if full_page:
                await self.browser.screenshot(screenshot_path, full_page=True)
            else:
                await self.browser.screenshot(screenshot_path)

            # 4. 版面分析
            layout_result = self.structure_engine(screenshot_path)

            # 5. 提取结构化信息
            regions = layout_result
            tables = self._extract_tables_from_layout(layout_result)

            # 6. 清理临时文件
            import os
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)

            return {
                'success': True,
                'url': url,
                'regions': regions,
                'tables': tables
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'分析页面布局失败: {str(e)}'
            }

    async def _scroll_to_load_content(self):
        """滚动页面以加载动态内容"""
        # 获取页面高度
        page_height = await self.browser.page.evaluate('document.body.scrollHeight')

        # 分段滚动
        scroll_step = 500
        current_position = 0

        while current_position < page_height:
            await self.browser.page.evaluate(f'window.scrollTo(0, {current_position})')
            await asyncio.sleep(0.3)  # 等待内容加载
            current_position += scroll_step

        # 滚动回顶部
        await self.browser.page.evaluate('window.scrollTo(0, 0)')

    def _extract_text_from_ocr(self, ocr_result) -> str:
        """从 OCR 结果中提取文本"""
        if not ocr_result or not ocr_result[0]:
            return ''

        texts = []
        for line in ocr_result[0]:
            text_info = line[1]
            text = text_info[0]
            texts.append(text)

        return '\n'.join(texts)

    def _extract_tables_from_layout(self, layout_result) -> List[Dict[str, Any]]:
        """从版面分析结果中提取表格"""
        tables = []

        if not layout_result:
            return tables

        for region in layout_result:
            if region['type'] == 'table':
                tables.append({
                    'html': region.get('res', {}).get('html', ''),
                    'data': region.get('res', {})
                })

        return tables

    async def smart_extraction(self, url: str,
                               fallback_to_ocr: bool = True) -> Dict[str, Any]:
        """
        智能提取：先尝试 DOM 提取，失败则降级到 OCR 提取

        Args:
            url: 页面 URL
            fallback_to_ocr: 是否在 DOM 提取失败时降级到 OCR

        Returns:
            提取的内容
        """
        try:
            # 1. 尝试 DOM 提取
            await self.browser.goto(url, wait_until='networkidle')

            # 尝试获取页面文本
            page_text = await self.browser.page.evaluate('document.body.innerText')

            # 判断是否成功提取到内容
            if len(page_text.strip()) > 100:
                return {
                    'success': True,
                    'method': 'dom',
                    'text': page_text
                }

            # 2. DOM 提取失败，降级到 OCR
            if fallback_to_ocr:
                return await self.analyze_complex_layout(url, full_page=True)

            else:
                return {
                    'success': False,
                    'error': 'DOM 提取失败，且未启用 OCR 降级'
                }

        except Exception as e:
            # 出错时降级到 OCR
            if fallback_to_ocr:
                return await self.analyze_complex_layout(url, full_page=True)
            else:
                return {
                    'success': False,
                    'error': f'提取失败: {str(e)}'
                }


def main():
    """命令行接口"""
    import argparse
    import json
    import asyncio

    parser = argparse.ArgumentParser(description='复杂页面处理器')
    parser.add_argument('--url', help='页面 URL')
    parser.add_argument('--canvas', help='Canvas 元素选择器')
    parser.add_argument('--images', nargs='+', help='图片选择器列表')
    parser.add_argument('--output', help='输出结果到文件')
    parser.add_argument('--gpu', action='store_true', help='使用 GPU 加速')

    args = parser.parse_args()

    async def process():
        from playwright_cli import AsyncPlaywrightBrowser

        # 初始化浏览器
        browser = AsyncPlaywrightBrowser(headless=True)
        await browser.start()

        # 初始化处理器
        processor = ComplexPageProcessor(browser, use_gpu=args.gpu)

        result = None

        if args.url:
            # 分析复杂页面布局
            result = await processor.analyze_complex_layout(args.url)
        elif args.canvas:
            # 从 Canvas 提取内容
            result = await processor.extract_from_canvas(args.canvas)
        elif args.images:
            # 从图片提取文本
            result = await processor.extract_from_images(args.images)

        # 关闭浏览器
        await browser.close()

        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"结果已保存到: {args.output}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))

    asyncio.run(process())


if __name__ == '__main__':
    main()
