# 安全漏洞模式识别

## SQL 注入常见模式

### 危险模式 ❌
```javascript
// 字符串拼接
const query = "SELECT * FROM users WHERE id = " + userId;

// 模板字符串
const query = `SELECT * FROM users WHERE name = '${username}'`;

// 执行原始 SQL
db.query("SELECT * FROM users WHERE id = " + req.params.id);
```

### 安全模式 ✅
```javascript
// 参数化查询
const query = "SELECT * FROM users WHERE id = ?";
db.execute(query, [userId]);

// ORM
const user = await User.findById(userId);
```

## XSS 攻击向量

### 危险模式 ❌
```javascript
// 直接插入 HTML
element.innerHTML = userInput;

// URL 参数未转义
<a href="/search?q=<script>...">点击</a>

// JSON 未转义直接输出
res.json(userData) // 包含 <script> 标签的用户名
```

### 安全模式 ✅
```javascript
// 文本内容转义
element.textContent = userInput;

// URL 参数编码
const safeUrl = `/search?q=${encodeURIComponent(query)}`;

// React 自动转义（除非使用 dangerouslySetInnerHTML）
<div>{userInput}</div>
```

## 权限绕过模式

### 危险模式 ❌
```javascript
// 仅前端验证
if (isAdmin) { showAdminPanel(); } // 可被绕过

// 缺失服务端验证
router.get('/admin/users', (req, res) => {
  // 假设用户已登录，未检查权限
  res.json(allUsers);
});

// 依赖客户端数据
const isOwner = req.body.isOwner; // 不可信
```

### 安全模式 ✅
```javascript
// 服务端强制验证
router.get('/admin/users', requireAdmin, (req, res) => {
  res.json(allUsers);
});

// 中间件验证
const requireAuth = (req, res, next) => {
  if (!req.user || !req.user.isAdmin) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  next();
};
```

## 敏感信息泄露

### 危险模式 ❌
```javascript
// 硬编码密钥
const API_KEY = "sk-1234567890abcdef";

// 错误信息泄露路径
catch (err) {
  res.send("Error in " + err.stack);
}

// 日志记录敏感数据
console.log("Password reset for:", user.password);
```

### 安全模式 ✅
```javascript
// 环境变量
const API_KEY = process.env.API_KEY;

// 安全错误处理
catch (err) {
  logger.error(err); // 仅内部日志
  res.status(500).json({ error: 'Internal server error' });
};

// 日志脱敏
logger.info("Password reset for:", { userId: user.id });
```

## 输入验证缺失

### 危险模式 ❌
```javascript
// 无验证
const age = req.body.age; // 可能是负数、字符串、对象

// 类型假设
const count = parseInt(req.body.count);
db.query(`LIMIT ${count}`); // count 可能是 NaN
```

### 安全模式 ✅
```javascript
// Schema 验证
const schema = Joi.object({
  age: Joi.number().integer().min(0).max(150).required()
});

// 显式类型和边界检查
const count = parseInt(req.body.count) || 0;
if (count < 0 || count > 100) {
  return res.status(400).json({ error: 'Invalid count' });
}
```
