"""自动归档核心流程（含大模型分类、重试与本地降级）。"""

import json
import os
import re
import shutil
import time
from datetime import datetime

from openai import OpenAI

import config
from category_paths import archive_target_directory, fallback_topic_by_category
from db_manager import ensure_db, insert_file_record
from file_parser import extract_text
from index_manager import ensure_index, index_document
from tag_generator import generate_tags

# 规范文件名主体过长时截断，避免超出系统限制。
_MAX_FILENAME_STEM = 120


CLASSIFICATION_TREE = """
【分类体系】
A类_企业基础信息库：
A01_组织架构（本部部门设置与职责、所属企业名录、分支机构清单）
A02_基础画像（企业简介、宣传册、信用评级报告）
B类_财务与经营动态库：
B01_财务快报与决算（年度财务决算审计报告、财务报表）
B02_经营分析报告（主业经营情况报告、对标世界一流分析报告）
B03_预算与投资（年度投资计划、全面预算报告、重大项目库）
B04_考核分配（中长期激励方案、股权激励、岗位分红）
C类_战略规划与改革重组库：
C01_五年规划（十四五/十五五发展规划纲要、专项子规划、中期评估报告）
C02_专项改革方案（国企改革三年行动/深化提升行动实施方案与台账）
C03_重组整合与压减（战略性重组与专业化整合方案、管理层级压减、僵尸企业处置）
C04_科技创新（创新平台认定文件、数字化转型规划与评估）
D类_项目与投资监管库：
D01_固定资产股权投资项目（项目可研报告、专家评审意见、项目后评价报告）
D02_基金业务（基金年度运营报告、托管报告）
E类_内控合规与监督库：
E01_法治合规（合规管理体系建设认证文件、重大法律纠纷案件台账与简报）
E02_社会责任与ESG（年度社会责任报告/ESG报告、乡村振兴帮扶报告）
F类_国资监管政策法规库：
F01_国务院国资委规章（投资管理、产权管理、财务监管、考核分配、改革改组、监督追责）
F02_省国资委规范性文件（按发文年份+文号归档）
F03_废止失效库
"""


def _normalize_metadata(raw: dict, file_name: str) -> dict:
    """校验并修正模型输出，保证字段完整且格式稳定。"""
    today = datetime.now().strftime("%Y%m%d")
    stem = os.path.splitext(file_name)[0]
    subject_default = re.sub(r"\s+", "", stem)[:15] or "未命名主题"

    category1 = str(raw.get("category1", "")).strip().upper()
    if category1 not in {"A", "B", "C", "D", "E", "F"}:
        category1 = "F"

    category2 = str(raw.get("category2", "")).strip().upper()
    if not re.fullmatch(r"[A-F]\d{2}", category2):
        category2 = f"{category1}01"

    file_date = re.sub(r"\D", "", str(raw.get("file_date", "")))[:8]
    if len(file_date) != 8:
        file_date = today

    company = str(raw.get("company", "")).strip()
    version = str(raw.get("version", "")).strip()
    subject = str(raw.get("subject", "")).strip()[:15] or subject_default

    return {
        "category1": category1,
        "category2": category2,
        "file_date": file_date,
        "company": company,
        "version": version,
        "subject": subject,
    }


def _extract_json_object(text: str) -> dict:
    """从模型返回文本中提取 JSON 对象。"""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if not match:
            raise
        return json.loads(match.group(0))


def _fallback_classification(content: str, filename: str) -> dict:
    """本地关键词兜底分类，保证流程不中断。"""
    source = f"{filename} {content[:2000]}"
    today = datetime.now().strftime("%Y%m%d")

    category1, category2 = "F", "F01"
    if any(k in source for k in ["规划", "十五五", "十四五", "改革"]):
        category1, category2 = "C", "C01"
    elif any(k in source for k in ["财务", "决算", "预算", "经营"]):
        category1, category2 = "B", "B01"
    elif any(k in source for k in ["项目", "可研", "投资", "基金"]):
        category1, category2 = "D", "D01"
    elif any(k in source for k in ["合规", "法治", "ESG", "责任"]):
        category1, category2 = "E", "E01"
    elif any(k in source for k in ["组织架构", "企业简介", "名录"]):
        category1, category2 = "A", "A01"

    version = ""
    for k in ["正式稿", "报批稿", "征求意见稿", "初稿"]:
        if k in source:
            version = k
            break

    subject = re.sub(r"\s+", "", os.path.splitext(filename)[0])[:15] or "未命名主题"
    return {
        "category1": category1,
        "category2": category2,
        "file_date": today,
        "company": "",
        "version": version,
        "subject": subject,
    }


def call_llm_for_classification(content: str, filename: str) -> dict:
    """调用国内 OpenAI 兼容模型提取元数据，失败则自动降级。"""
    if not config.AI_API_KEY:
        print("[WARN] 未配置 AI_API_KEY，降级为本地规则分类。")
        return _fallback_classification(content, filename)

    prompt = f"""你是一个国资系统文档分类专家。请根据以下文件内容和文件名，判断该文件应归档到哪个分类，并提取相关元数据。
{CLASSIFICATION_TREE}

【文件名】
{filename}

【文件内容（前2000字）】
{(content or '')[:2000]}

【输出要求】
请严格返回以下JSON格式，不要添加任何额外说明：
{{
  "category1": "C",
  "category2": "C01",
  "file_date": "20260320",
  "company": "机场集团",
  "version": "正式稿",
  "subject": "十五五发展规划纲要"
}}
"""

    client = OpenAI(
        api_key=config.AI_API_KEY,
        base_url=config.AI_BASE_URL,
        timeout=config.AI_TIMEOUT,
    )

    for retry in range(config.AI_MAX_RETRIES):
        try:
            print(f"[INFO] 正在调用模型 API（{config.AI_MODEL}）...")
            resp = client.chat.completions.create(
                model=config.AI_MODEL,
                messages=[
                    {"role": "system", "content": "你是严谨的文档分类助手，只输出JSON。"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=config.AI_MAX_TOKENS,
                temperature=0.2,
            )
            text = (resp.choices[0].message.content or "").strip()
            parsed = _extract_json_object(text)
            return _normalize_metadata(parsed, filename)
        except Exception as exc:  # noqa: BLE001
            print(
                f"[WARN] API 调用失败，正在重试({retry + 1}/{config.AI_MAX_RETRIES})... 错误: {exc}"
            )
            time.sleep(1.2)

    print("[WARN] 模型多次调用失败，降级为本地规则分类。")
    return _fallback_classification(content, filename)


def _sanitize_filename_part(s: str) -> str:
    """去除 Windows 文件名非法字符与多余空白。"""
    s = (s or "").strip()
    s = re.sub(r'[\\/:*?"<>|]', "_", s)
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _strip_leading_number_prefix(text: str) -> str:
    """移除序号前缀，如 1. / 7、 / （三）等。"""
    t = (text or "").strip()
    t = re.sub(
        r"^[\(\[（【]?\s*[0-9一二三四五六七八九十]+\s*[\)\]）】\.、\-_:：]?\s*",
        "",
        t,
    )
    return t.strip()


def _normalize_company(company: str) -> str:
    """清洗单位名称：去序号、去修饰词；空值保持为空字符串。"""
    value = _strip_leading_number_prefix(company)
    value = value.replace("\n", "").replace("\r", "")
    value = value.replace("“", "").replace("”", "").replace("'", "").replace('"', "")
    value = re.sub(r"^\s*(省|全省|市|全市|本省|本市)\s*", "", value)
    value = re.sub(r"(有限责任公司|股份有限公司|有限公司|总公司)$", "", value)
    value = re.sub(r"(文件|材料|报告|方案|规划|附件)$", "", value)
    value = value.strip(" _-")

    # 若包含“集团/公司”等组织关键词，优先抽取最靠近主体的一段。
    if "集团" in value:
        value = value[: value.index("集团") + 2]
    elif "公司" in value and len(value) > 2:
        value = value[: value.index("公司") + 2]

    value = _sanitize_filename_part(value)
    return value


def _normalize_subject(subject: str, category1: str, category2: str) -> str:
    """清洗主题并在不清晰时回退到二级分类默认主题。"""
    value = _strip_leading_number_prefix(subject or "")
    value = value.replace("\n", " ").replace("\r", " ")
    value = value.replace("“", "").replace("”", "").replace("'", "").replace('"', "")
    value = _sanitize_filename_part(value)
    bad_tokens = {"", "未命名主题", "文档", "材料", "附件", "报告", "文件"}
    if value in bad_tokens or len(value) < 4:
        value = fallback_topic_by_category(category1, category2)
    return _sanitize_filename_part(value)


def _normalize_version(version: str) -> str:
    """清洗版本字段，允许为空。"""
    value = _strip_leading_number_prefix(version or "")
    return _sanitize_filename_part(value)


def _build_standard_filename(metadata: dict, ext: str) -> str:
    """按规范生成 {YYYYMMDD}_{单位}_{主题}_{版本}.扩展名。"""
    file_date = re.sub(r"\D", "", str(metadata.get("file_date", "")))[:8]
    if len(file_date) != 8:
        file_date = datetime.now().strftime("%Y%m%d")
    category1 = str(metadata.get("category1", "")).strip().upper()
    category2 = str(metadata.get("category2", "")).strip().upper()
    company = _normalize_company(str(metadata.get("company", "")))
    subject = _normalize_subject(str(metadata.get("subject", "")), category1, category2)
    version = _normalize_version(str(metadata.get("version", "")))
    parts: list[str] = [file_date, company, subject, version]
    stem = "_".join(parts)
    if len(stem) > _MAX_FILENAME_STEM:
        stem = stem[:_MAX_FILENAME_STEM]
    e = ext.lower() if ext else ""
    return f"{stem}{e}"


def _file_modified_date(file_path: str) -> str:
    """返回文件最后修改日期（YYYYMMDD）。"""
    try:
        ts = os.path.getmtime(file_path)
        return datetime.fromtimestamp(ts).strftime("%Y%m%d")
    except OSError:
        return datetime.now().strftime("%Y%m%d")


def _ensure_unique_destination(path: str) -> str:
    """目标已存在时追加时间戳，避免覆盖。"""
    if not os.path.exists(path):
        return path
    stem, ext = os.path.splitext(path)
    ts = time.strftime("%Y%m%d%H%M%S")
    candidate = f"{stem}_{ts}{ext}"
    n = 1
    while os.path.exists(candidate):
        candidate = f"{stem}_{ts}_{n}{ext}"
        n += 1
    return candidate


def process_file(file_path: str) -> bool:
    """处理单个文件：提取文本、模型分类、打标签、入库、索引。

    返回 True 表示入库与索引等步骤全部成功；失败时返回 False（源文件应保留，由调用方决定是否清理）。
    """
    if not os.path.exists(file_path):
        print(f"[INFO] 源文件不存在，跳过处理: {file_path}")
        return False

    try:
        ensure_db()
        ensure_index()

        original_name = os.path.basename(file_path)
        content_snippet = extract_text(file_path, max_chars=2000)
        metadata = call_llm_for_classification(content_snippet, original_name)
        # 文件日期以源文件“最后修改时间”为准，不使用归档处理时间。
        metadata["file_date"] = _file_modified_date(file_path)
        # 标签仅保留单位/年份/版本与内容关键词（不再包含分类代码标签）。
        tags = generate_tags(metadata=metadata, content=content_snippet)

        ext = os.path.splitext(original_name)[1]
        canonical_name = _build_standard_filename(metadata, ext)
        target_dir = archive_target_directory(
            config.SHARED_BASE_PATH, metadata["category1"], metadata["category2"]
        )
        os.makedirs(target_dir, exist_ok=True)
        dest_path = os.path.join(target_dir, canonical_name)
        dest_path = _ensure_unique_destination(dest_path)
        try:
            shutil.move(file_path, dest_path)
        except FileNotFoundError:
            # 监听重复事件下，文件可能已被上一轮处理移动到目标位置。
            if os.path.exists(dest_path):
                print(f"[INFO] 源文件已不存在，沿用已归档结果: {dest_path}")
            else:
                print(f"[INFO] 源文件不存在且目标不存在，跳过本次处理: {file_path}")
                return False
        except OSError as exc:
            print(f"[ERROR] 移动到归档目录失败: {file_path} -> {dest_path} | {exc}")
            return False

        record = {
            "file_name": os.path.basename(dest_path),
            "original_name": original_name,
            "file_path": dest_path,
            "category1": metadata["category1"],
            "category2": metadata["category2"],
            "file_date": metadata["file_date"],
            "company": metadata["company"],
            "version": metadata["version"],
            "subject": metadata["subject"],
            "tags": ",".join(tags),
            "content_snippet": content_snippet,
        }
        row_id = insert_file_record(record)
        index_document(str(row_id), record["file_name"], record["content_snippet"], tags)

        if config.PROCESSED_DIR:
            os.makedirs(config.PROCESSED_DIR, exist_ok=True)
            backup_path = os.path.join(config.PROCESSED_DIR, os.path.basename(dest_path))
            backup_path = _ensure_unique_destination(backup_path)
            try:
                shutil.copy2(dest_path, backup_path)
                print(f"[INFO] 已额外备份到 PROCESSED_DIR: {backup_path}")
            except OSError as exc:
                print(f"[WARN] 复制到 PROCESSED_DIR 失败（归档文件已就位）: {exc}")

        print(f"[OK] 已归档: {dest_path}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] 自动归档失败: {file_path} | {exc}")
        return False


if __name__ == "__main__":
    print("请通过 watchdog_listener.py 触发处理，或在此文件中接入命令行参数。")

