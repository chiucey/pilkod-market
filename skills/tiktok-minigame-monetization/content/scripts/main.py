"""
TikTok Mini Game Monetization - Main Execution Script
TikTok海外小游戏广告变现 - 主执行脚本

This script provides comprehensive workflow for TikTok Mini Game monetization
"""

import json
import os
from typing import Dict, List, Optional

class TikTokMinigameMonetizer:
    """TikTok小游戏变现主类"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.current_step = 0

    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置文件"""
        default_config = {
            "language": "zh-CN",
            "region": "overseas",
            "platform": "TikTok",
            "ad_types": ["rewarded_video", "interstitial", "banner"],
            "min_payout": 100,
            "currency": "USD"
        }

        if config_path and os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                default_config.update(loaded)
        return default_config

    def get_workflow_steps(self) -> List[Dict]:
        """获取完整工作流程步骤"""
        return [
            {
                "step": 1,
                "name": "账号准备",
                "description": "注册TikTok开发者账号",
                "tasks": [
                    "访问 TikTok Developer Portal",
                    "注册开发者账号",
                    "验证邮箱和手机号",
                    "设置双因素认证"
                ],
                "output": "开发者账号凭证"
            },
            {
                "step": 2,
                "name": "资质认证",
                "description": "完成开发者资质认证",
                "tasks": [
                    "选择认证类型(公司/个人)",
                    "提交资质材料",
                    "等待审核通过",
                    "获取广告位申请资格"
                ],
                "output": "开发者资质认证"
            },
            {
                "step": 3,
                "name": "收款配置",
                "description": "配置收益收款方式",
                "tasks": [
                    "选择收款方式(PayPal/Wise/银行)",
                    "填写收款账户信息",
                    "完成账户验证",
                    "设置付款阈值"
                ],
                "output": "收款账户配置完成"
            },
            {
                "step": 4,
                "name": "游戏开发",
                "description": "开发或获取小游戏",
                "tasks": [
                    "选择游戏引擎(可选零代码工具)",
                    "创建或导入小游戏",
                    "TikTok平台适配",
                    "游戏测试与优化"
                ],
                "output": "可上线的小游戏"
            },
            {
                "step": 5,
                "name": "广告接入",
                "description": "集成TikTok广告SDK",
                "tasks": [
                    "申请广告位配额",
                    "集成TikTok Ads SDK",
                    "配置激励视频广告",
                    "配置插屏广告",
                    "广告位测试"
                ],
                "output": "广告集成完成"
            },
            {
                "step": 6,
                "name": "提交审核",
                "description": "提交游戏审核",
                "tasks": [
                    "准备审核材料",
                    "提交游戏审核",
                    "处理审核反馈",
                    "审核通过上线"
                ],
                "output": "游戏上线"
            },
            {
                "step": 7,
                "name": "收益优化",
                "description": "优化广告收益",
                "tasks": [
                    "监控广告数据",
                    "分析用户行为",
                    "优化广告展示频率",
                    "A/B测试广告策略",
                    "提升用户留存"
                ],
                "output": "收益提升"
            },
            {
                "step": 8,
                "name": "提现盈利",
                "description": "提取广告收益",
                "tasks": [
                    "确认收益达到门槛",
                    "提交提现申请",
                    "等待审核处理",
                    "收益到账"
                ],
                "output": "收益提现成功"
            }
        ]

    def get_step_detail(self, step: int) -> Dict:
        """获取指定步骤的详细信息"""
        steps = self.get_workflow_steps()
        if 1 <= step <= len(steps):
            return steps[step - 1]
        return {"error": "Invalid step number"}

    def generate_account_guide(self) -> str:
        """生成账号注册指南"""
        return """
# TikTok开发者账号注册指南

## 1. 注册入口
访问: https://developers.tiktok.com/

## 2. 注册步骤

### 第一步：创建账号
1. 点击 "Sign Up" 注册按钮
2. 选择账号类型：
   - 个人开发者：适合个人开发者
   - 公司开发者：需要提供公司资质

### 第二步：填写信息
- 邮箱地址（用于接收通知）
- 手机号码（用于验证）
- 开发者名称
- 所在地

### 第三步：验证身份
- 邮箱验证
- 手机验证码
- 个人开发者需身份证认证
- 公司开发者需营业执照

### 第四步：设置安全
- 开启双因素认证
- 设置安全问题
- 绑定应急联系方式

## 3. 注意事项
- 使用真实信息注册
- 公司账号需要与营业执照一致
- 保持账号活跃，避免被封禁
- 遵守TikTok开发者政策

## 4. 审核时间
- 个人开发者：1-3个工作日
- 公司开发者：3-7个工作日
"""

    def generate_ad_types_guide(self) -> str:
        """生成广告类型指南"""
        return """
# TikTok广告类型详解

## 1. 激励视频广告 (Rewarded Video)
- 用户主动观看以获得游戏内奖励
- 收益最高，通常 $10-30 CPM
- 用户体验最好

### 适用场景
- 体力/金币不足时
- 关卡奖励加倍
- 解锁新角色/道具
- 复活继续游戏

## 2. 插屏广告 (Interstitial)
- 游戏自然停顿时展示
- 收益中等，通常 $5-15 CPM
- 需要控制展示频率

### 适用场景
- 关卡之间
- 游戏暂停时
- 加载画面
- 成就达成时

## 3. Banner广告 (Banner)
- 固定位置展示
- 收益较低，通常 $1-5 CPM
- 适合休闲游戏

### 适用场景
- 游戏底部常驻
- 结果页面
- 菜单页面

## 4. 广告收益对比
| 广告类型 | CPM范围 | 用户体验 | 推荐指数 |
|---------|---------|---------|---------|
| 激励视频 | $10-30 | 最好 | 5星 |
| 插屏广告 | $5-15 | 中等 | 4星 |
| Banner | $1-5 | 一般 | 3星 |
"""

    def generate_payout_guide(self) -> str:
        """生成提现指南"""
        return """
# TikTok广告收益提现指南

## 1. 提现门槛
- 最低提现金额: $100 USD
- 结算周期: 每月结算
- 付款时间: 次月15-30日

## 2. 收款方式

### PayPal (推荐)
- 到账速度快 (1-3工作日)
- 支持多币种
- 手续费较低
- 需要PayPal账户

### Wise (formerly TransferWise)
- 汇率优惠
- 手续费透明
- 适合大额提现
- 需要Wise账户

### 银行转账
- 直接到账银行账户
- 可能涉及中间行手续费
- 到账时间较长 (5-10工作日)

## 3. 提现步骤
1. 登录TikTok开发者后台
2. 进入 "Payments" 页面
3. 查看收益报表
4. 确认收益金额
5. 选择收款方式
6. 提交提现申请
7. 等待处理到账

## 4. 税务注意事项
- 美国开发者需要填写W-9表格
- 非美国开发者需要填写W-8BEN表格
- 某些地区可能需要预扣税
- 建议咨询专业税务顾问

## 5. 避坑指南
- 确保收款账户信息正确
- 避免频繁更改收款方式
- 保留收益记录和截图
- 关注税务申报截止日期
"""

    def run_workflow(self, target_step: int = None) -> str:
        """运行工作流程"""
        steps = self.get_workflow_steps()

        if target_step:
            step_info = self.get_step_detail(target_step)
            return self._format_step_output(step_info)

        output = "# TikTok小游戏广告变现完整流程\\n\\n"
        for step in steps:
            output += self._format_step_output(step)
        return output

    def _format_step_output(self, step: Dict) -> str:
        """格式化步骤输出"""
        if "error" in step:
            return f"错误: {step['error']}\\n"

        output = f"## 第{step['step']}步: {step['name']}\\n"
        output += f"**{step['description']}**\\n\\n"
        output += "### 任务清单:\\n"
        for i, task in enumerate(step['tasks'], 1):
            output += f"{i}. {task}\\n"
        output += f"\\n### 产出: {step['output']}\\n\\n"
        output += "---\\n\\n"
        return output


def main():
    """主函数入口"""
    monitizer = TikTokMinigameMonetizer()

    print("=" * 60)
    print("TikTok Mini Game Monetization Plugin")
    print("TikTok海外小游戏广告变现插件")
    print("=" * 60)
    print()

    # 显示完整流程
    workflow = monitizer.run_workflow()
    print(workflow)

    # 显示广告类型指南
    print(monitizer.generate_ad_types_guide())

    # 显示提现指南
    print(monitizer.generate_payout_guide())


if __name__ == "__main__":
    main()
