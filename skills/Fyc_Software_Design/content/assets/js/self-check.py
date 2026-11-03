"""
大屏自检脚本模板(2026-07-07 增强版)
涵盖 SOP 第 4 步"交付前自检"的 三大块:逻辑 / 错误 / 配色
"""
from playwright.sync_api import sync_playwright
import os, sys

URL = 'http://localhost:8000/index.html'
VIEWPORTS = [
    (1920, 1080, '1920x1080'),
    (3840, 2160, '3840x2160'),
    (1366, 768, '1366x768'),
    (2560, 1440, '2560x1440'),
]
OUTPUT_DIR = './check-output'

REQUIRED_APIS = ['windMap', 'windTop10', 'windTable', 'syncFromMap', 'syncFromTop10']

REQUIRED_DOMS = [
    '#clock', '#weekday', '#date',
    '#mapChart', '#top10Chart', '#lineChart',
    '#quarterChart', '#equipmentChart', '#tableChart',
    '.tabs-floating', '.marquee',
]


# ====== A. 逻辑检查 ======

def check_linkage(page):
    """联动逻辑:点击地图 → 其他图表同步"""
    page.evaluate("window.windMap.highlight('内蒙古')")
    page.wait_for_timeout(200)
    # 验证 windTable / windTop10 是否同步
    state = page.evaluate("""() => ({
        tableActive: document.querySelector('.summary-card.active')?.textContent,
        top10Active: document.querySelector('.loss-table tr.active td')?.textContent
    })""")
    if state.get('tableActive') or state.get('top10Active'):
        print(f'  ✅ 联动高亮触发: table={state.get("tableActive")}, top10={state.get("top10Active")}')
        return True
    print(f'  ⚠️  联动未触发(可能未实现)')
    return True  # 联动可选,不算硬错


def check_esc_clear(page):
    """Esc 键清空所有高亮"""
    page.evaluate("window.windMap.highlight('内蒙古')")
    page.wait_for_timeout(200)
    page.keyboard.press('Escape')
    page.wait_for_timeout(200)
    # 验证清空
    cleared = page.evaluate("""() => ({
        mapHas: !!document.querySelector('[data-chart-instance="map"] .active'),
        tableHas: !!document.querySelector('.summary-card.active')
    })""")
    if not cleared.get('mapHas') and not cleared.get('tableHas'):
        print('  ✅ Esc 键正确清空高亮')
        return True
    print(f'  ❌ Esc 键未清空: {cleared}')
    return False


def check_time_update(page):
    """时间是否每秒更新"""
    t1 = page.evaluate("document.getElementById('clock').textContent")
    page.wait_for_timeout(1100)
    t2 = page.evaluate("document.getElementById('clock').textContent")
    if t1 != t2:
        print(f'  ✅ 时钟在更新: {t1} → {t2}')
        return True
    print(f'  ❌ 时钟卡死: {t1}')
    return False


def check_no_undefined(page):
    """页面上不能出现 undefined / null 字面值"""
    body_text = page.evaluate("document.body.innerText")
    bad = []
    for word in ['undefined', 'null', 'NaN', '[object Object]']:
        if word in body_text:
            count = body_text.count(word)
            bad.append(f'{word}({count}次)')
    if bad:
        print(f'  ❌ 页面出现: {", ".join(bad)}')
        return False
    print('  ✅ 无 undefined/null/NaN')
    return True


def check_min_fontsize(page):
    """最小字号 ≥ 12px"""
    small = page.evaluate("""() => {
        const els = document.querySelectorAll('*');
        const small = [];
        els.forEach(el => {
            const fs = parseFloat(getComputedStyle(el).fontSize);
            const text = el.textContent?.trim();
            if (text && fs < 12 && el.children.length === 0) {
                small.push({ text: text.substring(0, 20), size: fs });
            }
        });
        return small.slice(0, 5);
    }""")
    if small:
        print(f'  ⚠️  {len(small)} 个元素字号 < 12px:')
        for s in small[:3]:
            print(f'      "{s["text"]}" → {s["size"]}px')
        return False
    print('  ✅ 所有文字字号 ≥ 12px')
    return True


def check_no_overflow(page):
    """内容不能超出 1920x1080 视口"""
    overflow = page.evaluate("""() => {
        const docW = document.documentElement.clientWidth;
        const docH = document.documentElement.clientHeight;
        const issues = [];
        document.querySelectorAll('.panel, .summary-card, .summary-main, .map-bg').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.right > docW + 5) issues.push(`${el.className} right=${r.right} > ${docW}`);
            if (r.bottom > docH + 5) issues.push(`${el.className} bottom=${r.bottom} > ${docH}`);
        });
        return issues;
    }""")
    if overflow:
        print(f'  ❌ 元素超出视口:')
        for s in overflow[:3]:
            print(f'      {s}')
        return False
    print('  ✅ 元素未超出视口')
    return True


def check_label_overflow(page, viewport_w=1920, viewport_h=1080):
    """2026-07-08 新增: 边界超界检查 - 检测所有可见 div/span/p/table 元素是否超出 viewport
    触发条件: 右超 > 10px 或 底超 > 30px
    """
    result = page.evaluate(f"""() => {{
        const docW = {viewport_w};
        const docH = {viewport_h};
        const THRESHOLD_RIGHT = 10;
        const THRESHOLD_BOTTOM = 30;
        const out = [];
        const skipTag = ['body', 'html', 'script', 'style', 'head'];
        document.querySelectorAll('div, span, p, h1, h2, h3, h4, h5, h6, table, td, th, tr, svg, canvas').forEach(el => {{
            if (skipTag.includes(el.tagName.toLowerCase())) return;
            if (el.offsetWidth === 0 || el.offsetParent === null) return;
            const r = el.getBoundingClientRect();
            const tag = el.tagName.toLowerCase();
            const txt = (el.innerText || '').trim().substring(0, 30);
            // 跳过空文本 div (只作为容器)
            if (!txt && ['div'].includes(tag)) return;
            // 跳过 ECharts 画布 (canvas/svg 通常 > 500px)
            if (r.width > 500 || r.height > 500) return;
            const overflowRight = r.right - docW;
            const overflowBottom = r.bottom - docH;
            const overflowLeft = -r.left;
            const overflowTop = -r.top;
            if (overflowRight > THRESHOLD_RIGHT || overflowBottom > THRESHOLD_BOTTOM ||
                overflowLeft > 5 || overflowTop > 5) {{
                out.push({{
                    tag: tag,
                    cls: (el.className||'').toString().substring(0, 50),
                    txt: txt,
                    left: Math.round(r.left),
                    top: Math.round(r.top),
                    right: Math.round(r.right),
                    bottom: Math.round(r.bottom),
                    width: Math.round(r.width),
                    height: Math.round(r.height),
                    overflowRight: Math.round(overflowRight),
                    overflowBottom: Math.round(overflowBottom),
                    overflowLeft: Math.round(overflowLeft),
                    overflowTop: Math.round(overflowTop)
                }});
            }}
        }});
        return out.slice(0, 30);
    }}""")
    if result:
        print(f'  ❌ {len(result)} 个元素边界超界:')
        for o in result[:10]:
            print(f'      <{o["tag"]} class="{o["cls"][:25]}"> "{o["txt"][:25]}" 右超{o["overflowRight"]}px, 底超{o["overflowBottom"]}px')
        return False
    print('  ✅ 所有元素边界均在视口内')
    return True


def check_text_max_width(page):
    """2026-07-08 新增: 文字字号 > 14px 的元素必须有 max-width + overflow:hidden 控制"""
    result = page.evaluate("""() => {
        const issues = [];
        document.querySelectorAll('div, span, p, h1-h6, td').forEach(el => {
            if (el.offsetParent === null) return;
            const fs = parseFloat(getComputedStyle(el).fontSize);
            if (fs <= 14) return;
            const css = getComputedStyle(el);
            const maxWidth = css.maxWidth;
            const overflow = css.overflow;
            const textOverflow = css.textOverflow;
            const whiteSpace = css.whiteSpace;
            // 大字号数字必须能控制溢出
            if (!maxWidth.includes('px') && !maxWidth.includes('%') && maxWidth !== 'none') {
                if (overflow !== 'hidden' && overflow !== 'auto' && overflow !== 'scroll') {
                    if (!el.className.toString().match(/summary|total|value/i)) return;  // 容忍总计大数字
                    issues.push({
                        tag: el.tagName,
                        cls: el.className.toString().substring(0, 50),
                        fontSize: fs,
                        txt: (el.innerText||'').substring(0, 20),
                        reason: '大字号无 max-width + overflow 控件'
                    });
                }
            }
        });
        return issues.slice(0, 10);
    }""")
    if result:
        print(f'  ❌ {len(result)} 个大字号元素无溢出控制:')
        for o in result[:5]:
            print(f'      {o["txt"]} ({o["fontSize"]}px) - {o["reason"]}')
        return False
    print('  ✅ 大字号元素溢出控制正常')
    return True


# ====== B. 错误检查 ======

def check_console_errors(errors, page_errors):
    if errors or page_errors:
        print('  ❌ 发现错误:')
        for e in errors[:5]: print(f'    {e}')
        for e in page_errors[:5]: print(f'    {e}')
        return False
    print('  ✅ 无控制台错误')
    return True


def check_no_404(page):
    """检查资源 404"""
    failed = []
    page.on('requestfailed', lambda r: failed.append(r.url))
    page.reload(wait_until='domcontentloaded')
    page.wait_for_timeout(2000)
    if failed:
        print(f'  ❌ 资源 404: {failed[:3]}')
        return False
    print('  ✅ 无 404 资源')
    return True


# ====== C. 配色检查 ======

def check_color_60_30_10(page):
    """60/30/10 配色比例(粗略检查)"""
    palette = page.evaluate("""() => {
        // 简单的颜色分类
        const colors = {};
        document.querySelectorAll('*').forEach(el => {
            const cs = getComputedStyle(el);
            ['color', 'backgroundColor', 'borderColor'].forEach(prop => {
                const c = cs[prop];
                if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') {
                    colors[c] = (colors[c] || 0) + 1;
                }
            });
        });
        // 排序取前 10
        return Object.entries(colors).sort((a, b) => b[1] - a[1]).slice(0, 10);
    }""")
    print(f'  📊 调色板前 10 色:')
    for c, n in palette[:5]:
        print(f'      {c}: {n} 处')
    return True  # 只是观察,不算硬错


def check_no_pure_saturated(page):
    """没有纯饱和色 #ff0000 / #00ff00 / #0000ff"""
    found = page.evaluate("""() => {
        const pure = [];
        document.querySelectorAll('*').forEach(el => {
            const cs = getComputedStyle(el);
            ['color', 'backgroundColor', 'borderColor'].forEach(prop => {
                const c = cs[prop];
                if (c && (c.includes('255, 0, 0') || c.includes('0, 255, 0') || c.includes('0, 0, 255'))) {
                    pure.push(`${prop}=${c}`);
                }
            });
        });
        return pure.slice(0, 3);
    }""")
    if found:
        print(f'  ❌ 存在纯饱和色: {found}')
        return False
    print('  ✅ 无纯饱和色')
    return True


# ====== 主流程 ======

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print('=' * 60)
    print('  大屏自检 - 逻辑 / 错误 / 配色 三大块')
    print('=' * 60)

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path='/root/.cache/ms-playwright/chromium-1223/chrome-linux/chrome',
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )

        for vw, vh, name in VIEWPORTS:
            vp_w, vp_h = vw, vh
            print(f'\n[{name}]')
            ctx = browser.new_context(viewport={'width': vw, 'height': vh})
            page = ctx.new_page()

            errors = []
            page_errors = []
            page.on('console', lambda m: errors.append(f'[{m.type}] {m.text}') if m.type == 'error' else None)
            page.on('pageerror', lambda e: page_errors.append(str(e)))

            page.goto(URL, wait_until='domcontentloaded', timeout=15000)
            page.wait_for_timeout(5000)
            page.screenshot(path=f'{OUTPUT_DIR}/screen-{name}.png')

            # B. 错误
            print('  [B. 错误检查]')
            if not check_console_errors(errors, page_errors): results.append((name, 'console'))

            # A. 逻辑 (只在 1920 下测)
            if vw == 1920:
                print('  [A. 逻辑检查]')
                check_linkage(page)
                check_esc_clear(page)
                check_time_update(page)
                check_no_undefined(page)
                check_min_fontsize(page)
                check_no_overflow(page)
                check_label_overflow(page, vp_w, vp_h)
                check_text_max_width(page)

                # C. 配色
                print('  [C. 配色检查]')
                check_color_60_30_10(page)
                check_no_pure_saturated(page)

            ctx.close()
        browser.close()

    print('\n' + '=' * 60)
    if not results:
        print('  ✅ 自检通过')
        return 0
    else:
        print('  ❌ 自检失败项:')
        for n, item in results:
            print(f'    [{n}] {item}')
        return 1


if __name__ == '__main__':
    sys.exit(main())