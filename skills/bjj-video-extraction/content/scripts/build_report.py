#!/usr/bin/env python3
"""把 Markdown 报告 + 图片目录 打包成单文件 HTML（图片内嵌为 data URI）

用法:
  python3 build_report.py report.md imgs_dir output.html [--title "标题"]

然后用 mcp_matrix_get_upload_url + curl PUT 上传，最后用本脚本 --verify 验证。
"""
import argparse, base64, os, re, sys

TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
*{{box-sizing:border-box}}
body{{margin:0;background:#0f1115;color:#e6e6e6;
 font:16px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;}}
.wrap{{max-width:880px;margin:0 auto;padding:48px 24px 120px}}
h1{{font-size:30px;line-height:1.35;margin:0 0 6px;color:#fff;letter-spacing:-.3px}}
h2{{font-size:23px;margin:52px 0 18px;padding-bottom:10px;border-bottom:2px solid #2a2f3a;color:#8ab4f8}}
h3{{font-size:19px;margin:38px 0 12px;color:#e8a0bf}}
h4{{font-size:16px;margin:26px 0 8px;color:#f0c674}}
p{{margin:14px 0}}
a{{color:#8ab4f8}}
hr{{border:0;border-top:1px solid #262b34;margin:44px 0}}
blockquote{{margin:20px 0;padding:14px 20px;border-left:4px solid #4a8fe7;
 background:#161b24;border-radius:0 6px 6px 0;color:#cfd6e0;font-style:italic}}
blockquote p{{margin:8px 0}}
ul,ol{{padding-left:26px;margin:14px 0}}
li{{margin:7px 0}}
strong{{color:#ffd479}}
code{{background:#1b2029;padding:2px 6px;border-radius:4px;font-size:90%;
 font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:#ffb4a2}}
pre{{background:#1b2029;padding:16px 18px;border-radius:8px;overflow-x:auto}}
pre code{{background:none;padding:0;color:#d6deeb}}
img{{max-width:100%;height:auto;display:block;margin:22px auto;
 border-radius:10px;border:1px solid #2a2f3a;background:#000}}
table{{border-collapse:collapse;width:100%;margin:24px 0;font-size:14.5px;display:block;overflow-x:auto}}
th,td{{border:1px solid #2a2f3a;padding:10px 13px;text-align:left;vertical-align:top}}
th{{background:#1b2029;color:#8ab4f8;font-weight:600;white-space:nowrap}}
tr:nth-child(even) td{{background:#141820}}
.meta{{color:#7d8794;font-size:13.5px;margin:0 0 8px;line-height:1.7}}
.badge{{display:inline-block;background:#1b2029;border:1px solid #2a2f3a;color:#8ab4f8;
 border-radius:20px;padding:3px 12px;font-size:12.5px;margin-right:8px;margin-bottom:8px}}
@media(max-width:600px){{.wrap{{padding:28px 16px 80px}}h1{{font-size:23px}}h2{{font-size:19px}}}}
</style></head><body><div class="wrap">
<div class="badge">BJJ</div>
{body}
</div></body></html>"""

IMG_EXT = (".jpg", ".jpeg", ".png", ".webp")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("markdown")
    ap.add_argument("imgdir")
    ap.add_argument("output")
    ap.add_argument("--title", default="")
    ap.add_argument("--verify", help="验证已下载的 html 文件")
    a = ap.parse_args()

    if a.verify:
        h = open(a.verify, encoding="utf-8", errors="replace").read()
        print("len:", len(h))
        print("doctype:", h.startswith("<!DOCTYPE html>"))
        print("closes html:", h.rstrip().endswith("</html>"))
        print("img tags:", h.count("<img"))
        print("data-uri imgs:", h.count("data:image/"))
        print("h2:", h.count("<h2>"), " tables:", h.count("<table>"),
              " blockquotes:", h.count("<blockquote>"))
        m = re.search(r"<h1>(.*?)</h1>", h, re.S)
        print("h1:", m.group(1) if m else "(none)")
        bad = 0
        for m in re.finditer(r"data:image/[^;]+;base64,([A-Za-z0-9+/=]+)", h):
            try: base64.b64decode(m.group(1))
            except Exception as e:
                print("BAD base64:", e); bad += 1
        print("base64 全部有效" if bad == 0 else f"{bad} 个损坏")
        sys.exit(1 if bad else 0)

    from markdown_it import MarkdownIt

    md = open(a.markdown, encoding="utf-8").read()
    n = 0
    for f in sorted(os.listdir(a.imgdir)):
        if not f.lower().endswith(IMG_EXT):
            continue
        b64 = base64.b64encode(open(os.path.join(a.imgdir, f), "rb").read()).decode()
        uri = f"data:image/jpeg;base64,{b64}"
        # 报告里的图片路径前缀千差万别（p1_final/x.jpg、imgs/x.jpg、./x.jpg），
        # 按「路径的任意前缀 + 文件名」统一替换，不能只匹配 imgdir/filename
        md = re.sub(r"\]\([^)]*?" + re.escape(f) + r"\)", f"]({uri})", md)
        md = md.replace(f"]({f})", f"]({uri})")
        n += 1

    left = [x for x in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", md)
            if not x.startswith("data:")]
    if left:
        print(f"FAIL: 未替换的图片引用: {left}", file=sys.stderr)
        sys.exit(1)

    body = MarkdownIt("commonmark", {"html": True}).enable("table").render(md)
    title = a.title or re.sub(r"^#\s*", "", md.split("\n")[0])[:60]
    html = TEMPLATE.format(title=title, body=body)
    open(a.output, "w", encoding="utf-8").write(html)

    size = os.path.getsize(a.output)
    print(f"内嵌 {n} 张图片")
    print(f"输出 {a.output}  {size} 字节")
    print(f"\n下一步 —— 上传时 size_bytes 必须填这个真实数字: {size}")


if __name__ == "__main__":
    main()
