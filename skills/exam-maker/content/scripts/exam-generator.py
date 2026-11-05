#!/usr/bin/env python3
"""
exam-generator.py — 辅助生成试卷 Markdown 内容
用法：
  python exam-generator.py                    # 交互式生成
  python exam-generator.py --topic "三角函数"   # 指定知识点
  python exam-generator.py --auto             # 自动生成示例试卷
"""

import sys
import os
from datetime import datetime

TOPIC_BANK = {
    "函数": [
        ("幂函数 $y=x^n$ 的图象与性质", "选择题", 5),
        ("指数函数 $y=a^x$ 与对数函数 $y=\\log_a x$ 的图象关系", "填空题", 4),
        ("复合函数 $f(g(x))$ 的单调性判断", "解答题", 12),
        ("函数 $y = \\dfrac{x-1}{x+2}$ 的值域与渐近线", "解答题", 12),
    ],
    "三角函数": [
        ("已知 $\\sin x = \\dfrac{3}{5}$，$x \\in (0, 2\\pi)$，求 $\\cos x$", "填空题", 4),
        ("证明：$\\sin(A+B) = \\sin A \\cos B + \\cos A \\sin B$", "解答题", 12),
        ("求 $y = 2\\sin(x - \\dfrac{\\pi}{3})$ 的最大值、最小值及周期", "解答题", 12),
        ("解方程：$\\tan 2x = \\sqrt{3}$，$x \\in [0, 2\\pi)$", "选择题", 5),
    ],
    "数列": [
        ("等差数列 $\{a_n\}$，已知 $a_1=3$，$d=2$，求 $S_{20}$", "选择题", 5),
        ("等比数列 $\{a_n\}$ 中 $a_1=2$，$q=3$，求前 5 项和", "填空题", 4),
        ("已知 $a_1=1$，$a_{n+1}=2a_n+1$，求通项公式", "解答题", 12),
        ("求 $\\sum_{k=1}^n k^2$ 的公式及证明", "解答题", 12),
    ],
    "导数": [
        ("已知 $f(x)=x^3-3x^2+2x$，求 $f'(x)$ 及极值点", "选择题", 5),
        ("$\\displaystyle \\lim_{x \\to 0} \\frac{e^x - 1}{x} = $", "填空题", 4),
        ("求函数 $y=x^3-3x$ 在 $[-2,2]$ 上的最大值与最小值", "解答题", 12),
        ("利用导数证明：$e^x \\geqslant 1 + x$（$x \\in \\mathbb{R}$）", "解答题", 12),
    ],
    "解析几何": [
        ("椭圆 $\\dfrac{x^2}{25}+\\dfrac{y^2}{16}=1$ 的焦距为", "选择题", 5),
        ("直线 $y=kx+1$ 与圆 $x^2+y^2=4$ 相切，求 $k$", "填空题", 4),
        ("求双曲线 $x^2 - y^2 = 4$ 的渐近线方程", "填空题", 4),
        ("抛物线 $y^2=4x$ 的焦点到直线 $x-y+1=0$ 的距离", "选择题", 5),
        ("证明：椭圆上任意一点到两焦点的距离之和为常数", "解答题", 12),
    ],
    "向量": [
        ("已知 $\\vec{a}=(1,2)$，$\\vec{b}=(3,-1)$，求 $\\vec{a} \\cdot \\vec{b}$", "选择题", 5),
        ("若 $|\\vec{a}|=3$，$|\\vec{b}|=4$，夹角 $60°$，求 $|\\vec{a}+\\vec{b}|$", "填空题", 4),
        ("向量 $\\vec{AB}=(3,4)$，$A(1,2)$，求点 $B$ 坐标", "选择题", 5),
        ("用向量法证明：平行四边形对角线互相平分", "解答题", 12),
    ],
}

def format_choice(title, score):
    return f"""**{title}**
- A. 选项一
- B. 选项二
- C. 选项三
- D. 选项四
**答案：**[老师填写]"""

def format_blank(title, score):
    return f"""**{title}**
**答案：** __________"""

def format_essay(title, score):
    return f"""**{title}**
**答案：**
[教师参考答案]
"""

def generate_auto_exam():
    """根据题库自动生成一份示例试卷"""
    now = datetime.now()
    date_str = now.strftime("%Y年%B%B%d日").replace("0", "").lstrip("0")
    subject = "高中数学"

    lines = [
        f"# {date_str} {subject}复习练习",
        "",
        f"- 科目：{subject} | 满分：100分 | 时间：90分钟",
        "",
        "---",
        "",
        "## 一、选择题（共 8 题，每题 5 分）",
        "",
    ]

    # 从题库抽取选择题
    import random
    topics = list(TOPIC_BANK.keys())
    choice_qs = []
    for i in range(8):
        topic = random.choice(topics)
        q = random.choice(TOPIC_BANK[topic])
        lines.append(f"{i+1}. （5分）{q[0]}")
        lines.append(f"   - A. 正确")
        lines.append(f"   - B. 错误")
        lines.append(f"   - C. 不确定")
        lines.append(f"   - D. 以上都不对")
        lines.append(f"   **答案：**[老师填写]")
        lines.append("")

    lines.append("## 二、填空题（共 6 题，每题 5 分）")
    lines.append("")

    for i in range(6):
        topic = random.choice(topics)
        q = random.choice(TOPIC_BANK[topic])
        if "选择题" in q[1]:
            topic = random.choice(topics)
            q = random.choice(TOPIC_BANK[topic])
        lines.append(f"{i+9}. （5分）{q[0]}")
        lines.append(f"   **答案：** __________")
        lines.append("")

    lines.append("## 三、解答题（共 3 题，共 40 分）")
    lines.append("")

    for i, topic in enumerate(random.sample(topics, 3), 1):
        q = random.choice(TOPIC_BANK[topic])
        lines.append(f"{i+14}. （12分）{q[0]}")
        lines.append(f"   **答案：**[教师参考答案]")
        lines.append("")

    return "\n".join(lines)

def main():
    if "--auto" in sys.argv:
        content = generate_auto_exam()
    elif "--topic" in sys.argv:
        idx = sys.argv.index("--topic")
        topic = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "函数"
        content = f"# {topic} 练习题\n\n"
        if topic in TOPIC_BANK:
            for i, (q, qtype, score) in enumerate(TOPIC_BANK[topic], 1):
                content += f"{i}. （{score}分）{q}\n"
                content += "   **答案：** __________\n\n"
        else:
            content += f"（暂无 {topic} 题库，请联系管理员添加）\n"

    else:
        print("用法：")
        print("  python exam-generator.py --auto       # 自动生成示例试卷")
        print("  python exam-generator.py --topic 三角函数  # 生成指定知识点练习")
        sys.exit(0)

    output = f"generated_exam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(output, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ 试卷已生成：{output}")


if __name__ == '__main__':
    main()
