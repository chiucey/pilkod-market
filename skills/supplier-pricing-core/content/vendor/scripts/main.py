# /// script
# requires-python = ">=3.11"
# dependencies = ["aiohttp", "argparse", "PyYAML", "scikit-learn", "flask"]
# ///

import os
import io
import csv
import json
import yaml
import asyncio
import aiohttp
import argparse
import difflib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import statistics

# ==================== 常量配置 ====================
INVITE_CODE = os.getenv("MAISHOU_INVITE_CODE") or "6110440"
HEADERS = {
    aiohttp.hdrs.ACCEPT: "application/json",
    aiohttp.hdrs.REFERER: "https://hnbc018.kuaizhan.com/",
    aiohttp.hdrs.USER_AGENT: "Mozilla/5.0 AppleWebKit/537 Chrome/143 Safari/537",
}
SESSION: aiohttp.ClientSession | None = None

# 数据存储路径
DATA_DIR = Path(__file__).parent.parent / "data"
SUPPLIERS_FILE = DATA_DIR / "suppliers.json"
GOODS_CACHE_DIR = DATA_DIR / "cache"
REPORTS_DIR = DATA_DIR / "reports"

# 相对市场均价的偏差率 |(供价-均价)/均价| —— 用于上下架（与最低价无关）
THRESHOLD_AVG_AUTO_LIST = 0.10   # ±10% 内 → 自动上架
THRESHOLD_AVG_REVIEW = 0.20      # 10%～20% → 审核；>20% → 下架
SALES_CHECK_DAYS = 14  # 14天无销量检查

# 平台映射
PLATFORM_MAP = {
    0: "全部",
    1: "淘宝/天猫",
    2: "京东",
    3: "拼多多",
    4: "苏宁",
    5: "唯品会",
    6: "考拉",
    7: "抖音",
    8: "快手",
    10: "1688"
}

# ==================== 数据模型 ====================
@dataclass
class SupplierGoods:
    """供应商商品"""
    id: str                          # 唯一ID
    name: str                         # 物品名称
    brand: str                        # 品牌
    model: str                        # 型号
    spec: str                         # 规格
    price: float                      # 销售价格
    supplier_name: str = ""           # 供应商名称
    created_at: str = ""              # 创建时间
    updated_at: str = ""              # 更新时间
    status: str = "pending"           # pending/review/listed/delisted
    last_sales_check: str = ""        # 最后销量检查时间
    sales_count: int = 0              # 销量

@dataclass
class MarketMatch:
    """市场匹配结果"""
    platform: str                     # 平台
    title: str                        # 商品标题
    shop_name: str                    # 店铺名称
    original_price: float             # 原价
    actual_price: float               # 实际到手价
    coupon_price: float               # 优惠券
    month_sales: int                  # 月销量
    similarity: float                  # 相似度分数
    match_type: str                   # exact/similar/none
    goods_id: str = ""                # 商品ID

@dataclass
class PriceAnalysis:
    """价格分析结果"""
    supplier_price: float
    lowest_price: float
    lowest_price_with_coupon: float
    avg_price: float
    deviation_rate: float             # 偏差率 (供应商价-最低价)/最低价
    deviation_rate_with_coupon: float # 使用优惠券后的偏差率
    deviation_from_avg: float         # (供应商价-市场均价)/市场均价，用于上下架判断
    lowest_platform: str
    market_matches: List[MarketMatch]

# ==================== NLP 相似度匹配 ====================
class NLPMatcher:
    """NLP 相似度匹配器"""

    # 品牌别名映射
    BRAND_ALIASES = {
        'puma': ['puma', '彪马', 'puma彪马', 'pumapuma'],
        'nike': ['nike', '耐克', 'nike耐克', 'nk'],
        'adidas': ['adidas', '阿迪达斯', '阿迪', 'adidas阿迪'],
        'newbalance': ['newbalance', 'new balance', 'nb', '新百伦'],
        'converse': ['converse', '匡威', 'converse匡威'],
        'vans': ['vans', '万斯'],
        'anta': ['anta', '安踏', 'anta安踏'],
        'lining': ['lining', '李宁', 'lining李宁'],
        'huawei': ['huawei', '华为'],
        'apple': ['apple', '苹果', 'iphone'],
        'xiaomi': ['xiaomi', '小米', 'mi'],
        'samsung': ['samsung', '三星'],
    }

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 4),
            max_features=5000
        )

    def preprocess(self, text: str) -> str:
        """预处理文本"""
        import re
        # 转小写
        text = text.lower()
        # 移除特殊字符，保留中文、英文、数字
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)
        # 合并多个空格
        text = ' '.join(text.split())
        return text

    def levenshtein_similarity(self, s1: str, s2: str) -> float:
        """编辑距离相似度"""
        if not s1 or not s2:
            return 0.0

        len1, len2 = len(s1), len(s2)
        if len1 > len2:
            s1, s2 = s2, s1
            len1, len2 = len2, len1

        # 只需要两行
        prev_row = list(range(len1 + 1))
        curr_row = [0] * (len1 + 1)

        for i in range(1, len2 + 1):
            curr_row[0] = i
            for j in range(1, len1 + 1):
                cost = 0 if s2[i-1] == s1[j-1] else 1
                curr_row[j] = min(
                    prev_row[j] + 1,      # 删除
                    curr_row[j-1] + 1,    # 插入
                    prev_row[j-1] + cost  # 替换
                )
            prev_row, curr_row = curr_row, prev_row

        distance = prev_row[len1]
        max_len = max(len1, len2)
        return 1 - (distance / max_len) if max_len > 0 else 0.0

    def jaccard_similarity(self, s1: str, s2: str, n: int = 2) -> float:
        """Jaccard 相似度（基于 n-gram）"""
        def get_ngrams(s, n):
            return set(s[i:i+n] for i in range(len(s)-n+1))

        if not s1 or not s2:
            return 0.0

        ngrams1 = get_ngrams(s1, n)
        ngrams2 = get_ngrams(s2, n)

        if not ngrams1 or not ngrams2:
            return 0.0

        intersection = ngrams1 & ngrams2
        union = ngrams1 | ngrams2

        return len(intersection) / len(union) if union else 0.0

    def cosine_similarity(self, texts: List[str]) -> np.ndarray:
        """TF-IDF 余弦相似度"""
        if len(texts) < 2:
            return np.array([1.0])

        try:
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarities = cosine_similarity(tfidf_matrix)
            return similarities
        except:
            # 如果 TF-IDF 失败，返回 0
            return np.zeros((len(texts), len(texts)))

    def check_brand_match(self, brand: str, text: str) -> float:
        """检查品牌是否匹配，支持别名"""
        brand_lower = brand.lower()
        text_lower = text.lower()

        # 直接检查
        if brand_lower in text_lower:
            return 1.0

        # 检查别名
        brand_key = brand_lower.replace(' ', '')
        if brand_key in self.BRAND_ALIASES:
            aliases = self.BRAND_ALIASES[brand_key]
            for alias in aliases:
                if alias in text_lower:
                    return 1.0

        # 检查型号中的品牌关键词
        for key, aliases in self.BRAND_ALIASES.items():
            if key in brand_lower:
                for alias in aliases:
                    if alias in text_lower:
                        return 0.8  # 间接匹配

        return 0.0

    def extract_spec_features(self, text: str) -> Dict[str, List[str]]:
        """抽取规格特征（尺码/颜色/容量），用于弱结构化匹配"""
        import re
        clean = self.preprocess(text)

        size_tokens = re.findall(r'\b\d{2}(?:\.\d)?\s*(?:码|号|cm|mm)?\b', clean)
        storage_tokens = re.findall(r'\b\d+\s*(?:gb|tb|ml|l|kg|g|寸|英寸)\b', clean)

        color_vocab = [
            '黑色', '白色', '蓝色', '红色', '绿色', '粉色', '紫色', '灰色', '棕色', '卡其',
            'black', 'white', 'blue', 'red', 'green', 'pink', 'purple', 'gray', 'grey', 'brown'
        ]
        color_tokens = [c for c in color_vocab if c in clean]

        return {
            'size': list(set(size_tokens)),
            'color': list(set(color_tokens)),
            'storage': list(set(storage_tokens)),
        }

    def feature_overlap_score(self, supplier_vals: List[str], market_vals: List[str]) -> float:
        """
        规格维度匹配分:
        - 双方都有且相交 -> 1.0
        - 双方都有但冲突 -> 0.0
        - 至少一方缺失 -> 0.5（未知，不重罚）
        """
        if not supplier_vals or not market_vals:
            return 0.5
        return 1.0 if set(supplier_vals) & set(market_vals) else 0.0

    def match_score(self, supplier_goods: SupplierGoods, market_title: str) -> float:
        """综合匹配分数"""
        # 构建供应商商品关键词（规格不参与）
        supplier_keywords = f"{supplier_goods.brand} {supplier_goods.name} {supplier_goods.model}"
        supplier_text = self.preprocess(supplier_keywords)
        market_text = self.preprocess(market_title)

        # 1. 品牌匹配（支持别名）
        brand_match = self.check_brand_match(supplier_goods.brand, market_text)

        # 2. 物品名称匹配（优先）
        name_keyword = self.preprocess(supplier_goods.name)
        name_in_title = 1.0 if name_keyword and name_keyword in market_text else 0.0
        name_similarity = self.levenshtein_similarity(name_keyword, market_text) if name_keyword else 0.0
        name_score = max(name_in_title, name_similarity)

        # 3. 型号匹配（辅助）
        model_keyword = self.preprocess(supplier_goods.model)
        model_in_title = 1.0 if model_keyword and model_keyword in market_text else 0.0
        model_similarity = self.levenshtein_similarity(model_keyword, market_text) if model_keyword else 0.0
        model_similarity = max(model_in_title, model_similarity)

        # 4. 整体文本余弦相似度（兜底）
        cos_sim = self.cosine_similarity([supplier_text, market_text])[0, 1]

        # 综合分数：品牌 + 物品名称为主，型号和整体相似度为辅
        final_score = (
            brand_match * 0.45 +      # 品牌权重 45%
            name_score * 0.4 +        # 名称权重 40%
            model_similarity * 0.1 +  # 型号权重 10%
            cos_sim * 0.05            # 整体相似度权重 5%
        )

        return round(final_score, 4)

    def match(self, supplier_goods: SupplierGoods, market_results: List[Dict],
              threshold: float = 0.45) -> List[MarketMatch]:
        """匹配供应商商品与市场商品"""
        matches = []

        for item in market_results:
            title = item.get('title', '')
            score = self.match_score(supplier_goods, title)

            # 判断匹配类型
            if score >= 0.75:
                match_type = "exact"  # 精确匹配
            elif score >= threshold:
                match_type = "similar"  # 相似匹配
            else:
                match_type = "none"

            if match_type != "none":
                match = MarketMatch(
                    platform=PLATFORM_MAP.get(item.get('sourceType', 0), "未知"),
                    title=title[:100],  # 截断长标题
                    shop_name=item.get('shopName', ''),
                    original_price=float(item.get('originalPrice', 0)),
                    actual_price=float(item.get('actualPrice', 0)),
                    coupon_price=float(item.get('couponPrice', 0)),
                    month_sales=self._parse_sales(item.get('monthSales', '0')),
                    similarity=score,
                    match_type=match_type,
                    goods_id=item.get('goodsId', '')
                )
                matches.append(match)

        # 按相似度排序
        matches.sort(key=lambda x: x.similarity, reverse=True)
        return matches

    def _parse_sales(self, sales_str: str) -> int:
        """解析销量字符串"""
        if isinstance(sales_str, int):
            return sales_str

        sales_str = str(sales_str).replace('+', '').replace('万', '')

        try:
            if '万' in str(sales_str):
                return int(float(sales_str.replace('万', '')) * 10000)
            return int(sales_str)
        except:
            return 0

# ==================== 数据存储 ====================
class DataStore:
    """数据存储器"""

    def __init__(self):
        self.data_dir = DATA_DIR
        self.suppliers_file = SUPPLIERS_FILE
        self.cache_dir = GOODS_CACHE_DIR
        self.reports_dir = REPORTS_DIR
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保目录存在"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def _get_timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def load_suppliers(self) -> List[SupplierGoods]:
        """加载供应商商品"""
        if not self.suppliers_file.exists():
            return []

        try:
            with open(self.suppliers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [SupplierGoods(**item) for item in data]
        except Exception as e:
            print(f"加载供应商数据失败: {e}")
            return []

    def save_suppliers(self, suppliers: List[SupplierGoods]):
        """保存供应商商品"""
        self._ensure_dirs()

        data = [asdict(s) for s in suppliers]
        with open(self.suppliers_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                pass

    def generate_id(self) -> str:
        """生成唯一ID"""
        import hashlib
        import time
        raw = f"{time.time()}{os.getpid()}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    def save_report(self, goods_id: str, content: str) -> str:
        """保存审核报告"""
        self._ensure_dirs()
        filename = f"report_{goods_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.reports_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

# ==================== API 接口 ====================
async def search(keyword, source=0, func=None, **kwargs):
    """搜索市场商品"""
    resp = await SESSION.post(
        "https://appapi.maishou88.com/api/v1/homepage/searchList",
        headers={
            **HEADERS,
            aiohttp.hdrs.USER_AGENT: "MaiShouApp/3.7.7 (iPhone; iOS 26.3; Scale/3.00)",
            "openid": "564bdce0fa408fc9e1d5d42fd022ef0b",
            "version": "3.7.7.2",
        },
        data={
            "isCoupon": 0,
            "keyword": str(keyword),
            "openid": "564bdce0fa408fc9e1d5d42fd022ef0b",
            "order": "desc",
            "page": kwargs.get('page', 1),
            "pddListId": "",
            "sort": "",
            "sourceType": str(source),
            "user_id": "",
        },
    )
    data = await resp.json(encoding="utf-8-sig") or {}
    rows = data.pop("data", [])

    if not rows:
        return data.get("message") or await resp.text()

    idx = 0
    rows = [
        {
            "idx": idx,
            "goodsId": v.get("goodsId"),
            "sourceType": v.get("sourceType"),
            "title": v.get("title"),
            "shopName": v.get("shopName"),
            "originalPrice": v.get("originalPrice"),
            "actualPrice": v.get("actualPrice"),
            "couponPrice": v.get("couponPrice"),
            "monthSales": v.get("monthSales"),
            "picUrl": v.get("picUrl"),
        }
        for v in rows
        if (idx := idx + 1)
    ]

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    for item in rows:
        writer.writerow(item)

    text = output.getvalue()
    output.close()
    return text

async def get_market_price(brand: str, model: str, spec: str, name: str = "",
                           source: int = 0, page: int = 1) -> List[Dict]:
    """获取市场价格"""
    # 构建搜索关键词
    keyword = f"{brand} {model} {spec} {name}".strip()

    resp = await SESSION.post(
        "https://appapi.maishou88.com/api/v1/homepage/searchList",
        headers={
            **HEADERS,
            aiohttp.hdrs.USER_AGENT: "MaiShouApp/3.7.7 (iPhone; iOS 26.3; Scale/3.00)",
            "openid": "564bdce0fa408fc9e1d5d42fd022ef0b",
            "version": "3.7.7.2",
        },
        data={
            "isCoupon": 0,
            "keyword": keyword,
            "openid": "564bdce0fa408fc9e1d5d42fd022ef0b",
            "order": "desc",
            "page": page,
            "pddListId": "",
            "sort": "",
            "sourceType": str(source),
            "user_id": "",
        },
    )

    data = await resp.json(encoding="utf-8-sig") or {}
    return data.get("data", [])

def _trimmed_mean_prices(prices: List[float]) -> float:
    """去掉排序后两端各约 10% 再算平均，避免少数极端价拉偏中心。"""
    if not prices:
        return 0.0
    s = sorted(prices)
    n = len(s)
    if n <= 2:
        return sum(s) / n
    k = max(1, n // 10)
    core = s[k : n - k]
    if not core:
        core = s
    return sum(core) / len(core)


def _filter_matches_by_price_band(
    matches: List[MarketMatch], center: float, low_ratio: float, high_ratio: float
) -> List[MarketMatch]:
    if center <= 0:
        return list(matches)
    lo = max(1.0, center * low_ratio)
    hi = center * high_ratio
    return [m for m in matches if lo <= m.actual_price <= hi]


# ==================== 价格分析 ====================
def analyze_price(supplier_goods: SupplierGoods, matches: List[MarketMatch]) -> PriceAnalysis:
    """分析价格"""
    if not matches:
        return PriceAnalysis(
            supplier_price=supplier_goods.price,
            lowest_price=0,
            lowest_price_with_coupon=0,
            avg_price=0,
            deviation_rate=0,
            deviation_rate_with_coupon=0,
            deviation_from_avg=0,
            lowest_platform="无匹配",
            market_matches=[]
        )

    # 过滤有效匹配
    valid_matches = [m for m in matches if m.match_type != "none" and m.actual_price > 0]

    if not valid_matches:
        return PriceAnalysis(
            supplier_price=supplier_goods.price,
            lowest_price=0,
            lowest_price_with_coupon=0,
            avg_price=0,
            deviation_rate=0,
            deviation_rate_with_coupon=0,
            deviation_from_avg=0,
            lowest_platform="无匹配",
            market_matches=matches
        )

    # 价格分析使用更可靠的子集，避免 9.9 这类离群值污染结果
    # 1) 优先保留高相似度候选
    reliable_matches = [m for m in valid_matches if m.similarity >= 0.62]
    pricing_candidates = reliable_matches if len(reliable_matches) >= 3 else valid_matches

    # 2) 用「修剪平均」做中心，再按区间过滤；不再在样本少时回退到未过滤全量（否则 9.8 会重新进来）
    prices = [m.actual_price for m in pricing_candidates]
    center = _trimmed_mean_prices(prices)
    bounded_matches = _filter_matches_by_price_band(pricing_candidates, center, 0.50, 1.80)

    if len(bounded_matches) < 1:
        center = statistics.median(prices)
        bounded_matches = _filter_matches_by_price_band(pricing_candidates, center, 0.45, 2.00)
    if len(bounded_matches) < 1:
        bounded_matches = _filter_matches_by_price_band(pricing_candidates, center, 0.30, 2.50)

    pricing_matches = bounded_matches if bounded_matches else pricing_candidates

    def effective_price(match: MarketMatch) -> float:
        coupon = max(0.0, match.coupon_price)
        return max(0.01, match.actual_price - coupon)

    # 计算最低价（基于过滤后的可信集合）
    lowest = min(pricing_matches, key=lambda x: x.actual_price)
    lowest_with_coupon = min(pricing_matches, key=effective_price)

    # 计算平均价
    avg_price = sum(m.actual_price for m in pricing_matches) / len(pricing_matches)

    # 计算偏差率
    deviation_rate = (supplier_goods.price - lowest.actual_price) / lowest.actual_price if lowest.actual_price > 0 else 0
    lowest_coupon_price = effective_price(lowest_with_coupon)
    deviation_rate_with_coupon = (supplier_goods.price - lowest_coupon_price) / lowest_coupon_price if lowest_coupon_price > 0 else 0
    # 保留 6 位小数，避免 float 在 ±10% 边界误判成「审核」而界面仍显示「合理」
    deviation_from_avg = (
        round((supplier_goods.price - avg_price) / avg_price, 6) if avg_price > 0 else 0.0
    )

    return PriceAnalysis(
        supplier_price=supplier_goods.price,
        lowest_price=lowest.actual_price,
        lowest_price_with_coupon=lowest_coupon_price,
        avg_price=avg_price,
        deviation_rate=deviation_rate,
        deviation_rate_with_coupon=deviation_rate_with_coupon,
        deviation_from_avg=deviation_from_avg,
        lowest_platform=lowest.platform,
        market_matches=pricing_matches
    )

# ==================== 上下架判断 ====================
def should_list(analysis: PriceAnalysis, sales_count: int) -> Tuple[str, str]:
    """判断是否应该上架：相对市场均价，|偏差|≤10% 上架，10%～20% 审核，>20% 下架"""
    # 无匹配商品
    if not analysis.market_matches:
        return "review", "无法匹配到同款商品，需人工审核"

    if analysis.avg_price <= 0:
        return "review", "无法计算市场均价，需人工审核"

    d = round(float(analysis.deviation_from_avg), 6)
    d_pct = d * 100
    ad = abs(d)
    _eps = 1e-9

    if ad <= THRESHOLD_AVG_AUTO_LIST + _eps:
        return "listed", (
            f"相对市场均价偏差 {d_pct:+.1f}%（±{THRESHOLD_AVG_AUTO_LIST*100:.0f}% 内），建议直接上架"
        )
    if ad <= THRESHOLD_AVG_REVIEW + _eps:
        return "review", (
            f"相对市场均价偏差 {d_pct:+.1f}%（{THRESHOLD_AVG_AUTO_LIST*100:.0f}%～{THRESHOLD_AVG_REVIEW*100:.0f}%），建议人工审核"
        )
    return "delisted", (
        f"相对市场均价偏差 {d_pct:+.1f}%（超过 ±{THRESHOLD_AVG_REVIEW*100:.0f}%），建议下架"
    )

def check_sales_status(goods: SupplierGoods) -> Tuple[bool, str]:
    """检查销量状态"""
    if not goods.last_sales_check:
        return True, "首次检查"

    try:
        last_check = datetime.strptime(goods.last_sales_check, "%Y-%m-%d %H:%M:%S")
        days_since_check = (datetime.now() - last_check).days

        if days_since_check >= SALES_CHECK_DAYS:
            if goods.sales_count == 0:
                return False, f"已连续 {days_since_check} 天无销量，触发下架"
            else:
                return True, f"最近 {days_since_check} 天内有销量 {goods.sales_count}"

        return True, f"距离上次检查 {days_since_check} 天"
    except:
        return True, "无法解析检查时间"

# ==================== 报告生成 ====================
def generate_report(goods: SupplierGoods, analysis: PriceAnalysis,
                   action: str, reason: str) -> str:
    """生成 Markdown 审核报告"""

    d_avg = analysis.deviation_from_avg
    d_avg_pct = d_avg * 100

    report = f"""# 供应商商品审核报告

## 📦 商品信息

| 字段 | 内容 |
|------|------|
| **商品ID** | `{goods.id}` |
| **物品名称** | {goods.name} |
| **品牌** | {goods.brand} |
| **型号** | {goods.model} |
| **规格** | {goods.spec} |
| **供应商报价** | ¥{goods.price:.2f} |
| **供应商名称** | {goods.supplier_name or "未填写"} |
| **录入时间** | {goods.created_at} |
| **更新时间** | {goods.updated_at} |

---

## 🔍 同款匹配结果

### 匹配方式
- **NLP 相似度匹配**：品牌 + 型号 + 规格 综合评分
- **匹配阈值**：≥ 60% 视为相似，≥ 85% 视为同款

### 匹配详情

"""

    # 添加匹配商品列表
    if analysis.market_matches:
        for i, match in enumerate(analysis.market_matches[:5], 1):
            report += f"""#### {i}. {match.platform} - {match.title[:50]}...

| 字段 | 内容 |
|------|------|
| 店铺 | {match.shop_name} |
| 原价 | ¥{match.original_price:.2f} |
| 券后价 | ¥{match.actual_price:.2f} |
| 优惠券 | ¥{match.coupon_price:.2f} |
| 月销量 | {match.month_sales} |
| 相似度 | {match.similarity*100:.1f}% |
| 匹配类型 | {match.match_type} |

"""
    else:
        report += "> ⚠️ 未匹配到同款商品\n\n"

    report += f"""---

## 📊 外部价格分析

| 指标 | 数值 |
|------|------|
| **市场最低价** | ¥{analysis.lowest_price:.2f} |
| **市场最低到手价** | ¥{analysis.lowest_price_with_coupon:.2f} |
| **市场平均价** | ¥{analysis.avg_price:.2f} |
| **最低价平台** | {analysis.lowest_platform} |

---

## ⚠️ 核心指标

### 相对市场均价（上下架依据）

> **计算公式**: (供应商价 - 市场均价) / 市场均价

| 指标 | 数值 | 说明 |
|------|------|------|
| 相对均价偏差 | {d_avg_pct:+.2f}% | 绝对值 ≤10% 上架，10%～20% 审核，>20% 下架 |
| 相对最低价(标价) | {analysis.deviation_rate*100:.2f}% | 仅供参考 |
| 相对最低到手价 | {analysis.deviation_rate_with_coupon*100:.2f}% | 仅供参考 |

### 市场需求

| 指标 | 数值 |
|------|------|
| 最高月销量 | {max((m.month_sales for m in analysis.market_matches), default=0)} |
| 有销量商品数 | {sum(1 for m in analysis.market_matches if m.month_sales > 0)} |

---

## 🎯 系统判断

### 判断结果

| 状态 | 说明 |
|------|------|
| **系统建议** | {"✅ 建议上架" if action == "listed" else "🔍 需要审核" if action == "review" else "❌ 建议拒绝"} |
| **判断原因** | {reason} |

### 阈值参考（相对市场均价）

| 阈值类型 | 数值 | 说明 |
|----------|------|------|
| 自动上架 | 偏差绝对值 ≤ {THRESHOLD_AVG_AUTO_LIST*100:.0f}% | 供货价接近市场均价 |
| 人工审核 | {THRESHOLD_AVG_AUTO_LIST*100:.0f}% ＜ 偏差绝对值 ≤ {THRESHOLD_AVG_REVIEW*100:.0f}% | 偏离适中 |
| 建议下架 | 偏差绝对值 ＞ {THRESHOLD_AVG_REVIEW*100:.0f}% | 偏离过大（偏高或偏低） |

---

## 📝 审核意见

> 请审核人员根据以上分析，结合实际情况给出最终判断。

**审核人**: _______________

**审核时间**: _______________

**审核结果**:
- [ ] 同意上架
- [ ] 需修改价格
- [ ] 拒绝上架
- [ ] 其他意见：_______________

---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    return report

# ==================== CLI 命令实现 ====================
async def cmd_add(args, store: DataStore, matcher: NLPMatcher):
    """添加供应商商品"""
    goods = SupplierGoods(
        id=store.generate_id(),
        name=args.name,
        brand=args.brand,
        model=args.model,
        spec=args.spec,
        price=args.price,
        supplier_name=args.supplier or "",
        created_at=store._get_timestamp(),
        updated_at=store._get_timestamp(),
        status="pending"
    )

    suppliers = store.load_suppliers()
    suppliers.append(goods)
    store.save_suppliers(suppliers)

    print(f"✅ 商品添加成功！")
    print(f"   商品ID: {goods.id}")
    print(f"   名称: {goods.name}")
    print(f"   品牌: {goods.brand}")
    print(f"   型号: {goods.model}")
    print(f"   规格: {goods.spec}")
    print(f"   价格: ¥{goods.price:.2f}")

async def cmd_list(args, store: DataStore):
    """列出供应商商品"""
    suppliers = store.load_suppliers()

    if not suppliers:
        print("📭 暂无供应商商品，请先添加商品")
        return

    # 过滤
    if args.brand:
        suppliers = [s for s in suppliers if args.brand.lower() in s.brand.lower()]
    if args.status:
        suppliers = [s for s in suppliers if s.status == args.status]

    print(f"\n📦 供应商商品列表 (共 {len(suppliers)} 件)")
    print("=" * 80)

    for s in suppliers:
        status_icon = {"pending": "⏳", "review": "🔍", "listed": "✅", "delisted": "❌"}.get(s.status, "?")
        print(f"{status_icon} [{s.status.upper():8}] {s.brand} {s.model} - ¥{s.price:.2f}")
        print(f"   ID: {s.id} | 规格: {s.spec} | 录入: {s.created_at[:10]}")

    print("=" * 80)

async def cmd_update(args, store: DataStore):
    """更新供应商商品"""
    suppliers = store.load_suppliers()

    for i, s in enumerate(suppliers):
        if s.id == args.id:
            if args.price is not None:
                s.price = args.price
            if args.status:
                s.status = args.status
            s.updated_at = store._get_timestamp()

            store.save_suppliers(suppliers)
            print(f"✅ 商品更新成功: {s.brand} {s.model}")
            return

    print(f"❌ 未找到商品ID: {args.id}")

async def cmd_delete(args, store: DataStore):
    """删除供应商商品"""
    suppliers = store.load_suppliers()
    original_len = len(suppliers)

    suppliers = [s for s in suppliers if s.id != args.id]

    if len(suppliers) == original_len:
        print(f"❌ 未找到商品ID: {args.id}")
        return

    store.save_suppliers(suppliers)
    print(f"✅ 商品删除成功")

async def cmd_analyze(args, store: DataStore, matcher: NLPMatcher):
    """分析供应商商品"""
    suppliers = store.load_suppliers()

    # 找到目标商品
    target = None
    for s in suppliers:
        if s.id == args.id:
            target = s
            break

    if not target:
        print(f"❌ 未找到商品ID: {args.id}")
        return

    print(f"\n🔍 正在分析商品: {target.brand} {target.model} {target.spec}")
    print(f"   供应商报价: ¥{target.price:.2f}")
    print(f"   搜索平台: {PLATFORM_MAP.get(args.source, '全部')}")
    print()

    # 搜索市场数据
    print("📡 正在搜索市场数据...")
    market_results = await get_market_price(
        target.brand, target.model, target.spec, target.name, args.source, args.page
    )

    if not market_results:
        print("❌ 未搜索到市场数据")
        return

    print(f"   找到 {len(market_results)} 条市场数据")

    # NLP 匹配
    print("🧠 正在进行 NLP 相似度匹配...")
    matches = matcher.match(target, market_results, threshold=0.5)
    print(f"   匹配到 {len(matches)} 个相似商品")

    # 价格分析
    analysis = analyze_price(target, matches)

    print("\n📊 价格分析结果:")
    print(f"   市场最低价: ¥{analysis.lowest_price:.2f}")
    print(f"   市场最低到手价: ¥{analysis.lowest_price_with_coupon:.2f}")
    print(f"   市场平均价: ¥{analysis.avg_price:.2f}")
    print(f"   最低价平台: {analysis.lowest_platform}")

    # 上下架判断
    action, reason = should_list(analysis, target.sales_count)
    print(f"\n🎯 系统建议: {action.upper()}")
    print(f"   原因: {reason}")

    # 更新商品状态
    target.status = action
    target.updated_at = store._get_timestamp()

    if args.save:
        store.save_suppliers(suppliers)

        # 生成报告
        if action == "review":
            report = generate_report(target, analysis, action, reason)
            report_path = store.save_report(target.id, report)
            print(f"\n📄 审核报告已生成: {report_path}")
        else:
            print("\n💡 提示: 使用 --save 参数保存后会自动更新商品状态")

async def cmd_batch_analyze(args, store: DataStore, matcher: NLPMatcher):
    """批量分析供应商商品"""
    suppliers = store.load_suppliers()

    # 过滤待审核商品
    if args.status:
        targets = [s for s in suppliers if s.status == args.status]
    else:
        targets = [s for s in suppliers if s.status == "pending"]

    if not targets:
        print("📭 没有待分析的供应商商品")
        return

    print(f"\n🔍 批量分析 {len(targets)} 件商品...")
    print()

    results = []
    for i, target in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] 分析: {target.brand} {target.model}...", end=" ")

        try:
            # 搜索市场数据
            market_results = await get_market_price(
                target.brand, target.model, target.spec, target.name, args.source, 1
            )

            if market_results:
                matches = matcher.match(target, market_results, threshold=0.5)
                analysis = analyze_price(target, matches)
                action, reason = should_list(analysis, target.sales_count)
            else:
                matches = []
                analysis = analyze_price(target, [])
                action, reason = "review", "无法获取市场数据"

            target.status = action
            target.updated_at = store._get_timestamp()

            results.append({
                "id": target.id,
                "name": f"{target.brand} {target.model}",
                "price": target.price,
                "lowest_price": analysis.lowest_price,
                "deviation_rate": analysis.deviation_from_avg,
                "action": action,
                "reason": reason,
                "matches": matches
            })

            print(f"✅ {action.upper()}")

        except Exception as e:
            print(f"❌ 失败: {e}")
            results.append({
                "id": target.id,
                "name": f"{target.brand} {target.model}",
                "action": "error",
                "reason": str(e)
            })

    # 保存结果
    if args.save:
        store.save_suppliers(suppliers)

    # 生成汇总报告
    print("\n" + "=" * 80)
    print("📊 批量分析汇总")
    print("=" * 80)

    stats = {"listed": 0, "review": 0, "delisted": 0, "rejected": 0}
    for r in results:
        if r["action"] in stats:
            stats[r["action"]] += 1

    print(f"\n✅ 建议上架: {stats['listed']} 件")
    print(f"🔍 需要审核: {stats['review']} 件")
    print(f"❌ 建议下架: {stats['delisted']} 件")
    print(f"🚫 异常拒绝: {stats['rejected']} 件")

    # 详细列表
    print("\n详细列表:")
    print("-" * 80)
    for r in results:
        icon = {"listed": "✅", "review": "🔍", "delisted": "❌", "rejected": "🚫", "error": "⚠️"}.get(r["action"], "?")
        rate = r.get("deviation_rate", 0) * 100
        print(f"{icon} {r['name'][:30]:32} | ¥{r.get('price', 0):7.2f} | {rate:6.1f}% | {r['action'].upper()}")

    print("-" * 80)

    # 生成 Markdown 汇总报告
    if args.save and args.report:
        summary = f"""# 批量商品分析报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计汇总

| 状态 | 数量 |
|------|------|
| ✅ 建议上架 | {stats['listed']} |
| 🔍 需要审核 | {stats['review']} |
| ❌ 建议下架 | {stats['delisted']} |
| 🚫 异常拒绝 | {stats['rejected']} |

## 详细列表

| 商品 | 供应商价 | 最低市场价 | 偏差率 | 系统建议 |
|------|----------|------------|--------|----------|
"""

        for r in results:
            rate = r.get("deviation_rate", 0) * 100
            summary += f"| {r['name']} | ¥{r.get('price', 0):.2f} | ¥{r.get('lowest_price', 0):.2f} | {rate:.1f}% | {r['action'].upper()} |\n"

        report_path = store.save_report("batch", summary)
        print(f"\n📄 汇总报告已生成: {report_path}")

async def cmd_report(args, store: DataStore, matcher: NLPMatcher):
    """生成审核报告"""
    suppliers = store.load_suppliers()

    target = None
    for s in suppliers:
        if s.id == args.id:
            target = s
            break

    if not target:
        print(f"❌ 未找到商品ID: {args.id}")
        return

    print(f"\n📄 正在生成审核报告...")

    # 重新分析
    market_results = await get_market_price(
        target.brand, target.model, target.spec, target.name, args.source, args.page
    )

    if market_results:
        matches = matcher.match(target, market_results, threshold=0.5)
        analysis = analyze_price(target, matches)
        action, reason = should_list(analysis, target.sales_count)
    else:
        matches = []
        analysis = analyze_price(target, [])
        action, reason = "review", "无法获取市场数据"

    # 生成报告
    report = generate_report(target, analysis, action, reason)

    # 保存
    report_path = store.save_report(target.id, report)

    print(f"✅ 审核报告已生成: {report_path}")

    # 打印报告内容（简要）
    print("\n" + "=" * 80)
    print("📋 报告预览:")
    print("=" * 80)
    print(report[:1500] + "..." if len(report) > 1500 else report)
    print("=" * 80)

async def main():
    global SESSION

    # 初始化
    store = DataStore()
    matcher = NLPMatcher()

    async with aiohttp.ClientSession(headers=HEADERS) as SESSION:
        parser = argparse.ArgumentParser(description='供应商商品比价管理系统')
        subparsers = parser.add_subparsers(dest='command')

        # 添加商品
        add_parser = subparsers.add_parser('add', help='添加供应商商品')
        add_parser.add_argument('--name', required=True, help='物品名称')
        add_parser.add_argument('--brand', required=True, help='品牌')
        add_parser.add_argument('--model', required=True, help='型号')
        add_parser.add_argument('--spec', required=True, help='规格')
        add_parser.add_argument('--price', type=float, required=True, help='销售价格')
        add_parser.add_argument('--supplier', help='供应商名称')

        # 列出商品
        list_parser = subparsers.add_parser('list', help='列出供应商商品')
        list_parser.add_argument('--brand', help='按品牌筛选')
        list_parser.add_argument('--status', help='按状态筛选 (pending/review/listed/delisted)')

        # 更新商品
        update_parser = subparsers.add_parser('update', help='更新供应商商品')
        update_parser.add_argument('--id', required=True, help='商品ID')
        update_parser.add_argument('--price', type=float, help='新价格')
        update_parser.add_argument('--status', help='新状态')

        # 删除商品
        delete_parser = subparsers.add_parser('delete', help='删除供应商商品')
        delete_parser.add_argument('--id', required=True, help='商品ID')

        # 分析商品
        analyze_parser = subparsers.add_parser('analyze', help='分析单个商品')
        analyze_parser.add_argument('--id', required=True, help='商品ID')
        analyze_parser.add_argument('--source', type=int, default=0, help='搜索平台 (0=全部,1=淘宝,2=京东,3=拼多多)')
        analyze_parser.add_argument('--page', type=int, default=1, help='搜索页码')
        analyze_parser.add_argument('--save', action='store_true', help='保存分析结果')

        # 批量分析
        batch_parser = subparsers.add_parser('batch-analyze', help='批量分析商品')
        batch_parser.add_argument('--status', help='按状态筛选')
        batch_parser.add_argument('--source', type=int, default=0, help='搜索平台')
        batch_parser.add_argument('--save', action='store_true', help='保存分析结果')
        batch_parser.add_argument('--report', action='store_true', help='生成汇总报告')

        # 生成报告
        report_parser = subparsers.add_parser('report', help='生成审核报告')
        report_parser.add_argument('--id', required=True, help='商品ID')
        report_parser.add_argument('--source', type=int, default=0, help='搜索平台')
        report_parser.add_argument('--page', type=int, default=1, help='搜索页码')

        # 原有搜索命令（保留兼容）
        search_parser = subparsers.add_parser('search', help='搜索市场商品')
        search_parser.add_argument('--keyword', help='关键词')
        search_parser.add_argument('--source', default="1", help='来源')
        search_parser.add_argument('--page', type=int, default=1, help='分页')
        search_parser.set_defaults(func=search)

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return

        # 执行命令
        if args.command == 'add':
            await cmd_add(args, store, matcher)
        elif args.command == 'list':
            await cmd_list(args, store)
        elif args.command == 'update':
            await cmd_update(args, store)
        elif args.command == 'delete':
            await cmd_delete(args, store)
        elif args.command == 'analyze':
            await cmd_analyze(args, store, matcher)
        elif args.command == 'batch-analyze':
            await cmd_batch_analyze(args, store, matcher)
        elif args.command == 'report':
            await cmd_report(args, store, matcher)
        elif args.command == 'search':
            print(await search(**vars(args)))


if __name__ == "__main__":
    asyncio.run(main())
