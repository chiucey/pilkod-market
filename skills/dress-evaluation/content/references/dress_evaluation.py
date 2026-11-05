"""
增强版穿搭评价与建议系统
Dress Evaluation and Suggestion System (Enhanced Version)

支持的评价维度：
1. 基础版型与配色评估
2. 体型适配分析（苹果型、梨形、沙漏型、H型等）
3. 肤色匹配分析（冷暖色调）
4. 年龄与场景匹配
5. 配饰搭配评估
6. 上下装比例分析
7. 季节适宜性评估
"""

def minimax_dress_evaluation_enhanced(
    gender: str,
    age_range: str,
    scene: str = "日常",
    img_features: dict = None
):
    """
    增强版穿搭评价函数

    参数:
        gender: 性别 ("male" / "female")
        age_range: 年龄段 ("18-25" / "26-35" / "36-45" / "46+")
        scene: 场景 ("日常" / "职场" / "约会" / "运动" / "聚会")
        img_features: 图像特征字典

    返回:
        包含评分、优势、问题和建议的字典
    """
    if img_features is None:
        img_features = {}

    # ==================== 1. 基础参数与默认值 ====================
    score = 6.0
    advantage = []
    disadvantage = []
    warnings = []

    current_dress = img_features.get("current_dress", "")
    dress_lower = current_dress.lower()

    # ==================== 2. 体型适配分析（新增）====================
    body_type = img_features.get("body_type", "标准")
    body_type_analysis = _analyze_body_type(body_type, current_dress, gender)

    score += body_type_analysis["score_delta"]
    advantage.extend(body_type_analysis["advantages"])
    disadvantage.extend(body_type_analysis["disadvantages"])

    # ==================== 3. 肤色匹配分析（新增）====================
    complexion = img_features.get("complexion", "正常")
    skin_undertone = img_features.get("skin_undertone", "自然")  # 冷/暖/自然
    skin_color_analysis = _analyze_skin_color(
        skin_undertone, current_dress, gender, complexion
    )

    score += skin_color_analysis["score_delta"]
    advantage.extend(skin_color_analysis["advantages"])
    disadvantage.extend(skin_color_analysis["disadvantages"])
    warnings.extend(skin_color_analysis["warnings"])

    # ==================== 4. 基础版型与配色评估（原有逻辑优化）============
    basic_analysis = _analyze_basic_fit(current_dress, scene, gender)

    score += basic_analysis["score_delta"]
    advantage.extend(basic_analysis["advantages"])
    disadvantage.extend(basic_analysis["disadvantages"])

    # ==================== 5. 年龄与风格匹配评估 ====================
    age_analysis = _analyze_age_match(age_range, current_dress, gender)

    score += age_analysis["score_delta"]
    advantage.extend(age_analysis["advantages"])
    disadvantage.extend(age_analysis["disadvantages"])

    # ==================== 6. 上下装比例分析（新增）====================
    proportion_analysis = _analyze_proportion(
        img_features.get("top_length", "正常"),
        img_features.get("bottom_length", "正常"),
        img_features.get("waistline", "正常"),
        gender
    )

    score += proportion_analysis["score_delta"]
    advantage.extend(proportion_analysis["advantages"])
    disadvantage.extend(proportion_analysis["disadvantages"])

    # ==================== 7. 配饰搭配评估（新增）====================
    accessories = img_features.get("accessories", [])
    accessory_analysis = _analyze_accessories(accessories, gender, current_dress)

    score += accessory_analysis["score_delta"]
    advantage.extend(accessory_analysis["advantages"])
    disadvantage.extend(accessory_analysis["disadvantages"])

    # ==================== 8. 季节适宜性评估（新增）====================
    season = img_features.get("season", "春秋")
    season_analysis = _analyze_season(season, current_dress)

    score += season_analysis["score_delta"]
    advantage.extend(season_analysis["advantages"])
    disadvantage.extend(season_analysis["disadvantages"])
    warnings.extend(season_analysis["warnings"])

    # ==================== 9. 场景匹配最终评估 ====================
    scene_analysis = _analyze_scene(scene, current_dress, gender, age_range)

    score += scene_analysis["score_delta"]
    disadvantage.extend(scene_analysis["disadvantages"])
    warnings.extend(scene_analysis["warnings"])

    # ==================== 10. 得分描述 ====================
    score = max(1.0, min(10.0, score))  # 限制在1-10分之间

    if score >= 9.0:
        score_desc = "卓越，完美驾驭，时尚感与质感兼具"
    elif score >= 8.0:
        score_desc = "优秀，穿搭协调且有品味，细节处理得当"
    elif score >= 7.0:
        score_desc = "良好，基础合格，细节可进一步优化"
    elif score >= 6.0:
        score_desc = "中等偏上，整体尚可，有小幅提升空间"
    elif score >= 5.0:
        score_desc = "中等，整体普通，有明显提升空间"
    else:
        score_desc = "偏低，风格/版型/配色存在明显问题"

    # ==================== 11. 生成个性化建议 ====================
    suggestion = _generate_suggestion(
        gender, age_range, scene, body_type, skin_undertone,
        body_type_analysis, skin_color_analysis, proportion_analysis,
        season_analysis, score
    )

    # ==================== 12. 返回完整评估结果 ====================
    return {
        "score": round(score, 1),
        "score_desc": score_desc,
        "advantage": advantage if advantage else [],
        "disadvantage": disadvantage if disadvantage else [],
        "warnings": warnings if warnings else [],
        "analysis": {
            "body_type": body_type_analysis,
            "skin_color": skin_color_analysis,
            "proportion": proportion_analysis,
            "accessories": accessory_analysis,
            "season": season_analysis,
            "scene": scene_analysis
        },
        "suggestion": suggestion,
        "tags": _generate_tags(advantage, disadvantage, body_type, skin_undertone, scene)
    }


# ==================== 辅助分析函数 ====================

def _analyze_body_type(body_type: str, current_dress: str, gender: str) -> dict:
    """
    体型适配分析
    支持的体型: 苹果型、梨形、沙漏型、H型、倒三角型、标准型
    """
    result = {"score_delta": 0.0, "advantages": [], "disadvantages": []}

    # 苹果型身材（腰部较粗）
    if body_type == "苹果型":
        if any(x in current_dress for x in ["A字", "高腰", "伞裙", "直筒"]):
            result["advantages"].append("A字裙/高腰设计有效修饰腰部线条")
            result["score_delta"] += 1.2
        elif any(x in current_dress for x in ["紧身", "短款", "露腰"]):
            result["disadvantages"].append("紧身/短款上衣暴露腰部缺点")
            result["score_delta"] -= 1.5

    # 梨形身材（臀部较宽）
    elif body_type == "梨形":
        if any(x in current_dress for x in ["A字", "伞裙", "阔腿裤", "深色下装"]):
            result["advantages"].append("A字下装有效平衡臀部比例")
            result["score_delta"] += 1.2
        elif any(x in current_dress for x in ["紧身下装", "包臀", "浅色裤"]):
            result["disadvantages"].append("紧身浅色下装凸显臀部宽度")
            result["score_delta"] -= 1.5

    # 沙漏型身材
    elif body_type == "沙漏型":
        if any(x in current_dress for x in ["收腰", "X型", "鱼尾", "紧身"]):
            result["advantages"].append("收腰设计完美展现沙漏曲线")
            result["score_delta"] += 1.0
        elif any(x in current_dress for x in ["宽松直筒", "H型", " Oversized"]):
            result["disadvantages"].append("过于宽松的版型掩盖了身材优势")
            result["score_delta"] -= 0.8

    # H型身材
    elif body_type == "H型":
        if any(x in current_dress for x in ["收腰", "腰带", "高腰", "层穿"]):
            result["advantages"].append("腰带/高腰设计创造腰线，优化比例")
            result["score_delta"] += 1.2
        elif any(x in current_dress for x in ["直筒无腰", "宽松无曲线"]):
            result["disadvantages"].append("缺乏腰线设计，身材更显扁平")
            result["score_delta"] -= 1.0

    # 倒三角型身材（肩宽）
    elif body_type == "倒三角型":
        if any(x in current_dress for x in ["A字裙", "阔腿裤", "下摆宽"]):
            result["advantages"].append("下身外扩设计平衡肩宽比例")
            result["score_delta"] += 1.2
        elif any(x in current_dress for x in ["垫肩", "泡泡袖", "横条纹"]):
            result["disadvantages"].append("肩部装饰过多显得上半身更宽")
            result["score_delta"] -= 1.5

    # 标准型身材
    elif body_type == "标准":
        if any(x in current_dress for x in ["合身", "修身", "标准"]):
            result["advantages"].append("标准身材适合多种版型，穿出自我风格")
            result["score_delta"] += 0.5

    return result


def _analyze_skin_color(
    skin_undertone: str,
    current_dress: str,
    gender: str,
    complexion: str
) -> dict:
    """
    肤色匹配分析
    肤色底调: 冷色调(蓝粉底)、暖色调(黄金底)、自然色调
    """
    result = {"score_delta": 0.0, "advantages": [], "disadvantages": [], "warnings": []}

    # 冷色调肤色 - 适合蓝色系、紫色系、粉色系
    cold_colors = ["蓝", "宝蓝", "湖蓝", "藏青", "紫", "薰衣草紫", "粉", "玫红", "银"]
    cold_avoid = ["橙", "黄", "驼色", "姜黄", "土黄", "正红"]

    # 暖色调肤色 - 适合黄色系、橙色系、大地色系
    warm_colors = ["黄", "橙", "驼色", "焦糖", "姜黄", "砖红", "珊瑚", "大地色", "金"]
    warm_avoid = ["紫", "薰衣草", "玫红", "粉蓝", "薄荷绿"]

    # 自然色调 - 适合大多数颜色
    natural_good = ["白", "黑", "灰", "藏青", "酒红", "墨绿", "卡其", "牛仔蓝"]

    if skin_undertone == "冷":
        matching = any(color in current_dress for color in cold_colors)
        avoiding = any(color in current_dress for color in cold_avoid)

        if matching:
            result["advantages"].append(f"冷色调肤色与服装色彩和谐统一")
            result["score_delta"] += 0.8
        if avoiding:
            result["disadvantages"].append("暖色系与冷色调肤色对比过强，显得暗沉")
            result["score_delta"] -= 1.0
            result["warnings"].append("建议选择冷色调服装提亮肤色")

    elif skin_undertone == "暖":
        matching = any(color in current_dress for color in warm_colors)
        avoiding = any(color in current_dress for color in warm_avoid)

        if matching:
            result["advantages"].append(f"暖色调肤色与服装色彩相得益彰")
            result["score_delta"] += 0.8
        if avoiding:
            result["disadvantages"].append("冷色系与暖色调肤色冲突，显得气色不佳")
            result["score_delta"] -= 1.0
            result["warnings"].append("建议选择暖色调服装提升气色")

    elif skin_undertone == "自然":
        matching = any(color in current_dress for color in natural_good)
        if matching:
            result["advantages"].append("自然色调肤色适应性强，选择范围广")
            result["score_delta"] += 0.5

    # 肤色明暗度调整
    if complexion in ["偏黑", "古铜"]:
        if "白" in current_dress:
            result["advantages"].append("白色提亮深肤色，形成良好对比")
            result["score_delta"] += 0.5
    elif complexion in ["偏白", "白皙"]:
        if "深色" in current_dress or "黑色" in current_dress:
            result["advantages"].append("深色服装衬托白皙肤色，更显气质")
            result["score_delta"] += 0.5

    return result


def _analyze_basic_fit(current_dress: str, scene: str, gender: str) -> dict:
    """基础版型与配色评估"""
    result = {"score_delta": 0.0, "advantages": [], "disadvantages": []}

    # 版型评估
    if "合身" in current_dress or "修身" in current_dress or "简约" in current_dress:
        result["advantages"].append("版型合身，整体干净利落")
        result["score_delta"] += 0.8

    if "宽松" in current_dress and ("邋遢" in current_dress or "没型" in current_dress):
        result["disadvantages"].append("版型过于宽松，显得拖沓没精神")
        result["score_delta"] -= 1.0

    # 配色评估
    clean_colors = ["浅", "白", "灰", "黑", "藏青", "米"]
    if any(color in current_dress for color in clean_colors):
        if not any(x in current_dress for x in ["花", "艳", "乱", "杂"]):
            result["advantages"].append("配色简洁有序，视觉效果清爽")
            result["score_delta"] += 0.5

    # 色彩杂乱检测
    if "花" in current_dress or "艳" in current_dress or "乱" in current_dress:
        result["disadvantages"].append("颜色/图案杂乱，视觉效果过于繁复")
        result["score_delta"] -= 1.2

    # 整体协调性
    if scene in current_dress:
        result["advantages"].append(f"风格贴合{scene}场景")
        result["score_delta"] += 0.5

    return result


def _analyze_age_match(age_range: str, current_dress: str, gender: str) -> dict:
    """年龄与风格匹配评估"""
    result = {"score_delta": 0.0, "advantages": [], "disadvantages": []}

    if age_range == "18-25":
        if "正装" in current_dress or "老气" in current_dress or "中年" in current_dress:
            result["disadvantages"].append("风格偏成熟，不符合年轻定位")
            result["score_delta"] -= 1.0
        elif any(x in current_dress for x in ["清新", "活力", "简约", "青春"]):
            result["advantages"].append("青春简约风格与年龄段高度匹配")
            result["score_delta"] += 0.8

    elif age_range == "26-35":
        if "幼稚" in current_dress or "潮牌夸张" in current_dress or "卡通" in current_dress:
            result["disadvantages"].append("风格偏幼稚，与成熟年龄段略有违和")
            result["score_delta"] -= 1.0
        elif any(x in current_dress for x in ["轻熟", "通勤", "简约"]):
            result["advantages"].append("轻熟风格稳重又不失活力")
            result["score_delta"] += 0.8

    elif age_range in ["36-45", "46+"]:
        if "紧身" in current_dress or "亮色堆砌" in current_dress or "超短" in current_dress:
            result["disadvantages"].append("款式过于张扬，与成熟气质不符")
            result["score_delta"] -= 1.5
        elif any(x in current_dress for x in ["得体", "质感", "经典", "优雅"]):
            result["advantages"].append("得体优雅的风格彰显成熟魅力")
            result["score_delta"] += 0.8

    return result


def _analyze_proportion(
    top_length: str,
    bottom_length: str,
    waistline: str,
    gender: str
) -> dict:
    """上下装比例分析"""
    result = {"score_delta": 0.0, "advantages": [], "disadvantages": []}

    # 高腰线设置
    if waistline == "高腰":
        result["advantages"].append("高腰设计优化身材比例，显腿长")
        result["score_delta"] += 1.0
    elif waistline == "低腰":
        result["disadvantages"].append("低腰线可能拉低身材重心")
        result["score_delta"] -= 0.8

    # 上下长度比例
    if top_length == "短款" and bottom_length == "高腰":
        result["advantages"].append("短款+高腰组合完美打造三七比例")
        result["score_delta"] += 1.2

    if gender == "female":
        if bottom_length == "及踝" or bottom_length == "曳地":
            result["advantages"].append("长裙/长裤搭配得当，拉长身形")
            result["score_delta"] += 0.8
        elif bottom_length == "五分" and top_length == "正常":
            result["disadvantages"].append("五五分比例易显矮")
            result["score_delta"] -= 1.0
            result["warnings"].append("建议选择短上衣或高腰下装优化比例")

    elif gender == "male":
        if bottom_length == "九分":
            result["advantages"].append("九分裤露出脚踝，视觉显高")
            result["score_delta"] += 0.8

    return result


def _analyze_accessories(
    accessories: list,
    gender: str,
    current_dress: str
) -> dict:
    """配饰搭配评估"""
    result = {"score_delta": 0.0, "advantages": [], "disadvantages": []}

    if not accessories:
        # 无配饰时，检查是否需要点缀
        if any(x in current_dress for x in ["素色", "纯色", "基础款"]):
            result["warnings"].append("整体造型略显单调，可适当添加配饰点缀")
        return result

    # 检查配饰数量
    if len(accessories) > 5:
        result["disadvantages"].append("配饰过多显得累赘，喧宾夺主")
        result["score_delta"] -= 1.0
    elif 1 <= len(accessories) <= 3:
        result["advantages"].append("配饰数量恰到好处，起画龙点睛作用")
        result["score_delta"] += 0.8

    # 配饰风格匹配
    accessory_set = set(accessories)
    if gender == "female":
        if "简约耳饰" in accessory_set or "细项链" in accessory_set:
            if not any(x in current_dress for x in ["华丽", "隆重", "晚宴"]):
                result["advantages"].append("简约配饰提升精致度，不喧宾夺主")
                result["score_delta"] += 0.5
        if "大Logo" in accessory_set or "夸张首饰" in accessory_set:
            if any(x in current_dress for x in ["简约", "素色", "基础款"]):
                result["advantages"].append("用亮眼配饰点亮整体造型")
                result["score_delta"] += 0.5

    elif gender == "male":
        if "皮带" in accessory_set or "手表" in accessory_set:
            if any(x in current_dress for x in ["正装", "商务", "职场"]):
                result["advantages"].append("皮带/手表提升整体质感与专业度")
                result["score_delta"] += 0.8

    return result


def _analyze_season(season: str, current_dress: str) -> dict:
    """季节适宜性评估"""
    result = {"score_delta": 0.0, "advantages": [], "disadvantages": [], "warnings": []}

    # 春夏季节 - 适合轻薄、浅色
    spring_summer_good = ["浅", "白", "浅蓝", "浅粉", "薄", "透气", "棉麻", "雪纺"]
    spring_summer_bad = ["厚重", "皮草", "加绒", "深色堆砌", "高领毛衣"]

    # 秋冬季节 - 适合保暖、深色
    fall_winter_good = ["厚", "针织", "毛衣", "大衣", "羽绒服", "保暖"]
    fall_winter_bad = ["薄", "透", "纱", "吊带", "露肩"]

    if season in ["春", "夏", "春夏"]:
        if any(item in current_dress for item in spring_summer_good):
            result["advantages"].append("轻薄材质/浅色系符合春夏氛围")
            result["score_delta"] += 0.8
        if any(item in current_dress for item in spring_summer_bad):
            result["disadvantages"].append(f"材质/颜色不符合{season}季节")
            result["score_delta"] -= 1.0
            result["warnings"].append(f"建议更换为轻薄透气的春夏款式")

    elif season in ["秋", "冬", "秋冬"]:
        if any(item in current_dress for item in fall_winter_good):
            result["advantages"].append("保暖材质符合秋冬季节需求")
            result["score_delta"] += 0.8
        if any(item in current_dress for item in fall_winter_bad):
            result["disadvantages"].append(f"过于清凉的款式不适合秋冬季节")
            result["score_delta"] -= 1.0
            result["warnings"].append(f"建议添加保暖层或选择更适合秋冬的材质")

    elif season == "春秋":
        # 春秋适合叠穿、过渡色
        if any(x in current_dress for x in ["开衫", "风衣", "针织", "衬衫"]):
            result["advantages"].append("春秋过渡季节适合层穿搭配")
            result["score_delta"] += 0.5

    return result


def _analyze_scene(
    scene: str,
    current_dress: str,
    gender: str,
    age_range: str
) -> dict:
    """场景匹配最终评估"""
    result = {"score_delta": 0.0, "disadvantages": [], "warnings": []}

    # 职场场景
    if scene == "职场":
        if "拖鞋" in current_dress or "凉拖" in current_dress:
            result["disadvantages"].append("拖鞋与职场正式氛围不符")
            result["score_delta"] -= 1.5
        if "正装" in current_dress or "衬衫" in current_dress or "西装" in current_dress:
            result["score_delta"] += 0.5  # 已在其他模块评估

    # 约会场景
    elif scene == "约会":
        if "运动服" in current_dress or "运动裤" in current_dress:
            result["disadvantages"].append("运动装过于随意，缺乏约会氛围")
            result["score_delta"] -= 1.0
        if any(x in current_dress for x in ["裙", "连衣裙", "精致"]):
            result["score_delta"] += 0.3

    # 运动场景
    elif scene == "运动":
        if any(x in current_dress for x in ["高跟鞋", "皮鞋", "正装"]):
            result["disadvantages"].append("正装/皮鞋不适合运动场景")
            result["score_delta"] -= 1.5
        if "运动" in current_dress or "运动裤" in current_dress or "T恤" in current_dress:
            result["score_delta"] += 0.5

    # 聚会场景
    elif scene == "聚会":
        if "过于朴素" in current_dress or "家居服" in current_dress:
            result["disadvantages"].append("家居服/睡衣风格不适合聚会场合")
            result["score_delta"] -= 1.5
        if any(x in current_dress for x in ["精致", "设计感", "亮色"]):
            result["score_delta"] += 0.5

    # 日常场景
    elif scene == "日常":
        # 日常场景最宽容
        if "过于隆重" in current_dress or "晚礼服" in current_dress:
            result["warnings"].append("日常穿着略显隆重，可适当放松")

    return result


def _generate_suggestion(
    gender: str,
    age_range: str,
    scene: str,
    body_type: str,
    skin_undertone: str,
    body_analysis: dict,
    skin_analysis: dict,
    proportion_analysis: dict,
    season_analysis: dict,
    score: float
) -> dict:
    """生成个性化建议"""

    # 基础建议
    if gender == "male":
        if age_range == "18-25":
            color = "浅蓝、白色、卡其、浅灰等干净亮色"
            style = "简约休闲、合身T恤/衬衫、直筒裤/牛仔裤"
            matching = "帆布鞋/板鞋，简约手表或链条款式"
            age_fit = "突出青春干净感，避免过于成熟老气"
            top = "短款合身T恤、简约衬衫"
            bottom = "直筒牛仔裤、休闲短裤"

        elif age_range == "26-35":
            color = "雾霾蓝、深灰、藏青、墨绿、大地色"
            style = "轻商务/简约通勤，合身但不紧身"
            matching = "休闲皮鞋/小白鞋，皮带提升质感，手表彰显品味"
            age_fit = "稳重不失活力，适合职场与日常切换"
            top = "修身衬衫、针织衫、轻薄西装外套"
            bottom = "卡其裤、深色牛仔裤、西装裤"

        else:  # 36+
            color = "藏青、深灰、黑色、米色、驼色"
            style = "经典基础款，高品质面料优先"
            matching = "皮质鞋、简约公文包、质感皮带"
            age_fit = "稳重得体，凸显成熟气质与品味"
            top = "高支数衬衫、毛呢外套、羊绒衫"
            bottom = "直筒西裤、品质牛仔裤"

    else:  # female
        if age_range == "18-25":
            color = "马卡龙浅色系、白色、浅粉、薄荷绿"
            style = "清新甜酷、短款/高腰优化比例"
            matching = "小白鞋、小皮鞋、简约耳饰/发夹"
            age_fit = "青春灵动，避免过于成熟厚重"
            top = "短款上衣、高腰短袖、简约背心"
            bottom = "A字裙、高腰牛仔裤、百褶裙"
            dress = "碎花连衣裙、吊带裙（外搭衬衫）"

        elif age_range == "26-35":
            color = "莫兰迪色系、驼色、黑色、白色、米白"
            style = "轻熟优雅，合身剪裁，注重品质感"
            matching = "细带鞋、乐福鞋、简约耳饰/项链"
            age_fit = "优雅大方，适配职场与约会等多场景"
            top = "衬衫、真丝上衣、修身针织衫"
            bottom = "直筒裤、吸烟裤、A字裙"
            dress = "衬衫裙、收腰连衣裙、针织连衣裙"

        else:  # 36+
            color = "米色、灰色、藏青、酒红、墨绿"
            style = "简约大气，垂感好的面料为主"
            matching = "低跟鞋、质感包袋、精致但不过量的配饰"
            age_fit = "端庄大气，凸显气质与质感"
            top = "真丝衬衫、针织开衫、品质外套"
            bottom = "阔腿裤、伞裙、直筒裙"
            dress = "收腰连衣裙、优雅套装"

    # 场景微调
    if scene == "职场":
        style += "，正式感略提升"
        matching += "，注意保持专业形象"
    elif scene == "约会":
        style += "，增加一点精致感与柔和度"
        matching += "，可适当增加女人味元素"
    elif scene == "运动":
        style = "舒适透气运动款，合身不紧绷"
        color = "黑白灰为主，小面积亮色点缀"
        matching = "专业运动鞋、吸汗头带/发带"
    elif scene == "聚会":
        style += "，可选择更有设计感的款式"
        matching += "，配饰可稍微夸张增加亮点"

    # 体型专项建议
    body_tip = ""
    if body_type == "苹果型":
        body_tip = "【体型建议】选择A字版型、高腰设计，避免紧身短款上衣"
    elif body_type == "梨形":
        body_tip = "【体型建议】推荐A字裙/阔腿裤平衡比例，深色下装更显瘦"
    elif body_type == "沙漏型":
        body_tip = "【体型建议】收腰设计和X型剪裁最能展现身材优势"
    elif body_type == "H型":
        body_tip = "【体型建议】用腰带、高腰或层穿创造腰线，优化身材比例"
    elif body_type == "倒三角型":
        body_tip = "【体型建议】下身选择A字版型或亮色，平衡肩宽比例"

    # 肤色专项建议
    skin_tip = ""
    if skin_undertone == "冷":
        skin_tip = "【肤色建议】冷色调肤色适合蓝、紫、粉系，提亮效果更好"
    elif skin_undertone == "暖":
        skin_tip = "【肤色建议】暖色调肤色适合黄、橙、大地色系，显气色"

    # 季节专项建议
    season_tip = ""
    if season_analysis.get("warnings"):
        season_tip = f"【季节建议】{'；'.join(season_analysis['warnings'])}"

    suggestion = {
        "color": color,
        "style": style,
        "matching": matching,
        "age_fit": age_fit,
        "body_tip": body_tip,
        "skin_tip": skin_tip,
        "season_tip": season_tip,
        "top": top if 'top' in dir() else "",
        "bottom": bottom if 'bottom' in dir() else "",
        "dress": dress if 'dress' in dir() else "",
        "priority": _get_priority_tips(score, body_analysis, skin_analysis)
    }

    return suggestion


def _get_priority_tips(
    score: float,
    body_analysis: dict,
    skin_analysis: dict
) -> list:
    """获取优先改进建议"""
    tips = []

    if score < 7.0:
        # 体型适配优先
        if body_analysis.get("disadvantages"):
            tips.append(body_analysis["disadvantages"][0])
        # 肤色匹配次之
        if skin_analysis.get("disadvantages"):
            tips.append(skin_analysis["disadvantages"][0])

    return tips


def _generate_tags(
    advantages: list,
    disadvantages: list,
    body_type: str,
    skin_undertone: str,
    scene: str
) -> list:
    """生成标签"""
    tags = []

    # 正面标签
    if any("完美" in x or "优秀" in x for x in advantages):
        tags.append("时尚达人")
    if any("协调" in x for x in advantages):
        tags.append("配色协调")
    if any("优化" in x or "黄金比例" in x for x in advantages):
        tags.append("身材优化")

    # 问题标签
    if any("杂乱" in x for x in disadvantages):
        tags.append("色彩杂乱")
    if any("过于宽松" in x for x in disadvantages):
        tags.append("版型问题")
    if any("不匹配" in x for x in disadvantages):
        tags.append("场景不适")

    # 特征标签
    tags.append(body_type)
    tags.append(f"{skin_undertone}肤色")
    tags.append(scene)

    return list(set(tags))


# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 测试用例
    test_cases = [
        {
            "name": "男性-职场-标准身材",
            "input": {
                "gender": "male",
                "age_range": "26-35",
                "scene": "职场",
                "img_features": {
                    "current_dress": "合身白衬衫、藏青色西裤、简约手表",
                    "body_type": "标准",
                    "skin_undertone": "自然",
                    "complexion": "正常",
                    "accessories": ["手表", "皮带"],
                    "season": "春秋"
                }
            }
        },
        {
            "name": "女性-约会-梨形身材",
            "input": {
                "gender": "female",
                "age_range": "26-35",
                "scene": "约会",
                "img_features": {
                    "current_dress": "高腰A字裙、白色针织衫、简约耳饰",
                    "body_type": "梨形",
                    "skin_undertone": "暖",
                    "complexion": "偏白",
                    "accessories": ["简约耳饰", "细项链"],
                    "season": "春秋"
                }
            }
        },
        {
            "name": "女性-日常-苹果型身材",
            "input": {
                "gender": "female",
                "age_range": "18-25",
                "scene": "日常",
                "img_features": {
                    "current_dress": "宽松T恤、紧身牛仔裤",
                    "body_type": "苹果型",
                    "skin_undertone": "冷",
                    "complexion": "正常",
                    "accessories": [],
                    "season": "夏"
                }
            }
        }
    ]

    print("=" * 60)
    print("增强版穿搭评价系统 - 测试用例")
    print("=" * 60)

    for case in test_cases:
        print(f"\n【{case['name']}】")
        result = minimax_dress_evaluation_enhanced(**case["input"])
        print(f"评分: {result['score']} - {result['score_desc']}")
        print(f"优势: {result['advantage']}")
        print(f"问题: {result['disadvantage']}")
        print(f"建议: {result['suggestion']['style']}")
        print("-" * 60)
