def run(context=None):
    """
    Lincoln Weekly Report Skill Entry Function
    Function: Read weekly report template and provide weekly report generation capability
    """
    try:
        # Read the weekly report template file
        template_path = "../lincoln-weekly-report.md"
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        # Skill execution result
        result = f"""
林肯舆情周报生成技能已就绪。

使用方法：
1. 请提供Excel数据文件路径
2. 技能将自动分析数据并生成标准格式的周报

模板内容预览：
{template_content[:500]}...
"""
        return result
    except Exception as e:
        return f"技能执行出错：{str(e)}"
