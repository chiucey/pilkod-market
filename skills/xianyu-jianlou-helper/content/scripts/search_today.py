#!/usr/bin/env python3
"""
咸鱼代售捡漏日报生成器 v3.0
生成每日捡漏报告框架，AI将用实时搜索填充价格数据
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any

# 路径配置
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SKILL_DIR / "config.json"
OUTPUT_DIR = SKILL_DIR / "output"

def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_PATH}")
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_today() -> str:
    """获取今日日期"""
    return datetime.now().strftime("%Y-%m-%d")

def generate_search_links(config: Dict, keyword: str) -> Dict[str, str]:
    """生成各平台搜索链接"""
    links = {}
    platforms = config.get('platforms', {})

    for platform_id, platform_info in platforms.items():
        base_url = platform_info.get('base_url', '')
        if platform_id == 'douyin':
            # 抖音使用URL编码
            links[platform_id] = base_url + keyword.replace(' ', '%20')
        else:
            links[platform_id] = base_url + keyword

    return links

def format_search_link(platform_name: str, url: str) -> str:
    """格式化搜索链接为Markdown链接"""
    return f"[{platform_name}]({url})"

def generate_category_search_section(config: Dict) -> str:
    """生成全品类搜索链接部分"""
    lines = []
    platforms = config.get('platforms', {})

    # 为每个平台生成表头
    lines.append("| 品类 | " + " | ".join([p['name'] for p in platforms.values()]) + " |")
    lines.append("|" + "|".join(["---"] * (len(platforms) + 1)) + "|")

    # 为每个品类生成搜索链接
    for category in config.get('categories', []):
        cat_name = category['name']
        # 使用第一个子项的关键词
        if category.get('sub_items'):
            keyword = category['sub_items'][0]['keywords'][0]
            links = generate_search_links(config, keyword)
            link_cells = []
            for platform_id in platforms.keys():
                platform_name = platforms[platform_id]['name']
                if platform_id in links:
                    link_cells.append(format_search_link(platform_name, links[platform_id]))
                else:
                    link_cells.append("-")
            lines.append(f"| **{cat_name}** | " + " | ".join(link_cells) + " |")

    return "\n".join(lines)

def generate_price_threshold_table(config: Dict) -> str:
    """生成价格阈值速查表"""
    lines = []
    lines.append("| 品类 | 商品 | 建议入手价 | 捡漏警戒线 | 备注 |")
    lines.append("|------|------|-----------|-----------|------|")

    for category in config.get('categories', []):
        cat_name = category['name']
        # 只显示前3个子项
        for idx, item in enumerate(category.get('sub_items', [])[:3]):
            name = item['name']
            max_price = f"¥{item['max_price']:,}"
            hot_price = f"¥{item['hot_price']:,}"
            # 检查是否为高风险品类
            fake_risk = config.get('fake_risk_categories', [])
            mining_risk = config.get('mining_risk_categories', [])
            remark = ""
            if any(kw in name for kw in fake_risk):
                remark = "⚠️ 需验真"
            elif any(kw in name for kw in mining_risk):
                remark = "⚠️ 需查矿"
            lines.append(f"| {cat_name if idx == 0 else ''} | {name} | {max_price} | {hot_price} | {remark} |")

    return "\n".join(lines)

def generate_emotion_search_section(config: Dict) -> List[str]:
    """生成情绪词搜索组合"""
    emotions = config.get('emotion_keywords', [])
    categories = config.get('categories', [])

    # 选取高频品类关键词
    popular_keywords = []
    for cat in categories[:10]:
        if cat.get('sub_items'):
            popular_keywords.append(cat['sub_items'][0]['keywords'][0])

    combinations = []
    for emotion in emotions[:8]:
        for keyword in popular_keywords[:5]:
            combinations.append(f"{keyword} {emotion}")

    return combinations[:20]

def generate_profit_table(config: Dict) -> str:
    """生成代售利润速查表"""
    lines = []
    lines.append("| 商品类型 | 入手价区间 | 预计售价 | 预估利润 |")
    lines.append("|----------|-----------|---------|---------|")

    profit_config = config.get('profit_formula', {})
    target_margin = profit_config.get('target_margin', 15)
    platform_fee_rate = profit_config.get('platform_fee_rate', 0.05)

    # 样例数据
    samples = [
        ("iPhone 15PM 256G", "4200-5000", "5500-6200", "10-18%"),
        ("Switch 2", "1500-1800", "1900-2200", "12-20%"),
        ("PS5 Slim", "2600-3200", "3200-3800", "8-15%"),
        ("RTX 4060", "1700-2100", "2200-2600", "15-25%"),
        ("Mac mini M4", "3000-3500", "3800-4500", "12-20%"),
        ("AirPods Pro 2", "800-1100", "1200-1500", "20-30%"),
        ("石头G20S", "1500-1800", "2000-2400", "15-25%"),
        ("泡泡玛特MEGA", "1500-2500", "3000-4000", "25-40%"),
    ]

    for item in samples:
        lines.append(f"| {item[0]} | {item[1]} | {item[2]} | {item[3]} |")

    return "\n".join(lines)

def generate_report_template(config: Dict) -> str:
    """生成报告模板"""
    today = get_today()

    report = f"""# 📦 咸鱼代售捡漏日报 — {today}

> 本报告由 AI 实时搜索生成，价格数据仅供参考，实际价格请自行核实
>
> ⚠️ **重要提示**：二手交易存在风险，请在确认商品真实性和完整性后再付款

---

## 🔥 强烈推荐（低于捡漏警戒线）

> 以下商品价格已低于捡漏警戒线，性价比极高但需注意风险

| 品类 | 商品 | 今日参考价 | 警戒线 | 折扣率 | 数据来源 | 各平台搜索直链 |
|------|------|-----------|--------|-------|---------|---------------|

*暂无数据 - AI搜索填充中...*

---

## ✅ 推荐关注（低于建议入手价）

> 以下商品价格低于建议入手价，可考虑入手

| 品类 | 商品 | 今日参考价 | 建议入手价 | 折扣率 | 数据来源 | 各平台搜索直链 |
|------|------|-----------|-----------|-------|---------|---------------|

*暂无数据 - AI搜索填充中...*

---

## 📊 全品类价格阈值速查

> 完整阈值配置见 `config.json`

| 品类 | 商品 | 建议入手价 | 捡漏警戒线 | 备注 |
|------|------|-----------|-----------|------|

{generate_price_threshold_table(config)}

---

## 🔍 全品类搜索直链（8平台）

> 点击链接直接跳转至各平台搜索页面

| 品类 | 闲鱼 | 淘宝 | 天猫 | 京东 | 拼多多 | 1688 | 小红书 | 抖音 |
|------|------|------|------|------|--------|------|--------|------|

{generate_category_search_section(config)}

---

## 🎯 情绪词搜索组合

> 使用以下关键词组合在闲鱼搜索，可找到急售、换钱等高性价比商品

| 序号 | 搜索组合 | 推荐理由 |
|------|---------|---------|
"""

    # 添加情绪词组合
    emotion_combos = generate_emotion_search_section(config)
    for idx, combo in enumerate(emotion_combos, 1):
        report += f"| {idx} | {combo} | 急售/换钱 |" + "\n"

    report += f"""

---

## 📊 代售利润速查

> 基于平台抽成 {int(platform_fee_rate*100)}% 计算，目标利润率 ≥{target_margin}%

| 商品类型 | 入手价区间 | 预计售价 | 预估利润 |
|----------|-----------|---------|---------|
"""

    report += generate_profit_table(config)

    report += f"""

---

## 🔄 品类迭代报告

> 每日检查市场热点，动态调整配置

### 本日变更记录
- 暂无变更

### 待观察品类
| 品类 | 原因 | 观察天数 |
|------|------|---------|
| - | - | - |

---

## 💡 操作建议

1. **🔍 重点关注**：以下品类当前价格处于低位，适合入手
   - 待AI搜索填充

2. **⚠️ 谨慎入手**：以下品类假货风险高，建议当面交易或找专业验货
   - AirPods/iPhone 系列
   - 始祖鸟/高端户外装备
   - 投影仪

3. **🛡️ 显卡特别提示**：务必检查GPU使用时长和BIOS版本，防范矿卡

4. **📈 观望建议**：价格持续高于建议入手价的品类可继续观望

---

## ⚠️ 风险提示

### 假货高风险品类（务必验货）
- AirPods Pro 2 / AirPods Max
- iPhone 15 Pro 系列
- 始祖鸟冲锋衣
- 投影仪（坚果/极米）
- 泡泡玛特 MEGA / 潮玩手办

### 矿卡风险品类（务必查验）
- RTX 4060 / 4070 / 4080 系列
- 所有"锻炼过"、"挖过"的显卡

### 交易安全建议
1. 优先选择支持验货的平台（如咸鱼验货宝）
2. 尽量当面交易，检查商品完整性
3. 保留聊天记录和转账凭证
4. 拒绝私下转账，要求平台担保交易

---

## 📋 附录：配置信息

- **版本**: {config.get('version', '3.0')}
- **更新日期**: {config.get('update_date', today)}
- **品类总数**: {len(config.get('categories', []))} 大类
- **商品总数**: {sum(len(c.get('sub_items', [])) for c in config.get('categories', []))} 子项
- **平台覆盖**: {len(config.get('platforms', {}))} 个

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*数据来源: 公开网络搜索，价格仅供参考，实际价格请自行核实*
"""

    return report

def save_report(report: str, output_dir: Path = OUTPUT_DIR) -> Path:
    """保存报告到文件"""
    output_dir.mkdir(parents=True, exist_ok=True)

    today = get_today()
    report_path = output_dir / f"report_{today}.md"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    return report_path

def load_price_history() -> Dict:
    """加载历史价格记录"""
    history_path = OUTPUT_DIR / "price_history.json"
    if history_path.exists():
        with open(history_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"records": [], "last_update": None}

def save_price_history(history: Dict) -> None:
    """保存历史价格记录"""
    history_path = OUTPUT_DIR / "price_history.json"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def record_price(category: str, item_name: str, price: float, source: str, date: str) -> None:
    """记录价格到历史"""
    history = load_price_history()

    record = {
        "category": category,
        "item": item_name,
        "price": price,
        "source": source,
        "date": date
    }

    history["records"].append(record)
    history["last_update"] = datetime.now().isoformat()

    save_price_history(history)

def main():
    """主函数"""
    print("=" * 50)
    print("咸鱼代售捡漏日报生成器 v3.0")
    print("=" * 50)

    try:
        # 加载配置
        print("[1/3] 加载配置文件...")
        config = load_config()
        print(f"    ✓ 成功加载配置，版本 {config.get('version', 'unknown')}")
        print(f"    ✓ 覆盖 {len(config.get('categories', []))} 个品类")
        print(f"    ✓ 覆盖 {len(config.get('platforms', {}))} 个平台")

        # 生成报告
        print("\n[2/3] 生成报告框架...")
        report = generate_report_template(config)
        print("    ✓ 报告框架生成成功")

        # 保存报告
        print("\n[3/3] 保存报告...")
        report_path = save_report(report)
        print(f"    ✓ 报告已保存至: {report_path}")

        print("\n" + "=" * 50)
        print("报告框架生成完成！")
        print("=" * 50)
        print("\n下一步：AI将使用 batch_web_search 工具实时搜索各品类价格")
        print("       搜索完成后，将数据填入报告对应位置")

        return report_path

    except FileNotFoundError as e:
        print(f"\n[错误] {e}")
        print("请确保 config.json 文件存在于技能目录中")
        return None
    except Exception as e:
        print(f"\n[错误] 生成报告时发生异常: {e}")
        return None

if __name__ == "__main__":
    main()
