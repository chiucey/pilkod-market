# -*- coding: utf-8 -*-
"""
HTML转PDF生成器
将HTML文件通过Edge浏览器headless模式转换为PDF

用法:
    python html_to_pdf.py <输入html文件路径> [输出pdf路径]
    
示例:
    python html_to_pdf.py test.html
    python html_to_pdf.py test.html output.pdf
"""

import subprocess
import os
import shutil
import time
import sys
import tempfile

def html_to_pdf(input_html, output_pdf=None):
    """
    将HTML文件转换为PDF
    
    Args:
        input_html: 输入HTML文件路径
        output_pdf: 输出PDF路径（可选，默认与HTML同名）
    """
    if not os.path.exists(input_html):
        print(f"错误: 文件不存在: {input_html}")
        return False
    
    if output_pdf is None:
        base_name = os.path.splitext(input_html)[0]
        output_pdf = base_name + ".pdf"
    
    abs_input = os.path.abspath(input_html)
    abs_output = os.path.abspath(output_pdf)
    
    edge_candidates = [
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        shutil.which("msedge"),
        shutil.which("msedge.exe"),
    ]
    edge_candidates = [p for p in edge_candidates if p]
    edge_path = None
    for p in edge_candidates:
        if os.path.exists(p):
            edge_path = p
            break
    
    if not edge_path:
        print("错误: 未找到Microsoft Edge浏览器")
        return False
    
    # 处理可能的Unicode路径问题：拷贝到临时ASCII路径再打印
    tmp_dir = os.path.join(tempfile.gettempdir(), "edge_pdf_tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_input = os.path.join(tmp_dir, "input.html")
    tmp_output = os.path.join(tmp_dir, "output.pdf")
    try:
        shutil.copyfile(abs_input, tmp_input)
    except Exception as e:
        print(f"错误: 无法复制HTML到临时目录: {e}")
        return False
    
    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={tmp_output}",
        "--enable-features=UseSkiaRenderer",
        "--disable-extensions",
        "--disable-background-networking",
        "--disable-default-apps",
        "--disable-sync",
        "--disable-translate",
        "--metrics-recording-only",
        "--mute-audio",
        "--no-first-run",
        "--safebrowsing-disable-auto-update",
        tmp_input
    ]
    
    print(f"正在生成PDF: {abs_output}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        print("警告: 转换超时，尝试继续检查文件")
        result = subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="timeout")
    
    if result.returncode != 0:
        print(f"警告: Edge返回码 {result.returncode}")
        if result.stderr:
            print(f"stderr: {result.stderr.strip()}")
        if result.stdout:
            print(f"stdout: {result.stdout.strip()}")
    
    time.sleep(3)
    
    # 将临时输出移动到目标位置
    if os.path.exists(tmp_output):
        try:
            os.makedirs(os.path.dirname(abs_output), exist_ok=True)
            shutil.move(tmp_output, abs_output)
        except Exception as e:
            print(f"错误: 无法移动PDF到目标路径: {e}")
            return False
    
    if os.path.exists(abs_output):
        size = os.path.getsize(abs_output)
        print(f"✓ PDF生成成功: {abs_output} ({size/1024:.1f} KB)")
        return True
    else:
        print("错误: PDF生成失败")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = html_to_pdf(input_file, output_file)
    sys.exit(0 if success else 1)
