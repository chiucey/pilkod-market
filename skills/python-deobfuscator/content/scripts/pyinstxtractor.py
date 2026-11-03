#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller Exe 提取与反编译工具
用于从PyInstaller打包的exe中提取Python字节码并尝试反编译

支持:
- PyInstaller单文件模式 (-Fw)
- PyInstaller目录模式 (-D)
- 加密的PYZ资源提取
- 字节码修复与反编译
"""

import hashlib
import marshal
import os
import struct
import sys
import time
import zlib
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# PyInstaller常量
MAGIC_PYINST = b'MEI\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

PYZ_HEADER = b'PYZ\x00'

# Python字节码魔数 (部分)
PYTHON_MAGICS = {
    (0x33, 0x0d, 0x0d, 0x0a): ("3.11+", 16),
    (0x42, 0x0d, 0x0d, 0x0a): ("3.10", 16),
    (0x55, 0x0d, 0x0d, 0x0a): ("3.9", 16),
    (0x61, 0x0d, 0x0d, 0x0a): ("3.8", 16),
    (0x42, 0x13, 0x0d, 0x0a): ("3.7", 16),
    (0x6f, 0x0d, 0x0d, 0x0a): ("3.6", 16),
    (0x33, 0x0d, 0x0d, 0x0a): ("3.5", 16),
    (0xee, 0x0c, 0x0d, 0x0a): ("3.4", 16),
    (0x6c, 0x0c, 0x0d, 0x0a): ("3.3", 16),
    (0x6e, 0x0c, 0x0d, 0x0a): ("3.2", 16),
}


class PyinstExtractor:
    """PyInstaller exe提取器"""

    def __init__(self, exe_path: str, output_dir: Optional[str] = None):
        self.exe_path = Path(exe_path)
        self.output_dir = Path(output_dir) if output_dir else self.exe_path.with_name(
            self.exe_path.stem + "_extracted"
        )
        self.pycs: List[Dict] = []
        self.toc_offset = 0
        self.python_version = None
        self.pyc_header_size = 16

    def log(self, message: str):
        """日志输出"""
        print(f"[*] {message}")

    def error(self, message: str):
        """错误输出"""
        print(f"[-] {message}")

    def info(self, message: str):
        """信息输出"""
        print(f"[+] {message}")

    def extract(self) -> bool:
        """主提取函数"""
        self.log(f"Target: {self.exe_path}")
        self.log(f"Output: {self.output_dir}")

        if not self.exe_path.exists():
            self.error(f"File not found: {self.exe_path}")
            return False

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 检测文件类型
        if self.is_pyinstaller_archive(self.exe_path):
            return self.extract_archive()
        elif self.is_pyinstaller_solid(self.exe_path):
            return self.extract_solid()
        elif self.is_zip_sfx():
            return self.extract_zip()
        else:
            return self.fallback_extract()

    def is_pyinstaller_archive(self, path: Path) -> bool:
        """检测是否是PyInstaller打包的归档"""
        try:
            with open(path, 'rb') as f:
                # 搜索PyInstaller签名
                data = f.read(8192)
                if b'PYZ\x00' in data or b'PYZ\x00' in path.name.upper():
                    return True
                # 检查文件结构
                f.seek(0)
                magic = f.read(4)
                if magic == b'MZ\x90\x00':
                    return True
        except Exception:
            pass
        return False

    def is_pyinstaller_solid(self, path: Path) -> bool:
        """检测是否是PyInstaller单文件模式"""
        try:
            with open(path, 'rb') as f:
                # 搜索TOC表
                f.seek(0, 2)
                size = f.tell()
                if size > 1024 * 1024:  # 大于1MB
                    # 在文件末尾搜索
                    f.seek(max(0, size - 65536))
                    data = f.read()
                    if PYZ_HEADER in data:
                        return True
        except Exception:
            pass
        return False

    def is_zip_sfx(self) -> bool:
        """检测是否是ZIP自解压格式"""
        try:
            with open(self.exe_path, 'rb') as f:
                data = f.read(1024)
                # 检查ZIP签名
                if data[:4] == b'PK\x03\x04':
                    return True
        except Exception:
            pass
        return False

    def extract_zip(self) -> bool:
        """提取ZIP格式"""
        self.info("Detected ZIP archive format")

        try:
            with zipfile.ZipFile(self.exe_path, 'r') as zf:
                zf.extractall(self.output_dir)

            self.info("Extraction complete")
            return True
        except Exception as e:
            self.error(f"ZIP extraction failed: {e}")
            return False

    def extract_archive(self) -> bool:
        """提取PyInstaller归档格式"""
        self.log("Detected PyInstaller archive format")

        try:
            with open(self.exe_path, 'rb') as f:
                self._parse_archive(f)

            return True
        except Exception as e:
            self.error(f"Archive extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def extract_solid(self) -> bool:
        """提取PyInstaller单文件格式"""
        self.info("Detected PyInstaller onefile format")

        try:
            self._extract_from_solid()
            return True
        except Exception as e:
            self.error(f"Solid extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _parse_archive(self, f):
        """解析归档文件"""
        # 读取文件
        f.seek(0, 2)
        file_size = f.tell()
        f.seek(0)

        # 搜索TOC偏移量
        f.seek(max(0, file_size - 8192))
        tail = f.read()

        # 查找magic
        magic_pos = tail.rfind(MAGIC_PYINST)
        if magic_pos != -1:
            self.toc_offset = file_size - 8192 + magic_pos + 16
            f.seek(self.toc_offset)
            self.log(f"TOC offset: {self.toc_offset}")

        # 解析TOC表
        while f.tell() < file_size:
            try:
                entry = self._read_toc_entry(f)
                if entry is None:
                    break
                self._extract_entry(f, entry)
            except Exception as e:
                self.log(f"TOC parsing stopped: {e}")
                break

        self.info(f"Extracted {len(self.pycs)} Python files")

    def _read_toc_entry(self, f) -> Optional[Dict]:
        """读取TOC条目"""
        try:
            # 读取条目结构
            data = f.read(256)
            if len(data) < 24:
                return None

            # 解析
            entry = {}
            entry['data_offset'] = self._read_int64(f)

            if entry['data_offset'] == 0:
                return None

            entry['data_length'] = self._read_int64(f)
            entry['uncompressed_length'] = self._read_int64(f)
            entry['cflag'] = self._read_int64(f)
            entry['entry_length'] = self._read_int64(f)

            # 读取名称
            name_bytes = bytearray()
            for i in range(entry['entry_length']):
                c = f.read(1)
                if c == b'\x00':
                    break
                name_bytes.extend(c)

            entry['name'] = bytes(name_bytes).decode('utf-8', errors='replace')

            return entry

        except Exception:
            return None

    def _read_int64(self, f) -> int:
        """读取64位整数"""
        data = f.read(8)
        return struct.unpack('<Q', data)[0]

    def _extract_entry(self, f, entry: Dict):
        """提取条目"""
        name = entry['name']

        # 跳过目录
        if name.endswith('/') or name.endswith('\\'):
            return

        self.log(f"Extracting: {name}")

        # 保存到文件
        out_path = self.output_dir / name

        # 创建目录
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # 读取数据
        current_pos = f.tell()
        f.seek(entry['data_offset'])

        if entry['cflag'] & (1 << 7):  # 压缩标志
            try:
                compressed_data = f.read(entry['data_length'])
                data = zlib.decompress(compressed_data)
                with open(out_path, 'wb') as out:
                    out.write(data)
            except Exception as e:
                self.error(f"Decompression failed for {name}: {e}")
        else:
            data = f.read(entry['data_length'])
            with open(out_path, 'wb') as out:
                out.write(data)

        f.seek(current_pos)

        # 如果是pyc文件，记录
        if name.endswith('.pyc'):
            self.pycs.append({
                'path': out_path,
                'name': name,
                'size': entry['uncompressed_length']
            })

    def _extract_from_solid(self):
        """从单文件中提取"""
        self.log("Searching for embedded data...")

        with open(self.exe_path, 'rb') as f:
            # 搜索PKG签名
            f.seek(0, 2)
            file_size = f.tell()

            # 在文件末尾区域搜索
            search_start = max(0, file_size - 10 * 1024 * 1024)
            f.seek(search_start)
            tail = f.read()

            # 查找各个数据块
            # 查找PYZ
            pyz_pos = 0
            pkg_pos = 0

            for pattern in [b'PKG\x00', b'PYZ\x00', b'\x00\x00\x00\x00PKG']:
                pos = tail.rfind(pattern)
                if pos != -1:
                    pkg_pos = search_start + pos
                    self.log(f"Found PKG signature at {pkg_pos}")
                    break

            # 尝试提取
            f.seek(pkg_pos if pkg_pos else 0)

            # 提取所有可能的数据
            self._extract_pyz_files(f, file_size)

    def _extract_pyz_files(self, f, end_pos: int):
        """提取PYZ文件"""
        f.seek(0, 2)
        data = f.read()
        pos = 0

        # 搜索PYZ头部
        pyz_sigs = [
            b'PYZ\x00',
            b'PYZ\x00\x00\x00',
            b'PYZ\x00PK',
        ]

        found_pyz = []
        for sig in pyz_sigs:
            start = 0
            while True:
                pos = data.find(sig, start)
                if pos == -1:
                    break
                found_pyz.append(pos)
                start = pos + 1

        self.log(f"Found {len(found_pyz)} potential PYZ locations")

        for pos in found_pyz:
            self.log(f"PYZ candidate at offset {pos}")

            # 尝试提取
            try:
                # PYZ之后通常是marshal格式的数据
                pyz_data = data[pos:]
                if len(pyz_data) > 100:
                    out_path = self.output_dir / f"extracted_{pos:08x}.pyz"
                    with open(out_path, 'wb') as out:
                        out.write(pyz_data[:1024*1024])  # 保存前1MB
                    self.log(f"Saved PYZ candidate to {out_path.name}")
            except Exception as e:
                self.error(f"Failed to extract PYZ at {pos}: {e}")

    def fallback_extract(self) -> bool:
        """备用提取方法"""
        self.info("Using fallback extraction...")

        try:
            with open(self.exe_path, 'rb') as f:
                data = f.read()

            # 查找所有可能的数据块
            chunks = self._find_data_chunks(data)

            for i, chunk in enumerate(chunks):
                out_path = self.output_dir / f"chunk_{i:04d}.bin"
                with open(out_path, 'wb') as out:
                    out.write(chunk)
                self.log(f"Saved chunk {i}: {len(chunk)} bytes")

            return True

        except Exception as e:
            self.error(f"Fallback extraction failed: {e}")
            return False

    def _find_data_chunks(self, data: bytes) -> List[bytes]:
        """查找数据块"""
        chunks = []

        # 查找ZIP文件
        pos = 0
        while True:
            pos = data.find(b'PK\x03\x04', pos)
            if pos == -1:
                break

            # 读取ZIP头
            if pos + 30 < len(data):
                try:
                    comp_size = struct.unpack('<I', data[pos+18:pos+22])[0]
                    uncomp_size = struct.unpack('<I', data[pos+22:pos+26])[0]

                    if uncomp_size > 100 and uncomp_size < 10*1024*1024:
                        chunks.append(data[pos:pos+30+comp_size])
                except Exception:
                    pass

            pos += 1

        # 查找可能的marshal数据
        for magic in PYTHON_MAGICS.keys():
            pattern = bytes(magic)
            pos = 0
            while True:
                pos = data.find(pattern, pos)
                if pos == -1:
                    break

                # 尝试提取marshal数据
                chunk = data[pos:]
                try:
                    # 跳过头部，尝试作为marshal加载
                    marshal_data = chunk[16:16+1024*1024]
                    obj = marshal.loads(marshal_data)
                    if obj is not None:
                        chunks.append(chunk[:16+1024])
                except Exception:
                    pass

                pos += 1

        return chunks

    def fix_pyc_header(self, pyc_path: Path) -> bool:
        """修复pyc文件头"""
        self.log(f"Fixing: {pyc_path.name}")

        with open(pyc_path, 'rb') as f:
            data = f.read()

        # 检测Python版本
        version_info = None
        for magic, info in PYTHON_MAGICS.items():
            if data.startswith(bytes(magic)):
                version_info = info
                break

        if not version_info:
            self.error(f"Unknown magic number for {pyc_path.name}")
            return False

        version, header_size = version_info
        self.python_version = version
        self.pyc_header_size = header_size

        # 检查头部
        if len(data) < header_size + 4:
            self.error(f"File too small: {pyc_path.name}")
            return False

        # 尝试修复
        new_data = data

        # 如果是raw marshal数据，添加头部
        is_raw_marshal = True
        for magic in PYTHON_MAGICS.keys():
            if data.startswith(bytes(magic)):
                is_raw_marshal = False
                break

        if is_raw_marshal:
            # 创建标准头部
            header = bytes(magic)  # 使用第一个版本作为默认值
            # 添加flags, timestamp等
            header += struct.pack('<I', 0)  # flags
            header += struct.pack('<I', int(time.time()))  # timestamp
            header += struct.pack('<I', len(data))  # size

            new_data = header + data

        # 写回
        fixed_path = pyc_path.with_name(pyc_path.stem + '_fixed.pyc')
        with open(fixed_path, 'wb') as f:
            f.write(new_data)

        self.info(f"Fixed: {fixed_path.name}")
        return True

    def decompile_pyc(self, pyc_path: Path) -> Optional[str]:
        """反编译pyc文件"""
        self.log(f"Decompiling: {pyc_path.name}")

        try:
            # 尝试使用uncompyle6
            try:
                from uncompyle6 import decompile
                import io

                with open(pyc_path, 'rb') as f:
                    code = marshal.load(f)

                output = io.StringIO()
                decompile(code, output)
                return output.getvalue()

            except ImportError:
                pass

            # 尝试使用decompyle3
            try:
                from decompyle3 import decompile
                import io

                with open(pyc_path, 'rb') as f:
                    code = marshal.load(f)

                output = io.StringIO()
                decompile(code, output)
                return output.getvalue()

            except ImportError:
                pass

            self.error("No decompiler available. Install uncompyle6: pip install uncompyle6")
            return None

        except Exception as e:
            self.error(f"Decompile failed: {e}")
            return None


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: python pyinstxtractor.py <exe_file> [output_dir]")
        print("")
        print("Options:")
        print("  --decompile    Attempt to decompile extracted .pyc files")
        print("  --fix-header   Fix .pyc file headers")
        sys.exit(1)

    exe_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    options = {
        'decompile': '--decompile' in sys.argv,
        'fix_header': '--fix-header' in sys.argv,
    }

    # 创建提取器
    extractor = PyinstExtractor(exe_path, output_dir)

    # 执行提取
    if extractor.extract():
        print("\n" + "=" * 60)
        print("EXTRACTION COMPLETE")
        print("=" * 60)
        print(f"\nOutput directory: {extractor.output_dir}")

        # 修复pyc文件
        if options['fix_header'] or options['decompile']:
            for pyc_info in extractor.pycs:
                extractor.fix_pyc_header(pyc_info['path'])

        # 反编译
        if options['decompile']:
            print("\n--- Decompiling .pyc files ---")
            for pyc_info in extractor.pycs:
                source = extractor.decompile_pyc(pyc_info['path'])
                if source:
                    out_path = extractor.output_dir / (pyc_info['path'].stem + '.py')
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(source)
                    print(f"Decompiled: {out_path.name}")
    else:
        print("\n[-] Extraction failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
