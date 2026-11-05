#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base65536 文件编码/解码工具
使用Base65536编码将任意文件转换为Unicode文本，支持gzip压缩、原文件名保存，
以及基于本地网络抖动真随机密钥的字节级异或加密，加密模式下隐藏真实元数据。

安装依赖:
    pip install base65536

用法:
    # 普通编码（无加密，元数据明文）
    python skill.py encode <输入文件> [-o <输出文件>] [--no-compress]

    # 加密编码（真随机密钥 + 异或加密，隐藏元数据）
    python skill.py encode <输入文件> --scramble [-o <输出文件>] [--key-file <密钥文件>]

    # 加密编码（使用指定密钥）
    python skill.py encode <输入文件> --scramble --key <密钥整数> [-o <输出文件>]

    # 解码（若文件已加密，需提供密钥）
    python skill.py decode <输入文件> --key <密钥整数> [-o <输出文件>]

注意:
    - 加密模式下自动生成的密钥会保存到文件，不会在终端显示。
    - 密钥文件权限自动锁定为 600 (仅所有者可读写)。
    - 密钥来自本地回环网络抖动测量，不可复现，务必妥善保管。

Author: TurinFohlem
Version: 3.0.3
"""

import argparse
import gzip
import base65536
import os
import json
import hashlib   # only one import
import time
import socket
import stat

# ============================================================
# 密码学安全的密钥流派生
# ============================================================
def secure_keystream(seed: int, length: int) -> bytes:
    """从整数种子派生伪随机字节流（SHAKE-256）"""
    seed_bytes = seed.to_bytes(32, 'big')
    return hashlib.shake_256(seed_bytes).digest(length)

# ============================================================
# 真随机密钥生成器（本地回环网络抖动熵源）
# ============================================================
def get_true_jitter() -> bytes:
    """测量真实 localhost TCP 抖动，修复死锁：服务器必须回送数据"""
    entropy = b""
    
    for port in range(54321, 54326):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', port))
        server.listen(1)
        
        for _ in range(20):
            try:
                t1 = time.perf_counter_ns()
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(('127.0.0.1', port))
                t2 = time.perf_counter_ns()
                
                conn, _ = server.accept()
                t3 = time.perf_counter_ns()
                
                # 测量往返：客户端发送，服务器回送
                client.send(b'X')
                data = conn.recv(1)
                if data == b'X':          # 验证回送正确
                    conn.send(b'X')       # 关键修复：服务器必须发送回包
                t4 = time.perf_counter_ns()
                
                # 客户端接收回包（完成一次完整往返）
                client.recv(1)
                t5 = time.perf_counter_ns()
                
                entropy += (t2 - t1).to_bytes(8, 'little')
                entropy += (t3 - t2).to_bytes(8, 'little')
                entropy += (t4 - t3).to_bytes(8, 'little')
                entropy += (t5 - t4).to_bytes(8, 'little')
                
                client.close()
                conn.close()
                
            except Exception:
                # 静默失败，继续收集熵（避免挂起）
                pass
        
        server.close()
    
    entropy += os.urandom(32)
    return hashlib.sha256(entropy).digest()

def generate_true_random_key() -> int:
    """生成256位真随机密钥"""
    seed_bytes = get_true_jitter()
    return int.from_bytes(seed_bytes, byteorder='big')

# ============================================================
# 密钥安全输出
# ============================================================
def output_key(key_int: int, output_path: str = None):
    if output_path is None:
        output_path = "cipher65536.key"
    
    if os.path.exists(output_path):
        base, ext = os.path.splitext(output_path)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        output_path = f"{base}_{counter}{ext}"
        print(f"  ⚠️  密钥文件已存在，保存为: {output_path}")
    
    with open(output_path, "w") as f:
        f.write(f"# cipher65536 encryption key\n")
        f.write(f"# Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Keep this file secure.\n")
        f.write(f"{key_int}\n")
    
    try:
        os.chmod(output_path, stat.S_IRUSR | stat.S_IWUSR)
        perm_locked = True
    except Exception:
        perm_locked = False
    
    print(f"  🔑 密钥已保存至: {output_path}")
    if perm_locked:
        print(f"  🔒 文件权限 600 (仅所有者可读写)")

# ============================================================
# XOR 加解密核心
# ============================================================
def xor_bytes(data: bytes, seed: int) -> bytes:
    keystream = secure_keystream(seed, len(data))
    return bytes(a ^ b for a, b in zip(data, keystream))

def encrypt_body(text: str, seed: int) -> str:
    data_bytes = text.encode('utf-8')
    encrypted_bytes = xor_bytes(data_bytes, seed)
    return base65536.encode(encrypted_bytes)

def decrypt_body(encrypted_b65536: str, seed: int) -> str:
    encrypted_bytes = base65536.decode(encrypted_b65536)
    decrypted_bytes = xor_bytes(encrypted_bytes, seed)
    return decrypted_bytes.decode('utf-8')

# ============================================================
# 主程序
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="Base65536 编码/解码工具（真随机密钥版）")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    encode_parser = subparsers.add_parser("encode", help="编码文件")
    encode_parser.add_argument("input", help="输入文件路径")
    encode_parser.add_argument("-o", "--output", help="输出文件路径")
    encode_parser.add_argument("--no-compress", action="store_true", help="不压缩")
    encode_parser.add_argument("--scramble", action="store_true", help="真随机密钥 + 异或加密并隐藏元数据")
    encode_parser.add_argument("--key", help="指定密钥整数（若不提供则自动生成）")
    encode_parser.add_argument("--key-file", help="密钥输出文件路径")
    
    decode_parser = subparsers.add_parser("decode", help="解码文件")
    decode_parser.add_argument("input", help="输入文件路径")
    decode_parser.add_argument("-o", "--output", help="输出文件路径")
    decode_parser.add_argument("--key", help="解密密钥整数（加密模式必需）")
    
    args = parser.parse_args()
    
    if args.command == "encode":
        with open(args.input, "rb") as f:
            data = f.read()
        
        original_size = len(data)
        original_name = os.path.basename(args.input)
        
        compressed_flag = not args.no_compress
        if compressed_flag:
            compressed_data = gzip.compress(data, compresslevel=9)
            print(f"  压缩: {original_size} → {len(compressed_data)} 字节 ({len(compressed_data)/original_size*100:.1f}%)")
        else:
            compressed_data = data
        
        b65536_text = base65536.encode(compressed_data)
        print(f"  编码: {len(compressed_data)} 字节 → {len(b65536_text)} 字符")
        
        real_metadata = {
            "original_name": original_name,
            "compressed": compressed_flag,
            "original_size": original_size
        }
        
        if args.scramble:
            # 密钥处理
            if args.key:
                key_int = int(args.key)
                print(f"  🔑 使用用户指定密钥")
            else:
                print("  🌐 正在从本地网络抖动采集真随机熵...")
                key_int = generate_true_random_key()
                if args.key_file:
                    key_output = args.key_file
                else:
                    base = os.path.splitext(args.output or original_name)[0]
                    key_output = base + ".key"
                output_key(key_int, key_output)
            
            # 加密主体
            encrypted_body = encrypt_body(b65536_text, key_int)
            
            # 加密真实元数据
            real_meta_json = json.dumps(real_metadata).encode('utf-8')
            meta_key_bytes = secure_keystream(key_int, len(real_meta_json))
            encrypted_meta = bytes([a ^ b for a, b in zip(real_meta_json, meta_key_bytes)])
            encrypted_meta_b65536 = base65536.encode(encrypted_meta)
            
            # 假元数据（放在头部）
            fake_metadata = {
                "original_name": "encrypted_file",
                "compressed": True,
                "original_size": 0,
                "scrambled": True,
                "note": "This file is encrypted. Use key to decrypt."
            }
            metadata_line = f"#METADATA:{json.dumps(fake_metadata)}\n"
            
            final_text = metadata_line + encrypted_body + "\n###ENCRYPTED_META###" + encrypted_meta_b65536
        else:
            real_metadata["scrambled"] = False
            metadata_line = f"#METADATA:{json.dumps(real_metadata)}\n"
            final_text = metadata_line + b65536_text
        
        output = args.output or original_name + ".b65536.txt"
        with open(output, "w", encoding="utf-8") as f:
            f.write(final_text)
        
        print(f"✓ 已编码: {output}")
        if args.scramble and not args.key:
            print(f"  ⚠️  密钥未在终端显示，请从密钥文件获取。")
        print(f"  最终大小: {len(final_text)} 字符")
    
    elif args.command == "decode":
        with open(args.input, "r", encoding="utf-8") as f:
            content = f.read()
        
        if "\n" in content:
            first_line, rest = content.split("\n", 1)
        else:
            first_line, rest = content, ""
        
        metadata = None
        if first_line.startswith("#METADATA:"):
            try:
                metadata = json.loads(first_line[10:])
                print(f"  读取到元数据: {metadata}")
            except:
                print("  警告: 元数据损坏，尝试直接解码")
        
        is_scrambled = metadata.get("scrambled", False) if metadata else False
        
        if is_scrambled:
            if not args.key:
                print("❌ 错误: 此文件已加密，需要提供 --key 密钥才能解码")
                return
            try:
                key_int = int(args.key)
            except ValueError:
                print("❌ 错误: 密钥必须是整数")
                return
            
            print(f"  使用密钥解密...")
            
            if "###ENCRYPTED_META###" in rest:
                encrypted_body, encrypted_meta_b65536 = rest.split("###ENCRYPTED_META###", 1)
                encrypted_body = encrypted_body.rstrip("\n")
            else:
                print("❌ 错误: 加密文件格式不正确，缺少加密元数据")
                return
            
            # 解密真实元数据
            encrypted_meta = base65536.decode(encrypted_meta_b65536.strip())
            # 🔧 修复：使用加密元数据的实际长度，而不是未定义的 real_meta_json
            meta_key_bytes = secure_keystream(key_int, len(encrypted_meta))
            real_meta_json_bytes = bytes([a ^ b for a, b in zip(encrypted_meta, meta_key_bytes)])
            try:
                real_metadata = json.loads(real_meta_json_bytes.decode('utf-8'))
                print(f"  解密元数据: {real_metadata}")
            except:
                print("❌ 错误: 密钥错误或文件损坏，无法解密元数据")
                return
            
            b65536_text = decrypt_body(encrypted_body, key_int)
        else:
            real_metadata = metadata
            b65536_text = rest
        
        data = base65536.decode(b65536_text.strip())
        
        if real_metadata and real_metadata.get("compressed", False):
            if data[:2] == b'\x1f\x8b':
                print("  检测到 gzip 压缩，正在解压...")
                data = gzip.decompress(data)
            else:
                print("  警告: 元数据标记为压缩但数据非gzip格式，尝试直接还原")
        
        if args.output:
            output = args.output
        else:
            output = real_metadata.get("original_name", "restored_file") if real_metadata else "restored_file"
            if os.path.exists(output):
                base, ext = os.path.splitext(output)
                output = f"{base}_restored{ext}"
                print(f"  文件已存在，改为: {output}")
        
        with open(output, "wb") as f:
            f.write(data)
        
        print(f"✓ 已解码: {output}")
        print(f"  还原大小: {len(data)} 字节")

if __name__ == "__main__":
    main()