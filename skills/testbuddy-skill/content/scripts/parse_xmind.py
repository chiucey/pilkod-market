#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XMind 文件解析脚本
将 XMind 文件转换为测试节点 JSON 格式，保持内容完整

支持的 XMind 元素：
1. 主题和子主题
2. 备注
3. 标签
4. 图片
5. 链接
6. 优先级标记
7. 进度标记

使用方式:
    python parse_xmind.py <xmind_file>
    python parse_xmind.py <xmind_file> --output json
    python parse_xmind.py <xmind_file> --output yaml
"""
import json
import sys
import os
import argparse
import zipfile
import xml.etree.ElementTree as ET
from io import BytesIO

if sys.version_info[0] < 3:
    print("错误：此脚本需要 Python 3", file=sys.stderr)
    sys.exit(1)


def generate_uid(kind):
    """生成节点的唯一ID"""
    import random
    import string
    chars = string.ascii_letters + string.digits
    random_str = ''.join(random.choice(chars) for _ in range(10))
    return "{}-{}".format(kind.lower().replace('_', '-'), random_str)


def parse_xmind_content(xml_content):
    """解析 XMind 的 content.xml"""
    try:
        root = ET.fromstring(xml_content)
        return root
    except Exception as e:
        return None


def extract_text(element):
    """提取元素的文本内容"""
    if element is None:
        return ""
    
    text_parts = []
    if element.text:
        text_parts.append(element.text)
    
    for child in element:
        child_text = extract_text(child)
        if child_text:
            text_parts.append(child_text)
        if child.tail:
            text_parts.append(child.tail)
    
    return ''.join(text_parts).strip()


def get_topic_children(topic, tag_name):
    """获取主题的指定类型子元素"""
    children = []
    for child in topic:
        if child.tag.endswith(tag_name):
            children.append(child)
    return children


def parse_topic(topic, parent_uid=None, level=0):
    """
    解析单个主题，递归解析子主题
    保持内容完整，包括备注、标签、图片等
    """
    node = {}
    
    ns = {'x': 'urn:xmind:xmap:xmlns:content:2.0'}
    
    topic_id = topic.get('id', '')
    if not topic_id:
        topic_id = generate_uid('topic')
    
    title_elem = topic.find('.//x:title', ns)
    if title_elem is None:
        for child in topic:
            if 'title' in child.tag:
                title_elem = child
                break
    
    title = extract_text(title_elem) if title_elem is not None else "未命名主题"
    
    node['uid'] = topic_id
    node['name'] = title
    node['parent_uid'] = parent_uid
    node['kind'] = 'FEATURE'
    node['description'] = ''
    node['instance'] = None
    
    extra_info = {}
    
    notes_elem = topic.find('.//x:notes', ns)
    if notes_elem is None:
        for child in topic:
            if 'notes' in child.tag:
                notes_elem = child
                break
    
    if notes_elem is not None:
        note_text = extract_text(notes_elem)
        if note_text:
            extra_info['notes'] = note_text
            node['description'] = note_text
    
    labels = []
    labels_elem = topic.find('.//x:labels', ns)
    if labels_elem is None:
        for child in topic:
            if 'labels' in child.tag:
                labels_elem = child
                break
    
    if labels_elem is not None:
        for label_elem in labels_elem:
            label_text = extract_text(label_elem)
            if label_text:
                labels.append(label_text)
    
    if labels:
        extra_info['labels'] = labels
    
    marker_refs = topic.find('.//x:marker-refs', ns)
    if marker_refs is None:
        for child in topic:
            if 'marker-refs' in child.tag:
                marker_refs = child
                break
    
    if marker_refs is not None:
        markers = []
        for marker_ref in marker_refs:
            marker_id = marker_ref.get('marker-id', '')
            if marker_id:
                markers.append(marker_id)
                if marker_id.startswith('priority-'):
                    extra_info['priority'] = marker_id.replace('priority-', '')
                elif marker_id.startswith('task-start'):
                    extra_info['progress'] = 'started'
                elif marker_id.startswith('task-oct'):
                    extra_info['progress'] = 'oct'
                elif marker_id.startswith('task-quarter'):
                    extra_info['progress'] = 'quarter'
                elif marker_id.startswith('task-3quar'):
                    extra_info['progress'] = '3quar'
                elif marker_id.startswith('task-done'):
                    extra_info['progress'] = 'done'
        
        if markers:
            extra_info['markers'] = markers
    
    href = topic.get('href', '')
    if href:
        extra_info['link'] = href
    
    image_elem = topic.find('.//x:image', ns)
    if image_elem is None:
        for child in topic:
            if 'image' in child.tag:
                image_elem = child
                break
    
    if image_elem is not None:
        image_src = image_elem.get('src', '')
        if image_src:
            extra_info['image'] = image_src
    
    if extra_info:
        node['extra'] = extra_info
    
    nodes = [node]
    
    children_topic = topic.find('.//x:children', ns)
    if children_topic is None:
        for child in topic:
            if 'children' in child.tag:
                children_topic = child
                break
    
    if children_topic is not None:
        topics_elem = children_topic.find('.//x:topics', ns)
        if topics_elem is None:
            for child in children_topic:
                if 'topics' in child.tag:
                    topics_elem = child
                    break
        
        if topics_elem is not None:
            child_topics = []
            for child_topic in topics_elem:
                if 'topic' in child_topic.tag:
                    child_topics.append(child_topic)
            
            for child_topic in child_topics:
                child_nodes = parse_topic(child_topic, topic_id, level + 1)
                nodes.extend(child_nodes)
    
    return nodes


def parse_xmind_json(json_content):
    """解析 XMind 的 content.json（新版格式）"""
    try:
        data = json.loads(json_content)
        return data
    except Exception as e:
        return None


def parse_json_topic(topic, parent_name=None, level=0):
    """
    解析 JSON 格式的主题，递归解析子主题
    提取全量字段作为参考
    """
    node = {}
    
    title = topic.get('title', '未命名主题')
    node['name'] = title
    node['parent'] = parent_name
    node['level'] = level
    
    for key, value in topic.items():
        if key in ['id', 'title', 'children', 'parent']:
            continue
        
        if key == 'notes':
            if value and 'plain' in value:
                note_text = value['plain'].get('content', '')
                if note_text:
                    node['notes'] = note_text
        elif key == 'markers':
            if value:
                for marker in value:
                    marker_id = marker.get('markerId', '')
                    if marker_id:
                        if marker_id.startswith('priority-'):
                            node['priority'] = marker_id.replace('priority-', '')
                        elif marker_id.startswith('task-'):
                            node['progress'] = marker_id.replace('task-', '')
                        else:
                            if 'markers' not in node:
                                node['markers'] = []
                            node['markers'].append(marker_id)
        elif key == 'image':
            if value and 'src' in value:
                node['image'] = value['src']
        elif key == 'labels':
            if value:
                node['labels'] = value
        elif key == 'href':
            if value:
                node['link'] = value
        else:
            if value is not None and value != '' and value != [] and value != {}:
                node[key] = value
    
    nodes = [node]
    
    children = topic.get('children', {})
    attached = children.get('attached', [])
    
    for child_topic in attached:
        child_nodes = parse_json_topic(child_topic, title, level + 1)
        nodes.extend(child_nodes)
    
    return nodes


def parse_xmind_file(file_path):
    """解析 XMind 文件"""
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            file_list = zf.namelist()
            
            nodes = []
            
            if 'content.json' in file_list:
                json_content = zf.read('content.json')
                data = parse_xmind_json(json_content)
                
                if data is None:
                    return None, "XMind content.json 解析失败"
                
                if isinstance(data, list):
                    for sheet in data:
                        root_topic = sheet.get('rootTopic', {})
                        if root_topic:
                            sheet_nodes = parse_json_topic(root_topic, None, 0)
                            nodes.extend(sheet_nodes)
                elif isinstance(data, dict):
                    root_topic = data.get('rootTopic', {})
                    if root_topic:
                        sheet_nodes = parse_json_topic(root_topic, None, 0)
                        nodes.extend(sheet_nodes)
                
                if nodes:
                    return nodes, None
            
            if 'content.xml' in file_list:
                xml_content = zf.read('content.xml')
                root = parse_xmind_content(xml_content)
                
                if root is None:
                    return None, "XMind content.xml 解析失败"
                
                ns = {'x': 'urn:xmind:xmap:xmlns:content:2.0'}
                
                sheet_elems = root.findall('.//x:sheet', ns)
                if not sheet_elems:
                    sheet_elems = []
                    for elem in root.iter():
                        if 'sheet' in elem.tag:
                            sheet_elems.append(elem)
                
                if not sheet_elems:
                    sheet_elems = [root]
                
                for sheet_elem in sheet_elems:
                    topic_elem = sheet_elem.find('.//x:topic', ns)
                    if topic_elem is None:
                        for elem in sheet_elem.iter():
                            if 'topic' in elem.tag:
                                topic_elem = elem
                                break
                    
                    if topic_elem is not None:
                        sheet_nodes = parse_topic(topic_elem, None, 0)
                        nodes.extend(sheet_nodes)
                
                if nodes:
                    return nodes, None
            
            return None, "XMind 文件中未找到 content.json 或 content.xml"
            
    except zipfile.BadZipFile:
        return None, "无效的 XMind 文件格式"
    except Exception as e:
        return None, "XMind 解析失败: {}".format(str(e))


def convert_to_test_nodes(xmind_nodes):
    """
    将 XMind 节点转换为测试节点格式
    直接返回全量字段，作为参考分析
    """
    return xmind_nodes


def main():
    parser = argparse.ArgumentParser(description='解析 XMind 文件为测试节点格式')
    parser.add_argument('xmind_file', help='XMind 文件路径')
    parser.add_argument('--output', choices=['json', 'yaml'], default='json', help='输出格式')
    parser.add_argument('--keep-extra', action='store_true', help='保留所有额外信息')
    parser.add_argument('--output-file', help='输出文件路径（可选）')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.xmind_file):
        error_msg = json.dumps({
            'status': 'error',
            'msg': '文件不存在: {}'.format(args.xmind_file)
        }, ensure_ascii=False, indent=2)
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(error_msg)
        else:
            print(error_msg)
        sys.exit(1)
    
    nodes, error = parse_xmind_file(args.xmind_file)
    
    if error:
        error_msg = json.dumps({
            'status': 'error',
            'msg': error
        }, ensure_ascii=False, indent=2)
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(error_msg)
        else:
            print(error_msg)
        sys.exit(1)
    
    if args.keep_extra:
        output_nodes = nodes
    else:
        output_nodes = convert_to_test_nodes(nodes)
    
    if args.output == 'yaml':
        try:
            import yaml
            output_str = yaml.dump(output_nodes, allow_unicode=True, default_flow_style=False)
        except ImportError:
            output_str = json.dumps(output_nodes, ensure_ascii=False, indent=2)
    else:
        output_str = json.dumps(output_nodes, ensure_ascii=False, indent=2)
    
    if args.output_file:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            f.write(output_str)
    else:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        print(output_str)


if __name__ == "__main__":
    main()
