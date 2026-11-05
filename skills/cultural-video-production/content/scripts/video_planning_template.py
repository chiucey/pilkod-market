#!/usr/bin/env python3
"""
视频策划模板脚本
用于生成文化科普短视频的策划方案
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class VideoPlanningTemplate:
    """视频策划模板类"""
    
    def __init__(self):
        self.template = {
            "基本信息": {
                "视频主题": "",
                "核心概念": "",
                "目标受众": [],
                "文化元素": [],
                "节气关联": "",
                "文物关联": ""
            },
            "创意策划": {
                "故事线": "",
                "创意亮点": [],
                "情感基调": "",
                "视觉风格": ""
            },
            "平台适配": {
                "目标平台": [],
                "平台特点": {},
                "时长建议": "",
                "格式建议": ""
            },
            "制作方案": {
                "拍摄地点": [],
                "所需设备": [],
                "人员配置": [],
                "预算预估": "",
                "时间安排": ""
            }
        }
    
    def generate_plan(self, theme: str, concept: str, platforms: List[str]) -> Dict:
        """生成基础策划方案"""
        plan = self.template.copy()
        plan["基本信息"]["视频主题"] = theme
        plan["基本信息"]["核心概念"] = concept
        plan["平台适配"]["目标平台"] = platforms
        
        # 根据平台设置默认参数
        platform_settings = {
            "douyin": {"时长建议": "15-60秒", "格式建议": "竖屏9:16", "特点": "快节奏、强互动、音乐驱动"},
            "wechat": {"时长建议": "1-3分钟", "格式建议": "竖屏或横屏均可", "特点": "深度内容、知识性强、社交传播"},
            "bilibili": {"时长建议": "3-10分钟", "格式建议": "横屏16:9", "特点": "知识深度、社区互动、弹幕文化"},
            "news_app": {"时长建议": "1-5分钟", "格式建议": "横屏16:9或竖屏9:16", "特点": "权威性、新闻性、教育性"},
            "tv": {"时长建议": "3-10分钟", "格式建议": "横屏16:9高清", "特点": "专业制作、叙事完整、视觉精美"}
        }
        
        for platform in platforms:
            if platform in platform_settings:
                plan["平台适配"]["平台特点"][platform] = platform_settings[platform]
        
        return plan
    
    def save_to_json(self, plan: Dict, filename: str):
        """保存策划方案为JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=2)
        print(f"策划方案已保存到: {filename}")
    
    def generate_script_template(self, plan: Dict) -> str:
        """生成脚本模板"""
        template = f"""# 视频脚本：{plan["基本信息"]["视频主题"]}

## 一、视频信息
- 主题：{plan["基本信息"]["视频主题"]}
- 核心概念：{plan["基本信息"]["核心概念"]}
- 目标平台：{', '.join(plan["平台适配"]["目标平台"])}
- 建议时长：{plan["平台适配"]["时长建议"]}

## 二、开场（0-10秒）
[视觉：吸引眼球的画面/文物特写/节气元素]
[解说/字幕：引人入胜的开场白，提出问题或展示悬念]

## 三、主体内容
### 文化背景介绍
[解说/字幕：介绍相关文化、节气或文物的历史背景]

### 核心知识点
[解说/字幕：讲解2-3个核心知识点，配合视觉呈现]

### 现代关联
[解说/字幕：连接传统文化与现代生活]

## 四、结尾（最后10秒）
[视觉：总结性画面，呼应开头]
[解说/字幕：总结要点，引导互动]
[字幕：关注/点赞/分享提示]

## 五、制作要求
- 视觉风格：{plan["创意策划"]["视觉风格"]}
- 情感基调：{plan["创意策划"]["情感基调"]}
- 音乐建议：配合情感基调的背景音乐
"""
        return template

if __name__ == "__main__":
    # 示例使用
    planner = VideoPlanningTemplate()
    plan = planner.generate_plan(
        theme="清明节气与古代农耕文化",
        concept="通过清明节气展现古代农耕智慧",
        platforms=["wechat", "douyin"]
    )
    planner.save_to_json(plan, "video_plan.json")
    print("视频策划模板已生成")