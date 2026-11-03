#!/usr/bin/env python3
"""
故事剧本转漫画示例脚本
演示如何使用ComicGenerator从剧本生成漫画
"""

import os
import sys

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.generator import ComicGenerator, generate_comics_from_script


# 示例剧本
SAMPLE_SCRIPT = """
一、剧名：《书的另一边》
时长：约3-4分钟
场景：某高校图书馆

二、主角特征
小科（男，大一新生）
- 人设：信奉"搜索引擎解决一切"。
小图（女，资深学科馆员）
- 人设：25岁左右，戴金属框智能眼镜，穿着印有图书馆logo的文化衫，外表文静，说话轻声细语。
- 特殊能力：能将抽象的信息检索概念转化为具象的视觉场景。
- 隐藏身份：反转关键——她并非真人馆员，而是图书馆核心AI"馆灵"的拟人化终端。

三、剧情脉络
1. 开场：闯入者
（镜头：小科一边看手机地图一边走进图书馆，差点撞上还书台）
小科（对着手机吐槽）："这破图书馆APP，找个'电路基础'都这么费劲……算了，反正网上什么都有。"
（他随手抽出一本纸质《电磁场理论》，嫌弃地吹了吹灰，正准备离开。）
小图（无声出现在他身后）："同学，你拿错了。那本是1987年版，你们教材用的是第五版，在二楼北区TN类，索书号TN01-43/1024=5。"
小科（回头）："……你背下来的？"
小图："不是背的，是'看见'的。这座图书馆里每一本书的位置、每一个数据库的入口，我都能'看见'。"

2. 发展：不服与较量
小科："那又怎样？我百度一下，三秒出答案。"
小图（抬手在空中划了一下，周围的场景瞬间切换为虚拟空间）："那我们来比一次。题目——'近五年钙钛矿太阳能电池的衰减机理研究综述'，你搜你的，我查我的。规则：你得在广告弹窗、付费墙和垃圾信息里找出真东西，我只需要……一秒。"
（屏幕分屏显示：小科被各种付费PDF、无效链接折磨；小图瞬间调出5篇高被引综述、3个专利库数据、1个本校教授未公开的预印本。）

3. 反转：图书馆不是你以为的图书馆
小科："你到底是谁？普通馆员不可能……"
小图："我叫小图，是这座图书馆的AI管理系统。我的'身体'是投影，我的'记忆'是这座馆里每一本纸质书扫描后的字符库、每一个数据库的镜像节点。你以为图书馆只是存书的地方？"
（她抬手，整个图书馆的灯光依次亮起，组成巨大的知识网络图谱）
小图："纸质书是锚点，电子资源是触手，而我是这座岛屿与你们之间的摆渡人。你们以为在找书，其实书也在等你们。"

4. 结局：新生的开始
（镜头回到现实，小科仍站在书架前，手里还拿着那本1987年版的《电磁场理论》）
小科："那我刚才拿错这本书……也是你安排的？"
小图（已恢复普通馆员模样，在远处整理书架，回头笑了一下）："我只是让那本书'恰好'没被归位。它等了37年，终于等到了一个真正会问'为什么'的人。"
（小科怔住，低头看了看手里的旧书，翻开扉页——上面有历届学长用铅笔写下的批注、疑问、甚至吐槽。他第一次意识到，纸质书的温度，藏在时间的缝隙里。）
"""


def main():
    """主函数"""
    print("=" * 60)
    print("故事剧本转漫画示例")
    print("=" * 60)

    # 创建输出目录
    output_dir = "examples/output"
    os.makedirs(output_dir, exist_ok=True)

    # 方法1：使用ComicGenerator类
    print("\n[方法1] 使用ComicGenerator类")
    print("-" * 40)

    # 初始化生成器
    generator = ComicGenerator(style="comic", width=1200, height=900)

    # 解析剧本
    print("解析剧本...")
    script_info = generator.parse_script(SAMPLE_SCRIPT)

    # 显示解析结果
    print(f"剧名：{script_info.title}")
    print(f"时长：{script_info.duration}")
    print(f"场景：{script_info.location}")
    print(f"角色数量：{len(script_info.characters)}")
    print("角色列表：")
    for char in script_info.characters:
        print(f"  - {char.name} ({char.gender})")
        if char.personality:
            print(f"    人设：{char.personality}")
    print(f"场景数量：{len(script_info.scenes)}")
    print("场景列表：")
    for scene in script_info.scenes:
        print(f"  {scene.number}. {scene.title} ({len(scene.dialogues)}句对话)")

    # 生成漫画
    print("\n生成漫画...")
    results = generator.generate(
        script_info=script_info,
        output_dir=output_dir,
        format="png",
        layout="2x2"
    )

    print(f"生成完成！")
    print(f"封面：{results.get('cover', 'N/A')}")
    print(f"面板数量：{len(results['panels'])}")
    print(f"页面数量：{len(results['pages'])}")

    # 显示生成的文件
    print("\n生成的文件：")
    for i, panel in enumerate(results['panels']):
        print(f"  面板{i+1}: {panel['path']}")
    for page in results['pages']:
        print(f"  页面{page['page']}: {page['path']}")

    # 方法2：使用便捷函数
    print("\n" + "=" * 60)
    print("[方法2] 使用便捷函数")
    print("-" * 40)

    output_dir2 = "examples/output2"
    results2 = generate_comics_from_script(
        SAMPLE_SCRIPT,
        output_dir=output_dir2,
        style="simple"
    )
    print(f"生成完成！面板数量：{len(results2['panels'])}")

    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
