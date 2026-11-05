#!/usr/bin/env python3
"""
拍摄脚本模板生成器
用于生成文化科普短视频的拍摄脚本
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class ShootingScriptTemplate:
    """拍摄脚本模板类"""
    
    def __init__(self):
        self.template_structure = {
            "项目信息": {
                "视频标题": "",
                "导演": "",
                "摄影师": "",
                "制片": "",
                "拍摄日期": "",
                "地点": []
            },
            "分镜头脚本": [],
            "设备清单": {
                "摄影设备": [],
                "灯光设备": [],
                "音频设备": [],
                "辅助设备": []
            },
            "人员安排": {
                "核心团队": [],
                "出镜人员": [],
                "技术支持": []
            },
            "拍摄计划": {
                "日期安排": [],
                "场地安排": {},
                "备用方案": []
            }
        }
    
    def create_shot_template(self) -> Dict:
        """创建单个镜头模板"""
        return {
            "镜头编号": "",
            "场景": "",
            "内容描述": "",
            "景别": "",  # 特写、中景、全景等
            "角度": "",  # 平视、俯视、仰视等
            "运镜": "",  # 固定、推拉、摇移等
            "时长": "",  # 预计时长（秒）
            "对白/解说": "",
            "音效/音乐": "",
            "备注": ""
        }
    
    def generate_script(self, 
                       title: str, 
                       scenes: List[Dict], 
                       platform: str = "wechat") -> Dict:
        """生成完整的拍摄脚本"""
        
        script = self.template_structure.copy()
        script["项目信息"]["视频标题"] = title
        script["项目信息"]["拍摄日期"] = datetime.now().strftime("%Y年%m月%d日")
        
        # 根据平台调整
        platform_settings = {
            "douyin": {
                "镜头特点": "快节奏，多特写，强视觉冲击",
                "平均镜头时长": "2-5秒",
                "转场要求": "快速转场，节奏感强"
            },
            "wechat": {
                "镜头特点": "叙事完整，知识性强",
                "平均镜头时长": "5-10秒",
                "转场要求": "自然过渡，逻辑连贯"
            },
            "bilibili": {
                "镜头特点": "制作精良，细节丰富",
                "平均镜头时长": "8-15秒",
                "转场要求": "专业转场，视觉效果佳"
            }
        }
        
        platform_setting = platform_settings.get(platform, platform_settings["wechat"])
        
        # 生成分镜头
        shot_list = []
        for i, scene in enumerate(scenes, 1):
            shot = self.create_shot_template()
            shot["镜头编号"] = f"SC{i:03d}"
            shot["场景"] = scene.get("场景", "")
            shot["内容描述"] = scene.get("内容", "")
            shot["景别"] = scene.get("景别", "中景")
            shot["角度"] = scene.get("角度", "平视")
            shot["运镜"] = scene.get("运镜", "固定")
            shot["时长"] = scene.get("时长", platform_setting["平均镜头时长"])
            shot["对白/解说"] = scene.get("对白", "")
            shot["备注"] = f"平台适配：{platform_setting['镜头特点']}"
            
            shot_list.append(shot)
        
        script["分镜头脚本"] = shot_list
        
        # 设置默认设备清单
        script["设备清单"] = {
            "摄影设备": ["专业摄像机/电影机", "稳定器（如大疆如影）", "三脚架", "ND滤镜"],
            "灯光设备": ["LED影视灯", "柔光箱", "反光板", "灯光支架"],
            "音频设备": ["无线麦克风", "录音机", "防风毛衣", "监听耳机"],
            "辅助设备": ["监视器", "电池若干", "存储卡", "场记板"]
        }
        
        return script
    
    def generate_script_text(self, script: Dict) -> str:
        """生成可读的脚本文本"""
        
        text = f"""# 拍摄脚本：{script["项目信息"]["视频标题"]}

## 一、项目信息
- 视频标题：{script["项目信息"]["视频标题"]}
- 导演：{script["项目信息"]["导演"]}
- 摄影师：{script["项目信息"]["摄影师"]}
- 拍摄日期：{script["项目信息"]["拍摄日期"]}
- 地点：{', '.join(script["项目信息"]["地点"])}

## 二、分镜头脚本
"""
        
        for shot in script["分镜头脚本"]:
            text += f"""
### 镜头 {shot['镜头编号']}
- **场景**：{shot['场景']}
- **内容**：{shot['内容描述']}
- **景别/角度**：{shot['景别']} / {shot['角度']}
- **运镜**：{shot['运镜']}
- **时长**：{shot['时长']}秒
- **对白/解说**：{shot['对白/解说']}
- **音效/音乐**：{shot['音效/音乐']}
- **备注**：{shot['备注']}
"""
        
        text += """
## 三、设备清单
### 摄影设备
"""
        for equipment in script["设备清单"]["摄影设备"]:
            text += f"- {equipment}\n"
        
        text += """
### 灯光设备
"""
        for equipment in script["设备清单"]["灯光设备"]:
            text += f"- {equipment}\n"
        
        text += """
### 音频设备
"""
        for equipment in script["设备清单"]["音频设备"]:
            text += f"- {equipment}\n"
        
        return text
    
    def save_script(self, script: Dict, filename: str):
        """保存脚本到文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(script, f, ensure_ascii=False, indent=2)
        print(f"拍摄脚本已保存到: {filename}")

if __name__ == "__main__":
    # 示例使用
    script_gen = ShootingScriptTemplate()
    
    # 示例场景
    scenes = [
        {
            "场景": "博物馆展厅",
            "内容": "文物特写，展示青铜器的精美纹饰",
            "景别": "特写",
            "角度": "平视",
            "运镜": "缓慢推近",
            "时长": "8秒",
            "对白": "这件青铜器上的纹饰反映了..."
        },
        {
            "场景": "室外场景",
            "内容": "节气相关的自然景观",
            "景别": "全景",
            "角度": "航拍",
            "运镜": "缓慢平移",
            "时长": "10秒",
            "对白": "清明时节，万物复苏..."
        }
    ]
    
    script = script_gen.generate_script(
        title="节气与文物：清明的文化意义",
        scenes=scenes,
        platform="wechat"
    )
    
    script_gen.save_script(script, "shooting_script.json")
    
    # 生成文本格式
    script_text = script_gen.generate_script_text(script)
    with open("shooting_script.txt", 'w', encoding='utf-8') as f:
        f.write(script_text)
    
    print("拍摄脚本生成完成")