#!/usr/bin/env python3
"""
Tushare API 纯标准库实现 - 不需要 pip install tushare
直接通过 HTTP 调用 Tushare Pro API
"""

import os
import json
import urllib.request
import urllib.parse
from typing import Optional, Dict, List, Any

API_URL = "http://api.tushare.pro"


class TushareAPI:
    """Tushare API 客户端（纯标准库版本，无需 pip）"""

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("TUSHARE_TOKEN")
        if not self.token:
            raise ValueError(
                "未找到 Tushare Token。请设置环境变量 TUSHARE_TOKEN\n"
                "获取 Token: https://tushare.pro"
            )

    def call(self, api_name: str, params: Optional[Dict] = None,
             fields: Optional[str] = None) -> Dict:
        """调用 Tushare API"""
        payload = {
            "api_name": api_name,
            "token": self.token,
            "params": params or {},
            "fields": fields or ""
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            API_URL,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))

        if result.get("code") != 0:
            raise Exception(f"API Error [{result.get('code')}]: {result.get('msg')}")

        return result.get("data", {})

    def parse_data(self, data: Dict) -> List[Dict]:
        """解析 API 返回的数据为字典列表"""
        if not data or not data.get("items"):
            return []
        fields = data.get("fields", [])
        items = data.get("items", [])
        return [dict(zip(fields, item)) for item in items]

    # ==================== 常用接口 ====================

    def daily(self, ts_code: str, start_date: str = "", end_date: str = "",
              fields: Optional[str] = None) -> List[Dict]:
        """日线行情"""
        params = {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
        f = fields or "ts_code,trade_date,open,high,low,close,vol,amount"
        data = self.call("daily", params, f)
        return self.parse_data(data)

    def stock_basic(self, ts_code: str = "", market: str = "",
                    fields: Optional[str] = None) -> List[Dict]:
        """股票基本信息"""
        params = {"ts_code": ts_code, "market": market}
        f = fields or "ts_code,name,area,industry,market,list_date"
        data = self.call("stock_basic", params, f)
        return self.parse_data(data)

    def income(self, ts_code: str, start_date: str = "", end_date: str = "",
               fields: Optional[str] = None) -> List[Dict]:
        """利润表"""
        params = {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
        f = fields or "ts_code,ann_date,f_ann_date,report_type, Basic_EPS, Total_Revenue, Net_Profit"
        data = self.call("income", params, f)
        return self.parse_data(data)

    def fina_indicator(self, ts_code: str, start_date: str = "", end_date: str = "",
                       fields: Optional[str] = None) -> List[Dict]:
        """财务指标"""
        params = {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
        f = fields or "ts_code,ann_date,roe,eps,gross_profit_margin,net_profit_ratio"
        data = self.call("fina_indicator", params, f)
        return self.parse_data(data)

    def index_daily(self, ts_code: str, start_date: str = "", end_date: str = "",
                    fields: Optional[str] = None) -> List[Dict]:
        """指数日线"""
        params = {"ts_code": ts_code, "start_date": start_date, "end_date": end_date}
        f = fields or "ts_code,trade_date,close,vol,amount"
        data = self.call("index_daily", params, f)
        return self.parse_data(data)

    def trade_cal(self, exchange: str = "", start_date: str = "", end_date: str = "",
                  fields: Optional[str] = None) -> List[Dict]:
        """交易日历"""
        params = {"exchange": exchange, "start_date": start_date, "end_date": end_date}
        f = fields or "exchange,cal_date,is_open"
        data = self.call("trade_cal", params, f)
        return self.parse_data(data)

    def fund_nav(self, ts_code: str = "", market: str = "",
                 fields: Optional[str] = None) -> List[Dict]:
        """基金净值"""
        params = {"ts_code": ts_code, "market": market}
        f = fields or "ts_code,ann_date,nav,nav_type,unit_nav,acc_nav"
        data = self.call("fund_nav", params, f)
        return self.parse_data(data)


if __name__ == "__main__":
    import sys, pprint
    api = TushareAPI()

    if len(sys.argv) < 2:
        print("用法: python tushare_api.py <接口名> [参数JSON]")
        print("示例: python tushare_api.py daily '{\"ts_code\":\"000001.SZ\",\"start_date\":\"20240101\",\"end_date\":\"20240110\"}'")
        sys.exit(1)

    method = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    func = getattr(api, method, None)
    if not func:
        print(f"未知接口: {method}")
        sys.exit(1)

    result = func(**params) if params else func()
    pprint.pprint(result[:5] if result else [])
    print(f"\n共返回 {len(result)} 条记录")
