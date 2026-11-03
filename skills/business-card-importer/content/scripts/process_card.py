#!/usr/bin/env python3
"""
名片信息处理脚本
Business Card Information Processing Script

按照规定格式处理名片数据并导入到Excel模板中。
"""

import re
import json
from typing import Dict, List, Optional, Any
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side


class BusinessCardProcessor:
    """名片信息处理器"""

    # 直辖市和特别行政区列表
    MUNICIPALITIES = {
        "北京": "北京",
        "上海": "上海",
        "天津": "天津",
        "重庆": "重庆",
        "香港": "香港",
        "澳门": "澳门",
        "台湾": "台湾"
    }

    def __init__(self):
        self.raw_data = {}
        self.processed_data = {}

    def normalize_company_name(self, company_name: str) -> str:
        """
        规范化英文公司名：首字母大写，其余小写，多个公司用 / 隔开
        """
        if not company_name:
            return ""

        # 按 / 分割处理多个公司
        companies = company_name.split("/")
        normalized = []

        for company in companies:
            company = company.strip()
            if not company:
                continue
            # 首字母大写，其余小写
            normalized.append(company.capitalize())

        return " / ".join(normalized)

    def normalize_chinese_company_name(self, company_name: str) -> str:
        """
        规范化中文公司名：保持原样，多个公司用 / 隔开
        """
        if not company_name:
            return ""

        # 按 / 分割处理多个公司
        companies = company_name.split("/")
        normalized = [c.strip() for c in companies if c.strip()]

        return " / ".join(normalized)

    def extract_china_mobile(self, phone: str) -> Optional[str]:
        """
        提取中国内地手机号码（11位数字）
        排除：+86、86-、+86 等国际区号格式
        """
        if not phone:
            return None

        # 清理空白字符
        phone = phone.strip()

        # 移除常见的国际区号前缀
        phone_clean = re.sub(r'^\+86[\s\-]?', '', phone)
        phone_clean = re.sub(r'^86[\s\-]?', '', phone_clean)
        phone_clean = re.sub(r'^\+?86', '', phone_clean)

        # 移除所有非数字字符
        digits_only = re.sub(r'\D', '', phone_clean)

        # 检查是否是11位中国手机号（以1开头）
        if len(digits_only) == 11 and digits_only.startswith('1'):
            return digits_only

        return None

    def normalize_email(self, email: str) -> str:
        """
        规范化邮箱地址：全部转为小写
        """
        if not email:
            return ""
        return email.strip().lower()

    def is_email(self, text: str) -> bool:
        """判断是否为邮箱地址"""
        if not text:
            return False
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, text.strip()))

    def is_mobile_phone(self, text: str) -> bool:
        """判断是否为手机号码"""
        if not text:
            return False
        # 清理后检查
        cleaned = re.sub(r'[\s\-\(\)\+]', '', text)
        digits = re.sub(r'\D', '', cleaned)
        # 检查是否是中国手机号
        if len(digits) == 11 and digits.startswith('1'):
            return True
        return False

    def is_china_mobile_format(self, text: str) -> bool:
        """判断是否是中国手机格式（可能是手机号）"""
        if not text:
            return False
        # 包含+86或11位数字
        if '+86' in text:
            return True
        cleaned = re.sub(r'\D', '', text)
        if len(cleaned) >= 11 and cleaned.startswith('1'):
            return True
        return False

    def extract_province_city(self, address: str) -> tuple:
        """
        从地址中提取省份和城市信息
        直辖市和特别行政区：省份和城市填写同一名称
        """
        if not address:
            return "", ""

        address = address.strip()

        # 常见省份关键词映射
        province_keywords = {
            # 直辖市
            "北京": "北京",
            "上海": "上海",
            "天津": "天津",
            "重庆": "重庆",
            # 特别行政区
            "香港": "香港",
            "澳门": "澳门",
            # 省份
            "河北省": "河北", "石家庄": "河北",
            "山西省": "山西", "太原": "山西",
            "辽宁省": "辽宁", "沈阳": "辽宁",
            "吉林省": "吉林", "长春": "吉林",
            "黑龙江省": "黑龙江", "哈尔滨": "黑龙江",
            "江苏省": "江苏", "南京": "江苏",
            "浙江省": "浙江", "杭州": "浙江",
            "安徽省": "安徽", "合肥": "安徽",
            "福建省": "福建", "福州": "福建",
            "江西省": "江西", "南昌": "江西",
            "山东省": "山东", "济南": "山东",
            "河南省": "河南", "郑州": "河南",
            "湖北省": "湖北", "武汉": "湖北",
            "湖南省": "湖南", "长沙": "湖南",
            "广东省": "广东", "广州": "广东",
            "海南省": "海南", "海口": "海南",
            "四川省": "四川", "成都": "四川",
            "贵州省": "贵州", "贵阳": "贵州",
            "云南省": "云南", "昆明": "云南",
            "陕西省": "陕西", "西安": "陕西",
            "甘肃省": "甘肃", "兰州": "甘肃",
            "青海省": "青海", "西宁": "青海",
            "内蒙古": "内蒙古", "呼和浩特": "内蒙古",
            "广西": "广西", "南宁": "广西",
            "西藏": "西藏", "拉萨": "西藏",
            "宁夏": "宁夏", "银川": "宁夏",
            "新疆": "新疆", "乌鲁木齐": "新疆",
        }

        province = ""
        city = ""
        found_municipality = None

        # 首先检查直辖市/特别行政区
        for keyword, name in self.MUNICIPALITIES.items():
            if keyword in address:
                found_municipality = name
                break

        if found_municipality:
            province = found_municipality
            city = found_municipality
        else:
            # 查找省份
            for keyword, prov in province_keywords.items():
                if keyword in address:
                    province = prov
                    break

            # 查找城市（更精确的匹配）
            city_keywords = {
                "南京": "南京", "杭州": "杭州", "合肥": "合肥",
                "福州": "福州", "南昌": "南昌", "济南": "济南",
                "郑州": "郑州", "武汉": "武汉", "长沙": "长沙",
                "广州": "广州", "深圳": "深圳", "海口": "海口",
                "成都": "成都", "贵阳": "贵阳", "昆明": "昆明",
                "西安": "西安", "兰州": "兰州", "西宁": "西宁",
                "呼和浩特": "呼和浩特", "南宁": "南宁", "拉萨": "拉萨",
                "银川": "银川", "乌鲁木齐": "乌鲁木齐",
                "石家庄": "石家庄", "唐山": "唐山", "沈阳": "沈阳",
                "大连": "大连", "长春": "长春", "吉林": "吉林",
                "哈尔滨": "哈尔滨", "苏州": "苏州", "宁波": "宁波",
                "厦门": "厦门", "青岛": "青岛", "东莞": "东莞",
                "佛山": "佛山", "重庆": "重庆",
            }
            for keyword, c in city_keywords.items():
                if keyword in address:
                    city = c
                    break

        return province, city

    def process_card_data(self, raw_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理名片原始数据，返回规范化后的数据
        """
        result = {}

        # Company Name（英文）
        if "company_en" in raw_info:
            result["Company Name"] = self.normalize_company_name(raw_info["company_en"])
        else:
            result["Company Name"] = ""

        # 公司名（中文）
        if "company_cn" in raw_info:
            result["公司名"] = self.normalize_chinese_company_name(raw_info["company_cn"])
        elif "company" in raw_info:
            result["公司名"] = self.normalize_chinese_company_name(raw_info["company"])
        else:
            result["公司名"] = ""

        # 初始化联系人相关字段
        for i in range(1, 5):
            result[f"联系人{i}"] = ""
            result[f"联系人{i}职位"] = ""
            result[f"联系人{i}手机1"] = ""
            result[f"联系人{i}手机2"] = ""
            result[f"联系人{i}邮箱1"] = ""
            result[f"联系人{i}邮箱2"] = ""
            result[f"联系人{i}邮箱3"] = ""
            result[f"联系人{i}邮箱4"] = ""
        if "联系人3手机3" not in result:
            result["联系人3手机3"] = ""
        if "联系人4手机2" not in result:
            result["联系人4手机2"] = ""

        # 处理联系人
        contacts = raw_info.get("contacts", [])
        for idx, contact in enumerate(contacts[:4]):  # 最多4个联系人
            i = idx + 1
            result[f"联系人{i}"] = contact.get("name", "")
            result[f"联系人{i}职位"] = contact.get("title", "")

            # 处理手机号码
            phones = contact.get("phones", [])
            mobile_idx = 1
            for phone in phones:
                mobile = self.extract_china_mobile(phone)
                if mobile:
                    if mobile_idx == 1:
                        result[f"联系人{i}手机1"] = mobile
                    elif mobile_idx == 2:
                        result[f"联系人{i}手机2"] = mobile
                    elif mobile_idx == 3 and i <= 3:  # 只有联系人1-3有手机3列
                        result[f"联系人{i}手机3"] = mobile
                    mobile_idx += 1

            # 处理邮箱
            emails = contact.get("emails", [])
            email_idx = 1
            for email in emails:
                normalized_email = self.normalize_email(email)
                if normalized_email:
                    if email_idx == 1:
                        result[f"联系人{i}邮箱1"] = normalized_email
                    elif email_idx == 2:
                        result[f"联系人{i}邮箱2"] = normalized_email
                    elif email_idx == 3:
                        result[f"联系人{i}邮箱3"] = normalized_email
                    elif email_idx == 4:
                        result[f"联系人{i}邮箱4"] = normalized_email
                    email_idx += 1

        # 公司电话和传真
        result["公司电话"] = raw_info.get("phone", "")
        result["公司传真"] = raw_info.get("fax", "")

        # 地址处理
        addresses = raw_info.get("addresses", [])
        for idx in range(3):  # 最多3个地址
            if idx < len(addresses):
                addr = addresses[idx]
                province, city = self.extract_province_city(addr)
                result[f"省份{idx+1}"] = province
                result[f"城市{idx+1}"] = city
                result[f"地址{idx+1}"] = addr
            else:
                result[f"省份{idx+1}"] = ""
                result[f"城市{idx+1}"] = ""
                result[f"地址{idx+1}"] = ""

        # 公司网址
        result["公司网址"] = raw_info.get("website", "")

        return result

    def import_to_excel(self, data: Dict[str, Any], template_path: str, output_path: str) -> bool:
        """
        将处理后的数据导入到Excel模板
        """
        try:
            wb = load_workbook(template_path)
            ws = wb.active

            # 找到数据起始行（模板最后一行+1）
            start_row = ws.max_row + 1

            # Excel列映射
            column_mapping = {
                "Company Name": "A",
                "公司名": "B",
                "联系人1": "D",
                "联系人1职位": "E",
                "联系人1手机1": "F",
                "联系人1手机2": "G",
                "联系人1手机3": "H",
                "联系人1邮箱1": "I",
                "联系人1邮箱2": "J",
                "联系人1邮箱3": "K",
                "联系人1邮箱4": "L",
                "联系人2": "M",
                "联系人2职位": "N",
                "联系人2手机1": "O",
                "联系人2手机2": "P",
                "联系人2邮箱1": "Q",
                "联系人2邮箱2": "R",
                "联系人3": "S",
                "联系人3职位": "T",
                "联系人3手机1": "U",
                "联系人3手机2": "V",
                "联系人3邮箱1": "W",
                "联系人3邮箱2": "X",
                "联系人4": "Y",
                "联系人4职位": "Z",
                "联系人4手机1": "AA",
                "联系人4手机2": "AB",
                "联系人4邮箱1": "AC",
                "联系人4邮箱2": "AD",
                "公司电话": "AE",
                "公司传真": "AF",
                "省份1": "AG",
                "城市1": "AH",
                "地址1": "AI",
                "省份2": "AJ",
                "城市2": "AK",
                "地址2": "AL",
                "省份3": "AM",
                "城市3": "AN",
                "地址3": "AO",
                "公司网址": "AP",
            }

            # 写入数据
            for field, col in column_mapping.items():
                if field in data and data[field]:
                    ws[f"{col}{start_row}"] = data[field]

            wb.save(output_path)
            return True

        except Exception as e:
            print(f"Error importing to Excel: {e}")
            return False


def main():
    """测试函数"""
    processor = BusinessCardProcessor()

    # 测试数据
    test_cases = [
        {
            "name": "测试1: 多公司多联系方式",
            "input": {
                "company_en": "ABC corp / xyz inc",
                "company_cn": "华为技术 / 腾讯科技",
                "contacts": [
                    {"name": "张三", "title": "销售总监", "phones": ["13812345678", "+86 13987654321"], "emails": ["ZhangSan@ABC.com"]},
                    {"name": "李四", "title": "技术经理", "phones": ["13711112222"], "emails": ["LiSi@ABC.com", "lisi_backup@xyz.com"]}
                ],
                "addresses": ["上海市浦东新区世纪大道100号", "北京市朝阳区建国路88号"],
                "website": "HTTPS://WWW.EXAMPLE.COM"
            }
        },
        {
            "name": "测试2: 国际号码处理",
            "input": {
                "company": "Test Company",
                "contacts": [
                    {"name": "王五", "title": "经理", "phones": ["+86 13812345678", "+86-139-8765-4321"], "emails": ["JOHN@EXAMPLE.COM"]}
                ],
                "addresses": ["北京市朝阳区建国路88号"],
                "website": "https://test.com"
            }
        }
    ]

    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"测试: {test['name']}")
        print(f"{'='*60}")
        result = processor.process_card_data(test["input"])
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
