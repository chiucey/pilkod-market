#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Exec加密代码解码器
用于自动识别和解码exec加密的Python代码

支持模式:
- base64.b64decode/b85decode/a85decode
- marshal.loads
- zlib.decompress/gzip/decompress
- hex decoding
- 多层嵌套加密壳
- exec/eval动态执行
"""

import ast
import base64
import builtins
import inspect
import marshal
import mmap
import os
import re
import sys
import types
import zlib
from io import BytesIO
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


class ExecDecryptor:
    """Exec加密代码解码器"""

    def __init__(self):
        self.decoded_blocks: List[Tuple[str, Any]] = []
        self.layer_count = 0
        self.execution_log: List[str] = []

    def add_log(self, message: str):
        """添加执行日志"""
        self.execution_log.append(message)
        print(f"[*] {message}")

    def detect_encoding(self, code: str) -> Optional[str]:
        """检测加密编码类型"""
        patterns = {
            'base64': [
                r'(?:base64\.)?(?:b64decode|b85decode|a85decode)\s*\(',
                r'__import__\s*\(\s*[\'"]base64[\'"]\s*\)\.b64decode',
                r'(?:decode|decrypt)\s*\(\s*[\'"]base64[\'"]\s*\)',
            ],
            'marshal': [
                r'(?:marshal\.)?loads\s*\(',
                r'__import__\s*\(\s*[\'"]marshal[\'"]\s*\)\.loads',
                r'\.loads\s*\(',
            ],
            'zlib': [
                r'(?:zlib|gzip|decompress)\s*\(',
                r'__import__\s*\(\s*[\'"]zlib[\'"]\s*\)\.decompress',
            ],
            'hex': [
                r'(?:bytes\.fromhex|hex\.decode|\.fromhex)\s*\(',
                r'int\s*\([^)]*16[^)]*\)\.to_bytes',
            ],
            'exec': [
                r'exec\s*\(',
                r'eval\s*\(',
                r'compile\s*\(',
            ],
        }

        for encoding, patterns_list in patterns.items():
            for pattern in patterns_list:
                if re.search(pattern, code, re.IGNORECASE):
                    return encoding
        return None

    def extract_encoded_strings(self, code: str) -> List[str]:
        """从代码中提取编码的字符串"""
        strings = []

        # 匹配三引号字符串
        triple_quote_pattern = r'"""([\s\S]*?)"""'
        strings.extend(re.findall(triple_quote_pattern, code))

        # 匹配单引号字符串
        single_quote_pattern = r"'''([\s\S]*?)'''"
        strings.extend(re.findall(single_quote_pattern, code))

        # 匹配普通字符串
        string_pattern = r'["\']([^"\']+)["\']'
        for match in re.finditer(string_pattern, code):
            s = match.group(1)
            if len(s) > 10 and not s.startswith('__'):  # 过滤短字符串
                strings.append(s)

        return strings

    def try_base64_decode(self, data: Union[str, bytes]) -> Optional[bytes]:
        """尝试base64解码"""
        try:
            if isinstance(data, str):
                data = data.encode('latin-1')
            return base64.b64decode(data)
        except Exception:
            try:
                return base64.b85decode(data)
            except Exception:
                try:
                    return base64.a85decode(data)
                except Exception:
                    return None

    def try_marshal_loads(self, data: bytes) -> Optional[types.CodeType]:
        """尝试marshal.loads"""
        try:
            return marshal.loads(data)
        except Exception:
            return None

    def try_zlib_decompress(self, data: bytes) -> Optional[bytes]:
        """尝试zlib解压"""
        methods = [
            zlib.decompress,
            lambda d: zlib.decompress(d, -zlib.MAX_WBITS),
            lambda d: zlib.decompress(d, 16 + zlib.MAX_WBITS),
        ]
        for method in methods:
            try:
                return method(data)
            except Exception:
                continue
        return None

    def try_hex_decode(self, data: str) -> Optional[bytes]:
        """尝试hex解码"""
        try:
            # 移除空白字符
            cleaned = re.sub(r'\s', '', data)
            # 尝试直接hex解码
            return bytes.fromhex(cleaned)
        except Exception:
            try:
                # 尝试通过int转换
                int_val = int(data, 16)
                return int_val.to_bytes((int_val.bit_length() + 7) // 8, 'big')
            except Exception:
                return None

    def decode_layer(self, data: Union[str, bytes], depth: int = 0) -> Optional[bytes]:
        """递归解码一层加密"""
        if depth > 20:  # 防止无限递归
            return None

        result = data

        # 尝试各种解码方法
        if isinstance(result, str):
            result = result.encode('latin-1')

        # 尝试base64
        decoded = self.try_base64_decode(result)
        if decoded:
            self.add_log(f"Layer {depth}: base64 decode successful, {len(decoded)} bytes")
            return decoded

        # 尝试hex
        if isinstance(data, str):
            decoded = self.try_hex_decode(data)
            if decoded:
                self.add_log(f"Layer {depth}: hex decode successful, {len(decoded)} bytes")
                return decoded

        # 尝试zlib
        decoded = self.try_zlib_decompress(result)
        if decoded:
            self.add_log(f"Layer {depth}: zlib decompress successful, {len(decoded)} bytes")
            return decoded

        # 尝试marshal
        code_obj = self.try_marshal_loads(result)
        if code_obj:
            self.add_log(f"Layer {depth}: marshal loads successful (found code object)")
            return result  # 返回原始bytes供后续处理

        return None

    def try_decode_multiple_layers(self, data: Union[str, bytes]) -> Optional[bytes]:
        """尝试多层解码"""
        current = data
        max_layers = 20

        for i in range(max_layers):
            decoded = self.decode_layer(current, i)
            if decoded is None:
                # 检查当前数据是否是有效的Python字节码或代码
                if isinstance(current, bytes):
                    if self.is_valid_bytecode(current):
                        self.add_log(f"Valid Python bytecode found at layer {i}")
                        return current
                    elif self.is_valid_pyc(current):
                        self.add_log(f"Valid .pyc file found at layer {i}")
                        return self.extract_code_from_pyc(current)
                break
            current = decoded

        return current if isinstance(current, bytes) else None

    def is_valid_bytecode(self, data: bytes) -> bool:
        """检查是否是有效的Python字节码"""
        if len(data) < 4:
            return False

        try:
            # 尝试作为marshal数据加载
            obj = marshal.loads(data)
            return isinstance(obj, (types.CodeType, list, tuple))
        except Exception:
            pass

        # 检查字节码魔数
        magic_patterns = [
            b'\x33\x0d\x0d\x0a',  # Python 3.11+
            b'\x42\x0d\x0d\x0a',  # Python 3.10
            b'\x55\x0d\x0d\x0a',  # Python 3.9
            b'\x61\x0d\x0d\x0a',  # Python 3.8
            b'\x42\x13\x0d\x0a',  # Python 3.7
        ]

        for magic in magic_patterns:
            if data.startswith(magic):
                return True

        # 检查是否为有效字节码序列
        try:
            import dis
            code = marshal.loads(data)
            if isinstance(code, types.CodeType):
                return True
        except Exception:
            pass

        return False

    def is_valid_pyc(self, data: bytes) -> bool:
        """检查是否是有效的.pyc文件"""
        if len(data) < 16:
            return False

        magic_numbers = [
            b'\x33\x0d\x0d\x0a',  # Python 3.11+
            b'\x42\x0d\x0d\x0a',  # Python 3.10
            b'\x55\x0d\x0d\x0a',  # Python 3.9
            b'\x61\x0d\x0d\x0a',  # Python 3.8
            b'\x42\x13\x0d\x0a',  # Python 3.7
            b'\x6f\x0d\x0d\x0a',  # Python 3.6
            b'\x03\xf3\x0d\x0a',  # Python 3.5
        ]

        for magic in magic_numbers:
            if data.startswith(magic):
                return True

        return False

    def extract_code_from_pyc(self, pyc_data: bytes) -> Optional[bytes]:
        """从.pyc文件中提取代码对象"""
        if not self.is_valid_pyc(pyc_data):
            return None

        try:
            # Python 3.6+: 16字节头部
            # Python 3.7+: 16字节头部(magic + flags + timestamp/timezone)
            # Python 3.11+: 16字节头部(magic + bit_field + timestamp + size)

            # 尝试解析marshal数据
            if len(pyc_data) > 16:
                marshal_data = pyc_data[16:]
                code_obj = marshal.loads(marshal_data)
                if isinstance(code_obj, types.CodeType):
                    return marshal.dumps(code_obj)
        except Exception as e:
            self.add_log(f"Failed to extract code from .pyc: {e}")

        return None

    def execute_and_capture(self, code: str, context: Optional[Dict] = None) -> Optional[str]:
        """在受控环境下执行代码并捕获输出"""
        if context is None:
            context = {}

        # 创建自定义globals/locals
        safe_globals = {
            '__builtins__': builtins.__dict__,
            '__name__': '__deobfuscator__',
            '__doc__': None,
        }
        safe_globals.update(context)

        # 用于捕获exec结果的类
        class CaptureStdout:
            def __init__(self):
                self.output = BytesIO()

            def write(self, text):
                self.output.write(text.encode() if isinstance(text, str) else text)

            def getvalue(self):
                return self.output.getvalue().decode('utf-8', errors='replace')

        captured = CaptureStdout()

        try:
            # 尝试提取代码字符串
            exec_code = code

            # 替换常见的导入模式
            exec_code = re.sub(
                r"__import__\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
                r"__import__('\\1')",
                exec_code
            )

            # 执行
            old_stdout = sys.stdout
            sys.stdout = captured
            try:
                exec(exec_code, safe_globals)
            finally:
                sys.stdout = old_stdout

            result = captured.getvalue()
            if result:
                return result

        except Exception as e:
            self.add_log(f"Execute error: {type(e).__name__}: {e}")

        return None

    def analyze_and_decode(self, code: str) -> Dict[str, Any]:
        """分析并解码代码"""
        results = {
            'encoding_detected': self.detect_encoding(code),
            'decoded_content': None,
            'decoded_code': None,
            'execution_log': [],
            'success': False,
        }

        self.add_log(f"Detected encoding: {results['encoding_detected']}")

        # 提取编码字符串
        encoded_strings = self.extract_encoded_strings(code)
        self.add_log(f"Found {len(encoded_strings)} potential encoded strings")

        # 尝试解码每个编码字符串
        for i, encoded in enumerate(encoded_strings):
            decoded = self.try_decode_multiple_layers(encoded)
            if decoded:
                # 检查解码后的内容
                try:
                    decoded_str = decoded.decode('utf-8', errors='replace')
                    if self.looks_like_python_code(decoded_str):
                        results['decoded_code'] = decoded_str
                        results['success'] = True
                        self.add_log(f"Successfully decoded string #{i} to Python code")
                        break
                    else:
                        results['decoded_content'] = decoded
                except Exception:
                    results['decoded_content'] = decoded

        results['execution_log'] = self.execution_log
        return results

    def looks_like_python_code(self, text: str) -> bool:
        """判断文本是否像Python代码"""
        if not text or len(text) < 20:
            return False

        python_indicators = [
            r'def\s+\w+\s*\(',
            r'class\s+\w+',
            r'import\s+\w+',
            r'from\s+\w+\s+import',
            r'if\s+__name__',
            r'print\s*\(',
            r'return\s+',
            r'if\s+.*:',
            r'for\s+.*in\s+',
            r'while\s+',
            r'with\s+.*as\s+',
        ]

        score = sum(1 for pattern in python_indicators if re.search(pattern, text))
        return score >= 2

    def deobfuscate_exec_pattern(self, code: str) -> Optional[str]:
        """专门处理exec加密模式"""
        # 模式1: exec(__import__('base64').b64decode(...))
        pattern1 = r"exec\s*\(\s*__import__\s*\(\s*['\"]([^'\"]+)['\"]\s*\)\.(\w+)\s*\(\s*(.+?)\s*\)\s*\)"
        matches = re.findall(pattern1, code, re.DOTALL)

        for module, method, data in matches:
            self.add_log(f"Found exec pattern: {module}.{method}")

            try:
                # 获取模块
                mod = __import__(module)

                # 尝试调用方法解码
                # 处理引号包裹的数据
                if data.strip().startswith(('"', "'")):
                    data = eval(data)

                if isinstance(data, str):
                    decoded = getattr(mod, method)(data.encode() if method == 'b64decode' else data)
                else:
                    decoded = getattr(mod, method)(data)

                # 递归处理
                if isinstance(decoded, bytes):
                    decoded = self.try_decode_multiple_layers(decoded)
                    if decoded:
                        decoded = decoded.decode('utf-8', errors='replace')

                if decoded and self.looks_like_python_code(decoded):
                    return decoded

            except Exception as e:
                self.add_log(f"Failed to decode: {e}")

        # 模式2: exec(base64.b64decode(...))
        pattern2 = r"exec\s*\(\s*(\w+)\.(\w+)\s*\(\s*(.+?)\s*\)\s*\)"
        matches = re.findall(pattern2, code, re.DOTALL)

        for module, method, data in matches:
            self.add_log(f"Found direct exec pattern: {module}.{method}")

        # 模式3: exec("...".encode().decode())
        pattern3 = r'exec\s*\(\s*(["\'])(.+?)\1(?:\s*\.encode\(\))*(?:\s*\.decode\([^)]*\))*'
        # 这个模式需要特殊处理

        return None

    def smart_deobfuscate(self, code: str) -> Dict[str, Any]:
        """智能反混淆主函数"""
        results = {
            'original': code,
            'layers_analyzed': [],
            'final_result': None,
            'bytecode_result': None,
            'success': False,
            'warnings': [],
        }

        # 首先尝试识别并处理常见的混淆模式
        code = code.strip()

        # 处理bytes转化模式
        code = re.sub(r'bytes\s*\(\s*浸', '', code)

        # 处理字符串拼接模式
        if re.search(r'\+[\s\n]*["\']', code):
            self.add_log("Detected string concatenation pattern")
            try:
                # 使用AST分析
                compiled = compile(code, '<string>', 'exec')
                # 这里可以添加AST级别的分析
            except Exception as e:
                results['warnings'].append(f"AST analysis failed: {e}")

        # 尝试exec解码
        exec_result = self.deobfuscate_exec_pattern(code)
        if exec_result:
            results['final_result'] = exec_result
            results['success'] = True
            return results

        # 尝试直接分析解码
        analysis_result = self.analyze_and_decode(code)
        if analysis_result['success']:
            results['final_result'] = analysis_result['decoded_code']
            results['bytecode_result'] = analysis_result['decoded_content']
            results['success'] = True
            return results

        # 返回原始代码和警告
        results['warnings'].append("No known obfuscation pattern detected")
        return results


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: python exec_decryptor.py <code_file_or_string>")
        print("       python exec_decryptor.py --interactive")
        sys.exit(1)

    decryptor = ExecDecryptor()

    if sys.argv[1] == '--interactive':
        print("=== Python Exec Decryptor ===")
        print("Enter code to decrypt (Ctrl+D to finish):")
        code = sys.stdin.read()
    elif os.path.isfile(sys.argv[1]):
        with open(sys.argv[1], 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
    else:
        code = sys.argv[1]

    results = decryptor.smart_deobfuscate(code)

    print("\n" + "=" * 60)
    print("DECRYPTION RESULTS")
    print("=" * 60)

    if results['success']:
        print("\n[+] Decryption successful!")
        print("\n--- Decoded Python Code ---")
        print(results['final_result'])
        if results.get('bytecode_result'):
            print("\n--- Additional Bytecode Data ---")
            print(f"Length: {len(results['bytecode_result'])} bytes")
    else:
        print("\n[-] Decryption failed or no obfuscation detected")
        for warning in results.get('warnings', []):
            print(f"    Warning: {warning}")

    print("\n--- Execution Log ---")
    for log in results.get('execution_log', []):
        print(log)


if __name__ == '__main__':
    main()
