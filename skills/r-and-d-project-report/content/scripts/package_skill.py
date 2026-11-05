"""
技能打包脚本
将技能打包为可分发的.skill文件
"""

import os
import shutil
import zipfile
from datetime import datetime

def package_skill(skill_path, output_dir='.'):
    """打包技能为.skill文件"""
    skill_name = os.path.basename(skill_path)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    output_file = os.path.join(output_dir, f'{skill_name}_{timestamp}.skill')

    # 创建zip文件
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 排除隐藏文件和__pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for file in files:
                if not file.startswith('.') and not file.endswith('.pyc'):
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                    zf.write(file_path, arcname)

    print(f'技能已打包: {output_file}')
    return output_file

if __name__ == '__main__':
    import sys
    skill_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    package_skill(skill_path)