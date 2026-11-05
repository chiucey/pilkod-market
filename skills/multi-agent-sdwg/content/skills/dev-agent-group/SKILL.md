---
name: dev-agent-group
description: 开发智能体组技能。用于编码与测试阶段。每个开发智能体专注一个子模块。当用户要求生成代码、编写单元测试、修复bug、审查代码时触发。适配指令微调与强化学习优化。
---

# 开发智能体组

## 核心职责

每个开发智能体专注于一个系统子模块，生成高质量代码，自动生成单元测试，具备代码自修复能力与代码审查能力。

## 通用规范

### 编码规范

- **Python**: PEP8规范
- **JavaScript**: ES6+规范
- **命名**：简洁明了，贴合功能
- **注释**：类/函数需文档字符串，关键逻辑加行注释

### 协作机制

- 维护独立记忆（模块代码规范、接口契约、修复记录）
- 通过共享任务板获取其他模块接口信息
- 遵循架构师维护的契约

---

## 技能1：代码生成

### 输入

- 模块职责
- 接口定义（OpenAPI/GraphQL）
- 技术栈
- 编码规范

### 执行流程

1. **环境准备**：创建代码文件结构
2. **核心实现**：
   - 严格遵循接口契约
   - 处理异常（参数错误、网络异常、数据库失败）
   - 遵循单一职责原则
3. **数据库操作**：使用ORM框架，禁止直接拼接SQL
4. **代码质量**：无语法错误、逻辑严谨、可直接运行

### 输出格式

```
代码文件名称：XXX
代码内容：
```python
# 完整可运行代码
```
代码说明：
- 代码结构：XXX
- 核心逻辑：XXX
- 关键函数：XXX
- 运行方式：XXX
```

### 示例

```python
# auth_module.py
from typing import Optional
from .exceptions import AuthenticationError

class AuthService:
    """认证服务类

    提供用户登录、登出、token验证等功能
    """

    def __init__(self, user_repository, token_service):
        self.user_repo = user_repository
        self.token_service = token_service

    def login(self, username: str, password: str) -> dict:
        """用户登录

        Args:
            username: 用户名
            password: 密码

        Returns:
            dict: 包含token的用户信息

        Raises:
            AuthenticationError: 认证失败
        """
        # 实现登录逻辑
        pass
```

---

## 技能2：单元测试生成

### 覆盖率目标

- 核心代码覆盖率 ≥ 90%

### 测试框架

- Python: pytest
- Java: JUnit

### 执行流程

1. **正常场景**：核心功能，输入合法
2. **边界场景**：最大值、最小值、空值、临界值
3. **异常场景**：参数错误、数据为空、数据库异常

### 输出格式

```
测试文件名称：XXX
测试覆盖率：XXX%
测试用例分布：
- 正常场景：X个
- 边界场景：X个
- 异常场景：X个

测试代码：
```python
# 完整可运行测试代码
```

运行命令：pytest tests/test_xxx.py -v --cov
```

### 示例

```python
# test_auth_service.py
import pytest
from unittest.mock import Mock
from auth_module import AuthService, AuthenticationError

class TestAuthService:
    """认证服务测试类"""

    @pytest.fixture
    def auth_service(self):
        mock_repo = Mock()
        mock_token = Mock()
        return AuthService(mock_repo, mock_token)

    def test_login_success(self, auth_service):
        """正常登录测试"""
        # Arrange
        auth_service.user_repo.find_by_username.return_value = {'id': 1}

        # Act
        result = auth_service.login('user', 'pass')

        # Assert
        assert 'token' in result

    def test_login_invalid_password(self, auth_service):
        """密码错误测试"""
        # Arrange
        auth_service.user_repo.find_by_username.return_value = None

        # Act & Assert
        with pytest.raises(AuthenticationError):
            auth_service.login('user', 'wrong')
```

---

## 技能3：代码自修复（自愈循环）

### 执行流程

1. **Bug定位**：分析失败日志，定位代码行、函数
2. **原因分析**：语法错误/逻辑错误/异常处理缺失/参数校验不当
3. **代码修复**：
   - 精准修复，不引入新bug
   - 不改变核心功能与接口契约
   - 保持编码规范
4. **验证循环**：修复→测试→验证，最多3次
5. **升级机制**：3次失败后，生成报告升级至架构师

### 输出格式

```
Bug定位：
- 位置：XXX行/XXX函数
- 类型：XXX
- 原因：XXX

第1次修复：
- 修复内容：XXX
- 测试结果：XXX

[第2、3次修复...]

最终修复结果：XXX
自愈日志：XXX

升级报告（若3次失败）：
- 失败日志：XXX
- 定位结果：XXX
- 失败原因分析：XXX
```

---

## 技能4：代码审查

### 审查范围

基于PR Diff，重点审查变更代码

### 审查维度

1. **编码规范**：命名、缩进、注释
2. **逻辑正确性**：贴合模块职责与接口契约
3. **安全性**：SQL注入、XSS、数据泄露
4. **可维护性**：结构清晰、注释完整
5. **性能**：冗余查询、循环效率
6. **兼容性**：模块集成、接口调用

### 输出格式

```
评审结论：XXX（需修改后合并/无需修改可合并/存在重大问题驳回）

必须修改：
1. 位置：XXX，问题：XXX，改进建议：XXX

建议修改：
1. 位置：XXX，问题：XXX，改进建议：XXX

无需修改：XXX
```

---

## 训练方法

- **指令微调**：基于GitHub高星项目"需求→代码→测试→修复"链式样本
- **强化学习**：
  - 编译通过/测试通过 → 正向奖励
  - 编译失败/测试失败 → 负向奖励
- **记忆维护**：每个智能体维护独立记忆

---

## 输出产物

| 产物 | 用途 |
|------|------|
| 子模块代码 | 系统功能实现 |
| 单元测试代码 | 代码质量保障 |
| 自愈日志 | 问题追踪 |
| 代码审查报告 | 代码质量保障 |

---

*参考文档：`references/` 目录*
