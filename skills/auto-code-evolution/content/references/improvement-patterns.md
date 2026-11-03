# 代码改进模式参考

## 性能优化模式

### 1. 算法替换
```
Before: O(n²) - 嵌套循环遍历
for i in items:
    for j in items:
        if i.id == j.id:
            process(i)

After: O(n) - 哈希表查找
item_map = {item.id: item for item in items}
for i in items:
    if i.id in item_map:
        process(i)
```

### 2. 缓存复用
```
Before: 每次调用重新计算
def get_user_stats(user_id):
    data = expensive_db_query(user_id)
    return analyze(data)

After: 缓存结果
_cache = {}
def get_user_stats(user_id):
    if user_id not in _cache:
        data = expensive_db_query(user_id)
        _cache[user_id] = analyze(data)
    return _cache[user_id]
```

### 3. 懒加载
```
Before: 初始化时加载全部
class Report:
    def __init__(self):
        self.all_data = load_everything()

After: 按需加载
class Report:
    def __init__(self):
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = load_everything()
        return self._data
```

## 安全加固模式

### 1. 输入验证
```
Before: 直接使用用户输入
query = f"SELECT * FROM users WHERE name = '{username}'"

After: 参数化查询
query = "SELECT * FROM users WHERE name = ?"
cursor.execute(query, (username,))
```

### 2. 敏感数据处理
```
Before: 明文日志
logger.info(f"User {user_id} logged in with password {password}")

After: 脱敏处理
logger.info(f"User {user_id} logged in")  # 不记录敏感信息
```

### 3. 权限检查
```
Before: 信任客户端
def delete_document(doc_id):
    db.delete(doc_id)

After: 验证权限
def delete_document(doc_id, user):
    if not user.can_delete(doc_id):
        raise PermissionError()
    db.delete(doc_id)
```

## 可维护性模式

### 1. 提取方法
```
Before: 长函数
def process_order(order):
    # 50行代码处理订单

After: 分解职责
def process_order(order):
    validate_order(order)
    calculate_totals(order)
    apply_discounts(order)
    persist_order(order)
    notify_customer(order)
```

### 2. 消除魔法数字
```
Before: 魔法数字
if age > 18 and score > 60:
    return "Pass"

After: 有名常量
ADULT_AGE = 18
PASSING_SCORE = 60

if age > ADULT_AGE and score > PASSING_SCORE:
    return "Pass"
```

### 3. 使用上下文管理器
```
Before: 手动资源管理
file = open("data.txt")
try:
    content = file.read()
finally:
    file.close()

After: 自动资源管理
with open("data.txt") as file:
    content = file.read()
```

## 重构检查清单

### 代码异味识别
- [ ] 函数超过50行？
- [ ] 参数超过5个？
- [ ] 重复代码超过3处？
- [ ] 类承担过多职责？
- [ ] 存在紧耦合依赖？

### 改进优先级
1. **Critical**: 安全漏洞、崩溃风险
2. **High**: 性能问题、严重代码异味
3. **Medium**: 代码可读性、轻微冗余
4. **Low**: 命名规范、代码风格
