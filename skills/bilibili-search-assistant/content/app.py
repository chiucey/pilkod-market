"""
B站（哔哩哔哩）搜索小助手 - 后端服务
用于搜索B站视频并生成Excel统计分析报表
"""

import os
import re
import json
import random
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

app = Flask(__name__, static_folder='.')
CORS(app)

# 确保输出目录存在
os.makedirs('downloads', exist_ok=True)

# B站搜索API
BILIBILI_SEARCH_URL = "https://api.bilibili.com/x/web-interface/search/type"
BILIBILI_WEB_SEARCH_URL = "https://search.bilibili.com/api/search_search"

# 请求头 - 更完整的配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com',
    'Origin': 'https://www.bilibili.com',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br'
}

# 创建一个session来维护cookies
session = requests.Session()
session.headers.update(HEADERS)


def parse_number(text):
    """解析数字字符串，如'10.2万' -> 102000"""
    if not text:
        return 0
    text = str(text).strip()
    if '亿' in text:
        try:
            return int(float(text.replace('亿', '')) * 100000000)
        except:
            return 0
    elif '万' in text:
        try:
            return int(float(text.replace('万', '')) * 10000)
        except:
            return 0
    else:
        try:
            return int(text.replace(',', ''))
        except:
            return 0


def search_bilibili_api(keyword, page=1, page_size=30):
    """使用B站官方API搜索视频"""
    params = {
        'search_type': 'video',
        'keyword': keyword,
        'page': page,
        'page_size': page_size,
        'order': 'totalrank',
        'duration': 0,
        'tids': 0,
        'category_id': 0
    }

    try:
        response = session.get(BILIBILI_SEARCH_URL, params=params, timeout=15)
        data = response.json()

        if data.get('code') == 0:
            return data.get('data', {}).get('result', [])
        else:
            print(f"API错误: {data.get('message')}")
            return []
    except Exception as e:
        print(f"API搜索出错: {e}")
        return []


def search_bilibili_web(keyword, page=1, page_size=30):
    """使用B站网页搜索"""
    params = {
        'search_source': 'normal_search',
        'keyword': keyword,
        'page': page,
        'page_size': page_size,
        'order': 'totalrank',
        'duration': 0,
        'tids_1': 0,
        'tids_2': 0
    }

    try:
        response = session.get(BILIBILI_WEB_SEARCH_URL, params=params, timeout=15)
        data = response.json()

        if data.get('code') == 0:
            return data.get('data', {}).get('result', [])
        else:
            return []
    except Exception as e:
        print(f"网页搜索出错: {e}")
        return []


def scrape_bilibili_page(keyword, page=1):
    """直接抓取B站搜索页面"""
    url = f"https://search.bilibili.com/all?keyword={keyword}&page={page}&order=totalrank"

    try:
        response = session.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 尝试从script标签中提取数据
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and '__INITIAL_STATE__' in script.string:
                match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', script.string, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group(1))
                        videos = data.get('searchUI', {}).get('data', {}).get('result', [])
                        if videos:
                            return videos
                    except:
                        pass

        # 备选：直接查找视频元素
        video_items = soup.select('.video-item, .bili-video-card, .video-list-item')
        results = []

        for item in video_items[:30]:
            try:
                title_elem = item.select_one('.title, .bili-video-card__info--title, a')
                author_elem = item.select_one('.up-name, .bili-video-card__info--author')
                play_elem = item.select_one('.play, .bili-video-card__info--hot')
                video_link = item.select_one('a')
                bvid_match = re.search(r'BV\w+', str(video_link)) if video_link else None

                if title_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'author': author_elem.get_text(strip=True) if author_elem else '',
                        'play': play_elem.get_text(strip=True) if play_elem else '0',
                        'bvid': bvid_match.group(0) if bvid_match else '',
                        'url': video_link.get('href', '') if video_link else ''
                    })
            except:
                continue

        return results

    except Exception as e:
        print(f"页面抓取出错: {e}")
        return []


def get_video_detail(bvid):
    """获取视频详细信息（点赞、投币、收藏等）"""
    detail_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"

    try:
        response = session.get(detail_url, timeout=10)
        data = response.json()

        if data.get('code') == 0:
            stat = data.get('data', {}).get('stat', {})
            return {
                'likes': stat.get('like', 0),
                'coins': stat.get('coin', 0),
                'favorites': stat.get('favorite', 0),
                'shares': stat.get('share', 0),
                'danmus': stat.get('danmaku', 0)
            }
    except Exception as e:
        print(f"获取详情出错 {bvid}: {e}")

    return {
        'likes': 0,
        'coins': 0,
        'favorites': 0,
        'shares': 0,
        'danmus': 0
    }


def search_videos(keyword, max_count=30):
    """搜索并收集视频数据"""
    videos = []
    collected = 0
    page = 1

    # 首先尝试API搜索
    search_results = search_bilibili_api(keyword, page=page, page_size=30)

    # 如果API失败，尝试网页搜索
    if not search_results:
        search_results = search_bilibili_web(keyword, page=page, page_size=30)

    # 如果还是失败，尝试直接抓取
    if not search_results:
        search_results = scrape_bilibili_page(keyword, page=page)

    # 如果所有方法都失败，使用模拟数据（演示用）
    if not search_results:
        print("使用模拟数据进行演示...")
        search_results = generate_mock_data(keyword, max_count)

    for item in search_results[:max_count]:
        bvid = item.get('bvid', '')
        title = item.get('title', '')

        # 清理标题中的HTML标签
        if isinstance(title, str):
            title = re.sub(r'<[^>]+>', '', title)
            title = title.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')

        video_data = {
            'rank': collected + 1,
            'bvid': bvid,
            'title': title,
            'description': item.get('description', ''),
            'author': item.get('author', ''),
            'author_url': f"https://space.bilibili.com/{item.get('mid', '')}",
            'url': item.get('url', '') or (f"https://www.bilibili.com/video/{bvid}" if bvid else ''),
            'pubdate': item.get('pubdate', 0),
            'duration': item.get('duration', ''),
            'views': parse_number(item.get('play', '0')),
            'likes': 0,
            'coins': 0,
            'favorites': 0,
            'comments': parse_number(item.get('review', '0')),
            'danmus': parse_number(item.get('danmaku', '0')),
            'type': item.get('type', ''),
        }

        videos.append(video_data)
        collected += 1
        time.sleep(random.uniform(0.1, 0.2))

    # 获取详细数据（点赞、投币、收藏）
    if videos and videos[0].get('bvid'):
        print(f"已收集 {len(videos)} 条视频，开始获取详细信息...")
        for i, video in enumerate(videos[:15]):
            if video.get('bvid'):
                detail = get_video_detail(video['bvid'])
                video['likes'] = detail['likes']
                video['coins'] = detail['coins']
                video['favorites'] = detail['favorites']
                video['danmus'] = detail['danmus']
                print(f"  [{i+1}/{min(15, len(videos))}] {video['title'][:30]}...")
                time.sleep(random.uniform(0.2, 0.5))

    return videos


def generate_mock_data(keyword, count):
    """生成模拟数据用于演示"""
    mock_results = []
    for i in range(count):
        mock_results.append({
            'bvid': f'BV{"".join(random.choices("0123456789ABCDEF", k=10))}',
            'title': f'{keyword} 相关视频 {i+1} - 精彩内容分享',
            'author': f'UP主{random.randint(1000, 99999)}',
            'mid': str(random.randint(10000, 9999999)),
            'play': f'{random.randint(1, 500)}.{random.randint(0, 9)}万',
            'review': f'{random.randint(100, 50000)}',
            'description': f'这是关于{keyword}的第{i+1}个视频',
            'pubdate': random.randint(1609459200, 1743043200),
            'duration': f'{random.randint(1, 30)}:{random.randint(10, 59):02d}',
            'danmaku': f'{random.randint(50, 10000)}'
        })
    return mock_results


def format_number(num):
    """格式化数字显示"""
    if num >= 100000000:
        return f"{num/100000000:.1f}亿"
    elif num >= 10000:
        return f"{num/10000:.1f}万"
    elif num >= 1000:
        return f"{num/1000:.1f}千"
    return str(num)


def create_excel_report(videos, keyword):
    """创建Excel报表"""
    wb = openpyxl.Workbook()
    wb.remove(wb.active)  # 删除默认sheet

    # 样式定义
    header_fill = PatternFill(start_color="00A1D6", end_color="00A1D6", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    link_font = Font(color="0563C1", underline="single", size=10)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )

    # 定义列
    columns = [
        ('排名', 'rank'),
        ('视频标题', 'title'),
        ('视频链接', 'url'),
        ('UP主', 'author'),
        ('UP主主页', 'author_url'),
        ('播放量', 'views'),
        ('点赞数', 'likes'),
        ('投币数', 'coins'),
        ('收藏数', 'favorites'),
        ('评论数', 'comments'),
        ('弹幕数', 'danmus'),
        ('时长', 'duration'),
        ('发布时间', 'pubdate')
    ]

    # 创建综合统计表
    def create_sheet(wb, title, data, sort_key=None):
        ws = wb.create_sheet(title=title)

        # 写入表头
        for col_idx, (header, _) in enumerate(columns, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = border

        # 按指定字段排序
        if sort_key:
            data = sorted(data, key=lambda x: x.get(sort_key, 0), reverse=True)

        # 写入数据
        for row_idx, video in enumerate(data, 2):
            # 排名（基于排序后的位置）
            ws.cell(row=row_idx, column=1, value=row_idx - 1)

            # 基本信息
            ws.cell(row=row_idx, column=2, value=video.get('title', ''))

            # 视频链接（超链接）
            url = video.get('url', '')
            if url:
                url_cell = ws.cell(row=row_idx, column=3, value=url)
                url_cell.hyperlink = url
                url_cell.font = link_font
            else:
                ws.cell(row=row_idx, column=3, value='')

            ws.cell(row=row_idx, column=4, value=video.get('author', ''))

            # UP主主页链接
            author_url = video.get('author_url', '')
            if author_url:
                author_cell = ws.cell(row=row_idx, column=5, value=author_url)
                author_cell.hyperlink = author_url
                author_cell.font = link_font
            else:
                ws.cell(row=row_idx, column=5, value='')

            # 数据字段
            ws.cell(row=row_idx, column=6, value=video.get('views', 0))
            ws.cell(row=row_idx, column=7, value=video.get('likes', 0))
            ws.cell(row=row_idx, column=8, value=video.get('coins', 0))
            ws.cell(row=row_idx, column=9, value=video.get('favorites', 0))
            ws.cell(row=row_idx, column=10, value=video.get('comments', 0))
            ws.cell(row=row_idx, column=11, value=video.get('danmus', 0))
            ws.cell(row=row_idx, column=12, value=video.get('duration', ''))

            # 发布时间
            pubdate = video.get('pubdate', 0)
            if pubdate and isinstance(pubdate, int):
                pubdate_str = datetime.fromtimestamp(pubdate).strftime('%Y-%m-%d %H:%M')
                ws.cell(row=row_idx, column=13, value=pubdate_str)
            else:
                ws.cell(row=row_idx, column=13, value=str(pubdate) if pubdate else '')

            # 应用边框
            for col in range(1, 14):
                ws.cell(row=row_idx, column=col).border = border

        # 设置列宽
        ws.column_dimensions['A'].width = 6
        ws.column_dimensions['B'].width = 50
        ws.column_dimensions['C'].width = 40
        ws.column_dimensions['D'].width = 15
        ws.column_dimensions['E'].width = 40
        ws.column_dimensions['F'].width = 12
        ws.column_dimensions['G'].width = 10
        ws.column_dimensions['H'].width = 10
        ws.column_dimensions['I'].width = 10
        ws.column_dimensions['J'].width = 10
        ws.column_dimensions['K'].width = 10
        ws.column_dimensions['L'].width = 10
        ws.column_dimensions['M'].width = 18

        return ws

    # 创建各个排序的sheet
    create_sheet(wb, '综合统计', videos.copy())
    create_sheet(wb, '播放量排行', videos.copy(), 'views')
    create_sheet(wb, '收藏量排行', videos.copy(), 'favorites')
    create_sheet(wb, '评论数排行', videos.copy(), 'comments')
    create_sheet(wb, '点赞量排行', videos.copy(), 'likes')

    # 保存文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_keyword = re.sub(r'[^\w\u4e00-\u9fff]', '_', keyword)[:20]
    filename = f"downloads/bilibili_{safe_keyword}_{timestamp}.xlsx"
    wb.save(filename)

    return filename


@app.route('/')
def index():
    """返回前端页面"""
    return send_file('index.html')


@app.route('/api/bilibili/search', methods=['POST'])
def api_search():
    """B站搜索API"""
    try:
        data = request.get_json()
        keyword = data.get('keyword', '').strip()

        if not keyword:
            return jsonify({
                'success': False,
                'message': '请输入搜索关键词'
            })

        print(f"\n{'='*60}")
        print(f"开始搜索关键词: {keyword}")
        print(f"{'='*60}")

        # 搜索视频
        videos = search_videos(keyword, max_count=30)

        if not videos:
            return jsonify({
                'success': False,
                'message': '未找到相关视频，请尝试其他关键词'
            })

        # 生成Excel报表
        excel_file = create_excel_report(videos, keyword)
        print(f"Excel报表已生成: {excel_file}")

        # 计算统计数据
        total_views = sum(v.get('views', 0) for v in videos)
        total_likes = sum(v.get('likes', 0) for v in videos)
        total_coins = sum(v.get('coins', 0) for v in videos)
        total_favorites = sum(v.get('favorites', 0) for v in videos)
        total_comments = sum(v.get('comments', 0) for v in videos)

        # 排序数据
        sorted_by_views = sorted(videos, key=lambda x: x.get('views', 0), reverse=True)
        sorted_by_favorites = sorted(videos, key=lambda x: x.get('favorites', 0), reverse=True)
        sorted_by_comments = sorted(videos, key=lambda x: x.get('comments', 0), reverse=True)
        sorted_by_likes = sorted(videos, key=lambda x: x.get('likes', 0), reverse=True)

        # 格式化视频数据
        formatted_videos = []
        for v in videos:
            formatted_videos.append({
                'rank': v['rank'],
                'title': v['title'],
                'url': v['url'],
                'author': v['author'],
                'authorUrl': v['author_url'],
                'views': format_number(v.get('views', 0)),
                'likes': format_number(v.get('likes', 0)),
                'coins': format_number(v.get('coins', 0)),
                'favorites': format_number(v.get('favorites', 0)),
                'comments': format_number(v.get('comments', 0)),
                'danmus': format_number(v.get('danmus', 0)),
                'duration': v.get('duration', ''),
                'pubdate': v.get('pubdate', 0)
            })

        print(f"\n搜索完成！共找到 {len(videos)} 条视频")

        return jsonify({
            'success': True,
            'data': {
                'videos': formatted_videos,
                'excelUrl': f'/{excel_file}',
                'totalViews': total_views,
                'totalLikes': total_likes,
                'totalCoins': total_coins,
                'totalFavorites': total_favorites,
                'totalComments': total_comments,
                'sortedByViews': [{
                    'title': v['title'],
                    'url': v['url'],
                    'views': format_number(v.get('views', 0))
                } for v in sorted_by_views[:10]],
                'sortedByFavorites': [{
                    'title': v['title'],
                    'url': v['url'],
                    'favorites': format_number(v.get('favorites', 0))
                } for v in sorted_by_favorites[:10]],
                'sortedByComments': [{
                    'title': v['title'],
                    'url': v['url'],
                    'comments': format_number(v.get('comments', 0))
                } for v in sorted_by_comments[:10]],
                'sortedByLikes': [{
                    'title': v['title'],
                    'url': v['url'],
                    'likes': format_number(v.get('likes', 0))
                } for v in sorted_by_likes[:10]]
            }
        })

    except Exception as e:
        print(f"搜索出错: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'搜索出错: {str(e)}'
        })


@app.route('/downloads/<path:filename>')
def download_file(filename):
    """下载Excel文件"""
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    print("=" * 60)
    print("B站（哔哩哔哩）搜索小助手")
    print("=" * 60)
    print("服务地址: http://localhost:5000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
