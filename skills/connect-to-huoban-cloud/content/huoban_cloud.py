#!/usr/bin/env python3
"""
Huoban Cloud Connector - Huoban Cloud Data Management Skill
Extracts information from conversational input and automatically calls Huoban Cloud API
for data creation, querying, and modification operations.
"""

import json
import os
import re
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# ============== Configuration ==============
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SKILL_DIR, "config.json")
LOG_FILE = os.path.join(SKILL_DIR, "process.log")

DEFAULT_CONFIG = {
    "access_token": "",
    "current_wecom_user": "",
    "tables": {}
}

API_BASE_URL = "https://api.huoban.com/openapi/v1"


# ============== Config Management ==============

def load_config() -> Dict[str, Any]:
    """Load configuration from config.json"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to config.json"""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def log_process(user_message: str, result: Dict[str, Any],
                 process_steps: List[Dict] = None) -> None:
    """Log processing steps to process.log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "user_message": user_message,
        "process_steps": process_steps or [],
        "result": {
            "success": result.get("success"),
            "item_id": result.get("data", {}).get("item", {}).get("item_id") if result.get("data") else None,
            "error": result.get("error") or result.get("message")
        }
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


# ============== API Calls ==============

def api_request(url: str, method: str, access_token: str,
                payload: Dict = None) -> Optional[Dict]:
    """
    Make HTTP request to Huoban API

    Args:
        url: API endpoint URL
        method: HTTP method (GET, POST, PUT)
        access_token: API access token
        payload: Request body data

    Returns:
        Response data dict or None on failure
    """
    headers = {
        "Open-Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        data = json.dumps(payload or {}).encode('utf-8') if payload else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get("code") == 0:
                return result.get("data", {})
            else:
                print(f"API Error: {result.get('message')}")
                return None
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Request Error: {e}")
    return None


def get_table_list(space_id: str, access_token: str) -> Optional[List[Dict]]:
    """
    Get list of tables in a workspace

    API: POST https://api.huoban.com/openapi/v1/table/list
    Doc: https://openapi.huoban.com/api-17851168
    """
    url = f"{API_BASE_URL}/table/list"
    data = api_request(url, "POST", access_token, {"space_id": space_id})
    return data.get("tables", []) if data else None


def get_table_config(table_id: str, access_token: str) -> Optional[Dict]:
    """
    Get table configuration including fields

    API: POST https://api.huoban.com/openapi/v1/table/{table_id}
    Doc: https://openapi.huoban.com/api-17851169
    """
    url = f"{API_BASE_URL}/table/{table_id}"
    return api_request(url, "POST", access_token)


def query_items(table_id: str, filter_config: Dict = None,
                access_token: str = None, limit: int = 100,
                offset: int = 0) -> Optional[List[Dict]]:
    """
    Query items from a table

    API: POST https://api.huoban.com/openapi/v1/item/list
    Doc: https://openapi.huoban.com/api-17851170
    Filter Doc: https://openapi.huoban.com/doc-661258
    """
    url = f"{API_BASE_URL}/item/list"
    payload = {"table_id": table_id, "limit": limit, "offset": offset}
    if filter_config:
        payload["filter"] = filter_config
    data = api_request(url, "POST", access_token, payload)
    return data.get("items", []) if data else None


def get_item(item_id: str, access_token: str) -> Optional[Dict]:
    """
    Get single item details

    API: POST https://api.huoban.com/openapi/v1/item/{item_id}
    Doc: https://openapi.huoban.com/api-17851171
    """
    url = f"{API_BASE_URL}/item/{item_id}"
    return api_request(url, "POST", access_token)


def create_item(table_id: str, fields: Dict[str, Any],
                access_token: str) -> Dict[str, Any]:
    """
    Create new item in table

    API: POST https://api.huoban.com/openapi/v1/item
    Doc: https://openapi.huoban.com/api-17851172
    """
    url = f"{API_BASE_URL}/item"
    payload = {"table_id": table_id, "fields": fields}
    data = api_request(url, "POST", access_token, payload)

    if data:
        return {"success": True, "data": data}
    return {"success": False, "error": "Failed to create item"}


def update_item(item_id: str, fields: Dict[str, Any],
                access_token: str) -> Dict[str, Any]:
    """
    Update existing item

    API: PUT https://api.huoban.com/openapi/v1/item/{item_id}
    Doc: https://openapi.huoban.com/api-17851173
    """
    url = f"{API_BASE_URL}/item/{item_id}"
    payload = {"fields": fields}
    data = api_request(url, "PUT", access_token, payload)

    if data:
        return {"success": True, "data": data}
    return {"success": False, "error": "Failed to update item"}


# ============== Field Mapping ==============

def auto_map_category_fields(table_id: str, fields: Dict[str, Any],
                             config: Dict) -> Dict[str, Any]:
    """
    Convert category field values to option IDs based on table configuration

    Args:
        table_id: Target table ID
        fields: Fields dict with option names as values
        config: Table configuration with category_options

    Returns:
        Fields dict with option IDs instead of option names
    """
    if table_id not in config.get("tables", {}):
        return fields

    table_config = config["tables"][table_id]
    full_fields = table_config.get("full_fields_config", {})
    result_fields = dict(fields)

    for field_id, field_value in fields.items():
        if field_id not in full_fields:
            continue

        field_info = full_fields[field_id]
        if field_info.get("field_type") != "category":
            continue

        is_multi = field_info.get("config", {}).get("is_multi", 0)
        options = field_info.get("config", {}).get("options", [])

        if isinstance(field_value, str):
            for option in options:
                if option.get("name") == field_value:
                    result_fields[field_id] = [{"id": option.get("id")}] if is_multi else {"id": option.get("id")}
                    break
        elif isinstance(field_value, list):
            mapped_options = []
            for item in field_value:
                if isinstance(item, str):
                    for option in options:
                        if option.get("name") == item:
                            mapped_options.append({"id": option.get("id")})
                            break
                else:
                    mapped_options.append(item)
            result_fields[field_id] = mapped_options if is_multi else (mapped_options[0] if mapped_options else {"id": None})

    return result_fields


def map_to_huoban_fields(extracted_info: Dict, table_config: Dict) -> Dict[str, Any]:
    """
    Map extracted information to Huoban field format

    Args:
        extracted_info: Dict of {keyword: value} extracted from user message
        table_config: Table configuration including field_mapping and category_options

    Returns:
        Dict of {field_id: value} ready for API calls
    """
    fields = table_config.get("fields", {})
    field_mapping = table_config.get("field_mapping", {})
    category_options = table_config.get("category_options", {})
    full_fields_config = table_config.get("full_fields_config", {})

    huoban_fields = {}

    for key, value in extracted_info.items():
        field_id = field_mapping.get(key)

        if not field_id:
            for fid, fname in fields.items():
                if fname == key or key in fname:
                    field_id = fid
                    break

        if not field_id:
            for fid, fname in fields.items():
                if key in fname or fname in key:
                    field_id = fid
                    break

        if field_id:
            if field_id in category_options:
                options = category_options[field_id]
                option_id = None

                for opt in options:
                    if opt.get("name") == value:
                        option_id = opt.get("id")
                        break

                if not option_id:
                    for opt in options:
                        if value in opt.get("name") or opt.get("name") in value:
                            option_id = opt.get("id")
                            break

                if not option_id:
                    cleaned = value.replace("跟进", "").replace("客户", "").strip()
                    for opt in options:
                        opt_name = opt.get("name", "")
                        if cleaned in opt_name or opt_name in cleaned:
                            option_id = opt.get("id")
                            break

                if option_id:
                    huoban_fields[field_id] = [option_id]

            elif full_fields_config.get(field_id, {}).get("field_type") in ["numeric", "money"]:
                try:
                    huoban_fields[field_id] = int(value) if str(value).isdigit() else float(value)
                except:
                    huoban_fields[field_id] = value
            else:
                huoban_fields[field_id] = value

    return huoban_fields


# ============== Information Extraction ==============

def extract_info_from_text(text: str) -> Dict[str, Any]:
    """
    Extract structured information from user message

    Supported patterns:
    - Phone: 11-digit mobile (1[3-9]\\d{9})
    - Email: Standard email format
    - Date: Multiple formats (2024-03-11, 今天, 明天)
    - Time: With AM/PM support (上午10点)
    - Money: With currency (100元)
    - Age: With unit (25岁)
    - Keywords: Matched against field_mapping

    Returns:
        Dict of {field_name: extracted_value}
    """
    extracted = {}

    # Phone number pattern
    phone_pattern = r'1[3-9]\d{9}'
    phones = re.findall(phone_pattern, text)
    if phones:
        extracted["电话"] = phones[0]
    else:
        short_phone = r'\b(\d{3,8})\b'
        short_phones = re.findall(short_phone, text)
        for p in short_phones:
            if p.startswith('19') or p.startswith('20'):
                continue
            if len(p) >= 3:
                extracted["电话"] = p
                break

    # Email pattern
    email_pattern = r'\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'
    emails = re.findall(email_pattern, text)
    if emails:
        extracted["邮箱"] = emails[0]

    # Money pattern
    money_pattern = r'(\d+(?:\.\d+)?)\s*元'
    money = re.findall(money_pattern, text)
    if money:
        extracted["金额"] = money[0]

    # Age pattern
    age_pattern = r'(\d+)\s*岁'
    ages = re.findall(age_pattern, text)
    if ages:
        extracted["年龄"] = ages[0]

    # Date patterns
    date_pattern1 = r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)'
    dates = re.findall(date_pattern1, text)

    time_hour = None
    if "上午" in text:
        match = re.search(r'上午(\d{1,2})点', text)
        if match:
            time_hour = int(match.group(1))
    elif "下午" in text:
        match = re.search(r'下午(\d{1,2})点', text)
        if match:
            time_hour = 12 + int(match.group(1))
    elif "晚上" in text:
        match = re.search(r'晚上(\d{1,2})点', text)
        if match:
            time_hour = 18 + int(match.group(1))

    if not dates:
        date_pattern2 = r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}\s+\d{1,2}:\d{2}(?::\d{2})?)'
        dates = re.findall(date_pattern2, text)

    if not dates:
        today = datetime.now().date()
        if "今天" in text:
            dates = [today.strftime("%Y-%m-%d")]
        elif "明天" in text:
            dates = [(today + timedelta(days=1)).strftime("%Y-%m-%d")]
        elif "后天" in text:
            dates = [(today + timedelta(days=2)).strftime("%Y-%m-%d")]

    if dates:
        date_val = dates[0].replace('年', '-').replace('月', '-').replace('日', '')
        if time_hour is not None:
            date_val = f"{date_val} {time_hour}:00:00"
        extracted["日期"] = date_val

    # Customer name patterns
    name_pattern1 = r'客户姓名([\u4e00-\u9fa5]{2,4})'
    matches = re.findall(name_pattern1, text)
    if matches:
        extracted["客户"] = matches[0]

    if "客户" not in extracted:
        for match in re.finditer(r'客户', text):
            pos = match.start()
            if text[pos:pos+2] == '客户类型' or text[pos:pos+4] == '客户跟进':
                continue
            if text[pos:pos+4] == '客户姓名':
                continue
            value_part = text[pos + len("客户"):]
            for sep in ['、', '，', ',', ' ']:
                if value_part.startswith(sep):
                    value_part = value_part[1:]
            match2 = re.match(r'^([\u4e00-\u9fa5]{2})', value_part)
            if match2:
                candidate = match2.group(1)
                if candidate not in ['类型', '跟进', '姓名', '电话', '邮箱', '地址', '备注', '金额', '日期']:
                    extracted["客户"] = candidate
                    break

    # Customer type
    if "客户类型" in text:
        idx = text.find("客户类型")
        value_part = text[idx + len("客户类型"):]
        for sep in ['：', ':', '为', '是', ' ']:
            if value_part.startswith(sep):
                value_part = value_part[1:]
        for kw in ['、', '，', ',', '。']:
            if kw in value_part:
                value_part = value_part.split(kw)[0]
        if value_part.strip():
            extracted["客户类型"] = value_part.strip()

    # Key-value patterns: "字段名: 值"
    pattern1 = r'([\u4e00-\u9fa5a-zA-Z]+)[：:]\s*([^，,\n{}/]+)'
    for field_name, field_value in re.findall(pattern1, text):
        field_name = field_name.strip()
        field_value = field_value.strip()
        if field_value and len(field_value) < 50:
            if field_name not in ["电话", "邮箱"]:
                extracted[field_name] = field_value

    # Follow-up content
    if "跟进内容" in text:
        idx = text.find("跟进内容")
        value_part = text[idx + len("跟进内容"):]
        for sep in ['：', ':', '为', '是']:
            if value_part.startswith(sep):
                value_part = value_part[1:]
        if "跟进时间" in value_part:
            value_part = value_part.split("跟进时间")[0]
        if value_part.strip():
            extracted["跟进内容"] = value_part.strip()

    # Follow-up time
    if "跟进时间" in text:
        if "日期" in extracted:
            extracted["跟进时间"] = extracted["日期"]
        else:
            idx = text.find("跟进时间")
            value_part = text[idx + len("跟进时间"):]
            for sep in ['：', ':', '为', '是']:
                if value_part.startswith(sep):
                    value_part = value_part[1:]
            if value_part.strip():
                extracted["跟进时间"] = value_part.strip()

    return extracted


def build_filter_from_text(text: str, table_config: Dict) -> Dict:
    """
    Build filter configuration from query text

    Supports patterns like:
    - "客户姓名为张三" -> eq
    - "金额大于100" -> gt
    - "客户类型是重点客户" -> eq

    Returns:
        {"and": [{"field": "field_id", "query": {"operator": "value"}}]}
    """
    fields = table_config.get("fields", {})
    field_mapping = table_config.get("field_mapping", {})
    full_config = table_config.get("full_fields_config", {})
    category_options = table_config.get("category_options", {})

    conds = []

    patterns = [
        r'([\u4e00-\u9fa5a-zA-Z]+)(?:等于|为|是)\s*([^，,\n]+)',
        r'([\u4e00-\u9fa5a-zA-Z]+)[：:]\s*([^，,\n]+)',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text)
        for field_name, value in matches:
            field_name = field_name.strip()
            value = value.strip()

            field_id = field_mapping.get(field_name)
            if not field_id:
                for fid, fname in fields.items():
                    if field_name in fname or fname in field_name:
                        field_id = fid
                        break

            if field_id and value:
                field_info = full_config.get(field_id, {})
                field_type = field_info.get("field_type")
                query = {}

                if field_type in ["numeric", "money", "number"]:
                    num_match = re.match(r'(>=|<=|>|<)?\s*(\d+\.?\d*)', value)
                    if num_match:
                        op, num = num_match.groups()
                        if op == '>':
                            query = {"gt": float(num)}
                        elif op == '>=':
                            query = {"gte": float(num)}
                        elif op == '<':
                            query = {"lt": float(num)}
                        elif op == '<=':
                            query = {"lte": float(num)}
                        else:
                            query = {"eq": float(num)}
                    else:
                        query = {"eq": int(value) if value.isdigit() else value}

                elif field_type == "category":
                    options = category_options.get(field_id, [])
                    option_id = None
                    for opt in options:
                        if opt.get("name") == value:
                            option_id = opt.get("id")
                            break
                    if not option_id:
                        for opt in options:
                            if value in opt.get("name", "") or opt.get("name", "") in value:
                                option_id = opt.get("id")
                                break
                    if option_id:
                        query = {"eq": [option_id]}

                elif field_type == "date":
                    query = {"eq": value}
                else:
                    query = {"inc": value}

                if query:
                    conds.append({"field": field_id, "query": query})

    return {"and": conds} if conds else {}


# ============== Relation Handling ==============

def resolve_relation_fields(table_id: str, huoban_fields: Dict[str, Any],
                            table_config: Dict, access_token: str,
                            config: Dict) -> tuple:
    """
    Resolve relation fields by finding related item IDs

    Returns:
        (resolved_fields, process_steps)
    """
    fields_dict = table_config.get("fields", {})
    relation_configs = table_config.get("relation_configs", {})
    current_wecom_user = config.get("current_wecom_user", "")
    resolved_fields = dict(huoban_fields)
    process_steps = []

    for field_id, field_name in fields_dict.items():
        if field_id not in relation_configs and "关联" not in field_name:
            continue

        rel_config = relation_configs.get(field_id, {})
        relation_table_id = rel_config.get("table_id")
        relation_field_id = None

        if relation_table_id and relation_table_id in config.get("tables", {}):
            rel_table_fields = config["tables"][relation_table_id].get("fields", {})
            for fid, fname in rel_table_fields.items():
                if "姓名" in fname or "名称" in fname or "名" in fname:
                    relation_field_id = fid
                    break
            if not relation_field_id and rel_table_fields:
                relation_field_id = list(rel_table_fields.keys())[0]

        if not relation_table_id:
            if "客户" in field_name and "2100000074953145" in config.get("tables", {}):
                relation_table_id = "2100000074953145"
                relation_field_id = "2200000594696996"

        if relation_table_id and relation_field_id and field_id in resolved_fields:
            current_value = resolved_fields[field_id]
            if isinstance(current_value, str):
                process_steps.append({
                    "step": "Relation Query",
                    "field": field_name,
                    "search_value": current_value,
                    "relation_table": relation_table_id
                })

                filter_config = {"and": [{"field": relation_field_id, "query": {"eq": current_value}}]}
                items = query_items(relation_table_id, filter_config, access_token)
                if items:
                    related_item_id = items[0].get("item_id")
                    resolved_fields[field_id] = [related_item_id]
                    process_steps.append({
                        "step": "Relation Resolved",
                        "field": field_name,
                        "item_id": related_item_id
                    })
                else:
                    return {}, [{
                        "step": "Error",
                        "message": f"Related '{field_name}' '{current_value}' not found"
                    }]

    # Auto-fill current user for employee relations
    for field_id, field_name in fields_dict.items():
        if field_id in relation_configs and field_id not in resolved_fields and current_wecom_user:
            rel_config = relation_configs[field_id]
            relation_table_id = rel_config.get("table_id")
            if relation_table_id and "员工" in config.get("tables", {}).get(relation_table_id, {}).get("name", ""):
                employee_fields = config.get("tables", {}).get(relation_table_id, {}).get("fields", {})
                wecom_user_field_id = None
                for fid, fname in employee_fields.items():
                    if "企微" in fname or "企业微信" in fname:
                        wecom_user_field_id = fid
                        break

                if wecom_user_field_id:
                    filter_config = {"and": [{"field": wecom_user_field_id, "query": {"eq": current_wecom_user}}]}
                    items = query_items(relation_table_id, filter_config, access_token)
                    if items:
                        employee_item_id = items[0].get("item_id")
                        resolved_fields[field_id] = [employee_item_id]
                        process_steps.append({
                            "step": "Auto-fill Current User",
                            "field": field_name,
                            "item_id": employee_item_id
                        })

    return resolved_fields, process_steps


# ============== High-level Operations ==============

def setup(access_token: str) -> Dict:
    """Configure access token"""
    config = load_config()
    config["access_token"] = access_token
    save_config(config)
    return {"success": True, "message": "Access token configured"}


def add_table(table_id: str, table_name: str = None) -> Dict:
    """Add and configure a table"""
    config = load_config()
    if not config.get("access_token"):
        return {"success": False, "error": "Please configure access token first"}

    table_config = get_table_config(table_id, config["access_token"])
    if not table_config:
        return {"success": False, "error": f"Failed to get config for table {table_id}"}

    table_info = table_config.get("table", {})
    table_fields = table_info.get("fields", [])

    fields_dict = {}
    relation_configs = {}
    full_fields_config = {}
    category_options = {}

    for field in table_fields:
        field_id = field.get("field_id")
        field_name = field.get("name")
        field_type = field.get("field_type")
        field_config = field.get("config", {})

        if field_id and field_name:
            fields_dict[field_id] = field_name
            full_fields_config[field_id] = field

            if field_type == "relation":
                rel_table_id = field_config.get("table_id")
                if rel_table_id:
                    relation_configs[field_id] = {"table_id": rel_table_id, "name": field_name}

            if field_type == "category" and field_config.get("options"):
                category_options[field_id] = field_config.get("options")

    if "tables" not in config:
        config["tables"] = {}

    config["tables"][table_id] = {
        "name": table_name or table_info.get("name", "Unnamed"),
        "fields": fields_dict,
        "full_fields_config": full_fields_config,
        "field_mapping": {},
        "relation_configs": relation_configs,
        "category_options": category_options
    }

    save_config(config)
    return {
        "success": True,
        "table_id": table_id,
        "table_name": table_info.get("name"),
        "fields": fields_dict,
        "message": f"Table '{table_info.get('name')}' added with {len(fields_dict)} fields"
    }


def sync_table(table_id: str) -> Dict:
    """Sync table configuration from API and auto-generate field mappings"""
    config = load_config()
    if not config.get("access_token"):
        return {"success": False, "error": "Please configure access token first"}

    table_config = get_table_config(table_id, config["access_token"])
    if not table_config:
        return {"success": False, "error": f"Failed to get config for table {table_id}"}

    table_info = table_config.get("table", {})
    table_fields = table_info.get("fields", [])

    fields_dict = {}
    full_fields_config = {}
    relation_configs = {}
    auto_field_mapping = {}
    category_options = {}

    for field in table_fields:
        field_id = field.get("field_id")
        field_name = field.get("name")
        field_alias = field.get("alias")
        field_type = field.get("field_type")
        field_config = field.get("config", {})

        if field_id and field_name:
            fields_dict[field_id] = field_name
            full_fields_config[field_id] = field

            auto_field_mapping[field_name] = field_id
            if field_alias:
                auto_field_mapping[field_alias] = field_id
            if "客户" in field_name:
                clean_name = field_name.replace("客户", "")
                if clean_name:
                    auto_field_mapping[clean_name] = field_id

            if field_type == "relation":
                rel_table_id = field_config.get("table_id")
                if rel_table_id:
                    relation_configs[field_id] = {
                        "table_id": rel_table_id,
                        "name": field_name,
                        "is_multi": field_config.get("is_multi", 0)
                    }

            if field_type == "category" and field_config.get("options"):
                category_options[field_id] = field_config.get("options")

    if table_id not in config.get("tables", {}):
        return {"success": False, "error": f"Table {table_id} not added yet"}

    old_field_mapping = config["tables"][table_id].get("field_mapping", {})
    merged_field_mapping = {**old_field_mapping, **auto_field_mapping}

    config["tables"][table_id] = {
        "name": table_info.get("name"),
        "fields": fields_dict,
        "full_fields_config": full_fields_config,
        "field_mapping": merged_field_mapping,
        "relation_configs": relation_configs,
        "category_options": category_options
    }
    save_config(config)

    return {
        "success": True,
        "message": f"Table '{table_info.get('name')}' synced",
        "fields": fields_dict,
        "field_mapping": merged_field_mapping
    }


def init_workspace(space_id: str) -> Dict:
    """Initialize workspace: get all tables and configure them"""
    config = load_config()
    if not config.get("access_token"):
        return {"success": False, "error": "Please configure access token first"}

    print(f"Initializing workspace: {space_id}")

    config["tables"] = {}
    save_config(config)

    tables = get_table_list(space_id, config["access_token"])
    if not tables:
        return {"success": False, "error": "Failed to get table list"}

    print(f"Found {len(tables)} tables")

    success_count = 0
    results = []

    for i, table in enumerate(tables):
        table_id = table.get("table_id")
        table_name = table.get("name")

        print(f"[{i+1}/{len(tables)}] Processing: {table_name}")

        table_config = get_table_config(table_id, config["access_token"])
        if not table_config:
            print(f"  Failed to get config")
            results.append({"table_id": table_id, "name": table_name, "success": False})
            continue

        table_info = table_config.get("table", {})
        table_fields = table_info.get("fields", [])

        fields_dict = {}
        full_fields_config = {}
        relation_configs = {}
        auto_field_mapping = {}
        category_options = {}

        for field in table_fields:
            field_id = field.get("field_id")
            field_name = field.get("name")
            field_alias = field.get("alias")
            field_type = field.get("field_type")
            field_config = field.get("config", {})

            if field_id and field_name:
                fields_dict[field_id] = field_name
                full_fields_config[field_id] = field
                auto_field_mapping[field_name] = field_name
                if field_alias:
                    auto_field_mapping[field_alias] = field_id
                if "客户" in field_name:
                    clean_name = field_name.replace("客户", "")
                    if clean_name:
                        auto_field_mapping[clean_name] = field_id

                if field_type == "relation":
                    rel_table_id = field_config.get("table_id")
                    if rel_table_id:
                        relation_configs[field_id] = {
                            "table_id": rel_table_id,
                            "name": field_name,
                            "is_multi": field_config.get("is_multi", 0)
                        }

                if field_type == "category" and field_config.get("options"):
                    category_options[field_id] = field_config.get("options")

        config["tables"][table_id] = {
            "name": table_name,
            "fields": fields_dict,
            "full_fields_config": full_fields_config,
            "field_mapping": auto_field_mapping,
            "relation_configs": relation_configs,
            "category_options": category_options
        }

        success_count += 1
        results.append({
            "table_id": table_id,
            "name": table_name,
            "success": True,
            "field_count": len(fields_dict)
        })
        print(f"  OK: {len(fields_dict)} fields")

        save_config(config)

    save_config(config)
    return {
        "success": True,
        "message": f"Initialized {success_count}/{len(tables)} tables",
        "total": len(tables),
        "success_count": success_count,
        "results": results
    }


def list_tables() -> List[Dict]:
    """List all configured tables"""
    config = load_config()
    result = []
    for table_id, table_info in config.get("tables", {}).items():
        result.append({
            "table_id": table_id,
            "name": table_info.get("name"),
            "field_count": len(table_info.get("fields", {})),
            "field_mapping_count": len(table_info.get("field_mapping", {}))
        })
    return result


def show_fields(table_id: str) -> Optional[Dict]:
    """Show detailed field information for a table"""
    config = load_config()
    if table_id not in config.get("tables", {}):
        return None

    table = config["tables"][table_id]
    return {
        "table_id": table_id,
        "name": table.get("name"),
        "fields": table.get("full_fields_config", {})
    }


# ============== Data Operations ==============

def run(user_message: str, table_id: str = None) -> Dict[str, Any]:
    """
    Main entry point: Create data from user message

    Args:
        user_message: User's message containing data to create
        table_id: Target table ID (optional, uses first table if not specified)

    Returns:
        Result dict with success status and created item info
    """
    config = load_config()
    process_steps = []

    if not config.get("access_token"):
        return {"success": False, "message": "Please configure access token", "action": "setup"}

    if not table_id:
        tables = config.get("tables", {})
        if not tables:
            return {"success": False, "message": "No tables configured", "action": "add_table"}
        table_id = list(tables.keys())[0]

    if table_id not in config.get("tables", {}):
        return {"success": False, "message": f"Table {table_id} not configured", "action": "add_table"}

    table_config = config["tables"][table_id]
    access_token = config["access_token"]

    process_steps.append({
        "step": "Select Table",
        "table_id": table_id,
        "table_name": table_config.get("name", table_id)
    })

    extracted = extract_info_from_text(user_message)
    process_steps.append({"step": "Extract Info", "extracted": extracted})

    if not extracted:
        result = {"success": False, "message": "No valid information extracted", "extracted": {}}
        log_process(user_message, result, process_steps)
        return result

    huoban_fields = map_to_huoban_fields(extracted, table_config)
    huoban_fields = auto_map_category_fields(table_id, huoban_fields, config)
    process_steps.append({"step": "Map Fields", "huoban_fields": huoban_fields})

    if not huoban_fields:
        result = {"success": False, "message": "Cannot map to any fields", "extracted": extracted}
        log_process(user_message, result, process_steps)
        return result

    resolved_fields, relation_steps = resolve_relation_fields(
        table_id, huoban_fields, table_config, access_token, config
    )
    process_steps.extend(relation_steps)

    if not resolved_fields:
        result = {"success": False, "message": "Failed to resolve relation fields"}
        log_process(user_message, result, process_steps)
        return result

    process_steps.append({"step": "Create Item", "fields": resolved_fields})
    result = create_item(table_id, resolved_fields, access_token)

    if result.get("success"):
        item_id = result.get("data", {}).get("item", {}).get("item_id")
        process_steps.append({"step": "Created", "item_id": item_id})

    log_process(user_message, result, process_steps)
    return result


def query(query_message: str, table_id: str = None, limit: int = 20) -> Dict[str, Any]:
    """
    Query data from table

    Args:
        query_message: Query condition from user
        table_id: Target table ID
        limit: Maximum results to return

    Returns:
        Result dict with query results
    """
    config = load_config()

    if not config.get("access_token"):
        return {"success": False, "message": "Please configure access token"}

    if not table_id:
        tables = config.get("tables", {})
        if not tables:
            return {"success": False, "message": "No tables configured"}
        table_id = list(tables.keys())[0]

    if table_id not in config.get("tables", {}):
        return {"success": False, "message": f"Table {table_id} not configured"}

    table_config = config["tables"][table_id]
    access_token = config["access_token"]

    filter_config = build_filter_from_text(query_message, table_config)
    items = query_items(table_id, filter_config, access_token, limit=limit)

    if items is not None:
        return {
            "success": True,
            "table_name": table_config.get("name", table_id),
            "items": items,
            "count": len(items)
        }
    return {"success": False, "message": "Query failed"}


def modify(item_id: str, user_message: str, table_id: str = None) -> Dict[str, Any]:
    """
    Update existing item

    Args:
        item_id: Item ID to update
        user_message: Modification content
        table_id: Target table ID

    Returns:
        Result dict with update status
    """
    config = load_config()

    if not config.get("access_token"):
        return {"success": False, "message": "Please configure access token"}

    if not table_id:
        tables = config.get("tables", {})
        if not tables:
            return {"success": False, "message": "No tables configured"}
        table_id = list(tables.keys())[0]

    if table_id not in config.get("tables", {}):
        return {"success": False, "message": f"Table {table_id} not configured"}

    table_config = config["tables"][table_id]
    access_token = config["access_token"]

    extracted = extract_info_from_text(user_message)
    if not extracted:
        return {"success": False, "message": "No modification content extracted"}

    huoban_fields = map_to_huoban_fields(extracted, table_config)
    huoban_fields = auto_map_category_fields(table_id, huoban_fields, config)

    if not huoban_fields:
        return {"success": False, "message": "Cannot map to any fields"}

    resolved_fields, _ = resolve_relation_fields(
        table_id, huoban_fields, table_config, access_token, config
    )

    if not resolved_fields:
        return {"success": False, "message": "Failed to resolve relation fields"}

    return update_item(item_id, resolved_fields, access_token)


# ============== CLI Interface ==============

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("ConnectToHuobanCloud - Huoban Cloud Data Management")
        print("\nCommands:")
        print("  setup <token>                    Configure access token")
        print("  init <space_id>                  Initialize workspace")
        print("  add <table_id> [name]            Add a table")
        print("  update <table_id>                 Update table config")
        print("  list                             List all tables")
        print("  fields <table_id>                Show table fields")
        print("  run <table_id> <message>         Create data")
        print("  query <table_id> <condition>     Query data")
        print("  modify <table_id> <item_id> <msg> Update data")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "setup":
        if len(sys.argv) < 3:
            print("Usage: setup <access_token>")
            sys.exit(1)
        result = setup(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "init":
        if len(sys.argv) < 3:
            print("Usage: init <space_id>")
            sys.exit(1)
        result = init_workspace(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "add":
        if len(sys.argv) < 3:
            print("Usage: add <table_id> [table_name]")
            sys.exit(1)
        table_id = sys.argv[2]
        table_name = sys.argv[3] if len(sys.argv) > 3 else None
        result = add_table(table_id, table_name)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "update":
        if len(sys.argv) < 3:
            print("Usage: update <table_id>")
            sys.exit(1)
        result = sync_table(sys.argv[2])
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "list":
        result = list_tables()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "fields":
        if len(sys.argv) < 3:
            print("Usage: fields <table_id>")
            sys.exit(1)
        result = show_fields(sys.argv[2])
        if result:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Table {sys.argv[2]} not found")

    elif cmd == "run":
        if len(sys.argv) < 4:
            print("Usage: run <table_id> <message>")
            sys.exit(1)
        table_id = sys.argv[2]
        message = " ".join(sys.argv[3:])
        result = run(message, table_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "query":
        if len(sys.argv) < 4:
            print("Usage: query <table_id> <condition>")
            sys.exit(1)
        table_id = sys.argv[2]
        condition = " ".join(sys.argv[3:])
        result = query(condition, table_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "modify":
        if len(sys.argv) < 5:
            print("Usage: modify <table_id> <item_id> <message>")
            sys.exit(1)
        table_id = sys.argv[2]
        item_id = sys.argv[3]
        message = " ".join(sys.argv[4:])
        result = modify(item_id, message, table_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "log":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        print(json.dumps(json.loads(line), ensure_ascii=False, indent=2))
                    except:
                        pass

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
