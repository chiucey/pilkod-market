# -*- coding: utf-8 -*-
"""
Skill 验证脚本
用于检查 Skill 的完整性和正确性
"""
import os
import sys
import re
import json
import hashlib
import importlib.util
from pathlib import Path
from datetime import datetime


class SkillValidator:
    """Skill 验证器"""

    def __init__(self, skill_dir):
        self.skill_dir = Path(skill_dir)
        self.errors = []
        self.warnings = []
        self.info = []

    def validate(self):
        """执行完整验证流程"""
        print("="*70)
        print(f"  Skill 验证报告")
        print(f"  目录: {self.skill_dir}")
        print(f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)

        # 1. 检查目录存在
        self._check_directory_exists()
        # 2. 检查 SKILL.md
        self._check_skill_md()
        # 3. 检查目录结构
        self._check_structure()
        # 4. 检查脚本
        self._check_scripts()
        # 5. 检查示例
        self._check_examples()
        # 6. 功能测试
        self._run_functional_test()

        # 输出报告
        self._print_report()
        return len(self.errors) == 0

    def _check_directory_exists(self):
        """检查目录存在"""
        if not self.skill_dir.exists():
            self.errors.append(f"❌ Skill 目录不存在: {self.skill_dir}")
            return False
        self.info.append(f"✅ Skill 目录存在: {self.skill_dir.name}")
        return True

    def _check_skill_md(self):
        """检查 SKILL.md 元数据"""
        skill_md = self.skill_dir / "SKILL.md"
        if not skill_md.exists():
            self.errors.append("❌ 缺少 SKILL.md 文件")
            return False

        content = skill_md.read_text(encoding='utf-8')

        # 检查 YAML frontmatter
        if not content.startswith('---'):
            self.errors.append("❌ SKILL.md 缺少 YAML frontmatter (应以 --- 开头)")
            return False

        # 提取 frontmatter
        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                self.errors.append("❌ SKILL.md frontmatter 格式错误")
                return False
            frontmatter = parts[1].strip()
        except Exception as e:
            self.errors.append(f"❌ SKILL.md frontmatter 解析失败: {e}")
            return False

        # 必需字段
        required_fields = ['name', 'description', 'skill_id']
        for field in required_fields:
            pattern = rf'^{field}:\s*'
            if not re.search(pattern, frontmatter, re.MULTILINE):
                self.errors.append(f"❌ SKILL.md 缺少必需字段: {field}")

        # 检查 name 格式
        name_match = re.search(r'^name:\s*([\w-]+)', frontmatter, re.MULTILINE)
        if name_match:
            name = name_match.group(1)
            if not re.match(r'^[a-z0-9-]+$', name):
                self.warnings.append(f"⚠️  Skill name 应使用小写字母、数字和连字符: {name}")
            else:
                self.info.append(f"✅ Skill name: {name}")

        # 检查 skill_id 是数字
        id_match = re.search(r'^skill_id:\s*(\d+)', frontmatter, re.MULTILINE)
        if id_match:
            skill_id = id_match.group(1)
            if not skill_id.isdigit():
                self.errors.append(f"❌ skill_id 必须是数字: {skill_id}")
            else:
                self.info.append(f"✅ Skill ID: {skill_id}")

        # 检查 description 长度
        desc_match = re.search(r'^description:\s*\|', frontmatter, re.MULTILINE)
        if desc_match:
            self.info.append("✅ description 字段存在（多行格式）")

        # 文件大小
        size_kb = skill_md.stat().st_size / 1024
        self.info.append(f"📄 SKILL.md 大小: {size_kb:.2f} KB")

    def _check_structure(self):
        """检查目录结构"""
        required_dirs = ['scripts']
        recommended_dirs = ['examples', 'assets']

        for d in required_dirs:
            path = self.skill_dir / d
            if not path.exists():
                self.errors.append(f"❌ 缺少必需目录: {d}/")
            else:
                files = list(path.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                self.info.append(f"✅ 目录 {d}/ 存在，包含 {file_count} 个文件")

        for d in recommended_dirs:
            path = self.skill_dir / d
            if not path.exists():
                self.warnings.append(f"⚠️  建议添加目录: {d}/")
            else:
                files = list(path.rglob('*'))
                file_count = len([f for f in files if f.is_file()])
                self.info.append(f"✅ 目录 {d}/ 存在，包含 {file_count} 个文件")

    def _check_scripts(self):
        """检查脚本文件"""
        scripts_dir = self.skill_dir / "scripts"
        if not scripts_dir.exists():
            return

        py_files = list(scripts_dir.glob("*.py"))
        if not py_files:
            self.warnings.append("⚠️  scripts/ 目录没有 Python 脚本")
            return

        for py_file in py_files:
            # 检查 Python 语法
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), py_file.name, 'exec')
                self.info.append(f"✅ 脚本语法正确: {py_file.name}")
            except SyntaxError as e:
                self.errors.append(f"❌ 脚本语法错误: {py_file.name} - {e}")

            # 检查文件大小
            size_kb = py_file.stat().st_size / 1024
            if size_kb < 1:
                self.warnings.append(f"⚠️  脚本文件过小: {py_file.name} ({size_kb:.2f} KB)")
            else:
                self.info.append(f"📄 脚本大小: {py_file.name} ({size_kb:.2f} KB)")

    def _check_examples(self):
        """检查示例文件"""
        examples_dir = self.skill_dir /"examples"
        if not examples_dir.exists():
            return

        for ex_file in examples_dir.iterdir():
            if ex_file.suffix == '.json':
                try:
                    with open(ex_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self.info.append(f"✅ JSON 示例有效: {ex_file.name}")
                    # 检查关键字段
                    if 'model' in data and 'full_name' in data:
                        self.info.append(f"   └─ 包含完整产品信息: {data.get('full_name', 'N/A')}")
                except json.JSONDecodeError as e:
                    self.errors.append(f"❌ JSON 示例无效: {ex_file.name} - {e}")
            elif ex_file.suffix in ['.md', '.txt']:
                self.info.append(f"✅ 文档示例: {ex_file.name}")

    def _run_functional_test(self):
        """功能测试：实际运行生成脚本"""
        print("\n" + "="*70)
        print("  🧪 功能测试")
        print("="*70)

        # 尝试导入并运行生成脚本
        script_path = self.skill_dir / "scripts" / "generate_requirements.py"
        if not script_path.exists():
            self.errors.append("❌ 生成脚本不存在，无法进行功能测试")
            return

        try:
            # 动态导入
            spec = importlib.util.spec_from_file_location("gen_req", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 测试数据
            test_data = {
                "model": "TEST01",
                "product_name": "Test-Product",
                "full_name": "FMS Test Product for Validation",
                "scale": "1/18",
                "motor_type": "有刷",
                "vehicle_model": "TestVehicle",
                "license": "TestLicense",
                "colors": ["黑色", "白色"],
                "features": [
                    "测试卖点1：LCG低重心底盘",
                    "测试卖点2：多品牌授权",
                    "测试卖点3：磁吸快拆",
                    "测试卖点4：首推车型"
                ],
                "dimensions": "300*150*150mm",
                "wheelbase": "200mm",
                "ground_clearance": "30mm",
                "battery_motor": "180有刷",
                "has_source_assets": True,
                "need_scene_images": True,
                "need_shooting": False,
                "output_dir": str(self.skill_dir.parent / "test_output")
            }

            # 执行生成
            output_path = module.generate_amazon_image_requirements(test_data)
            self.info.append(f"✅ 功能测试通过")
            self.info.append(f"   └─ 输出文件: {Path(output_path).name}")

            # 检查输出文件
            if os.path.exists(output_path):
                size_kb = os.path.getsize(output_path) / 1024
                self.info.append(f"   └─ 文件大小: {size_kb:.2f} KB")

                # 验证 Excel 文件可读
                try:
                    import openpyxl
                    wb = openpyxl.load_workbook(output_path, data_only=True)
                    ws = wb.active
                    self.info.append(f"   └─ Excel 可读，行数: {ws.max_row}, 列数: {ws.max_column}")

                    # 检查关键行
                    if ws.max_row >= 10:
                        self.info.append(f"   └─ ✅ 数据行数满足要求 (>= 10)")
                    else:
                        self.warnings.append(f"⚠️  数据行数偏少: {ws.max_row}")

                except Exception as e:
                    self.errors.append(f"❌ Excel 文件无法读取: {e}")

                # 清理测试文件
                try:
                    os.remove(output_path)
                    self.info.append(f"   └─ 测试文件已清理")
                except:
                    pass
            else:
                self.errors.append(f"❌ 输出文件不存在: {output_path}")

        except Exception as e:
            self.errors.append(f"❌ 功能测试失败: {e}")
            import traceback
            self.errors.append(f"   └─ {traceback.format_exc()}")

    def _print_report(self):
        """打印验证报告"""
        print("\n" + "="*70)
        print("  📋 验证报告汇总")
        print("="*70)

        if self.info:
            print("\n📗 信息 ({}):".format(len(self.info)))
            for msg in self.info:
                print(f"  {msg}")

        if self.warnings:
            print("\n📒 警告 ({}):".format(len(self.warnings)))
            for msg in self.warnings:
                print(f"  {msg}")

        if self.errors:
            print("\n📕 错误 ({}):".format(len(self.errors)))
            for msg in self.errors:
                print(f"  {msg}")

        print("\n" + "="*70)
        if self.errors:
            print(f"  ❌ 验证失败: 发现 {len(self.errors)} 个错误")
        else:
            print(f"  ✅ 验证通过: {'无错误' if not self.errors else f'有 {len(self.errors)} 个错误待修复'}")
        print("="*70)

        # 输出 JSON 格式报告
        report = {
            "skill_dir": str(self.skill_dir),
            "timestamp": datetime.now().isoformat(),
            "passed": len(self.errors) == 0,
            "info_count": len(self.info),
            "warning_count": len(self.warnings),
            "error_count": len(self.errors),
            "errors": self.errors,
            "warnings": self.warnings
        }
        report_path = self.skill_dir / "validation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n📄 详细报告已保存: {report_path}")


def main():
    if len(sys.argv) > 1:
        skill_dir = sys.argv[1]
    else:
        # 默认检查当前脚本所在目录的父目录
        skill_dir = Path(__file__).parent.parent

    validator = SkillValidator(skill_dir)
    success = validator.validate()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
