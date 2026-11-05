#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyperion Python混淆器 解混淆工具

Hyperion是一个多层Python混淆器,主要特点:
1. 字符串加密 (替换为函数调用)
2. 变量名混淆
3. 代码结构混淆
4. 多层嵌套加密壳

本工具用于还原被Hyperion混淆的代码
"""

import ast
import base64
import builtins
import dis
import marshal
import os
import re
import sys
import types
import zlib
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union


class HyperionDeobfuscator:
    """Hyperion混淆代码还原器"""

    def __init__(self):
        self.layers: List[Dict] = []
        self.decoded_strings: Dict[str, str] = {}
        self.reconstructed_code: List[str] = []
        self.execution_log: List[str] = []

    def log(self, message: str):
        """添加日志"""
        self.execution_log.append(message)
        print(f"[*] {message}")

    def info(self, message: str):
        """添加信息"""
        print(f"[+] {message}")

    def error(self, message: str):
        """添加错误"""
        print(f"[-] {message}")

    def detect_hyperion(self, code: str) -> bool:
        """检测是否是Hyperion混淆的代码"""
        # Hyperion特征
        patterns = [
            r'__obfuscator__\s*=\s*[\'"]Hyperion[\'"]',
            r'__authors__\s*=',
            r'from\s+builtins\s+import\s+\*',
            r'from\s+math\s+import\s+\w+\s+as\s+\w+',
            r'__import__\s*\(\s*[\'"]base64[\'"]',
            r'Eval\s*=\s*exec',
        ]

        matches = sum(1 for p in patterns if re.search(p, code, re.IGNORECASE))
        return matches >= 2

    def extract_layers(self, code: str) -> List[str]:
        """提取混淆的代码层次"""
        layers = []

        # 查找所有字符串常量
        strings = re.findall(r'"""([\s\S]*?)"""|\'\'\'([\s\S]*?)\'\'\'', code)

        for s in strings:
            if isinstance(s, tuple):
                s = ''.join(s)
            if s and len(s) > 50:  # 长字符串可能是编码数据
                layers.append(s)

        return layers

    def try_decode_layer(self, data: Union[str, bytes]) -> Optional[bytes]:
        """尝试解码一层"""
        if isinstance(data, str):
            data = data.encode('latin-1')

        # 尝试base64
        try:
            decoded = base64.b64decode(data)
            if self.is_valid_layer(decoded):
                return decoded
        except Exception:
            pass

        # 尝试base85
        try:
            decoded = base64.b85decode(data)
            if self.is_valid_layer(decoded):
                return decoded
        except Exception:
            pass

        # 尝试zlib
        try:
            decoded = zlib.decompress(data)
            if self.is_valid_layer(decoded):
                return decoded
        except Exception:
            pass

        # 尝试hex
        try:
            if isinstance(data, bytes):
                decoded = bytes.fromhex(data.decode('ascii', errors='ignore'))
                if self.is_valid_layer(decoded):
                    return decoded
        except Exception:
            pass

        return None

    def is_valid_layer(self, data: bytes) -> bool:
        """检查是否是有效的代码层"""
        if len(data) < 10:
            return False

        # 检查是否是marshal数据
        try:
            obj = marshal.loads(data)
            if isinstance(obj, (types.CodeType, list, tuple)):
                return True
        except Exception:
            pass

        # 检查magic number
        magic_numbers = [
            b'\x33\x0d\x0d\x0a', b'\x42\x0d\x0d\x0a',
            b'\x55\x0d\x0d\x0a', b'\x61\x0d\x0d\x0a',
        ]

        for magic in magic_numbers:
            if data.startswith(magic):
                return True

        return False

    def decode_all_layers(self, code: str) -> Optional[bytes]:
        """解码所有混淆层"""
        self.log("Starting multi-layer decoding...")

        # 首先提取可能的编码数据
        encoded_parts = self._extract_encoded_parts(code)

        if not encoded_parts:
            self.log("No encoded parts found")
            return None

        best_result = None
        best_layer_count = 0

        for part in encoded_parts:
            current = part
            layer_count = 0

            while layer_count < 15:  # 最多15层
                decoded = self.try_decode_layer(current)
                if decoded is None:
                    break

                current = decoded
                layer_count += 1
                self.log(f"Layer {layer_count} decoded: {len(decoded)} bytes")

            if layer_count > best_layer_count:
                best_layer_count = layer_count
                best_result = current

        if best_result:
            self.info(f"Successfully decoded {best_layer_count} layers")

        return best_result

    def _extract_encoded_parts(self, code: str) -> List[Union[str, bytes]]:
        """提取编码的部分"""
        parts = []

        # 查找base64编码的字符串
        b64_pattern = r'(?:b64decode|b85decode)\s*\(\s*["\']([A-Za-z0-9+/=\s]+)["\']'
        for match in re.finditer(b64_pattern, code):
            parts.append(match.group(1).strip())

        # 查找__import__模式
        import_pattern = r'__import__\s*\(\s*["\']([^"\']+)["\']\s*\)\.(\w+)\s*\(\s*(.+?)\s*\)'
        for match in re.finditer(import_pattern, code, re.DOTALL):
            data = match.group(3)
            if data.startswith(('"', "'")):
                parts.append(data.strip('"\''))

        # 查找长字符串
        long_strings = re.findall(r'["\']([A-Za-z0-9+/=]{100,})["\']', code)
        parts.extend(long_strings)

        # 查找exec/eval参数
        exec_pattern = r'(?:exec|eval|compile)\s*\(\s*(.+?)\s*\)'
        for match in re.finditer(exec_pattern, code, re.DOTALL):
            arg = match.group(1).strip()
            if len(arg) > 50:
                parts.append(arg)

        return parts

    def extract_bytecode_strings(self, bytecode: bytes) -> List[str]:
        """从字节码中提取字符串"""
        strings = []

        try:
            # 如果是marshal数据
            code_obj = marshal.loads(bytecode)
            strings.extend(self._extract_from_code(code_obj))
        except Exception:
            pass

        # 如果是pyc文件
        if len(bytecode) > 16:
            try:
                # 尝试作为marshal解析
                marshal_data = bytecode[16:]
                code_obj = marshal.loads(marshal_data)
                strings.extend(self._extract_from_code(code_obj))
            except Exception:
                pass

        return strings

    def _extract_from_code(self, code: types.CodeType) -> List[str]:
        """从代码对象中提取字符串"""
        strings = []

        for const in code.co_consts:
            if isinstance(const, str):
                strings.append(const)
            elif isinstance(const, bytes):
                # 尝试解码bytes
                try:
                    decoded = const.decode('utf-8')
                    strings.append(decoded)
                except Exception:
                    pass

        # 递归处理子代码
        for const in code.co_consts:
            if isinstance(const, types.CodeType):
                strings.extend(self._extract_from_code(const))

        return strings

    def reconstruct_code(self, bytecode: bytes) -> Optional[str]:
        """重构Python代码"""
        try:
            code_obj = marshal.loads(bytecode)

            if not isinstance(code_obj, types.CodeType):
                self.error("Decoded data is not valid bytecode")
                return None

            # 使用dis模块生成反汇编
            output = BytesIO()
            dis.dis(code_obj, file=output)

            return output.getvalue().decode('utf-8', errors='replace')

        except Exception as e:
            self.error(f"Code reconstruction failed: {e}")
            return None

    def deobfuscate(self, code: str) -> Dict[str, Any]:
        """主反混淆函数"""
        results = {
            'is_hyperion': False,
            'layers_decoded': 0,
            'decoded_code': None,
            'bytecode_output': None,
            'strings_extracted': [],
            'success': False,
            'warnings': [],
            'log': []
        }

        self.log("Starting Hyperion deobfuscation...")

        # 检测是否是Hyperion
        results['is_hyperion'] = self.detect_hyperion(code)
        if results['is_hyperion']:
            self.info("Hyperion obfuscation detected")
        else:
            self.log("Code may not be Hyperion, attempting generic deobfuscation")

        # 解码层
        decoded_bytes = self.decode_all_layers(code)

        if decoded_bytes:
            results['bytecode_output'] = decoded_bytes
            results['strings_extracted'] = self.extract_bytecode_strings(decoded_bytes)

            # 尝试重构代码
            reconstructed = self.reconstruct_code(decoded_bytes)
            if reconstructed:
                results['decoded_code'] = reconstructed
                results['success'] = True

        # 检查是否有__obfuscator__标记
        if '__obfuscator__' in code:
            match = re.search(r"__obfuscator__\s*=\s*[\"']([^\"']+)[\"']", code)
            if match:
                self.info(f"Obfuscator: {match.group(1)}")

        results['log'] = self.execution_log
        return results


class HyperionBytecodeAnalyzer:
    """Hyperion字节码分析器"""

    def __init__(self):
        self.obfuscated_names: Dict[str, str] = {}
        self.decrypted_strings: List[str] = []

    def analyze_bytecode(self, bytecode: bytes) -> Dict[str, Any]:
        """分析混淆的字节码"""
        results = {
            'magic': None,
            'python_version': None,
            'code_objects': [],
            'string_constants': [],
            'name_constants': [],
        }

        # 检测Python版本
        if len(bytecode) >= 4:
            magic = bytecode[:4]
            results['magic'] = magic.hex()

            version_map = {
                b'\x33\x0d\x0d\x0a': '3.11+',
                b'\x42\x0d\x0d\x0a': '3.10',
                b'\x55\x0d\x0d\x0a': '3.9',
                b'\x61\x0d\x0d\x0a': '3.8',
                b'\x42\x13\x0d\x0a': '3.7',
                b'\x6f\x0d\x0d\x0a': '3.6',
            }

            results['python_version'] = version_map.get(magic, 'unknown')

        # 尝试解析marshal数据
        try:
            if len(bytecode) > 16:
                code_obj = marshal.loads(bytecode[16:])
            else:
                code_obj = marshal.loads(bytecode)

            if isinstance(code_obj, types.CodeType):
                self._analyze_code_object(code_obj, results)

        except Exception as e:
            print(f"Parse error: {e}")

        return results

    def _analyze_code_object(self, code: types.CodeType, results: Dict):
        """分析代码对象"""
        # 收集字符串常量
        for const in code.co_consts:
            if isinstance(const, str) and len(const) > 0:
                results['string_constants'].append(const)

        # 收集名称
        results['name_constants'].extend(code.co_names)

        # 递归分析子代码
        for const in code.co_consts:
            if isinstance(const, types.CodeType):
                self._analyze_code_object(const, results)


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: python hyperion_deobfuscator.py <file_or_code>")
        print("")
        print("Options:")
        print("  --analyze     Only analyze without deobfuscating")
        print("  --verbose     Verbose output")
        sys.exit(1)

    input_path = sys.argv[1]

    # 读取输入
    if os.path.isfile(input_path):
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
    else:
        code = input_path

    # Hyperion检测
    deobfuscator = HyperionDeobfuscator()

    print("=" * 70)
    print("HYPERION DEOBFUSCATOR")
    print("=" * 70)

    # 检测
    if deobfuscator.detect_hyperion(code):
        print("\n[+] Hyperion obfuscation signature detected!")
    else:
        print("\n[*] No explicit Hyperion signature, attempting generic analysis...")

    # 反混淆
    results = deobfuscator.deobfuscate(code)

    print("\n--- Results ---")
    print(f"Hyperion detected: {results['is_hyperion']}")
    print(f"Success: {results['success']}")

    if results['strings_extracted']:
        print(f"\nStrings extracted: {len(results['strings_extracted'])}")
        for s in results['strings_extracted'][:10]:
            if len(s) < 100:
                print(f"  - {repr(s)}")

    if results['bytecode_output']:
        print(f"\nBytecode decoded: {len(results['bytecode_output'])} bytes")

        if '--analyze' not in sys.argv:
            # 保存字节码
            output_path = input_path + '.decoded.pyc'
            if os.path.isfile(input_path):
                output_path = os.path.splitext(input_path)[0] + '_decoded.pyc'

            with open(output_path, 'wb') as f:
                f.write(results['bytecode_output'])

            print(f"Saved decoded bytecode to: {output_path}")

    if results['decoded_code']:
        print("\n--- Disassembled Code ---")
        print(results['decoded_code'][:2000])  # 显示前2000字符
        if len(results['decoded_code']) > 2000:
            print("\n... (truncated)")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
