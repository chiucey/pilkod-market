#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""industry_taxonomy.py — 行业/赛道归类规则（引擎通用版）。

设计原则：
  - 引擎只内置【通用品类词】（生活服务 / 内容社区 / 电商 / 硬件…），**不含任何具体公司名**；
  - 使用者把自己面过的公司填进 `config.yaml` 的 `industry_map`，即可得到自己的赛道归类；
  - 各分析脚本统一从这里取规则，避免同一套词表被复制到多个文件里。

config.yaml 写法（可选，见 config.example.yaml）：
  industry_map:
    某某公司: 生活服务/点评
    某硬件厂: 硬件系内容/商店
  categories:              # 可选：覆盖/补充下面的通用归类
    生活服务/点评: ["外卖", "到店", "酒店", "旅游"]
  company_scale:           # 可选：公司体量（大厂/中厂/小厂/创业团队）
    某某公司: 中厂
  main_tracks:             # 可选：你的主场赛道（"跨界一面挂告警"用）
    - 生活服务/点评
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

# 通用品类 → 关键词（不含任何具体公司名）
#
# ⚠️ 两个关键点（都是实测踩过的）：
#   1. 判定以【岗位/业务方向】为主，所以除了行业词，也要有方向词。
#   2. **顺序即优先级**（先命中先返回）。越具体的方向越要排在前面，
#      否则会被泛化词抢走。例：「到餐·内容运营」里如果"内容运营"排在
#      "生活服务"前面，就会被归成"内容/社区大厂"而不是"生活服务/点评"。
#      所以这里按「具体业务 → 泛能力」排列。
DEFAULT_TAXONOMY = {
    # ── 具体业务方向（优先判定）──
    # ⚠️ 「出海/国际化」的关键词**必须是业务词，不能只是市场/地域词**。
    #    教训：裸词 "海外" 会把「某大厂·浏览器海外业务·内容策略运营」整场
    #    吸进"出海/国际化"（因为"海外"先于"内容策略"命中）。
    #    但那是**内容策略**岗——"海外"只是它服务的市场，不是它的业务方向；
    #    同一个组做国内版就是内容策略，做海外版还是内容策略。
    #    实测：该类卡有 5 场被误归成"出海/国际化"，
    #    导致该赛道 11 场里有 5 场是假的，直接撑起了"第二好赛道"的排名。
    #    所以现在只保留**明确以出海为业务形态**的词
    #    （国际化/出海/跨境/多语言/本地化/海外发行…），
    #    而 "海外" 单独出现**不再**触发本赛道。
    "出海/国际化": ["国际化", "出海业务", "出海", "跨境", "多语言",
                   "海外发行", "海外运营", "海外内容", "本地化", "localization"],
    "B端/商家": ["B端", "商家", "供给运营", "商家运营", "服务商", "toB", "ToB", "快聘"],
    "招聘/人力": ["招聘", "人力", "蓝领", "灵活用工", "求职", "雇主"],
    "用户增长": ["用户增长", "增长", "拉新", "留存", "DNU", "促活"],
    "金融/财经": ["金融", "财经", "证券", "保险", "支付", "股票", "投顾"],
    "汽车/出行": ["汽车", "车企", "新能源车", "自动驾驶", "车展"],
    "教育/医疗": ["教育", "培训", "医疗", "健康", "医药", "医生", "课程"],
    "AI/工具": ["AI", "AIGC", "大模型", "工具", "SaaS", "效率", "数字人",
               "智能助手", "语音", "算法"],
    # ⚠️ 「硬件系内容/商店」的判据是**硬件这个行业**，不是"在哪做内容"。
    #    用户指出：「应用商店·品类经营·内容运营」「画报·内容运营」
    #    和「浏览器海外业务·内容策略运营」**本质是同一类岗** —— 都是内容策略，
    #    商店/画报/浏览器只是**载体/平台**，不是业务方向。
    #    这与"海外是市场不是方向"是同一条原则：
    #      载体词（浏览器/商店/画报/APP）≠ 行业归属。
    #    所以这里**移除** 应用商店 / 画报 —— 它们会把内容策略岗
    #    错误地吸到"硬件系"，而实际上该走泛内容类（内容/社区大厂）。
    #    保留的是真正的硬件行业词：公司/产品本身属于硬件赛道时才归这里。
    "硬件系内容/商店": ["硬件", "智能硬件", "电子书", "墨水屏", "IoT",
                      "可穿戴", "厂商", "设备"],
    # ⚠️ 「游戏/泛娱乐」只保留**行业本身**的词，不保留**内容题材**词。
    #    判据（用户两次纠正后总结）：题材 ≠ 行业。
    #      「某大厂·应用商店·品类经营·影视综方向」——"影视综"只是它经营的品类，
    #      岗位本质还是内容运营；若泛娱乐收了"影视/综艺"，
    #      这张卡会从内容策略被吸到"游戏/泛娱乐"。
    #    所以移除：影视 / 综艺 / 剧集 / 小说 / 短剧 / 音乐 / 音频
    #    （这些是"做什么内容"，不是"属于哪个行业"）。
    #    保留：游戏 / 动漫 / 二次元 / 泛娱乐 —— 这些通常指公司或业务的行业属性。
    "游戏/泛娱乐": ["游戏", "动漫", "二次元", "泛娱乐"],
    "电商/种草": ["电商", "种草", "购物", "门店", "导购", "品牌电商", "交易",
                 "商品", "选品", "带货"],
    # ── 泛内容类（放最后，避免抢走上面的具体业务）──
    # ⚠️ 这里原来叫「内容/社区大厂」，是一个**吞掉 68% 卡**的大桶，
    #    用户已删除它，并确认：**泛内容类一律算「内容运营」**。
    #    所以本条目 = 旧桶的关键词 → 收敛到「内容运营」这个名字。
    #    它必须留在**最后**：上面的行业词（金融/汽车/教育…）更具体，
    #    要先有机会命中；只有都说不上来时，才落到"这就是个内容岗"。
    #    关键词依据：用户自己的口径是"岗位名写了什么就是什么"，
    #    故这里收的都是**职能词**，不收行业词（行业词会劫持职能分类）。
    "内容运营": ["内容社区", "社区", "内容平台", "资讯", "短视频", "直播",
                "体育业务", "PGC", "UGC", "频道", "编辑", "机构运营",
                "图文", "论坛", "贴吧", "创作者", "作者", "UP主",
                "垂类内容", "内容运营", "内容策略", "内容生态", "信息流",
                "内容与用户", "品类经营"],
}


_CONFIG_CACHE = None
_CONFIG_LOADED = False


def _load_config():
    """读 config.yaml（**带进程内缓存**）。

    ⚠️ 必须缓存：这个函数原先每次调用都去 open + yaml.safe_load 一遍文件，
    而 classify() 每判一张卡都要调 taxonomy() → _load_config()。
    单次遍历 真实卡时这点开销看不出来，但 backtest 的留一法要跑
    O(n²) 次（每张卡都重算一遍桶），于是从不到 1 秒变成**跑不完**。
    配置在单次进程运行期间不会变，缓存是安全的。
    （若确实需要热重载，调 reload_config()。）
    """
    global _CONFIG_CACHE, _CONFIG_LOADED
    if _CONFIG_LOADED:
        return _CONFIG_CACHE
    _CONFIG_LOADED = True
    _CONFIG_CACHE = {}
    for name in ("config.yaml", "config.yml"):
        p = os.path.join(BASE, name)
        if os.path.exists(p):
            try:
                import yaml
                with open(p, encoding="utf-8") as f:
                    _CONFIG_CACHE = yaml.safe_load(f) or {}
            except Exception:
                _CONFIG_CACHE = {}
            break
    return _CONFIG_CACHE


def reload_config():
    """清掉配置缓存（供测试/长驻进程在配置变更后调用）。"""
    global _CONFIG_CACHE, _CONFIG_LOADED, _TAX_CACHE
    _CONFIG_CACHE = None
    _CONFIG_LOADED = False
    _TAX_CACHE = None
    return _load_config()


# 公司体量档位（顺序即从大到小；用于报表里的「体量 × 赛道」交叉统计）
SCALE_TIERS = ["大厂", "中厂", "小厂", "创业团队"]

# 体量别名 → 标准档位。卡里/配置里写"初创/startup/头部"等都能收敛。
SCALE_ALIASES = {
    "大厂": "大厂", "头部": "大厂", "一线大厂": "大厂", "big": "大厂", "large": "大厂",
    "中厂": "中厂", "中型": "中厂", "mid": "中厂", "medium": "中厂", "垂类头部": "中厂",
    "小厂": "小厂", "小型": "小厂", "小公司": "小厂", "small": "小厂", "sme": "小厂",
    "创业团队": "创业团队", "初创": "创业团队", "创业": "创业团队",
    "早期": "创业团队", "startup": "创业团队",
}


def norm_scale(text):
    """把各种写法的体量收敛到 SCALE_TIERS 之一；认不出返回 ""。

    ⚠️ 为什么需要它：体量**无法从岗位/JD 文本推断**，只能由用户标注
    （同一个赛道里既有大厂也有小厂，词表永远猜不出来）。
    所以这里只做"归一"，不做"猜测"。
    """
    t = str(text or "").strip().lower()
    if not t:
        return ""
    for k, v in SCALE_ALIASES.items():
        if k.lower() == t:
            return v
    for k, v in SCALE_ALIASES.items():
        if k.lower() in t:
            return v
    return ""


def company_scales():
    """公司名 → 体量档位（来自 config.yaml 的 company_scale）。"""
    out = {}
    for k, v in (_load_config().get("company_scale") or {}).items():
        s = norm_scale(v)
        if k and s:
            out[str(k)] = s
    return out


def scale_of(company, explicit=""):
    """取一家公司的体量档位。

    优先级：
      ① 卡里显式写的 interview.company_scale（最准，逐卡覆盖）
      ② config.yaml 的 company_scale 精确/包含匹配
      ③ ""（未标注 —— 报表要如实显示"未标注"，不要瞎猜）
    """
    s = norm_scale(explicit)
    if s:
        return s
    t = str(company or "")
    for comp, sc in company_scales().items():
        if comp and comp in t:
            return sc
    return ""


def main_tracks():
    """你的主场赛道白名单（来自 config.yaml 的 main_tracks）。

    ⚠️ 引擎**不预设**任何人的主场 —— 之前这里把「生活服务/点评」
    「内容/社区大厂」写死在 report 里当主场，于是所有别的主场
    （以及词表后加的出海/国际化等）都被误判成"跨界"。
    默认返回空集：没有配置时，告警区不按赛道排除任何卡。
    """
    return [str(x) for x in (_load_config().get("main_tracks") or []) if str(x).strip()]


# blocker_keywords() / blocker_hits() 定义在文件后半部分（见 DEFAULT_BLOCKER_KEYWORDS）。

def offer_flag(card):
    """把 result.offer 归一成 'got' / 'no' / 'ongoing' / ''（认不出）。

    ⚠️ 为什么必须归一，而不是各模块自己 str().startswith("no"）：
      schema 文档写的是 `offer: got/no/ongoing`（**字符串**），
      但 YAML 会把裸写的 `no` / `false` 解析成**布尔**。
      实测真实数据：40 张是 `offer: False`、98 张缺失、4 张空串，
      **没有一张是字符串 "no"**。

      于是旧代码 `off.lower().startswith("no")` 对那 40 张**永远为假**
      （str(False) == 'False'），成了 100% 死分支 —— 它们只是碰巧
      why_ended 有值才没被漏掉。一旦出现「offer: False + why_ended 为空」，
      该场就会从「业务全过但 offer=no」里**静默消失**。

      同一个 bug 曾散落在 report2/report3/decision 三个文件里；
      strategy.py 甚至在原地打了个补丁
      （`in ("no","False","false")`）—— 那正说明有人撞上过它，
      却只补了自己那一处、没修根因。现在统一走这里。
    """
    off = (card.get("result") or {}).get("offer")
    if isinstance(off, bool):
        return "got" if off else "no"
    s = str(off or "").strip().lower()
    if not s:
        return ""
    if s.startswith("no") or s in ("false", "否", "没", "没有", "未", "无"):
        return "no"
    if s.startswith("got") or s in ("true", "是", "有"):
        return "got"
    if "ongoing" in s or "在走" in s or "进行" in s or "待定" in s:
        return "ongoing"
    return ""


_TAX_CACHE = None


def taxonomy():
    """合并后的归类表（带缓存）。

    优先级：**用户自定义赛道 track_rules 在最前** → 内置默认表。
    `categories` 是"往某个已有类目里加词"，`track_rules` 是"定义你自己的类目"。
    后者说明使用者对业务的理解更准（本会话被纠正过 4 次），所以排在前面。
    """
    global _TAX_CACHE
    if _TAX_CACHE is not None:
        return _TAX_CACHE
    cfg = _load_config()

    tax = {}
    # ① 用户自定义赛道（顺序即优先级；先命中先返回）
    for k, v in (cfg.get("track_rules") or {}).items():
        kws = [str(x) for x in (v or []) if str(x).strip()]
        if kws:
            tax[str(k)] = list(dict.fromkeys(kws))
    # ② 内置表（用户已定义同名类目时，把内置词并进去而不是覆盖）
    #    ⚠️ 泛化兜底桶（_GENERIC_BUILTIN_NAMES）在 ④ 里统一处理：
    #       它必须排在**所有**赛道之后，否则会抢走更具体的卡
    #       （实测：并进用户排在第 1 位的「内容运营」后，
    #        25 张卡从 策略/垂类/社区/产品运营 掉进内容运营）。
    for k, v in DEFAULT_TAXONOMY.items():
        if k in _GENERIC_BUILTIN_NAMES:
            continue  # 交给 ④，保证排在最后
        if k in tax:
            tax[k] = list(dict.fromkeys(tax[k] + list(v)))
        else:
            tax[k] = list(v)
    # ③ categories：往类目里补词
    for k, v in (cfg.get("categories") or {}).items():
        tax.setdefault(str(k), [])
        tax[str(k)] = list(dict.fromkeys(tax[str(k)] + [str(x) for x in (v or [])]))
    # ④ 泛化兜底桶：**永远排在最后**（这是它唯一的作用，别处不再处理）
    #    目的：用户没写 track_rules 时，"内容运营/内容策略/机构运营"这类
    #    最常见的岗位不会掉进「其他」；用户写了自定义赛道时，
    #    它只在所有自定义赛道都没命中之后才生效，不会抢卡。
    #
    #    ⚠️ 本块与 ② 的 continue 是**同一个意图的两半**，缺一不可：
    #       去掉 continue → 泛化词并入用户词表的高位赛道（抢卡）
    #       去掉本块     → 泛化桶根本不进表（新用户"内容运营"落到「其他」）
    #       已用注入检验验证：两处都去掉时，垂类/策略/社区/品类 全部塌成内容运营。
    for k in _GENERIC_BUILTIN_NAMES:
        if k in DEFAULT_TAXONOMY:
            kws = list(DEFAULT_TAXONOMY[k])
            if k in tax:
                merged = [w for w in tax[k] if w not in kws] + kws
                del tax[k]
                tax[k] = list(dict.fromkeys(merged))
            else:
                tax[k] = kws
    _TAX_CACHE = tax
    return tax


def card_track_map():
    """卡号 → 赛道 的**强制指定**（config.yaml 的 card_track）。

    ⚠️ 这是最高优先级的归类方式：使用者按卡号一对一指定，引擎不再猜测。
      用途：某些卡的业务归属只有本人知道（如"应用商店的内容运营其实算内容策略"），
      词表再准也猜不到，这时直接指定最可靠，而且**不影响其他任何卡**。
    """
    out = {}
    for k, v in (_load_config().get("card_track") or {}).items():
        cid = str(k).strip().upper()
        t = str(v or "").strip()
        if cid and t:
            out[cid] = t
    return out


def track_of_card(card, fallback="其他"):
    """判定一张卡的赛道 —— **先查 card_track 强制指定**，没有再走启发式。

    所有按卡统计的模块都应该用这个（而不是自己拼文本去 classify），
    否则"手动指定"会在那些模块里失效。
    """
    cid = str(card.get("id") or card.get("_id") or "").strip().upper()
    forced = card_track_map().get(cid)
    if forced:
        return forced
    iv = card.get("interview") or {}
    return classify_position(str(iv.get("company") or ""),
                             str(iv.get("position") or ""),
                             fallback=fallback)


def industry_map():
    """用户自定义的 公司名→赛道 精确映射。"""
    return {str(k): str(v) for k, v in (_load_config().get("industry_map") or {}).items()}


# 「泛化赛道」——命中这些说明**只说清了是内容类工作，没说是哪个业务方向**。
# 此时不应该就此定案，而要继续看括注里有没有更具体的方向。
# 判据来自实测：「内容运营中台(生活服务/团购向)」「内容运营(金融垂类)」
# 的主线只给出"内容运营"，真正的方向都在括注里。
#
# ⚠️ 原来这里是 {"内容/社区大厂"}，那个内置桶已被用户删除，故为空集。
#    保留变量本身：_match_specific() 的语义（"只要泛化类则返回空"）仍然成立，
#    将来若再引入泛化桶，只需把名字加回来。
_GENERIC_TRACKS = set()

# 内置表里属于「泛化兜底」的赛道名：它们的词很泛，必须排在**所有**赛道之后，
# 既不并进用户的同名定义（会抢卡），也不能排在中间。
# 详见 taxonomy() 里 ② 和 ④ 的注释。
_GENERIC_BUILTIN_NAMES = ("内容运营",)


def _match_track(text):
    """在词表里按顺序找第一个命中的赛道；找不到返回 ""。"""
    if not text:
        return ""
    for ind, kws in taxonomy().items():
        if any(k in text for k in kws):
            return ind
    return ""


def _match_specific(text):
    """只返回**非泛化**的赛道；若只命中泛化类则返回 ""。"""
    ind = _match_track(text)
    return "" if ind in _GENERIC_TRACKS else ind


def strip_notes(text):
    """去掉括号里的备注，只留主线。"""
    import re
    t = str(text or "")
    t = re.sub(r"[（(][^）)]*[）)]", "", t)
    t = re.sub(r"[【\[][^】\]]*[】\]]", "", t)
    return t.strip()


def classify_position(company, position, fallback="其他"):
    """推荐的调用方式：公司和岗位**分开传**。

    判定顺序：
      ① 岗位**主线**（去掉括注）—— 主线决定归属，这是主口径
      ② 岗位全文（含括注）
      ③ 公司（含公司括注 —— 那里的线索常常是唯一的，如
         「某财经平台（股票/财经型APP…）」的"财经"只在括注里）
      ④ 公司名精确映射 → fallback

    ⚠️ 为什么"岗位主线优先于括注"（用户指出的实例）：
      `浏览器海外业务·内容运营（偏toB内容运营，对接CP供应商）`
      括注里的 "toB" 会把它归成「B端/商家」，
      但用户明确要求：那是**内容策略**岗，归「内容/社区大厂」。
      括注是备注，主线才是岗位身份。

    ⚠️ 为什么不用"具体方向优先于泛化类"那种更聪明的规则（试过，失败了）：
      我曾改成"主线只判出泛化类时，就去看括注里有没有具体方向"，
      想救回 `内容运营（金融垂类）` 这类卡。结果：
        · 救回了几张「内容运营(金融垂类)」「内容运营(生活服务/团购向)」
        · 但**弄坏了一批** —— 「美食品类活动运营」被括注里的"作者增长"
          带去「用户增长」、另一些被"汽车"带去「汽车/出行」、
          被"AI"带去「AI/工具」… 而那些括注是在**描述工作内容**（做什么），
          不是**业务归属**（属于哪条线）。
        · 实测全库有 93 张卡带括注，"括注是方向还是工作描述"**无法用规则区分** ——
          这需要业务判断。
      所以退回到可预测的简单规则：**主线说了算**。
      个别判错的，使用者知道的可以直接改卡或用 config 的 industry_map 覆盖。
      （结论：宁可规则简单可预测，也不要一个时对时错的"聪明"规则。）
    """
    comp = str(company or "")
    pos = str(position or "")

    # ① 岗位主线
    ind = _match_track(strip_notes(pos))
    if ind:
        return ind
    # ② 岗位全文
    ind = _match_track(pos)
    if ind:
        return ind
    # ③ 公司（含括注）
    ind = _match_track(comp)
    if ind:
        return ind
    # ④ 公司名精确映射
    for c, i in industry_map().items():
        if c and (c in comp or c in pos):
            return i
    return fallback


def classify(text, fallback="其他"):
    """把「公司 + 岗位」拼串归到一个赛道（兼容旧调用方式）。

    调用方若有分开的公司/岗位字段，建议直接调
    `classify_position(company, position)`，语义更准确。
    """
    t = str(text or "")
    if not t:
        return fallback
    return classify_position("", t, fallback=fallback)




# 用工性质的标准取值。**正编 与 外包 必须分开统计** —— 外包岗通过率天然虚高
# （降维岗易过），把它混进正编会让人误判自己的主战场。
NATURE_KINDS = ["正编", "外包", "兼职", "实习"]

# 未标注时的文本兜底信号（仅在 interview.nature 为空时使用）
_NATURE_TEXT_HINTS = [
    ("外包", ["外包", "派遣", "驻场", "劳务", "外派"]),
    ("兼职", ["兼职", "part-time", "parttime"]),
    ("实习", ["实习", "intern"]),
]


def nature_of(card, default="正编"):
    """判定一张卡的**用工性质**：正编 / 外包 / 兼职 / 实习。

    ⚠️ 为什么必须放在这里共用（2026 审计发现）：
      这张逻辑此前被**四个模块各写了一遍**，而且四份结果互不相同 ——
      同一批卡，外包场数被算成 17 / 18 / 19 / **15**：
        · report2.py  读 interview.nature，但只认"正编/正式/外包"，
                      遇到"兼职"返回第四种值 "未知nature"（报表里冒出一行看不懂的桶）
        · report3.py  纯文本子串匹配，不看 nature 字段
        · decision.py 读 nature，词表又不一样（含"实习"）
        · strategy.py **完全不读 nature**，只 grep "外包" ——
                      于是漏掉那些 nature=外包 的卡，外包数少算
      结果用户在总报看到"外包通过率 88.2%"，在定位报告看到"78.9%"，同一份数据两个数。

    判定顺序：
      ① 优先读 interview.nature（用户显式标注，最可信）
      ② 没标才退到文本信号（岗位名/公司名/结果原因）
      ③ 都没有则按 default（正编）
    """
    iv = card.get("interview") or {}
    n = str(iv.get("nature") or "").strip().lower()
    if n:
        # 精确优先，避免"非正编"这类描述性写法被误判
        for k in NATURE_KINDS:
            if k in n:
                return k
        if "正式" in n or "全职" in n or "正职" in n:
            return "正编"
        # 认不出的写法（如"外包转正"已含"外包"故上面已命中）→ 落到文本兜底

    blob = " ".join([
        str(iv.get("position") or ""),
        str(iv.get("company") or ""),
        str((card.get("result") or {}).get("reason") or ""),
        str(card.get("context") or ""),
    ]).lower()
    for kind, kws in _NATURE_TEXT_HINTS:
        if any(k in blob for k in kws):
            return kind
    return default




def round_no(card):
    """把面试轮次归一成 1/2/3/... ；认不出返回 0。

    ⚠️ 为什么需要（2026 审计发现）：
      `interview.round` 是**自由文本**，真实数据里有 58 种不同写法：
        "一面"、"一面（业务）"、"一面(业务)"（**半角括号**）、"业务面(一面)"、
        "二面"、"二面（交叉面）"、"HR面"、"三面（boss 面，终轮）"…
      旧代码用**枚举白名单**去比对：
        round in ("一面","一面（业务）","业务面","业务面（一面）","一面（业务面）")
      结果 87 张 fail 卡里只有 49 张命中，**38 张被静默丢掉** ——
      而且白名单里写的是全角括号"一面（业务面）"，数据里却有半角"一面(业务)"，
      一个 Unicode 宽度差异就让整条规则失效。
      这类"封闭枚举 vs 自由文本"是本项目反复复发的 bug，故改为解析语义。
    """
    r = str((card.get("interview") or {}).get("round") or "").strip()
    if not r:
        return 0
    rl = r.lower().replace("（", "(").replace("）", ")")
    # 中文数字 / 阿拉伯数字
    for n, words in ((1, ["一面", "初面", "第一轮", "1面"]),
                     (2, ["二面", "复面", "第二轮", "2面"]),
                     (3, ["三面", "第三轮", "3面"]),
                     (4, ["四面", "第四轮", "4面"])):
        if any(w in rl for w in words):
            return n
    # HR 面 / boss 面 / 终面 通常是最后一轮，但序号不定 —— 用 9 表示"后期轮"
    if any(w in rl for w in ["hr", "终面", "boss", "ceo", "总监", "总经理"]):
        return 9
    # 形如 "第3轮" / "3轮" / "round 3"
    m = __import__("re").search(r"(\d+)\s*(?:轮|round|面)", rl)
    if m:
        return int(m.group(1))
    # 只写"业务面"/"专业面"/"交叉面"而没给序号：中文语境里这就是**第一轮业务面**
    # （没有哪家把"业务面"当第三轮叫）。真实数据里有 5 张这样写，旧白名单
    # 虽然收录了裸的"业务面"却因为带括号后缀（"业务面（COO/公司经营层）"）
    # 而全部失配 —— 所以这里用"包含"而不是"相等"。
    if any(w in rl for w in ["业务面", "专业面", "交叉面", "技术面", "群面"]):
        return 1
    return 0


def is_first_round(card):
    """是否第一轮（业务一面）。用于"跨界一面挂"这类告警。"""
    return round_no(card) == 1


# 挂因关键词的**默认**表。长词在前（匹配时按长度降序，避免"行业gap"被拆成"行业"+"gap"）。
# ⚠️ 这只是兜底；config.yaml 的 blocker_keywords 可整体覆盖。
# 之所以给这么一份：完全不给的话各模块会各自硬编码一份互不相同的短表
# （审计实测：diagnosis 27 词、cross_analysis 16 词、decision 14 词，
#  同一批 fail 卡分别漏掉 20 / 68 / 21 张的 weakness）。
DEFAULT_BLOCKER_KEYWORDS = [
    # 行业/背景适配
    "行业gap", "背景gap", "经验gap", "业务gap", "英语gap", "能力gap", "有gap", "gap",
    # 经验欠缺
    "经验不足", "经验少", "了解不够", "理解不够", "深度不足", "了解不深", "需补",
    "不足", "不够", "不深", "缺", "陌生",
    # ⚠️ 以下两组是**用真实数据补出来的**（v3.2.3）。
    #    起因：拿某张真实卡跑链路，发现 `blocker_hits` 返回空，
    #    而它的 weakness 写得很清楚——"后半段大量未事先想过的上层题…当场没答上"。
    #    全库一查：**87 张 fail 卡里有 23 张（26%）一个词都命中不了**，
    #    那些卡的挂因在报表里完全不可见。补完这两组后降到个位数。
    #    每条都能在真实卡里找到出处，不是凑数：
    #      "没答上/答不上" —— 最高频的失败形态，原词表竟无对应词
    #      "不匹配/差距/没接触/行业理解" —— 能力与经验层面的错配
    #      "薪资/降幅/无HC/审批" —— 谈判与流程层面的卡点（不是能力问题）
    "没答上", "答不上", "答不出", "没答", "未准备", "没准备", "没想过", "未想过",
    "答不好", "没接触", "没做过", "无经验", "缺乏", "欠缺", "差距", "不匹配",
    "行业理解", "理解力", "认知",
    # 履历/叙事
    "外包", "稳定性", "简历", "被动", "求职动机", "职业定位", "职业规划", "空窗",
    "频繁", "跳槽", "犹豫", "纠结", "没说服", "未说服", "不坚定",
    # 硬约束/现场
    "商业化", "base", "职级", "口径", "语速", "表达", "字节", "薪资", "降幅",
    "回流", "无HC", "没HC", "审批", "名额",
    "指标", "数据", "方法论", "亮点", "执行", "作者", "用户", "社群", "策略",
]


def blocker_keywords():
    """挂因统计用的关键词 = **内置默认表 + config.yaml 里用户自己加的**。

    ⚠️ 这里原来是 `cfg or default`（配置**整体覆盖**默认），这是个设计错误：
      实测你的 config.yaml 里定义了自己的 blocker_keywords（26 个词），
      于是本次给默认表补的那些新词（"没答上/不匹配/无HC"…）**一个都没生效**，
      87 张 fail 卡里仍有 23 张（26%）挂因不可见 —— 我改了代码却没改到你的结果。

      改成**合并**：用户加的词只做增量，内置表继续演进。
      这样以后我在内置表里补词，老用户不用改配置也能受益。
      想去掉某个内置词，用 `blocker_keywords_exclude` 显式排除（不常用）。
    """
    cfg = _load_config()
    user = [str(x) for x in (cfg.get("blocker_keywords") or []) if str(x).strip()]
    merged = list(DEFAULT_BLOCKER_KEYWORDS)
    for w in user:
        if w not in merged:
            merged.append(w)
    excl = {str(x).strip() for x in (cfg.get("blocker_keywords_exclude") or []) if str(x).strip()}
    if excl:
        merged = [w for w in merged if w not in excl]
    return merged


def blocker_hits(card, keywords=None):
    """从 weakness 里抽出挂因关键词，**最长优先且不重叠**。

    所有模块都应调用这个，而不是各自硬编码一份短词表 ——
    那样会各自漏掉一批卡，且同一份数据在不同报告里给出不同的"挂因排行"。
    """
    return blocker_hits_from_text(
        str((card.get("reflection") or {}).get("weakness", "") or ""), keywords)


def blocker_hits_from_text(text, keywords=None):
    """同上，但直接吃一段文本（有些模块手里只有 weakness 字符串，没有整张卡）。"""
    w = str(text or "").lower()
    if not w:
        return []
    kws = keywords or blocker_keywords()
    kws = sorted({str(k).lower() for k in kws if str(k).strip()}, key=len, reverse=True)
    hits, consumed = [], w
    for k in kws:
        if k and k in consumed:
            hits.append(k)
            consumed = consumed.replace(k, "\0" * len(k))  # 占位，防短词重复命中
    return hits
