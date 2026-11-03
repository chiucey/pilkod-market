#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
微信公众号文章抓取主脚本
Author: OpenClaw User
Version: 1.0.0
"""

import os
import sys
import json
import time
import re
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Selenium imports
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Pillow for image processing
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class WechatArticleFetcher:
    """微信公众号文章抓取器"""
    
    def __init__(
        self,
        output_dir: str = "./output",
        enable_ocr: bool = True,
        max_comments: int = 10,
        headless: bool = False
    ):
        """
        初始化抓取器
        
        Args:
            output_dir: 输出目录
            enable_ocr: 是否启用OCR
            max_comments: 最大评论数
            headless: 是否使用无头模式
        """
        self.output_dir = Path(output_dir)
        self.images_dir = self.output_dir / "images"
        self.enable_ocr = enable_ocr
        self.max_comments = max_comments
        self.headless = headless
        
        # 创建目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(exist_ok=True)
        
        # 浏览器驱动
        self.driver = None

        # 当前公众号名称（用于动态水印过滤）
        self.current_author = ""

        # OCR引擎
        self.ocr_engine = None
        if enable_ocr:
            self._init_ocr()
    
    def _init_ocr(self):
        """初始化OCR引擎"""
        # 尝试加载EasyOCR
        try:
            import easyocr
            self.ocr_engine = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            self.ocr_type = 'easyocr'
            print("[OCR] 使用 EasyOCR")
            return
        except ImportError:
            pass
        
        # 尝试加载PaddleOCR
        try:
            from paddleocr import PaddleOCR
            self.ocr_engine = PaddleOCR(use_angle_cls=True, lang='ch', use_gpu=False)
            self.ocr_type = 'paddleocr'
            print("[OCR] 使用 PaddleOCR")
            return
        except ImportError:
            pass
        
        # 尝试Tesseract
        try:
            import pytesseract
            self.ocr_engine = pytesseract
            self.ocr_type = 'tesseract'
            print("[OCR] 使用 Tesseract")
            return
        except ImportError:
            pass
        
        print("[OCR] 未找到OCR工具，图片文字识别功能不可用")
        self.ocr_engine = None
        self.ocr_type = None
    
    def _init_browser(self):
        """初始化浏览器"""
        print("[浏览器] 正在启动...")
        
        # 优先使用Edge（Windows自带）
        try:
            options = EdgeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            
            self.driver = webdriver.Edge(options=options)
            print("[浏览器] Edge 启动成功")
            return
        except Exception as e:
            print(f"[浏览器] Edge 启动失败: {e}")
        
        # 尝试Chrome
        try:
            options = ChromeOptions()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--no-sandbox')
            options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=options)
            print("[浏览器] Chrome 启动成功")
            return
        except Exception as e:
            print(f"[浏览器] Chrome 启动失败: {e}")
        
        raise RuntimeError("无法启动浏览器，请确保已安装 Edge 或 Chrome")
    
    def _download_image(self, url: str, save_path: Path, referer: str) -> bool:
        """下载图片"""
        try:
            # 处理URL
            if url.startswith('http://'):
                url = 'https://' + url[7:]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': referer
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
        except Exception as e:
            print(f"    [图片] 下载失败: {e}")
        return False
    
    def _get_image_size(self, image_path: Path) -> tuple:
        """获取图片尺寸"""
        if HAS_PIL:
            try:
                with Image.open(image_path) as img:
                    return img.size
            except:
                pass
        
        # 从文件头读取JPEG尺寸
        try:
            with open(image_path, 'rb') as f:
                data = f.read()
                if data[0] == 0xFF and data[1] == 0xD8:
                    offset = 2
                    while offset < len(data) - 1:
                        if data[offset] != 0xFF:
                            break
                        marker = data[offset + 1]
                        offset += 2
                        if marker == 0xC0 or marker == 0xC2:
                            height = (data[offset + 3] << 8) | data[offset + 4]
                            width = (data[offset + 5] << 8) | data[offset + 6]
                            return (width, height)
                        length = (data[offset] << 8) | data[offset + 1]
                        offset += length
        except:
            pass
        
        return (800, 600)
    
    def _ocr_image(self, image_path: Path, author: str = "") -> str:
        """OCR识别图片文字

        Args:
            image_path: 图片路径
            author: 公众号名称（用于动态过滤该公众号的水印）
        """
        if not self.ocr_engine:
            return ""

        try:
            if self.ocr_type == 'easyocr':
                results = self.ocr_engine.readtext(str(image_path))
                text = '\n'.join([r[1] for r in results])
            elif self.ocr_type == 'paddleocr':
                results = self.ocr_engine.ocr(str(image_path), cls=True)
                text = '\n'.join([line[1][0] for line in results[0]] if results else [])
            elif self.ocr_type == 'tesseract':
                text = self.ocr_engine.image_to_string(Image.open(image_path), lang='chi_sim+eng')
            else:
                text = ""

            # 过滤水印和推广文字（传入公众号名称用于动态过滤）
            text = self._filter_watermark(text, author)
            return text.strip()
        except Exception as e:
            print(f"    [OCR] 识别失败: {e}")
            return ""
    
    def _filter_watermark(self, text: str, author: str = "") -> str:
        """
        过滤水印和推广文字

        Args:
            text: OCR识别出的原始文本
            author: 公众号名称（用于动态过滤该公众号的水印）
        """
        # 基础过滤规则
        filters = [
            r'扫码关注[：:]?\s*\w+',
            r'点击关注',
            r'长按识别[：:]?\s*\w*',
            r'关注[我们您]?[：:]?\s*\w*',
            r'更多精彩',
            r'分享到[：:]?\s*\w*',
            r'转载需注明',
            r'本文来源',
            r'作者[：:]?\s*\w*',
            r'来源[：:]?\s*\w*',
            r'阅读[：:]?\s*\w*',
            r'在看[：:]?\s*\w*',
            r'赞[：:]?\s*\w*',
            r'收藏',
        ]

        for pattern in filters:
            text = re.sub(pattern, '', text)

        # 动态添加公众号名称作为过滤词
        if author:
            # 公众号名称的多种写法变体
            author_variants = [
                author,                           # 原名
                author + '公众号',                 # 加"公众号"后缀
                author + '视频号',                 # 加"视频号"后缀
                author.replace(' ', ''),          # 去掉空格
                author.replace(' ', '') + '公众号', # 去空格+后缀
            ]

            # 如果公众号名含英文，添加全大写版本
            if any(c.isalpha() and c.islower() for c in author):
                author_variants.append(author.upper())
                author_variants.append(author.upper() + '公众号')

            for variant in author_variants:
                if len(variant) >= 2:  # 只过滤长度>=2的变体
                    text = re.sub(re.escape(variant), '', text)

        # 过滤纯水印行（短行且含特定关键词）
        lines = text.split('\n')
        filtered_lines = []
        watermark_keywords = ['关注', '扫码', '分享', '在看', '收藏', '来源', '作者']

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 过滤短行（<8字符）且只包含水印关键词
            if len(line) < 8 and any(kw in line for kw in watermark_keywords):
                continue

            # 过滤只包含公众号名称的行
            if author and len(line) < len(author) + 3 and author in line:
                continue

            filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    def _detect_content_boundary(self, content_el, content_html: str) -> int:
        """
        检测正文边界，识别正文结束位置

        通过多种策略判断正文何时结束、广告/推广内容从何处开始：
        1. 关键词定位：相关阅读、推荐阅读、广告等
        2. 结构分析：检查section/div等结构变化
        3. 内容密度：正文内容密度高，广告区密度低
        4. 元素类型：常见广告元素识别

        Args:
            content_el: 正文区域的WebElement
            content_html: 正文区域的HTML内容

        Returns:
            正文结束位置索引（字符位置），-1表示未检测到边界
        """
        if not content_html:
            return -1

        # 策略1：关键词定位 - 常见正文结束标志
        end_markers = [
            # 相关阅读类
            r'相关阅读[：:]?',
            r'推荐阅读[：:]?',
            r'往期推荐[：:]?',
            r'更多推荐[：:]?',
            r'热文推荐[：:]?',
            r'精选推荐[：:]?',
            r'延伸阅读[：:]?',
            r'阅读推荐[：:]?',
            # 广告类
            r'广告[：:]?',
            r'推广[：:]?',
            r'商务合作[：:]?',
            r'合作联系[：:]?',
            # 互动类
            r'互动留言[：:]?',
            r'留言区[：:]?',
            r'评论区[：:]?',
            # 关注类
            r'长按.*识别.*关注',
            r'扫码.*关注',
            r'点击.*关注',
            r'关注.*公众号',
            # 文章信息类
            r'正文完',
            r'文章转载',
            r'原创声明',
            # 分隔类
            r'─' * 10,
            r'─' * 5,
            r'—' * 5,
        ]

        best_position = -1

        for marker in end_markers:
            matches = list(re.finditer(marker, content_html, re.IGNORECASE))
            if matches:
                # 取最后一个匹配位置（最接近正文的结束标记）
                pos = matches[-1].start()
                if best_position == -1 or pos < best_position:
                    best_position = pos

        if best_position != -1:
            print(f"    [边界检测] 通过关键词定位到正文结束位置")
            return best_position

        # 策略2：结构分析 - 检测常见广告容器
        ad_containers = [
            r'<section[^>]*class="[^"]*ad[^"]*"',
            r'<div[^>]*class="[^"]*ad[^"]*"',
            r'<section[^>]*class="[^"]*promo[^"]*"',
            r'<div[^>]*class="[^"]*promo[^"]*"',
            r'<section[^>]*class="[^"]*related[^"]*"',
            r'<div[^>]*class="[^"]*related[^"]*"',
            r'<section[^>]*class="[^"]*recommend[^"]*"',
            r'<div[^>]*class="[^"]*recommend[^"]*"',
        ]

        for container in ad_containers:
            matches = list(re.finditer(container, content_html, re.IGNORECASE))
            if matches:
                pos = matches[0].start()
                if best_position == -1 or pos < best_position:
                    best_position = pos
                    print(f"    [边界检测] 通过结构分析定位到正文结束位置")
                    return best_position

        # 策略3：分析段落密度变化
        # 提取所有段落并分析长度分布
        paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', content_html, re.DOTALL | re.IGNORECASE)
        if paragraphs:
            # 计算正文段落的平均长度
            text_lengths = [len(re.sub(r'<[^>]+>', '', p).strip()) for p in paragraphs]
            valid_lengths = [l for l in text_lengths if l > 20]  # 过滤短段落

            if valid_lengths:
                avg_length = sum(valid_lengths) / len(valid_lengths)

                # 从后向前扫描，找到正文内容密度突然下降的位置
                for i in range(len(paragraphs) - 1, -1, -1):
                    length = text_lengths[i]
                    if length > 0:
                        text = re.sub(r'<[^>]+>', '', paragraphs[i]).strip()
                        # 如果段落很短且含有推广关键词
                        if length < avg_length * 0.3:
                            if any(kw in text for kw in ['相关', '推荐', '广告', '关注', '扫码', '阅读', '原文']):
                                # 找到这个段落在HTML中的位置
                                pos = content_html.find(paragraphs[i])
                                if pos > 0:
                                    print(f"    [边界检测] 通过内容密度分析定位到正文结束位置")
                                    return pos

        # 未检测到明确边界
        return -1

    def _extract_main_content(self, content_el, content_html: str) -> tuple:
        """
        提取纯净的正文内容，排除广告和推广

        Args:
            content_el: 正文区域的WebElement
            content_html: 正文区域的HTML内容

        Returns:
            (正文文本, 正文HTML, 是否检测到边界)
        """
        boundary_pos = self._detect_content_boundary(content_el, content_html)

        if boundary_pos != -1 and boundary_pos > 100:
            # 找到了正文边界，截取正文部分
            main_html = content_html[:boundary_pos]
            main_text = re.sub(r'<[^>]+>', '', main_html)
            main_text = re.sub(r'\s+', '\n', main_text).strip()
            return main_text, main_html, True
        else:
            # 未检测到边界，返回完整内容
            return content_el.text.strip(), content_html, False
    
    def fetch(self, url: str) -> Dict[str, Any]:
        """
        抓取文章
        
        Args:
            url: 微信公众号文章链接
        
        Returns:
            文章数据字典
        """
        print("=" * 60)
        print("微信公众号文章抓取工具")
        print("=" * 60)
        print(f"\n目标URL: {url}")
        print(f"输出目录: {self.output_dir}")
        
        # 初始化浏览器
        if not self.driver:
            self._init_browser()
        
        try:
            # 访问文章
            print("\n[1/7] 访问文章...")
            self.driver.get(url)
            
            # 等待加载
            print("[2/7] 等待页面加载...")
            wait = WebDriverWait(self.driver, 30)
            
            try:
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#js_content, .rich_media_content, #js_image_content')
                ))
            except TimeoutException:
                print("    [警告] 页面加载超时")
            
            time.sleep(10)  # 额外等待，确保动态内容加载完成
            
            # 提取标题
            print("[3/7] 提取文章信息...")
            try:
                title_el = self.driver.find_element(By.CSS_SELECTOR, '.rich_media_title, #activity-name')
                title = title_el.text.strip()
            except NoSuchElementException:
                title = "未知标题"
            print(f"    标题: {title}")
            
            # 提取作者（公众号名称）
            try:
                author_el = self.driver.find_element(By.CSS_SELECTOR, '#js_name, .rich_media_meta_nickname')
                author = author_el.text.strip()
            except NoSuchElementException:
                author = ""
            if author:
                print(f"    作者: {author}")
                self.current_author = author  # 保存公众号名称用于水印过滤
            
            # 提取时间
            try:
                time_el = self.driver.find_element(By.CSS_SELECTOR, '#publish_time')
                pub_time = time_el.text.strip()
            except NoSuchElementException:
                pub_time = ""
            if pub_time:
                print(f"    时间: {pub_time}")
            
            # 提取正文文字
            print("[4/7] 提取正文内容...")
            content_text = ""
            content_html = ""
            boundary_detected = False

            try:
                # 优先获取普通文章正文
                content_el = self.driver.find_element(By.CSS_SELECTOR, '#js_content, .rich_media_content')
                content_html = content_el.get_attribute('innerHTML') or ""

                # 智能检测正文边界，排除广告和推广内容
                content_text, main_html, boundary_detected = self._extract_main_content(content_el, content_html)
                content_html = main_html

                if boundary_detected:
                    print(f"    正文长度: {len(content_text)} 字符 (已排除广告推广)")
                else:
                    print(f"    正文长度: {len(content_text)} 字符")
            except NoSuchElementException:
                # 尝试获取图片文章描述
                try:
                    desc_el = self.driver.find_element(By.CSS_SELECTOR, '#js_image_desc, .share_notice')
                    content_text = desc_el.text.strip()
                    print(f"    描述: {content_text[:50]}...")
                except NoSuchElementException:
                    print("    未找到正文内容")
            
            # 下载图片
            print("[5/7] 下载图片...")
            
            # 获取正文区域的图片
            try:
                content_el = self.driver.find_element(By.CSS_SELECTOR, '#js_content, .rich_media_content')
                img_elements = content_el.find_elements(By.TAG_NAME, 'img')
                print(f"    找到 {len(img_elements)} 张图片元素")
            except NoSuchElementException:
                img_elements = self.driver.find_elements(By.TAG_NAME, 'img')
                print(f"    页面总图片: {len(img_elements)}")
            
            downloaded_images = []
            seen_urls = set()
            
            for idx, img in enumerate(img_elements):
                # 优先获取 data-src，其次 src
                img_url = img.get_attribute('data-src') or img.get_attribute('src')
                class_name = img.get_attribute('class') or ''
                
                # 过滤条件
                if not img_url or img_url in seen_urls:
                    continue
                
                # 只保留微信图片
                if 'mmbiz.qpic.cn' not in img_url and 'wxapp-asset' not in img_url:
                    continue
                
                # 过滤头像、二维码等
                if any(skip in class_name.lower() for skip in ['avatar', 'qrcode', 'follow', 'head_img', 'profile']):
                    continue
                
                # 过滤表情包等小图（通常包含 emoji 或特定路径）
                if 'emoji' in img_url.lower() or '/0?' in img_url:
                    continue
                
                seen_urls.add(img_url)
                
                # 处理URL
                if img_url.startswith('http://'):
                    img_url = 'https://' + img_url[7:]
                
                # 获取格式
                fmt = 'jpg'
                if 'mmbiz_png' in img_url:
                    fmt = 'png'
                elif 'mmbiz_gif' in img_url:
                    fmt = 'gif'
                
                img_path = self.images_dir / f"image_{len(downloaded_images)+1:02d}.{fmt}"
                print(f"    下载图片 {len(downloaded_images)+1}...", end=' ')
                
                if self._download_image(img_url, img_path, url):
                    width, height = self._get_image_size(img_path)
                    downloaded_images.append({
                        'index': len(downloaded_images) + 1,
                        'path': str(img_path),
                        'url': img_url,
                        'format': fmt,
                        'width': width,
                        'height': height
                    })
                    print("OK")
                else:
                    print("FAIL")
            
            print(f"    共下载 {len(downloaded_images)} 张图片")
            
            # OCR识别
            ocr_results = {}
            if self.enable_ocr and self.ocr_engine:
                print("[6/7] 识别图片文字...")
                for img in downloaded_images:
                    img_path = Path(img['path'])
                    print(f"    处理: {img_path.name}")
                    text = self._ocr_image(img_path, self.current_author)
                    ocr_results[img_path.name] = {
                        'text': text,
                        'width': img['width'],
                        'height': img['height']
                    }
            else:
                print("[6/7] 跳过OCR识别")
            
            # 获取评论
            print("[7/7] 获取评论...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            comments = []
            try:
                comment_items = self.driver.find_elements(By.CSS_SELECTOR, '.discuss_item, .comment_item')
                for item in comment_items[:self.max_comments]:
                    try:
                        nick = item.find_element(By.CSS_SELECTOR, '.discuss_sender, .comment_nickname').text.strip()
                        content = item.find_element(By.CSS_SELECTOR, '.discuss_message, .comment_content').text.strip()
                        likes = item.find_element(By.CSS_SELECTOR, '.discuss_extra, .comment_like_num').text.strip()
                        
                        comments.append({
                            'nickname': nick,
                            'content': content,
                            'likes': likes,
                            'replies': []
                        })
                    except NoSuchElementException:
                        pass
                
                print(f"    找到 {len(comments)} 条评论")
            except Exception as e:
                print(f"    未找到评论区: {e}")
            
            # 组装数据
            article_data = {
                'title': title,
                'author': author,
                'publish_time': pub_time,
                'content': content_text,
                'content_html': content_html,
                'images': downloaded_images,
                'comments': comments,
                'url': url,
                'fetch_time': datetime.now().isoformat(),
                'ocr_results': ocr_results,
                'boundary_detected': boundary_detected  # 记录是否检测到正文边界
            }
            
            # 保存数据
            data_file = self.output_dir / "article_data.json"
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            
            print("\n" + "=" * 60)
            print("抓取完成!")
            print("=" * 60)
            print(f"\n数据已保存: {data_file}")
            
            return article_data
            
        except Exception as e:
            print(f"\n[错误] 抓取失败: {e}")
            raise
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def generate_docx(self, article_data: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """
        生成Word文档
        
        Args:
            article_data: 文章数据
            output_path: 输出路径（可选，默认为桌面）
        
        Returns:
            生成的文档路径
        """
        # 默认输出到桌面
        if output_path is None:
            desktop = Path.home() / 'Desktop'
            if not desktop.exists():
                desktop = Path.home() / '桌面'
            if not desktop.exists():
                desktop = self.output_dir
            title = re.sub(r'[\\/:*?"<>|]', '_', article_data['title'])
            output_path = str(desktop / f"{title}.docx")
        
        # 调用Node.js脚本生成Word
        script_dir = Path(__file__).parent
        docx_script = script_dir / "generate_docx.js"
        
        if not docx_script.exists():
            raise FileNotFoundError(f"找不到Word生成脚本: {docx_script}")
        
        # 保存临时数据文件
        temp_data = self.output_dir / "temp_article_data.json"
        with open(temp_data, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False)
        
        # 调用Node.js
        import subprocess
        result = subprocess.run(
            ['node', str(docx_script), str(temp_data)],
            cwd=str(self.output_dir),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode != 0:
            print(f"[错误] Word生成失败: {result.stderr}")
            raise RuntimeError(f"Word生成失败: {result.stderr}")
        
        print(f"\n[Word] 文档已生成: {output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description='微信公众号文章抓取工具')
    parser.add_argument('url', help='微信公众号文章链接')
    parser.add_argument('-o', '--output', default='./output', help='输出目录')
    parser.add_argument('--no-ocr', action='store_true', help='禁用OCR')
    parser.add_argument('--headless', action='store_true', help='使用无头模式')
    parser.add_argument('--max-comments', type=int, default=10, help='最大评论数')
    
    args = parser.parse_args()
    
    fetcher = WechatArticleFetcher(
        output_dir=args.output,
        enable_ocr=not args.no_ocr,
        max_comments=args.max_comments,
        headless=args.headless
    )
    
    article_data = fetcher.fetch(args.url)
    fetcher.generate_docx(article_data)


if __name__ == '__main__':
    main()
