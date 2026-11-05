#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python字节码分析与反混淆工具
用于分析、理解和反混淆Python字节码

功能:
- 字节码反汇编与可视化
- 控制流图(CFG)生成
- 关键操作码检测
- 反混淆模式识别
- 字节码指令流分析
"""

import dis
import marshal
import operator
import os
import sys
import types
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


# Python操作码分类
OPCODES = {
    # 加载
    'LOAD_GLOBAL': 'load',
    'LOAD_FAST': 'load',
    'LOAD_CONST': 'load',
    'LOAD_ATTR': 'load',
    'LOAD_METHOD': 'load',
    # 存储
    'STORE_GLOBAL': 'store',
    'STORE_FAST': 'store',
    'STORE_ATTR': 'store',
    # 函数调用
    'CALL_FUNCTION': 'call',
    'CALL_FUNCTION_KW': 'call',
    'CALL_METHOD': 'call',
    'CALL_FUNCTION_EX': 'call',
    # 栈操作
    'POP_TOP': 'stack',
    'DUP_TOP': 'stack',
    'DUP_TOP_TWO': 'stack',
    'ROT_TWO': 'stack',
    'ROT_THREE': 'stack',
    'ROT_FOUR': 'stack',
    # 二进制运算
    'BINARY_ADD': 'arithmetic',
    'BINARY_SUBTRACT': 'arithmetic',
    'BINARY_MULTIPLY': 'arithmetic',
    'BINARY_TRUE_DIVIDE': 'arithmetic',
    'BINARY_MODULO': 'arithmetic',
    'BINARY_POWER': 'arithmetic',
    # 比较
    'COMPARE_OP': 'compare',
    # 跳转
    'JUMP_FORWARD': 'jump',
    'JUMP_ABSOLUTE': 'jump',
    'POP_JUMP_IF_TRUE': 'jump',
    'POP_JUMP_IF_FALSE': 'jump',
    'JUMP_IF_TRUE_OR_POP': 'jump',
    'JUMP_IF_FALSE_OR_POP': 'jump',
    # 返回
    'RETURN_VALUE': 'return',
    # 异常
    'RAISE_VARARGS': 'exception',
    'SETUP_FINALLY': 'exception',
    'END_FINALLY': 'exception',
    # Import
    'IMPORT_NAME': 'import',
    'IMPORT_FROM': 'import',
    'IMPORT_STAR': 'import',
}


@dataclass
class BytecodeInstruction:
    """字节码指令"""
    offset: int
    opcode: int
    opname: str
    arg: Optional[int] = None
    argval: Optional[Any] = None
    argrepr: str = ""
    category: str = ""


@dataclass
class BasicBlock:
    """基本块"""
    start: int
    end: int
    instructions: List[BytecodeInstruction] = field(default_factory=list)
    predecessors: List[int] = field(default_factory=list)
    successors: List[int] = field(default_factory=list)
    is_entry: bool = False
    is_loop: bool = False
    is_branch: bool = False


class BytecodeAnalyzer:
    """字节码分析器"""

    def __init__(self, source: Any = None):
        self.source = source
        self.code: Optional[types.CodeType] = None
        self.instructions: List[BytecodeInstruction] = []
        self.basic_blocks: List[BasicBlock] = []
        self.cfg: Dict[int, Set[int]] = defaultdict(set)
        self.constant_pool: Dict[int, Any] = {}
        self.name_pool: List[str] = []
        self.varname_pool: List[str] = []
        self.freevars: List[str] = []
        self.cellvars: List[str] = []
        self.opcode_counts: Dict[str, int] = defaultdict(int)

    def load_source(self, source: Any):
        """加载源码或代码对象"""
        if isinstance(source, (str, Path)):
            source = open(source).read()
            self.code = compile(source, '<string>', 'exec')
        elif isinstance(source, types.CodeType):
            self.code = source
        elif callable(source):
            self.code = source.__code__
        else:
            self.code = source

        if not isinstance(self.code, types.CodeType):
            raise ValueError("Invalid source type")

        self._parse_pools()

    def _parse_pools(self):
        """解析常量池和名称池"""
        self.constant_pool = {i: c for i, c in enumerate(self.code.co_consts)}
        self.name_pool = list(self.code.co_names)
        self.varname_pool = list(self.code.co_varnames)
        self.freevars = list(self.code.co_freevars)
        self.cellvars = list(self.code.co_cellvars)

    def disassemble(self) -> List[BytecodeInstruction]:
        """反汇编字节码"""
        if self.code is None:
            raise ValueError("No code loaded")

        self.instructions = []

        for instr in dis.get_instructions(self.code):
            bi = BytecodeInstruction(
                offset=instr.offset,
                opcode=instr.opcode,
                opname=instr.opname,
                arg=instr.arg,
                argval=instr.argval,
                argrepr=instr.argrepr,
                category=OPCODES.get(instr.opname, 'unknown')
            )
            self.instructions.append(bi)
            self.opcode_counts[instr.opname] += 1

        return self.instructions

    def get_formatted_disassembly(self) -> str:
        """获取格式化的反汇编输出"""
        output = BytesIO()
        dis.dis(self.code, file=output)
        return output.getvalue().decode('utf-8', errors='replace')

    def build_cfg(self) -> Dict[int, Set[int]]:
        """构建控制流图"""
        if not self.instructions:
            self.disassemble()

        self.basic_blocks = []
        self.cfg = defaultdict(set)

        # 识别跳转目标
        jump_targets = set()
        for instr in self.instructions:
            if instr.opname in ('JUMP_FORWARD', 'JUMP_ABSOLUTE',
                                 'POP_JUMP_IF_TRUE', 'POP_JUMP_IF_FALSE',
                                 'JUMP_IF_TRUE_OR_POP', 'JUMP_IF_FALSE_OR_POP'):
                if instr.argval is not None:
                    jump_targets.add(instr.argval)

        # 识别异常处理
        for instr in self.instructions:
            if instr.opname == 'SETUP_FINALLY':
                if instr.argval is not None:
                    jump_targets.add(instr.argval)

        # 构建基本块
        current_block = BasicBlock(start=0, is_entry=True)

        for instr in self.instructions:
            if instr.offset in jump_targets and current_block.instructions:
                # 新块开始
                current_block.end = self.instructions[self.instructions.index(
                    current_block.instructions[-1]) - 1].offset if current_block.instructions else 0
                self.basic_blocks.append(current_block)
                current_block = BasicBlock(start=instr.offset)
                current_block.is_entry = True

            current_block.instructions.append(instr)

            # 检查跳转指令
            if instr.opname in ('JUMP_FORWARD', 'JUMP_ABSOLUTE'):
                if instr.argval is not None:
                    jump_targets.add(instr.argval)
                    self.cfg[instr.offset].add(instr.argval)

            elif instr.opname in ('POP_JUMP_IF_TRUE', 'POP_JUMP_IF_FALSE'):
                if instr.argval is not None:
                    self.cfg[instr.offset].add(instr.argval)
                    current_block.is_branch = True

            elif instr.opname in ('JUMP_IF_TRUE_OR_POP', 'JUMP_IF_FALSE_OR_POP'):
                if instr.argval is not None:
                    self.cfg[instr.offset].add(instr.argval)

            # Fall-through
            if instr.offset in jump_targets or instr.opname == 'RETURN_VALUE':
                pass  # 将在后面处理

        # 添加最后一个块
        if current_block.instructions:
            current_block.end = current_block.instructions[-1].offset
            self.basic_blocks.append(current_block)

        # 处理fall-through
        for i, block in enumerate(self.basic_blocks[:-1]):
            if block.instructions:
                last_instr = block.instructions[-1]
                if last_instr.opname not in ('JUMP_FORWARD', 'JUMP_ABSOLUTE',
                                               'RETURN_VALUE', 'RAISE_VARARGS'):
                    next_block = self.basic_blocks[i + 1]
                    self.cfg[last_instr.offset].add(next_block.start)

        return dict(self.cfg)

    def detect_obfuscation_patterns(self) -> Dict[str, List[str]]:
        """检测混淆模式"""
        if not self.instructions:
            self.disassemble()

        patterns = {
            'dead_code': [],
        }

        # 检测NOP序列（死代码）
        nop_count = 0
        for instr in self.instructions:
            if instr.opname == 'NOP':
                nop_count += 1
            else:
                if nop_count > 3:
                    patterns['dead_code'].append(
                        f"Found {nop_count} consecutive NOPs"
                    )
                nop_count = 0

        # 检测loader模式 (LOAD_CONST + CALL_FUNCTION)
        loader_patterns = []
        for i in range(len(self.instructions) - 1):
            if self.instructions[i].opname == 'LOAD_CONST' and \
               self.instructions[i + 1].opname == 'CALL_FUNCTION':
                loader_patterns.append(f"Loader at offset {self.instructions[i].offset}")

        if loader_patterns:
            patterns['loader'] = loader_patterns

        # 检测字符串拼接（动态代码构建）
        string_build = []
        for i in range(len(self.instructions) - 4):
            ops = [self.instructions[i + j].opname for j in range(5)]
            if ops == ['LOAD_CONST', 'LOAD_CONST', 'BINARY_ADD',
                       'STORE_FAST', 'LOAD_FAST']:
                string_build.append(f"String build at offset {self.instructions[i].offset}")

        if string_build:
            patterns['string_build'] = string_build

        # 检测exec/eval模式
        for i, instr in enumerate(self.instructions):
            if instr.opname == 'LOAD_GLOBAL' and instr.argval in ('exec', 'eval', 'compile'):
                patterns.setdefault('dynamic_exec', []).append(
                    f"Dynamic {instr.argval} at offset {instr.offset}"
                )

        return patterns

    def analyze_function_calls(self) -> List[Dict]:
        """分析函数调用"""
        calls = []

        for i, instr in enumerate(self.instructions):
            if instr.opname in ('CALL_FUNCTION', 'CALL_FUNCTION_KW', 'CALL_METHOD',
                                 'CALL_FUNCTION_EX'):
                call_info = {
                    'offset': instr.offset,
                    'type': instr.opname,
                    'arg_count': instr.arg if instr.arg else 0,
                }

                # 尝试识别调用目标
                if i > 0:
                    prev = self.instructions[i - 1]
                    if prev.opname == 'LOAD_GLOBAL':
                        call_info['target'] = prev.argval
                    elif prev.opname == 'LOAD_METHOD':
                        call_info['method'] = prev.argval

                calls.append(call_info)

        return calls

    def detect_imports(self) -> List[str]:
        """检测导入语句"""
        imports = []

        for i, instr in enumerate(self.instructions):
            if instr.opname == 'IMPORT_NAME':
                if i > 0 and self.instructions[i - 1].opname == 'LOAD_CONST':
                    module = self.instructions[i - 1].argval
                    if isinstance(module, str):
                        imports.append(module)

        return imports

    def extract_strings(self) -> List[Tuple[str, int]]:
        """从字节码中提取字符串常量"""
        strings = []

        for instr in self.instructions:
            if instr.opname == 'LOAD_CONST' and instr.argval is not None:
                if isinstance(instr.argval, str):
                    strings.append((instr.argval, instr.offset))

        return strings

    def generate_report(self) -> str:
        """生成分析报告"""
        if not self.instructions:
            self.disassemble()

        report = []
        report.append("=" * 70)
        report.append("PYTHON BYTECODE ANALYSIS REPORT")
        report.append("=" * 70)

        # 基本信息
        report.append("\n--- Code Information ---")
        report.append(f"Filename: {getattr(self.code, 'co_filename', 'unknown')}")
        report.append(f"Name: {getattr(self.code, 'co_name', 'unknown')}")
        report.append(f"First Line: {getattr(self.code, 'co_firstlineno', 'unknown')}")
        report.append(f"Arguments: {getattr(self.code, 'co_argcount', 0)}")
        report.append(f"Local Variables: {len(self.varname_pool)}")
        report.append(f"Constants: {len(self.constant_pool)}")
        report.append(f"Names: {len(self.name_pool)}")

        # 操作码统计
        report.append("\n--- Opcode Statistics ---")
        for opname, count in sorted(self.opcode_counts.items(),
                                     key=lambda x: -x[1])[:15]:
            report.append(f"  {opname:20s}: {count:5d}")

        # 检测到的模式
        patterns = self.detect_obfuscation_patterns()
        if any(patterns.values()):
            report.append("\n--- Obfuscation Patterns Detected ---")
            for pattern_name, instances in patterns.items():
                if instances:
                    report.append(f"\n  [{pattern_name.upper()}]")
                    for instance in instances[:5]:  # 最多显示5个
                        report.append(f"    {instance}")

        # 导入检测
        imports = self.detect_imports()
        if imports:
            report.append("\n--- Imports ---")
            for module in imports:
                report.append(f"  {module}")

        # 字符串常量
        strings = self.extract_strings()
        if strings:
            report.append(f"\n--- String Constants ({len(strings)} found) ---")
            for s, offset in strings[:20]:  # 显示前20个
                if len(s) > 50:
                    s = s[:50] + "..."
                report.append(f"  [{offset:4d}] {repr(s)}")

        # 函数调用
        calls = self.analyze_function_calls()
        if calls:
            report.append(f"\n--- Function Calls ({len(calls)} found) ---")
            for call in calls[:10]:
                target = call.get('target', call.get('method', 'unknown'))
                report.append(f"  [{call['offset']:4d}] {call['type']} {target}")

        report.append("\n" + "=" * 70)

        return "\n".join(report)

    def export_cfg_dot(self) -> str:
        """导出DOT格式的控制流图"""
        if not self.basic_blocks:
            self.build_cfg()

        lines = ['digraph CFG {']
        lines.append('    rankdir=TB;')

        for block in self.basic_blocks:
            block_id = f"B{block.start}"
            label = f"Block_{block.start}\\n"

            # 简化指令显示
            for instr in block.instructions[:5]:
                label += f"{instr.opname}\\n"

            lines.append(f'    {block_id} [label="{label}" shape=box];')

        for block in self.basic_blocks:
            block_id = f"B{block.start}"
            if block.instructions:
                last = block.instructions[-1]
                if last.offset in self.cfg:
                    for target in self.cfg[last.offset]:
                        lines.append(f'    {block_id} -> B{target};')

        lines.append('}')
        return "\n".join(lines)


def analyze_code(source: Any) -> BytecodeAnalyzer:
    """分析代码的便捷函数"""
    analyzer = BytecodeAnalyzer()
    analyzer.load_source(source)
    analyzer.disassemble()
    return analyzer


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: python bytecode_analyzer.py <source_file_or_code> [--cfg]")
        print("")
        print("Options:")
        print("  --cfg        Generate control flow graph in DOT format")
        print("  --dis        Show disassembly")
        print("  --strings    Extract strings only")
        sys.exit(1)

    source_path = sys.argv[1]
    options = {
        'cfg': '--cfg' in sys.argv,
        'dis': '--dis' in sys.argv,
        'strings': '--strings' in sys.argv,
    }

    # 加载源码
    if os.path.isfile(source_path):
        with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = compile(f.read(), source_path, 'exec')
    else:
        code = compile(source_path, '<string>', 'exec')

    # 分析
    analyzer = BytecodeAnalyzer()
    analyzer.load_source(code)

    if options['strings']:
        print("--- Extracted Strings ---")
        for s, offset in analyzer.extract_strings():
            print(f"[{offset:4d}] {repr(s)}")
    elif options['cfg']:
        analyzer.disassemble()
        analyzer.build_cfg()
        print(analyzer.export_cfg_dot())
    else:
        analyzer.disassemble()
        print(analyzer.generate_report())


if __name__ == '__main__':
    main()
