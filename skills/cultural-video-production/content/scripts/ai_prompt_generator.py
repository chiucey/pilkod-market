#!/usr/bin/env python3
"""
AI视频提示词生成器
用于生成文生视频、图生视频的提示词
"""

import json
from typing import Dict, List

class AIPromptGenerator:
    """AI视频提示词生成器"""
    
    def __init__(self):
        # 常用风格描述
        self.styles = {
            "纪录片": "纪录片风格，写实画面，自然光影，真实感强",
            "国风": "中国风，水墨画风格，传统色彩，优雅意境",
            "现代感": "现代设计感，简洁构图，明亮色彩，时尚感",
            "科普": "科普教育风格，信息可视化，清晰明了，知识性强",
            "艺术": "艺术感强，创意构图，独特视角，视觉冲击力"
        }
        
        # 视频质量描述
        self.quality = {
            "基础": "基础质量，清晰度720p",
            "标准": "标准质量，清晰度1080p，细节丰富",
            "高清": "高清质量，清晰度4K，细节精致",
            "电影级": "电影级质量，电影感光影，专业级细节"
        }
        
        # 运镜描述
        self.camera_moves = {
            "固定": "固定镜头，稳定构图",
            "推拉": "推拉镜头，从全景到特写或从特写到全景",
            "平移": "平移镜头，左右或上下移动",
            "环绕": "环绕拍摄，围绕主体旋转",
            "航拍": "航拍视角，高空俯视",
            "跟踪": "跟踪拍摄，跟随主体移动"
        }
        
        # 平台优化参数
        self.platform_params = {
            "douyin": {"aspect_ratio": "9:16", "duration": "15-60秒", "style": "快节奏，强视觉冲击"},
            "wechat": {"aspect_ratio": "多种比例", "duration": "1-3分钟", "style": "深度内容，知识性强"},
            "bilibili": {"aspect_ratio": "16:9", "duration": "3-10分钟", "style": "知识深度，制作精良"},
            "news_app": {"aspect_ratio": "16:9或9:16", "duration": "1-5分钟", "style": "权威严谨，教育性强"}
        }
    
    def generate_video_prompt(self, 
                             subject: str, 
                             style: str = "纪录片", 
                             quality: str = "标准",
                             platform: str = "wechat") -> Dict:
        """生成视频提示词"""
        
        # 获取平台参数
        platform_param = self.platform_params.get(platform, self.platform_params["wechat"])
        
        prompt_dict = {
            "基础提示": f"一段关于{subject}的{style}风格视频",
            "详细描述": f"{self.styles.get(style, '')}，{self.quality.get(quality, '')}",
            "视觉要素": [
                f"主题：{subject}",
                f"风格：{style} - {self.styles.get(style, '')}",
                f"色彩：与主题相符的协调色彩",
                f"光影：自然光影，突出主体"
            ],
            "动态要素": [
                "流畅的镜头运动",
                "合理的转场效果",
                "动态元素的自然运动"
            ],
            "技术参数": {
                "画幅比例": platform_param["aspect_ratio"],
                "建议时长": platform_param["duration"],
                "风格适配": platform_param["style"],
                "质量要求": quality
            },
            "提示词示例": [
                f"cinematic video of {subject}, {self.styles.get(style, '')}, {self.quality.get(quality, '')}, {platform_param['aspect_ratio']} aspect ratio",
                f"documentary style video about {subject}, detailed and realistic, professional lighting",
                f"educational video explaining {subject}, clear visuals, informative content"
            ]
        }
        
        return prompt_dict
    
    def generate_shot_prompts(self, 
                             script_segments: List[str], 
                             style: str = "纪录片") -> List[Dict]:
        """根据脚本片段生成分镜头提示词"""
        
        shot_prompts = []
        
        for i, segment in enumerate(script_segments, 1):
            shot_prompt = {
                "镜头编号": f"Shot {i:03d}",
                "脚本内容": segment,
                "视觉建议": f"表现：{segment[:50]}...",
                "提示词": [
                    f"{self.styles.get(style, '')} shot of {segment[:30]}...",
                    f"cinematic scene showing {segment[:30]}...",
                    f"visual representation of {segment[:30]}..."
                ],
                "技术建议": {
                    "镜头类型": "根据内容选择特写、中景或全景",
                    "运镜方式": "根据情绪选择固定或运动镜头",
                    "时长建议": "3-8秒"
                }
            }
            shot_prompts.append(shot_prompt)
        
        return shot_prompts
    
    def save_prompts(self, prompts: Dict, filename: str):
        """保存提示词到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        print(f"提示词已保存到: {filename}")

if __name__ == "__main__":
    # 示例使用
    generator = AIPromptGenerator()
    
    # 生成视频提示词
    video_prompt = generator.generate_video_prompt(
        subject="清明节气与传统农耕",
        style="国风",
        quality="高清",
        platform="wechat"
    )
    
    generator.save_prompts(video_prompt, "ai_video_prompts.json")
    
    # 生成分镜头提示词
    script_segments = [
        "清明时节的田园风光",
        "古代农民春耕的场景",
        "传统农具的使用方法",
        "节气与农耕的关系"
    ]
    
    shot_prompts = generator.generate_shot_prompts(script_segments, "国风")
    generator.save_prompts({"分镜头提示词": shot_prompts}, "shot_prompts.json")
    
    print("AI提示词生成完成")