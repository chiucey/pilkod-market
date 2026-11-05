#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成模块 - 投研报告生成和预警监控
已修复: generate_report 正确填充 content 字段
"""

from __future__ import annotations

import json
import uuid
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import defaultdict
import sys as _sys
import os as _os

_SCRIPT_DIR = _os.path.dirname(_os.path.abspath(__file__))
_SKILLS_ROOT = _os.path.dirname(_os.path.dirname(_SCRIPT_DIR))
_sys.path.insert(0, _os.path.join(_SKILLS_ROOT, 'stock-analyzer', 'scripts'))
_sys.path.insert(0, _os.path.join(_SKILLS_ROOT, 'risk-manager', 'scripts'))
_sys.path.insert(0, _os.path.join(_SKILLS_ROOT, 'market-data-fetcher', 'scripts'))

# 顶层函数导入（用于章节生成）
_HAS_DATA = False
try:
    from technical_analysis import compute_indicators, detect_patterns, detect_anomalies
    from fundamental_analysis import analyze_fundamentals, screen_stocks
    from risk_management import assess_risk, forecast_price
    from market_data import get_realtime_quotes, get_valuation
    _HAS_DATA = True
except Exception:
    pass


# ═══════════════════════════════════════════════════════
#  报告模板定义
# ═══════════════════════════════════════════════════════

TEMPLATES: Dict = {
    "stock_deep_dive": {
        "name": "深度投研报告",
        "sections": ["overview", "fundamentals", "technical", "risk", "recommendation"],
        "description": "完整的股票投研分析报告"
    },
    "technical_only": {
        "name": "技术分析报告",
        "sections": ["overview", "technical"],
        "description": "仅包含技术分析"
    },
    "fundamental_only": {
        "name": "基本面分析报告",
        "sections": ["overview", "fundamentals"],
        "description": "仅包含基本面分析"
    },
    "quick_scan": {
        "name": "快速扫描",
        "sections": ["overview"],
        "description": "仅市场概览"
    }
}


# ═══════════════════════════════════════════════════════
#  报告生成器
# ═══════════════════════════════════════════════════════

class ReportGenerator:
    """投研报告生成器"""

    TEMPLATES = TEMPLATES

    def __init__(self) -> None:
        self.report_counter = 0
        self.reports: Dict = {}

    def _generate_report_id(self) -> str:
        sid = self.report_counter + 1
        self.report_counter = sid
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        return "RPT-" + ts + "-" + str(sid).zfill(4)

    # ── 概览章节 ──
    def generate_overview_section(self, stocks: List[str]) -> Dict:
        section: Dict = {"content": "", "type": "overview"}
        parts: List[str] = []
        parts.append("## 一、市场概览\n")
        parts.append("**报告生成时间**: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        parts.append("**分析标的**: " + ", ".join(stocks) + "\n\n")

        if _HAS_DATA:
            try:
                rt = get_realtime_quotes(stocks)
                if rt and rt.get("data"):
                    parts.append("### 个股行情\n\n")
                    parts.append("| 股票代码 | 名称 | 当前价 | 涨跌幅 | 成交量 |\n")
                    parts.append("|---------|------|-------|-------|--------|\n")
                    for sym, d in rt["data"].items():
                        nm = d.get("name", sym)
                        px = d.get("close", 0)
                        pct = d.get("change_pct", 0)
                        vol = d.get("volume", 0)
                        parts.append("| " + str(sym) + " | " + str(nm) + " | " + str(round(px, 2)) + " | " + ("+" if pct >= 0 else "") + str(round(pct, 2)) + "% | " + str(vol) + " |\n")
                    parts.append("\n")
            except Exception:
                parts.append("（行情数据获取失败）\n\n")
        else:
            parts.append("（数据模块未加载，使用模拟数据）\n\n")

        section["content"] = "".join(parts)
        return section

    # ── 基本面章节 ──
    def generate_fundamentals_section(self, symbol: str) -> Dict:
        section: Dict = {"content": "", "type": "fundamentals"}
        parts: List[str] = []
        parts.append("## 二、基本面分析 — " + symbol + "\n\n")
        if _HAS_DATA:
            try:
                val = get_valuation(symbol)
                if val:
                    parts.append("### 估值指标\n\n")
                    parts.append("- **市盈率(TTM)**: " + str(round(val.get("pe_ttm", 0), 2)) + "\n")
                    parts.append("- **市净率**: " + str(round(val.get("pb", 0), 2)) + "\n")
                    parts.append("- **市值(亿元)**: " + str(round(val.get("market_cap", 0), 2)) + "\n")
                    parts.append("- **股息率**: " + str(round(val.get("dividend_yield", 0), 2)) + "%\n\n")
            except Exception:
                parts.append("（估值数据获取失败）\n\n")
        section["content"] = "".join(parts)
        return section

    # ── 技术面章节 ──
    def generate_technical_section(self, symbol: str) -> Dict:
        section: Dict = {"content": "", "type": "technical"}
        section["content"] = "## 三、技术分析 — " + symbol + "\n\n（详细技术指标见股票分析器模块）\n\n"
        return section

    # ── 风险章节 ──
    def generate_risk_section(self, stocks: List[str]) -> Dict:
        section: Dict = {"content": "", "type": "risk"}
        parts: List[str] = ["## 四、风险评估\n\n"]
        if _HAS_DATA:
            try:
                risk = assess_risk({s: {"weight": 1.0/len(stocks), "returns": []} for s in stocks})
                if risk:
                    vr = risk.get("var_95", risk.get("var", 0))
                    md = risk.get("max_drawdown", 0)
                    sp = risk.get("sharpe_ratio", 0)
                    parts.append("- **VaR(95%)**: " + str(round(float(vr), 4)) + "\n")
                    parts.append("- **最大回撤**: " + str(round(float(md), 4)) + "\n")
                    parts.append("- **夏普比率**: " + str(round(float(sp), 4)) + "\n\n")
            except Exception:
                parts.append("（风险数据获取失败）\n\n")
        section["content"] = "".join(parts)
        return section

    # ── 投资建议章节 ──
    def generate_recommendation_section(self, stocks: List[str]) -> Dict:
        section: Dict = {"content": "", "type": "recommendation"}
        parts: List[str] = ["## 五、投资建议\n\n"]
        parts.append("- **标的数量**: " + str(len(stocks)) + " 只\n")
        parts.append("- **综合评级**: 参考各章节分析\n")
        parts.append("- ⚠️ 免责声明：本报告仅供参考，不构成投资建议\n\n")
        section["content"] = "".join(parts)
        return section

    # ═══════════════════════════════════════════════
    #  核心：generate_report（已修复）
    # ═══════════════════════════════════════════════
    def generate_report(self,
                       title: str,
                       stocks: List[str],
                       sections: List[str] = None,
                       template: str = "stock_deep_dive",
                       output_format: str = "markdown") -> Dict:
        # ── 构建骨架 ──
        report_id = self._generate_report_id()
        result: Dict = {
            "code": 0,
            "message": "success",
            "content": "",   # ← 已修复：将在下方填充
            "data": {
                "report_id": report_id,
                "title": title,
                "generated_at": datetime.now().isoformat(),
                "sections": {},
                "metadata": {
                    "stocks_analyzed": stocks,
                    "template": template,
                    "output_format": output_format
                }
            }
        }

        # ── 确定章节列表 ──
        if sections is None:
            tpl = TEMPLATES.get(template)
            if tpl and isinstance(tpl, dict):
                sections = tpl.get("sections", ["overview", "recommendation"])
            else:
                sections = ["overview", "recommendation"]

        # ── 生成各章节 ──
        generated_sections: Dict = {}
        section_texts: List[str] = []

        for sec_name in sections:
            try:
                if sec_name == "overview":
                    sec = self.generate_overview_section(stocks)
                elif sec_name == "fundamentals":
                    sec = self.generate_fundamentals_section(stocks[0]) if len(stocks) >= 1 else {}
                elif sec_name == "technical":
                    sec = self.generate_technical_section(stocks[0]) if len(stocks) >= 1 else {}
                elif sec_name == "risk":
                    sec = self.generate_risk_section(stocks)
                elif sec_name == "recommendation":
                    sec = self.generate_recommendation_section(stocks)
                else:
                    sec = {}
                generated_sections[sec_name] = sec

                # 收集 markdown 文本
                if isinstance(sec, dict) and sec.get("content"):
                    section_texts.append(sec["content"])
                elif isinstance(sec, dict):
                    txt_parts = ["## " + sec_name.replace("_", " ").title(), ""]
                    for k, v in sec.items():
                        if v not in (None, "", {}, []):
                            txt_parts.append("- **" + str(k) + "**: " + str(v))
                    section_texts.append("\n".join(txt_parts))
            except Exception as exc:
                generated_sections[sec_name] = {"error": str(exc)}

        result["data"]["sections"] = generated_sections

        # ── 修复：填充 content 字段 ──
        if output_format == "markdown":
            md_parts: List[str] = [
                "# " + title,
                "",
                "**生成时间**: " + datetime.now().strftime("%Y-%m-%d %H:%M"),
                "**分析标的**: " + ", ".join(stocks),
                ""
            ]
            for txt in section_texts:
                if txt:
                    md_parts.append(txt)
                    md_parts.append("")
            result["content"] = "\n".join(md_parts)

        elif output_format == "json":
            data_str = json.dumps(result["data"], ensure_ascii=False, indent=2)
            result["content"] = data_str

        else:
            result["content"] = "\n\n".join(section_texts)

        # 保存到内存
        self.reports[report_id] = result
        return result

    def save(self, path: str, report: Dict = None) -> str:
        if report is None:
            return ""
        content = report.get("content", "")
        if not content:
            sections = report.get("data", {}).get("sections", {})
            lines = [report.get("data", {}).get("title", "报告"), ""]
            for sec_data in sections.values():
                if isinstance(sec_data, dict) and sec_data.get("content"):
                    lines.append(sec_data["content"])
            content = "\n".join(lines)
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            return path
        except Exception:
            return ""


# ═══════════════════════════════════════════════════════
#  预警管理器
# ═══════════════════════════════════════════════════════

class AlertManager:
    def __init__(self) -> None:
        self.alerts: Dict = {}
        self.alert_id_counter = 0

    def _generate_alert_id(self) -> str:
        self.alert_id_counter += 1
        ds = datetime.now().strftime("%Y%m%d")
        return "ALERT-" + ds + "-" + str(self.alert_id_counter).zfill(3)

    def set_alert(self,
                  symbol: str,
                  conditions: List[Dict],
                  alert_name: str = None,
                  notification_channels: List[str] = None) -> Dict:
        aid = self._generate_alert_id()
        alert: Dict = {
            "alert_id": aid,
            "name": alert_name or (symbol + "预警"),
            "symbol": symbol,
            "conditions": conditions,
            "notification_channels": notification_channels or ["push"],
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "last_triggered": None,
            "trigger_count": 0
        }
        self.alerts[aid] = alert
        return alert

    def get_alerts(self, status: str = None, symbol: str = None) -> List[Dict]:
        results: List[Dict] = []
        for al in self.alerts.values():
            if status and al.get("status") != status:
                continue
            if symbol and al.get("symbol") != symbol:
                continue
            results.append(al.copy())
        return results

    def delete_alert(self, alert_id: str) -> bool:
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            return True
        return False


# ═══════════════════════════════════════════════════════
#  顶层便捷函数
# ═══════════════════════════════════════════════════════

_alert_manager_global: Optional[AlertManager] = None

def generate_report(title: str,
                   stocks: List[str],
                   sections: List[str] = None,
                   template: str = "stock_deep_dive",
                   output_format: str = "markdown") -> Dict:
    return ReportGenerator().generate_report(title, stocks, sections, template, output_format)

def set_alert(symbol: str,
              conditions: List[Dict],
              alert_name: str = None,
              notification_channels: List[str] = None) -> Dict:
    global _alert_manager_global
    if _alert_manager_global is None:
        _alert_manager_global = AlertManager()
    return _alert_manager_global.set_alert(symbol, conditions, alert_name, notification_channels)

def get_alerts(status: str = None, symbol: str = None) -> List[Dict]:
    global _alert_manager_global
    if _alert_manager_global is None:
        _alert_manager_global = AlertManager()
    return _alert_manager_global.get_alerts(status, symbol)

def delete_alert(alert_id: str) -> bool:
    global _alert_manager_global
    if _alert_manager_global is None:
        _alert_manager_global = AlertManager()
    return _alert_manager_global.delete_alert(alert_id)
