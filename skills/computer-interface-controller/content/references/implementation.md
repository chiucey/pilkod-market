# Computer Interface Controller - Implementation Guide

## 安装依赖

### 本地环境
```bash
pip install pyautogui Pillow pytesseract pyscreenshot opencv-python
```

### OCR引擎 (Linux)
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

## 核心API实现

### 1. 截图模块
```python
import pyscreenshot as ImageGrab

def capture_screen(region=None):
    """捕获屏幕截图
    Args:
        region: (x, y, width, height) 可选区域
    Returns:
        PIL Image对象
    """
    if region:
        x, y, w, h = region
        img = ImageGrab.grab(bbox=(x, y, x+w, y+h))
    else:
        img = ImageGrab.grab()
    return img
```

### 2. OCR识别
```python
import pytesseract

def ocr_image(image):
    """从图像中提取文字
    Args:
        image: PIL Image对象
    Returns:
        str: 识别的文字
    """
    text = pytesseract.image_to_string(image, lang='chi_sim+eng')
    return text.strip()
```

### 3. 鼠标控制
```python
import pyautogui

def click_at(x, y, button='left'):
    """点击指定坐标
    Args:
        x, y: 目标坐标
        button: 'left', 'right', 'middle'
    """
    pyautogui.click(x, y, button=button)

def move_to(x, y):
    """移动鼠标到指定坐标"""
    pyautogui.moveTo(x, y)

def drag_to(x, y, duration=0.5):
    """拖拽到指定位置"""
    pyautogui.dragTo(x, y, duration=duration)
```

### 4. 键盘控制
```python
import pyautogui

def type_text(text):
    """输入文本"""
    pyautogui.write(text, interval=0.05)

def press_key(key):
    """按压单个键"""
    pyautogui.press(key)

def hotkey(*keys):
    """执行快捷键组合
    Example: hotkey('ctrl', 'c') 复制
    """
    pyautogui.hotkey(*keys)
```

### 5. 图像识别
```python
import cv2
import numpy as np

def find_on_screen(template_path, confidence=0.8):
    """在屏幕上查找目标图像
    Args:
        template_path: 目标图像路径
        confidence: 匹配置信度
    Returns:
        (x, y) 匹配位置中心坐标，未找到返回None
    """
    screen = capture_screen()
    screen_np = np.array(screen)
    template = cv2.imread(template_path)

    result = cv2.matchTemplate(screen_np, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= confidence:
        h, w = template.shape[:2]
        return (max_loc[0] + w//2, max_loc[1] + h//2)
    return None
```

## 远程控制实现

### SSH远程执行
```python
import paramiko

def remote_execute(host, port, username, password, command):
    """通过SSH在远程机器执行命令"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode()
```

## 典型工作流程

### 流程1: 自动化网页登录
```
1. 截图当前屏幕
2. OCR识别用户名输入框位置
3. 点击输入框
4. 输入用户名
5. Tab切换到密码框
6. 输入密码
7. Tab切换到登录按钮
8. 点击登录
```

### 流程2: 文件自动化管理
```
1. 打开文件管理器 (Win+E)
2. 导航到目标文件夹
3. 创建/重命名/移动文件
4. 关闭文件管理器
```

## 错误处理策略

```python
class AutomationError(Exception):
    """自动化操作异常"""
    pass

def safe_execute(func, max_retries=3):
    """带重试的执行包装器"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise AutomationError(f"Failed after {max_retries} attempts: {e}")
            time.sleep(1)
```

## 安全最佳实践

1. **操作前确认**: 涉及删除、重要操作需二次确认
2. **日志记录**: 记录所有自动化操作及时间戳
3. **超时设置**: 每个操作设置合理超时
4. **紧急停止**: 提供紧急停止机制 (Esc键可中断)
5. **沙箱环境**: 敏感操作在沙箱中测试
