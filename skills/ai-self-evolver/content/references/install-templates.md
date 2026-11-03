# 安装脚本模板

## 自动安装工作流

```
检测项目 → 验证安全 → 克隆代码 → 安装依赖 → 测试运行 → 记录安装
```

## 1. GitHub项目安装模板

### Python项目

```bash
#!/bin/bash
REPO_URL="$1"
PROJECT_NAME="$2"

# 克隆仓库
git clone "$REPO_URL" "/tmp/$PROJECT_NAME"
cd "/tmp/$PROJECT_NAME"

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "pyproject.toml" ]; then
    pip install -e .
elif [ -f "setup.py" ]; then
    pip install -e .
fi

# 验证安装
if [ -f "test_*.py" ] || [ -f "*_test.py" ]; then
    python -m pytest --version 2>/dev/null && pytest
fi

# 移动到安装目录
mkdir -p ~/ai-tools/
cp -r "/tmp/$PROJECT_NAME" ~/ai-tools/

echo "✅ 安装完成: $PROJECT_NAME"
```

### Node.js项目

```bash
#!/bin/bash
REPO_URL="$1"
PROJECT_NAME="$2"

git clone "$REPO_URL" "/tmp/$PROJECT_NAME"
cd "/tmp/$PROJECT_NAME"

# 安装依赖
npm install

# 构建项目
if [ -f "package.json" ]; then
    if grep -q '"build"' package.json; then
        npm run build
    fi
fi

# 全局安装（如适用）
if grep -q '"bin"' package.json; then
    npm install -g .
fi

# 移动到安装目录
mkdir -p ~/ai-tools/
cp -r "/tmp/$PROJECT_NAME" ~/ai-tools/

echo "✅ 安装完成: $PROJECT_NAME"
```

## 2. 安装前验证脚本

```python
#!/usr/bin/env python3
"""
install_validator.py - 安装前安全验证
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

class InstallValidator:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.issues = []
        self.warnings = []

    def validate_all(self) -> bool:
        checks = [
            self.check_file_size,
            self.check_suspicious_files,
            self.check_network_calls,
            self.check_environment_vars,
            self.check_system_commands,
            self.check_dependencies
        ]

        results = [check() for check in checks]
        return all(results) and len(self.issues) == 0

    def check_file_size(self) -> bool:
        """检查文件大小是否合理"""
        max_file_size = 10 * 1024 * 1024  # 10MB

        for file in self.repo_path.rglob("*"):
            if file.is_file() and file.stat().st_size > max_file_size:
                self.warnings.append(f"大文件: {file.name}")

        return True

    def check_suspicious_files(self) -> bool:
        """检测可疑文件"""
        suspicious = [
            "*.exe", "*.dll", "*.so", "*.dylib",
            "*.jar", "*.war", "*.class"
        ]

        for pattern in suspicious:
            matches = list(self.repo_path.glob(f"**/{pattern}"))
            if matches:
                self.warnings.append(f"二进制文件: {pattern}")

        return True

    def check_network_calls(self) -> bool:
        """检查是否有可疑的网络调用"""
        network_patterns = [
            r"curl\s+",
            r"wget\s+",
            r"requests\.get\(",
            r"http\.request\(",
            r"os\.system\s*\(\s*[\"'](curl|wget|nc)"
        ]

        for py_file in self.repo_path.glob("**/*.py"):
            content = py_file.read_text()
            for pattern in network_patterns:
                if re.search(pattern, content):
                    self.warnings.append(f"网络调用在: {py_file.name}")

        return True

    def check_environment_vars(self) -> bool:
        """检查环境变量使用"""
        env_patterns = [
            r"os\.environ\[",
            r"os\.getenv\(",
            r"dotenv"
        ]

        for py_file in self.repo_path.glob("**/*.py"):
            content = py_file.read_text()
            for pattern in env_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    self.warnings.append(f"环境变量在: {py_file.name}")

        return True

    def check_system_commands(self) -> bool:
        """检查系统命令执行"""
        dangerous = [
            r"os\.system\(",
            r"subprocess\.call\(",
            r"eval\(",
            r"exec\(",
            r"__import__"
        ]

        for py_file in self.repo_path.glob("**/*.py"):
            content = py_file.read_text()
            for pattern in dangerous:
                if re.search(pattern, content):
                    self.issues.append(f"危险操作: {py_file.name}")

        return len(self.issues) == 0

    def check_dependencies(self) -> bool:
        """检查依赖安全性"""
        if not (self.repo_path / "requirements.txt").exists():
            return True

        requirements = (self.repo_path / "requirements.txt").read_text()

        # 高风险依赖检查
        risky_packages = [
            "pty", "ptyprocess", "termios",
            "socket", "subprocess", "multiprocessing"
        ]

        for pkg in risky_packages:
            if pkg in requirements.lower():
                self.warnings.append(f"系统级依赖: {pkg}")

        return True

    def report(self) -> str:
        output = []
        output.append("=== 安装安全验证报告 ===\n")

        if self.issues:
            output.append("❌ 问题 (必须修复):")
            for issue in self.issues:
                output.append(f"  - {issue}")

        if self.warnings:
            output.append("\n⚠️ 警告 (建议关注):")
            for warning in self.warnings:
                output.append(f"  - {warning}")

        if not self.issues and not self.warnings:
            output.append("✅ 验证通过")

        return "\n".join(output)
```

## 3. 依赖安装脚本

```bash
#!/bin/bash
# install_dependencies.sh - 智能依赖安装

set -e

PROJECT_DIR="$1"

cd "$PROJECT_DIR"

echo "📦 开始安装依赖..."

# 检测包管理器
if [ -f "Pipfile" ]; then
    echo "使用 pipenv..."
    pipenv install

elif [ -f "poetry.lock" ]; then
    echo "使用 poetry..."
    poetry install

elif [ -f "requirements.txt" ]; then
    echo "使用 pip (requirements.txt)..."
    pip install -r requirements.txt --user

    # 检查是否有可选依赖
    if [ -f "requirements-dev.txt" ]; then
        echo "安装开发依赖..."
        pip install -r requirements-dev.txt --user
    fi

elif [ -f "pyproject.toml" ]; then
    echo "使用 pip (pyproject.toml)..."
    pip install -e .

elif [ -f "setup.py" ]; then
    echo "使用 setup.py..."
    pip install -e .

elif [ -f "package.json" ]; then
    echo "使用 npm..."
    npm install

    if [ -f "package-lock.json" ]; then
        echo "使用 package-lock.json..."
        npm ci
    fi

    if [ -f ".nvmrc" ]; then
        echo "使用 .nvmrc 指定版本..."
        nvm use
    fi

elif [ -f "go.mod" ]; then
    echo "使用 Go modules..."
    go mod download

elif [ -f "Cargo.toml" ]; then
    echo "使用 Cargo..."
    cargo build --release

else
    echo "⚠️ 未检测到包管理器配置文件"
    echo "请手动安装依赖"
    exit 1
fi

echo "✅ 依赖安装完成"
```

## 4. 安装后验证脚本

```bash
#!/bin/bash
# verify_installation.sh - 验证安装成功

set -e

PROJECT_NAME="$1"
PROJECT_DIR="$2"

echo "🔍 验证安装..."

cd "$PROJECT_DIR"

# 检查关键文件是否存在
REQUIRED_FILES=(
    "README.md"
    "setup.py"  # 或 package.json, go.mod 等
)

MISSING=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "⚠️ 缺少文件: $file"
        MISSING=1
    fi
done

# 运行测试（如有）
if [ -f "pytest.ini" ] || [ -d "tests" ]; then
    echo "🧪 运行测试..."
    if command -v pytest &> /dev/null; then
        pytest -v || echo "⚠️ 部分测试失败"
    fi
fi

# 检查CLI命令
if [ -f "setup.py" ]; then
    if grep -q "console_scripts" setup.py; then
        echo "⚙️ 检查CLI命令..."
        pip show "$PROJECT_NAME" | grep -q "Location"
    fi
fi

# 验证Python包
if [ -f "setup.py" ] || [ -f "pyproject.toml" ]; then
    echo "🐍 验证Python包..."
    python -c "import $PROJECT_NAME; print('✅ 导入成功')"
fi

echo ""
echo "================================"
echo "✅ 安装验证完成: $PROJECT_NAME"
echo "📁 安装位置: $PROJECT_DIR"
echo "================================"
```

## 5. 自动化安装执行脚本

```bash
#!/bin/bash
# auto_install.sh - 全自动安装脚本

GITHUB_URL="$1"
PROJECT_NAME=$(basename "$GITHUB_URL" .git)

echo "🚀 开始安装: $PROJECT_NAME"
echo "📥 源: $GITHUB_URL"

# 创建临时目录
WORK_DIR=$(mktemp -d)
trap "rm -rf $WORK_DIR" EXIT

# 克隆
echo "📡 克隆仓库..."
git clone --depth 1 "$GITHUB_URL" "$WORK_DIR/$PROJECT_NAME"

cd "$WORK_DIR/$PROJECT_NAME"

# 安全验证
echo "🔒 安全检查..."
python3 /path/to/install_validator.py .

# 安装依赖
echo "📦 安装依赖..."
bash /path/to/install_dependencies.sh "$WORK_DIR/$PROJECT_NAME"

# 安装到系统
echo "⚙️ 安装到系统..."
mkdir -p ~/ai-tools
cp -r "$WORK_DIR/$PROJECT_NAME" ~/ai-tools/

# 验证
echo "✅ 验证安装..."
bash /path/to/verify_installation.sh "$PROJECT_NAME" "~/ai-tools/$PROJECT_NAME"

echo ""
echo "🎉 安装成功！"
echo "使用方式请查看: ~/ai-tools/$PROJECT_NAME/README.md"
```

## 使用示例

```bash
# 安装 auto-gpt
./auto_install.sh https://github.com/Significant-Gravitas/Auto-GPT.git

# 安装 langchain
./auto_install.sh https://github.com/hwchase17/langchain.git
```
