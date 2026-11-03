---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 5ee6bb5bbb5b912d85baf31d7a71cbba
    PropagateID: 5ee6bb5bbb5b912d85baf31d7a71cbba
    ReservedCode1: 3045022071bd4131f2294bc3ac48ca1bc7bedf40f8b4b1b0158da23277354d63a8f611a9022100e633937247b51e3c03b8696baeb17a679f87dc503f3767bd58f387e7f55cee9b
    ReservedCode2: 3046022100e8926be38434e327a39df9e38b5a100499c727f306c1cab1d3849bf4c83e1377022100fedc33e724c3b9e41e86037ec6706e8d2dbca079a0cc21ebc830ec35fff00039
---

# C/C++ 编码规范参考

## C++ 编码标准

### 现代 C++ 特性使用指南

#### 智能指针替代原始指针

```cpp
// ❌ 不推荐
void process() {
    auto* ptr = new SomeClass();
    ptr->doSomething();
    delete ptr;  // 容易忘记删除
}

// ✅ 推荐
void process() {
    auto ptr = std::make_unique<SomeClass>();
    ptr->doSomething();  // 自动管理内存
}
```

#### 范围 for 循环

```cpp
std::vector<int> vec = {1, 2, 3};

// ❌ 不推荐
for (auto it = vec.begin(); it != vec.end(); ++it) {
    std::cout << *it << " ";
}

// ✅ 推荐
for (const auto& val : vec) {
    std::cout << val << " ";
}
```

#### 自动类型推导

```cpp
// ❌ 不推荐
std::map<std::string, std::vector<int>>::const_iterator it = map.begin();

// ✅ 推荐
const auto it = map.cbegin();
```

#### Lambda 表达式

```cpp
// 简单 lambda
auto is_even = [](int n) { return n % 2 == 0; };

// 带捕获的 lambda
int multiplier = 2;
auto multiply = [multiplier](int n) { return n * multiplier; };

// 在 STL 算法中使用
std::vector<int> nums = {1, 2, 3, 4, 5};
std::for_each(nums.begin(), nums.end(), [](int& n) { n *= 2; });
```

### STL 容器选择指南

| 需求 | 推荐容器 | 原因 |
|------|----------|------|
| 动态数组 | `std::vector` | 连续内存，缓存友好 |
| 头尾操作 | `std::deque` | 两端高效插入 |
| 唯一键集合 | `std::unordered_set` | O(1) 平均查找 |
| 有序集合 | `std::set` | O(log n) 查找，自动排序 |
| 键值对 | `std::unordered_map` | O(1) 平均查找 |
| 栈 | `std::stack` | 适配器容器 |
| 队列 | `std::queue` | 适配器容器 |
| 优先级队列 | `std::priority_queue` | O(log n) 极值访问 |

### 异常处理规范

```cpp
// ✅ 推荐：异常规范
class MyException : public std::exception {
public:
    explicit MyException(const std::string& msg) : message(msg) {}
    const char* what() const noexcept override { return message.c_str(); }
private:
    std::string message;
};

// 使用 noexcept 标记不抛异常的函数
void critical_function() noexcept {
    // 保证不抛出异常
}
```

## C 语言编码标准

### 内存管理要点

```c
// ✅ 正确的内存分配模式
int* allocate_array(size_t size) {
    int* arr = malloc(size * sizeof(int));
    if (arr == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }
    // 初始化
    memset(arr, 0, size * sizeof(int));
    return arr;
}

// 使用后释放
void free_array(int* arr) {
    free(arr);
    arr = NULL;  // 避免悬空指针
}
```

### 错误处理模式

```c
typedef enum {
    SUCCESS = 0,
    ERR_NULL_PTR = -1,
    ERR_INVALID_SIZE = -2,
    ERR_MEMORY = -3
} ErrorCode;

ErrorCode process_data(Data* data, size_t size) {
    if (data == NULL) {
        return ERR_NULL_PTR;
    }
    if (size == 0) {
        return ERR_INVALID_SIZE;
    }
    // 处理逻辑
    return SUCCESS;
}
```

### 预处理宏最佳实践

```c
// ✅ 安全宏定义
#define MAX(a, b) ((a) > (b) ? (a) : (b))

// ✅ 更好的内联函数替代宏
static inline int max(int a, int b) {
    return a > b ? a : b;
}

// ✅ 条件编译保护
#ifdef DEBUG
    #define LOG(fmt, ...) fprintf(stderr, "[DEBUG] " fmt "\n", ##__VA_ARGS__)
#else
    #define LOG(fmt, ...) do {} while(0)
#endif
```

## 跨语言注意事项

### C/C++ 互操作

```cpp
// C++ 中使用 C 代码
extern "C" {
    #include "c_header.h"
}

// C 中调用 C++ 代码
// 在 C++ 头文件中使用
#ifdef __cplusplus
extern "C" {
#endif
    void cpp_function();
// C 代码可调用
#ifdef __cplusplus
}
#endif
```

### 常见陷阱

| 陷阱 | C++ | C |
|------|-----|-----|
| 字符串比较 | `str1 == str2` ❌<br>`str1 == "hello"` ❌<br>`strcmp()` ✅ | 同样使用 `strcmp()` |
| 布尔值 | `bool` 类型 | `int` (0/非0) |
| 循环变量 | 循环内声明 `for (int i=0;...)` | C99 前需提前声明 |
| 布尔运算 | `&& \|\|` | `&& \|\|` 相同 |
| 类型转换 | `static_cast<T>` | `(T)value` |
