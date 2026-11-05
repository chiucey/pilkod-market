#!/usr/bin/env python3
"""
dex_splitter.py — 修复 dump 出来的 dex 文件

主要功能:
  1) --fix-checksum   修复 dex 头部 Adler32 校验和
  2) --verify         验证 dex 文件合法性
  3) --dedup          多个 dump 出来的 dex 去重
  4) --merge          把多个 dex 拼成 multidex 形式(简单合并)

Usage:
    python3 dex_splitter.py --fix-checksum dump.dex
    python3 dex_splitter.py --verify dump.dex
    python3 dex_splitter.py --dedup --in-dir ./dumps --out-dir ./merged
"""

import argparse
import hashlib
import struct
import sys
import zlib
from pathlib import Path

DEX_MAGIC = b"dex\n035\0"


def adler32(data: bytes) -> int:
    return zlib.adler32(data) & 0xFFFFFFFF


def fix_checksum(path: Path) -> bool:
    """dex header 0x08-0x0C 是 Adler32(从 0x0C 开始算),把校验和清零再算"""
    data = bytearray(path.read_bytes())
    if data[:8] != DEX_MAGIC:
        print(f"  ✗ not a dex file: {path}")
        return False
    # 清零校验和
    data[0x08:0x0C] = b"\x00\x00\x00\x00"
    # 从 0x0C 开始算
    checksum = adler32(bytes(data[0x0C:]))
    struct.pack_into("<I", data, 0x08, checksum)
    # 顺手算 sha1 写回 0x0C-0x20 (签名, 不影响 jadx 解析但 dexopt 要)
    sha1 = hashlib.sha1(bytes(data[0x20:])).digest()
    data[0x0C:0x20] = sha1
    path.write_bytes(bytes(data))
    print(f"  ✓ {path.name}: checksum=0x{checksum:08x}, sha1={sha1.hex()[:16]}...")
    return True


def verify(path: Path) -> dict:
    data = path.read_bytes()
    info = {"file": str(path), "size": len(data), "valid": False, "errors": []}
    if data[:8] != DEX_MAGIC:
        info["errors"].append("magic mismatch")
        return info
    info["magic"] = "dex\\n035\\0"
    file_size = struct.unpack_from("<I", data, 0x20)[0]
    header_size = struct.unpack_from("<I", data, 0x24)[0]
    info["declared_size"] = file_size
    info["header_size"] = header_size
    if header_size != 0x70:
        info["errors"].append(f"header_size=0x{header_size:x}, expected 0x70")
    if file_size != len(data):
        info["errors"].append(f"declared_size({file_size}) != actual({len(data)})")
    # 校验和
    stored_cksum = struct.unpack_from("<I", data, 0x08)[0]
    data_no_cksum = bytearray(data)
    data_no_cksum[0x08:0x0C] = b"\x00\x00\x00\x00"
    expected = adler32(bytes(data_no_cksum[0x0C:]))
    info["checksum_stored"] = f"0x{stored_cksum:08x}"
    info["checksum_computed"] = f"0x{expected:08x}"
    if stored_cksum != expected:
        info["errors"].append(f"checksum mismatch: stored={info['checksum_stored']}, computed={info['checksum_computed']}")
    info["valid"] = len(info["errors"]) == 0
    # string_ids 数量
    if file_size >= 0x70:
        string_ids_size = struct.unpack_from("<I", data, 0x38)[0]
        type_ids_size = struct.unpack_from("<I", data, 0x40)[0]
        class_defs_size = struct.unpack_from("<I", data, 0x60)[0]
        info["string_ids"] = string_ids_size
        info["type_ids"] = type_ids_size
        info["class_defs"] = class_defs_size
        if class_defs_size == 0:
            info["errors"].append("class_defs=0, likely empty/stub dex")
    return info


def dedup(in_dir: Path, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    seen = {}  # sha1 → path
    dups = 0
    for p in sorted(in_dir.glob("*.dex")):
        sha1 = hashlib.sha1(p.read_bytes()).hexdigest()
        if sha1 in seen:
            dups += 1
            print(f"  = dup: {p.name} == {seen[sha1].name}")
            continue
        # 改名按 sha1 前 8 位
        new_name = f"dedup_{sha1[:8]}_{p.name}"
        out_path = out_dir / new_name
        out_path.write_bytes(p.read_bytes())
        seen[sha1] = out_path
    print(f"[*] dedup: {len(seen)} unique, {dups} duplicates")
    return len(seen)


def main():
    ap = argparse.ArgumentParser(description="DEX file repair / verification / dedup")
    ap.add_argument("--fix-checksum", action="store_true", help="修复 Adler32 校验和")
    ap.add_argument("--verify", action="store_true", help="验证 dex 合法性")
    ap.add_argument("--dedup", action="store_true", help="目录内 dex 去重")
    ap.add_argument("--in-dir", type=Path, help="dedup 输入目录")
    ap.add_argument("--out-dir", type=Path, help="dedup 输出目录")
    ap.add_argument("files", nargs="*", type=Path, help="dex 文件")
    args = ap.parse_args()

    if args.dedup:
        if not args.in_dir or not args.out_dir:
            print("--dedup 需要 --in-dir 和 --out-dir")
            sys.exit(1)
        dedup(args.in_dir, args.out_dir)
        return

    if not args.files:
        print("需要 dex 文件 (或用 --dedup)")
        ap.print_help()
        sys.exit(1)

    for f in args.files:
        if not f.exists():
            print(f"not found: {f}")
            continue
        if args.fix_checksum:
            fix_checksum(f)
        elif args.verify:
            import json
            info = verify(f)
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            # 默认 verify
            import json
            info = verify(f)
            print(f"{f.name}: {'OK' if info['valid'] else 'INVALID'} "
                  f"(size={info['size']}, classes={info.get('class_defs', '?')})")
            for e in info["errors"]:
                print(f"  - {e}")


if __name__ == "__main__":
    main()
