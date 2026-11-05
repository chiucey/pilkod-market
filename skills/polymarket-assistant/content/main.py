"""
Polymarket Assistant - 预测市场助手

该技能帮助用户查询 Polymarket 预测市场的数据、赔率和账户信息，
以及进行交易操作。

依赖安装：
    pip install requests web3 python-dotenv

环境变量：
    POLYMARKET_API_KEY - API 密钥（可选，用于交易操作）
    POLYMARKET_WALLET_ADDRESS - 钱包地址
    POLYMARKET_PRIVATE_KEY - 私钥（可选，用于签名交易）
"""

import os
import json
import logging
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

import requests
from web3 import Web3

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MarketInfo:
    """市场信息数据结构"""
    market_id: str
    question: str
    description: str
    outcomes: List[str]
    probabilities: List[float]
    volume: float
    liquidity: float
    end_date: Optional[str] = None
    creator: Optional[str] = None


@dataclass
class PositionInfo:
    """持仓信息数据结构"""
    market_id: str
    question: str
    outcome: str
    amount: float
    avg_price: float
    current_price: float
    pnl: float
    pnl_percentage: float


@dataclass
class AccountInfo:
    """账户信息数据结构"""
    wallet_address: str
    usdc_balance: float
    positions: List[PositionInfo]
    total_pnl: float


class PolymarketClient:
    """Polymarket API 客户端"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        wallet_address: Optional[str] = None,
        private_key: Optional[str] = None
    ):
        """
        初始化 Polymarket 客户端

        Args:
            api_key: API 密钥（可选，用于交易操作）
            wallet_address: 钱包地址
            private_key: 私钥（可选，用于签名交易）
        """
        self.api_key = api_key or os.getenv("POLYMARKET_API_KEY")
        self.wallet_address = wallet_address or os.getenv("POLYMARKET_WALLET_ADDRESS")
        self.private_key = private_key or os.getenv("POLYMARKET_PRIVATE_KEY")

        # Polymarket CLOB API 端点
        self.base_url = "https://clob.polymarket.com"
        self.markets_url = f"{self.base_url}/markets"
        self.orders_url = f"{self.base_url}/orders"
        self.positions_url = f"{self.base_url}/positions"

        # 初始化 Web3（Polygon 网络）
        self.w3 = Web3(Web3.HTTPProvider(
            "https://polygon-rpc.com"
        ))

        self._session = requests.Session()
        if self.api_key:
            self._session.headers.update({"Authorization": f"Bearer {self.api_key}"})

    def get_trending_markets(self, limit: int = 10) -> List[MarketInfo]:
        """
        获取热门/趋势市场

        Args:
            limit: 返回的市场数量上限

        Returns:
            热门市场列表
        """
        try:
            # 获取热门市场（按成交量排序）
            url = f"{self.base_url}/markets"
            params = {"limit": limit, "closed": "false"}
            response = self._session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            markets = []
            for item in data.get("markets", [])[:limit]:
                market = MarketInfo(
                    market_id=item.get("conditionId", ""),
                    question=item.get("question", ""),
                    description=item.get("description", ""),
                    outcomes=item.get("outcomes", []),
                    probabilities=[float(p) for p in item.get("outcomePrices", [0, 0])],
                    volume=float(item.get("volume", 0)),
                    liquidity=float(item.get("liquidity", 0)),
                    end_date=item.get("endDate"),
                    creator=item.get("creator")
                )
                markets.append(market)

            return markets

        except requests.RequestException as e:
            logger.error(f"获取热门市场失败: {e}")
            return []

    def search_markets(self, query: str, limit: int = 10) -> List[MarketInfo]:
        """
        根据关键词搜索市场

        Args:
            query: 搜索关键词
            limit: 返回的市场数量上限

        Returns:
            匹配的市场列表
        """
        try:
            # 使用 Polymarket 的市场搜索 API
            url = f"{self.base_url}/markets"
            params = {
                "query": query,
                "limit": limit,
                "closed": "false"
            }
            response = self._session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            markets = []
            for item in data.get("markets", [])[:limit]:
                market = MarketInfo(
                    market_id=item.get("conditionId", ""),
                    question=item.get("question", ""),
                    description=item.get("description", ""),
                    outcomes=item.get("outcomes", []),
                    probabilities=[float(p) for p in item.get("outcomePrices", [0, 0])],
                    volume=float(item.get("volume", 0)),
                    liquidity=float(item.get("liquidity", 0)),
                    end_date=item.get("endDate"),
                    creator=item.get("creator")
                )
                markets.append(market)

            return markets

        except requests.RequestException as e:
            logger.error(f"搜索市场失败: {e}")
            return []

    def get_market_details(self, market_id: str) -> Optional[MarketInfo]:
        """
        获取特定市场的详细信息

        Args:
            market_id: 市场 ID

        Returns:
            市场详细信息
        """
        try:
            url = f"{self.base_url}/markets/{market_id}"
            response = self._session.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not data:
                return None

            return MarketInfo(
                market_id=data.get("conditionId", ""),
                question=data.get("question", ""),
                description=data.get("description", ""),
                outcomes=data.get("outcomes", []),
                probabilities=[float(p) for p in data.get("outcomePrices", [0, 0])],
                volume=float(data.get("volume", 0)),
                liquidity=float(data.get("liquidity", 0)),
                end_date=data.get("endDate"),
                creator=data.get("creator")
            )

        except requests.RequestException as e:
            logger.error(f"获取市场详情失败: {e}")
            return None

    def get_account_balance(self) -> Optional[Dict[str, float]]:
        """
        获取账户余额

        Returns:
            余额信息字典
        """
        if not self.wallet_address:
            logger.warning("未配置钱包地址")
            return None

        try:
            # 使用 Polygon 节点查询 USDC 余额
            # USDC on Polygon: 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
            usdc_address = Web3.to_checksum_address(
                "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
            )

            # ERC-20 代币余额 ABI
            abi = [{
                "constant": True,
                "inputs": [{"name": "_owner"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance"}],
                "type": "function"
            }]

            contract = self.w3.eth.contract(address=usdc_address, abi=abi)
            balance_wei = contract.functions.balanceOf(
                Web3.to_checksum_address(self.wallet_address)
            ).call()

            # 转换为正常数字（USDC 有 6 位小数）
            balance = balance_wei / (10 ** 6)

            return {
                "usdc": balance,
                "wallet_address": self.wallet_address
            }

        except Exception as e:
            logger.error(f"获取账户余额失败: {e}")
            return None

    def get_positions(self) -> List[PositionInfo]:
        """
        获取用户持仓信息

        Returns:
            持仓列表
        """
        if not self.wallet_address or not self.api_key:
            logger.warning("未配置钱包地址或 API Key")
            return []

        try:
            url = f"{self.positions_url}"
            params = {"user": self.wallet_address}
            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = self._session.get(
                url, params=params, headers=headers, timeout=10
            )
            response.raise_for_status()
            data = response.json()

            positions = []
            for item in data.get("positions", []):
                pos = PositionInfo(
                    market_id=item.get("conditionId", ""),
                    question=item.get("question", ""),
                    outcome=item.get("outcome", ""),
                    amount=float(item.get("size", 0)),
                    avg_price=float(item.get("avgPrice", 0)),
                    current_price=float(item.get("currentPrice", 0)),
                    pnl=float(item.get("pnl", 0)),
                    pnl_percentage=float(item.get("pnlPercentage", 0))
                )
                positions.append(pos)

            return positions

        except requests.RequestException as e:
            logger.error(f"获取持仓信息失败: {e}")
            return []

    def place_order(
        self,
        market_id: str,
        outcome_index: int,
        amount: float,
        side: str = "BUY"
    ) -> Optional[Dict[str, Any]]:
        """
        下单交易

        Args:
            market_id: 市场 ID
            outcome_index: 结果索引（0 或 1）
            amount: 买入/卖出数量
            side: 订单方向 ("BUY" 或 "SELL")

        Returns:
            订单结果
        """
        if not self.api_key or not self.wallet_address:
            logger.error("交易操作需要 API Key 和钱包地址")
            return None

        try:
            url = f"{self.orders_url}"
            order_data = {
                "market": market_id,
                "outcomeIndex": outcome_index,
                "amount": amount,
                "side": side.upper(),
                "user": self.wallet_address,
                "signature": self._generate_signature(market_id, outcome_index, amount, side)
            }

            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = self._session.post(
                url, json=order_data, headers=headers, timeout=10
            )
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            logger.error(f"下单失败: {e}")
            return None

    def _generate_signature(
        self,
        market_id: str,
        outcome_index: int,
        amount: float,
        side: str
    ) -> str:
        """
        生成交易签名（简化版本）

        注意：实际生产环境中应使用正确的 EIP-712 签名
        """
        message = f"{market_id}:{outcome_index}:{amount}:{side}"
        if self.private_key and self.w3.eth.account:
            account = self.w3.eth.account.from_key(self.private_key)
            signed = account.sign_message(text=message)
            return signed.signature.hex()
        return ""


def format_market_info(market: MarketInfo) -> str:
    """格式化市场信息为可读字符串"""
    outcomes_str = "\n".join([
        f"  - {outcome}: {prob*100:.1f}%"
        for outcome, prob in zip(market.outcomes, market.probabilities)
    ])

    return f"""
**市场问题**: {market.question}

**描述**: {market.description}

**当前赔率**:
{outcomes_str}

**成交量**: ${market.volume:,.2f}
**流动性**: ${market.liquidity:,.2f}
**市场ID**: `{market.market_id}`
"""


def format_account_info(account: AccountInfo) -> str:
    """格式化账户信息为可读字符串"""
    positions_str = ""
    if account.positions:
        for pos in account.positions:
            positions_str += f"""
- **{pos.question}**
  - 方向: {pos.outcome}
  - 数量: {pos.amount}
  - 当前价格: {pos.current_price:.4f}
  - 盈亏: ${pos.pnl:.2f} ({pos.pnl_percentage:.1f}%)
"""
    else:
        positions_str = "暂无持仓"

    return f"""
**钱包地址**: `{account.wallet_address}`

**USDC 余额**: ${account.usdc_balance:,.2f}

**当前持仓**:
{positions_str}

**总盈亏**: ${account.total_pnl:.2f}
"""


# === 主要入口函数 ===

def handle_trending_markets(client: PolymarketClient, limit: int = 10) -> str:
    """处理热门市场查询"""
    markets = client.get_trending_markets(limit)

    if not markets:
        return "暂时无法获取热门市场数据，请稍后重试。"

    result = "## 热门预测市场\n\n"
    for i, market in enumerate(markets, 1):
        result += f"### {i}. {market.question}\n"
        result += f"成交量: ${market.volume:,.2f}\n"
        result += f"赔率: {market.probabilities[0]*100:.1f}% vs {market.probabilities[1]*100:.1f}%\n"
        result += f"市场ID: `{market.market_id}`\n\n"

    return result


def handle_market_search(client: PolymarketClient, query: str) -> str:
    """处理市场搜索"""
    markets = client.search_markets(query)

    if not markets:
        return f"没有找到与 '{query}' 相关的市场。"

    result = f"## '{query}' 相关市场\n\n"
    for market in markets:
        result += format_market_info(market)
        result += "---\n\n"

    return result


def handle_market_details(client: PolymarketClient, market_id: str) -> str:
    """处理市场详情查询"""
    market = client.get_market_details(market_id)

    if not market:
        return f"无法找到市场 ID 为 '{market_id}' 的市场。"

    return f"## 市场详情\n\n{format_market_info(market)}"


def handle_account_info(client: PolymarketClient) -> str:
    """处理账户信息查询"""
    balance = client.get_account_balance()
    positions = client.get_positions()

    if not balance:
        return "无法获取账户信息。请确保已配置钱包地址。"

    # 计算总盈亏
    total_pnl = sum(pos.pnl for pos in positions)

    account = AccountInfo(
        wallet_address=balance["wallet_address"],
        usdc_balance=balance["usdc"],
        positions=positions,
        total_pnl=total_pnl
    )

    return f"## 账户信息\n\n{format_account_info(account)}"


def handle_trade(
    client: PolymarketClient,
    market_id: str,
    outcome_index: int,
    amount: float,
    side: str = "BUY"
) -> str:
    """处理交易操作"""
    if not client.api_key:
        return "交易操作需要 API Key。请联系管理员获取。"

    result = client.place_order(market_id, outcome_index, amount, side)

    if not result:
        return f"交易执行失败。请检查市场 ID 和参数是否正确。"

    return f"""
## 交易执行成功

**市场 ID**: `{market_id}`
**方向**: {side}
**数量**: {amount}
**结果索引**: {outcome_index}

订单详情: {json.dumps(result, indent=2)}
"""


# === 对外暴露的技能入口 ===

def main():
    """主函数 - 用于测试"""
    import sys

    client = PolymarketClient()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "trending":
            print(handle_trending_markets(client))
        elif command == "search" and len(sys.argv) > 2:
            print(handle_market_search(client, sys.argv[2]))
        elif command == "details" and len(sys.argv) > 2:
            print(handle_market_details(client, sys.argv[2]))
        elif command == "account":
            print(handle_account_info(client))
        elif command == "trade" and len(sys.argv) > 5:
            print(handle_trade(
                client,
                sys.argv[2],
                int(sys.argv[3]),
                float(sys.argv[4]),
                sys.argv[5]
            ))
        else:
            print("用法:")
            print("  python main.py trending                    # 查看热门市场")
            print("  python main.py search <关键词>            # 搜索市场")
            print("  python main.py details <市场ID>           # 查看市场详情")
            print("  python main.py account                    # 查看账户信息")
            print("  python main.py trade <市场ID> <结果> <数量> <方向>  # 交易")
    else:
        print(handle_trending_markets(client))


if __name__ == "__main__":
    main()
