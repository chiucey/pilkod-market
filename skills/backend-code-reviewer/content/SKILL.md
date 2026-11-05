---
name: backend-code-reviewer
description: 当用户要求审查代码、分析代码质量、检查后端代码（SpringBoot/MyBatis-Plus）时使用。触发短语：代码审查、代码检查、审查代码、代码质量分析、代码审计、PR审查、拉取请求审查、分析代码问题、扫描代码问题。
---

# 后端代码审查技能

## 审查范围

### 1. 代码规范检查

- **命名规则**：变量、方法、类命名是否符合规范（驼峰命名、语义化）
- **代码格式**：缩进、空格、换行是否统一
- **注释完整性**：核心逻辑是否有必要注释，注释是否准确
- **魔法值**：是否存在未定义的可配置常量
- **方法长度**：单个方法是否过长（建议不超过80行）
- **重复代码**：是否存在可提取的重复代码块

### 2. 潜在 Bug 检测

- **空指针异常（NPE）**：对象使用前是否进行空值判断
- **集合越界**：集合操作是否进行边界检查
- **异常处理**：异常是否被正确捕获和处理
- **逻辑错误**：条件判断、循环逻辑是否存在缺陷
- **事务使用**：事务注解是否正确使用（传播行为、只读事务）

### 3. 安全风险扫描

- **SQL 注入**：SQL拼接是否使用参数化查询
- **硬编码密钥**：是否存在明文密码、Token、密钥
- **接口鉴权**：敏感接口是否缺少权限校验
- **输入校验**：用户输入是否进行参数校验

### 4. 性能问题分析

- **循环冗余**：是否存在可优化的循环逻辑
- **低效 SQL**：是否存在 N+1 查询、全表扫描
- **内存浪费**：是否存在大对象重复创建
- **资源泄漏**：流、连接是否正确关闭

### 5. 架构设计审查

- **分层规范**：Controller/Service/Mapper 职责是否清晰
- **注解使用**：注解使用是否正确、是否滥用
- **依赖引入**：是否存在不必要的依赖

## 问题分级标准

| 级别 | 标识 | 定义 | 处理建议 |
|------|------|------|----------|
| 严重 | 🔴 | 可能导致系统崩溃、数据丢失、安全漏洞 | 必须立即修复 |
| 高危 | 🟠 | 可能导致功能异常、性能严重下降 | 应尽快修复 |
| 中等 | 🟡 | 代码规范问题、潜在风险 | 建议修复 |
| 建议 | 🟢 | 代码优化建议、最佳实践 | 可选择性采纳 |

## SpringBoot + MyBatis-Plus 专项规则

### Controller 层规范

- 禁止在 Controller 中编写业务逻辑
- 参数校验必须使用 `@Valid` 或 `@Validated` 注解
- 统一返回格式使用 ResponseEntity 或统一响应类

```java
// ✅ 正确示例
@RestController
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping("/users")
    public ResponseEntity<Result<Long>> createUser(@Valid @RequestBody UserDTO dto) {
        Long id = userService.createUser(dto);
        return ResponseEntity.ok(Result.success(id));
    }
}

// ❌ 错误示例 - 业务逻辑放在Controller
@PostMapping("/users")
public User createUser(@RequestBody UserDTO dto) {
    // 直接在Controller处理业务逻辑
    User user = new User();
    user.setName(dto.getName());
    userMapper.insert(user);
    return user;
}
```

### Service 层规范

- 业务逻辑必须集中在 Service 层
- `@Transactional` 使用正确：
  - 只读操作不添加事务
  - 注意事务传播行为
  - 事务方法避免直接调用同类方法

```java
// ✅ 正确示例
@Service
@RequiredArgsConstructor
public class UserService {

    private final UserMapper userMapper;

    @Transactional(rollbackFor = Exception.class)
    public void updateUser(Long id, UserDTO dto) {
        User user = userMapper.selectById(id);
        if (user == null) {
            throw new BusinessException("用户不存在");
        }
        BeanUtils.copyProperties(dto, user);
        userMapper.updateById(user);
    }
}

// ❌ 错误示例 - 只读操作添加事务
@Transactional
public User getUser(Long id) {
    return userMapper.selectById(id);
}
```

### Mapper 层规范

- 禁止在 Mapper 接口中写复杂 SQL
- 复杂查询必须使用 XML 编写
- SQL 语句必须使用参数化查询，防止注入

```java
// ✅ 正确示例 - 简单查询在接口中
@Select("SELECT * FROM user WHERE id = #{id}")
User selectById(Long id);

// ✅ 正确示例 - 复杂查询使用XML
List<User> selectUserList(UserQuery query);
```

```xml
<!-- mapper/UserMapper.xml -->
<select id="selectUserList" resultType="com.example.entity.User">
    SELECT * FROM user
    <where>
        <if test="name != null and name != ''">
            AND name LIKE CONCAT('%', #{name}, '%')
        </if>
    </where>
</select>

// ❌ 错误示例 - Mapper中写复杂SQL
@Select("SELECT u.*, r.role_name FROM user u LEFT JOIN role r ON u.role_id = r.id WHERE u.status = #{status}")
List<UserVO> selectUsersWithRole(Integer status);
```

### 实体类规范

- 必须使用 Lombok 注解（@Data、@TableName 等）
- 避免重复 getter/setter 方法
- 字段命名符合数据库规范
- 使用 MyBatis-Plus 的 @TableField 处理特殊映射

```java
// ✅ 正确示例
@Data
@TableName("sys_user")
public class User {

    @TableId(type = IdType.AUTO)
    private Long id;

    @TableField("user_name")
    private String userName;

    private Integer status;

    @TableField(exist = false)
    private String extraField; // 非数据库字段
}

// ❌ 错误示例 - 手动编写getter/setter
public class User {
    private Long id;
    private String name;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}
```

### 异常处理规范

- 统一使用全局异常处理器
- 禁止在业务代码中 try-catch 吞掉异常
- 禁止使用 catch (Exception e) 万能捕获
- 自定义业务异常使用统一异常码

```java
// ✅ 正确示例 - 全局异常处理器
@RestControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusinessException(BusinessException e) {
        return Result.error(e.getCode(), e.getMessage());
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidException(MethodArgumentNotValidException e) {
        String message = e.getBindingResult().getFieldError().getDefaultMessage();
        return Result.error(400, message);
    }
}

// ❌ 错误示例 - 吞掉异常
try {
    userMapper.deleteById(id);
} catch (Exception e) {
    // 什么都不做，异常被吞掉
}

// ❌ 错误示例 - 万能捕获
try {
    // some code
} catch (Exception e) {
    log.error("error", e);
}
```

## 输出格式

### 审查报告结构

```
# 代码审查报告

## 📊 审查概览

| 项目 | 数量 |
|------|------|
| 审查文件数 | X |
| 🔴 严重问题 | X |
| 🟠 高危问题 | X |
| 🟡 中等问题 | X |
| 🟢 建议优化 | X |

## 🔴 严重问题

### 1. [文件路径:行号] 问题标题

**问题说明**：详细描述问题

**风险影响**：说明可能造成的影响

**修复代码**：
```java
// 修复前
[错误代码]

// 修复后
[正确代码]
```

---

## 🟠 高危问题

[同上格式]

---

## 🟡 中等问题

[同上格式]

---

## 🟢 建议优化

[同上格式]

---

## 📝 审查总结

[总结性描述]
```

## 执行流程

1. **文件扫描**：自动扫描项目中的 Java 源文件
2. **规则匹配**：根据审查范围逐项检查
3. **问题分类**：按严重程度分级
4. **报告生成**：输出结构化审查报告

## 审查原则

- 所有输出内容贴合项目实际，不生成无关内容
- 优先给出可落地的修复方案
- 避免空泛建议，每条建议必须明确
- 避免误报，不对合理代码逻辑进行误判
- 保持输出干净，不添加无关注释和签名
