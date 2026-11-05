"""
财务报表勾稽校验 - 免API Key版
使用 MaxClaw 内置模型，无需外部 API Key
"""
import json, os, logging, re, time
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("financial-reconciliation")

# ── 勾稽校验标准科目 ──
STANDARD_FIN_ITEMS = {
    "资产负债表": ["资产合计","流动资产合计","非流动资产合计","负债合计",
                  "流动负债合计","非流动负债合计","股东权益合计","所有者权益合计",
                  "货币资金","未分配利润"],
    "利润表": ["营业收入","营业成本","营业利润","营业外收入","营业外支出",
               "利润总额","所得税费用","净利润总额"],
    "现金流量表": ["经营活动现金流量净额","投资活动现金流量净额",
                   "筹资活动现金流量净额","现金及现金等价物净增加额"]
}
DEFAULT_TOLERANCE = 0.001
LLM_MODEL = "deepseek-chat"  # 或 "gpt-4o" 根据平台配置


class FinancialReconciliationPlugin:

    def __init__(self):
        self.tolerance = DEFAULT_TOLERANCE
        self.multi_standard_fin_data: Dict[str, Dict] = {}
        self.all_table_names: List[str] = []

    def call_llm(self, prompt: str) -> str:
        """通过 OpenClaw invoke 调用内置 LLM"""
        try:
            from openclaw import invoke
            result = invoke(
                prompt=prompt,
                schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"}
                    },
                    "required": ["content"]
                }
            )
            return result.get("content", "")
        except ImportError:
            pass
        # 降级：使用 MaxClaw 平台 LLM API
        try:
            import urllib.request, urllib.parse
            api_key = os.getenv("MAXCLAW_API_KEY", "")
            if not api_key:
                # 尝试从平台环境获取
                api_key = os.getenv("OPENCLAW_API_KEY", "")

            url = "https://api.maxclaw.ai/v1/chat/completions"
            data = {
                "model": LLM_MODEL,
                "messages": [
                    {"role": "system", "content": "你是一名资深的勾稽校验专家，只返回JSON，不返回其他文字。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 8192,
                "temperature": 0.0
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
            return resp_data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            return ""

    def call_llm_standardize_data(self, md_content: str) -> Dict[str, Any]:
        """调用 LLM 标准化财务报表"""
        std_items_prompt = json.dumps(STANDARD_FIN_ITEMS, ensure_ascii=False, indent=2)
        prompt = f"""你是资深注册会计师，精通财务报表解析，严格按以下要求处理：

### 第一步：识别所有财务表
从Markdown内容中提取所有表格；精准识别报表类型（仅识别：资产负债表/利润表/现金流量表），同类型表按顺序编号。

### 第二步：标准化处理
科目统一为标准财务科目名称；列整合示例：{{"资产合计": {{"2025-06-30": 1000.00, "2025-09-30": 1200.00}}}}；金额转浮点型保留2位，空值填0.0。

### 第三步：输出格式
仅返回纯净JSON字符串：
{{
  "资产负债表1": {{"科目": {{"金额列名": 金额值}}}},
  "利润表1": {{"科目": {{"金额列名": 金额值}}}}
}}

### 参考标准科目
{std_items_prompt}

### 待处理内容
{md_content}
"""
        try:
            raw = self.call_llm(prompt)
            raw = raw.strip()
            # 清洗 markdown 代码块
            for marker in ["```json", "```", "“", "”", "‘", "’"]:
                raw = raw.replace(marker, '"' if marker in ['"'] else '')
            # 提取 JSON 对象
            m = re.search(r'\{[\s\S]*\}', raw)
            if m:
                data = json.loads(m.group())
                # 确保金额为浮点
                for tname, tdata in data.items():
                    for subj, cdata in list(tdata.items()):
                        for col, val in list(cdata.items()):
                            try:
                                data[tname][subj][col] = float(round(float(val), 2))
                            except:
                                data[tname][subj][col] = 0.0
                return data
        except Exception as e:
            logger.error(f"标准化失败: {e}")
        return {}

    def standardize_report_data(self, payload: dict) -> None:
        self.multi_standard_fin_data.clear()
        self.all_table_names = []
        content = payload.get("report_content", "")
        if not content:
            logger.warning("未获取到报表内容")
            return
        data = self.call_llm_standardize_data(content)
        self.multi_standard_fin_data = data
        self.all_table_names = list(data.keys())
        logger.info(f"识别到 {len(self.all_table_names)} 张报表")

    def execute_dynamic_check(self) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        if not self.multi_standard_fin_data:
            return results

        data_str = json.dumps(self.multi_standard_fin_data, ensure_ascii=False, indent=2)
        prompt = f"""你是资深注册会计师，执行全自动勾稽校验：

### 校验规则（容差={self.tolerance}）
- 资产负债表：资产合计=流动资产合计+非流动资产合计；负债合计=流动负债合计+非流动负债合计；资产合计=负债合计+所有者权益合计
- 利润表：利润总额=营业利润+营业外收入-营业外支出；净利润=利润总额-所得税费用
- 现金流量表：现金及现金等价物净增加额=经营活动现金流量净额+投资活动现金流量净额+筹资活动现金流量净额

### 输出要求
仅返回JSON数组，每项包含：table_name, check_type, check_name, check_amount_column, calc_value, actual_value, diff_value, is_pass。示例：
[
  {{"table_name":"资产负债表1","check_type":"表内校验","check_name":"资产合计=流动资产合计+非流动资产合计","check_amount_column":"2025-06-30","calc_value":700.00,"actual_value":700.00,"diff_value":0.00,"is_pass":true}}
]

### 待校验数据
{data_str}
"""
        try:
            raw = self.call_llm(prompt)
            raw = raw.strip()
            for marker in ["```json", "```"]:
                raw = raw.replace(marker, "")
            m = re.search(r'\[[\s\S]*\]', raw)
            if m:
                results = json.loads(m.group())
                for r in results:
                    for k in ["calc_value","actual_value","diff_value"]:
                        if k in r:
                            try: r[k] = float(round(r[k], 2))
                            except: r[k] = 0.0
            logger.info(f"校验完成，{len(results)} 条结果")
        except Exception as e:
            logger.error(f"校验异常: {e}")
        return results

    def execute_full_reconciliation(self, payload: dict) -> Dict[str, Any]:
        self.tolerance = payload.pop("tolerance", DEFAULT_TOLERANCE)
        self.standardize_report_data(payload)
        details = self.execute_dynamic_check()
        total = len(details)
        passed = sum(1 for d in details if d.get("is_pass"))
        table_summary = {}
        for d in details:
            tname = d.get("table_name","未知")
            if tname not in table_summary:
                table_summary[tname] = {"total":0,"pass":0,"fail":0}
            table_summary[tname]["total"] += 1
            if d.get("is_pass"): table_summary[tname]["pass"] += 1
            else: table_summary[tname]["fail"] += 1
        return {
            "summary": {"total_check_count": total, "pass_count": passed,
                        "fail_count": total-passed, "table_summary": table_summary},
            "details": details
        }


def run_financial_reconciliation(report_content: str,
                                  tolerance: float = DEFAULT_TOLERANCE) -> Dict[str, Any]:
    logger.info(f"执行财务勾稽校验 | 容差={tolerance}")
    checker = FinancialReconciliationPlugin()
    result = checker.execute_full_reconciliation({"report_content": report_content, "tolerance": tolerance})
    logger.info(f"完成，返回 {len(result.get('details',[]))} 条结果")
    return result
