#!/usr/bin/env python3
"""
garminconnect 库中国服务器支持修复脚本

此脚本修复 garminconnect 库以支持中国大陆 Garmin 服务器 (garmin.cn)

使用方法:
    python fix_garmin_cn.py

修复内容:
1. _establish_session 方法 - fallback URL
2. _exchange_service_ticket 方法 - DI 认证 URL
3. _exchange_service_ticket 方法 - service URL
4. _do_mobile_login 方法 - service 参数

修复前请确保已安装 garminconnect:
    pip install --upgrade garminconnect
"""

import os
import sys
import shutil

def get_client_py_path():
    """获取 client.py 文件路径"""
    import site
    sites = site.getsitepackages() + [site.getusersitepackages()]
    for site_dir in sites:
        client_py = os.path.join(site_dir, 'garminconnect', 'client.py')
        if os.path.exists(client_py):
            return client_py
    # 尝试从已安装的包中查找
    try:
        import garminconnect
        return os.path.join(os.path.dirname(garminconnect.__file__), 'client.py')
    except:
        pass
    return None

def backup_file(filepath):
    """备份文件"""
    backup_path = filepath + '.backup_cn'
    if not os.path.exists(backup_path):
        shutil.copy(filepath, backup_path)
        print(f"  已备份到: {backup_path}")
    return backup_path

def fix_garmin_lib():
    """修复 garminconnect 库"""
    print("=" * 60)
    print("garminconnect 库中国服务器修复脚本")
    print("=" * 60)
    
    # 获取 client.py 路径
    client_py = get_client_py_path()
    if not client_py:
        print("\n错误: 无法找到 garminconnect 库的 client.py 文件")
        print("请确保已安装 garminconnect:")
        print("    pip install --upgrade garminconnect")
        return False
    
    print(f"\n找到文件: {client_py}")
    
    # 读取文件
    with open(client_py, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"文件长度: {len(content)} 字符")
    
    # 备份
    print("\n[1/4] 备份原始文件...")
    backup_file(client_py)
    
    modifications = []
    
    # 修复 1: _establish_session 方法中的 fallback URL
    print("\n[2/4] 修复 _establish_session 方法...")
    old1 = 'svc = service_url or IOS_SERVICE_URL'
    new1 = 'svc = service_url or f"https://mobile.integration.{self.domain}/gcm/ios"'
    if old1 in content:
        content = content.replace(old1, new1)
        modifications.append("_establish_session fallback URL")
        print("  已修复 fallback URL")
    
    # 修复 2: _exchange_service_ticket 方法中的 MOBILE_SSO_SERVICE_URL
    print("\n[3/4] 修复 _exchange_service_ticket 方法...")
    old2 = 'svc_url = service_url or MOBILE_SSO_SERVICE_URL'
    new2 = 'svc_url = service_url or f"https://mobile.integration.{self.domain}/gcm/android"'
    if old2 in content:
        content = content.replace(old2, new2)
        modifications.append("exchange_service_ticket service URL")
        print("  已修复 service URL")
    
    # 修复 3: _exchange_service_ticket 方法中的 DI_TOKEN_URL
    old3 = 'r = self._http_post(\n                DI_TOKEN_URL,'
    new3 = 'di_auth_url = f"https://diauth.{self.domain}/di-oauth2-service/oauth/token"\n            r = self._http_post(\n                di_auth_url,'
    if old3 in content:
        content = content.replace(old3, new3)
        modifications.append("exchange_service_ticket DI auth URL")
        print("  已修复 DI auth URL")
    
    # 修复 4: _do_mobile_login 方法中的 IOS_SERVICE_URL
    print("\n[4/4] 修复 _do_mobile_login 方法...")
    old4 = '"service": IOS_SERVICE_URL,'
    new4 = '"service": f"https://mobile.integration.{self.domain}/gcm/ios",'
    if old4 in content:
        content = content.replace(old4, new4)
        modifications.append("_do_mobile_login service URL")
        print("  已修复 mobile login service URL")
    
    # 保存修复后的文件
    with open(client_py, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n修复后文件长度: {len(content)} 字符")
    
    # 结果
    print("\n" + "=" * 60)
    if modifications:
        print("修复完成！已进行以下修改:")
        for i, mod in enumerate(modifications, 1):
            print(f"  {i}. {mod}")
    else:
        print("未发现需要修复的内容（可能已经修复过或文件格式不同）")
    print("=" * 60)
    
    return True

def revert_fix():
    """恢复原始文件"""
    client_py = get_client_py_path()
    if not client_py:
        print("错误: 无法找到 client.py 文件")
        return False
    
    backup_path = client_py + '.backup_cn'
    if os.path.exists(backup_path):
        shutil.copy(backup_path, client_py)
        print(f"已从备份恢复: {client_py}")
        return True
    else:
        print("未找到备份文件")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--revert':
        print("恢复原始文件...")
        revert_fix()
    else:
        fix_garmin_lib()
