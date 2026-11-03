#!/usr/bin/env python3
"""
百度网盘文件上传脚本
用法: python3 baidu_upload.py <file_path> <remote_path> <access_token>
示例: python3 baidu_upload.py ./report.pdf /apps/myapp/report.pdf <token>
"""
import sys
import os
import hashlib
import json
import urllib.request
import urllib.parse
import urllib.error

BLOCK_SIZE = 4 * 1024 * 1024  # 4MB per block

def md5_hex(file_path):
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def file_blocks_md5(file_path):
    """Return list of MD5 for each block."""
    blocks = []
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(BLOCK_SIZE)
            if not chunk:
                break
            blocks.append(hashlib.md5(chunk).hexdigest())
    return blocks

def precreate(path, size, block_list, access_token, app_name="AppName"):
    import uuid
    uploadid = str(uuid.uuid4())
    params = urllib.parse.urlencode({
        "method": "precreate",
        "access_token": access_token,
        "path": path,
        "size": size,
        "isdir": 0,
        "uploadid": uploadid,
        "block_list": json.dumps(block_list),
    })
    url = f"https://pan.baidu.com/rest/2.0/pcs/superfile2?{params}"
    req = urllib.request.Request(url, data=b"", method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
    if result.get("errno") != 0:
        raise Exception(f"precreate failed: {result}")
    return result.get("uploadid"), uploadid

def upload_block(block_data, seq, uploadid, access_token):
    params = urllib.parse.urlencode({
        "method": "upload",
        "access_token": access_token,
        "uploadid": uploadid,
        "part_id": seq + 1,
    })
    url = f"https://pan.baidu.com/rest/2.0/pcs/superfile2?{params}"
    req = urllib.request.Request(url, data=block_data, method="POST")
    req.add_header("Content-Type", "application/octet-stream")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def create_file(path, uploadid, block_list, access_token):
    params = urllib.parse.urlencode({
        "method": "create",
        "access_token": access_token,
        "path": path,
        "uploadid": uploadid,
        "ondup": "newcopy",
        "block_list": json.dumps(block_list),
    })
    url = f"https://pan.baidu.com/rest/2.0/pcs/superfile2?{params}"
    req = urllib.request.Request(url, data=b"", method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode())
    if result.get("errno") != 0:
        raise Exception(f"create failed: {result}")
    return result

def simple_upload(file_path, remote_path, access_token):
    """Single file upload for files < 2GB via direct PCS API."""
    file_size = os.path.getsize(file_path)
    params = urllib.parse.urlencode({
        "method": "upload",
        "access_token": access_token,
        "path": remote_path,
    })
    url = f"https://c.pcs.baidu.com/rest/2.0/pcs/file?{params}"
    with open(file_path, "rb") as f:
        req = urllib.request.Request(url, data=f, method="POST")
        req.add_header("Content-Type", "application/octet-stream")
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())

def check_quota(access_token):
    url = f"https://pan.baidu.com/api/quota?access_token={access_token}"
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read().decode())

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python3 baidu_upload.py <file_path> <remote_path> <access_token>")
        sys.exit(1)

    file_path = sys.argv[1]
    remote_path = sys.argv[2]
    access_token = sys.argv[3]
    file_size = os.path.getsize(file_path)

    print(f"文件: {file_path} ({file_size} bytes)")
    print(f"目标: {remote_path}")

    if file_size <= 2 * 1024 * 1024 * 1024:
        print("使用简单上传...")
        result = simple_upload(file_path, remote_path, access_token)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("使用分片上传...")
        block_list = file_blocks_md5(file_path)
        print(f"分片数: {len(block_list)}, 预创建...")
        uploadid, _ = precreate(remote_path, file_size, block_list, access_token)
        print(f"开始上传分片...")
        for i, block_md5 in enumerate(block_list):
            with open(file_path, "rb") as f:
                f.seek(i * BLOCK_SIZE)
                chunk = f.read(BLOCK_SIZE)
            print(f"  上传分片 {i+1}/{len(block_list)}...")
            upload_block(chunk, i, uploadid, access_token)
        print("合并文件...")
        result = create_file(remote_path, uploadid, block_list, access_token)
        print(json.dumps(result, indent=2, ensure_ascii=False))
