#!/bin/bash
# 打包技能为 .skill 文件

SKILL_DIR="/workspace/temp-skills/policy-long-image-generator"
OUTPUT_DIR="/workspace/temp-skills"

# 创建打包目录
PACK_DIR="$OUTPUT_DIR/.pack_tmp"
rm -rf "$PACK_DIR"
mkdir -p "$PACK_DIR"

# 复制技能文件
cp -r "$SKILL_DIR" "$PACK_DIR/"

# 进入打包目录
cd "$PACK_DIR"

# 打包为 tar.gz
tar -czf "policy-long-image-generator.skill" "policy-long-image-generator/"
rm -rf "policy-long-image-generator"

# 移动到输出目录
mv "$PACK_DIR/policy-long-image-generator.skill" "$OUTPUT_DIR/"

# 清理临时目录
rm -rf "$PACK_DIR"

echo "技能包已生成: $OUTPUT_DIR/policy-long-image-generator.skill"
ls -la "$OUTPUT_DIR/policy-long-image-generator.skill"
