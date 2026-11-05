#!/usr/bin/env python3
"""
剪辑思路模板生成器
用于生成文化科普短视频的后期制作方案
"""

import json
from typing import Dict, List, Optional

class EditingPlanTemplate:
    """剪辑思路模板类"""
    
    def __init__(self):
        # 剪辑风格模板
        self.editing_styles = {
            "快节奏": {
                "特点": "快速剪辑，多转场，强节奏感",
                "适用平台": ["douyin", "kuaishou"],
                "平均镜头时长": "2-4秒",
                "转场效果": ["快速切换", "动态转场", "节奏匹配"]
            },
            "叙事型": {
                "特点": "逻辑清晰，叙事完整，节奏平稳",
                "适用平台": ["wechat", "bilibili", "news_app"],
                "平均镜头时长": "5-10秒",
                "转场效果": ["淡入淡出", "交叉溶解", "匹配剪辑"]
            },
            "电影感": {
                "特点": "视觉精美，节奏舒缓，情感丰富",
                "适用平台": ["bilibili", "tv"],
                "平均镜头时长": "8-15秒",
                "转场效果": ["长镜头", "缓慢转场", "色彩过渡"]
            },
            "科普教育": {
                "特点": "信息清晰，重点突出，便于理解",
                "适用平台": ["wechat", "news_app", "bilibili"],
                "平均镜头时长": "6-12秒",
                "转场效果": ["图形动画", "文字提示", "信息标注"]
            }
        }
        
        # 常用转场效果
        self.transitions = {
            "基础": ["切", "淡入", "淡出", "交叉溶解"],
            "动态": ["滑动", "缩放", "旋转", "翻页"],
            "创意": ["遮罩转场", "匹配运动", "色彩爆破", "形状变换"]
        }
        
        # 音频处理模板
        self.audio_templates = {
            "纪录片": {
                "解说": "清晰的人声，适中的语速",
                "背景音乐": "轻柔的器乐，不抢人声",
                "音效": "环境音，自然音效",
                "混音比例": "人声:音乐:音效 = 7:2:1"
            },
            "快节奏": {
                "解说": "充满活力的声音，较快语速",
                "背景音乐": "节奏感强的音乐",
                "音效": "强调音效，转场音效",
                "混音比例": "人声:音乐:音效 = 6:3:1"
            },
            "艺术感": {
                "解说": "富有感情的声音，适当留白",
                "背景音乐": "氛围音乐，情绪导向",
                "音效": "艺术化音效，空间感音效",
                "混音比例": "人声:音乐:音效 = 5:4:1"
            }
        }
    
    def generate_editing_plan(self, 
                             video_info: Dict, 
                             style: str = "叙事型",
                             platform: str = "wechat") -> Dict:
        """生成剪辑方案"""
        
        editing_style = self.editing_styles.get(style, self.editing_styles["叙事型"])
        audio_template = self.audio_templates.get(style, self.audio_templates["纪录片"])
        
        plan = {
            "视频信息": video_info,
            "剪辑风格": {
                "选择风格": style,
                "风格特点": editing_style["特点"],
                "适用性": f"适用于{platform}平台",
                "镜头节奏": editing_style["平均镜头时长"]
            },
            "剪辑结构": {
                "开场部分": {
                    "时长": "10-15秒",
                    "目标": "吸引注意力，引出主题",
                    "手法": ["快剪开场", "悬念设置", "视觉冲击"]
                },
                "主体部分": {
                    "时长": "视频主体",
                    "目标": "传递核心信息，讲述故事",
                    "手法": ["节奏控制", "信息分层", "视觉引导"]
                },
                "结尾部分": {
                    "时长": "10-15秒",
                    "目标": "总结升华，引导互动",
                    "手法": ["情感升华", "信息回顾", "行动号召"]
                }
            },
            "视觉处理": {
                "色彩校正": {
                    "基调": "根据主题选择冷暖色调",
                    "对比度": "适度增强以突出主体",
                    "饱和度": "自然适度，避免过度"
                },
                "特效应用": {
                    "文字动画": "用于知识点强调",
                    "图形标注": "用于信息说明",
                    "动态元素": "增强视觉吸引力"
                },
                "转场策略": {
                    "主要转场": editing_style["转场效果"],
                    "特殊转场": "根据内容需要添加创意转场",
                    "转场节奏": "与音乐节奏或内容节奏匹配"
                }
            },
            "音频处理": {
                "解说处理": {
                    "要求": audio_template["解说"],
                    "处理": ["降噪", "均衡", "压缩"],
                    "混音": audio_template["混音比例"]
                },
                "背景音乐": {
                    "风格": "与视频风格匹配",
                    "作用": "营造氛围，增强情绪",
                    "混音": audio_template["混音比例"]
                },
                "音效设计": {
                    "类型": audio_template["音效"],
                    "作用": "增强真实感，强调重点",
                    "位置": "关键动作点，转场点"
                }
            },
            "输出设置": {
                "分辨率": self._get_resolution(platform),
                "帧率": "25/30fps",
                "编码格式": "H.264",
                "文件格式": "MP4",
                "平台优化": self._get_platform_optimization(platform)
            }
        }
        
        return plan
    
    def _get_resolution(self, platform: str) -> str:
        """根据平台获取推荐分辨率"""
        resolutions = {
            "douyin": "1080×1920 (竖屏)",
            "wechat": "1080×1920 或 1920×1080",
            "bilibili": "1920×1080 (横屏)",
            "news_app": "1920×1080 或 1080×1920",
            "tv": "3840×2160 (4K)"
        }
        return resolutions.get(platform, "1920×1080")
    
    def _get_platform_optimization(self, platform: str) -> List[str]:
        """获取平台优化建议"""
        optimizations = {
            "douyin": ["前3秒吸引眼球", "添加热门音乐", "竖屏适配", "添加字幕"],
            "wechat": ["深度内容", "知识性强", "社交传播元素", "公众号适配"],
            "bilibili": ["高质量制作", "添加弹幕提示", "章节分段", "社区互动元素"],
            "news_app": ["权威性体现", "信息准确性", "教育性内容", "官方风格"]
        }
        return optimizations.get(platform, [])
    
    def generate_timeline_template(self, plan: Dict) -> str:
        """生成时间线模板"""
        timeline = f"""# 剪辑时间线规划：{plan["视频信息"].get("标题", "未知标题")}

## 整体结构
- 总时长：{plan["视频信息"].get("预计时长", "未知")}
- 剪辑风格：{plan["剪辑风格"]["选择风格"]}

## 详细时间线
### 开场 (0:00 - 0:15)
{plan["剪辑结构"]["开场部分"]["目标"]}
手法：{', '.join(plan["剪辑结构"]["开场部分"]["手法"])}

### 主体部分
- 第一部分：引入主题 (0:15 - 1:00)
- 第二部分：核心讲解 (1:00 - 2:30)
- 第三部分：深入分析 (2:30 - 4:00)

### 结尾 (最后15秒)
{plan["剪辑结构"]["结尾部分"]["目标"]}
手法：{', '.join(plan["剪辑结构"]["结尾部分"]["手法"])}

## 技术参数
- 分辨率：{plan["输出设置"]["分辨率"]}
- 帧率：{plan["输出设置"]["帧率"]}
- 输出格式：{plan["输出设置"]["文件格式"]}

## 平台优化
{chr(10).join(f"- {opt}" for opt in plan["输出设置"]["平台优化"])}
"""
        return timeline
    
    def save_plan(self, plan: Dict, filename: str):
        """保存剪辑方案"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        print(f"剪辑方案已保存到: {filename}")

if __name__ == "__main__":
    # 示例使用
    editor = EditingPlanTemplate()
    
    video_info = {
        "标题": "清明节气与农耕文化",
        "预计时长": "3分钟",
        "主题": "传统文化",
        "平台": "wechat"
    }
    
    plan = editor.generate_editing_plan(
        video_info=video_info,
        style="科普教育",
        platform="wechat"
    )
    
    editor.save_plan(plan, "editing_plan.json")
    
    # 生成时间线模板
    timeline = editor.generate_timeline_template(plan)
    with open("editing_timeline.txt", 'w', encoding='utf-8') as f:
        f.write(timeline)
    
    print("剪辑方案生成完成")