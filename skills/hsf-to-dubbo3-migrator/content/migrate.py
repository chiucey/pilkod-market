#!/usr/bin/env python3
"""
HSF to Dubbo3 Migration Tool
阿里云 HSF 框架迁移到 Apache Dubbo3 框架的自动化迁移工具
支持生成清晰的变更记录供研发人员审核
"""

import os
import re
import sys
import json
import argparse
import difflib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class ChangeType(Enum):
    """变更类型枚举"""
    ANNOTATION = "annotation"
    IMPORT = "import"
    DEPENDENCY = "dependency"
    CONFIG = "config"
    XML_TAG = "xml_tag"
    UNKNOWN = "unknown"


@dataclass
class ChangeRecord:
    """单个变更记录"""
    change_type: str
    original: str
    converted: str
    line_number: int = 0
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "change_type": self.change_type,
            "original": self.original,
            "converted": self.converted,
            "line_number": self.line_number,
            "description": self.description
        }


@dataclass
class FileChangeRecord:
    """文件变更记录"""
    file_path: str
    file_type: str
    total_lines: int
    changes: List[ChangeRecord] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0

    @property
    def change_count(self) -> int:
        return len(self.changes)

    def to_dict(self) -> dict:
        return {
            "file_path": self.file_path,
            "file_type": self.file_type,
            "total_lines": self.total_lines,
            "change_count": self.change_count,
            "additions": self.additions,
            "deletions": self.deletions,
            "changes": [c.to_dict() for c in self.changes]
        }


class HSFToDubbo3Migrator:
    """HSF 到 Dubbo3 迁移器 - 增强版"""

    def __init__(self, input_path: str, output_path: str):
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.migration_report = {
            "migration_info": {
                "timestamp": datetime.now().isoformat(),
                "source_framework": "HSF",
                "target_framework": "Dubbo3",
                "version": "1.0.0"
            },
            "summary": {
                "files_processed": 0,
                "files_modified": 0,
                "files_unchanged": 0,
                "total_changes": 0,
                "annotations_converted": 0,
                "imports_converted": 0,
                "dependencies_updated": 0,
                "configs_migrated": 0
            },
            "file_changes": [],
            "unchanged_files": []
        }
        self.current_file_record: Optional[FileChangeRecord] = None
        self.line_number = 0

        # HSF 注解到 Dubbo3 的映射配置
        self.annotation_mappings = {
            # 服务提供者注解
            '@HSFProvider': ('@DubboService', ChangeType.ANNOTATION, '服务提供者注解'),
            '@com.alibaba.boot.hsf.annotation.HSFProvider': ('@org.apache.dubbo.config.annotation.DubboService', ChangeType.ANNOTATION, '服务提供者注解(完整路径)'),
            '@com.alibaba.boot.hsf.HSFService': ('@org.apache.dubbo.config.annotation.DubboService', ChangeType.ANNOTATION, '服务实现注解'),
            '@com.taobao.hsf.annotation.HSFService': ('@org.apache.dubbo.config.annotation.DubboService', ChangeType.ANNOTATION, '服务实现注解(完整路径)'),
            '@com.alibaba.hsf.annotation.Service': ('@org.apache.dubbo.config.annotation.DubboService', ChangeType.ANNOTATION, '服务注解'),

            # 服务消费者注解
            '@HSFConsumer': ('@DubboReference', ChangeType.ANNOTATION, '服务消费者注解'),
            '@com.alibaba.boot.hsf.annotation.HSFConsumer': ('@org.apache.dubbo.config.annotation.DubboReference', ChangeType.ANNOTATION, '服务消费者注解(完整路径)'),
            '@HSFReference': ('@DubboReference', ChangeType.ANNOTATION, '远程引用注解'),
            '@com.taobao.hsf.annotation.HSFReference': ('@org.apache.dubbo.config.annotation.DubboReference', ChangeType.ANNOTATION, '远程引用注解(完整路径)'),
            '@com.alibaba.hsf.annotation.Reference': ('@org.apache.dubbo.config.annotation.DubboReference', ChangeType.ANNOTATION, '引用注解'),
        }

        # 导入语句映射
        self.import_mappings = {
            'com.alibaba.boot.hsf.annotation.HSFProvider': 'org.apache.dubbo.config.annotation.DubboService',
            'com.alibaba.boot.hsf.annotation.HSFConsumer': 'org.apache.dubbo.config.annotation.DubboReference',
            'com.alibaba.boot.hsf.HSFService': 'org.apache.dubbo.config.annotation.DubboService',
            'com.alibaba.boot.hsf.HSFReference': 'org.apache.dubbo.config.annotation.DubboReference',
            'com.taobao.hsf.annotation.HSFService': 'org.apache.dubbo.config.annotation.DubboService',
            'com.taobao.hsf.annotation.HSFReference': 'org.apache.dubbo.config.annotation.DubboReference',
            'com.alibaba.hsf.annotation.Service': 'org.apache.dubbo.config.annotation.DubboService',
            'com.alibaba.hsf.annotation.Reference': 'org.apache.dubbo.config.annotation.DubboReference',
        }

        # 依赖映射
        self.dependency_mappings = {
            'com.alibaba.boot:hsf-spring-boot-starter': {
                'groupId': 'org.apache.dubbo',
                'artifactId': 'dubbo-spring-boot-starter',
                'version': '3.2.0',
                'description': 'Dubbo3 Spring Boot 启动器'
            },
            'com.taobao.hsf:hsf': {
                'groupId': 'org.apache.dubbo',
                'artifactId': 'dubbo',
                'version': '3.2.0',
                'description': 'Dubbo3 核心包'
            },
            'org.springframework.cloud:spring-cloud-starter-pandora': {
                'removed': True,
                'description': 'Pandora 容器（Ali-Tomcat 环境）已移除'
            }
        }

    def _add_change_record(self, change_type: ChangeType, original: str, converted: str,
                          description: str = "") -> None:
        """添加变更记录"""
        if self.current_file_record:
            record = ChangeRecord(
                change_type=change_type.value,
                original=original.strip(),
                converted=converted.strip(),
                line_number=self.line_number,
                description=description
            )
            self.current_file_record.changes.append(record)

    def _convert_annotation_with_attrs(self, original: str) -> str:
        """转换带属性的注解"""
        # 提取注解名称
        match = re.match(r'(@\w+(?:\.\w+)*)', original)
        if not match:
            return original

        annotation_name = match.group(1)
        if annotation_name not in self.annotation_mappings:
            return original

        new_annotation, change_type, desc = self.annotation_mappings[annotation_name]

        # 提取属性内容
        attr_match = re.search(r'\((.*)\)', original, re.DOTALL)
        if attr_match:
            attrs = attr_match.group(1)
            # 属性映射转换
            attrs = self._convert_annotation_attrs(attrs)
            return f"{new_annotation}({attrs})"

        return new_annotation

    def _convert_annotation_attrs(self, attrs: str) -> str:
        """转换注解属性"""
        # 属性名称映射
        attr_name_mappings = {
            'serviceInterface': 'interfaceClass',
        }

        result = attrs
        for old_name, new_name in attr_name_mappings.items():
            # 替换属性名
            pattern = rf'\b{old_name}\s*='
            result = re.sub(pattern, f'{new_name}=', result)

        return result

    def migrate_file(self, file_path: Path) -> Tuple[str, bool, List[str], FileChangeRecord]:
        """迁移单个文件 - 增强版"""
        self.current_file_record = FileChangeRecord(
            file_path=str(file_path.relative_to(self.input_path)),
            file_type=file_path.suffix,
            total_lines=0
        )

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            self.current_file_record.total_lines = len(lines)
            original_lines = lines.copy()

            # 按行处理
            for i, line in enumerate(lines):
                self.line_number = i + 1
                new_line = line

                # 1. 转换导入语句
                for old_import, new_import in self.import_mappings.items():
                    if old_import in line:
                        new_line = new_line.replace(old_import, new_import)
                        self._add_change_record(
                            ChangeType.IMPORT,
                            line.strip(),
                            new_line.strip(),
                            f"导入语句转换: {old_import} -> {new_import}"
                        )
                        self.migration_report['summary']['imports_converted'] += 1

                # 2. 转换注解
                for hsf_annotation, (dubbo_annotation, change_type, desc) in self.annotation_mappings.items():
                    if hsf_annotation in line:
                        new_line = self._convert_annotation_with_attrs(line)
                        if new_line != line:
                            self._add_change_record(
                                change_type,
                                line.strip(),
                                new_line.strip(),
                                f"{desc}: {hsf_annotation} -> {dubbo_annotation}"
                            )
                            self.migration_report['summary']['annotations_converted'] += 1

                lines[i] = new_line

            content = ''.join(lines)
            modified = content != ''.join(original_lines)

            # 计算行数变化
            if modified:
                new_lines = content.split('\n')
                self.current_file_record.additions = len(new_lines)
                self.current_file_record.deletions = len(original_lines)

            change_summaries = [
                f"[{c.change_type}] {c.description}" for c in self.current_file_record.changes
            ]

            return content, modified, change_summaries, self.current_file_record

        except Exception as e:
            error_record = FileChangeRecord(
                file_path=str(file_path.relative_to(self.input_path)),
                file_type=file_path.suffix,
                total_lines=0
            )
            error_record.changes.append(ChangeRecord(
                change_type=ChangeType.UNKNOWN.value,
                original="",
                converted="",
                description=f"迁移错误: {str(e)}"
            ))
            return f"// 迁移错误: {str(e)}\n", False, [f"错误: {str(e)}"], error_record

    def migrate_pom_file(self, file_path: Path) -> Tuple[str, bool, List[str], FileChangeRecord]:
        """迁移 Maven POM 文件 - 增强版"""
        self.current_file_record = FileChangeRecord(
            file_path=str(file_path.relative_to(self.input_path)),
            file_type=".xml",
            total_lines=0
        )

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            change_summaries = []

            # 处理每个依赖
            for dep_key, dep_info in self.dependency_mappings.items():
                group_id, artifact_id = dep_key.split(':')

                # 构建依赖块匹配模式
                pattern = rf'<dependency>\s*<groupId>{re.escape(group_id)}</groupId>\s*<artifactId>{re.escape(artifact_id)}</artifactId>.*?</dependency>'

                match = re.search(pattern, content, re.DOTALL)
                if match:
                    original_dep = match.group(0)

                    if dep_info.get('removed'):
                        # 移除依赖
                        new_dep = f"<!-- 已移除: {artifact_id} -->\n        <!-- 原因: {dep_info['description']} -->"
                        content = content.replace(original_dep, new_dep)
                    else:
                        # 替换依赖
                        new_dep = f"""
        <dependency>
            <groupId>{dep_info['groupId']}</groupId>
            <artifactId>{dep_info['artifactId']}</artifactId>
            <version>{dep_info['version']}</version>
            <!-- 原: {group_id}:{artifact_id} -->
        </dependency>"""
                        content = content.replace(original_dep, new_dep)

                    self._add_change_record(
                        ChangeType.DEPENDENCY,
                        original_dep.strip(),
                        new_dep.strip(),
                        f"依赖迁移: {group_id}:{artifact_id} -> {dep_info['groupId']}:{dep_info['artifactId']}"
                    )
                    change_summaries.append(f"[dependency] {group_id}:{artifact_id} -> {dep_info['groupId']}:{dep_info['artifactId']}")
                    self.migration_report['summary']['dependencies_updated'] += 1

            # 添加 Dubbo3 必需依赖
            if 'dubbo-spring-boot-starter' not in content:
                dubbo_deps = '''
        <!-- Dubbo3 核心依赖 (新增) -->
        <dependency>
            <groupId>org.apache.dubbo</groupId>
            <artifactId>dubbo-spring-boot-starter</artifactId>
            <version>3.2.0</version>
        </dependency>
        <dependency>
            <groupId>org.apache.dubbo</groupId>
            <artifactId>dubbo-registry-nacos</artifactId>
            <version>3.2.0</version>
        </dependency>
'''
                content = content.replace('</dependencies>', f'{dubbo_deps}</dependencies>')
                self._add_change_record(
                    ChangeType.DEPENDENCY,
                    "",
                    dubbo_deps.strip(),
                    "新增 Dubbo3 核心依赖"
                )
                change_summaries.append("[dependency] 新增 Dubbo3 核心依赖")
                self.migration_report['summary']['dependencies_updated'] += 1

            modified = content != original_content

            return content, modified, change_summaries, self.current_file_record

        except Exception as e:
            error_record = FileChangeRecord(
                file_path=str(file_path.relative_to(self.input_path)),
                file_type=".xml",
                total_lines=0
            )
            return f"<!-- POM 迁移错误: {str(e)} -->", False, [f"错误: {str(e)}"], error_record

    def _generate_diff(self, original: str, converted: str) -> str:
        """生成统一格式的diff"""
        original_lines = original.splitlines(keepends=True)
        converted_lines = converted.splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            original_lines,
            converted_lines,
            fromfile='original',
            tofile='converted',
            lineterm=''
        ))

        return ''.join(diff)

    def process_directory(self) -> None:
        """处理整个目录"""
        self.output_path.mkdir(parents=True, exist_ok=True)

        java_files = list(self.input_path.rglob('*.java'))
        pom_files = list(self.input_path.rglob('pom.xml'))
        xml_files = list(self.input_path.rglob('*.xml'))
        properties_files = list(self.input_path.rglob('*.properties'))

        all_files = java_files + pom_files + xml_files + properties_files

        for file_path in all_files:
            rel_path = file_path.relative_to(self.input_path)
            output_file = self.output_path / rel_path
            output_file.parent.mkdir(parents=True, exist_ok=True)

            self.migration_report['summary']['files_processed'] += 1

            if file_path.suffix == '.java':
                content, modified, changes, file_record = self.migrate_file(file_path)
            elif file_path.name == 'pom.xml':
                content, modified, changes, file_record = self.migrate_pom_file(file_path)
            elif file_path.suffix == '.xml':
                content, modified, changes, file_record = self.migrate_file(file_path)
            elif file_path.suffix == '.properties':
                content, modified, changes, file_record = self.migrate_file(file_path)
            else:
                with open(file_path, 'rb') as f:
                    content = f.read()
                with open(output_file, 'wb') as f:
                    f.write(content)
                continue

            if isinstance(content, str):
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                with open(output_file, 'wb') as f:
                    f.write(content)

            if modified:
                self.migration_report['summary']['files_modified'] += 1
                self.migration_report['file_changes'].append(file_record.to_dict())
            else:
                self.migration_report['summary']['files_unchanged'] += 1
                self.migration_report['unchanged_files'].append(str(rel_path))

            self.migration_report['summary']['total_changes'] += len(changes)

        self._generate_report()

    def _generate_report(self) -> None:
        """生成增强的迁移报告"""
        # JSON 报告
        report_file = self.output_path / 'migration_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.migration_report, f, ensure_ascii=False, indent=2)

        # Markdown 详细报告
        md_report = self._generate_markdown_report()
        md_report_file = self.output_path / 'migration_report.md'
        with open(md_report_file, 'w', encoding='utf-8') as f:
            f.write(md_report)

        # 变更汇总CSV
        csv_report = self._generate_csv_report()
        csv_report_file = self.output_path / 'change_summary.csv'
        with open(csv_report_file, 'w', encoding='utf-8') as f:
            f.write(csv_report)

    def _generate_markdown_report(self) -> str:
        """生成 Markdown 格式的详细审核报告"""
        summary = self.migration_report['summary']
        timestamp = self.migration_report['migration_info']['timestamp']

        report = f"""# HSF 到 Dubbo3 迁移审核报告

> 生成时间: {timestamp}
> 源框架: HSF → 目标框架: Dubbo3

---

## 一、变更概要

### 1.1 统计概览

| 指标 | 数量 |
|:-----|-----:|
| 处理文件总数 | {summary['files_processed']} |
| 变更文件数 | {summary['files_modified']} |
| 未变更文件数 | {summary['files_unchanged']} |
| 变更记录总数 | {summary['total_changes']} |
| 注解转换数 | {summary['annotations_converted']} |
| 导入语句转换数 | {summary['imports_converted']} |
| 依赖更新数 | {summary['dependencies_updated']} |

### 1.2 变更类型分布

"""

        # 统计变更类型
        change_type_stats = {}
        for file_change in self.migration_report['file_changes']:
            for change in file_change['changes']:
                ct = change['change_type']
                change_type_stats[ct] = change_type_stats.get(ct, 0) + 1

        for ct, count in sorted(change_type_stats.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{ct}**: {count} 处变更\n"

        report += """
---

## 二、变更明细

"""

        if self.migration_report['file_changes']:
            for i, file_change in enumerate(self.migration_report['file_changes'], 1):
                report += f"""### 2.{i} {file_change['file_path']}

**文件类型**: `{file_change['file_type']}`
**变更数量**: {file_change['change_count']} 处

#### 变更详情

| 行号 | 类型 | 变更前 | 变更后 |
|:----:|:-----|:-------|:-------|
"""
                for change in file_change['changes']:
                    original = change['original'][:40] + ('...' if len(change['original']) > 40 else '')
                    converted = change['converted'][:40] + ('...' if len(change['converted']) > 40 else '')
                    report += f"| {change['line_number']} | {change['change_type']} | `{original}` | `{converted}` |\n"

                report += f"""
#### 变更描述

"""
                for change in file_change['changes']:
                    report += f"- {change['description']}\n"

                report += "\n---\n"

        report += """
## 三、未变更文件清单

"""
        if self.migration_report['unchanged_files']:
            for f in self.migration_report['unchanged_files']:
                report += f"- {f}\n"
        else:
            report += "无未变更文件。\n"

        report += """
---

## 四、审核检查项

### 4.1 代码完整性检查

- [ ] 所有 HSF 注解是否已正确转换为 Dubbo3 注解
- [ ] 导入语句是否完整，无遗漏
- [ ] 依赖配置是否正确添加

### 4.2 配置检查

- [ ] 注册中心地址是否配置（推荐使用 Nacos）
- [ ] 协议端口是否正确（默认 20880）
- [ ] 服务分组和版本是否一致

### 4.3 测试建议

1. **编译测试**: 执行 `mvn clean compile` 验证代码无误
2. **单元测试**: 运行项目单元测试确保功能正常
3. **集成测试**: 启动服务验证注册发现正常
4. **调用测试**: 测试服务间调用是否正常

---

## 五、后续操作建议

1. **代码审查**: 由研发人员Review所有变更
2. **配置补充**: 添加 Dubbo3 配置文件 `application-dubbo.yml`
3. **依赖检查**: 确认所有间接依赖兼容性
4. **灰度发布**: 建议先灰度部分服务验证
5. **监控告警**: 配置 Dubbo3 相关监控指标

---

## 六、附录

### 6.1 注解对照表

| HSF 注解 | Dubbo3 注解 |
|----------|-------------|
| @HSFProvider | @DubboService |
| @HSFConsumer | @DubboReference |
| @HSFService | @DubboService |
| @HSFReference | @DubboReference |

### 6.2 依赖对照表

| HSF 依赖 | Dubbo3 依赖 |
|----------|-------------|
| com.alibaba.boot:hsf-spring-boot-starter | org.apache.dubbo:dubbo-spring-boot-starter:3.2.0 |
| com.taobao.hsf:hsf | org.apache.dubbo:dubbo:3.2.0 |

---

*报告由 HSF to Dubbo3 Migration Tool 自动生成*
"""

        return report

    def _generate_csv_report(self) -> str:
        """生成 CSV 格式的变更汇总"""
        lines = ['文件路径,变更类型,行号,变更前,变更后,描述']

        for file_change in self.migration_report['file_changes']:
            for change in file_change['changes']:
                # CSV 转义
                original = change['original'].replace('"', '""')
                converted = change['converted'].replace('"', '""')
                description = change['description'].replace('"', '""')

                lines.append(
                    f'"{file_change["file_path"]}",'
                    f'"{change["change_type"]}",'
                    f'{change["line_number"]},'
                    f'"{original}",'
                    f'"{converted}",'
                    f'"{description}"'
                )

        return '\n'.join(lines)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='HSF 到 Dubbo3 框架迁移工具（增强版）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python migrate.py --input ./hsf-project --output ./dubbo3-project
  python migrate.py -i ./myapp -o ./migrated-app

生成报告:
  - migration_report.json  : JSON格式完整报告
  - migration_report.md     : Markdown格式审核报告
  - change_summary.csv      : CSV格式变更汇总
        """
    )

    parser.add_argument('--input', '-i', required=True, help='输入目录（HSF 项目路径）')
    parser.add_argument('--output', '-o', required=True, help='输出目录（Dubbo3 项目路径）')

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f"错误: 输入路径不存在: {args.input}")
        sys.exit(1)

    print("=" * 60)
    print("HSF 到 Dubbo3 框架迁移工具 (增强版)")
    print("=" * 60)
    print(f"\n输入目录: {args.input}")
    print(f"输出目录: {args.output}")
    print("-" * 60)

    migrator = HSFToDubbo3Migrator(args.input, args.output)
    migrator.process_directory()

    summary = migrator.migration_report['summary']

    print("\n" + "=" * 60)
    print("迁移完成!")
    print("=" * 60)
    print(f"\n[统计信息]")
    print(f"  处理文件: {summary['files_processed']}")
    print(f"  变更文件: {summary['files_modified']}")
    print(f"  注解转换: {summary['annotations_converted']}")
    print(f"  导入转换: {summary['imports_converted']}")
    print(f"  依赖更新: {summary['dependencies_updated']}")

    print(f"\n[生成报告]")
    print(f"  {args.output}/migration_report.json  - JSON完整报告")
    print(f"  {args.output}/migration_report.md    - Markdown审核报告")
    print(f"  {args.output}/change_summary.csv     - CSV变更汇总")
    print("\n请研发人员查阅报告进行代码审核。")


if __name__ == '__main__':
    main()
