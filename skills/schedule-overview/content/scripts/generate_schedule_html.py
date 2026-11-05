#!/usr/bin/env python3
"""
日程快速一览表HTML生成器

根据用户输入的日程文字，生成包含搜索功能的交互式HTML表格页面。
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


def get_week_number(date: datetime) -> int:
    """
    计算给定日期在2026年的周数
    规则：2026年1月1日-1月4日为第1周，每周从周一开始
    """
    year_start = datetime(2026, 1, 1)
    days_diff = (date - year_start).days
    week_num = days_diff // 7 + 1
    return max(1, week_num)


def get_weekday_name(date: datetime) -> str:
    """获取星期几的中文名称"""
    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekday_names[date.weekday()]


def parse_time_to_24h(time_str: str) -> Optional[str]:
    """将各种时间格式转换为24小时制 HH:MM"""
    if not time_str:
        return None

    time_str = time_str.strip()

    # 格式: HH:MM
    match = re.match(r'(\d{1,2}):(\d{2})', time_str)
    if match:
        return f"{int(match.group(1)):02d}:{match.group(2)}"

    # 格式: HH点HH分 或 HH点 或 HH时HH分
    match = re.match(r'(\d{1,2})[点时](\d{1,2})?分?', time_str)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2)) if match.group(2) else 0
        return f"{hour:02d}:{minute:02d}"

    return None


def extract_time_range(text: str) -> tuple:
    """从文本中提取时间范围，返回 (开始时间, 结束时间)"""
    start_time = None
    end_time = None

    # 格式1: HH:MM-HH:MM 或 HH:MM~HH:MM
    match = re.search(r'(\d{1,2}):(\d{2})\s*[-~至]\s*(\d{1,2}):(\d{2})', text)
    if match:
        start_time = f"{int(match.group(1)):02d}:{match.group(2)}"
        end_time = f"{int(match.group(3)):02d}:{match.group(4)}"
        return start_time, end_time

    # 格式2: 上午9-12点、下午14-17点
    match = re.search(r'(上午|下午|早上|晚上)([\d零一二三四五六七八九十]+)\s*[-~至]\s*([\d零一二三四五六七八九十]+)[点时]?', text)
    if match:
        period = match.group(1)
        start_hour = chinese_to_number(match.group(2))
        end_hour = chinese_to_number(match.group(3))

        # 转换为24小时制
        if '下午' in period or '晚' in period:
            if start_hour < 12:
                start_hour += 12
            if end_hour < 12:
                end_hour += 12
        elif '上午' in period or '早' in period:
            if start_hour == 12:
                start_hour = 0
            if end_hour == 12:
                end_hour = 0

        start_time = f"{start_hour:02d}:00"
        end_time = f"{end_hour:02d}:00"
        return start_time, end_time

    # 格式3: 上午9点 或 下午2点
    match = re.search(r'(上午|下午|早上|晚上)?([\d零一二三四五六七八九十]+)[点时](?:(\d{1,2}))?', text)
    if match:
        period = match.group(1) or ''
        hour = chinese_to_number(match.group(2))
        minute = int(match.group(3)) if match.group(3) else 0

        if '下午' in period or '晚' in period:
            if hour < 12:
                hour += 12
        elif '上午' in period or '早' in period:
            if hour == 12:
                hour = 0

        start_time = f"{hour:02d}:{minute:02d}" if minute else f"{hour:02d}:00"
        return start_time, None

    # 格式4: 9-11点 或 9-11时
    match = re.search(r'(\d{1,2})\s*[-~至]\s*(\d{1,2})[点时]', text)
    if match:
        start_hour = int(match.group(1))
        end_hour = int(match.group(2))
        start_time = f"{start_hour:02d}:00"
        end_time = f"{end_hour:02d}:00"
        return start_time, end_time

    return None, None


def chinese_to_number(s: str) -> int:
    """将中文数字转换为整数"""
    mapping = {'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    try:
        return int(s) if s.isdigit() else mapping.get(s, 0)
    except:
        return 0


def parse_date(text: str) -> tuple:
    """从文本中提取日期，返回 (日期对象, 剩余文本)"""
    # 格式: 2026年6月25日 或 6月25日
    match = re.search(r'((?:2026)?年)?(\d{1,2})[月.](\d{1,2})(日?)', text)
    if match:
        year_str = match.group(1) or ''
        year = 2026 if not year_str else int(year_str.replace('年', ''))
        month = int(match.group(2))
        day = int(match.group(3))
        try:
            date_obj = datetime(year, month, day)
            remaining = text[:match.start()] + text[match.end():]
            return date_obj, remaining.strip()
        except ValueError:
            pass

    # 格式: 7.2 (简写)
    match = re.search(r'(\d{1,2})\.(\d{1,2})', text)
    if match:
        month = int(match.group(1))
        day = int(match.group(2))
        try:
            date_obj = datetime(2026, month, day)
            remaining = text[:match.start()] + text[match.end():]
            return date_obj, remaining.strip()
        except ValueError:
            pass

    return None, text


def parse_line(line: str) -> Optional[Dict]:
    """解析一行日程记录"""
    line = line.strip()
    if not line:
        return None

    result = {
        'date': None,
        'time_start': None,
        'time_end': None,
        'location': '未知',
        'subject': '未知',
        'participants': '未知',
        'is_training': False,
        'is_online': False
    }

    text = line

    # 检测线上培训
    if '线上' in text:
        result['is_online'] = True
        result['location'] = '线上'

    # 检测培训
    if '培训' in text:
        result['is_training'] = True

    # 提取日期
    date_obj, text = parse_date(text)
    if date_obj:
        result['date'] = date_obj

    # 提取时间
    start_time, end_time = extract_time_range(text)
    if start_time:
        result['time_start'] = start_time
        result['time_end'] = end_time
        # 移除已提取的时间
        time_patterns = [
            r'\d{1,2}:\d{2}\s*[-~至]\s*\d{1,2}:\d{2}',
            r'(?:上午|下午|早上|晚上)?[\d零一二三四五六七八九十]+\s*[-~至]\s*[\d零一二三四五六七八九十]+[点时]?',
            r'(?:上午|下午|早上|晚上)?[\d零一二三四五六七八九十]+[点时](?:\d{1,2})?',
            r'\d{1,2}\s*[-~至]\s*\d{1,2}[点时]'
        ]
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                text = text[:match.start()] + text[match.end():]
                break

    # 提取主题
    subject = None

    # 格式1: 培训主题：XXX
    match = re.search(r'培训[主题：:]\s*["""]?([^"""\n，,。]+)', text)
    if match:
        subject = match.group(1).strip().strip('""').strip()

    # 格式2: 主题：XXX
    if not subject:
        match = re.search(r'(?:培训)?主题[：:]\s*["""]?([^"""\n，,。]+)', text)
        if match:
            subject = match.group(1).strip().strip('""').strip()

    # 格式3: 活动名称（常见关键词）
    if not subject:
        activity_keywords = ['分享会', '宣讲', '活动', '例会', '学习', '开放日', '检索练习']
        for kw in activity_keywords:
            if kw in text:
                idx = text.find(kw)
                # 获取这个词周围的内容作为主题
                start = max(0, idx - 20)
                end = min(len(text), idx + len(kw) + 10)
                subject_candidate = text[start:end].strip()
                # 清理
                subject_candidate = re.sub(r'^[^\u4e00-\u9fa5]+', '', subject_candidate)
                subject_candidate = re.sub(r'[^\u4e00-\u9fa5]+$', '', subject_candidate)
                if subject_candidate:
                    subject = subject_candidate
                    break

    if subject:
        result['subject'] = subject

    # 提取地点
    location_patterns = [
        r'\d+#\S+',  # 2#307
        r'#\S+',  # #307
        r'[\S]*会议室[\S]*',
        r'[\S]*教室[\S]*',
        r'[\S]*会议中心[\S]*',
        r'[\S]*报告厅[\S]*',
        r'[\S]*活动室[\S]*',
        r'[\S]*阳光厅[\S]*',
        r'\d+号楼[\S]*',
    ]

    for pattern in location_patterns:
        match = re.search(pattern, text)
        if match:
            result['location'] = match.group(0)
            break

    # 提取参与人员
    participant_keywords = [
        '全体党员', '全体人员', '全体同事', '全体成员', '全体干部',
        '管理干部', '审查员', '党员同志', '青年同事', '参赛人员',
        '感兴趣人员', '已报名'
    ]
    for kw in participant_keywords:
        if kw in text:
            result['participants'] = kw
            break

    # 培训默认参与人员
    if result['is_training'] and result['participants'] == '未知':
        result['participants'] = '报名培训人员'

    # 添加培训前缀
    if result['is_training'] and result['subject'] != '未知' and not result['subject'].startswith('培训：'):
        result['subject'] = f"培训：{result['subject']}"

    return result


def parse_input_text(text: str) -> List[Dict]:
    """解析用户输入的整个文本"""
    lines = text.strip().split('\n')
    events = []

    for line in lines:
        parsed = parse_line(line)
        if parsed and parsed['date']:
            events.append(parsed)

    # 按日期和时间排序
    events.sort(key=lambda x: (x['date'], x['time_start'] or ''))
    return events


def generate_html(events: List[Dict], title: str = "日程一览表") -> str:
    """生成完整的HTML页面"""

    # 准备表格数据
    table_rows = []
    for event in events:
        week_num = get_week_number(event['date'])
        weekday = get_weekday_name(event['date'])
        date_str = event['date'].strftime('%Y-%m-%d')

        # 时间格式
        if event['time_start']:
            if event['time_end']:
                time_str = f"{event['time_start']}-{event['time_end']}"
            else:
                time_str = event['time_start']
        else:
            time_str = ""

        location = event['location']
        subject = event['subject']
        participants = event['participants']

        table_rows.append({
            'week': week_num,
            'date': date_str,
            'weekday': weekday,
            'time': time_str,
            'location': location,
            'subject': subject,
            'participants': participants
        })

    # 生成行rowspan信息
    week_rowspan = {}
    for i, row in enumerate(table_rows):
        week = row['week']
        if week not in week_rowspan:
            week_rowspan[week] = {'start': i, 'count': 0}
        week_rowspan[week]['count'] += 1

    # 构建HTML表格
    table_html = []
    processed_weeks = set()

    for i, row in enumerate(table_rows):
        week = row['week']
        is_odd_week = week % 2 == 1  # 奇数周白色，偶数周灰色
        bg_color = '#FFFFFF' if is_odd_week else '#E8E8E8'

        # 检查是否需要rowspan
        if week not in processed_weeks:
            rowspan_attr = f'rowspan="{week_rowspan[week]["count"]}"'
            processed_weeks.add(week)
        else:
            rowspan_attr = ''

        table_html.append(f'''
            <tr data-week="{week}">
                <td class="week-cell" {rowspan_attr} style="background-color: {bg_color};">
                    第{week}周
                </td>
                <td class="date-cell" style="background-color: {bg_color};">
                    {row['date']} ({row['weekday']})
                </td>
                <td class="time-cell" style="background-color: {bg_color};">
                    {row['time']}
                </td>
                <td class="location-cell" style="background-color: {bg_color};" data-search="{row['location']}">
                    {row['location']}
                </td>
                <td class="subject-cell" style="background-color: {bg_color};" data-search="{row['subject']}">
                    <strong>{row['subject']}</strong>
                </td>
                <td class="participants-cell" style="background-color: {bg_color};" data-search="{row['participants']}">
                    {row['participants']}
                </td>
            </tr>
        ''')

    table_content = ''.join(table_html)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: "Microsoft YaHei", "PingFang SC", -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 5px;
        }}

        .header p {{
            font-size: 14px;
            opacity: 0.9;
        }}

        .search-container {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}

        .search-box {{
            display: flex;
            gap: 10px;
            max-width: 600px;
            margin: 0 auto;
        }}

        .search-input {{
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
        }}

        .search-input:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .search-btn {{
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}

        .search-btn:hover {{
            background: #5a6fd6;
        }}

        .clear-btn {{
            padding: 12px 16px;
            background: #6c757d;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }}

        .clear-btn:hover {{
            background: #5a6268;
        }}

        .table-container {{
            padding: 20px 30px 30px;
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}

        th {{
            background: #f8f9fa;
            color: #495057;
            font-weight: 600;
            padding: 14px 12px;
            text-align: center;
            border-bottom: 2px solid #dee2e6;
        }}

        td {{
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #e9ecef;
            vertical-align: middle;
        }}

        .week-cell {{
            font-weight: 600;
            color: #495057;
            width: 80px;
        }}

        .date-cell {{
            color: #212529;
            width: 160px;
        }}

        .time-cell {{
            color: #212529;
            width: 120px;
        }}

        .location-cell {{
            color: #212529;
        }}

        .subject-cell strong {{
            color: #333;
        }}

        .participants-cell {{
            color: #495057;
        }}

        .highlight {{
            background-color: #fff3cd !important;
            transition: background-color 0.3s;
        }}

        .dimmed {{
            opacity: 0.4;
        }}

        tr:hover:not(.dimmed) {{
            background-color: #f1f3f5;
        }}

        .no-results {{
            text-align: center;
            padding: 40px;
            color: #6c757d;
            font-size: 16px;
            display: none;
        }}

        .stats {{
            padding: 10px 30px 20px;
            color: #6c757d;
            font-size: 13px;
            text-align: center;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}

            .header h1 {{
                font-size: 20px;
            }}

            th, td {{
                padding: 8px 6px;
                font-size: 12px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>2026年度日程安排</p>
        </div>

        <div class="search-container">
            <div class="search-box">
                <input type="text" id="searchInput" class="search-input" placeholder="输入关键词搜索...">
                <button onclick="performSearch()" class="search-btn">搜索</button>
                <button onclick="clearSearch()" class="clear-btn">清除</button>
            </div>
        </div>

        <div class="stats" id="stats"></div>

        <div class="table-container">
            <table id="scheduleTable">
                <thead>
                    <tr>
                        <th>自然周数</th>
                        <th>日期和星期</th>
                        <th>具体时间</th>
                        <th>地点</th>
                        <th>活动主题</th>
                        <th>参与人员</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                    {table_content}
                </tbody>
            </table>
            <div class="no-results" id="noResults">未找到匹配的结果</div>
        </div>
    </div>

    <script>
        function performSearch() {{
            const input = document.getElementById('searchInput');
            const keyword = input.value.trim().toLowerCase();

            if (!keyword) {{
                clearSearch();
                return;
            }}

            const rows = document.querySelectorAll('#tableBody tr');
            let matchCount = 0;

            rows.forEach(row => {{
                const cells = row.querySelectorAll('td');
                let rowMatches = false;

                cells.forEach(cell => {{
                    const text = cell.getAttribute('data-search') || cell.textContent;
                    if (text.toLowerCase().includes(keyword)) {{
                        rowMatches = true;
                        cell.classList.add('highlight');
                    }} else {{
                        cell.classList.remove('highlight');
                    }}
                }});

                if (rowMatches) {{
                    row.classList.remove('dimmed');
                    matchCount++;
                }} else {{
                    row.classList.add('dimmed');
                }}
            }});

            document.getElementById('stats').textContent =
                `找到 ${{matchCount}} 个匹配结果`;

            document.getElementById('noResults').style.display =
                matchCount === 0 ? 'block' : 'none';
        }}

        function clearSearch() {{
            document.getElementById('searchInput').value = '';

            const rows = document.querySelectorAll('#tableBody tr');
            rows.forEach(row => {{
                row.classList.remove('dimmed');
                const cells = row.querySelectorAll('td');
                cells.forEach(cell => {{
                    cell.classList.remove('highlight');
                }});
            }});

            document.getElementById('stats').textContent =
                `共 ${{rows.length}} 条日程记录`;
            document.getElementById('noResults').style.display = 'none';
        }}

        document.getElementById('searchInput').addEventListener('input', function(e) {{
            if (!e.target.value.trim()) {{
                clearSearch();
            }}
        }});

        document.getElementById('searchInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') {{
                performSearch();
            }}
        }});

        document.addEventListener('DOMContentLoaded', function() {{
            const rows = document.querySelectorAll('#tableBody tr');
            document.getElementById('stats').textContent =
                `共 ${{rows.length}} 条日程记录`;
        }});
    </script>
</body>
</html>'''

    return html


def save_html(html_content: str, output_path: str) -> str:
    """保存HTML文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return output_path


if __name__ == '__main__':
    # 测试示例
    test_input = """
6月10日 14:00-16:00 2#307 科室例会 全体科室成员参加
6月12日 9:00 3#201 青年培训 全体青年同事
6月15日 10:00-12:00 会议室A 党支部会议 所有党员
6月20日 线上培训 新人入职培训
    """

    events = parse_input_text(test_input)
    print(f"解析到 {len(events)} 个日程事件")

    for event in events:
        print(f"  - {event['date'].strftime('%Y-%m-%d')}: {event['subject']}")

    html = generate_html(events)
    output = save_html(html, '/workspace/dist/index.html')
    print(f"HTML已保存到: {output}")
