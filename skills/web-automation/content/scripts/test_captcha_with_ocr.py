#!/usr/bin/env python3
"""
使用 OCR 识别验证码的测试脚本
测试 51CTO 等网站的验证码处理能力
"""

import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright, Page

# 添加技能路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.ocr_service import OCRService


async def main():
    """主测试函数"""
    print("=" * 60)
    print("验证码识别测试 - 使用 OCR 服务")
    print("=" * 60)
    
    # 初始化 OCR 服务
    print("\n[1/3] 初始化 OCR 服务...")
    try:
        ocr = OCRService(
            use_angle_cls=True,
            lang="ch",
            use_gpu=False,
            show_log=False
        )
        print("✅ OCR 服务初始化成功")
    except Exception as e:
        print(f"❌ OCR 服务初始化失败: {e}")
        return
    
    # 访问带验证码的网站
    target_url = "https://blog.51cto.com/"
    print(f"\n[2/3] 访问目标网站: {target_url}")
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(
            headless=False,  # 显示浏览器窗口，方便观察验证码
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        page = await context.new_page()
        
        try:
            # 访问目标网站
            print("📄 正在加载页面...")
            response = await page.goto(target_url, wait_until="networkidle", timeout=30000)
            
            status = response.status
            print(f"📊 HTTP 状态码: {status}")
            
            # 检查是否有验证码
            print("\n🔍 检查页面是否有验证码...")
            
            # 截图保存
            screenshot_path = "/workspace/full-test/captcha_screenshot.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            print(f"📸 页面截图已保存: {screenshot_path}")
            
            # 尝试 OCR 识别整个页面
            print(f"\n[3/3] 使用 OCR 识别页面内容...")
            ocr_result = ocr.recognize_image(screenshot_path)
            
            if ocr_result["success"]:
                print(f"✅ OCR 识别成功")
                print(f"   识别到 {len(ocr_result.get('text_lines', []))} 行文字")
                
                # 查找验证码相关关键词
                captcha_keywords = ["验证码", "验证", "码", "code", "captcha", "human"]
                found_captcha = False
                
                for line in ocr_result.get('text_lines', []):
                    text = line.get('text', '')
                    for keyword in captcha_keywords:
                        if keyword.lower() in text.lower():
                            print(f"\n🎯 发现验证码相关文字: {text}")
                            found_captcha = True
                            break
                
                if not found_captcha:
                    print("⚠️ 未在页面中发现明显的验证码文字")
                
                # 显示识别结果摘要
                print("\n📝 OCR 识别结果（前 10 行）:")
                for i, line in enumerate(ocr_result.get('text_lines', [])[:10]):
                    text = line.get('text', '')
                    confidence = line.get('confidence', 0)
                    print(f"   {i+1}. [{confidence:.2f}] {text}")
            
            else:
                print(f"❌ OCR 识别失败: {ocr_result.get('error', '未知错误')}")
            
            # 尝试查找验证码图片元素
            print("\n🔍 查找验证码图片元素...")
            captcha_images = await page.query_selector_all('img[src*="captcha"], img[src*="code"], img[alt*="验证"], img[alt*="code"]')
            
            if captcha_images:
                print(f"✅ 找到 {len(captcha_images)} 个验证码图片元素")
                
                for i, img in enumerate(captcha_images):
                    try:
                        img_src = await img.get_attribute('src')
                        print(f"\n   图片 {i+1}: {img_src}")
                        
                        # 截取验证码图片
                        captcha_img_path = f"/workspace/full-test/captcha_img_{i}.png"
                        await img.screenshot(path=captcha_img_path)
                        print(f"   ✅ 验证码图片已保存: {captcha_img_path}")
                        
                        # 识别验证码
                        captcha_result = ocr.recognize_image(captcha_img_path)
                        
                        if captcha_result["success"]:
                            captcha_text = ''.join([line.get('text', '') for line in captcha_result.get('text_lines', [])])
                            print(f"   🔤 识别结果: {captcha_text}")
                        else:
                            print(f"   ❌ 识别失败: {captcha_result.get('error')}")
                    
                    except Exception as e:
                        print(f"   ❌ 处理失败: {e}")
            else:
                print("⚠️ 未找到验证码图片元素")
            
            # 等待用户观察（非 headless 模式）
            if not browser._impl_obj._options.headless:
                print("\n⏳ 浏览器窗口将保持 10 秒，请观察页面...")
                await asyncio.sleep(10)
        
        except Exception as e:
            print(f"❌ 访问失败: {e}")
        
        finally:
            await browser.close()
    
    print("\n" + "=" * 60)
    print("验证码识别测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
