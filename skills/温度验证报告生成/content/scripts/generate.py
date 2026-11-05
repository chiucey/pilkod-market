# -*- coding: utf-8 -*-
"""
温度验证报告生成器（1:1 复刻 SiNSE 验证报告版式）
- 输入 CSV（首列时间，其余 T 开头为探头，自动忽略"最高/最低"等汇总列）
- 可选生成 PDF / HTML / 两者
- 工艺标准（目标/下限/上限/保持分钟数）可配置
- 验证信息 INFO 可配置（公司名、验证对象、仪器等）

用法示例：
  python generate.py --csv code.csv --format both
  python generate.py --csv code.csv --format pdf --target 121 --low 120 --high 122 --holdmin 15
  python generate.py --csv code.csv --format html --info my_info.json
"""
import os, math, csv, io, base64, json, argparse
from datetime import datetime, timedelta

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
import pymupdf

# ============ 字体 ============
FONT_PATH = r"C:\Windows\Fonts\msyh.ttc"
FONT_BD_PATH = r"C:\Windows\Fonts\msyhbd.ttc"
FONT = "YaHei"
FONT_B = "YaHeiBold"
pdfmetrics.registerFont(TTFont(FONT, FONT_PATH, subfontIndex=0))
pdfmetrics.registerFont(TTFont(FONT_B, FONT_BD_PATH, subfontIndex=0))
registerFontFamily(FONT, normal=FONT, bold=FONT_B, italic=FONT, boldItalic=FONT_B)
yahei_prop = fm.FontProperties(fname=FONT_PATH)

# ============ INFO 默认值（乌苏里江，可按需覆盖）============
DEFAULT_INFO = {
    "装载类型": "满载热分布1",
    "公司名称": "黑龙江乌苏里江制药有限公司",
    "验证报告编号": "YZ20260820_T01",
    "校准报告编号": "请见“校准数据报告”",
    "验证对象": "灭菌柜A",
    "型号": "XG-1.2",
    "编号": "SZ-001",
    "备注": "备注1",
    "验证仪器": "温度验证仪",
    "仪器型号": "C200",
    "仪器编号": "1786939758",
    "简称": "J01",
    "SOP": "",
    "扫描间隔": "1.8",
    "记录间隔": "60",
    "探头数量": "3",
    "压力探头": "0",
    "验证类型": "湿热",
    "压力要求": "",
    "时长要求": "15",
    "日期": "2026-08-20",
}

# ============ 命令行 / JSON 覆盖项（常用字段）============
QUICK_KEYS = ["装载类型", "公司名称", "验证报告编号", "校准报告编号", "验证对象",
              "型号", "编号", "备注", "验证仪器", "仪器型号", "仪器编号", "简称",
              "SOP", "扫描间隔", "记录间隔", "压力探头", "验证类型", "压力要求", "日期"]


def build_info(args):
    info = dict(DEFAULT_INFO)
    # 1) JSON 文件整体覆盖（若存在）
    if args.info and os.path.exists(args.info):
        with open(args.info, encoding="utf-8") as f:
            info.update(json.load(f))
    # 2) 快捷参数覆盖
    for k in QUICK_KEYS:
        v = getattr(args, k.replace(" ", "_"), None)
        if v is not None:
            info[k] = v
    return info


def parse_time(tstr, fallback_date):
    tstr = tstr.strip()
    if "时" in tstr and "分" in tstr:
        h, m = tstr.replace("分", "").split("时")
        return datetime.strptime(f"{fallback_date} {int(h):02d}:{int(m):02d}:00", "%Y-%m-%d %H:%M:%S")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(tstr, fmt)
        except ValueError:
            pass
    raise ValueError("无法解析时间: %r" % tstr)


def load_csv(csv_path, info):
    raw_times, times, data = [], [], {}
    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = [h.strip() for h in next(reader)]
        # 探头列：列名以 T 开头；记录其在表头中的真实列序号（支持汇总列任意穿插）
        probe_cols = [h for h in header if h.startswith("T")]
        probe_idx = {h: header.index(h) for h in probe_cols}
        # 时间列：默认首列；若首列本身是探头名，则取第一个非 T 列作为时间列
        if header and header[0].startswith("T"):
            time_idx = next((i for i, h in enumerate(header) if not h.startswith("T")), 0)
        else:
            time_idx = 0
        for c in probe_cols:
            data[c] = []
        first_dt = None
        for row in reader:
            if not row or len(row) <= time_idx or not row[time_idx].strip():
                continue
            dt = parse_time(row[time_idx], info.get("日期", datetime.now().strftime("%Y-%m-%d")))
            if first_dt is None:
                first_dt = dt
                info["日期"] = dt.strftime("%Y-%m-%d")
            raw_times.append(dt.strftime("%Y-%m-%d %H:%M:%S"))
            times.append(dt.hour * 60 + dt.minute + dt.second / 60.0)
            for c in probe_cols:
                data[c].append(float(row[probe_idx[c]]))
    return raw_times, times, data, probe_cols


def compute(raw_times, times, data, probe_cols, info, T_TARGET, T_LOW, T_HIGH, HOLD_MIN_MIN):
    N = len(probe_cols)
    M = len(times)
    channels = [f"{info['简称']}_{i + 1:02d}" for i in range(N)]
    tags = [f"T{i + 1}" for i in range(N)]
    channel_of = {probe_cols[i]: channels[i] for i in range(N)}
    tag_of = {probe_cols[i]: tags[i] for i in range(N)}

    stats = {}
    for c in probe_cols:
        arr = data[c]
        mn = min(arr); mx = max(arr); avg = sum(arr) / len(arr)
        stats[c] = {
            "min": mn, "max": mx, "range": mx - mn, "avg": avg,
            "dev": avg - T_TARGET, "波动度": (mx - mn) / 2.0,
            "最大减平均": mx - avg, "平均减最小": avg - mn,
        }

    all_vals = [v for arr in data.values() for v in arr]
    gmin, gmax, gavg = min(all_vals), max(all_vals), sum(all_vals) / len(all_vals)
    std = math.sqrt(sum((v - gavg) ** 2 for v in all_vals) / len(all_vals))

    max_span, max_span_t = -1, times[0]
    max_dev_hi, max_dev_hi_t = -1, times[0]
    max_dev_lo, max_dev_lo_t = -1, times[0]
    for i, t in enumerate(times):
        vals = [data[c][i] for c in probe_cols]
        mi, ma, av = min(vals), max(vals), sum(vals) / len(vals)
        if ma - mi > max_span:
            max_span, max_span_t = ma - mi, t
        if ma - av > max_dev_hi:
            max_dev_hi, max_dev_hi_t = ma - av, t
        if av - mi > max_dev_lo:
            max_dev_lo, max_dev_lo_t = av - mi, t

    dur_min = times[-1] - times[0]
    within = (gmin >= T_LOW) and (gmax <= T_HIGH)
    is_ok = within and dur_min >= HOLD_MIN_MIN

    # 把派生项写回 INFO
    info["探头数量"] = str(N)
    info["时长要求"] = str(HOLD_MIN_MIN)
    return dict(N=N, M=M, channels=channels, tags=tags, channel_of=channel_of, tag_of=tag_of,
                stats=stats, gmin=gmin, gmax=gmax, gavg=gavg, std=std,
                max_span=max_span, max_span_t=max_span_t, max_dev_hi=max_dev_hi, max_dev_hi_t=max_dev_hi_t,
                max_dev_lo=max_dev_lo, max_dev_lo_t=max_dev_lo_t, dur_min=dur_min, within=within, is_ok=is_ok)


# ============ 趋势图 ============
def draw_trend(times, data, probe_cols, channel_of, T_TARGET, T_LOW, T_HIGH, dur_min):
    fig, ax = plt.subplots(figsize=(11.5, 3.8), dpi=150)
    cmap = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]
    M = len(times)
    for i, c in enumerate(probe_cols):
        ax.plot(range(M), data[c], marker="o", ms=2.5, lw=1.2,
                color=cmap[i % len(cmap)], label=channel_of[c])
    ax.axhline(T_HIGH, color="red", ls="--", lw=1.0)
    ax.axhline(T_LOW, color="red", ls="--", lw=1.0)
    ax.axhline(T_TARGET, color="green", ls="--", lw=1.0)
    ax.text(M - 0.5, T_HIGH + 0.05, "温度上限(%.0f)" % T_HIGH,
            fontproperties=yahei_prop, fontsize=8, color="red", va="bottom")
    ax.text(M - 0.5, T_TARGET + 0.05, "工艺温度(%.0f)" % T_TARGET,
            fontproperties=yahei_prop, fontsize=8, color="green", va="bottom")
    ax.text(M - 0.5, T_LOW - 0.05, "温度下限(%.0f)" % T_LOW,
            fontproperties=yahei_prop, fontsize=8, color="red", va="top")
    xlabels = [fmt_hm(t) for t in times]
    ax.set_xticks(range(M)[::2])
    ax.set_xticklabels([xlabels[i] for i in range(0, M, 2)],
                       rotation=45, ha="right", fontsize=7, fontproperties=yahei_prop)
    ax.set_ylabel("温度", fontproperties=yahei_prop, fontsize=9)
    ax.set_title("温度(压力)趋势分析图表 工艺时间段本时间段时长：（%s）" % fmt_dhms(dur_min),
                 fontproperties=yahei_prop, fontsize=11)
    ax.grid(True, ls=":", alpha=0.5)
    ax.legend(loc="upper left", ncol=len(probe_cols), fontsize=7, frameon=True, prop=yahei_prop)
    ax.set_xlim(-0.5, M - 0.5)
    ax.set_ylim(T_LOW - 2, T_HIGH + 2)
    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, dpi=150, bbox_inches="tight", format="png")
    plt.close(fig)
    buf.seek(0)
    return buf


def draw_layout(N, info):
    fig, ax = plt.subplots(figsize=(8, 3.5), dpi=150)
    ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis('off')
    rect = plt.Rectangle((1, 0.5), 8, 3, fill=False, edgecolor='black', lw=2)
    ax.add_patch(rect)
    cols = math.ceil(math.sqrt(N)); rows = math.ceil(N / cols)
    positions = []
    for idx in range(N):
        r = idx // cols; c = idx % cols
        x = 1 + 8 * (c + 0.5) / cols
        y = 0.5 + 3 * (rows - r - 0.5) / rows
        positions.append((x, y))
    for i, (x, y) in enumerate(positions):
        ax.plot(x, y, 'o', markersize=16, color='#1f77b4')
        ax.text(x, y, f"T{i + 1}", ha='center', va='center', fontsize=10,
                color='white', fontproperties=yahei_prop, fontweight='bold')
    ax.text(5, 3.8, "灭菌柜腔体布点示意图", ha='center', fontproperties=yahei_prop, fontsize=12)
    buf = io.BytesIO()
    fig.savefig(buf, dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


# ============ 工具函数 ============
def fmt_hm(minutes):
    m = int(round(minutes)); return f"{m // 60:02d}:{m % 60:02d}"

def fmt_dt(minutes, date_str):
    base = datetime.strptime(date_str, "%Y-%m-%d")
    return (base + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")

def fmt_dhms(minutes):
    m = int(round(minutes)); h = m // 60; mi = m % 60
    return f"0天{h}小时{mi}分0秒"

def gray():
    return colors.HexColor("#E7E6E6")

def p(text, size=9, bold=False, align=TA_LEFT, leading=None):
    if leading is None:
        leading = size + 3
    return Paragraph(
        f"<font name='{FONT_B if bold else FONT}' size={size}>{text}</font>",
        ParagraphStyle("p", fontName=FONT_B if bold else FONT, fontSize=size,
                       leading=leading, alignment=align)
    )


# ============ PDF 生成 ============
def build_pdf(out_path, info, ctx, raw_times, times, data, channel_of, tag_of, stats,
              T_TARGET, T_LOW, T_HIGH, HOLD_MIN_MIN):
    N = ctx["N"]; M = ctx["M"]
    gmin, gmax, gavg, std = ctx["gmin"], ctx["gmax"], ctx["gavg"], ctx["std"]
    max_span, max_span_t = ctx["max_span"], ctx["max_span_t"]
    max_dev_hi, max_dev_hi_t = ctx["max_dev_hi"], ctx["max_dev_hi_t"]
    max_dev_lo, max_dev_lo_t = ctx["max_dev_lo"], ctx["max_dev_lo_t"]
    dur_min, within, is_ok = ctx["dur_min"], ctx["within"], ctx["is_ok"]
    probe_cols = list(channel_of.keys())
    date_str = info["日期"]

    PAGE_W, PAGE_H = landscape(A4)
    LMARGIN = RMARGIN = 12 * mm
    TMARGIN = 18 * mm; BMARGIN = 12 * mm
    usable_w = PAGE_W - LMARGIN - RMARGIN
    usable_h = PAGE_H - TMARGIN - BMARGIN

    trend_buf = draw_trend(times, data, probe_cols, channel_of, T_TARGET, T_LOW, T_HIGH, dur_min)
    layout_buf = draw_layout(N, info)
    trend_path = out_path + ".trend.png"
    layout_path = out_path + ".layout.png"
    with open(trend_path, "wb") as f: f.write(trend_buf.getvalue())
    with open(layout_path, "wb") as f: f.write(layout_buf.getvalue())

    def make_header(canvas, doc, total_pages):
        canvas.saveState()
        canvas.setFont(FONT, 9); canvas.setFillColor(colors.black)
        canvas.drawString(LMARGIN, PAGE_H - 10 * mm, "SiNSE")
        canvas.drawString(LMARGIN + 18 * mm, PAGE_H - 10 * mm, "验证报告")
        canvas.drawCentredString(PAGE_W / 2 - 40 * mm, PAGE_H - 10 * mm, info["验证对象"])
        canvas.drawCentredString(PAGE_W / 2 - 5 * mm, PAGE_H - 10 * mm, info["编号"])
        canvas.drawCentredString(PAGE_W / 2 + 30 * mm, PAGE_H - 10 * mm, info["装载类型"])
        canvas.drawRightString(PAGE_W - RMARGIN, PAGE_H - 10 * mm, f"页码：{doc.page} / {total_pages}")
        canvas.setStrokeColor(colors.grey)
        canvas.line(LMARGIN, PAGE_H - 12 * mm, PAGE_W - RMARGIN, PAGE_H - 12 * mm)
        canvas.restoreState()

    def draw_p1_footer(canvas):
        canvas.saveState()
        y = BMARGIN + 8 * mm; w = usable_w / 8
        row = ["验证人：", "", "签字日期：", "", "审核人：", "", "签字日期：", ""]
        for i, txt in enumerate(row):
            x = LMARGIN + i * w
            if i % 2 == 0:
                canvas.setFillColor(gray()); canvas.rect(x, y, w, 7 * mm, fill=1, stroke=1)
                canvas.setFillColor(colors.black); canvas.setFont(FONT, 9)
                canvas.drawString(x + 2 * mm, y + 2 * mm, txt)
            else:
                canvas.rect(x, y, w, 7 * mm, fill=0, stroke=1)
        canvas.restoreState()

    # 首页
    def create_front_page():
        story = []
        story.append(Spacer(1, 6 * mm))
        title_table = Table([[p("验证报告", size=14, bold=True, align=TA_CENTER)]], colWidths=[usable_w])
        title_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_B), ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), gray()), ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
        story.append(title_table); story.append(Spacer(1, 1 * mm))
        col_w = usable_w / 8
        info_rows = [
            [p("装载类型：", size=8), p(info["装载类型"], size=8), p("公司名称：", size=8), p(info["公司名称"], size=8), p("", size=8), p("", size=8), p("", size=8), p("", size=8)],
            [p("验证报告编号：", size=8), p(info["验证报告编号"], size=8), p("", size=8), p("", size=8), p("", size=8), p("", size=8), p("", size=8), p("", size=8)],
            [p("校准报告编号：", size=8), p(info["校准报告编号"], size=8), p("", size=8), p("", size=8), p("", size=8), p("", size=8), p("", size=8), p("", size=8)],
            [p("验证对象：", size=8), p(info["验证对象"], size=8), p("型号：", size=8), p(info["型号"], size=8), p("编号：", size=8), p(info["编号"], size=8), p("备注：", size=8), p(info["备注"], size=8)],
            [p("验证仪器：", size=8), p(info["验证仪器"], size=8), p("型号：", size=8), p(info["仪器型号"], size=8), p("编号：", size=8), p(info["仪器编号"], size=8), p("简称：", size=8), p(info["简称"], size=8)],
            [p("SOP：", size=8), p(info["SOP"], size=8), p("扫描间隔(秒)：", size=8), p(info["扫描间隔"], size=8), p("记录间隔(秒)：", size=8), p(info["记录间隔"], size=8), p("", size=8), p("", size=8)],
            [p("探头数量：", size=8), p(info["探头数量"], size=8), p("压力探头：", size=8), p(info["压力探头"], size=8), p("验证类型：", size=8), p(info["验证类型"], size=8), p("", size=8), p("", size=8)],
            [p("工艺时间段<br/>（标:上:下）", size=8), p("%.0f:%.0f:%.0f" % (T_TARGET, T_HIGH, T_LOW), size=8), p("压力要求：", size=8), p(info["压力要求"], size=8), p("时长要求(分钟)：", size=8), p(info["时长要求"], size=8), p("", size=8), p("", size=8)],
        ]
        info_table = Table(info_rows, colWidths=[col_w] * 8)
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT), ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEADING', (0, 0), (-1, -1), 10), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('TOPPADDING', (0, 0), (-1, -1), 1.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1.5), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, 0), gray()), ('BACKGROUND', (2, 0), (2, 0), gray()),
            ('BACKGROUND', (0, 1), (0, 1), gray()), ('BACKGROUND', (0, 2), (0, 2), gray()),
            ('BACKGROUND', (0, 3), (0, 3), gray()), ('BACKGROUND', (2, 3), (2, 3), gray()),
            ('BACKGROUND', (4, 3), (4, 3), gray()), ('BACKGROUND', (6, 3), (6, 3), gray()),
            ('BACKGROUND', (0, 4), (0, 4), gray()), ('BACKGROUND', (2, 4), (2, 4), gray()),
            ('BACKGROUND', (4, 4), (4, 4), gray()), ('BACKGROUND', (6, 4), (6, 4), gray()),
            ('BACKGROUND', (0, 5), (0, 5), gray()), ('BACKGROUND', (2, 5), (2, 5), gray()),
            ('BACKGROUND', (4, 5), (4, 5), gray()), ('BACKGROUND', (0, 6), (0, 6), gray()),
            ('BACKGROUND', (2, 6), (2, 6), gray()), ('BACKGROUND', (4, 6), (4, 6), gray()),
            ('BACKGROUND', (0, 7), (0, 7), gray()), ('BACKGROUND', (2, 7), (2, 7), gray()),
            ('BACKGROUND', (4, 7), (4, 7), gray()),
            ('SPAN', (1, 0), (1, 0)), ('SPAN', (3, 0), (7, 0)),
            ('SPAN', (1, 1), (7, 1)), ('SPAN', (1, 2), (7, 2))]))
        story.append(info_table); story.append(Spacer(1, 1 * mm))
        note_table = Table([[p("注释：", size=8)]], colWidths=[usable_w])
        note_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT), ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('BACKGROUND', (0, 0), (-1, -1), gray()),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey)]))
        story.append(note_table); story.append(Spacer(1, 1 * mm))

        concl_text = "符合要求" if is_ok else "不符合要求"
        range_text = f"符合{T_LOW:.0f}到{T_HIGH:.0f}之间" if within else f"不符合{T_LOW:.0f}到{T_HIGH:.0f}之间"
        flu_half_max_c = max(probe_cols, key=lambda c: stats[c]["波动度"])
        flu_hi_max_c = max(probe_cols, key=lambda c: stats[c]["最大减平均"])
        flu_lo_max_c = max(probe_cols, key=lambda c: stats[c]["平均减最小"])
        hot_c = max(probe_cols, key=lambda c: stats[c]["avg"])
        cold_c = min(probe_cols, key=lambda c: stats[c]["avg"])
        max_temp_c = max(probe_cols, key=lambda c: stats[c]["max"])
        min_temp_c = min(probe_cols, key=lambda c: stats[c]["min"])
        concl_body = (
            f"工艺要求：温度{T_TARGET:.0f}℃，时长 {fmt_dhms(HOLD_MIN_MIN)}。温度要求:{T_LOW:.0f}到{T_HIGH:.0f}之间。<br/>"
            f"1、 工艺时长实际{fmt_dhms(dur_min)} ，{concl_text}。<br/>"
            f"2、 在工艺时间段内温度结论：<br/>"
            f"（1）温度范围： 最高温度是{channel_of[max_temp_c]}={gmax:.2f}℃，"
            f"最低温度是{channel_of[min_temp_c]}={gmin:.2f}℃，"
            f"平均温度是{gavg:.2f}℃，{range_text}。<br/>"
            f"（2）最冷和最热点：平均温度最大的是{channel_of[hot_c]}={stats[hot_c]['avg']:.2f}，可能是本次验证的最热点。<br/>"
            f"平均温度最小的是{channel_of[cold_c]}={stats[cold_c]['avg']:.2f}，可能是本次验证的最冷点。<br/>"
            f"（3）整体温度均匀度={std:.2f}℃,同一时刻的温度均匀性：<br/>"
            f"Max(最大-最小)={max_span:.2f}℃ （{fmt_dt(max_span_t, date_str)}）<br/>"
            f"Max(最大-平均)={max_dev_hi:.2f}℃ （{fmt_dt(max_dev_hi_t, date_str)}）<br/>"
            f"Max(平均-最小)={max_dev_lo:.2f}℃ （{fmt_dt(max_dev_lo_t, date_str)}）<br/>"
            f"（4）时间段内每个探头自己的温度波动度：<br/>"
            f"Max[(最大-最小)/2]={stats[flu_half_max_c]['波动度']:.2f}℃是{channel_of[flu_half_max_c]}号探头<br/>"
            f"Max(最大-平均)={stats[flu_hi_max_c]['最大减平均']:.2f}℃是{channel_of[flu_hi_max_c]}号探头<br/>"
            f"Max(平均-最小)={stats[flu_lo_max_c]['平均减最小']:.2f}℃是{channel_of[flu_lo_max_c]}号探头"
        )
        left_w = 28 * mm; right_w = usable_w - left_w
        concl_table = Table([[p("结论一：工艺<br/>时间段", size=8, bold=True, align=TA_CENTER),
                              p(concl_body, size=8, align=TA_LEFT)]], colWidths=[left_w, right_w])
        concl_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT), ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEADING', (0, 0), (-1, -1), 11), ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), gray()), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey)]))
        story.append(concl_table)
        return story

    def create_probe_page():
        story = []
        story.append(Spacer(1, 6 * mm))
        title = Table([[p("探头定义", size=14, bold=True, align=TA_CENTER)]], colWidths=[usable_w])
        title.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_B), ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), gray()), ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
        story.append(title); story.append(Spacer(1, 2 * mm))
        sub = Table([[p(info["简称"], size=10, bold=True, align=TA_CENTER)]], colWidths=[usable_w])
        sub.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT_B), ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), gray()), ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
        story.append(sub)
        rows = [[p("通道", size=9, bold=True), p("标签", size=9, bold=True)]]
        for c in probe_cols:
            rows.append([p(channel_of[c], size=9), p(tag_of[c], size=9)])
        table = Table(rows, colWidths=[usable_w / 2] * 2)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT), ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEADING', (0, 0), (-1, -1), 12), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey), ('BACKGROUND', (0, 0), (-1, 0), gray())]))
        story.append(table)
        return story

    def create_layout_page():
        story = []
        story.append(Spacer(1, 6 * mm))
        story.append(p("布点图", size=14, bold=True, align=TA_CENTER))
        story.append(Spacer(1, 4 * mm))
        story.append(Image(layout_path, width=usable_w * 0.75, height=usable_w * 0.32))
        return story

    def create_trend_page():
        story = []
        story.append(Spacer(1, 6 * mm))
        story.append(Image(trend_path, width=usable_w, height=usable_w * 0.32))
        return story

    def create_stats_page():
        story = []
        story.append(Spacer(1, 6 * mm))
        story.append(p("温度阶段统计 工艺时间段:%s~~%s" % (raw_times[0], raw_times[-1]),
                       size=12, bold=True, align=TA_CENTER))
        story.append(Spacer(1, 3 * mm))
        header = ["探头"] + [channel_of[c] for c in probe_cols]
        rows = [header]
        for key, label in [("min", "最小值"), ("max", "最大值"), ("range", "大减小"),
                           ("avg", "平均值"), ("dev", "平减标")]:
            row = [label]
            for c in probe_cols:
                v = stats[c][key]
                row.append("%.4f" % v if key == "avg" else "%.2f" % v)
            rows.append(row)

        def rank_parts(key, reverse=False, fmt="%.2f"):
            ordered = sorted(probe_cols, key=lambda c: stats[c][key], reverse=reverse)
            parts = []
            for i, c in enumerate(ordered):
                if i > 0:
                    parts.append("<" if not reverse else ">")
                parts.append("(%s=%s℃)" % (channel_of[c], fmt % stats[c][key]))
            return "".join(parts)

        rank_defs = [
            ("每个探头的最小值排序(由小到大):", "min", False, "%.2f"),
            ("每个探头的最大值排序(由大到小):", "max", True, "%.2f"),
            ("每个探头的波动度排序(由大到小)(也就是(本时间段内每一个探头本身的最大值-最小值)/2 进行排序):", "波动度", True, "%.2f"),
            ("每个探头的平均值排序(由大到小):", "avg", True, "%.4f"),
            ("每个探头的平均值分别减标准工艺温度的差排序(由大到小):", "dev", True, "%.2f"),
        ]
        for title, key, rev, fmt in rank_defs:
            rows.append([title] + [""] * N)
            rows.append([rank_parts(key, rev, fmt)] + [""] * N)

        rows_p = [[p(x, size=8) for x in row] for row in rows]
        table = Table(rows_p, colWidths=[usable_w / (N + 1)] * (N + 1))
        style = [
            ('FONTNAME', (0, 0), (-1, -1), FONT), ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEADING', (0, 0), (-1, -1), 10), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), gray()), ('BACKGROUND', (0, 1), (0, 5), gray())]
        for k in range(5):
            title_i = 6 + k * 2; expr_i = title_i + 1
            style.append(('SPAN', (0, title_i), (-1, title_i)))
            style.append(('SPAN', (0, expr_i), (-1, expr_i)))
            style.append(('BACKGROUND', (0, title_i), (-1, title_i), gray()))
            style.append(('ALIGN', (0, title_i), (-1, title_i), 'LEFT'))
            style.append(('ALIGN', (0, expr_i), (-1, expr_i), 'LEFT'))
        table.setStyle(TableStyle(style))
        story.append(table)
        return story

    def create_uniformity_page():
        story = []
        story.append(Spacer(1, 6 * mm))
        hot_c = max(probe_cols, key=lambda c: stats[c]["avg"])
        cold_c = min(probe_cols, key=lambda c: stats[c]["avg"])
        col_w = usable_w / 6
        rows = [
            [p("同一时刻的温度均匀性：", size=9, align=TA_LEFT), "", "", "", "", ""],
            [p(f"Max(最大-最小)={max_span:.2f} （{fmt_dt(max_span_t, date_str)}）", size=9, align=TA_LEFT), "", "", "", "", ""],
            [p(f"Max(最大-平均)={max_dev_hi:.2f} （{fmt_dt(max_dev_hi_t, date_str)}）", size=9, align=TA_LEFT), "", "", "", "", ""],
            [p(f"Max(平均-最小)={max_dev_lo:.2f} （{fmt_dt(max_dev_lo_t, date_str)}）", size=9, align=TA_LEFT), "", "", "", "", ""],
            [p("全均℃：", size=9, bold=True), p("%.4f" % gavg, size=9),
             p("最大均-全均℃：", size=9, bold=True), p("%.4f" % (stats[hot_c]["avg"] - gavg), size=9),
             p("全均-最小均℃：", size=9, bold=True), p("%.4f" % (gavg - stats[cold_c]["avg"]), size=9)],
        ]
        tbl = Table(rows, colWidths=[col_w] * 6)
        tbl.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT), ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEADING', (0, 0), (-1, -1), 11), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, 3), 'LEFT'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (5, 0)), ('SPAN', (0, 1), (5, 1)), ('SPAN', (0, 2), (5, 2)), ('SPAN', (0, 3), (5, 3)),
            ('BACKGROUND', (0, 4), (0, 4), gray()), ('BACKGROUND', (2, 4), (2, 4), gray()),
            ('BACKGROUND', (4, 4), (4, 4), gray()),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), ('BOX', (0, 0), (-1, -1), 0.5, colors.black)]))
        story.append(tbl)
        return story

    def create_detail_pages():
        story = []
        story.append(Spacer(1, 6 * mm))
        story.append(p("温度数据", size=12, bold=True, align=TA_CENTER))
        story.append(Spacer(1, 3 * mm))
        header = ["时间"] + [channel_of[c] for c in probe_cols]
        rows = [header]
        for i, t in enumerate(times):
            row = [raw_times[i]] + ["%.2f" % data[c][i] for c in probe_cols]
            rows.append(row)
        rows_p = [[p(x, size=8) for x in row] for row in rows]
        table = Table(rows_p, colWidths=[usable_w / (N + 1)] * (N + 1), repeatRows=1)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT), ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('LEADING', (0, 0), (-1, -1), 10), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey), ('BACKGROUND', (0, 0), (-1, 0), gray())]))
        story.append(table)
        return story

    def create_sign_page():
        story = []
        story.append(Spacer(1, 6 * mm))
        row_w = usable_w / 8
        table = Table([[p("验证人：", size=9, bold=True), p("", size=9),
                        p("签字日期：", size=9, bold=True), p("", size=9),
                        p("审核人：", size=9, bold=True), p("", size=9),
                        p("签字日期：", size=9, bold=True), p("", size=9)]],
                      colWidths=[row_w] * 8, rowHeights=[12 * mm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), FONT), ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('BACKGROUND', (0, 0), (0, 0), gray()), ('BACKGROUND', (2, 0), (2, 0), gray()),
            ('BACKGROUND', (4, 0), (4, 0), gray()), ('BACKGROUND', (6, 0), (6, 0), gray()),
            ('LINEBELOW', (1, 0), (1, 0), 0.5, colors.black), ('LINEBELOW', (3, 0), (3, 0), 0.5, colors.black),
            ('LINEBELOW', (5, 0), (5, 0), 0.5, colors.black), ('LINEBELOW', (7, 0), (7, 0), 0.5, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.grey), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
        story.append(table)
        return story

    def create_story(total_pages=1):
        story = create_front_page()
        story.append(PageBreak())
        story.extend(create_probe_page()); story.append(PageBreak())
        story.extend(create_trend_page()); story.append(PageBreak())
        story.extend(create_stats_page()); story.append(PageBreak())
        story.extend(create_uniformity_page()); story.append(PageBreak())
        story.extend(create_detail_pages()); story.append(PageBreak())
        story.extend(create_sign_page())
        return story

    def build(path, total_pages):
        doc = SimpleDocTemplate(path, pagesize=landscape(A4),
                                leftMargin=LMARGIN, rightMargin=RMARGIN,
                                topMargin=TMARGIN, bottomMargin=BMARGIN)
        def on_page(canvas, doc):
            make_header(canvas, doc, total_pages)
            if doc.page == 1:
                draw_p1_footer(canvas)
        doc.build(create_story(total_pages), onFirstPage=on_page, onLaterPages=on_page)

    build(out_path, 1)
    tmp = pymupdf.open(out_path); total = len(tmp); tmp.close()
    build(out_path, total)

    for fp in (trend_path, layout_path):
        try: os.remove(fp)
        except OSError: pass
    return out_path


# ============ HTML 生成 ============
def build_html(out_path, info, ctx, raw_times, times, data, channel_of, tag_of, stats,
               T_TARGET, T_LOW, T_HIGH, HOLD_MIN_MIN):
    N = ctx["N"]; M = ctx["M"]
    gmin, gmax, gavg, std = ctx["gmin"], ctx["gmax"], ctx["gavg"], ctx["std"]
    max_span, max_span_t = ctx["max_span"], ctx["max_span_t"]
    max_dev_hi, max_dev_hi_t = ctx["max_dev_hi"], ctx["max_dev_hi_t"]
    max_dev_lo, max_dev_lo_t = ctx["max_dev_lo"], ctx["max_dev_lo_t"]
    dur_min, within, is_ok = ctx["dur_min"], ctx["within"], ctx["is_ok"]
    probe_cols = list(channel_of.keys())
    date_str = info["日期"]

    trend_buf = draw_trend(times, data, probe_cols, channel_of, T_TARGET, T_LOW, T_HIGH, dur_min)
    trend_b64 = base64.b64encode(trend_buf.getvalue()).decode()

    hot_c = max(probe_cols, key=lambda c: stats[c]["avg"])
    cold_c = min(probe_cols, key=lambda c: stats[c]["avg"])
    max_temp_c = max(probe_cols, key=lambda c: stats[c]["max"])
    min_temp_c = min(probe_cols, key=lambda c: stats[c]["min"])
    flu_half = max(probe_cols, key=lambda c: stats[c]["波动度"])
    flu_hi = max(probe_cols, key=lambda c: stats[c]["最大减平均"])
    flu_lo = max(probe_cols, key=lambda c: stats[c]["平均减最小"])
    concl_text = "符合要求" if is_ok else "不符合要求"
    range_text = f"符合{T_LOW:.0f}到{T_HIGH:.0f}之间" if within else f"不符合{T_LOW:.0f}到{T_HIGH:.0f}之间"

    header_html = (f'<div class="header"><span>SiNSE</span><span>验证报告</span>'
                   f'<span>{info["验证对象"]}</span><span>{info["编号"]}</span>'
                   f'<span>{info["装载类型"]}</span>'
                   f'<span class="pg">页码：PAGE / TOTAL</span></div>')

    info_rows = [
        ['装载类型：', info['装载类型'], '公司名称：', info['公司名称'], '', '', '', ''],
        ['验证报告编号：', info['验证报告编号'], '', '', '', '', '', ''],
        ['校准报告编号：', info['校准报告编号'], '', '', '', '', '', ''],
        ['验证对象：', info['验证对象'], '型号：', info['型号'], '编号：', info['编号'], '备注：', info['备注']],
        ['验证仪器：', info['验证仪器'], '型号：', info['仪器型号'], '编号：', info['仪器编号'], '简称：', info['简称']],
        ['SOP：', info['SOP'], '扫描间隔(秒)：', info['扫描间隔'], '记录间隔(秒)：', info['记录间隔'], '', ''],
        ['探头数量：', info['探头数量'], '压力探头：', info['压力探头'], '验证类型：', info['验证类型'], '', ''],
        ['工艺时间段（标:上:下）', f"{T_TARGET:.0f}:{T_HIGH:.0f}:{T_LOW:.0f}", '压力要求：', info['压力要求'], '时长要求(分钟)：', info['时长要求'], '', ''],
    ]
    gray_cells = {(0,0),(2,0),(0,1),(0,2),(0,3),(2,3),(4,3),(6,3),(0,4),(2,4),(4,4),(6,4),
                  (0,5),(2,5),(4,5),(0,6),(2,6),(4,6),(0,7),(2,7),(4,7)}
    info_td = []
    for r, row in enumerate(info_rows):
        tds = []
        for c, txt in enumerate(row):
            cls = ' class="gray"' if (r, c) in gray_cells else ''
            tds.append(f'<td{cls}>{txt}</td>')
        info_td.append('<tr>' + ''.join(tds) + '</tr>')
    info_table = '<table class="info">' + ''.join(info_td) + '</table>'

    concl_body = (f"工艺要求：温度{T_TARGET:.0f}℃，时长 {fmt_dhms(HOLD_MIN_MIN)}。温度要求:{T_LOW:.0f}到{T_HIGH:.0f}之间。<br>"
                  f"1、 工艺时长实际{fmt_dhms(dur_min)} ，{concl_text}。<br>"
                  f"2、 在工艺时间段内温度结论：<br>"
                  f"（1）温度范围： 最高温度是{channel_of[max_temp_c]}={gmax:.2f}℃，"
                  f"最低温度是{channel_of[min_temp_c]}={gmin:.2f}℃，"
                  f"平均温度是{gavg:.2f}℃，{range_text}。<br>"
                  f"（2）最冷和最热点：平均温度最大的是{channel_of[hot_c]}={stats[hot_c]['avg']:.2f}，可能是本次验证的最热点。<br>"
                  f"平均温度最小的是{channel_of[cold_c]}={stats[cold_c]['avg']:.2f}，可能是本次验证的最冷点。<br>"
                  f"（3）整体温度均匀度={std:.2f}℃,同一时刻的温度均匀性：<br>"
                  f"Max(最大-最小)={max_span:.2f}℃ （{fmt_dt(max_span_t, date_str)}）<br>"
                  f"Max(最大-平均)={max_dev_hi:.2f}℃ （{fmt_dt(max_dev_hi_t, date_str)}）<br>"
                  f"Max(平均-最小)={max_dev_lo:.2f}℃ （{fmt_dt(max_dev_lo_t, date_str)}）<br>"
                  f"（4）时间段内每个探头自己的温度波动度：<br>"
                  f"Max[(最大-最小)/2]={stats[flu_half]['波动度']:.2f}℃是{channel_of[flu_half]}号探头<br>"
                  f"Max(最大-平均)={stats[flu_hi]['最大减平均']:.2f}℃是{channel_of[flu_hi]}号探头<br>"
                  f"Max(平均-最小)={stats[flu_lo]['平均减最小']:.2f}℃是{channel_of[flu_lo]}号探头")

    probe_rows = ''.join(f'<tr><td>{channel_of[c]}</td><td>{tag_of[c]}</td></tr>' for c in probe_cols)

    stat_keys = [("min", "最小值"), ("max", "最大值"), ("range", "大减小"), ("avg", "平均值"), ("dev", "平减标")]
    def fmtv(key, v):
        return f"{v:.4f}" if key == "avg" else f"{v:.2f}"
    stat_head = '<tr><th>探头</th>' + ''.join(f'<th>{channel_of[c]}</th>' for c in probe_cols) + '</tr>'
    stat_body = ''
    for key, label in stat_keys:
        cells = ''.join(f'<td>{fmtv(key, stats[c][key])}</td>' for c in probe_cols)
        stat_body += f'<tr><td class="gray">{label}</td>{cells}</tr>'

    def rank_rows(title, key, reverse=False, fmt="%.2f"):
        ordered = sorted(probe_cols, key=lambda c: stats[c][key], reverse=reverse)
        parts = []
        for i, c in enumerate(ordered):
            if i > 0:
                parts.append("<" if not reverse else ">")
            parts.append(f"({channel_of[c]}={fmt % stats[c][key]}℃)")
        col_n = N + 1
        return (f'<tr><td class="gray rank-title" colspan="{col_n}">{title}</td></tr>'
                f'<tr><td class="rank-expr" colspan="{col_n}">{"".join(parts)}</td></tr>')

    rank_sections = (
        rank_rows("每个探头的最小值排序(由小到大):", "min") +
        rank_rows("每个探头的最大值排序(由大到小):", "max", True) +
        rank_rows("每个探头的波动度排序(由大到小)(也就是(本时间段内每一个探头本身的最大值-最小值)/2 进行排序):", "波动度", True) +
        rank_rows("每个探头的平均值排序(由大到小):", "avg", True, "%.4f") +
        rank_rows("每个探头的平均值分别减标准工艺温度的差排序(由大到小):", "dev", True, "%.2f")
    )

    uniform_html = (
        f'<table class="uni"><tr><td class="span" colspan="6">同一时刻的温度均匀性：</td></tr>'
        f'<tr><td class="span" colspan="6">Max(最大-最小)={max_span:.2f} （{fmt_dt(max_span_t, date_str)}）</td></tr>'
        f'<tr><td class="span" colspan="6">Max(最大-平均)={max_dev_hi:.2f} （{fmt_dt(max_dev_hi_t, date_str)}）</td></tr>'
        f'<tr><td class="span" colspan="6">Max(平均-最小)={max_dev_lo:.2f} （{fmt_dt(max_dev_lo_t, date_str)}）</td></tr>'
        f'<tr><td class="gray">全均℃：</td><td>{gavg:.4f}</td>'
        f'<td class="gray">最大均-全均℃：</td><td>{stats[hot_c]["avg"] - gavg:.4f}</td>'
        f'<td class="gray">全均-最小均℃：</td><td>{gavg - stats[cold_c]["avg"]:.4f}</td></tr></table>'
    )

    detail_head = '<tr><th>时间</th>' + ''.join(f'<th>{channel_of[c]}</th>' for c in probe_cols) + '</tr>'
    detail_body = ''.join(
        f'<tr><td>{raw_times[i]}</td>' + ''.join(f'<td>{data[c][i]:.2f}</td>' for c in probe_cols) + '</tr>'
        for i in range(M))

    FOOTER = ('<table class="signrow"><tr>'
              '<td class="gray">验证人：</td><td></td>'
              '<td class="gray">签字日期：</td><td></td>'
              '<td class="gray">审核人：</td><td></td>'
              '<td class="gray">签字日期：</td><td></td></tr></table>')

    PAGES = []
    PAGES.append(f'''{header_html}
<div class="title-bar">验证报告</div>
{info_table}
<div class="note-bar">注释：</div>
<table class="concl"><tr><td class="gray concl-l">结论一：工艺<br>时间段</td>
<td class="concl-r">{concl_body}</td></tr></table>
<div class="p1footer">{FOOTER}</div>''')
    PAGES.append(f'''{header_html}
<div class="title-bar">探头定义</div>
<div class="sub-bar">{info['简称']}</div>
<table class="probe"><tr><th>通道</th><th>标签</th></tr>{probe_rows}</table>''')
    PAGES.append(f'''{header_html}
<div class="chart-wrap"><img src="data:image/png;base64,{trend_b64}" style="width:100%;"></div>''')
    PAGES.append(f'''{header_html}
<div class="center-title">温度阶段统计 工艺时间段:{raw_times[0]}~~{raw_times[-1]}</div>
<table class="stat">{stat_head}{stat_body}{rank_sections}</table>''')
    PAGES.append(f'''{header_html}
{uniform_html}''')
    PAGES.append(f'''{header_html}
<div class="center-title">温度数据</div>
<table class="detail"><tr>{detail_head}</tr>{detail_body}</table>''')
    PAGES.append(f'''{header_html}
{FOOTER}''')

    TOTAL = len(PAGES)
    pages_html = ''.join(f'<div class="page" data-pg="{i+1}">{p}</div>' for i, p in enumerate(PAGES))

    CSS = '''
* { box-sizing: border-box; }
body { font-family: "Microsoft YaHei","微软雅黑",sans-serif; margin:0; background:#cfcfcf; color:#000; }
.page { width:297mm; height:210mm; background:#fff; margin:8mm auto; padding:14mm 12mm 12mm 12mm;
        position:relative; box-shadow:0 0 6px rgba(0,0,0,.35); overflow:hidden; }
@media print { body{background:#fff;} .page{margin:0;box-shadow:none;page-break-after:always;} }
.header { display:flex; justify-content:space-between; font-size:10.5pt; border-bottom:1px solid #888;
           padding-bottom:3px; margin-bottom:6px; }
.header .pg { font-weight:normal; }
.title-bar { background:#e7e6e6; text-align:center; font-size:14pt; font-weight:bold;
              padding:4px; border:1px solid #999; margin-bottom:3px; }
.sub-bar { background:#e7e6e6; text-align:center; font-size:10.5pt; font-weight:bold;
            padding:3px; border:1px solid #999; margin-top:2px; }
table { border-collapse:collapse; width:100%; font-size:9pt; }
th,td { border:1px solid #999; padding:2px 4px; text-align:center; }
td.gray,th.gray,th { background:#e7e6e6; }
.note-bar { background:#e7e6e6; font-size:9pt; padding:2px 4px; border:1px solid #999; border-top:none; }
.info td { height:15px; }
.concl { margin-top:3px; }
.concl-l { width:30mm; font-weight:bold; font-size:9pt; vertical-align:middle; }
.concl-r { text-align:left; font-size:9pt; line-height:1.4; padding:4px 6px; }
.p1footer { position:absolute; left:12mm; right:12mm; bottom:12mm; }
.signrow td { height:9mm; }
.chart-wrap { text-align:center; margin-top:6mm; }
.center-title { text-align:center; font-size:12pt; font-weight:bold; margin:4px 0; }
.rank-title { text-align:left; font-size:9pt; }
.rank-expr { text-align:left; font-size:9pt; line-height:1.5; }
.stat td, .stat th { border:1px solid #999; }
.uni { margin-top:8mm; }
.uni .span { text-align:left; }
.probe td, .probe th { padding:4px; }
.detail td, .detail th { padding:3px; }
@media print { .header{position:static;} }
'''
    HTML = f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>温度验证报告</title>
<style>{CSS}</style></head>
<body>{pages_html}
<script>
var total={TOTAL};
document.querySelectorAll('.page').forEach(function(pg){{
  var n=pg.getAttribute('data-pg');
  var el=pg.querySelector('.pg');
  if(el) el.textContent='页码：'+n+' / '+total;
}});
</script>
</body></html>'''
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(HTML)
    return out_path


# ============ 主流程 ============
def main():
    ap = argparse.ArgumentParser(description="温度验证报告生成器")
    ap.add_argument("--csv", required=True, help="CSV 数据路径")
    ap.add_argument("--format", choices=["pdf", "html", "both"], default="both", help="输出格式（默认 both）")
    ap.add_argument("--outdir", default=None, help="输出目录（默认 CSV 同目录）")
    ap.add_argument("--target", type=float, default=121.0, help="目标温度")
    ap.add_argument("--low", type=float, default=120.0, help="温度下限")
    ap.add_argument("--high", type=float, default=122.0, help="温度上限")
    ap.add_argument("--holdmin", type=float, default=15.0, help="保持分钟数")
    ap.add_argument("--info", default=None, help="INFO 覆盖 JSON 路径")
    for k in QUICK_KEYS:
        ap.add_argument("--" + k.replace(" ", "_"), default=None, help="覆盖 %s" % k)
    args = ap.parse_args()

    info = build_info(args)
    raw_times, times, data, probe_cols = load_csv(args.csv, info)
    ctx = compute(raw_times, times, data, probe_cols, info, args.target, args.low, args.high, args.holdmin)

    outdir = args.outdir or os.path.dirname(os.path.abspath(args.csv))
    os.makedirs(outdir, exist_ok=True)
    date_tag = info["日期"].replace("-", "")
    base = os.path.join(outdir, f"温度验证报告_{date_tag}")

    if args.format in ("pdf", "both"):
        pdf_path = base + ".pdf"
        build_pdf(pdf_path, info, ctx, raw_times, times, data, ctx["channel_of"], ctx["tag_of"],
                  ctx["stats"], args.target, args.low, args.high, args.holdmin)
        print("PDF 已生成:", pdf_path)
    if args.format in ("html", "both"):
        html_path = base + ".html"
        build_html(html_path, info, ctx, raw_times, times, data, ctx["channel_of"], ctx["tag_of"],
                   ctx["stats"], args.target, args.low, args.high, args.holdmin)
        print("HTML 已生成:", html_path)


if __name__ == "__main__":
    main()
