#!/usr/bin/env python3
"""
张雪峰 Skill 主入口模块。
基于用户意图进行分流处理：院校查询、专业分析、志愿填报、升学规划。
无任何OpenClaw依赖，纯本地逻辑。
"""

import sys
import json
import os
from typing import Dict, Any, List, Optional

# --- 模拟数据与配置 ---

# 院校数据库 (模拟)
COLLEGE_DB = {
    "清华大学": {
        "level": "C9/985/211",
        "city": "北京",
        "feature": "工科顶尖，毕业基本横着走，前提是你得能进去。"
    },
    "北京大学": {
        "level": "C9/985/211",
        "city": "北京",
        "feature": "文理医都很强，光华管理学院那是真牛。"
    },
    "复旦大学": {
        "level": "C9/985/211",
        "city": "上海",
        "feature": "江南学子向往之地，经管、新传都很强。"
    },
    "上海交通大学": {
        "level": "C9/985/211",
        "city": "上海",
        "feature": "工科强校，船舶、机械、计算机都不错。"
    },
    "浙江大学": {
        "level": "C9/985/211",
        "city": "杭州",
        "feature": "综合实力强，农学、工科、医科都有实力。"
    },
    "南京大学": {
        "level": "C9/985/211",
        "city": "南京",
        "feature": "文理见长，天文、地质是王牌。"
    },
    "中国科学技术大学": {
        "level": "C9/985/211",
        "city": "合肥",
        "feature": "理工科精英学府，科研氛围浓。"
    },
    "哈尔滨工业大学": {
        "level": "C9/985/211",
        "city": "哈尔滨",
        "feature": "工科老牌劲旅，航天、机械、计算机都很强。"
    },
    "西安交通大学": {
        "level": "C9/985/211",
        "city": "西安",
        "feature": "老牌工科强校，管理、电气、能动是招牌。"
    },
    "北京航空航天大学": {
        "level": "985/211",
        "city": "北京",
        "feature": "航天航空计算机都硬核，进大厂研究所的多。"
    },
    "北京理工大学": {
        "level": "985/211",
        "city": "北京",
        "feature": "工科实力派，车辆工程、自动化是强项。"
    },
    "同济大学": {
        "level": "985/211",
        "city": "上海",
        "feature": "建筑、土木、汽车工程是王牌。"
    },
    "华东师范大学": {
        "level": "985/211",
        "city": "上海",
        "feature": "师范类顶尖，想当老师的可以冲。"
    },
    "华中科技大学": {
        "level": "985/211",
        "city": "武汉",
        "feature": "工科强校，光电、计算机、机械都很牛。"
    },
    "武汉大学": {
        "level": "985/211",
        "city": "武汉",
        "feature": "综合实力强，法学、测绘、水利是招牌。"
    },
    "中山大学": {
        "level": "985/211",
        "city": "广州",
        "feature": "华南第一学府，医科、商科都很强。"
    },
    "四川大学": {
        "level": "985/211",
        "city": "成都",
        "feature": "医学、口腔、高分子是王牌。"
    },
    "电子科技大学": {
        "level": "985/211",
        "city": "成都",
        "feature": "电子信息类顶尖，计算机、通信就业无敌。"
    },
    "北京邮电大学": {
        "level": "211",
        "city": "北京",
        "feature": "通信、计算机就业王牌，进大厂的比例高。"
    },
    "西安电子科技大学": {
        "level": "211",
        "city": "西安",
        "feature": "电子信息类强校，性价比极高。"
    },
    "北京工业大学": {
        "level": "211",
        "city": "北京",
        "feature": "北京市属211，计算机、土木不错，在北京就业有优势。"
    },
    "苏州大学": {
        "level": "211",
        "city": "苏州",
        "feature": "江苏省属211，在苏州就业很有优势。"
    },
    "郑州大学": {
        "level": "211",
        "city": "郑州",
        "feature": "河南唯一211，人多分高，临床医学是王牌。"
    },
    "河南大学": {
        "level": "双一流",
        "city": "开封/郑州",
        "feature": "生物学一流学科，文科底蕴深厚，性价比不错。"
    },
    "北京信息科技大学": {
        "level": "普通本科",
        "city": "北京",
        "feature": "分数不高想留北京的工科生可以考虑，主打一个地域优势。"
    }
}

# 专业评价库 (张雪峰风格)
MAJOR_EVAL_DB = {
    "计算机": {
        "verdict": "可以学，但要做好996和35岁危机的准备。分高的冲华科、北邮，分低的找个理工科学校的软件工程也行，至少毕业能有个万把块工作。",
        "warning": "别以为学了计算机就能躺着进大厂，你得刷LeetCode刷到吐。"
    },
    "软件工程": {
        "verdict": "跟计算机差不多，更偏应用，学费可能贵点，但就业确实好。分不够计算机的，报这个没毛病。",
        "warning": None
    },
    "电子信息": {
        "verdict": "就业面广，通信、硬件、嵌入式都能搞。是个好方向，但课程难度也不小。",
        "warning": "别以为学这个就能进华为，得是真有两把刷子。"
    },
    "临床医学": {
        "verdict": "家里不差钱、孩子能吃苦、能熬到35岁以后结婚的，你就报。不然别选，周期太长，读出来头发都没了。",
        "warning": "劝人学医，天打雷劈。但你真想学，我敬你是条汉子。"
    },
    "口腔医学": {
        "verdict": "比临床医学轻松点，不用值夜班，是医学里性价比不错的方向。",
        "warning": "但分数也不低，得掂量掂量。"
    },
    "法学": {
        "verdict": "五院四系或者985的法学可以报，普通学校的法学毕业即失业，大概率去卖保险或考公三不限。",
        "warning": "法考通过率自己查查，别光看着律师在法庭上帅。"
    },
    "电气工程": {
        "verdict": "电网、设计院，稳定之选。分数不是特别高也能找到好工作，性价比可以。",
        "warning": None
    },
    "自动化": {
        "verdict": "万金油专业，就业面广，但学的东西多且杂。",
        "warning": "得自己找方向，别啥都学啥都不精。"
    },
    "机械工程": {
        "verdict": "传统工科，就业稳定但工资一般。车辆工程方向现在还不错。",
        "warning": "别指望像计算机那样拿高薪，但也不至于失业。"
    },
    "生物": {
        "verdict": "你家里有矿啊？没有的话这个专业你给我离得远远的。21世纪是生物的世纪？那是说给你爸妈听的。本科毕业除了当销售就是考研，考研出来还是做实验。",
        "warning": "四大天坑之首，慎入。"
    },
    "化学": {
        "verdict": "跟生物难兄难弟，化工厂、实验室，环境待遇自己琢磨。想当化学老师可以，其他就算了。",
        "warning": "天坑专业，能跑则跑。"
    },
    "环境": {
        "verdict": "环保是国策，但企业要盈利，环保岗位工资不高。除非你能进顶级设计院或者考公环保局，不然就是情怀。",
        "warning": "天坑之一。"
    },
    "材料": {
        "verdict": "新能源材料现在稍微好点，但传统材料比如金属、高分子，依然是坑。要学就奔着半导体、新能源方向去。",
        "warning": "四大天坑，现在勉强爬出来半个身子。"
    },
    "物理学": {
        "verdict": "当老师或者继续深造是主要出路，本科毕业不好就业。除非你真的热爱物理，愿意读到博士。",
        "warning": "纯物理就业难，师范物理还行。"
    },
    "数学": {
        "verdict": "万金油专业，转计算机、金融都很吃香。本科学数学，研究生再转方向，是条不错的路。",
        "warning": "前提是你数学得是真牛，不是高中那种数学好就行。"
    },
    "金融学": {
        "verdict": "名校金融才有出路，普通学校金融毕业大概率去银行当柜员或者卖保险。",
        "warning": "别看着电视剧里穿西装的banker就心动，那是极少数。"
    },
    "经济学": {
        "verdict": "跟金融类似，理论多实践少。就业不如金融，想好了再报。",
        "warning": None
    },
    "新闻传播": {
        "verdict": "新媒体时代，人人都能当自媒体。但传统媒体就业难，新媒体又不稳定。",
        "warning": "真想学的话，写作能力得强。"
    },
    "汉语言文学": {
        "verdict": "考公王牌专业，不想当老师的话，考公是个出路。",
        "warning": "就业面窄，想好再报。"
    },
    "英语": {
        "verdict": "翻译现在被AI冲击得厉害，当老师也不如以前香。英语+其他技能才是王炸。",
        "warning": "光会英语不够，得有个专业背景。"
    },
    "小语种": {
        "verdict": "学好了确实稀缺，但就业面太窄。俄语现在因为国际形势倒是有点机会。",
        "warning": "慎选，除非你真的热爱。"
    },
    "教育学": {
        "verdict": "当老师是个出路，但教育学本身教的偏理论。想当老师还是直接报师范专业更实在。",
        "warning": None
    },
    "土木工程": {
        "verdict": "前几年房地产火的时候还行，现在嘛...懂的都懂。设计院、施工单位，辛苦钱。",
        "warning": "行业下行期，慎入。"
    },
    "建筑学": {
        "verdict": "跟土木类似，房地产不景气的情况下，就业也不如从前。设计院加班多。",
        "warning": "但比土木稍微好点，建筑师还是需要的。"
    },
    "心理学": {
        "verdict": "本科就业难，心理咨询师门槛高。想学的话做好深造的准备。",
        "warning": "毕业大概率去当HR或者考公。"
    },
    "哲学": {
        "verdict": "热爱可以，但就业确实难。考公算是一条路。",
        "warning": "没矿别选。"
    },
    "历史学": {
        "verdict": "当老师或者继续深造是主要出路。",
        "warning": "就业面很窄。"
    }
}

# 往年投档线模拟数据 (位次)
RANK_DB = {
    "北京": {
        "理科": [
            {"school": "清华大学", "min_rank": 300},
            {"school": "北京大学", "min_rank": 320},
            {"school": "中国科学技术大学", "min_rank": 500},
            {"school": "复旦大学", "min_rank": 600},
            {"school": "上海交通大学", "min_rank": 700},
            {"school": "南京大学", "min_rank": 800},
            {"school": "北京航空航天大学", "min_rank": 1500},
            {"school": "北京理工大学", "min_rank": 2500},
            {"school": "哈尔滨工业大学", "min_rank": 3000},
            {"school": "华中科技大学", "min_rank": 3500},
            {"school": "武汉大学", "min_rank": 3800},
            {"school": "电子科技大学", "min_rank": 4000},
            {"school": "西安电子科技大学", "min_rank": 6000},
            {"school": "北京邮电大学", "min_rank": 5500},
            {"school": "北京工业大学", "min_rank": 8000},
            {"school": "苏州大学", "min_rank": 12000},
            {"school": "郑州大学", "min_rank": 12000},
            {"school": "北京信息科技大学", "min_rank": 20000}
        ],
        "文科": [
            {"school": "北京大学", "min_rank": 50},
            {"school": "复旦大学", "min_rank": 200},
            {"school": "南京大学", "min_rank": 300},
            {"school": "北京师范大学", "min_rank": 400},
            {"school": "华东师范大学", "min_rank": 600},
            {"school": "武汉大学", "min_rank": 800},
            {"school": "中山大学", "min_rank": 1000},
            {"school": "四川大学", "min_rank": 1500},
            {"school": "首都师范大学", "min_rank": 4000},
            {"school": "河南大学", "min_rank": 6000}
        ]
    },
    "河南": {
        "理科": [
            {"school": "清华大学", "min_rank": 100},
            {"school": "北京大学", "min_rank": 120},
            {"school": "复旦大学", "min_rank": 200},
            {"school": "上海交通大学", "min_rank": 220},
            {"school": "浙江大学", "min_rank": 250},
            {"school": "中国科学技术大学", "min_rank": 280},
            {"school": "南京大学", "min_rank": 300},
            {"school": "北京航空航天大学", "min_rank": 800},
            {"school": "哈尔滨工业大学", "min_rank": 1000},
            {"school": "华中科技大学", "min_rank": 1500},
            {"school": "武汉大学", "min_rank": 1600},
            {"school": "电子科技大学", "min_rank": 2000},
            {"school": "西安交通大学", "min_rank": 1800},
            {"school": "中山大学", "min_rank": 2200},
            {"school": "四川大学", "min_rank": 2500},
            {"school": "北京邮电大学", "min_rank": 3000},
            {"school": "西安电子科技大学", "min_rank": 4000},
            {"school": "郑州大学", "min_rank": 25000},
            {"school": "河南大学", "min_rank": 40000},
            {"school": "北京信息科技大学", "min_rank": 35000}
        ],
        "文科": [
            {"school": "北京大学", "min_rank": 50},
            {"school": "复旦大学", "min_rank": 100},
            {"school": "南京大学", "min_rank": 150},
            {"school": "武汉大学", "min_rank": 300},
            {"school": "中山大学", "min_rank": 350},
            {"school": "四川大学", "min_rank": 500},
            {"school": "华东师范大学", "min_rank": 600},
            {"school": "郑州大学", "min_rank": 4000},
            {"school": "河南大学", "min_rank": 8000}
        ]
    },
    "山东": {
        "理科": [
            {"school": "清华大学", "min_rank": 200},
            {"school": "北京大学", "min_rank": 220},
            {"school": "复旦大学", "min_rank": 400},
            {"school": "上海交通大学", "min_rank": 450},
            {"school": "浙江大学", "min_rank": 500},
            {"school": "南京大学", "min_rank": 550},
            {"school": "中国科学技术大学", "min_rank": 400},
            {"school": "北京航空航天大学", "min_rank": 1500},
            {"school": "哈尔滨工业大学", "min_rank": 1800},
            {"school": "华中科技大学", "min_rank": 2500},
            {"school": "武汉大学", "min_rank": 2600},
            {"school": "电子科技大学", "min_rank": 3000},
            {"school": "西安交通大学", "min_rank": 2800},
            {"school": "山东大学", "min_rank": 8000},
            {"school": "中国海洋大学", "min_rank": 12000}
        ],
        "文科": [
            {"school": "北京大学", "min_rank": 100},
            {"school": "复旦大学", "min_rank": 200},
            {"school": "南京大学", "min_rank": 300},
            {"school": "武汉大学", "min_rank": 500},
            {"school": "中山大学", "min_rank": 550},
            {"school": "山东大学", "min_rank": 2000},
            {"school": "中国海洋大学", "min_rank": 3500}
        ]
    },
    "江苏": {
        "理科": [
            {"school": "清华大学", "min_rank": 150},
            {"school": "北京大学", "min_rank": 170},
            {"school": "复旦大学", "min_rank": 300},
            {"school": "上海交通大学", "min_rank": 350},
            {"school": "浙江大学", "min_rank": 400},
            {"school": "南京大学", "min_rank": 450},
            {"school": "中国科学技术大学", "min_rank": 350},
            {"school": "北京航空航天大学", "min_rank": 1000},
            {"school": "哈尔滨工业大学", "min_rank": 1200},
            {"school": "华中科技大学", "min_rank": 1800},
            {"school": "东南大学", "min_rank": 2000},
            {"school": "南京航空航天大学", "min_rank": 3000},
            {"school": "南京理工大学", "min_rank": 4000},
            {"school": "苏州大学", "min_rank": 6000},
            {"school": "南京师范大学", "min_rank": 8000}
        ],
        "文科": [
            {"school": "北京大学", "min_rank": 80},
            {"school": "复旦大学", "min_rank": 150},
            {"school": "南京大学", "min_rank": 200},
            {"school": "东南大学", "min_rank": 600},
            {"school": "南京师范大学", "min_rank": 2000},
            {"school": "苏州大学", "min_rank": 1800}
        ]
    },
    "浙江": {
        "理科": [
            {"school": "清华大学", "min_rank": 100},
            {"school": "北京大学", "min_rank": 120},
            {"school": "复旦大学", "min_rank": 200},
            {"school": "上海交通大学", "min_rank": 180},
            {"school": "浙江大学", "min_rank": 500},
            {"school": "南京大学", "min_rank": 350},
            {"school": "中国科学技术大学", "min_rank": 250},
            {"school": "北京航空航天大学", "min_rank": 800},
            {"school": "哈尔滨工业大学", "min_rank": 900},
            {"school": "华中科技大学", "min_rank": 1200},
            {"school": "电子科技大学", "min_rank": 1500},
            {"school": "浙江工业大学", "min_rank": 15000},
            {"school": "宁波大学", "min_rank": 18000}
        ],
        "文科": [
            {"school": "北京大学", "min_rank": 50},
            {"school": "复旦大学", "min_rank": 100},
            {"school": "南京大学", "min_rank": 150},
            {"school": "浙江大学", "min_rank": 400},
            {"school": "浙江工业大学", "min_rank": 8000},
            {"school": "宁波大学", "min_rank": 10000}
        ]
    },
    "广东": {
        "理科": [
            {"school": "清华大学", "min_rank": 200},
            {"school": "北京大学", "min_rank": 220},
            {"school": "复旦大学", "min_rank": 400},
            {"school": "上海交通大学", "min_rank": 450},
            {"school": "中山大学", "min_rank": 3000},
            {"school": "华南理工大学", "min_rank": 5000},
            {"school": "暨南大学", "min_rank": 8000},
            {"school": "深圳大学", "min_rank": 12000},
            {"school": "华南师范大学", "min_rank": 10000}
        ],
        "文科": [
            {"school": "中山大学", "min_rank": 800},
            {"school": "华南理工大学", "min_rank": 2000},
            {"school": "暨南大学", "min_rank": 2500},
            {"school": "深圳大学", "min_rank": 3000}
        ]
    },
    "四川": {
        "理科": [
            {"school": "清华大学", "min_rank": 150},
            {"school": "北京大学", "min_rank": 170},
            {"school": "复旦大学", "min_rank": 300},
            {"school": "上海交通大学", "min_rank": 350},
            {"school": "四川大学", "min_rank": 5000},
            {"school": "电子科技大学", "min_rank": 4000},
            {"school": "西南交通大学", "min_rank": 8000},
            {"school": "四川农业大学", "min_rank": 20000}
        ],
        "文科": [
            {"school": "四川大学", "min_rank": 1500},
            {"school": "电子科技大学", "min_rank": 3000},
            {"school": "西南财经大学", "min_rank": 2500}
        ]
    },
    "湖北": {
        "理科": [
            {"school": "清华大学", "min_rank": 150},
            {"school": "北京大学", "min_rank": 170},
            {"school": "复旦大学", "min_rank": 300},
            {"school": "上海交通大学", "min_rank": 350},
            {"school": "华中科技大学", "min_rank": 3000},
            {"school": "武汉大学", "min_rank": 3200},
            {"school": "中南财经政法大学", "min_rank": 8000},
            {"school": "武汉理工大学", "min_rank": 10000}
        ],
        "文科": [
            {"school": "武汉大学", "min_rank": 500},
            {"school": "华中科技大学", "min_rank": 1200},
            {"school": "中南财经政法大学", "min_rank": 2000}
        ]
    }
}


# --- 意图识别与分支处理 ---

def _detect_intent(query: str) -> str:
    """根据用户查询判断意图"""
    if not query:
        return "general"
    if any(k in query for k in ["院校", "大学", "学校", "学院", "推荐学校", "什么学校"]):
        return "college"
    if any(k in query for k in ["专业", "学科", "就业", "前景", "学什么", "好不好", "怎么样"]):
        return "major"
    if any(k in query for k in ["志愿", "填报", "报考", "冲稳保", "能上什么", "分能", "位次"]):
        return "volunteer"
    if any(k in query for k in ["规划", "升学", "考研", "留学", "复读"]):
        return "plan"
    return "general"


def _handle_college_query(params: Dict) -> Dict:
    """院校查询"""
    school_name = params.get("school", "")
    if school_name in COLLEGE_DB:
        info = COLLEGE_DB[school_name]
        reply = f"【{school_name}】 {info['level']}，在{info['city']}。{info['feature']}"
    else:
        reply = f"关于【{school_name}】，数据暂未收录。但你可以告诉我具体想看哪个省市的学校，我给你捋捋。"
    return {"info": reply}


def _handle_major_query(params: Dict) -> Dict:
    """专业分析"""
    major_name = params.get("major", "")
    eval_data = MAJOR_EVAL_DB.get(major_name)
    if eval_data:
        reply = eval_data["verdict"]
        warning = eval_data.get("warning")
        if warning:
            reply += f" {warning}"
    else:
        reply = f"【{major_name}】这个专业我不常讲，但原则就一条：看它能不能让你毕业后有口饭吃，且饭里带点肉。你自己去查查对口岗位的招聘要求和薪资。"
    return {"evaluation": reply}


def _handle_volunteer_query(params: Dict) -> Dict:
    """志愿填报核心算法：基于位次的冲稳保"""
    province = params.get("province")
    stu_type = params.get("type")  # 理科/文科
    rank = params.get("rank")
    major_pref = params.get("major")

    if not province or not stu_type or not rank:
        raise ValueError("省份、文理科、位次缺一不可。你赶紧告诉我，别磨叽。")

    province_data = RANK_DB.get(province, {}).get(stu_type, [])
    if not province_data:
        return {
            "recommendations": [],
            "zhang_quote": f"我手里暂时没有{province}的详细数据，你先告诉我你的位次，我给你按通用逻辑盘盘道。"
        }

    recommendations = []
    for school in province_data:
        min_rank = school["min_rank"]
        if rank <= min_rank * 0.85:  # 冲
            tier = "冲"
            comment = "大胆冲！今年可能没人敢报，捡漏了你就是运气王。"
        elif rank <= min_rank * 1.1:  # 稳
            tier = "稳"
            comment = "这个区间最稳，正常发挥基本就是这儿了。"
        elif rank <= min_rank * 1.5:  # 保
            tier = "保"
            comment = "给你兜底的，闭着眼都能上，但大概率你也不想去。"
        else:
            continue  # 位次差距过大，不推荐

        recommendations.append({
            "school": school["school"],
            "tier": tier,
            "comment": comment
        })

    # 按tier分组
    chong = [r for r in recommendations if r["tier"] == "冲"]
    wen = [r for r in recommendations if r["tier"] == "稳"]
    bao = [r for r in recommendations if r["tier"] == "保"]

    # 专业点评 (张雪峰语录)
    zhang_quote = ""
    if major_pref:
        major_eval = MAJOR_EVAL_DB.get(major_pref)
        if major_eval:
            zhang_quote = f"\n\n另外，关于你想学【{major_pref}】专业：{major_eval['verdict']}"
            if major_eval.get("warning"):
                zhang_quote += f" {major_eval['warning']}"
        else:
            zhang_quote = f"\n\n你选的【{major_pref}】专业，自己打听好出路，别毕业了再来找我哭。"

    return {
        "recommendations": recommendations[:10],
        "chong": chong,
        "wen": wen,
        "bao": bao,
        "zhang_quote": zhang_quote
    }


def _handle_plan_query(params: Dict) -> Dict:
    """升学规划"""
    return {
        "advice": "升学规划是个长线活儿。我的原则就一条：以终为始。你想成为什么样的人，过什么样的生活，再倒推你现在该选什么路。别听别人忽悠，自己多查多问。"
    }


def _handle_general_query(params: Dict) -> Dict:
    """通用咨询"""
    return {
        "reply": "你问的这事儿，说大不大说小不小。我给你个实在建议：别想太多，先动起来查资料。实在不行，你再把具体问题细化一下问我。"
    }


# --- 主函数 ---
def run(input_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    执行Skill核心逻辑
    Args:
        input_data: { "query": "用户原话", "params": { ... } }
    Returns:
        { "status": "success"|"error", "data": ..., "message_for_user": ... }
    """
    try:
        input_data = input_data or {}
        query = input_data.get("query", "")
        params = input_data.get("params", {})

        # 如果 params 为空，尝试从 query 中简单提取
        if not params and query:
            # 这里仅做示意，实际由 AI 在调用前解析参数
            params = {"raw_query": query}

        intent = _detect_intent(query)
        data = {}

        if intent == "college":
            data = _handle_college_query(params)
        elif intent == "major":
            data = _handle_major_query(params)
        elif intent == "volunteer":
            data = _handle_volunteer_query(params)
        elif intent == "plan":
            data = _handle_plan_query(params)
        else:
            data = _handle_general_query(params)

        # 构造用户友好的消息
        if intent == "volunteer":
            recs = data.get("recommendations", [])
            chong = data.get("chong", [])
            wen = data.get("wen", [])
            bao = data.get("bao", [])

            if chong or wen or bao:
                msg = "根据你的位次，我给你划拉了几个学校：\n\n"

                if chong:
                    msg += "【冲 - 大胆冲，说不定就捡漏了】\n"
                    for r in chong[:3]:
                        msg += f"  - {r['school']}: {r['comment']}\n"
                    msg += "\n"

                if wen:
                    msg += "【稳 - 正常发挥就在这儿】\n"
                    for r in wen[:3]:
                        msg += f"  - {r['school']}: {r['comment']}\n"
                    msg += "\n"

                if bao:
                    msg += "【保 - 给你兜底的】\n"
                    for r in bao[:2]:
                        msg += f"  - {r['school']}: {r['comment']}\n"
                    msg += "\n"

                msg += data.get("zhang_quote", "")
                msg += "\n\n⚠️ 最后提醒：数据仅供参考！最终以省招办官方发布为准，别到时候滑档了来找我哭！"
            else:
                msg = data.get("zhang_quote", "数据不足，你再把位次报准确点。")
        elif intent == "college":
            msg = data.get("info", "你说，我听着呢。")
        elif intent == "major":
            msg = data.get("evaluation", "你说，我听着呢。")
        elif intent == "plan":
            msg = data.get("advice", "你说，我听着呢。")
        else:
            msg = data.get("reply", "你说，我听着呢。")

        return {
            "status": "success",
            "data": data,
            "message_for_user": msg
        }

    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message_for_user": f"出岔子了：{str(e)}。你检查下输入，咱重来。"
        }


if __name__ == "__main__":
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        input_data = json.loads(input_json) if input_json else {}
    else:
        input_data = {}
    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False, indent=2))
