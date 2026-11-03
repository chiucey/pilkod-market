import sys
import re
from urllib.parse import urljoin

def extract_articles(html_content, base_url="https://www.ipeconomy.cn"):
    results = []
    
    # 1. 提取所有 a 标签及其内容
    # 匹配模式: <a ... href="URL" ...>TITLE</a>
    a_pattern = re.compile(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.DOTALL | re.IGNORECASE)
    matches = a_pattern.findall(html_content)

    for href, raw_title in matches:
        # 清理标题：去除 HTML 标签、换行符和多余空格
        title = re.sub(r'<[^>]+>', '', raw_title)
        title = re.sub(r'\s+', ' ', title).strip()
        
        if not href or href.startswith('javascript:') or href == '#' or len(href) < 5:
            continue
            
        # 2. 过滤逻辑：识别文章链接的特征
        # 包含数字 ID 或特定的路径模式
        is_article_path = any(kw in href for kw in ['dongtai', 'casereport', 'dianxing', 'view', 'article', 'p/'])
        has_id = re.search(r'\d{4,}', href) # 至少 4 位数字 ID
        
        if not (is_article_path or has_id):
            continue
            
        # 过滤掉非文章链接（如静态资源、外部链接等）
        if any(ext in href.lower() for ext in ['.css', '.js', '.png', '.jpg', '.pdf']):
            continue
            
        full_url = urljoin(base_url, href)
        
        # 过滤掉导航、分类等短文本链接
        if not title or len(title) < 6:
            continue
            
        # 3. 智能提取时间
        time_str = "未知时间"
        # 在 HTML 中查找该链接前后的文本（前后各 300 字符）
        link_index = html_content.find(href)
        if link_index != -1:
            context = html_content[max(0, link_index-100):link_index+400]
            # 匹配日期格式：YYYY-MM-DD 或 YYYY/MM/DD
            time_match = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2}(\s+\d{2}:\d{2})?)', context)
            if time_match:
                time_str = time_match.group(1)
        
        source_str = "知产财经"
            
        # 4. 去重并添加结果
        if not any(res['url'] == full_url for res in results):
            results.append({
                "url": full_url,
                "title": title,
                "time": time_str,
                "source": source_str
            })
    
    return results

if __name__ == "__main__":
    html_input = ""
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r', encoding='utf-8') as f:
                html_input = f.read()
        except Exception:
            html_input = sys.argv[1]
    
    if not html_input:
        try:
            with open('/home/ubuntu/ipeconomy_source_full.html', 'r', encoding='utf-8') as f:
                html_input = f.read()
        except FileNotFoundError:
            print("错误：未提供 HTML 输入且未找到缓存文件。")
            sys.exit(1)
            
    articles = extract_articles(html_input)
    for art in articles:
        print(f"链接地址：{art['url']} |标题名称：{art['title']} |发文时间：{art['time']} |来源于 {art['source']}")
