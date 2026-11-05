#!/usr/bin/env python3
"""
Image Gallery Sender - 生成图片画廊并发送链接
用法: python3 send_gallery.py [图片路径1] [图片路径2] ... [--title 标题] [--name 项目名]
"""
import os, subprocess, shutil, time, argparse

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
*{{box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;background:#0f1724;margin:0;padding:0;color:#e2e8f0}}
.header{{text-align:center;padding:40px 20px 30px;background:linear-gradient(135deg,#1a1a2e,#16213e)}}
.header h1{{margin:0;font-size:22px;color:#ffd700;letter-spacing:1px}}
.header p{{margin:10px 0 0;color:#94a3b8;font-size:13px}}
.tip{{text-align:center;color:#64748b;font-size:13px;padding:12px 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;padding:20px;max-width:1200px;margin:0 auto}}
.card{{background:#1e293b;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.4);transition:transform 0.2s}}
.card:hover{{transform:translateY(-4px)}}
.card img{{width:100%;height:380px;object-fit:cover;display:block}}
.card .label{{padding:12px 16px;font-size:13px;color:#cbd5e1;background:#1e293b;border-top:1px solid #334155}}
.footer{{text-align:center;padding:30px;color:#475569;font-size:12px}}
</style>
</head>
<body>
<div class="header">
  <h1>{emoji} {title}</h1>
  {desc_html}
</div>
<p class="tip">👆 长按或点击图片即可保存到手机</p>
<div class="grid">
{cards}
</div>
<div class="footer">{count} 张图片 · AI 助理生成</div>
</body>
</html>"""

def build_gallery(images, title, description, emoji="🖼️"):
    cards = ""
    for i, img in enumerate(images):
        num = f"0{i+1}" if i < 9 else str(i+1)
        fname = os.path.basename(img)
        cards += f'<div class="card"><img src="{fname}" alt="图{num}"><div class="label">图{num}</div></div>\n'
    desc_html = f'<p style="margin:10px 0 0;color:#94a3b8;font-size:13px">{description}</p>' if description else ""
    return HTML_TEMPLATE.format(
        title=title, emoji=emoji, desc_html=desc_html,
        cards=cards, count=len(images)
    )

def send_via_message_tool(link, title, wechat_id):
    msg = f"🖼️ {title}\n\n👆 点击链接 → 长按图片即可保存\n{link}"
    r = subprocess.run(
        ["bash", "-c",
         f'message --action send --channel openclaw-weixin '
         f'--to "{wechat_id}" --message "{msg}"'],
        capture_output=True, text=True, timeout=20
    )
    return r.returncode == 0

def send_images_one_by_one(images, title, wechat_id, interval=4):
    """降级方案：逐张发送图片"""
    for i, img in enumerate(images):
        num = f"0{i+1}" if i < 9 else str(i+1)
        label = f"图{num}"
        r = subprocess.run(
            ["bash", "-c",
             f'message --action send --channel openclaw-weixin '
             f'--to "{wechat_id}" --message "{label}" --media "{img}"'],
            capture_output=True, text=True, timeout=20
        )
        print(f"  [{i+1}/{len(images)}] {'✅' if r.returncode==0 else '❌'} {label}")
        if i < len(images) - 1:
            time.sleep(interval)
    return True

def main():
    parser = argparse.ArgumentParser(description="图片画廊发送工具")
    parser.add_argument("images", nargs="+", help="图片绝对路径列表")
    parser.add_argument("--title", default="图片集", help="相册标题")
    parser.add_argument("--desc", default="长按图片即可保存", help="描述")
    parser.add_argument("--name", default="my-gallery", help="部署项目名")
    parser.add_argument("--wechat", default="", help="微信ID（留空则使用当前用户自己的微信）")
    parser.add_argument("--no-gallery", action="store_true", help="跳过画廊，直接逐张发图")
    args = parser.parse_args()

    title = args.title
    wechat_id = args.wechat.strip() if args.wechat.strip() else "self"

    print(f"[Image Gallery Sender]")
    print(f"  标题: {title}")
    print(f"  图片: {len(args.images)} 张")
    print(f"  微信: {wechat_id}")

    if args.no_gallery:
        send_images_one_by_one(args.images, title, wechat_id)
        return

    # 生成画廊
    tmp = f"/tmp/gallery_{os.getpid()}"
    os.makedirs(tmp, exist_ok=True)

    for src in args.images:
        if os.path.exists(src):
            shutil.copy2(src, f"{tmp}/{os.path.basename(src)}")
            print(f"  已复制: {os.path.basename(src)}")
        else:
            print(f"  ⚠️ 找不到: {src}")

    html = build_gallery(args.images, title, args.desc)
    with open(f"{tmp}/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    # 尝试部署
    deploy_url = None
    try:
        r = subprocess.run(
            ["npx", "--yes", "serveo-deploy", tmp, "--name", args.name],
            capture_output=True, text=True, timeout=60, cwd="/tmp"
        )
        if r.returncode == 0 and r.stdout:
            for line in r.stdout.strip().split("\n"):
                if "http" in line:
                    deploy_url = line.strip()
                    break
    except Exception as e:
        print(f"  部署尝试: {e}")

    # 发送
    if deploy_url:
        ok = send_via_message_tool(deploy_url, title, wechat_id)
        if ok:
            print(f"  ✅ 画廊链接已发送!")
            print(f"  🔗 {deploy_url}")
        else:
            print("  ⚠️ 发送失败，降级为逐张发送...")
            send_images_one_by_one(args.images, title, wechat_id)
    else:
        print("  ⚠️ 无法获取画廊链接，降级为逐张发送...")
        send_images_one_by_one(args.images, title, wechat_id)

    # 清理
    shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
