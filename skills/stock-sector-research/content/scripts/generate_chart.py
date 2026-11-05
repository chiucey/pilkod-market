#!/usr/bin/env python3
"""
Chart Generator for Stock Sector Research
Generate visual charts including industry maps, competition charts, and capital flow diagrams
"""

from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class ChartConfig:
    """Configuration for chart generation"""
    width: int = 800
    height: int = 600
    theme: str = "default"
    output_format: str = "svg"


class MermaidChartGenerator:
    """Generate charts using Mermaid syntax"""

    def __init__(self, config: Optional[ChartConfig] = None):
        self.config = config or ChartConfig()

    def industry_chain_chart(
        self,
        sectors: List[str],
        relationships: List[Tuple[str, str]],
        output_file: str = "industry_chain.md"
    ) -> str:
        """
        Generate industry chain chart in Mermaid syntax

        Args:
            sectors: List of sector names (e.g., ["原材料", "制造", "应用"])
            relationships: List of (upstream, downstream) tuples
            output_file: Output file path

        Returns:
            Mermaid syntax string
        """
        mermaid = "```mermaid\n"
        mermaid += "flowchart LR\n"
        mermaid += "    subgraph 产业链[" + "=" * 30 + "\\n产业链结构\\n" + "=" * 30 + "]\n"

        # Create nodes
        node_map = {}
        for i, sector in enumerate(sectors):
            node_id = f"S{i+1}"
            node_map[sector] = node_id
            # Add Chinese/English labels
            mermaid += f"        {node_id}[{sector}]\n"

        mermaid += "    end\n"

        # Create relationships
        for upstream, downstream in relationships:
            if upstream in node_map and downstream in node_map:
                mermaid += f"    {node_map[upstream]} --> {node_map[downstream]}\n"

        mermaid += "```"
        return mermaid

    def competition_landscape_chart(
        self,
        companies: List[Tuple[str, float, float]],
        title: str = "竞争格局"
    ) -> str:
        """
        Generate competition landscape pie chart

        Args:
            companies: List of (name, market_share, revenue) tuples
            title: Chart title

        Returns:
            Mermaid syntax string
        """
        mermaid = "```mermaid\n"
        mermaid += "pie \\"" + title + "\\"\n"

        total = sum(c[1] for c in companies)
        for name, share, _ in companies:
            mermaid += f'    "{name} ({share:.1f}%)" : {share}\n'

        mermaid += "```"
        return mermaid

    def capital_flow_chart(
        self,
        flows: List[Tuple[str, float, str]],
        title: str = "资金流向"
    ) -> str:
        """
        Generate capital flow chart

        Args:
            flows: List of (name, amount, direction) tuples
                   direction: "inflow" or "outflow"
            title: Chart title

        Returns:
            Mermaid syntax string
        """
        mermaid = "```mermaid\n"
        mermaid += "flowchart TD\n"

        # Create flow nodes
        for i, (name, amount, direction) in enumerate(flows):
            node_id = f"F{i+1}"
            emoji = "📈" if direction == "inflow" else "📉"
            color = "#90EE90" if direction == "inflow" else "#FFB6C1"
            mermaid += f'    {node_id}["{emoji} {name}: {amount}亿"]\n'

            if direction == "inflow":
                mermaid += f"    style {node_id} fill:{color}\n"
            else:
                mermaid += f"    style {node_id} fill:{color}\n"

        # Add subtitle
        mermaid += f'    title["📊 {title}"]\n'

        mermaid += "```"
        return mermaid

    def valuation_comparison_chart(
        self,
        markets: List[Tuple[str, float, float, float]],
        metric: str = "PE"
    ) -> str:
        """
        Generate valuation comparison chart

        Args:
            markets: List of (market_name, pe, pb, dividend) tuples
            metric: Valuation metric name

        Returns:
            Mermaid syntax string
        """
        mermaid = "```mermaid\n"
        mermaid += "bar-vertical\\n"
        mermaid += f'    title[估值对比 - {metric}]\\n'

        for market, pe, pb, div in markets:
            mermaid += f'    "{market}" : {pe}\\n'

        mermaid += "```"
        return mermaid

    def sector_rotation_chart(
        self,
        phases: List[Tuple[str, str, List[str]]],
        current_phase: int = 0
    ) -> str:
        """
        Generate sector rotation cycle chart

        Args:
            phases: List of (phase_name, asset_class, sectors) tuples
            current_phase: Index of current phase

        Returns:
            Mermaid syntax string
        """
        mermaid = "```mermaid\n"
        mermaid += "stateDiagram-v2\\n"
        mermaid += "    [*] --> 复苏期\\n"

        phase_names = [p[0] for p in phases]
        for i, (name, asset, sectors) in enumerate(phases):
            is_current = "===" if i == current_phase else ""
            mermaid += f'    {name}{is_current} : {asset}\\n'
            mermaid += f'    note for {name} : {", ".join(sectors)}\\n'

        # Create cycle
        for i in range(len(phases) - 1):
            mermaid += f"    {phases[i][0]} --> {phases[i+1][0]}\\n"
        mermaid += f"    {phases[-1][0]} --> {phases[0][0]}\\n"

        mermaid += "```"
        return mermaid

    def porter_five_forces_chart(
        self,
        forces: Dict[str, Tuple[int, str]]
    ) -> str:
        """
        Generate Porter's Five Forces radar chart

        Args:
            forces: Dict of {force_name: (score, description)} where score is 1-5

        Returns:
            Mermaid syntax string
        """
        mermaid = "```mermaid\n"
        mermaid += "flowchart TB\\n"
        mermaid += '    subgraph 五力分析["波特五力分析"]\\n'

        colors = {
            1: "#90EE90",  # Low
            2: "#FFFF99",  # Medium-Low
            3: "#FFD700",  # Medium
            4: "#FFA500",  # Medium-High
            5: "#FF6B6B"   # High
        }

        for force, (score, desc) in forces.items():
            node_id = force.replace(" ", "_")
            color = colors.get(score, "#FFFFFF")
            intensity = "弱" if score <= 2 else ("中" if score == 3 else "强")
            mermaid += f'        {node_id}["{force}\\n{intensity}({score}/5)"]\\n'
            mermaid += f"        style {node_id} fill:{color}\\n"

        mermaid += "    end\\n"
        mermaid += "```"
        return mermaid

    def market_concentration_chart(
        self,
        companies: List[Tuple[str, float]],
        cr_values: Dict[str, float]
    ) -> str:
        """
        Generate market concentration chart

        Args:
            companies: List of (company_name, market_share) tuples
            cr_values: Dict of {"CR3": x, "CR5": y, "CR10": z}

        Returns:
            Mermaid syntax string
        """
        mermaid = "```mermaid\n"
        mermaid += "pie \\"市场集中度\\"\\n"

        for name, share in companies:
            mermaid += f'    "{name} ({share:.1f}%)" : {share}\\n'

        mermaid += "```\\n\\n"

        # Add CR values
        mermaid += "```mermaid\\n"
        mermaid += "flowchart LR\\n"

        for cr, value in cr_values.items():
            emoji = "🏆" if value > 50 else "📊"
            mermaid += f'    {cr}["{emoji} {cr}: {value:.1f}%"]\\n'

        mermaid += "```"
        return mermaid

    def save_chart(self, chart_content: str, output_file: str) -> bool:
        """Save chart to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(chart_content)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False


class ASCIIChartGenerator:
    """Generate ASCII charts for simple terminal output"""

    @staticmethod
    def bar_chart(data: Dict[str, float], title: str = "", max_width: int = 50) -> str:
        """Generate horizontal bar chart in ASCII"""
        output = []
        if title:
            output.append(f"=== {title} ===\\n")

        max_value = max(data.values()) if data else 1
        for label, value in data.items():
            bar_length = int((value / max_value) * max_width)
            bar = "█" * bar_length
            output.append(f"{label:15s} | {bar} {value:.1f}")

        return "\\n".join(output)

    @staticmethod
    def pie_chart(data: Dict[str, float], title: str = "") -> str:
        """Generate simple pie chart representation"""
        output = []
        if title:
            output.append(f"=== {title} ===\\n")

        total = sum(data.values())
        for label, value in data.items():
            pct = (value / total * 100) if total > 0 else 0
            bar_len = int(pct / 2)
            bar = "●" * bar_len
            output.append(f"{label:15s} | {bar} {pct:.1f}%")

        return "\\n".join(output)

    @staticmethod
    def table(data: List[List[str]], headers: List[str]) -> str:
        """Generate ASCII table"""
        if not data or not headers:
            return ""

        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in data:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # Generate header
        header = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
        separator = "-+-".join("-" * w for w in col_widths)

        output = [header, separator]

        # Generate rows
        for row in data:
            line = " | ".join(str(cell).ljust(col_widths[i]) if i < len(col_widths) else str(cell)
                             for i, cell in enumerate(row))
            output.append(line)

        return "\\n".join(output)


class ChartGenerator:
    """Main chart generator with multiple output formats"""

    def __init__(self, output_format: str = "mermaid"):
        self.output_format = output_format
        self.mermaid_gen = MermaidChartGenerator()
        self.ascii_gen = ASCIIChartGenerator()

    def generate(
        self,
        chart_type: str,
        data: Dict,
        output_file: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate chart based on type

        Args:
            chart_type: Type of chart (industry_chain, competition, capital_flow, etc.)
            data: Chart data
            output_file: Optional output file path
            **kwargs: Additional parameters

        Returns:
            Generated chart content
        """
        generators = {
            "industry_chain": self._generate_industry_chain,
            "competition": self._generate_competition,
            "capital_flow": self._generate_capital_flow,
            "valuation": self._generate_valuation,
            "rotation": self._generate_rotation,
            "porter": self._generate_porter,
            "concentration": self._generate_concentration,
        }

        generator = generators.get(chart_type)
        if not generator:
            raise ValueError(f"Unknown chart type: {chart_type}")

        content = generator(data, **kwargs)

        if output_file:
            self.mermaid_gen.save_chart(content, output_file)

        return content

    def _generate_industry_chain(self, data: Dict) -> str:
        sectors = data.get("sectors", [])
        relationships = data.get("relationships", [])
        return self.mermaid_gen.industry_chain_chart(sectors, relationships)

    def _generate_competition(self, data: Dict) -> str:
        companies = data.get("companies", [])
        title = data.get("title", "竞争格局")
        return self.mermaid_gen.competition_landscape_chart(companies, title)

    def _generate_capital_flow(self, data: Dict) -> str:
        flows = data.get("flows", [])
        title = data.get("title", "资金流向")
        return self.mermaid_gen.capital_flow_chart(flows, title)

    def _generate_valuation(self, data: Dict) -> str:
        markets = data.get("markets", [])
        metric = data.get("metric", "PE")
        return self.mermaid_gen.valuation_comparison_chart(markets, metric)

    def _generate_rotation(self, data: Dict) -> str:
        phases = data.get("phases", [])
        current = data.get("current_phase", 0)
        return self.mermaid_gen.sector_rotation_chart(phases, current)

    def _generate_porter(self, data: Dict) -> str:
        forces = data.get("forces", {})
        return self.mermaid_gen.porter_five_forces_chart(forces)

    def _generate_concentration(self, data: Dict) -> str:
        companies = data.get("companies", [])
        cr_values = data.get("cr_values", {})
        return self.mermaid_gen.market_concentration_chart(companies, cr_values)

    # Convenience methods
    def industry_chain(self, sectors: List, relationships: List, output: str = None) -> str:
        return self.generate("industry_chain", {"sectors": sectors, "relationships": relationships}, output)

    def competition_landscape(self, companies: List, output: str = None) -> str:
        return self.generate("competition", {"companies": companies}, output)

    def capital_flow(self, flows: List, output: str = None) -> str:
        return self.generate("capital_flow", {"flows": flows}, output)

    def valuation_comparison(self, markets: List, metric: str = "PE", output: str = None) -> str:
        return self.generate("valuation", {"markets": markets, "metric": metric}, output)

    def sector_rotation(self, phases: List, current_phase: int = 0, output: str = None) -> str:
        return self.generate("rotation", {"phases": phases, "current_phase": current_phase}, output)

    def porter_five_forces(self, forces: Dict, output: str = None) -> str:
        return self.generate("porter", {"forces": forces}, output)


def main():
    """Example usage"""
    generator = ChartGenerator()

    # Example 1: Industry Chain
    print("=== Industry Chain Chart ===")
    chain = generator.industry_chain(
        sectors=["锂矿", "电池材料", "电池芯", "整车制造", "充电服务"],
        relationships=[
            ("锂矿", "电池材料"),
            ("电池材料", "电池芯"),
            ("电池芯", "整车制造"),
            ("整车制造", "充电服务")
        ]
    )
    print(chain)
    print()

    # Example 2: Competition Landscape
    print("=== Competition Landscape ===")
    competition = generator.competition_landscape([
        ("比亚迪", 30, 3000),
        ("特斯拉", 25, 2500),
        ("蔚来", 15, 500),
        ("小鹏", 12, 400),
        ("其他", 18, 800)
    ])
    print(competition)
    print()

    # Example 3: Capital Flow
    print("=== Capital Flow ===")
    flow = generator.capital_flow([
        ("北向资金", 50, "inflow"),
        ("主力资金", -30, "outflow"),
        ("杠杆资金", 20, "inflow"),
        ("融资余额", 15, "inflow")
    ])
    print(flow)
    print()

    # Example 4: Porter's Five Forces
    print("=== Porter's Five Forces ===")
    forces = generator.porter_five_forces({
        "供应商议价能力": (4, "锂矿集中度高"),
        "购买者议价能力": (3, "消费者选择多"),
        "新进入者威胁": (2, "技术壁垒高"),
        "替代品威胁": (3, "混动车型竞争"),
        "行业内竞争": (5, "竞争激烈")
    })
    print(forces)
    print()

    # Example 5: Sector Rotation
    print("=== Sector Rotation Cycle ===")
    rotation = generator.sector_rotation([
        ("复苏期", "股票>债券", ["可选消费", "信息技术"]),
        ("过热期", "大宗商品>股票", ["原材料", "能源"]),
        ("滞胀期", "现金>大宗商品", ["医药", "公用事业"]),
        ("衰退期", "债券>现金", ["金融", "防御消费"])
    ], current_phase=0)
    print(rotation)


if __name__ == "__main__":
    main()
