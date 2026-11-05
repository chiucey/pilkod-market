#!/usr/bin/env python3
"""
Douyin Browser Automation with QR Login (Python Version)

This module provides browser-based Douyin access with QR code login for MaxClaw skill integration.

Usage:
    from douyin_browser import DouyinBrowser
    browser = DouyinBrowser()
    result = await browser.login()  # Returns QR code as base64
    result = await browser.search("美食教程")
    result = await browser.get_video_info("https://www.douyin.com/video/xxx")
    result = await browser.get_trending()
"""

import asyncio
import base64
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict

# Try to import playwright, install if needed
try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    print("Installing playwright...")
    os.system("pip install playwright -q")
    os.system("playwright install chromium")
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page


@dataclass
class QRCodeResult:
    """QR code generation result"""
    success: bool
    qr_code_base64: Optional[str] = None
    qr_image_path: Optional[str] = None
    message: str = ""
    error: Optional[str] = None


@dataclass
class LoginResult:
    """Login result"""
    success: bool
    session_file: Optional[str] = None
    message: str = ""
    error: Optional[str] = None


@dataclass
class VideoInfo:
    """Video information"""
    title: str = ""
    author: str = ""
    description: str = ""
    likes: str = ""
    comments: str = ""
    shares: str = ""
    plays: str = ""
    hashtags: List[str] = None
    url: str = ""

    def __post_init__(self):
        if self.hashtags is None:
            self.hashtags = []


@dataclass
class VideoSearchResult:
    """Video search result"""
    videos: List[Dict[str, Any]]
    query: str
    total_count: int


class DouyinBrowser:
    """
    Douyin Browser Automation Class

    Provides browser-based access to Douyin with QR code login support.
    """

    def __init__(
        self,
        data_dir: str = None,
        headless: bool = False,
        timeout: int = 120000
    ):
        """
        Initialize Douyin Browser

        Args:
            data_dir: Directory for storing session data and QR codes
            headless: Whether to run browser in headless mode
            timeout: Timeout for operations in milliseconds
        """
        self.base_dir = Path(data_dir or os.path.join(os.path.dirname(__file__), '../data'))
        self.qr_dir = self.base_dir / 'qrcodes'
        self.session_file = self.base_dir / 'session.json'

        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.qr_dir.mkdir(parents=True, exist_ok=True)

        self.headless = headless
        self.timeout = timeout

        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.playwright = await async_playwright().start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def launch_browser(self) -> Browser:
        """Launch browser with anti-detection settings"""
        if self.browser:
            return self.browser

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        return self.browser

    async def create_context(self) -> BrowserContext:
        """Create browser context with realistic user agent"""
        browser = await self.launch_browser()

        self.context = await browser.new_context(
            viewport={'width': 1280, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        return self.context

    async def close(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    def _load_session(self) -> Optional[Dict]:
        """Load saved session"""
        if self.session_file.exists():
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def _save_session(self, cookies: List, user_agent: str):
        """Save session cookies"""
        session_data = {
            'cookies': cookies,
            'login_time': self._get_timestamp(),
            'user_agent': user_agent
        }
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    async def generate_qr_code(self, page: Page) -> Optional[str]:
        """
        Find and extract QR code from login page

        Args:
            page: Playwright page object

        Returns:
            Base64 encoded QR code image, or None if not found
        """
        # QR code selectors (Douyin may change these)
        qr_selectors = [
            '.login-qrcode img',
            'img[class*="qrcode"]',
            'img[class*="qr-code"]',
            '[class*="qrcode"] img',
            '.qrcode-container img',
            'img[alt*="qr" i]',
            '[class*="scan"] img',
            '.login-box img'
        ]

        for selector in qr_selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                img_element = page.locator(selector).first

                # Get image source
                img_src = await img_element.get_attribute('src')

                if img_src:
                    if img_src.startswith('data:'):
                        return img_src  # Already base64

                    # Download image
                    qr_path = self.qr_dir / f'qr_{self._get_timestamp().replace(":", "-")}.png'

                    # Download via page
                    async with page.expect_download() as download_info:
                        pass

                    # Try to get base64 from image
                    img_buffer = await page.evaluate('''(selector) => {
                        const img = document.querySelector(selector);
                        if (img && img.src) {
                            return img.src;
                        }
                        return null;
                    }''', selector)

                    if img_buffer and img_buffer.startswith('data:'):
                        return img_buffer

            except Exception:
                continue

        return None

    async def login(self, poll_interval: float = 2.0) -> LoginResult:
        """
        Perform QR code login

        Args:
            poll_interval: How often to check for successful login (seconds)

        Returns:
            LoginResult with success status and session info
        """
        try:
            async with self:
                await self.create_context()
                self.page = await self.context.new_page()

                print("📱 Opening Douyin login page...")
                await self.page.goto('https://www.douyin.com/login', timeout=30000)
                await self.page.wait_for_timeout(2000)

                # Generate QR code
                qr_code = await self.generate_qr_code(self.page)

                if not qr_code:
                    return LoginResult(
                        success=False,
                        error="Could not find QR code on login page"
                    )

                # Save QR code image
                qr_path = self.qr_dir / 'current_qr.png'
                if ',' in qr_code:
                    img_data = base64.b64decode(qr_code.split(',')[1])
                else:
                    img_data = base64.b64decode(qr_code)

                with open(qr_path, 'wb') as f:
                    f.write(img_data)

                print("=" * 60)
                print("📱 QR CODE GENERATED")
                print("=" * 60)
                print(f"QR Code saved to: {qr_path}")
                print("Please scan with Douyin app within 2 minutes")
                print("=" * 60)

                # Wait for login
                start_time = asyncio.get_event_loop().time()
                timeout = self.timeout / 1000

                while (asyncio.get_event_loop().time() - start_time) < timeout:
                    await asyncio.sleep(poll_interval)

                    # Check if still on login page
                    current_url = self.page.url
                    if '/login' not in current_url:
                        # Login successful
                        cookies = await self.context.cookies()
                        user_agent = await self.context.evaluate('navigator.userAgent')

                        self._save_session(cookies, user_agent)

                        print("\n🎉 LOGIN SUCCESSFUL!")
                        print(f"Session saved to: {self.session_file}")

                        return LoginResult(
                            success=True,
                            session_file=str(self.session_file),
                            message="Login successful"
                        )

                    elapsed = int(asyncio.get_event_loop().time() - start_time)
                    print(f"\r⏳ Waiting for scan... {elapsed}s / {int(timeout)}s", end='', flush=True)

                return LoginResult(
                    success=False,
                    error="Login timeout - QR code expired"
                )

        except Exception as e:
            return LoginResult(success=False, error=str(e))

    async def get_qr_code_only(self) -> QRCodeResult:
        """
        Generate QR code only without waiting for login

        Returns:
            QRCodeResult with QR code image data
        """
        try:
            async with self:
                await self.create_context()
                self.page = await self.context.new_page()

                print("📱 Opening Douyin login page...")
                await self.page.goto('https://www.douyin.com/login', timeout=30000)
                await self.page.wait_for_timeout(2000)

                qr_code = await self.generate_qr_code(self.page)

                if not qr_code:
                    return QRCodeResult(
                        success=False,
                        error="Could not find QR code on login page"
                    )

                # Save QR code
                qr_path = self.qr_dir / 'current_qr.png'
                if ',' in qr_code:
                    img_data = base64.b64decode(qr_code.split(',')[1])
                else:
                    img_data = base64.b64decode(qr_code)

                with open(qr_path, 'wb') as f:
                    f.write(img_data)

                return QRCodeResult(
                    success=True,
                    qr_code_base64=qr_code,
                    qr_image_path=str(qr_path),
                    message=f"QR code saved to {qr_path}"
                )

        except Exception as e:
            return QRCodeResult(success=False, error=str(e))

    def _ensure_logged_in(self) -> bool:
        """Check if logged in"""
        return self.session_file.exists()

    async def search(self, query: str, limit: int = 20) -> VideoSearchResult:
        """
        Search for videos

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            VideoSearchResult with found videos
        """
        if not self._ensure_logged_in():
            raise PermissionError("Not logged in. Please run login() first.")

        session = self._load_session()

        async with self:
            await self.create_context()
            await self.context.add_cookies(session['cookies'])
            self.page = await self.context.new_page()

            search_url = f'https://www.douyin.com/search/{query}'
            print(f"🔍 Searching: {search_url}")

            await self.page.goto(search_url, timeout=30000)
            await self.page.wait_for_timeout(3000)

            # Scroll to load more
            for _ in range(3):
                await self.page.evaluate('window.scrollBy(0, 500)')
                await self.page.wait_for_timeout(1000)

            # Extract videos
            videos = await self.page.evaluate(f'''
                () => {{
                    const results = [];
                    const items = document.querySelectorAll('[class*="video-card"], [class*="item"]');

                    items.forEach((item, i) => {{
                        if (i >= {limit}) return;

                        const title = item.querySelector('[class*="title"]')?.textContent?.trim();
                        const author = item.querySelector('[class*="author"]')?.textContent?.trim();
                        const link = item.querySelector('a[href*="/video/"]')?.href;

                        if (title || link) {{
                            results.push({{
                                title: title || 'Untitled',
                                author: author || 'Unknown',
                                url: link || ''
                            }});
                        }}
                    }});

                    return results;
                }}
            ''')

            return VideoSearchResult(
                videos=videos,
                query=query,
                total_count=len(videos)
            )

    async def get_video_info(self, video_url: str) -> VideoInfo:
        """
        Get detailed information for a video

        Args:
            video_url: Douyin video URL

        Returns:
            VideoInfo object with video details
        """
        if not self._ensure_logged_in():
            raise PermissionError("Not logged in. Please run login() first.")

        session = self._load_session()

        async with self:
            await self.create_context()
            await self.context.add_cookies(session['cookies'])
            self.page = await self.context.new_page()

            print(f"📹 Getting video info: {video_url}")

            await self.page.goto(video_url, timeout=30000)
            await self.page.wait_for_timeout(3000)

            info = await self.page.evaluate('''
                () => ({
                    title: document.querySelector('h1[class*="title"]')?.textContent?.trim() || '',
                    author: document.querySelector('[class*="author-name"]')?.textContent?.trim() || '',
                    description: document.querySelector('[class*="desc"]')?.textContent?.trim() || '',
                    likes: document.querySelector('[class*="like"] span')?.textContent?.trim() || '',
                    comments: document.querySelector('[class*="comment"] span')?.textContent?.trim() || '',
                    shares: document.querySelector('[class*="share"] span')?.textContent?.trim() || '',
                    plays: document.querySelector('[class*="play-count"]')?.textContent?.trim() || '',
                    hashtags: Array.from(document.querySelectorAll('[class*="tag"] a'))
                        .map(el => el.textContent?.trim())
                        .filter(Boolean),
                    url: window.location.href
                })
            ''')

            return VideoInfo(**info)

    async def get_trending(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get trending videos from homepage

        Args:
            limit: Maximum number of results

        Returns:
            List of trending video info
        """
        if not self._ensure_logged_in():
            raise PermissionError("Not logged in. Please run login() first.")

        session = self._load_session()

        async with self:
            await self.create_context()
            await self.context.add_cookies(session['cookies'])
            self.page = await self.context.new_page()

            print("🔥 Fetching trending videos...")

            await self.page.goto('https://www.douyin.com', timeout=30000)
            await self.page.wait_for_timeout(3000)

            # Scroll to load content
            for _ in range(5):
                await self.page.evaluate('window.scrollBy(0, 800)')
                await self.page.wait_for_timeout(1000)

            trending = await self.page.evaluate(f'''
                () => {{
                    const results = [];
                    const items = document.querySelectorAll('[class*="video-card"], [class*="item"]');

                    items.forEach((item, i) => {{
                        if (i >= {limit}) return;

                        const title = item.querySelector('[class*="title"]')?.textContent?.trim();
                        const author = item.querySelector('[class*="author"]')?.textContent?.trim();
                        const link = item.querySelector('a[href*="/video/"]')?.href;

                        if (title || link) {{
                            results.push({{
                                title: title || 'Untitled',
                                author: author || 'Unknown',
                                url: link || ''
                            }});
                        }}
                    }});

                    return results;
                }}
            ''')

            return trending


# CLI interface
async def main():
    import argparse

    parser = argparse.ArgumentParser(description='Douyin Browser Automation')
    parser.add_argument('command', choices=['login', 'qr', 'search', 'video', 'trending', 'status'],
                        help='Command to run')
    parser.add_argument('args', nargs='*', help='Command arguments')

    args = parser.parse_args()

    browser = DouyinBrowser()

    if args.command == 'login':
        result = await browser.login()
        if result.success:
            print("✅ Login successful!")
        else:
            print(f"❌ Login failed: {result.error}")
            sys.exit(1)

    elif args.command == 'qr':
        result = await browser.get_qr_code_only()
        if result.success:
            print(f"✅ QR code generated: {result.qr_image_path}")
        else:
            print(f"❌ Failed: {result.error}")
            sys.exit(1)

    elif args.command == 'search':
        query = ' '.join(args.args) if args.args else '热门视频'
        result = await browser.search(query)
        print(f"\n✅ Found {result.total_count} videos for '{result.query}'")

    elif args.command == 'video':
        if not args.args:
            print("❌ Video URL required")
            sys.exit(1)
        info = await browser.get_video_info(args.args[0])
        print(f"\n📊 Video Info:")
        print(f"  Title: {info.title}")
        print(f"  Author: {info.author}")
        print(f"  Likes: {info.likes}")
        print(f"  Comments: {info.comments}")

    elif args.command == 'trending':
        videos = await browser.get_trending()
        print(f"\n🔥 Top {len(videos)} Trending Videos:")
        for i, v in enumerate(videos, 1):
            print(f"  {i}. {v['title']} - @{v['author']}")

    elif args.command == 'status':
        session_file = Path(__file__).parent.parent / 'data' / 'session.json'
        if session_file.exists():
            with open(session_file) as f:
                data = json.load(f)
            print(f"✅ Logged in since: {data['login_time']}")
        else:
            print("❌ Not logged in")


if __name__ == '__main__':
    asyncio.run(main())
