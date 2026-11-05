#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网页舆情分析 - 多维度分析模块
包括：情感分析、垃圾文本检测、行业分类、命名实体识别、文本摘要、热点趋势
"""

import re
import json
import sys
import argparse
from collections import Counter
from pathlib import Path
from datetime import datetime

# 中文NLP库
try:
    from snownlp import SnowNLP
except ImportError:
    print("⚠️ 警告: SnowNLP未安装，情感分析功能将受限")
    SnowNLP = None

try:
    import jieba
    import jieba.analyse
except ImportError:
    print("⚠️ 警告: jieba未安装，关键词提取功能将受限")
    jieba = None

try:
    import spacy

    # 尝试加载中文模型
    try:
        nlp = spacy.load("zh_core_web_sm")
    except OSError:
        print("⚠️ 警告: spaCy中文模型未安装，命名实体识别功能将受限")
        nlp = None
except ImportError:
    print("⚠️ 警告: spaCy未安装，命名实体识别功能将受限")
    nlp = None


class OpinionAnalyzer:
    """舆情分析器"""

    # 行业关键词库
    INDUSTRY_KEYWORDS = {
        "科技": [
            "人工智能",
            "AI",
            "机器学习",
            "大数据",
            "云计算",
            "互联网",
            "软件",
            "芯片",
            "半导体",
            "5G",
            "6G",
            "物联网",
            "区块链",
            "元宇宙",
            "数字化",
            "智能制造",
            "互联网公司",
            "科技巨头",
            "程序员",
            "代码",
            "算法",
            "数据",
            "服务器",
        ],
        "金融": [
            "银行",
            "证券",
            "保险",
            "基金",
            "股票",
            "债券",
            "期货",
            "外汇",
            "理财",
            "投资",
            "融资",
            "IPO",
            "市值",
            "股价",
            "收益率",
            "金融",
            "货币",
            "汇率",
            "降息",
            "加息",
            "存款",
            "贷款",
            "信用卡",
            "支付",
            "区块链",
            "数字货币",
        ],
        "医疗健康": [
            "医疗",
            "医院",
            "医生",
            "药品",
            "药物",
            "疫苗",
            "治疗",
            "诊断",
            "健康",
            "保健",
            "养生",
            "疾病",
            "疫情",
            "病毒",
            "细菌",
            "感染",
            "手术",
            "体检",
            "医保",
            "医药",
            "医疗器械",
            "中药",
            "西药",
            "研发",
            "临床",
        ],
        "教育": [
            "教育",
            "学校",
            "大学",
            "中学",
            "小学",
            "幼儿园",
            "培训",
            "辅导",
            "课程",
            "学生",
            "老师",
            "教师",
            "学习",
            "考试",
            "升学",
            "就业",
            "考研",
            "留学",
            "edu",
            "培训",
            "技能",
            "职业",
            "学历",
            "高考",
            "中考",
        ],
        "房地产": [
            "房地产",
            "房价",
            "购房",
            "租房",
            "房产",
            "楼市",
            "开发商",
            "中介",
            "土地",
            "Mortgage",
            "房贷",
            "利率",
            "限购",
            "调控",
            "学区房",
            "物业",
            "建筑",
            "施工",
            "拆迁",
            "棚改",
            "公积金",
        ],
        "汽车": [
            "汽车",
            "车企",
            "新车",
            "二手车",
            "电动车",
            "新能源汽车",
            "自动驾驶",
            "驾驶",
            "车牌",
            "交通",
            "事故",
            "维修",
            "保养",
            "油耗",
            "续航",
            "电池",
            "特斯拉",
            "比亚迪",
            "蔚来",
            "理想",
            "小鹏",
        ],
        "零售消费": [
            "电商",
            "网购",
            "购物",
            "零售",
            "超市",
            "便利店",
            "外卖",
            "餐饮",
            "食品",
            "饮料",
            "服装",
            "化妆品",
            "奢侈品",
            "双十一",
            "618",
            "直播带货",
            "拼多多",
            "淘宝",
            "京东",
            "天猫",
            "美团",
            "饿了么",
        ],
        "能源": [
            "石油",
            "天然气",
            "煤炭",
            "电力",
            "新能源",
            "太阳能",
            "风电",
            "核电",
            "氢能",
            "储能",
            "电池",
            "充电",
            "电价",
            "油价",
            "能源",
            "碳中和",
            "环保",
        ],
        "旅游": [
            "旅游",
            "旅行",
            "酒店",
            "机票",
            "景区",
            "景点",
            "度假",
            "签证",
            "护照",
            "出境",
            "入境",
            "导游",
            "观光",
            "门票",
            "民宿",
            "航空公司",
            "铁路",
        ],
        "娱乐": [
            "电影",
            "电视剧",
            "综艺",
            "音乐",
            "游戏",
            "动漫",
            "明星",
            "演员",
            "导演",
            "票房",
            "收视率",
            "演唱会",
            "演出",
            "娱乐",
            "短视频",
            "直播",
            "抖音",
            "B站",
        ],
        "政务": [
            "政府",
            "政策",
            "法规",
            "条例",
            "文件",
            "国务院",
            "部委",
            "省级",
            "市级",
            "政务",
            "行政",
            "审批",
            "监管",
            "执法",
            "廉政",
            "反腐",
            "党建",
            "党史",
        ],
        "军事": [
            "军事",
            "军队",
            "国防",
            "军演",
            "武器",
            "装备",
            "海军",
            "陆军",
            "空军",
            "导弹",
            "战斗机",
            "航母",
            "核武",
            "战略",
            "战术",
            "军费",
            "征兵",
        ],
        "体育": [
            "体育",
            "足球",
            "篮球",
            "排球",
            "网球",
            "游泳",
            "田径",
            "奥运",
            "亚运",
            "世界杯",
            "联赛",
            "冠军",
            "运动员",
            "教练",
            "球队",
            "比赛",
            "赛事",
        ],
    }

    # 垃圾文本检测关键词
    SPAM_KEYWORDS = [
        "兼职",
        "日结",
        "高薪",
        "招聘",
        "求职",
        "转让",
        "出售",
        "批发",
        "微商",
        "代理",
        "加盟",
        "招商",
        "收款",
        "付款",
        "红包",
        "中奖",
        "点击此处",
        "立即注册",
        "免费领取",
        "限时优惠",
        "原价999",
        "扫码",
        "加微信",
        "QQ号",
        "联系方式",
        "电话联系",
    ]

    def __init__(self):
        """初始化分析器"""
        pass

    def sentiment_analysis(self, text):
        """
        情感分析

        Args:
            text: 待分析文本

        Returns:
            情感分析结果字典
        """
        if not SnowNLP:
            return {
                "sentiment": "中性",
                "score": 0.5,
                "confidence": 0.5,
                "description": "SnowNLP未安装，无法进行情感分析",
            }

        try:
            # 使用SnowNLP进行情感分析
            s = SnowNLP(text[:10000])  # 限制文本长度
            score = s.sentiments  # 0-1之间的得分

            # 判断情感倾向
            if score >= 0.6:
                sentiment = "正面"
            elif score <= 0.4:
                sentiment = "负面"
            else:
                sentiment = "中性"

            # 计算置信度（距离边界的距离）
            if sentiment == "正面":
                confidence = (score - 0.6) / 0.4
            elif sentiment == "负面":
                confidence = (0.4 - score) / 0.4
            else:
                confidence = 1 - abs(score - 0.5) * 2

            return {
                "sentiment": sentiment,
                "score": round(score, 4),
                "confidence": round(confidence, 4),
                "description": f"情感得分为{score:.2f}，倾向{sentiment}",
            }

        except Exception as e:
            return {
                "sentiment": "中性",
                "score": 0.5,
                "confidence": 0.5,
                "description": f"情感分析失败: {str(e)}",
            }

    def spam_detection(self, text):
        """
        垃圾文本检测

        Args:
            text: 待检测文本

        Returns:
            检测结果字典
        """
        text_lower = text.lower()
        score = 0
        matched_keywords = []

        # 检查文本长度
        text_length = len(text)
        if text_length < 50:
            score += 30
        elif text_length < 100:
            score += 15

        # 检查广告关键词
        for keyword in self.SPAM_KEYWORDS:
            if keyword in text:
                score += 10
                matched_keywords.append(keyword)

        # 检查无意义字符占比
        meaningless_chars = re.findall(r"[^\u4e00-\u9fa5a-zA-Z0-9\s]", text)
        if text_length > 0:
            meaningless_ratio = len(meaningless_chars) / text_length
            if meaningless_ratio > 0.3:
                score += 20

        # 检查特殊字符过多
        special_pattern = re.findall(r"[#$@%^&*(){}\[\]|\\]", text)
        if len(special_pattern) > 20:
            score += 15

        # 判断是否为垃圾文本
        is_spam = score >= 30
        confidence = min(score / 100, 1.0)

        return {
            "is_spam": is_spam,
            "spam_score": score,
            "confidence": round(confidence, 4),
            "matched_keywords": matched_keywords[:10],
            "description": f"垃圾文本得分{score}分，{'判定为垃圾文本' if is_spam else '判定为正常文本'}",
        }

    def industry_classification(self, text):
        """
        行业分类

        Args:
            text: 待分类文本

        Returns:
            分类结果字典
        """
        # 统计各行业关键词匹配次数
        industry_scores = {}

        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            score = 0
            matched = []

            for keyword in keywords:
                count = text.count(keyword)
                if count > 0:
                    score += count
                    matched.append((keyword, count))

            if score > 0:
                industry_scores[industry] = {
                    "score": score,
                    "matched": sorted(matched, key=lambda x: x[1], reverse=True)[:5],
                }

        if not industry_scores:
            return {
                "industry": "综合",
                "confidence": 0.5,
                "matched_keywords": [],
                "description": "未能识别具体行业",
            }

        # 找出得分最高的行业
        top_industry = max(industry_scores.items(), key=lambda x: x[1]["score"])

        # 计算置信度
        total_score = sum(s["score"] for s in industry_scores.values())
        confidence = top_industry[1]["score"] / total_score if total_score > 0 else 0.5

        return {
            "industry": top_industry[0],
            "confidence": round(confidence, 4),
            "matched_keywords": [k[0] for k in top_industry[1]["matched"]],
            "all_industries": {k: v["score"] for k, v in industry_scores.items()},
            "description": f'文本属于"{top_industry[0]}"行业，置信度{confidence:.2%}',
        }

    def named_entity_recognition(self, text):
        """
        命名实体识别

        Args:
            text: 待识别文本

        Returns:
            实体识别结果字典
        """
        if not nlp:
            return {
                "entities": [],
                "top_entities": [],
                "entity_types": {},
                "description": "spaCy模型未安装，无法进行命名实体识别",
            }

        try:
            # 限制文本长度
            doc = nlp(text[:50000])

            # 提取实体
            entities = []
            for ent in doc.ents:
                entities.append(
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    }
                )

            # 统计实体频次（只看人名、地名、机构名）
            entity_counts = Counter()
            entity_types = {}

            for ent in entities:
                if ent["label"] in ["PER", "LOC", "ORG", "PERSON", "GPE", "NORP"]:
                    entity_counts[ent["text"]] += 1
                    entity_types[ent["label"]] = entity_types.get(ent["label"], 0) + 1

            # TOP5高频实体
            top_entities = [
                {"text": text, "count": count}
                for text, count in entity_counts.most_common(5)
            ]

            return {
                "entities": entities[:100],  # 限制返回数量
                "top_entities": top_entities,
                "entity_types": entity_types,
                "description": f"识别到{len(entities)}个实体，TOP5实体已提取",
            }

        except Exception as e:
            return {
                "entities": [],
                "top_entities": [],
                "entity_types": {},
                "description": f"命名实体识别失败: {str(e)}",
            }

    def text_summary(self, text, max_sentences=3):
        """
        文本摘要

        Args:
            text: 待摘要文本
            max_sentences: 最大句子数

        Returns:
            摘要结果字典
        """
        if not jieba:
            # 简单按标点分句
            sentences = re.split(r"[。！？\n]", text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            summary = sentences[:max_sentences]
        else:
            # 使用TF-IDF提取关键词，按关键词重要性排序句子
            try:
                # 提取关键词
                keywords = jieba.analyse.extract_tags(text, topK=50, withWeight=True)
                keyword_weights = {kw: weight for kw, weight in keywords}

                # 分句
                sentences = re.split(r"[。！？\n]", text)
                sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

                # 计算每句话的关键词得分
                sentence_scores = []
                for i, sent in enumerate(sentences):
                    score = 0
                    for kw, weight in keyword_weights.items():
                        if kw in sent:
                            score += weight
                    # 开头句子权重稍高
                    if i < 3:
                        score *= 1.2
                    sentence_scores.append((sent, score))

                # 按得分排序
                sentence_scores.sort(key=lambda x: x[1], reverse=True)
                summary = [s[0] for s in sentence_scores[:max_sentences]]

            except Exception as e:
                # 回退到简单方法
                sentences = re.split(r"[。！？\n]", text)
                sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
                summary = sentences[:max_sentences]

        # 清理摘要
        summary = [s.strip() for s in summary if len(s.strip()) > 10]

        return {
            "summary": summary,
            "sentence_count": len(summary),
            "description": f"生成{len(summary)}句摘要",
        }

    def trend_analysis(self, text, top_n=10):
        """
        热点趋势分析

        Args:
            text: 待分析文本
            top_n: 返回TOP N关键词

        Returns:
            趋势分析结果字典
        """
        if not jieba:
            return {
                "keywords": [],
                "trends": [],
                "description": "jieba未安装，无法进行趋势分析",
            }

        try:
            # 分词
            words = jieba.cut(text)

            # 过滤停用词和短词
            stopwords = set(
                [
                    "的",
                    "了",
                    "是",
                    "在",
                    "我",
                    "有",
                    "和",
                    "就",
                    "不",
                    "人",
                    "都",
                    "一",
                    "一个",
                    "上",
                    "也",
                    "很",
                    "到",
                    "说",
                    "要",
                    "去",
                    "你",
                    "会",
                    "着",
                    "没有",
                    "看",
                    "好",
                    "自己",
                    "这",
                    "那",
                    "他",
                    "她",
                    "它",
                    "们",
                    "这个",
                    "那个",
                    "什么",
                    "怎么",
                    "如何",
                    "为什么",
                ]
            )

            # 词性标注，过滤掉虚词
            import jieba.posseg as pseg

            words = pseg.cut(text)

            # 保留名词、动词、形容词
            valid_words = []
            for word, flag in words:
                if len(word) >= 2 and word not in stopwords:
                    if (
                        flag.startswith("n")
                        or flag.startswith("v")
                        or flag.startswith("a")
                    ):
                        valid_words.append(word)

            # 统计词频
            word_counts = Counter(valid_words)
            top_keywords = word_counts.most_common(top_n)

            # 判断趋势（基于关键词）
            trend_keywords = [kw for kw, _ in top_keywords[:5]]
            trend_description = self._analyze_trend(trend_keywords)

            return {
                "keywords": [{"word": w, "count": c} for w, c in top_keywords],
                "trends": trend_keywords,
                "description": trend_description,
            }

        except Exception as e:
            return {
                "keywords": [],
                "trends": [],
                "description": f"趋势分析失败: {str(e)}",
            }

    def _analyze_trend(self, keywords):
        """
        分析趋势方向

        Args:
            keywords: 关键词列表

        Returns:
            趋势描述
        """
        positive_words = [
            "增长",
            "发展",
            "创新",
            "突破",
            "提升",
            "上涨",
            "上升",
            "利好",
        ]
        negative_words = [
            "下降",
            "下跌",
            "风险",
            "问题",
            "危机",
            "下滑",
            "减少",
            "亏损",
        ]

        pos_count = sum(1 for kw in keywords for w in positive_words if w in kw)
        neg_count = sum(1 for kw in keywords for w in negative_words if w in kw)

        if pos_count > neg_count:
            return "整体趋势向好"
        elif neg_count > pos_count:
            return "整体趋势偏弱"
        else:
            return "趋势平稳"

    def analyze(self, text):
        """
        执行完整分析

        Args:
            text: 待分析文本

        Returns:
            完整分析结果字典
        """
        print("🔍 正在进行多维度舆情分析...")

        result = {
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "text_length": len(text),
        }

        # 1. 情感分析
        print("   📊 情感分析...")
        result["sentiment"] = self.sentiment_analysis(text)

        # 2. 垃圾文本检测
        print("   🗑️ 垃圾文本检测...")
        result["spam"] = self.spam_detection(text)

        # 3. 行业分类
        print("   🏷️ 行业分类...")
        result["industry"] = self.industry_classification(text)

        # 4. 命名实体识别
        print("   🏷️ 命名实体识别...")
        result["ner"] = self.named_entity_recognition(text)

        # 5. 文本摘要
        print("   📝 文本摘要...")
        result["summary"] = self.text_summary(text)

        # 6. 热点趋势
        print("   🔥 热点趋势分析...")
        result["trends"] = self.trend_analysis(text)

        print("✅ 分析完成")
        return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="网页舆情分析 - 多维度分析工具")
    parser.add_argument("input", help="输入文本文件路径或直接输入文本")
    parser.add_argument("-o", "--output", help="输出JSON文件路径")
    parser.add_argument(
        "--text", action="store_true", help="将输入作为直接文本而非文件路径"
    )

    args = parser.parse_args()

    # 读取文本
    if args.text:
        text = args.input
    else:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ 文件不存在: {args.input}")
            sys.exit(1)
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

    # 执行分析
    analyzer = OpinionAnalyzer()
    result = analyzer.analyze(text)

    # 输出结果
    print(f"\n📊 分析结果预览:")
    print(
        f"   情感: {result['sentiment']['sentiment']} ({result['sentiment']['score']:.2f})"
    )
    print(f"   行业: {result['industry']['industry']}")
    print(f"   垃圾文本: {'是' if result['spam']['is_spam'] else '否'}")
    if result["ner"]["top_entities"]:
        print(
            f"   核心实体: {', '.join([e['text'] for e in result['ner']['top_entities'][:3]])}"
        )

    # 保存到文件
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 已保存到: {args.output}")


if __name__ == "__main__":
    main()
