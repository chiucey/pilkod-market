#!/usr/bin/env python3
"""
影视内容OPC - 主入口脚本
素材抓取 → 智能筛选 → 爆款重构 → 运营优化
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from content_scraper import ContentScraper
from ranker import ContentRanker

class OPCPipeline:
    """OPC内容生产流水线"""

    def __init__(self):
        self.scraper = ContentScraper()
        self.ranker = ContentRanker()
        self.cache_dir = Path("cache")
        self.output_dir = Path("output")
        self.cache_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

    def step1_scrape(self) -> dict:
        """第一步：素材抓取"""
        print("=" * 50)
        print("【步骤1】素材抓取")
        print("=" * 50)

        data = self.scraper.run_full_scrape()
        cache_file = self.cache_dir / f"raw_materials_{datetime.now().strftime('%Y%m%d')}.json"
        self.scraper.save_to_cache(str(cache_file))

        print(f"✓ 抓取完成，共 {data['total_count']} 条素材")
        print(f"✓ 已保存至: {cache_file}")

        return data

    def step2_rank(self, materials: list = None) -> list:
        """第二步：智能筛选与排名"""
        print("\n" + "=" * 50)
        print("【步骤2】智能筛选与排名")
        print("=" * 50)

        # 如果没有传入素材，从缓存读取
        if materials is None:
            cache_files = sorted(self.cache_dir.glob("raw_materials_*.json"))
            if cache_files:
                with open(cache_files[-1], 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    materials = (
                        cached.get("douban", []) +
                        cached.get("bilibili", []) +
                        cached.get("toutiao", [])
                    )

        if not materials:
            print("⚠️ 没有找到素材，请先执行抓取")
            return []

        top3 = self.ranker.rank_and_filter(materials, top_n=3)

        print("\n🏆 TOP 3 主题排名：")
        for i, item in enumerate(top3, 1):
            print(f"\n{i}. {item.get('movie_name', '未知电影')}")
            print(f"   综合得分: {item['total_score']:.3f}")
            print(f"   - 文化密度: {item['breakdown']['cultural_density']:.2f}")
            print(f"   - 社交力: {item['breakdown']['social_power']:.2f}")
            print(f"   - 长尾价值: {item['breakdown']['geo_value']:.2f}")
            print(f"   📌 挖掘建议: {item['deep_dive_suggestion']}")

        # 保存排名结果
        output_file = self.output_dir / f"ranked_topics_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(top3, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 排名结果已保存至: {output_file}")

        return top3

    def step3_generate_prompts(self, top_topics: list) -> dict:
        """第三步：生成文章Prompt"""
        print("\n" + "=" * 50)
        print("【步骤3】爆款文章重构")
        print("=" * 50)

        prompts = {}
        for i, topic in enumerate(top_topics, 1):
            movie = topic.get('movie_name', '未知电影')
            print(f"\n📝 为《{movie}》生成文章Prompt...")

            prompts[movie] = {
                "basic_info": {
                    "片名": movie,
                    "导演": topic.get('director', '未知'),
                    "豆瓣评分": topic.get('douban_score', 'N/A'),
                    "核心争议": topic.get('controversial_topics', [])
                },
                "article_prompt": self._build_article_prompt(topic),
                "image_prompts": self._generate_image_prompts(topic)
            }

        # 保存Prompt
        output_file = self.output_dir / f"article_prompts_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(prompts, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 文章Prompt已保存至: {output_file}")

        return prompts

    def _build_article_prompt(self, topic: dict) -> str:
        """构建完整文章Prompt"""
        return f"""
【素材】
- 电影：{topic.get('movie_name')}
- 豆瓣评分：{topic.get('douban_score')}
- 核心争议：{', '.join(topic.get('controversial_topics', []))}
- 高赞评论摘要：{topic.get('review_content', '')[:200]}...

【任务】
请基于以上素材，撰写1篇深度影视推文。

【结构要求】
1. 爆款标题（5个选项）
2. 黄金开头（Hook）- 300字内
3. 深度拆解（The Story）- 600-800字
4. 谈资扩展（The Value）
5. GEO模块（Fact Sheet）- 5组Q&A
6. 评论区神助攻 - 1个引导问题

【深度挖掘方向】
{topic.get('deep_dive_suggestion')}
"""

    def _generate_image_prompts(self, topic: dict) -> list:
        """生成AI配图Prompt"""
        movie = topic.get('movie_name', '')
        style = "Cinematic photography, film grain, nostalgic mood"

        return [
            {
                "位置": "封面图",
                "描述": f"Feature film poster style for {movie}, dramatic lighting, cinematic composition"
            },
            {
                "位置": "黄金开头配图",
                "描述": f"{movie} key scene, moody atmosphere, emotional moment, film photography"
            },
            {
                "位置": "深度拆解配图",
                "描述": f"Detail close-up from {movie}, cinematic lighting, symbolic imagery"
            },
            {
                "位置": "谈资扩展配图",
                "描述": f"Abstract concept visualization, artistic interpretation, film aesthetic"
            }
        ]

    def run_full_pipeline(self):
        """运行完整流水线"""
        print("\n" + "🚀" * 25)
        print("  影视内容OPC生产流水线启动")
        print("🚀" * 25)

        # Step 1: 抓取
        self.step1_scrape()

        # Step 2: 排名
        top3 = self.step2_rank()

        if top3:
            # Step 3: 生成Prompt
            prompts = self.step3_generate_prompts(top3)

            print("\n" + "=" * 50)
            print("✅ 流水线执行完成！")
            print("=" * 50)
            print("\n📋 下一步：")
            print("1. 打开 output/ 目录查看生成的Prompt")
            print("2. 将Prompt复制到MiniMax进行文章生成")
            print("3. 使用 references/ai-image-prompts.md 生成配图")
        else:
            print("\n⚠️ 没有足够的素材进行排名，请检查抓取结果")

if __name__ == "__main__":
    pipeline = OPCPipeline()
    pipeline.run_full_pipeline()
