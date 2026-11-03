#!/usr/bin/env python3
"""安装校验过的官方二进制；不执行上游安装器，不修改其他 Agent。"""
import base64
import hashlib
import io
import os
from pathlib import Path
import platform
import tarfile
import tempfile
import urllib.request
import zipfile

VERSION = "1.0.64"
URL = f"https://registry.npmjs.org/dingtalk-workspace-cli/-/dingtalk-workspace-cli-{VERSION}.tgz"
INTEGRITY = "0ySv3ZezEeMwYY4m3Db7AEON9DceVr/dQaS2lz07gy/fIlNMh50qbnQN7Llqc5B5CjuZoUrBKUaspTbJN0Vyaw=="


def extract_binary(package, system, machine):
    os_name = {"Darwin": "darwin", "Windows": "windows", "Linux": "linux"}.get(system)
    arch = {"aarch64": "arm64", "arm64": "arm64", "amd64": "amd64", "x86_64": "amd64"}.get(machine.lower())
    if not os_name or not arch:
        raise ValueError(f"不支持的平台：{system}/{machine}")
    windows = os_name == "windows"
    ext = "zip" if windows else "tar.gz"
    name = "dws.exe" if windows else "dws"
    with tarfile.open(fileobj=package, mode="r:gz") as outer:
        member = outer.getmember(f"package/assets/dws-{os_name}-{arch}.{ext}")
        if not member.isfile() or member.size > 128 * 1024 * 1024:
            raise ValueError("发布包格式异常")
        data = outer.extractfile(member).read()
    # 只读取固定文件，不解压任意路径、链接或安装脚本。
    if windows:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            return {f: archive.read(f) for f in (name, "LICENSE", "NOTICE")}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        result = {}
        for f in (name, "LICENSE", "NOTICE"):
            member = archive.getmember(f"./{f}")
            if not member.isfile():
                raise ValueError("发布包包含非法文件类型")
            result[f] = archive.extractfile(member).read()
        return result


def main():
    with tempfile.TemporaryFile() as package:
        digest = hashlib.sha512()
        total = 0
        with urllib.request.urlopen(URL, timeout=60) as response:
            while chunk := response.read(1024 * 1024):
                total += len(chunk)
                if total > 512 * 1024 * 1024:
                    raise ValueError("发布包超出大小限制")
                digest.update(chunk)
                package.write(chunk)
        if base64.b64encode(digest.digest()).decode() != INTEGRITY:
            raise ValueError("发布包完整性校验失败，未安装")
        package.seek(0)
        files = extract_binary(package, platform.system(), platform.machine())
    target = Path.home() / ".pilkod" / "tools" / "dws" / VERSION / "bin"
    target.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        path = target / name
        if path.exists():
            if path.read_bytes() != data:
                raise ValueError(f"已有文件与发布包不一致，未覆盖：{path}")
            continue
        # 独占创建，避免覆盖并发安装或已有用户文件。
        with path.open("xb") as output:
            output.write(data)
        if name == "dws":
            os.chmod(path, 0o755)
    print(target / ("dws.exe" if platform.system() == "Windows" else "dws"))


if __name__ == "__main__":
    main()
