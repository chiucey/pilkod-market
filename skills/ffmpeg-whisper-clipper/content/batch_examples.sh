#!/bin/bash
# FFmpeg Whisper 批量处理示例

# 示例1: 批量转录文件夹中的所有视频
transcribe_all() {
    local dir="$1"
    local model="${2:-base}"

    for file in "$dir"/*.mp4 "$dir"/*.avi "$dir"/*.mkv; do
        if [ -f "$file" ]; then
            echo "转录: $file"
            python clipper.py --model "$model" transcribe "$file"
        fi
    done
}

# 示例2: 批量关键词剪辑
clip_by_keyword() {
    local dir="$1"
    local keyword="$2"
    local model="${3:-base}"

    for file in "$dir"/*.mp4; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            output="${dir}/clip_${filename}"
            echo "剪辑 '$keyword': $file -> $output"
            python clipper.py --model "$model" clip "$file" --keywords "$keyword" -o "$output"
        fi
    done
}

# 示例3: 批量去除静音
remove_silence_all() {
    local dir="$1"

    for file in "$dir"/*.mp4; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            output="${dir}/clean_${filename}"
            echo "去静音: $file -> $output"
            python clipper.py remove-silence "$file" -o "$output"
        fi
    done
}

# 示例4: 批量格式转换
convert_all() {
    local dir="$1"
    local target_codec="${2:-libx264}"

    for file in "$dir"/*.avi "$dir"/*.mkv; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            output="${dir}/${filename%.*}.mp4"
            echo "转换: $file -> $output"
            python clipper.py convert "$file" -o "$output" --codec "$target_codec"
        fi
    done
}

# 根据命令行参数执行不同操作
case "${1:-help}" in
    transcribe)
        transcribe_all "${2:-.}" "${3:-base}"
        ;;
    clip)
        clip_by_keyword "${2:-.}" "${3:-关键词}" "${4:-base}"
        ;;
    silence)
        remove_silence_all "${2:-.}"
        ;;
    convert)
        convert_all "${2:-.}" "${3:-libx264}"
        ;;
    *)
        echo "用法: $0 <command> [directory] [options]"
        echo ""
        echo "命令:"
        echo "  transcribe [dir] [model]  - 批量转录"
        echo "  clip [dir] [keyword] [model] - 批量关键词剪辑"
        echo "  silence [dir]            - 批量去除静音"
        echo "  convert [dir] [codec]    - 批量格式转换"
        echo ""
        echo "示例:"
        echo "  $0 transcribe ./videos base"
        echo "  $0 clip ./videos 重要 base"
        echo "  $0 silence ./recordings"
        echo "  $0 convert ./videos libx264"
        ;;
esac
