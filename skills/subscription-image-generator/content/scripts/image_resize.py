#!/usr/bin/env python3
"""
订阅号图片尺寸调整工具
支持常见社交媒体平台图片尺寸调整
"""

import os
import sys
from PIL import Image
import argparse

# 平台尺寸定义
PLATFORM_SIZES = {
    # 微信公众号
    'wechat_cover': (900, 383),      # 头条封面
    'wechat_secondary': (500, 500),  # 次条封面
    'wechat_article': (640, None),   # 文章内图宽度
    
    # 小红书
    'xiaohongshu': (1242, 1660),     # 笔记封面
    
    # 抖音/快手
    'douyin': (1080, 1920),          # 视频封面
    
    # 微博
    'weibo': (1200, 628),            # 微博配图
    
    # 通用尺寸
    'square': (1080, 1080),          # 正方形
    'portrait': (1080, 1350),        # 竖版2:3
    'landscape': (1920, 1080),       # 横版16:9
    'story': (1080, 1920),           # 故事模式9:16
}

def resize_image(input_path, output_path, target_size, mode='fit', quality=85):
    """
    调整图片尺寸
    
    Args:
        input_path: 输入图片路径
        output_path: 输出图片路径
        target_size: 目标尺寸 (width, height)
        mode: 调整模式 - 'fit'（填充）, 'crop'（裁剪）, 'stretch'（拉伸）
        quality: 输出质量 (1-100)
    """
    try:
        # 打开图片
        img = Image.open(input_path)
        original_size = img.size
        
        # 获取目标尺寸
        target_width, target_height = target_size
        
        # 如果高度为None，根据宽度等比例缩放
        if target_height is None:
            ratio = target_width / original_size[0]
            target_height = int(original_size[1] * ratio)
            target_size = (target_width, target_height)
        
        # 根据模式调整图片
        if mode == 'fit':
            # 保持宽高比填充
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            new_img = Image.new('RGB', target_size, (255, 255, 255))
            offset = ((target_size[0] - img.size[0]) // 2, 
                     (target_size[1] - img.size[1]) // 2)
            new_img.paste(img, offset)
            result = new_img
            
        elif mode == 'crop':
            # 裁剪到目标尺寸
            # 计算裁剪区域
            ratio = max(target_size[0] / original_size[0], 
                       target_size[1] / original_size[1])
            new_size = (int(original_size[0] * ratio), 
                       int(original_size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 计算裁剪位置
            left = (new_size[0] - target_size[0]) // 2
            top = (new_size[1] - target_size[1]) // 2
            right = left + target_size[0]
            bottom = top + target_size[1]
            
            result = img.crop((left, top, right, bottom))
            
        elif mode == 'stretch':
            # 拉伸到目标尺寸
            result = img.resize(target_size, Image.Resampling.LANCZOS)
            
        else:
            raise ValueError(f"不支持的调整模式: {mode}")
        
        # 保存图片
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            result.save(output_path, 'JPEG', quality=quality, optimize=True)
        else:
            result.save(output_path, optimize=True)
        
        print(f"图片已调整: {original_size} -> {target_size}")
        print(f"保存到: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"调整图片时出错: {e}")
        return False

def batch_resize(input_dir, output_dir, target_size, mode='fit', 
                 extensions=('.jpg', '.jpeg', '.png', '.gif')):
    """
    批量调整图片尺寸
    
    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        target_size: 目标尺寸
        mode: 调整模式
        extensions: 处理的文件扩展名
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    processed = 0
    failed = 0
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(extensions):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            print(f"处理: {filename}")
            if resize_image(input_path, output_path, target_size, mode):
                processed += 1
            else:
                failed += 1
    
    print(f"\n处理完成: {processed} 成功, {failed} 失败")

def create_platform_sizes():
    """创建各平台标准尺寸的图片"""
    parser = argparse.ArgumentParser(description='订阅号图片尺寸调整工具')
    parser.add_argument('input', help='输入图片路径')
    parser.add_argument('--output-dir', default='./output', 
                       help='输出目录 (默认: ./output)')
    parser.add_argument('--platform', choices=list(PLATFORM_SIZES.keys()),
                       help='目标平台')
    parser.add_argument('--width', type=int, help='自定义宽度')
    parser.add_argument('--height', type=int, help='自定义高度')
    parser.add_argument('--mode', choices=['fit', 'crop', 'stretch'],
                       default='fit', help='调整模式 (默认: fit)')
    parser.add_argument('--quality', type=int, default=85,
                       help='输出质量 (1-100, 默认: 85)')
    parser.add_argument('--batch', action='store_true',
                       help='批量处理目录中的所有图片')
    
    args = parser.parse_args()
    
    # 确定目标尺寸
    if args.platform:
        target_size = PLATFORM_SIZES[args.platform]
    elif args.width and args.height:
        target_size = (args.width, args.height)
    elif args.width:
        target_size = (args.width, None)
    else:
        print("请指定平台或尺寸")
        return
    
    # 处理单个文件或批量
    if args.batch:
        if os.path.isdir(args.input):
            batch_resize(args.input, args.output_dir, target_size, 
                        args.mode, args.quality)
        else:
            print("批量处理需要输入目录")
    else:
        if os.path.isfile(args.input):
            # 单个文件
            if not os.path.exists(args.output_dir):
                os.makedirs(args.output_dir)
            
            filename = os.path.basename(args.input)
            output_path = os.path.join(args.output_dir, filename)
            
            resize_image(args.input, output_path, target_size, 
                        args.mode, args.quality)
        else:
            print("输入文件不存在")

if __name__ == '__main__':
    create_platform_sizes()