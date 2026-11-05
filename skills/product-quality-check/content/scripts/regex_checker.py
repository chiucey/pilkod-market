#!/usr/bin/env python3
"""
regex_checker.py — 正则化核查模块
==================================
针对可 pattern 化的检查项，用正则表达式进行精确比对。

适用检查类型：
  1. 命名规范    — 文件名是否符合命名规则（产品名/版本号/日期等）
  2. 目录结构    — 文档章节编号、目录层级是否规范
  3. 存在性检查  — 关键章节/段落是否存在（标题+内容双重确认）
  4. 参数定义    — 参数名/类型/必填/说明是否完整
  5. URL/接口地址 — 请求地址是否符合规范格式
  6. 代码/命令   — 部署步骤中的命令是否包含具体指令
  7. 数量统计    — 用例数/参数数/功能点数是否符合要求
  8. 签字/公章   — 特定签章标识是否存在

每个检查类型对应一个 Checker 类，统一接口：
  check(text: str, context: dict) -> CheckResult
"""

import re
import os
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class CheckResult:
    """检查结果 dataclass"""
    result: str          # "pass" | "partial" | "fail" | "skip"
    score: float         # 得分（满分由调用者按权重计算）
    matched_texts: list  # 匹配到的文本片段（最多5条）
    reason: str          # 判定理由
    confidence: float = 1.0  # 置信度 0~1


# ============================================================================
# 基础检查器
# ============================================================================

class BaseChecker:
    """所有 Checker 的基类，提供通用方法"""

    def check(self, text: str, context: dict = None) -> CheckResult:
        raise NotImplementedError

    def _best_match(self, patterns: list, text: str, max_lines: int = 5) -> list:
        """返回匹配到的文本行（去重，最多max_lines条）"""
        matched = []
        seen = set()
        for pattern in patterns:
            for line in text.split('\n'):
                if pattern.search(line) and line.strip() not in seen:
                    seen.add(line.strip())
                    matched.append(line.strip())
                    if len(matched) >= max_lines:
                        return matched
        return matched

    def _match_count(self, pattern, text: str) -> int:
        """返回匹配次数"""
        return len(pattern.findall(text))


# ============================================================================
# 1. 文件命名规范检查器
# ============================================================================

class NamingChecker(BaseChecker):
    """
    检查文件名是否符合规范。
    context keys:
      required_keywords: list[str]   — 必须包含的关键词（如产品名）
      pattern: str                   — 额外正则要求（如 v\\d+\\.\\d+\\.\\d+）
      forbidden: list[str]           — 禁止出现的词（如 draft、草稿、v1.old）
    """

    def check(self, text: str, context: dict = None) -> CheckResult:
        ctx = context or {}
        required = ctx.get("required_keywords", [])
        extra_pattern = ctx.get("pattern", "")
        forbidden = ctx.get("forbidden", [])
        filename = ctx.get("filename", text.split('\n')[0] if text else "")

        matched_kw = []
        missing_kw = []
        for kw in required:
            if re.search(re.escape(kw), filename, re.IGNORECASE):
                matched_kw.append(kw)
            else:
                missing_kw.append(kw)

        matched_forbidden = [f for f in forbidden if f in filename]

        if matched_forbidden:
            return CheckResult(
                result="fail",
                score=0.0,
                matched_texts=[filename],
                reason=f"文件名含禁止词: {matched_forbidden}"
            )

        if missing_kw:
            return CheckResult(
                result="fail",
                score=0.0,
                matched_texts=[f"包含: {matched_kw}"],
                reason=f"文件名缺少必要关键词: {missing_kw}"
            )

        if extra_pattern:
            if not re.search(extra_pattern, filename):
                return CheckResult(
                    result="partial",
                    score=0.5,
                    matched_texts=[filename],
                    reason=f"文件名不符合附加格式要求"
                )

        if len(matched_kw) == len(required) and not matched_forbidden:
            return CheckResult(
                result="pass",
                score=1.0,
                matched_texts=[filename],
                reason=f"文件名规范，包含所有要求关键词"
            )

        return CheckResult(result="skip", score=0.0, matched_texts=[], reason="命名检查跳过")


# ============================================================================
# 2. 目录/章节结构检查器
# ============================================================================

class StructureChecker(BaseChecker):
    """
    检查文档章节编号和目录层级是否规范。
    context keys:
      required_sections: list[str]  — 必须存在的章节标题（精确匹配或关键词）
      section_pattern: str          — 章节编号正则（如 "第\\d+节"）
      min_depth: int                — 最小层级深度
    """

    SECTION_NUM_PATTERN = re.compile(r'^(\d+[.])+\d*\s+\S+')
    MARKDOWN_H_PATTERN  = re.compile(r'^(#{1,6})\s+(.+)$')

    def check(self, text: str, context: dict = None) -> CheckResult:
        ctx = context or {}
        required_sections = ctx.get("required_sections", [])
        section_nums = self.SECTION_NUM_PATTERN
        md_heads = self.MARKDOWN_H_PATTERN

        # 找所有章节标题行
        section_lines = []
        for line in text.split('\n'):
            s_match = section_nums.match(line.strip())
            m_match = md_heads.match(line.strip())
            if s_match:
                section_lines.append(line.strip())
            elif m_match:
                section_lines.append(line.strip())

        found_sections = []
        missing_sections = []
        for req in required_sections:
            req_lower = req.lower()
            found = any(req_lower in sec.lower() for sec in section_lines)
            if found:
                found_sections.append(req)
            else:
                missing_sections.append(req)

        total = len(required_sections)
        found_count = len(found_sections)

        if found_count == 0:
            result, score = "fail", 0.0
        elif found_count == total:
            result, score = "pass", 1.0
        else:
            result, score = "partial", found_count / total * 0.7

        return CheckResult(
            result=result,
            score=score,
            matched_texts=found_sections[:5],
            reason=f"找到 {found_count}/{total} 个必要章节，缺失: {missing_sections[:3]}",
            confidence=0.9
        )


# ============================================================================
# 3. 存在性检查器（关键内容是否存在）
# ============================================================================

class ExistenceChecker(BaseChecker):
    """
    检查某项内容是否在文档中存在（关键词双重确认：标题+正文）。
    context keys:
      keywords: list[str]          — 必须存在的关键词
      must_have_title: bool        — 是否要求有关键词作为独立标题行
      min_occurrences: int          — 最少出现次数（默认1）
    """

    def check(self, text: str, context: dict = None) -> CheckResult:
        ctx = context or {}
        keywords = ctx.get("keywords", [])
        must_have_title = ctx.get("must_have_title", False)
        min_occ = ctx.get("min_occurrences", 1)

        if not keywords:
            return CheckResult(result="skip", score=0.0, matched_texts=[], reason="无关键词")

        found_kw = {}
        for kw in keywords:
            escaped = re.escape(kw)
            # 找所有包含该关键词的行
            matches = [l.strip() for l in text.split('\n') if re.search(escaped, l, re.IGNORECASE)]
            if must_have_title:
                # 进一步要求关键词出现在标题行（行首无缩进）
                title_matches = [l for l in matches if re.match(r'^\S', l)]
                found_kw[kw] = len(title_matches) if title_matches else 0
            else:
                found_kw[kw] = len(matches)

        # 全部找到
        all_pass = all(count >= min_occ for count in found_kw.values())
        any_found = any(count > 0 for count in found_kw.values())
        partial_ratio = sum(1 for c in found_kw.values() if c > 0) / len(found_kw)

        if all_pass:
            result, score = "pass", 1.0
        elif any_found:
            result, score = "partial", partial_ratio * 0.7
        else:
            result, score = "fail", 0.0

        matched = []
        for kw, count in found_kw.items():
            if count > 0:
                lines = [l for l in text.split('\n') if re.search(re.escape(kw), l, re.IGNORECASE)]
                matched.append(f"{kw}(×{count}): {lines[0][:50]}" if lines else kw)

        return CheckResult(
            result=result,
            score=score,
            matched_texts=matched[:5],
            reason=f"关键词出现情况: {dict((k,v) for k,v in found_kw.items())}",
            confidence=0.85
        )


# ============================================================================
# 4. 参数定义完整性检查器
# ============================================================================

class ParameterChecker(BaseChecker):
    """
    检查参数说明表是否完整（名称/类型/必填/说明四要素）。
    context keys:
      param_names: list[str]        — 必须包含的参数名
      required_fields: list[str]    — 必须有的列/字段（如类型、必填、说明）
    """

    PARAM_TABLE_ROW = re.compile(
        r'(?:\||\t)\s*(\S+)\s*(?:\||\t)\s*(\S+)\s*(?:\||\t)',
        re.IGNORECASE
    )

    def check(self, text: str, context: dict = None) -> CheckResult:
        ctx = context or {}
        required_params = ctx.get("param_names", [])
        required_fields = ctx.get("required_fields", ["类型", "必填", "说明", "描述"])

        # 找参数表区域（包含"参数"关键词的表格区域）
        param_section = self._extract_section(text, ["参数", "parameter", "field"], window=200)
        if not param_section:
            return CheckResult(
                result="fail", score=0.0, matched_texts=[],
                reason="未找到参数定义区域"
            )

        # 检查必需字段是否出现
        found_fields = [f for f in required_fields if re.search(re.escape(f), param_section, re.IGNORECASE)]

        # 检查必需参数名
        found_params = []
        for pname in required_params:
            if re.search(re.escape(pname), param_section, re.IGNORECASE):
                found_params.append(pname)

        total_params = len(required_params)
        found_param_count = len(found_params)
        field_ratio = len(found_fields) / len(required_fields) if required_fields else 1.0

        if found_param_count == 0 and len(found_fields) == 0:
            result, score = "fail", 0.0
        elif found_param_count == total_params and field_ratio >= 0.75:
            result, score = "pass", 1.0
        elif found_param_count > 0 or field_ratio > 0:
            score = (found_param_count / total_params * 0.6 + field_ratio * 0.4) if total_params else field_ratio * 0.7
            result = "partial"
        else:
            result, score = "fail", 0.0

        return CheckResult(
            result=result,
            score=score,
            matched_texts=[f"{p}" for p in found_params[:5]],
            reason=f"找到 {found_param_count}/{total_params} 个参数，{len(found_fields)}/{len(required_fields)} 个必需字段",
            confidence=0.8
        )

    def _extract_section(self, text: str, keywords: list, window: int = 200) -> str:
        """提取包含关键词的文本区域"""
        sections = []
        for kw in keywords:
            for i, line in enumerate(text.split('\n')):
                if re.search(re.escape(kw), line, re.IGNORECASE):
                    start = max(0, i * 80 - window)
                    end = min(len(text), i * 80 + window)
                    sections.append(text[start:end])
        return ' '.join(sections[:3])


# ============================================================================
# 5. URL/接口地址检查器
# ============================================================================

class URLChecker(BaseChecker):
    """
    检查 URL/接口地址是否存在且格式正确。
    context keys:
      required_urls: list[str]      — 必须存在的 URL（精确或关键词）
      url_pattern: str             — URL正则（如 https?://...）
      require_version: bool         — 是否要求 URL 包含版本号
    """

    URL_RE = re.compile(r'https?://[^\s\'"<>\\|]+', re.IGNORECASE)

    def check(self, text: str, context: dict = None) -> CheckResult:
        ctx = context or {}
        required = ctx.get("required_urls", [])
        custom_pattern = ctx.get("url_pattern", "")
        require_ver = ctx.get("require_version", False)

        urls = self.URL_RE.findall(text)

        found_required = []
        missing_required = []
        for req in required:
            found = any(re.search(re.escape(req), u, re.IGNORECASE) for u in urls)
            if found:
                found_required.append(req)
            else:
                missing_required.append(req)

        valid_urls = [u for u in urls if self._is_valid_url(u, require_ver)]

        if missing_required:
            result, score = "fail", 0.0
        elif len(valid_urls) >= len(required):
            result, score = "pass", 1.0
        else:
            result, score = "partial", 0.6

        return CheckResult(
            result=result,
            score=score,
            matched_texts=valid_urls[:5],
            reason=f"找到 {len(valid_urls)} 个有效URL，{len(found_required)}/{len(required)} 个必需URL"
        )

    def _is_valid_url(self, url: str, require_version: bool) -> bool:
        if not url.startswith(('http://', 'https://')):
            return False
        if require_version and not re.search(r'v\d+|/api/\d+', url):
            return False
        return True


# ============================================================================
# 6. 命令/步骤完整性检查器
# ============================================================================

class CommandChecker(BaseChecker):
    """
    检查步骤命令是否存在且可执行。
    context keys:
      expected_commands: list[str]  — 期望出现的命令（关键词）
      command_prefixes: list[str]   — 命令前缀（如 cd, docker, kubectl, mv）
      min_steps: int                — 最少步骤数
    """

    STEP_RE = re.compile(r'^\d+[.、]\s+\S+', re.MULTILINE)
    CODE_BLOCK_RE = re.compile(r'`([^`]+)`|```\n?([\s\S]+?)\n?```')

    def check(self, text: str, context: dict = None) -> CheckResult:
        ctx = context or {}
        expected_cmds = ctx.get("expected_commands", [])
        prefixes = ctx.get("command_prefixes", ["cd ", "docker", "kubectl", "pip", "npm", "make", "./", "bash", "sh "])
        min_steps = ctx.get("min_steps", 1)

        # 提取代码块和带编号的步骤行
        code_lines = []
        for m in self.CODE_BLOCK_RE.finditer(text):
            code_lines.append(m.group(1) or m.group(2))

        step_lines = self.STEP_RE.findall(text)

        # 统计以命令前缀开头的实际命令
        actual_cmds = []
        for block in code_lines:
            for line in block.split('\n'):
                line = line.strip()
                for prefix in prefixes:
                    if line.startswith(prefix):
                        actual_cmds.append(line)
                        break

        # 检查期望命令关键词
        found_cmds = []
        missing_cmds = []
        for exp in expected_cmds:
            exp_esc = re.escape(exp)
            found = any(re.search(exp_esc, cmd, re.IGNORECASE) for cmd in actual_cmds)
            if found:
                found_cmds.append(exp)
            else:
                missing_cmds.append(exp)

        step_count = len(step_lines)
        cmd_count = len(actual_cmds)

        if step_count < min_steps and cmd_count == 0:
            return CheckResult(result="fail", score=0.0, matched_texts=[],
                               reason=f"未找到任何步骤或命令")
        if missing_cmds:
            return CheckResult(result="partial", score=0.6, matched_texts=actual_cmds[:3],
                               reason=f"缺少期望命令: {missing_cmds[:2]}")
        return CheckResult(result="pass", score=1.0, matched_texts=actual_cmds[:5],
                          reason=f"找到 {step_count} 步、{cmd_count} 条命令")


# ============================================================================
# 7. 数量统计检查器
# ============================================================================

class CountChecker(BaseChecker):
    """
    检查数量是否达到要求（用例数/功能点数/接口数等）。
    context keys:
      keyword: str                  — 数量描述的关键词（如 "测试用例"、"功能点"）
      min_count: int                — 最少数量
      count_pattern: str            — 数量提取正则（默认从文本中匹配数字+X的模式）
    """

    COUNT_RE = re.compile(r'(\d+)\s*(?:个|条|项|份|页|张|步|模块|接口|用例|功能|类)')

    def check(self, text: str, context: dict = None) -> CheckResult:
        ctx = context or {}
        kw = ctx.get("keyword", "")
        min_count = ctx.get("min_count", 1)
        custom_pattern = ctx.get("count_pattern", "")

        if custom_pattern:
            pattern = re.compile(custom_pattern)
        else:
            pattern = self.COUNT_RE

        # 搜索关键词附近的数量
        mentions = []
        for i, line in enumerate(text.split('\n')):
            if kw and not re.search(re.escape(kw), line, re.IGNORECASE):
                continue
            matches = pattern.findall(line)
            mentions.extend((int(m), line.strip()) for m in matches)

        if not mentions:
            return CheckResult(result="fail", score=0.0, matched_texts=[],
                              reason=f"未找到 '{kw}' 相关数量描述")

        # 取最大数量（通常是最完整的统计）
        max_count = max(m for m, _ in mentions if m > 0)
        best_line = next(line for m, line in mentions if m == max_count)

        if max_count >= min_count:
            result, score = "pass", 1.0
        elif max_count >= min_count * 0.5:
            result, score = "partial", max_count / min_count
        else:
            result, score = "fail", 0.0

        return CheckResult(
            result=result,
            score=score,
            matched_texts=[f"数量={max_count}: {best_line[:60]}"],
            reason=f"找到数量 {max_count}，要求最少 {min_count}"
        )


# ============================================================================
# 8. 签字/公章/版本标识检查器
# ============================================================================

class SignatureChecker(BaseChecker):
    """
    检查特定标识是否存在（签字、公章、版本号等）。
    context keys:
      types: list[str]             — 标识类型列表
      allow_fuzzy: bool            — 是否允许模糊匹配（默认False，严格模式）
    """

    SIGNATURE_PATTERNS = {
        "公章": re.compile(r'(公章|印章|印模|公司章)', re.IGNORECASE),
        "签字": re.compile(r'(签字|签名|签署)\s*[：:]\s*\S+|^\S+\s+签字', re.MULTILINE),
        "版本号": re.compile(r'(版本[号]?\s*[：:\s]*v?\d+[.]\d+|v\d+[.]\d+[.]\d+)', re.IGNORECASE),
        "日期": re.compile(r'(20\d{2}[-/年]\d{1,2}[-/月]\d{1,2}日?|\d{4}-\d{2}-\d{2})'),
        "审批": re.compile(r'(审批|审核|批准|approve|review)', re.IGNORECASE),
    }

    def check(self, text: str, context: dict = None) -> CheckResult:
        ctx = context or {}
        required_types = ctx.get("types", list(self.SIGNATURE_PATTERNS.keys()))

        found = []
        missing = []
        for t in required_types:
            pattern = self.SIGNATURE_PATTERNS.get(t, re.compile(re.escape(t), re.IGNORECASE))
            matches = pattern.findall(text)
            if matches:
                found.append(t)
            else:
                missing.append(t)

        total = len(required_types)
        found_count = len(found)

        if found_count == 0:
            result, score = "fail", 0.0
        elif found_count == total:
            result, score = "pass", 1.0
        else:
            result, score = "partial", found_count / total * 0.8

        return CheckResult(
            result=result,
            score=score,
            matched_texts=found,
            reason=f"找到 {found_count}/{total} 个必需标识，缺失: {missing}",
            confidence=0.9
        )


# ============================================================================
# 9. 跨文档一致性检查器（用于 Q5）
# ============================================================================

class CrossDocChecker(BaseChecker):
    """
    检查两个文档之间的对应关系是否一致。
    context keys:
      source_doc: str               — 源文档名
      target_doc: str               — 目标文档名
      source_keywords: list[str]    — 源文档关键词
      target_keywords: list[str]    — 目标文档关键词
      check_mode: "one-way" | "mutual"  — 单向对应 or 双向一致
    """

    def check(self, text: str, context: dict = None) -> CheckResult:
        # 注意：cross_doc_checker 需要同时访问两个文档的文本
        # 这里只处理单个文本，返回结构化信息供上层合并
        ctx = context or {}
        source_kw = ctx.get("source_keywords", [])
        target_kw = ctx.get("target_keywords", [])

        source_found = []
        target_found = []
        for kw in source_kw:
            for line in text.split('\n'):
                if re.search(re.escape(kw), line, re.IGNORECASE):
                    source_found.append(line.strip())

        for kw in target_kw:
            for line in text.split('\n'):
                if re.search(re.escape(kw), line, re.IGNORECASE):
                    target_found.append(line.strip())

        return CheckResult(
            result="skip",
            score=0.0,
            matched_texts={
                "source_matches": source_found[:5],
                "target_matches": target_found[:5],
                "note": "需调用 cross_doc_compare() 函数进行跨文档比对"
            },
            reason="跨文档检查需同时提供两个文档"
        )


def cross_doc_compare(source_text: str, target_text: str, context: dict) -> CheckResult:
    """
    比较两个文档之间的对应关系。
    context keys:
      source_label: str
      target_label: str
      source_keywords: list[str]
      target_keywords: list[str]
      match_threshold: float (0~1，默认0.7)
    """
    ctx = context or {}
    src_kw = ctx.get("source_keywords", [])
    tgt_kw = ctx.get("target_keywords", [])
    threshold = ctx.get("match_threshold", 0.7)

    # 提取两边的关键词匹配
    src_found = set()
    for kw in src_kw:
        for line in source_text.split('\n'):
            if re.search(re.escape(kw), line, re.IGNORECASE):
                src_found.add(kw)
                break

    tgt_found = set()
    for kw in tgt_kw:
        for line in target_text.split('\n'):
            if re.search(re.escape(kw), line, re.IGNORECASE):
                tgt_found.add(kw)
                break

    # 计算覆盖率
    src_coverage = len(src_found) / len(src_kw) if src_kw else 0
    tgt_coverage = len(tgt_found) / len(tgt_kw) if tgt_kw else 0
    avg_coverage = (src_coverage + tgt_coverage) / 2

    if avg_coverage >= threshold:
        result = "pass"
        score = avg_coverage
    elif avg_coverage >= 0.5:
        result = "partial"
        score = avg_coverage * 0.7
    else:
        result = "fail"
        score = avg_coverage * 0.4

    return CheckResult(
        result=result,
        score=score,
        matched_texts=[f"源端覆盖率={src_coverage:.0%}", f"目标端覆盖率={tgt_coverage:.0%}"],
        reason=f"源端 {len(src_found)}/{len(src_kw)}，目标端 {len(tgt_found)}/{len(tgt_kw)}，综合覆盖率={avg_coverage:.0%}",
        confidence=0.85
    )


# ============================================================================
# 主入口：运行全套 regex 检查
# ============================================================================

def run_regex_checks(check_item: dict, doc_text: str, doc_context: dict = None) -> CheckResult:
    """
    根据检查项类型，自动路由到对应的 Checker。
    这是 regex_checker.py 的主入口函数。

    check_item: parse_control_plan() 中的检查项（含 keywords, regex_friendly, name）
    doc_text:   文档纯文本
    doc_context: 额外上下文（如 filename、doc_type 等）
    """
    name = check_item.get("name", "")
    doc_context = doc_context or {}

    # 根据关键词自动选择 Checker
    if any(k in name for k in ["命名", "文件", "格式", "规范", "标准产品名"]):
        return NamingChecker().check(doc_text, {
            "required_keywords": check_item.get("keywords", []),
            "filename": doc_context.get("filename", ""),
            "forbidden": ["draft", "草稿", "旧版", "v1.old", "备份"]
        })

    if any(k in name for k in ["目录", "章节", "结构", "层级", "排版"]):
        return StructureChecker().check(doc_text, {
            "required_sections": check_item.get("keywords", []),
        })

    if any(k in name for k in ["包含", "涵盖", "提供", "具备", "有", "说明"]):
        # 存在性检查
        kw_list = check_item.get("keywords", [])
        if kw_list:
            return ExistenceChecker().check(doc_text, {
                "keywords": kw_list,
                "must_have_title": "标题" in name or "章节" in name
            })

    if any(k in name for k in ["参数", "字段", "类型", "必填", "说明"]):
        return ParameterChecker().check(doc_text, {
            "param_names": check_item.get("keywords", []),
            "required_fields": ["名称", "类型", "必填", "说明"]
        })

    if any(k in name for k in ["URL", "url", "请求地址", "接口地址", "endpoint"]):
        return URLChecker().check(doc_text, {
            "required_urls": check_item.get("keywords", []),
            "url_pattern": r'https?://[^\s\'"<>]+'
        })

    if any(k in name for k in ["步骤", "命令", "脚本", "部署", "回滚", "排查"]):
        return CommandChecker().check(doc_text, {
            "expected_commands": check_item.get("keywords", []),
            "min_steps": 1
        })

    if any(k in name for k in ["数量", "总数", "个", "项", "条", "份"]):
        return CountChecker().check(doc_text, {
            "keyword": check_item.get("keywords", [""])[0] if check_item.get("keywords") else "",
            "min_count": 1
        })

    if any(k in name for k in ["签字", "签名", "公章", "签章", "审批"]):
        sig_types = []
        if "公章" in name or "印" in name:
            sig_types.append("公章")
        if "签字" in name or "签名" in name:
            sig_types.append("签字")
        if "版本" in name:
            sig_types.append("版本号")
        return SignatureChecker().check(doc_text, {"types": sig_types})

    # 默认走 ExistenceChecker
    return ExistenceChecker().check(doc_text, {
        "keywords": check_item.get("keywords", []),
        "min_occurrences": 1
    })


if __name__ == "__main__":
    # 简单测试
    test_text = """
    产品名称：智能协同平台 V2.3.1
    版本号：v2.3.1
    研发单位：XX科技有限公司
    公章：[印模]
    签字：张三
    第1章 系统概述
    第1.1节 项目背景
    第2章 功能需求
    接口URL: https://api.example.com/v1/user
    请求方式: POST
    参数：userId (string, 必填), name (string, 选填)
    部署步骤：
    1. docker build -t app:v2.3.1 .
    2. docker run -d -p 8080:8080 app:v2.3.1
    测试用例总数：128条
    """
    from regex_checker import run_regex_checks

    test_item = {
        "name": "涵盖接口URL",
        "keywords": ["URL", "接口", "请求地址"],
        "regex_friendly": True
    }
    r = run_regex_checks(test_item, test_text)
    print(f"URL检查: {r.result} | {r.reason}")
