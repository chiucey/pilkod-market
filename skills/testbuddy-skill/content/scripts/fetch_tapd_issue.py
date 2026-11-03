#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAPD 需求获取脚本
通过 Web 接口抓包方式获取 TAPD 需求内容及关联需求

使用方式:
    python fetch_tapd_issue.py --issue-id <需求ID>
    python fetch_tapd_issue.py --issue-id <需求ID> --output markdown
    python fetch_tapd_issue.py --issue-id <需求ID> --save

配置文件: .testbuddy/env/session.json
    {
        "tapd": {
            "base_url": "https://www.tapd.cn",
            "cookie": "your_cookie_string",
            "workspace_id": "工作空间ID"
        }
    }
"""
import json
import os
import sys
import argparse
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from html.parser import HTMLParser

if sys.version_info[0] < 3:
    print("错误：此脚本需要 Python 3", file=sys.stderr)
    sys.exit(1)

SESSION_FILE = os.path.join(os.getcwd(), ".testbuddy/env/session.json")


class HTMLToMarkdown(HTMLParser):
    """简单的 HTML 转 Markdown 转换器"""
    
    def __init__(self):
        super().__init__()
        self.result = []
        self.list_stack = []
        self.skip_tags = {'style', 'script', 'head', 'meta', 'link'}
        self.current_skip = False
    
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = dict(attrs)
        
        if tag in self.skip_tags:
            self.current_skip = True
            return
        
        if self.current_skip:
            return
        
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            level = int(tag[1])
            self.result.append('\n' + '#' * level + ' ')
        elif tag == 'p':
            self.result.append('\n\n')
        elif tag == 'br':
            self.result.append('\n')
        elif tag == 'hr':
            self.result.append('\n---\n')
        elif tag == 'strong' or tag == 'b':
            self.result.append('**')
        elif tag == 'em' or tag == 'i':
            self.result.append('*')
        elif tag == 'code':
            self.result.append('`')
        elif tag == 'pre':
            self.result.append('\n```\n')
        elif tag == 'blockquote':
            self.result.append('\n> ')
        elif tag == 'a':
            href = attrs_dict.get('href', '')
            self.result.append(f'[')
            self.link_href = href
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            alt = attrs_dict.get('alt', attrs_dict.get('title', '图片'))
            self.result.append(f'![{alt}]({src})')
        elif tag == 'ul':
            self.list_stack.append('ul')
            self.result.append('\n')
        elif tag == 'ol':
            self.list_stack.append(('ol', 1))
            self.result.append('\n')
        elif tag == 'li':
            if self.list_stack:
                last = self.list_stack[-1]
                if last == 'ul':
                    self.result.append('- ')
                elif isinstance(last, tuple) and last[0] == 'ol':
                    num = last[1]
                    self.result.append(f'{num}. ')
                    self.list_stack[-1] = ('ol', num + 1)
        elif tag == 'table':
            self.result.append('\n')
        elif tag == 'tr':
            self.result.append('|')
        elif tag == 'th' or tag == 'td':
            self.result.append(' ')
        elif tag == 'span':
            pass
    
    def handle_endtag(self, tag):
        tag = tag.lower()
        
        if tag in self.skip_tags:
            self.current_skip = False
            return
        
        if self.current_skip:
            return
        
        if tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            self.result.append('\n')
        elif tag == 'p':
            self.result.append('\n')
        elif tag == 'strong' or tag == 'b':
            self.result.append('**')
        elif tag == 'em' or tag == 'i':
            self.result.append('*')
        elif tag == 'code':
            self.result.append('`')
        elif tag == 'pre':
            self.result.append('\n```\n')
        elif tag == 'a':
            self.result.append(f']({getattr(self, "link_href", "")})')
        elif tag == 'ul':
            if self.list_stack and self.list_stack[-1] == 'ul':
                self.list_stack.pop()
            self.result.append('\n')
        elif tag == 'ol':
            if self.list_stack:
                self.list_stack.pop()
            self.result.append('\n')
        elif tag == 'li':
            self.result.append('\n')
        elif tag == 'th' or tag == 'td':
            self.result.append(' |')
        elif tag == 'tr':
            self.result.append('\n')
    
    def handle_data(self, data):
        if self.current_skip:
            return
        text = data.replace('\n', ' ').replace('\r', '')
        text = re.sub(r'\s+', ' ', text)
        self.result.append(text)
    
    def get_markdown(self):
        md = ''.join(self.result)
        md = re.sub(r'\n{3,}', '\n\n', md)
        md = re.sub(r'^\s+', '', md, flags=re.MULTILINE)
        return md.strip()


def html_to_markdown(html_content):
    """将 HTML 内容转换为 Markdown"""
    if not html_content:
        return ''
    
    try:
        parser = HTMLToMarkdown()
        parser.feed(html_content)
        return parser.get_markdown()
    except Exception as e:
        return html_content


def load_config():
    """加载配置"""
    if not os.path.exists(SESSION_FILE):
        return None
    
    with open(SESSION_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('tapd', {})


def make_request(url, cookie, data=None, method='GET'):
    """发送 HTTP 请求"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': cookie,
        'Referer': 'https://www.tapd.cn/',
        'Origin': 'https://www.tapd.cn',
    }
    
    if data and method == 'POST':
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        data = urlencode(data).encode('utf-8')
    
    request = Request(url, data=data, headers=headers, method=method)
    
    try:
        with urlopen(request, timeout=30) as response:
            content_type = response.headers.get('Content-Type', '')
            body = response.read().decode('utf-8')
            
            if 'application/json' in content_type or body.startswith('{') or body.startswith('['):
                return json.loads(body)
            else:
                return {'raw_response': body, 'content_type': content_type}
                
    except HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else ''
        return {'error': f'HTTP Error: {e.code}', 'message': error_body[:500]}
    except URLError as e:
        return {'error': f'URL Error: {e.reason}', 'message': str(e)}
    except json.JSONDecodeError as e:
        return {'error': 'JSON Decode Error', 'message': str(e), 'raw': body[:500] if 'body' in dir() else ''}


def extract_dsc_token(cookie):
    """从 cookie 中提取 dsc_token"""
    match = re.search(r'dsc-token=([^;]+)', cookie)
    if match:
        return match.group(1)
    return ''


def fetch_issue_by_aggregation(base_url, cookie, workspace_id, issue_id, entity_type='story'):
    """
    获取需求详情 - 使用聚合接口
    
    接口: /api/aggregation/workitem_aggregation/get_info
    请求方式: POST (application/x-www-form-urlencoded)
    """
    url = f"{base_url}/api/aggregation/workitem_aggregation/get_info"
    
    dsc_token = extract_dsc_token(cookie)
    
    data = {
        'workspace_id': workspace_id,
        'entity_id': issue_id,
        'entity_type': entity_type,
        'api_controller_prefix': '',
        'enable_description': 'true',
        'is_detail': 1,
        'blacklist_fields': '[]',
        'identifier': 'app_for_editor,app_for_obj_more,app_for_obj_dialog_dropdown,app_for_obj_detail_panel,app_for_obj_detail_bottom_card,app_for_obj_attachment,app_for_obj_copy_link,app_for_obj_additional_panel',
        'installed_app_entity': json.dumps({
            'obj_id': issue_id,
            'obj_type': entity_type,
            'obj_name': '需求' if entity_type == 'story' else '缺陷'
        }, ensure_ascii=False),
        'has_edit_rule_fields': '[]',
        'is_archived': 0,
        'is_assistant_exec_log': 1,
        'app_id': '',
        'dsc_token': dsc_token,
    }
    
    result = make_request(url, cookie, data=data, method='POST')
    
    if 'error' in result:
        return result
    
    if result.get('meta', {}).get('code') and result['meta']['code'] != '0':
        return {'error': result['meta'].get('message', 'Unknown error'), 'code': result['meta']['code']}
    
    return parse_aggregation_response(result, issue_id)


def parse_aggregation_response(response, issue_id):
    """解析聚合接口响应"""
    if not response or 'error' in response:
        return response
    
    data = response.get('data', {})
    
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return {'error': 'Failed to parse data field', 'raw': data[:500]}
    
    if not data:
        return {'error': 'No data in response', 'raw': response}
    
    workitem_data = data.get('get_workitem_basic_info_ret', {}).get('data', {})
    
    if not workitem_data:
        workitem_data = data.get('workitem', data)
    
    if isinstance(workitem_data, list) and len(workitem_data) > 0:
        workitem_data = workitem_data[0]
    
    issue_type = workitem_data.get('entity_type', workitem_data.get('type', 'story'))
    
    issue_info = {
        'id': issue_id,
        'name': workitem_data.get('name', workitem_data.get('title', '')),
        'description': html_to_markdown(workitem_data.get('description', workitem_data.get('content', ''))),
        'status': workitem_data.get('status', workitem_data.get('status_name', '')),
        'priority': workitem_data.get('priority', workitem_data.get('priority_name', '')),
        'category': workitem_data.get('category', workitem_data.get('story_type', workitem_data.get('workitem_type_name', ''))),
        'creator': workitem_data.get('creator', workitem_data.get('created_by', '')),
        'owner': workitem_data.get('owner', workitem_data.get('owned_by', '')),
        'created': workitem_data.get('created', workitem_data.get('created_time', '')),
        'modified': workitem_data.get('modified', workitem_data.get('modified_time', '')),
        'workspace_id': workitem_data.get('workspace_id', ''),
        'workspace_name': workitem_data.get('workspace_name', ''),
        'type': issue_type,
        'raw_data': workitem_data
    }
    
    if issue_type == 'bug':
        issue_info['severity'] = workitem_data.get('severity', workitem_data.get('severity_name', ''))
    
    return issue_info


def fetch_issue_detail(base_url, cookie, workspace_id, issue_id):
    """获取需求详情 - 尝试多个接口"""
    result = fetch_issue_by_aggregation(base_url, cookie, workspace_id, issue_id, entity_type='story')
    
    if 'error' not in result:
        return result
    
    url = f"{base_url}/stories/view_story_data"
    params = {
        'id': issue_id,
        'workspace_id': workspace_id,
    }
    result = make_request(f"{url}?{urlencode(params)}", cookie)
    
    if 'error' in result:
        return result
    
    return parse_issue_response(result, issue_id)


def parse_issue_response(response, issue_id):
    """解析需求响应"""
    if not response or 'error' in response:
        return response
    
    data = response.get('data', response)
    
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
    
    issue_info = {
        'id': issue_id,
        'name': data.get('name', data.get('title', '')),
        'description': data.get('description', data.get('content', '')),
        'status': data.get('status', ''),
        'priority': data.get('priority', ''),
        'category': data.get('category', data.get('story_type', '')),
        'creator': data.get('creator', ''),
        'owner': data.get('owner', ''),
        'created': data.get('created', ''),
        'modified': data.get('modified', ''),
        'workspace_id': data.get('workspace_id', ''),
        'type': 'story',
        'raw_data': data
    }
    
    return issue_info


def fetch_bug_detail(base_url, cookie, workspace_id, bug_id):
    """获取缺陷详情"""
    result = fetch_issue_by_aggregation(base_url, cookie, workspace_id, bug_id, entity_type='bug')
    
    if 'error' not in result:
        return result
    
    url = f"{base_url}/bugs/view_bug_data"
    params = {
        'id': bug_id,
        'workspace_id': workspace_id,
    }
    result = make_request(f"{url}?{urlencode(params)}", cookie)
    
    if 'error' in result:
        return result
    
    data = result.get('data', result)
    
    if isinstance(data, list) and len(data) > 0:
        data = data[0]
    
    bug_info = {
        'id': bug_id,
        'name': data.get('title', ''),
        'description': html_to_markdown(data.get('description', '')),
        'status': data.get('status', ''),
        'priority': data.get('priority', ''),
        'severity': data.get('severity', ''),
        'creator': data.get('reporter', data.get('creator', '')),
        'owner': data.get('owner', ''),
        'created': data.get('created', ''),
        'modified': data.get('modified', ''),
        'workspace_id': data.get('workspace_id', ''),
        'type': 'bug',
        'raw_data': data
    }
    
    return bug_info


def detect_issue_type(issue_id):
    """检测需求类型：story 或 bug"""
    issue_id_upper = str(issue_id).upper()
    if issue_id_upper.startswith('BUG') or issue_id_upper.startswith('BUG-'):
        return 'bug'
    if re.match(r'^\d{10,}$', issue_id):
        return 'story'
    return 'story'


def format_output(issue):
    """格式化输出"""
    return {'issue': issue}


def format_as_markdown(data):
    """格式化为 Markdown"""
    issue = data.get('issue', {})
    linked = issue.get('linked_issues', [])
    
    lines = [
        f"# {issue.get('name', '需求详情')}",
        "",
        f"**ID**: {issue.get('id', '')}",
        f"**类型**: {issue.get('type', 'story')}",
        f"**状态**: {issue.get('status', '')}",
        f"**优先级**: {issue.get('priority', '')}",
    ]
    
    if issue.get('severity'):
        lines.append(f"**严重程度**: {issue.get('severity')}")
    
    lines.extend([
        f"**创建人**: {issue.get('creator', '')}",
        f"**负责人**: {issue.get('owner', '')}",
        f"**创建时间**: {issue.get('created', '')}",
        "",
        "## 描述",
        "",
        issue.get('description', '无描述') or '无描述',
        "",
    ])
    
    if linked:
        lines.extend([
            "## 关联需求",
            "",
        ])
        for item in linked:
            lines.append(f"- [{item.get('id', '')}] {item.get('name', '')} ({item.get('type', 'related')})")
        lines.append("")
    
    return '\n'.join(lines)


def fetch_linked_issues(base_url, cookie, workspace_id, issue_id, issue_type='story'):
    """
    获取关联需求
    """
    url = f"{base_url}/api/aggregation/workitem_aggregation/get_related_workitems"
    
    dsc_token = extract_dsc_token(cookie)
    
    data = {
        'workspace_id': workspace_id,
        'entity_id': issue_id,
        'entity_type': issue_type,
        'page': 1,
        'limit': 50,
        'dsc_token': dsc_token,
    }
    
    result = make_request(url, cookie, data=data, method='POST')
    
    if 'error' in result:
        return []
    
    linked_issues = []
    data = result.get('data', {})
    
    if data is None:
        return []
    
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return []
    
    if not isinstance(data, dict):
        return []
    
    related_items = data.get('related_workitems', {}).get('data', [])
    
    for item in related_items:
        linked_issue = {
            'id': item.get('id', ''),
            'name': item.get('name', item.get('title', '')),
            'type': item.get('entity_type', item.get('type', 'related')),
            'status': item.get('status', item.get('status_name', ''))
        }
        if linked_issue['id']:
            linked_issues.append(linked_issue)
    
    return linked_issues

def main():
    parser = argparse.ArgumentParser(description='从 TAPD 获取需求内容')
    parser.add_argument('--issue-id', required=True, help='需求ID，如: 1123456789001 或 BUG001')
    parser.add_argument('--output', choices=['json', 'markdown'], default='json', help='输出格式')
    parser.add_argument('--save', action='store_true', help='是否保存到文件')
    parser.add_argument('--debug', action='store_true', help='显示原始响应')
    parser.add_argument('--with-linked', action='store_true', help='是否获取关联需求')
    
    args = parser.parse_args()
    
    config = load_config()
    if not config:
        print(json.dumps({
            'error': '配置未找到',
            'message': f'请在 {SESSION_FILE} 中配置 tapd 参数',
            'config_example': {
                'tapd': {
                    'base_url': 'https://www.tapd.cn',
                    'cookie': 'your_cookie_string',
                    'workspace_id': 'your_workspace_id'
                }
            }
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    base_url = config.get('base_url', 'https://www.tapd.cn')
    cookie = config.get('cookie', '')
    workspace_id = config.get('workspace_id', '')
    
    if not cookie:
        print(json.dumps({
            'error': 'Cookie 未配置',
            'message': '请在 session.json 的 tapd.cookie 中配置',
            'hint': '通过浏览器开发者工具抓包获取 Cookie'
        }, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    issue_type = detect_issue_type(args.issue_id)
    
    if issue_type == 'bug':
        issue = fetch_bug_detail(base_url, cookie, workspace_id, args.issue_id)
    else:
        issue = fetch_issue_detail(base_url, cookie, workspace_id, args.issue_id)
    
    if 'error' in issue:
        print(json.dumps(issue, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    # 获取关联需求
    if args.with_linked:
        linked_issues = fetch_linked_issues(base_url, cookie, workspace_id, args.issue_id, issue_type)
        issue['linked_issues'] = linked_issues
    
    result = format_output(issue)
    
    if args.debug:
        print("--- Raw Data ---", file=sys.stderr)
        print(json.dumps(issue.get('raw_data', {}), ensure_ascii=False, indent=2), file=sys.stderr)
        print("--- End Raw Data ---", file=sys.stderr)
    
    if args.output == 'markdown':
        output_content = format_as_markdown(result)
    else:
        output_content = json.dumps(result, ensure_ascii=False, indent=2)
    
    print(output_content)
    
    if args.save:
        output_dir = os.path.join(os.getcwd(), '.testbuddy/md')
        os.makedirs(output_dir, exist_ok=True)
        
        issue_id = issue.get('id', args.issue_id)
        issue_kind = issue.get('type', 'STORY').upper()
        output_file = os.path.join(output_dir, f'{issue_kind}-{issue_id}.md')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(format_as_markdown(result))
        
        print(f"\n---\n已保存到: {output_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
