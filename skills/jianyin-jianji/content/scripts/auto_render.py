#!/usr/bin/env python3
"""批量视频渲染脚本
用法: python auto_render.py --input DIR --output DIR
"""
import argparse, os

def main():
    p = argparse.ArgumentParser(description="批量视频渲染")
    p.add_argument("--input",  default="~/.openclaw/jianyin-work/temp")
    p.add_argument("--output", default="~/.openclaw/output")
    p.add_argument("--tts",    default="~/.openclaw/jianyin-work/tts")
    p.add_argument("--music",  default="~/.openclaw/jianyin-work/music")
    p.add_argument("--subs",   default="~/.openclaw/jianyin-work/subs")
    args = p.parse_args()

    home = os.path.expanduser("~")
    for k in ["input","output","tts","music","subs"]:
        setattr(args, k, getattr(args,k).replace("~", home))

    os.makedirs(args.output, exist_ok=True)
    script = f"""#!/bin/bash
FFMPEG=ffmpeg
for video in "{args.input}"/*.mp4; do
    name=$(basename "$video" .mp4)
    voice="{args.tts}/${{name}}.mp3"
    bgm="{args.music}/bgm_default.mp3"
    sub="{args.subs}/${{name}}.ass"
    out="{args.output}/${{name}}_final.mp4"
    if [ -f "$voice" ] && [ -f "$bgm" ]; then
        $FFMPEG -y -i "$video" -i "$voice" -i "$bgm" \
          -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.4[bgm];[voice][bgm]amix=inputs=2:duration=first[aout]" \
          -map 0:v -map "[aout]" -c:v libx264 -crf 20 -preset fast "$out"
        [ -f "$sub" ] && $FFMPEG -y -i "$out" -vf "ass=$sub" "$out"
    else
        $FFMPEG -y -i "$video" -c:v libx264 -crf 20 "$out"
    fi
    echo "Done: $name"
done
echo "All done -> {args.output}"
"""
    path = os.path.join(args.output, "batch_render.sh")
    with open(path,"w") as f: f.write(script)
    os.chmod(path, 0o755)
    print(f"Render script: {path}")

if __name__ == "__main__":
    main()
