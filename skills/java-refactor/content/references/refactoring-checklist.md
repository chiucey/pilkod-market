# Java重构质量检查清单（专家级）

## 阶段一：重构前诊断清单

### 1.1 业务理解
- [ ] 理解代码的业务逻辑和目的
- [ ] 识别代码的输入输出契约
- [ ] 了解代码的依赖关系
- [ ] 确定代码的关键路径和边界条件
- [ ] 识别代码的利益相关者（谁会受到影响）
- [ ] 记录业务规则和不变量

### 1.2 测试覆盖评估
- [ ] 代码是否有单元测试
- [ ] 测试覆盖范围是否充分（>70%）
- [ ] 是否需要补充测试用例
- [ ] 是否有集成测试
- [ ] 是否有端到端测试
- [ ] 边界条件和异常场景是否有测试

### 1.3 代码分析
- [ ] 运行静态分析工具（SonarQube/PMD/Checkstyle）
- [ ] 识别代码味道（Code Smells）
- [ ] 分析圈复杂度
- [ ] 识别重复代码
- [ ] 分析依赖关系
- [ ] 识别性能热点

### 1.4 重构规划
- [ ] 列出所有需要重构的问题
- [ ] 按风险程度排序重构任务
- [ ] 识别重构依赖关系
- [ ] 确定安全边际
- [ ] 制定回滚计划
- [ ] 确定验收标准

## 阶段二：重构执行清单

### 2.1 重构前准备
- [ ] 创建代码快照或分支
- [ ] 备份相关配置
- [ ] 通知相关团队成员
- [ ] 准备测试环境
- [ ] 设置持续集成监控

### 2.2 单步执行原则
- [ ] 每次只做一个重构操作
- [ ] 重构后立即运行测试
- [ ] 确保测试通过后再继续
- [ ] 保持代码在可工作状态
- [ ] 使用IDE的重构工具（IntelliJ IDEA/Eclipse）

### 2.3 功能保持验证
- [ ] 所有测试用例通过
- [ ] 边界条件处理一致
- [ ] 异常行为保持一致
- [ ] 日志输出保持一致
- [ ] API契约保持不变
- [ ] 数据格式保持一致

### 2.4 提交管理
- [ ] 原子提交（一个重构操作一个commit）
- [ ] 详细的commit message
- [ ] 关联相关Issue/Task
- [ ] 代码审查通过

## 阶段三：重构后验证清单

### 3.1 功能验证
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 端到端测试通过
- [ ] 手动功能测试完成
- [ ] 边界条件测试通过
- [ ] 异常场景测试通过

### 3.2 代码质量验证

#### 可读性检查
- [ ] 类名、方法名、变量名见名知意
- [ ] 方法长度不超过40行
- [ ] 类长度不超过500行
- [ ] 注释解释"为什么"而非"是什么"
- [ ] 没有神秘的数字常量（使用枚举或常量）
- [ ] 缩进和格式化一致
- [ ] 没有死代码

#### 可维护性检查
- [ ] 消除重复代码（DRY原则）
- [ ] 每个类职责单一（SRP）
- [ ] 每个方法职责单一
- [ ] 方法圈复杂度 ≤ 10
- [ ] 参数数量 ≤ 3（考虑参数对象）
- [ ] 没有过深的嵌套（≤ 4层）
- [ ] 减少循环嵌套
- [ ] 使用卫语句减少嵌套

#### 可扩展性检查
- [ ] 遵循SOLID原则
- [ ] 依赖抽象而非具体实现（DIP）
- [ ] 面向接口编程
- [ ] 易于添加新功能
- [ ] 易于修改现有功能
- [ ] 使用合适的设计模式

### 3.3 技术检查

#### 资源管理
- [ ] 使用try-with-resources管理资源
- [ ] 资源正确关闭（流、连接等）
- [ ] 没有资源泄漏

#### 并发安全
- [ ] 线程安全（如适用）
- [ ] 正确的同步机制
- [ ] 避免死锁
- [ ] 不可变对象优先

#### 异常处理
- [ ] 使用有意义的异常类型
- [ ] 异常信息清晰
- [ ] 异常不会吞没
- [ ] 正确使用try-catch-finally

#### 性能考虑
- [ ] 没有不必要的对象创建
- [ ] 集合操作高效
- [ ] 数据库查询优化
- [ ] 没有N+1查询问题
- [ ] 字符串拼接使用StringBuilder

### 3.4 安全检查

#### 输入验证
- [ ] 所有输入都经过验证
- [ ] 防止SQL注入
- [ ] 防止XSS攻击
- [ ] 防止CSRF攻击
- [ ] 敏感数据加密

#### 认证授权
- [ ] 正确的权限检查
- [ ] 会话管理安全
- [ ] 密码存储安全

#### 最佳实践
- [ ] 不在日志中记录敏感信息
- [ ] 错误信息不泄露内部细节
- [ ] 使用安全的随机数生成器

## 阶段四：文档与沟通

### 4.1 代码文档
- [ ] 类有JavaDoc注释
- [ ] 公共API有文档
- [ ] 复杂算法有解释
- [ ] TODO注释已处理

### 4.2 技术文档
- [ ] API文档更新
- [ ] 架构图更新
- [ ] 数据库schema更新
- [ ] 部署文档更新

### 4.3 沟通交接
- [ ] 向团队说明变更
- [ ] 更新维护文档
- [ ] 记录已知限制
- [ ] 交接测试要点

## Java编码规范速查表

### 命名规范
| 元素 | 规范 | 正确示例 | 错误示例 |
|------|------|----------|----------|
| 类名 | UpperCamelCase | `UserAccountService` | `userService`, `User_service` |
| 接口名 | UpperCamelCase | `PaymentGateway` | `IPaymentGateway` |
| 方法名 | lowerCamelCase | `getUserById` | `GetUserById`, `get_user_by_id` |
| 变量名 | lowerCamelCase | `activeUsers` | `ActiveUsers`, `active_users` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` | `MAX_RETRY`, `maxRetryCount` |
| 包名 | 全小写 | `com.example.service` | `com.Example.Service` |
| 枚举值 | UPPER_SNAKE_CASE | `ORDER_STATUS.PENDING` | `OrderStatus.Pending` |

### 现代Java特性检查清单

#### Java 8+
- [ ] 使用Lambda表达式替代匿名内部类
- [ ] 使用Stream API处理集合
- [ ] 使用Optional处理空值
- [ ] 使用方法引用（::）
- [ ] 使用接口默认方法

#### Java 10+
- [ ] 使用var进行局部变量类型推断
- [ ] 不可变集合工厂方法（List.of(), Set.of()）

#### Java 14+
- [ ] 使用switch表达式
- [ ] 使用instanceof模式匹配

#### Java 16+
- [ ] 使用record定义不可变数据类
- [ ] 使用文本块（Text Blocks）

#### Java 17+
- [ ] 使用sealed类
- [ ] 使用模式匹配增强

### 代码示例对照

#### ✅ 推荐做法
```java
// Optional处理
public Optional<User> findById(Long id) {
    return Optional.ofNullable(userRepository.findOne(id));
}

// Stream API
List<String> activeEmails = users.stream()
    .filter(User::isActive)
    .map(User::getEmail)
    .collect(Collectors.toList());

// try-with-resources
try (Connection conn = dataSource.getConnection()) {
    // 使用连接
}

// record（Java 16+）
public record UserDTO(Long id, String name) { }

// switch表达式
int result = switch (day) {
    case MONDAY, FRIDAY, SUNDAY -> 6;
    case TUESDAY -> 7;
    default -> 8;
};
```

#### ❌ 避免做法
```java
// null检查链
if (user != null) {
    if (user.getProfile() != null) {
        if (user.getProfile().getAddress() != null) {
            return user.getProfile().getAddress();
        }
    }
}

// 冗余循环
List<String> emails = new ArrayList<>();
for (User user : users) {
    if (user.isActive()) {
        emails.add(user.getEmail());
    }
}

// 手动资源管理
Connection conn = null;
try {
    conn = dataSource.getConnection();
} finally {
    if (conn != null) conn.close();
}
```

## 重构验收标准

### 必须满足（Blocker）
- [ ] 所有测试通过
- [ ] 功能保持100%一致
- [ ] 无编译错误
- [ ] 无致命警告

### 强烈建议（Critical）
- [ ] 圈复杂度 ≤ 10
- [ ] 方法行数 ≤ 40
- [ ] 无重复代码
- [ ] 无安全漏洞

### 建议优化（Major）
- [ ] 类行数 ≤ 500
- [ ] 圈复杂度 ≤ 5
- [ ] 测试覆盖率 ≥ 70%
- [ ] 消除所有警告

### 可选改进（Minor）
- [ ] 方法行数 ≤ 20
- [ ] 类行数 ≤ 300
- [ ] 测试覆盖率 ≥ 90%
- [ ] 添加性能优化
