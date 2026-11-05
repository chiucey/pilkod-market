#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多班级考试成绩对比分析报告生成器

输出：自包含的对比分析 HTML（支持 2 个及以上班级，自动扫描 N 班级）

用法：
  python compare_classes.py
  python compare_classes.py --input-dir "F:\成绩分析"
  python compare_classes.py --input-dir "F:\成绩分析" --output "对比报告.html"

分析维度（共6章）：
  一、整体总体对比  — 分组柱状图（平均分及通过率指标）
  二、单科维度对比  — 分组柱状图 + 雷达图
  三、分数段梯队对比 — 频数直方图
  四、学情结构分析  — 环形图
  五、成绩问题溯源  — 文本分析（优势/短板/共性问题/个性问题）
  六、教学改进建议  — 分班级分层次培优补差方案
  七、跨月趋势分析  — 折线图
"""

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from datetime import datetime


def _ensure_deps():
    """检查并自动安装依赖（pandas, openpyxl）"""
    try:
        import pandas  # noqa
    except ImportError:
        import subprocess
        print("正在安装依赖 pandas 和 openpyxl...")
        r = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'pandas', 'openpyxl'],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            print("=" * 50)
            print("依赖安装失败！请手动执行：")
            print("  pip install pandas openpyxl")
            print("错误信息：")
            print(r.stderr)
            print("=" * 50)
            sys.exit(1)
        print("依赖安装成功。")


_ensure_deps()
import pandas as pd


# ════════════════════════════════════════════════════════════
#  颜色方案（最多支持 10 个班级）
# ════════════════════════════════════════════════════════════

CLASS_COLORS = ['#2196f3', '#ff5722', '#4caf50', '#9c27b0', '#ff9800',
                '#00bcd4', '#e91e63', '#607d8b', '#795548', '#3f51b5']

def get_class_color(idx):
    return CLASS_COLORS[idx % len(CLASS_COLORS)]

def get_class_rgba(idx, alpha=0.1):
    c = get_class_color(idx)
    r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
    return f'rgba({r},{g},{b},{alpha})'


# ════════════════════════════════════════════════════════════
#  CSS 样式（动态 class 在 main() 中补充）
# ════════════════════════════════════════════════════════════

CSS = '''
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: "Microsoft YaHei","PingFang SC",sans-serif; background: #f0f2f5; color: #333; }
.navbar { display: flex; align-items: center; height: 52px; background: #1a1a2e; color: #fff; padding: 0 16px; position: fixed; top: 0; left: 0; right: 0; z-index: 9999; }
.navbar-title { font-size: 16px; font-weight: 600; margin-right: 16px; color: #4fc3f7; white-space: nowrap; }
.navbar-tabs { display: flex; gap: 2px; flex: 1; overflow-x: auto; height: 100%; align-items: stretch; }
.nav-item { display: flex; align-items: center; gap: 5px; padding: 0 14px; cursor: pointer; font-size: 12px; color: #aaa; border-bottom: 3px solid transparent; transition: all .2s; white-space: nowrap; }
.nav-item:hover { background: rgba(255,255,255,.08); color: #fff; }
.nav-item.active { background: rgba(255,255,255,.12); color: #fff; border-bottom-color: #4fc3f7; }
.nav-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.main-container { margin-top: 52px; }
.tab-content { display: none; }
.tab-content.active { display: block; }
.main-comp { padding: 20px; max-width: 1100px; margin: 0 auto; }

/* ── 内页侧边栏布局（每月对比） ── */
.comp-layout { display: flex; min-height: calc(100vh - 52px); }
.inner-sidebar { width: 170px; background: #f8f9fa; border-right: 1px solid #e0e0e0; flex-shrink: 0; padding: 16px 0; position: sticky; top: 52px; height: calc(100vh - 52px); overflow-y: auto; }
.inner-sidebar-title { font-size: 11px; color: #888; font-weight: 600; letter-spacing: 1px; padding: 0 16px 10px; text-transform: uppercase; }
.inner-nav-item { display: block; padding: 8px 16px; font-size: 12.5px; color: #555; text-decoration: none; border-left: 3px solid transparent; transition: all .2s; cursor: pointer; }
.inner-nav-item:hover { background: #e8f4fc; color: #1a1a2e; }
.inner-nav-item.active { background: #e3f2fd; border-left-color: #4fc3f7; color: #1565c0; font-weight: 500; }
.comp-main { flex: 1; overflow-y: auto; padding: 20px; max-width: 1000px; }

/* ── 章节卡片 ── */
.comp-section { background: #fff; border-radius: 10px; padding: 25px; margin-bottom: 22px; box-shadow: 0 2px 8px rgba(0,0,0,.07); scroll-margin-top: 65px; }
.comp-section h2 { font-size: 19px; color: #1a1a2e; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 3px solid #4fc3f7; display: flex; align-items: center; gap: 8px; }
.section-number { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; background: #1a1a2e; color: #fff; border-radius: 50%; font-size: 14px; font-weight: 600; flex-shrink: 0; }

/* ── 图表 ── */
.chart-container { max-width: 800px; margin: 18px auto; position: relative; height: 360px; }
.chart-row { display: flex; gap: 16px; flex-wrap: wrap; }
.chart-row .chart-container { flex: 1; min-width: 300px; height: 360px; }
.chart-label { text-align: center; font-size: 12px; color: #888; margin-top: -8px; margin-bottom: 12px; }

/* ── 数据表 ── */
.data-table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }
.data-table th { background: #1a1a2e; color: #fff; padding: 8px 12px; text-align: center; white-space: nowrap; }
.data-table td { padding: 7px 12px; text-align: center; border-bottom: 1px solid #eee; }
.data-table tr:nth-child(even) { background: #f8f9fa; }
.data-table .neg { color: #d32f2f; }
.data-table .pos { color: #388e3c; }

/* ── 结论框 ── */
.conclusion-box { background: linear-gradient(135deg, #e3f2fd 0%, #fce4ec 100%); border-radius: 8px; padding: 14px 18px; margin: 12px 0; border-left: 4px solid #4fc3f7; line-height: 1.8; }
.conclusion-box strong { color: #1a1a2e; }
.insight-box { background: #fffde7; border-radius: 8px; padding: 14px 18px; margin: 12px 0; border-left: 4px solid #ffc107; line-height: 1.8; }
.suggest-box { background: #e8f5e9; border-radius: 8px; padding: 14px 18px; margin: 12px 0; border-left: 4px solid #4caf50; line-height: 1.8; }

/* ── N 栏布局（动态多列） ── */
.n-col { display: flex; gap: 16px; flex-wrap: wrap; }
.n-col > div { flex: 1; min-width: 220px; background: #fafbfc; border-radius: 8px; padding: 14px; border: 1px solid #eee; }
.n-col h4 { font-size: 14px; margin-bottom: 6px; }

/* ── 建议列表 ── */
.suggestion-list { line-height: 2.2; padding-left: 20px; font-size: 13.5px; }
.suggestion-list li { margin-bottom: 4px; }
.suggestion-list .highlight { color: #d32f2f; font-weight: 600; }
.suggestion-list .good { color: #388e3c; font-weight: 600; }

.footer { text-align: center; padding: 16px; color: #888; font-size: 12px; border-top: 1px solid #eee; background: #f8f9fa; clear: both; }
@media (max-width:768px){ .chart-row .chart-container { min-width:100%; } .navbar-title { display:none; } }
'''

def read_chart_js():
    """读取本地 chart.umd.min.js 并返回内嵌 script 标签"""
    js_path = Path(__file__).parent / 'chart.umd.min.js'
    with open(js_path, 'r', encoding='utf-8') as f:
        return f'<script>{f.read()}</script>'


# ════════════════════════════════════════════════════════════
#  JavaScript 生成 — 动态构建 N 班级 Chart.js 代码
# ════════════════════════════════════════════════════════════

def build_compare_js():
    """生成 COMPARE_JS 字符串，内嵌 N 班级图表的 JS 渲染函数。
    渲染函数通过参数接收数据，不再硬编码班级数量。
    """
    return r'''
// ── 图表1: 整体指标对比（分组柱状图） ──
function renderOverallChart(tag, d) {
    var ctx = document.getElementById(tag + '_overallChart');
    if (!ctx) return;
    var datasets = [];
    var metrics = ['平均分', '最高分', '最低分', '中位数'];
    for (var ci = 0; ci < d.class_order.length; ci++) {
        var ck = d.class_order[ci];
        var s = d.classes[ck].stats;
        datasets.push({
            label: ck,
            data: [s.mean, s.max, s.min, s.median],
            backgroundColor: d.class_colors[ck],
            borderRadius: 4
        });
    }
    new Chart(ctx, {
        type: 'bar',
        data: { labels: metrics, datasets: datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: '图表1：各班级整体指标对比（分组柱状图）—— 直观对比各班级集中趋势与离散程度', font: { size: 13 } }
            },
            scales: { y: { beginAtZero: true, title: { display: true, text: '分数' } } }
        }
    });
}

// ── 图表2: 全科单科均分对比（分组柱状图） ──
function renderSubjBarChart(tag, d) {
    var ctx = document.getElementById(tag + '_subjBar');
    if (!ctx) return;
    var datasets = [];
    for (var ci = 0; ci < d.class_order.length; ci++) {
        var ck = d.class_order[ci];
        datasets.push({
            label: ck + ' 均分',
            data: d.classes[ck].subj_means,
            backgroundColor: d.class_colors[ck],
            borderRadius: 4
        });
    }
    new Chart(ctx, {
        type: 'bar',
        data: { labels: d.subj_labels, datasets: datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: '图表2a：全科单科成绩对比（分组柱状图）—— 各科均分差异一目了然', font: { size: 13 } },
                tooltip: { callbacks: { label: function (c) { return c.dataset.label + ': ' + c.parsed.y + '分'; } } }
            },
            scales: { y: { beginAtZero: true, max: 160, title: { display: true, text: '平均分' } } }
        }
    });
}

// ── 图表3: 全科单科均分对比（雷达图） ──
function renderRadarChart(tag, d) {
    var ctx = document.getElementById(tag + '_subjRadar');
    if (!ctx) return;
    var datasets = [];
    for (var ci = 0; ci < d.class_order.length; ci++) {
        var ck = d.class_order[ci];
        datasets.push({
            label: ck,
            data: d.classes[ck].subj_means,
            borderColor: d.class_colors[ck],
            backgroundColor: d.class_colors_rgba[ck],
            pointBackgroundColor: d.class_colors[ck]
        });
    }
    new Chart(ctx, {
        type: 'radar',
        data: { labels: d.subj_labels, datasets: datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: '图表2b：单科均分雷达图 —— 整体评估各班级各科均衡性与差距分布', font: { size: 13 } }
            },
            scales: { r: { beginAtZero: true, max: 160 } }
        }
    });
}

// ── 图表4: 分数段人数分布对比（频数直方图） ──
function renderTierChart(tag, d) {
    var ctx = document.getElementById(tag + '_tierChart');
    if (!ctx) return;
    var datasets = [];
    for (var ci = 0; ci < d.class_order.length; ci++) {
        var ck = d.class_order[ci];
        datasets.push({
            label: ck,
            data: d.classes[ck].tier,
            backgroundColor: d.class_colors[ck],
            borderRadius: 4
        });
    }
    new Chart(ctx, {
        type: 'bar',
        data: { labels: d.tier_labels, datasets: datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: '图表3：各分数段人数分布对比（频数直方图）—— 呈现各班级成绩结构分层', font: { size: 13 } }
            },
            scales: { y: { beginAtZero: true, title: { display: true, text: '人数' }, ticks: { stepSize: 1 } } }
        }
    });
}

// ── 图表5: 各班级优中差层级占比（环形图，每个班级一个） ──
function renderPieCharts(tag, d) {
    for (var ci = 0; ci < d.class_order.length; ci++) {
        var ck = d.class_order[ci];
        var canvasId = tag + '_pie' + (ci + 1);
        var ctx = document.getElementById(canvasId);
        if (!ctx) continue;
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['优生(≥600)', '中等生(450-599)', '后进生(<450)'],
                datasets: [{ data: d.classes[ck].lv, backgroundColor: ['#4caf50', '#ff9800', '#f44336'] }]
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: {
                    title: { display: true, text: ck + '学情层级分布（环形图）—— 优生/中等生/后进生占比', font: { size: 13 } }
                }
            }
        });
    }
}

// ── 图表6: 跨月趋势折线图 ──
function renderTrendChart(canvasId, trendData) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;
    var datasets = [];
    for (var ci = 0; ci < trendData.class_order.length; ci++) {
        var ck = trendData.class_order[ci];
        datasets.push({
            label: ck,
            data: trendData.series[ck],
            borderColor: trendData.class_colors[ck],
            backgroundColor: trendData.class_colors_rgba[ck],
            fill: false,
            tension: 0.3,
            pointRadius: 4
        });
    }
    new Chart(ctx, {
        type: 'line',
        data: { labels: trendData.labels, datasets: datasets },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' },
                title: { display: true, text: trendData.title || '', font: { size: 13 } },
                tooltip: { callbacks: { label: function (c) { return c.dataset.label + ': ' + c.parsed.y; } } }
            },
            scales: { y: { beginAtZero: trendData.beginZero || false, title: { display: true, text: trendData.unit || '' } } }
        }
    });
}

// ── 统一入口（单月所有图表） ──
function renderComparisonCharts(tag, d) {
    renderOverallChart(tag, d);
    renderSubjBarChart(tag, d);
    renderRadarChart(tag, d);
    renderTierChart(tag, d);
    renderPieCharts(tag, d);
}
'''


# ════════════════════════════════════════════════════════════
#  数据解析与统计
# ════════════════════════════════════════════════════════════

def parse_arguments():
    parser = argparse.ArgumentParser(description='多班级考试成绩对比分析报告生成')
    parser.add_argument('--input-dir', default=r'F:\成绩分析',
                        help='Excel文件所在目录（默认: F:\\成绩分析）')
    parser.add_argument('--output', default='',
                        help='输出HTML文件路径（默认: 输入目录/考试成绩综合分析平台.html）')
    return parser.parse_args()


def find_excel_files(input_dir):
    """动态发现 N 个班级的 Excel 文件。
    
    返回:
        class_files: {class_key: {month_key: Path, ...}, ...}
        common_months: sorted list of month keys common to all classes
        month_order: sorted month keys
        class_order: sorted class keys (e.g. ['班级1', '班级2', ...])
    """
    input_dir = Path(input_dir)
    if not input_dir.exists():
        print(f"错误：目录不存在: {input_dir}")
        sys.exit(1)

    all_files = []
    for pattern in ['*.xlsx', '*.xls']:
        all_files.extend(input_dir.glob(pattern))
    all_files = [f for f in all_files if not f.name.startswith('~$')]

    # 动态发现班级：文件名包含 "班级N" 的就归入该班
    class_files = {}  # {class_key: {month: Path}}
    for fp in all_files:
        name = fp.stem
        cm = re.search(r'班级(\d+)', name)
        if not cm:
            continue
        class_key = f'班级{cm.group(1)}'
        mm = re.search(r'(\d+)月', name)
        month = mm.group(1) if mm else name
        if class_key not in class_files:
            class_files[class_key] = {}
        class_files[class_key][month] = fp

    if len(class_files) < 2:
        print(f"错误：至少需要2个班级才能对比，当前发现 {len(class_files)} 个（文件名需包含'班级1''班级2'等标识）")
        sys.exit(1)

    # 排序班级（按编号）
    def sort_class_key(k):
        m = re.search(r'(\d+)', k)
        return int(m.group(1)) if m else 999
    class_order = sorted(class_files.keys(), key=sort_class_key)

    # 取各班级月份的**交集**作为共同月份
    month_sets = [set(cf.keys()) for cf in class_files.values()]
    common = sorted(set.intersection(*month_sets),
                    key=lambda x: int(x) if x.isdigit() else 999)
    if not common:
        print("错误：未找到各班级的共同月份")
        sys.exit(1)

    return class_files, common, class_order


def load_excel(fp):
    """读取Excel并返回DataFrame，智能检测表头行"""
    df_raw = pd.read_excel(fp, header=None, engine='openpyxl', nrows=2)
    header_row = 0
    for i in range(min(2, len(df_raw))):
        row_str = ' '.join(str(v) for v in df_raw.iloc[i]).lower()
        if any(kw in row_str for kw in ['姓名', '总分', '名次', '语文']):
            header_row = i
            break
    df = pd.read_excel(fp, header=header_row, engine='openpyxl')
    df.columns = df.columns.astype(str).str.strip()
    df = df.dropna(how='all')
    return df


def safe_num(s, to_type=float):
    try:
        x = float(s)
        return None if math.isnan(x) else (to_type(x) if to_type == int else x)
    except:
        return None


def extract_numeric(df, col_name):
    if col_name not in df.columns:
        return pd.Series(dtype=float)
    return pd.to_numeric(df[col_name], errors='coerce').dropna()


def build_comparison_data(month, class_file_dict, class_order):
    """构建某个月份 N 个班级的完整对比数据。
    
    class_file_dict: {class_key: filepath, ...}
    
    返回结构:
    {
        'month': month,
        'classes': {
            class_key: {
                'stats': {count, mean, max, min, median, std},
                'pass_rate': float,
                'excellent_rate': float,
                'low_rate': float,
                'tier': [int]*4,
                'lv': [int]*3,
                'subj_means': [float]*5,
                'str': [str],   # strengths (subjects above avg)
                'wk': [str],    # weaknesses (subjects below avg)
                'pass_subj': [float]*5,   # subject pass rates
                'excellent_subj': [float]*5,  # subject excellent rates
                'count': int,
                'poly': float,  # coefficient of variation
            },
            ...
        },
        'class_order': [class_key, ...],
        'subj_labels': ['语文', '数学', '英语', '物理', '化学'],
        'tier_labels': [...],
    }
    """
    subj_labels = ['语文', '数学', '英语', '物理', '化学']

    # 读取所有班级的数据
    raw_data = {}  # {class_key: (total_series, subj_dict, count)}
    for ck in class_order:
        fp = class_file_dict[ck]
        df = load_excel(fp)
        total = extract_numeric(df, '总分')
        subjects = {}
        for s in subj_labels:
            subjects[s] = extract_numeric(df, s)
        raw_data[ck] = (total, subjects, len(df))

    # 计算各班级的统计
    classes = {}
    for ck in class_order:
        total, subjects, n = raw_data[ck]

        def mk(t):
            return {
                'count': len(t), 'mean': round(t.mean(), 1), 'max': round(t.max(), 1),
                'min': round(t.min(), 1), 'median': round(t.median(), 1), 'std': round(t.std(), 1)
            }

        stats = mk(total)

        # 通过率指标
        pass_rate = round(100 * sum(1 for v in total if v >= 450) / len(total), 1) if len(total) > 0 else 0
        excellent_rate = round(100 * sum(1 for v in total if v >= 600) / len(total), 1) if len(total) > 0 else 0
        low_rate = round(100 * sum(1 for v in total if v < 300) / len(total), 1) if len(total) > 0 else 0

        # 单科数据
        subj_means = []
        pass_subj = []
        excellent_subj = []
        for s in subj_labels:
            v = subjects.get(s, pd.Series(dtype=float))
            m = round(v.mean(), 1) if len(v) > 0 else 0
            subj_means.append(m)
            mx = 150 if s in ['语文', '数学', '英语'] else 100
            ps = round(100 * sum(1 for x in v if x >= mx * 0.6) / len(v), 1) if len(v) > 0 else 0
            es = round(100 * sum(1 for x in v if x >= mx * 0.8) / len(v), 1) if len(v) > 0 else 0
            pass_subj.append(ps)
            excellent_subj.append(es)

        # 分数段（4段）
        tier_bounds = [(600, 999), (500, 599), (400, 499), (0, 399)]
        tier = [sum(1 for v in total if lo <= v <= hi) for lo, hi in tier_bounds]

        # 学情分层（3层）
        lv = [
            sum(1 for v in total if v >= 600),
            sum(1 for v in total if 450 <= v < 600),
            sum(1 for v in total if v < 450)
        ]

        poly = round(stats['std'] / stats['mean'] * 100, 1) if stats['mean'] else 0

        classes[ck] = {
            'stats': stats,
            'pass_rate': pass_rate,
            'excellent_rate': excellent_rate,
            'low_rate': low_rate,
            'tier': tier,
            'lv': lv,
            'subj_means': subj_means,
            'pass_subj': pass_subj,
            'excellent_subj': excellent_subj,
            'count': n,
            'poly': poly,
        }

    # 计算各班级相对于平均的优势/短板
    # 先算各科目所有班级的平均分
    overall_subj_avg = []
    for si in range(len(subj_labels)):
        vals = [classes[ck]['subj_means'][si] for ck in class_order]
        overall_subj_avg.append(sum(vals) / len(vals))

    for ck in class_order:
        str_list = []
        wk_list = []
        for si, s in enumerate(subj_labels):
            diff = classes[ck]['subj_means'][si] - overall_subj_avg[si]
            if diff > 2:
                str_list.append(f'{s}（高{abs(diff):.1f}分）')
            elif diff < -2:
                wk_list.append(f'{s}（低{abs(diff):.1f}分）')
        classes[ck]['str'] = str_list
        classes[ck]['wk'] = wk_list

    tier_labels = ['高分段(≥600)', '中高分段(500-599)', '中分段(400-499)', '低分段(<400)']

    return {
        'month': month,
        'classes': classes,
        'class_order': class_order,
        'subj_labels': subj_labels,
        'tier_labels': tier_labels,
    }


# ════════════════════════════════════════════════════════════
#  HTML 章节生成
# ════════════════════════════════════════════════════════════

def _cls_tag(ck, colors):
    """为班级生成带颜色的 CSS class 名，返回 (class_name, color_hex)"""
    idx = list(colors.keys()).index(ck) if ck in colors else 0
    safe = re.sub(r'\D', '', ck) or '0'
    return f'c{safe}', colors[ck]


def gen_overall_section(d, tag, class_colors):
    """一、整体总体对比"""
    co = d['class_order']
    classes = d['classes']

    # 表头：指标 + N 个班级 + 全距
    th_cols = ''.join(f'<th style="color:{class_colors[ck]}">{ck}</th>' for ck in co)
    th_cols += '<th>全距</th>'

    # 指标行
    all_means = [classes[ck]['stats']['mean'] for ck in co]
    overall_mean = sum(all_means) / len(all_means)

    def metric_row(label, getter, fmt='{:.1f}', show_range=True):
        vals = [getter(classes[ck]) for ck in co]
        cells = ''.join(f'<td>{fmt.format(v)}</td>' for v in vals)
        rng = f'{max(vals) - min(vals):.1f}' if show_range else '-'
        return f'<tr><td><strong>{label}</strong></td>{cells}<td>{rng}</td></tr>'

    sget = lambda c: c['stats']
    rows = ''
    rows += metric_row('学生人数', lambda c: c['stats']['count'], '{:d}')
    rows += metric_row('平均分', lambda c: c['stats']['mean'])
    rows += metric_row('最高分', lambda c: c['stats']['max'])
    rows += metric_row('最低分', lambda c: c['stats']['min'])
    rows += metric_row('中位数', lambda c: c['stats']['median'])
    rows += metric_row('标准差', lambda c: c['stats']['std'])
    rows += metric_row('及格率(≥450)', lambda c: c['pass_rate'], '{:.1f}%')
    rows += metric_row('优秀率(≥600)', lambda c: c['excellent_rate'], '{:.1f}%')
    rows += metric_row('低分率(<300)', lambda c: c['low_rate'], '{:.1f}%')

    # 差距总结文本
    gap_desc = []
    best_ck = max(co, key=lambda ck: classes[ck]['stats']['mean'])
    worst_ck = min(co, key=lambda ck: classes[ck]['stats']['mean'])
    best_m = classes[best_ck]['stats']['mean']
    worst_m = classes[worst_ck]['stats']['mean']
    diff = best_m - worst_m
    if diff >= 5:
        gap_desc.append(f'均分差距显著（{diff:.1f}分），{best_ck}领先{worst_ck}。')
    elif diff >= 1:
        gap_desc.append(f'均分差距较小（{diff:.1f}分），{best_ck}略高于{worst_ck}。')
    else:
        gap_desc.append('各班级均分基本持平。')

    # 标准差/均衡度
    min_std_ck = min(co, key=lambda ck: classes[ck]['stats']['std'])
    gap_desc.append(f'{min_std_ck}标准差最小（{classes[min_std_ck]["stats"]["std"]}），整体成绩分布最集中。')

    # 优秀率
    max_excellent_ck = max(co, key=lambda ck: classes[ck]['excellent_rate'])
    min_excellent_ck = min(co, key=lambda ck: classes[ck]['excellent_rate'])
    er_diff = classes[max_excellent_ck]['excellent_rate'] - classes[min_excellent_ck]['excellent_rate']
    if er_diff >= 5:
        gap_desc.append(f'优秀率方面，{max_excellent_ck}领先{min_excellent_ck}{er_diff:.1f}个百分点。')

    return f'''
<div class="comp-section" id="{tag}_overall">
  <h2><span class="section-number">1</span> 整体总体对比</h2>
  <p style="margin-bottom:8px;color:#555;font-size:13px;"><strong>图表1：各班级整体指标对比（分组柱状图）</strong> — 直观展示各班级在平均分、最高分、最低分、中位数上的差异。</p>
  <div class="chart-container"><canvas id="{tag}_overallChart"></canvas></div>
  <table class="data-table"><thead><tr><th>指标</th>{th_cols}</tr></thead><tbody>{rows}</tbody></table>
  <div class="conclusion-box"><strong>差距总结：</strong>{' '.join(gap_desc)}</div>
</div>'''


def gen_subject_section(d, tag, class_colors):
    """二、单科维度对比"""
    co = d['class_order']
    classes = d['classes']
    subj_labels = d['subj_labels']

    # 表头
    th_cols = ''.join(f'<th style="color:{class_colors[ck]}">{ck}均分</th>' for ck in co)
    for suffix in ['及格率', '优秀率']:
        th_cols += ''.join(f'<th style="color:{class_colors[ck]}">{ck}{suffix}</th>' for ck in co)

    rows_subj = ''
    for si, s in enumerate(subj_labels):
        cells = ''.join(f'<td>{classes[ck]["subj_means"][si]}</td>' for ck in co)
        for suffix_type in ['pass_subj', 'excellent_subj']:
            cells += ''.join(f'<td>{classes[ck][suffix_type][si]}%</td>' for ck in co)
        rows_subj += f'<tr><td><strong>{s}</strong></td>{cells}</tr>'

    # 强弱分析
    all_parts = []
    for ck in co:
        str_list = classes[ck]['str']
        wk_list = classes[ck]['wk']
        html_str = '、'.join(str_list) if str_list else '<span style="color:#888">整体均衡</span>'
        html_wk = '、'.join(wk_list) if wk_list else '<span style="color:#888">无明显短板</span>'
        all_parts.append(f'<div><h4 style="color:{class_colors[ck]};">📍 {ck}</h4><p style="font-size:13px;"><strong>优势：</strong>{html_str}</p><p style="font-size:13px;"><strong>短板：</strong>{html_wk}</p></div>')

    return f'''
<div class="comp-section" id="{tag}_subject">
  <h2><span class="section-number">2</span> 单科维度对比</h2>
  <p style="margin-bottom:8px;color:#555;font-size:13px;">
    <strong>图表2a：全科单科成绩对比（分组柱状图）</strong> — 各科目均分横向对比，一目了然差距分布。<br>
    <strong>图表2b：单科均分雷达图</strong> — 整体评估各班级各科均衡性与差距轮廓。
  </p>
  <div class="chart-container" style="height:420px"><canvas id="{tag}_subjBar"></canvas></div>
  <div class="chart-container" style="height:520px"><canvas id="{tag}_subjRadar"></canvas></div>
  <table class="data-table"><thead><tr><th>科目</th>{th_cols}</tr></thead><tbody>{rows_subj}</tbody></table>
  <div class="conclusion-box">
    <strong>强弱分析：</strong>
    <div class="n-col" style="margin-top:10px;">{"".join(all_parts)}</div>
  </div>
</div>'''


def gen_tier_section(d, tag, class_colors):
    """三、分数段梯队对比"""
    co = d['class_order']
    classes = d['classes']

    th_cols = ''
    for ck in co:
        th_cols += f'<th style="color:{class_colors[ck]}">{ck}</th><th>占比</th>'

    rows = ''
    for i in range(4):
        cells = ''
        for ck in co:
            cnt = classes[ck]['tier'][i]
            pct = round(100 * cnt / classes[ck]['stats']['count'], 1) if classes[ck]['stats']['count'] > 0 else 0
            cells += f'<td>{cnt}</td><td>{pct}%</td>'
        rows += f'<tr><td>{d["tier_labels"][i]}</td>{cells}</tr>'

    # 分层分析文本
    parts = []
    for ck in co:
        c = classes[ck]
        high_pct = round(100 * c['tier'][0] / c['stats']['count'], 1)
        mid_high_pct = round(100 * c['tier'][1] / c['stats']['count'], 1)
        parts.append(f'{ck}高分段（≥600）占比{high_pct}%，中高分段（500-599）占比{mid_high_pct}%。')

    # 高分段比较
    high_tiers = [(ck, classes[ck]['tier'][0]) for ck in co]
    high_tiers.sort(key=lambda x: -x[1])
    parts.append(f'高分段人数最多的是{high_tiers[0][0]}（{high_tiers[0][1]}人），拔尖培养效果较好。')

    # 低分段
    has_low = [(ck, classes[ck]['tier'][3]) for ck in co if classes[ck]['tier'][3] > 0]
    if has_low:
        parts.append(f'低分段（<400分）需关注：{"、".join(f"{ck}({n}人)" for ck, n in has_low)}。')
    else:
        parts.append('各班级均无400分以下学生，整体学业基础较好。')

    return f'''
<div class="comp-section" id="{tag}_tier">
  <h2><span class="section-number">3</span> 分数段梯队对比</h2>
  <p style="margin-bottom:8px;color:#555;font-size:13px;"><strong>图表3：各分数段人数分布对比（频数直方图）</strong> — 呈现各班级成绩结构分层，了解各分数段人数分布差异。</p>
  <div class="chart-container"><canvas id="{tag}_tierChart"></canvas></div>
  <table class="data-table"><thead><tr><th>分数段</th>{th_cols}</tr></thead><tbody>{rows}</tbody></table>
  <div class="conclusion-box"><strong>分层分析：</strong>{" ".join(parts)}</div>
</div>'''


def gen_structure_section(d, tag, class_colors):
    """四、学情结构分析"""
    co = d['class_order']
    classes = d['classes']

    th_cols = ''
    for ck in co:
        th_cols += f'<th style="color:{class_colors[ck]}">{ck}</th><th>占比</th>'

    layer_data = [('优生', '≥600'), ('中等生', '450-599'), ('后进生', '<450')]
    rows = ''
    for i, (l, c) in enumerate(layer_data):
        cells = ''
        for ck in co:
            cnt = classes[ck]['lv'][i]
            pct = round(100 * cnt / classes[ck]['stats']['count'], 1) if classes[ck]['stats']['count'] > 0 else 0
            cells += f'<td>{cnt}</td><td>{pct}%</td>'
        rows += f'<tr><td>{l}</td><td>{c}</td>{cells}</tr>'

    # 均衡度分析
    balance_parts = []
    min_poly_ck = min(co, key=lambda ck: classes[ck]['poly'])
    balance_parts.append(f'{min_poly_ck}变异系数最小（{classes[min_poly_ck]["poly"]}%），学情最均衡。')

    has_low = [ck for ck in co if classes[ck]['lv'][2] > 0]
    if has_low:
        balance_parts.append(f'后进生（<450分）存在于：{"、".join(has_low)}，需关注学困生帮扶。')
    else:
        balance_parts.append('各班级均无后进生，整体学业水平良好。')

    has_excellent = [(ck, classes[ck]['lv'][0]) for ck in co if classes[ck]['lv'][0] > 0]
    if has_excellent:
        has_excellent.sort(key=lambda x: -x[1])
        balance_parts.append(f'{has_excellent[0][0]}优生群体最大（{has_excellent[0][1]}人），拔尖能力突出。')

    # 环形图 canvas 布局
    pie_canvases = ''
    for ci, ck in enumerate(co):
        pie_canvases += f'<div class="chart-container"><canvas id="{tag}_pie{ci+1}"></canvas></div>'

    return f'''
<div class="comp-section" id="{tag}_structure">
  <h2><span class="section-number">4</span> 学情结构分析</h2>
  <p style="margin-bottom:8px;color:#555;font-size:13px;">各班级优生/中等生/后进生占比（环形图）。</p>
  <div class="chart-row">{pie_canvases}</div>
  <table class="data-table"><thead><tr><th>层级</th><th>标准</th>{th_cols}</tr></thead><tbody>{rows}</tbody></table>
  <div class="conclusion-box">
    <strong>均衡度分析：</strong>{" ".join(balance_parts)}
  </div>
</div>'''


def gen_traceback_section(d, tag, class_colors):
    """五、成绩问题溯源"""
    co = d['class_order']
    classes = d['classes']

    def fmt_adv(lst):
        if not lst:
            return '整体无显著优势学科，各科发展较为均衡。'
        return '、'.join(lst) + '等方面表现较好。'

    def fmt_weak(lst):
        if not lst:
            return '无明显短板学科。'
        return '、'.join(lst) + '等方面需重点加强。'

    # 各班级
    class_boxes = ''
    for ck in co:
        class_boxes += f'''
    <div>
      <h4 style="color:{class_colors[ck]};">🏫 {ck}</h4>
      <p style="font-size:13px;"><strong>优势：</strong>{fmt_adv(classes[ck]["str"])}</p>
      <p style="font-size:13px;"><strong>短板：</strong>{fmt_weak(classes[ck]["wk"])}</p>
    </div>'''

    # 共性问题：找出所有班级都薄弱的科目
    common_wk = set()
    for ck in co:
        for item in classes[ck]['wk']:
            subj = item.split('（')[0]
            if all(subj in ''.join(classes[other]['wk']) for other in co):
                common_wk.add(subj)

    common_issues = []
    if common_wk:
        common_issues.append(f'各班级在{"、".join(sorted(common_wk))}科目上均存在短板，需作为教研重点。')

    all_full_pass = all(classes[ck]['pass_rate'] == 100 for ck in co)
    if all_full_pass:
        common_issues.append('各班级及格率均为100%，基础知识掌握较好。')

    # 个性化问题
    specific_parts = []
    for ck in co:
        if classes[ck]['wk']:
            specific_parts.append(f'{ck}需针对性解决{fmt_weak(classes[ck]["wk"])}')

    return f'''
<div class="comp-section" id="{tag}_traceback">
  <h2><span class="section-number">5</span> 成绩问题溯源</h2>
  <div class="n-col">{class_boxes}
  </div>
  <div class="insight-box" style="margin-top:12px;">
    <strong>🔍 共性问题：</strong>{' '.join(common_issues) if common_issues else '无显著共性问题。'}<br>
    <strong style="margin-top:6px;display:block;">🎯 个性化问题：</strong>
    {'<br>'.join(specific_parts) if specific_parts else '各班级无明显个性短板。'}
  </div>
</div>'''


def gen_suggestion_section(d, tag, class_colors):
    """六、教学改进建议"""
    co = d['class_order']
    classes = d['classes']

    # 各班单独建议
    all_sugs = {}
    for ck in co:
        sugs = []
        c = classes[ck]

        # 培优
        if c['lv'][0] > 0:
            str_text = '、'.join(x for x in c['str']) if c['str'] else '优势科目'
            sugs.append(f'培优：对尖子生（≥600分）加强思维训练与拔高练习，重点针对{str_text}进一步突破。')
        else:
            sugs.append('培优：目前无600分以上学生，需从500分以上学生中遴选苗子，加大培优力度。')

        # 补差
        if c['lv'][2] > 0:
            wk_text = '、'.join(c['wk'])
            sugs.append(f'补差：对后进生（<450分）实施"一对一"帮扶，夯实基础，重点补齐{wk_text}。')
        else:
            sugs.append('补差：无后进生，保持基础教学节奏即可。')

        # 学科针对性
        for item_str in c['wk']:
            sugs.append(f'{item_str.split("（")[0]}学科：需加强训练，缩小差距。')

        all_sugs[ck] = sugs

    # 整体建议
    conf = ''
    all_means = [classes[ck]['stats']['mean'] for ck in co]
    overall_mean = sum(all_means) / len(all_means)
    worst_ck = min(co, key=lambda ck: classes[ck]['stats']['mean'])
    best_ck = max(co, key=lambda ck: classes[ck]['stats']['mean'])
    diff = classes[best_ck]['stats']['mean'] - classes[worst_ck]['stats']['mean']
    if diff > 3:
        conf += f'<li><strong>整体建议：</strong>{worst_ck}需从教学管理、课堂效率、作业分层等方面系统提升，借鉴{best_ck}的教学经验，重点缩小{diff:.1f}分的均分差距。</li>'

    # 各班级建议列
    sug_cols = ''.join(
        f'<div><h4 style="color:{class_colors[ck]};">🏫 {ck} 改进方案</h4><ul class="suggestion-list">'
        + ''.join(f'<li>{s}</li>' for s in all_sugs[ck][:4])
        + '</ul></div>'
        for ck in co
    )

    return f'''
<div class="comp-section" id="{tag}_suggestion">
  <h2><span class="section-number">6</span> 教学改进建议</h2>
  <div class="suggest-box">
    <strong>📋 综合建议</strong>
    <ul class="suggestion-list">
      {conf if conf else '<li><strong>整体建议：</strong>各班级整体水平接近，可采用统一教学策略，在各自短板学科上精细施策。</li>'}
      <li><strong>分层教学：</strong>高分段（≥600）侧重思维拓展与综合应用；中分段（450-599）侧重方法指导与提分策略；低分段（<450）侧重基础巩固与信心建立。</li>
      <li><strong>协同教研：</strong>各班级教师可就优势学科交叉交流，共享教学资源，互听互评，共同提升教学质量。</li>
    </ul>
  </div>
  <div class="n-col" style="margin-top:14px;">{sug_cols}</div>
</div>'''


def gen_trend_section(all_data, tag_prefix, class_order, class_colors):
    """七、跨月趋势分析（折线图）"""
    month_labels = sorted(all_data.keys(), key=lambda x: int(x))

    # 趋势文本
    trend_parts = []
    if len(month_labels) >= 2:
        for ck in class_order:
            means = [all_data[m]['classes'][ck]['stats']['mean'] for m in month_labels]
            trend = means[-1] - means[0]
            trend_parts.append(f'{ck}均分从{month_labels[0]}月到{month_labels[-1]}月{"上升" if trend > 0 else "下降"}了{abs(trend):.1f}分。')

        best_trend_ck = max(class_order, key=lambda ck: all_data[month_labels[-1]]['classes'][ck]['stats']['mean'] - all_data[month_labels[0]]['classes'][ck]['stats']['mean'])
        worst_trend_ck = min(class_order, key=lambda ck: all_data[month_labels[-1]]['classes'][ck]['stats']['mean'] - all_data[month_labels[0]]['classes'][ck]['stats']['mean'])
        best_diff = all_data[month_labels[-1]]['classes'][best_trend_ck]['stats']['mean'] - all_data[month_labels[0]]['classes'][best_trend_ck]['stats']['mean']
        if best_diff > 0:
            trend_parts.append(f'{best_trend_ck}进步幅度最大，教学改进成效最显著。')

    return f'''
<div class="tab-content" id="tab-{tag_prefix}">
<div class="main-comp">
<div class="comp-section">
  <h2><span class="section-number">1</span> 跨月趋势分析</h2>
  <p style="margin-bottom:8px;color:#555;font-size:13px;"><strong>图表1：各班级均分跨月变化趋势（折线图）</strong> — 追踪各月份各班级均分变化，评估学业发展趋势。</p>
  <div class="chart-container"><canvas id="{tag_prefix}_meanChart"></canvas></div>
  <div class="chart-container"><canvas id="{tag_prefix}_stdChart"></canvas></div>
  <div class="conclusion-box"><strong>趋势总结：</strong>{" ".join(trend_parts) if trend_parts else "仅有一个月份数据，无法进行趋势分析。"}</div>
</div>
</div>
</div>'''


# ════════════════════════════════════════════════════════════
#  HTML 组装
# ════════════════════════════════════════════════════════════

def gen_month_section(d, tag, class_colors):
    sections = (gen_overall_section(d, tag, class_colors) +
                gen_subject_section(d, tag, class_colors) +
                gen_tier_section(d, tag, class_colors) +
                gen_structure_section(d, tag, class_colors) +
                gen_traceback_section(d, tag, class_colors) +
                gen_suggestion_section(d, tag, class_colors))

    inner_nav = f'''
<div class="inner-sidebar">
  <div class="inner-sidebar-title">📋 章节导航</div>
  <a class="inner-nav-item" href="#{tag}_overall" onclick="scrollToSection(event, \'{tag}_overall\')">整体总体对比</a>
  <a class="inner-nav-item" href="#{tag}_subject" onclick="scrollToSection(event, \'{tag}_subject\')">单科维度对比</a>
  <a class="inner-nav-item" href="#{tag}_tier" onclick="scrollToSection(event, \'{tag}_tier\')">分数段梯队对比</a>
  <a class="inner-nav-item" href="#{tag}_structure" onclick="scrollToSection(event, \'{tag}_structure\')">学情结构分析</a>
  <a class="inner-nav-item" href="#{tag}_traceback" onclick="scrollToSection(event, \'{tag}_traceback\')">成绩问题溯源</a>
  <a class="inner-nav-item" href="#{tag}_suggestion" onclick="scrollToSection(event, \'{tag}_suggestion\')">教学改进建议</a>
</div>'''

    return f'<div class="tab-content" id="tab-{tag}"><div class="comp-layout">{inner_nav}<div class="comp-main">{sections}</div></div></div>'


def main():
    args = parse_arguments()
    input_dir = args.input_dir
    output_path = args.output or os.path.join(input_dir, '考试成绩综合分析平台.html')

    print("=" * 50)
    print("多班级考试成绩对比分析报告 生成器")
    print("=" * 50)

    # 1. 查找文件
    print(f"\n扫描目录: {input_dir}")
    class_files, common_months, class_order = find_excel_files(input_dir)
    print(f"发现班级: {', '.join(class_order)}")
    print(f"共同月份: {', '.join(common_months)}")

    # 构建 class_colors 映射
    class_colors = {}
    for idx, ck in enumerate(class_order):
        class_colors[ck] = get_class_color(idx)
    class_colors_rgba = {}
    for idx, ck in enumerate(class_order):
        class_colors_rgba[ck] = get_class_rgba(idx)

    # 2. 生成数据
    print("\n生成对比数据...")
    comp_data = {}
    for m in common_months:
        month_dict = {ck: class_files[ck][m] for ck in class_order}
        print(f"  {m}月: " + ' + '.join(f'{class_files[ck][m].name}' for ck in class_order))
        comp_data[m] = build_comparison_data(m, month_dict, class_order)
        # 注入颜色信息供 JS 图表渲染使用
        comp_data[m]['class_colors'] = class_colors
        comp_data[m]['class_colors_rgba'] = class_colors_rgba
        for ck in class_order:
            print(f"    -> {ck}={comp_data[m]['classes'][ck]['count']}人")

    # 3. 组装HTML
    print("\n组装HTML...")

    chart_js_embed = read_chart_js()
    COMPARE_JS = build_compare_js()

    # 附加 CSS 动态 class
    extra_css = ''
    for idx, ck in enumerate(class_order):
        color = get_class_color(idx)
        extra_css += f'.data-table .c{idx+1} {{ color: {color}; font-weight: bold; }}\n'

    nav_items = ''
    first = True
    month_colors_palette = ['#4caf50', '#ff9800', '#9c27b0', '#2196f3', '#f44336']
    for i, m in enumerate(common_months):
        tag = f'm{m}'
        color = month_colors_palette[i % len(month_colors_palette)]
        active = ' active' if first else ''
        nav_items += f'<div class="nav-item{active}" onclick="switchTab(\'{tag}\')"><span class="nav-dot" style="background:{color}"></span>{m}月对比分析</div>\n'
        first = False

    # 添加趋势导航
    nav_items += f'<div class="nav-item" onclick="switchTab(\'trend\')"><span class="nav-dot" style="background:#607d8b"></span>跨月趋势分析</div>\n'

    tab_contents = ''.join(gen_month_section(comp_data[m], f'm{m}', class_colors) for m in common_months)
    tab_contents += gen_trend_section(comp_data, 'trend', class_order, class_colors)

    # 序列化 comp_data: 把 classes 中的嵌套对象转为 JSON 友好的格式
    comp_init_json = json.dumps(comp_data, ensure_ascii=False)

    # 趋势数据 — 为每个班级构建一个 series
    month_labels = sorted(comp_data.keys(), key=lambda x: int(x))
    trend_mean_series = {}
    trend_std_series = {}
    for ck in class_order:
        trend_mean_series[ck] = [comp_data[m]['classes'][ck]['stats']['mean'] for m in month_labels]
        trend_std_series[ck] = [comp_data[m]['classes'][ck]['stats']['std'] for m in month_labels]

    trend_mean_data = json.dumps({
        'labels': [f'{m}月' for m in month_labels],
        'series': trend_mean_series,
        'class_order': class_order,
        'class_colors': class_colors,
        'class_colors_rgba': class_colors_rgba,
        'title': '各班级均分跨月变化趋势（折线图）—— 各月份均分走势对比',
        'unit': '分数',
        'beginZero': False
    }, ensure_ascii=False)
    trend_std_data = json.dumps({
        'labels': [f'{m}月' for m in month_labels],
        'series': trend_std_series,
        'class_order': class_order,
        'class_colors': class_colors,
        'class_colors_rgba': class_colors_rgba,
        'title': '各班级标准差跨月变化趋势（折线图）—— 评估班级成绩稳定性变化',
        'unit': '标准差',
        'beginZero': True
    }, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>多班级考试成绩对比分析报告</title>
{chart_js_embed}
<style>{CSS}
{extra_css}</style>
</head>
<body>

<div class="navbar">
<div class="navbar-title">考试成绩对比分析</div>
<div class="navbar-tabs">
{nav_items}
</div>
</div>

<div class="main-container">
{tab_contents}
</div>

<script>
var compRendered = {{}};
var compData = {comp_init_json};

function switchTab(id) {{
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  var nav = document.querySelector('.nav-item[onclick*="' + id + '"]');
  if (nav) nav.classList.add('active');
  var tab = document.getElementById('tab-' + id);
  if (tab) tab.classList.add('active');

  document.querySelectorAll('.inner-nav-item').forEach(el => el.classList.remove('active'));
  var firstInner = tab ? tab.querySelector('.inner-nav-item') : null;
  if (firstInner) firstInner.classList.add('active');

  if (!compRendered[id]) {{
    compRendered[id] = true;
    if (id === 'trend') {{
      setTimeout(function() {{
        renderTrendChart('trend_meanChart', {trend_mean_data});
        renderTrendChart('trend_stdChart', {trend_std_data});
        window.dispatchEvent(new Event('resize'));
      }}, 200);
    }} else {{
      setTimeout(function() {{
        var monthKey = id.replace('m', '');
        renderComparisonCharts(id, compData[monthKey]);
        window.dispatchEvent(new Event('resize'));
        initScrollSpy(id);
      }}, 200);
    }}
  }} else {{
    setTimeout(function() {{ window.dispatchEvent(new Event('resize')); initScrollSpy(id); }}, 100);
  }}
}}

var _lastClickTime = 0;

function scrollToSection(event, id) {{
  if (event) event.preventDefault();
  var el = document.getElementById(id);
  if (!el) return;

  document.querySelectorAll('.tab-content.active .inner-nav-item').forEach(function(item) {{
    item.classList.remove('active');
  }});
  var link = document.querySelector('.tab-content.active .inner-nav-item[href="#' + id + '"]');
  if (link) link.classList.add('active');

  _lastClickTime = Date.now();
  el.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
}}

function initScrollSpy(tag) {{
  var container = document.getElementById('tab-' + tag);
  if (!container) return;
  var navItems = container.querySelectorAll('.inner-nav-item');
  var sections = [];
  navItems.forEach(function(item) {{
    var href = item.getAttribute('href');
    if (href) sections.push(document.getElementById(href.substring(1)));
  }});
  if (!sections.length) return;

  var ticking = false;
  function updateActive() {{
    ticking = false;
    if (Date.now() - _lastClickTime < 800) return;
    var scrollY = window.scrollY;
    var current = -1;
    var offset = 100;
    sections.forEach(function(sec, idx) {{
      if (sec && sec.offsetTop <= scrollY + offset) current = idx;
    }});
    navItems.forEach(function(item, idx) {{
      item.classList.toggle('active', idx === current);
    }});
  }}
  window.addEventListener('scroll', function() {{
    if (!ticking) requestAnimationFrame(function() {{ updateActive(); }});
    ticking = true;
  }});
  updateActive();
}}

{COMPARE_JS}

document.addEventListener('DOMContentLoaded', function() {{
  var first = document.querySelector('.nav-item.active');
  if (first) {{
    var onclick = first.getAttribute('onclick');
    var match = onclick.match(/'([^']+)'/);
    if (match) switchTab(match[1]);
  }}
}});
</script>

<footer class="footer">
<p>报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')} | 分析 {len(common_months)} 个月份，{len(class_order)} 个班级 | 学校教务成绩对比分析报告</p>
<p style="margin-top:4px;color:#aaa;">图表对照：①分组柱状图（整体指标）②分组柱状图+雷达图（单科对比）③频数直方图（分数段）④环形图（学情分层）⑤折线图（跨月趋势）</p>
</footer>

</body>
</html>'''

    # 4. 写入
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n[OK] 生成: {output_path} ({os.path.getsize(output_path) / 1024:.0f} KB)")


if __name__ == '__main__':
    main()
