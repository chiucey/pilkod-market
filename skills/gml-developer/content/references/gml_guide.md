# GML完整参考指南

基于GameMaker官方教程PDF提取，涵盖GML核心概念与语法。

---

## 一、数据类型与变量

### 1.1 基本数据类型

| 类型 | 示例 | 说明 |
|------|------|------|
| `real` | 100, 2.456575, -56 | 64位双精度浮点数/整数 |
| `string` | "Hello world!" | 双引号包裹的字符序列 |
| `bool` | true, false | 布尔值 |
| `array` | `[1, 2, 3]` | 数组类型 |
| `undefined` | 未初始化变量 | 未定义值 |

**整数溢出**：GML整数为64位有符号，超出范围会溢出（最大9223372036854775807 → 最小-9223372036854775808）

### 1.2 变量声明与赋值

```javascript
_score = 5000;              // 实例变量
var temp = 10;             // 局部变量（函数内）
global.player_name = "";    // 全局变量
```

**组合赋值运算符**：
```javascript
x += 5;    // x = x + 5
x -= 3;    // x = x - 3
x *= 2;    // x = x * 2
x /= 4;    // x = x / 4
x %= 7;    // x = x % 7
```

**递增/递减运算符**：
```javascript
++x;    // 前置递增（先加后用）
x++;    // 后置递增（先用后加）
--x;    // 前置递减
x--;    // 后置递减
```

### 1.3 变量作用域

| 作用域类型 | 说明 | 声明方式 |
|------------|------|----------|
| 全局变量 | 程序任意位置可访问 | `global.xxx` |
| 实例变量 | 实例生命周期内存在 | 直接赋值 |
| 局部变量 | 函数/事件结束销毁 | `var xxx` |
| 静态变量 | 函数首次调用后保持 | `static xxx` |

**注意**：GML无块级嵌套作用域，`{}`不创建新的变量层级。

---

## 二、常量

### 2.1 宏常量（#macro）

```javascript
#macro ALIEN_POINTS 150
#macro MAX_ENEMIES 10
```

**特点**：编译时替换，不可修改，命名惯例为全大写。

### 2.2 枚举常量（enum）

```javascript
enum difficulty {NOVICE, EASY, NORMAL, HARD, UNBEATABLE}
// 默认值: NOVICE=0, EASY=1, NORMAL=2, HARD=3, UNBEATABLE=4

enum ship_cost {FIGHTER_COST=25, BOMBER_COST, CRUISER_COST=50}
// FIGHTER_COST=25, BOMBER_COST=26, CRUISER_COST=50

// 访问枚举成员
my_difficulty = difficulty.EASY;
```

---

## 三、运算符

### 3.1 算术运算符

| 运算符 | 名称 | 示例 |
|--------|------|------|
| + | 加法 | `7 + 3 = 10` |
| - | 减法 | `7 - 3 = 4` |
| * | 乘法 | `7 * 3 = 21` |
| / | 除法 | `7 / 3 = 2.33` |
| div | 整除 | `7 div 3 = 2` |
| % / mod | 模除 | `7 % 3 = 1` |

**优先级**：括号`()` > 乘除`*/div%` > 加减`+-`

### 3.2 关系运算符

| 运算符 | 意义 |
|--------|------|
| == | 等于 |
| != | 不等于 |
| > | 大于 |
| < | 小于 |
| >= | 大于等于 |
| <= | 小于等于 |

### 3.3 逻辑运算符

| 运算符 | 说明 |
|--------|------|
| && | 逻辑与 |
| \|\| | 逻辑或 |
| ! | 逻辑非 |

---

## 四、分支语句

### 4.1 if语句

```javascript
if (expression)
{
    statement;
}
// 或单行形式
if (expression) statement;
```

### 4.2 else子句

```javascript
if (expression)
    statement1;
else
    statement2;
```

### 4.3 else if链

```javascript
if (score >= 90)
    grade = "A";
else if (score >= 80)
    grade = "B";
else if (score >= 70)
    grade = "C";
else
    grade = "F";
```

### 4.4 switch语句

```javascript
switch (expression)
{
    case constant1:
        code;
        break;
    case constant2:
        code;
        break;
    default:
        code;
}
```

**注意**：
- break语句用于退出switch
- 去掉break后程序继续执行下一case
- 支持整数和字符串，不推荐实数（浮点精度问题）

---

## 五、循环

### 5.1 for循环

```javascript
for (var i = 0; i < 10; ++i)
{
    show_debug_message(i);
}

// 向前计数（0到9）
for (var i = 0; i < 10; ++i) put_out += string(i);

// 向后计数（9到0）
for (var i = 9; i >= 0; --i) put_out += string(i);

// 每次加5（0到50）
for (var i = 0; i <= 50; i += 5) put_out += string(i);
```

### 5.2 嵌套for循环

```javascript
for (var i = 0; i < ROWS; ++i)
{
    for (var j = 0; j < COLUMNS; ++j)
    {
        put_out += board[i][j];
    }
    put_out += "\n";
}
```

### 5.3 while循环

```javascript
var i = 0;
while (i < 10)
{
    show_debug_message(i);
    ++i;
}
```

### 5.4 repeat语句

```javascript
repeat (5)
{
    show_debug_message("Hello");
}
```

### 5.5 break与continue

```javascript
for (var i = 0; i < 10; ++i)
{
    if (i == 5) break;        // 退出循环
    if (i == 3) continue;     // 跳到下次迭代
    show_debug_message(i);
}
```

---

## 六、字符串

### 6.1 创建与连接

```javascript
word1 = "Game";
word2 = string("Over");
phrase = word1 + " " + word2 + "!";  // 连接字符串
phrase += "!";                        // 使用+=连接
```

**注意**：字符串连接时两个操作数都必须是string类型，需要转换时用`string()`函数。

### 6.2 字符串模板（插值）

```javascript
show_debug_message($"Score: {_score}, Lives: {_lives}");
show_debug_message($"Item '{inventory[0]}' has {string_length(inventory[0])} letters");
```

### 6.3 常用字符串函数

| 函数 | 说明 | 示例 |
|------|------|------|
| `string_length(str)` | 获取字符数 | `string_length("Hello")` → 5 |
| `string_char_at(str, pos)` | 获取指定位置字符（从1开始） | `string_char_at("Hello", 2)` → "e" |
| `string_delete(str, pos, len)` | 删除字符 | `string_delete(str, 1, 1)` |
| `string_insert(sub, str, pos)` | 插入字符 | `string_insert("X", str, 3)` |
| `string_copy(str, pos, len)` | 复制子字符串 | `string_copy(str, 1, 4)` |
| `string_pos(sub, str)` | 查找子字符串位置（从1开始，未找到返回0） | `string_pos("Over", str)` |
| `string_replace(str, sub, new)` | 替换子字符串 | `string_replace(str, "old", "new")` |
| `string_lower(str)` | 转为小写 | `string_lower("ABC")` → "abc" |
| `string_upper(str)` | 转为大写 | `string_upper("abc")` → "ABC" |
| `string_repeat(char, count)` | 重复字符 | `string_repeat("!", 3)` → "!!!" |
| `string_split(str, delim)` | 按分隔符拆分为数组 | `string_split(str, ",")` |
| `string_concat(arr)` | 将数组元素合并为字符串 | `string_concat(arr)` |
| `string_format(value, tot, dec)` | 格式化数字 | `string_format(7/3, 0, 5)` → "2.33333" |

---

## 七、数组

### 7.1 创建数组

```javascript
// 使用字面量
numbers = [0, 1, 2, 3, 4, 5];
fruits = ["Apples", "Oranges", "Mangoes"];
empty_arr = [];

// 使用函数
inventory = array_create(10, "");  // 创建10个元素的数组，初始值为""

// 通过索引创建
numbers[0] = 2;
numbers[3] = 8;
```

### 7.2 数组长度

```javascript
array_length(inventory)  // 获取数组长度
```

### 7.3 多维数组

```javascript
// 二维数组
board = [
    ["0", "X", "0"],
    [" ", "X", "X"],
    ["X", "0", "0"]
];

// 访问元素
board[1][0] = "X";

// 创建固定大小的二维数组
chessBoard = array_create(8, array_create(8, ""));
```

### 7.4 数组遍历

```javascript
for (var i = 0; i < array_length(inventory); ++i)
{
    show_debug_message(inventory[i]);
}
```

### 7.5 数组操作

| 函数 | 说明 |
|------|------|
| `array_create(size, value)` | 创建数组 |
| `array_length(arr)` | 获取长度 |
| `array_push(arr, value)` | 末尾添加元素 |
| `array_pop(arr)` | 移除并返回最后一个元素 |
| `array_insert(arr, pos, value)` | 在指定位置插入 |
| `array_delete(arr, pos, len)` | 删除元素 |
| `array_shuffle(arr)` | 打乱数组顺序 |
| `array_reverse(arr)` | 反转数组 |
| `array_first(arr)` | 获取第一个元素 |
| `array_last(arr)` | 获取最后一个元素 |

---

## 八、函数

### 8.1 函数定义

```javascript
function function_name(param1, param2 = default_value)
{
    // 函数体
    return value;
}
```

**示例**：
```javascript
function triple(input)
{
    if is_real(input) return input * 3;
    else if is_string(input) return string_repeat(input, 3);
}

function askText(prompt)
{
    var text = get_string(prompt, "");
    return text;
}
```

### 8.2 默认参数

```javascript
function setDisplay(height, width, depth = 32, fullscreen = true)
{
    // depth和fullscreen有默认值
}

// 合法调用
setDisplay(1680, 1050);           // 使用所有默认值
setDisplay(1680, 1050, 24, true); // 覆盖默认值

// 不合法调用
setDisplay(1680, 1050, false);   // 不能跳过depth直接传fullscreen
```

**规则**：默认参数必须从右到左连续设置。

### 8.3 参数传递

| 参数类型 | 传递方式 | 说明 |
|----------|----------|------|
| 实数、字符串 | 按值传递 | 复制副本 |
| 数组、结构体 | 按引用传递 | 直接修改原数据 |
| 句柄 | 按引用传递 | 直接修改原数据 |

### 8.4 返回值

```javascript
function max(a, b)
{
    if (a > b) return a;
    return b;
}

// 无返回值函数返回undefined
function printMessage(msg)
{
    show_debug_message(msg);
}
```

### 8.5 宏模拟内联函数

```javascript
#macro radiation (_health / 2)

// 多行宏
#macro HELLO show_debug_message("Hello " + \
    string(player_name) + \
    ", how are you?");
```

---

## 九、引用

### 9.1 引用类型

数组、结构体、句柄属于引用类型，直接赋值会共享内存：

```javascript
myScore = [1000];
mikesScore = myScore;  // 创建引用，指向同一内存

myScore[0] += 500;     // 修改后两者都显示1500
```

### 9.2 按引用传递

```javascript
function goodSwap(_x, _y)
{
    var temp = _x[0];
    _x[0] = _y[0];
    _y[0] = temp;
}

goodSwap(myScore, yourScore);  // 会真正交换原变量值
```

### 9.3 复制引用

```javascript
function display(vec)
{
    vec = variable_clone(vec);  // 创建独立副本
    // 对vec的修改不会影响原始数组
}
```

---

## 十、结构体与类

### 10.1 结构体定义

```javascript
function Critter(hunger = 0) constructor
{
    m_Hunger = hunger;
    Greet = function()
    {
        show_debug_message($"Hi. My hunger is {m_Hunger}.");
    }
}

// 创建实例
crit1 = new Critter(5);
crit1.Greet();
```

### 10.2 成员访问

```javascript
crit1.m_Hunger = 9;                    // 赋值
show_debug_message(crit1.m_Hunger);    // 读取
```

### 10.3 继承

```javascript
// 基类
function Enemy() constructor
{
    m_Damage = 10;
    Attack = function()
    {
        show_debug_message("Attack inflicts " + string(m_Damage) + " damage!");
    }
}

// 派生类
function Boss() : Enemy() constructor
{
    m_DamageMultiplier = 3;
    SpecialAttack = function()
    {
        show_debug_message("Special Attack inflicts " + string(m_DamageMultiplier * m_Damage) + " damage!");
    }
}
```

### 10.4 事件继承

```javascript
// 子对象创建事件
event_inherited();              // 调用父对象的事件
m_MyVar = 10;                  // 添加子对象特有的变量
Attack = Boss_Attack;          // 重写回调函数
```

---

## 十一、数据结构

### 11.1 ds_list

```javascript
// 创建
inventory = ds_list_create();

// 添加元素
ds_list_add(inventory, "sword");
ds_list_add(inventory, "armor", "shield");  // 一次添加多个

// 访问
value = inventory[| 0];
ds_list_set(inventory, 0, "new value");

// 大小与操作
ds_list_size(inventory);
ds_list_delete(inventory, 0);
ds_list_insert(inventory, 0, "crossbow");
ds_list_clear(inventory);

// 销毁（必须！）
ds_list_destroy(inventory);
inventory = noone;
```

### 11.2 ds_map

```javascript
// 创建
score_map = ds_map_create();

// 设置/获取
score_map[? "player"] = 100;
score_map[? "enemy"] = 50;
value = score_map[? "player"];

// 检查与删除
if (ds_map_exists(score_map, "player"))
    ds_map_delete(score_map, "player");

// 销毁
ds_map_destroy(score_map);
score_map = noone;
```

### 11.3 内存管理要点

**必须手动销毁**：
- ds_list, ds_map, ds_grid
- buffer
- surface

**自动回收**：
- 普通变量
- 数组、结构体（无引用时）

---

## 十二、标准输入输出

### 12.1 输出函数

```javascript
show_debug_message("Debug info");           // 输出到编译窗口
show_message("Game Over!");                 // 弹出消息框
game_end();                                 // 结束游戏

// 格式化输出
show_debug_message($"Score: {_score}, Lives: {_lives}");
show_debug_message("Value: {0}", some_value);
```

### 12.2 输入函数

```javascript
fuel = get_string("\nHow much fuel? ", "");  // 弹出输入框
name = get_string("Enter your name:", "Player");
```

---

## 十三、常用内置函数

### 13.1 实例操作

| 函数 | 说明 |
|------|------|
| `instance_create_layer(x, y, layer, obj)` | 创建实例 |
| `instance_destroy()` | 销毁自身 |
| `instance_exists(obj)` | 检查实例是否存在 |
| `instance_number(obj)` | 获取实例数量 |

### 13.2 运动

| 函数 | 说明 |
|------|------|
| `randomize()` | 初始化随机数生成器 |
| `irandom(max)` | 生成0到max的随机整数 |
| `random(max)` | 生成0到max的随机浮点数 |

### 13.3 类型检查

| 函数 | 说明 |
|------|------|
| `is_real(value)` | 是否为实数 |
| `is_string(value)` | 是否为字符串 |
| `is_array(value)` | 是否为数组 |
| `is_struct(value)` | 是否为结构体 |
| `is_undefined(value)` | 是否未定义 |
| `is_handle(value)` | 是否为句柄 |

### 13.4 变量操作

| 函数 | 说明 |
|------|------|
| `variable_clone(value)` | 复制变量 |
| `variable_instance_get_names(obj)` | 获取实例变量名列表 |
| `variable_instance_set(obj, name, value)` | 设置实例变量 |
| `variable_instance_get(obj, name)` | 获取实例变量 |

---

## 十四、gm_cli命令

```bash
gm-cli init <project_name>    # 创建新项目
gm-cli build                   # 编译项目
gm-cli run                     # 运行游戏
gm-cli check                   # 代码检查
gm-cli clean                   # 清理编译产物
```