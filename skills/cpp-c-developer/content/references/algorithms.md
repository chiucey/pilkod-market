---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f4966b714c5349d6c959f6e7ba994b47
    PropagateID: f4966b714c5349d6c959f6e7ba994b47
    ReservedCode1: 304402203e3899e8c7fed1145570f5c9165fa8683001878670e530d810574ceb2b28983b02203bb92b8ebe509ac5101fdabecae293411a7bcd649f79bce76c1c92ff6e95414a
    ReservedCode2: 3046022100b11acffdd6f94b6c7e62886b99a82105ed994d4c5b755b3b24d50babafe5234d022100c32a76dc7f235db494c33824b5a4320d9b94e41f38080a6da73c353b307ce045
---

# 常用算法与数据结构参考

## 排序算法复杂度对比

| 算法 | 平均时间 | 最坏时间 | 空间 | 稳定性 |
|------|----------|----------|------|--------|
| 快速排序 | O(n log n) | O(n²) | O(log n) | 不稳定 |
| 归并排序 | O(n log n) | O(n log n) | O(n) | 稳定 |
| 堆排序 | O(n log n) | O(n log n) | O(1) | 不稳定 |
| 冒泡排序 | O(n²) | O(n²) | O(1) | 稳定 |
| 插入排序 | O(n²) | O(n²) | O(1) | 稳定 |
| 希尔排序 | O(n^1.3) | O(n²) | O(1) | 不稳定 |

## 常见数据结构操作复杂度

| 数据结构 | 访问 | 搜索 | 插入 | 删除 |
|----------|------|------|------|------|
| 数组 | O(1) | O(n) | O(n) | O(n) |
| 链表 | O(n) | O(n) | O(1) | O(1) |
| 栈 | O(n) | - | O(1) | O(1) |
| 队列 | O(n) | - | O(1) | O(1) |
| 哈希表 | - | O(1) | O(1) | O(1) |
| 二叉搜索树 | O(log n) | O(log n) | O(log n) | O(log n) |

## C++ STL 算法示例

```cpp
#include <algorithm>
#include <vector>
#include <numeric>

// 排序
std::vector<int> v = {3, 1, 4, 1, 5, 9};
std::sort(v.begin(), v.end());  // 升序
std::sort(v.begin(), v.end(), std::greater<int>());  // 降序

// 查找
auto it = std::find(v.begin(), v.end(), 5);
bool exists = std::binary_search(v.begin(), v.end(), 5);

// 去重
std::sort(v.begin(), v.end());
v.erase(std::unique(v.begin(), v.end()), v.end());

// 数值运算
int sum = std::accumulate(v.begin(), v.end(), 0);
int product = std::accumulate(v.begin(), v.end(), 1, std::multiplies<int>());

// 变换
std::transform(v.begin(), v.end(), v.begin(), [](int x) { return x * 2; });

// 计数
int even_count = std::count_if(v.begin(), v.end(), [](int x) { return x % 2 == 0; });

// 移除元素（需配合 erase）
v.erase(std::remove_if(v.begin(), v.end(), [](int x) { return x < 0; }), v.end());
```

## 常见问题模式

### 双指针技巧

```cpp
// 有序数组去重
int removeDuplicates(std::vector<int>& nums) {
    if (nums.empty()) return 0;
    int slow = 0;
    for (int fast = 1; fast < nums.size(); ++fast) {
        if (nums[fast] != nums[slow]) {
            nums[++slow] = nums[fast];
        }
    }
    return slow + 1;
}

// 两数之和（有序数组）
std::pair<int, int> twoSum(const std::vector<int>& nums, int target) {
    int left = 0, right = nums.size() - 1;
    while (left < right) {
        int sum = nums[left] + nums[right];
        if (sum == target) return {left, right};
        else if (sum < target) ++left;
        else --right;
    }
    return {-1, -1};
}
```

### 滑动窗口

```cpp
// 最大子数组和（长度至少 k）
int maxSum(const std::vector<int>& nums, int k) {
    int windowSum = 0, maxSum = 0;
    for (int i = 0; i < k; ++i) windowSum += nums[i];
    maxSum = windowSum;

    for (int i = k; i < nums.size(); ++i) {
        windowSum += nums[i] - nums[i - k];
        maxSum = std::max(maxSum, windowSum);
    }
    return maxSum;
}

// 最长无重复子串
int lengthOfLongestSubstring(const std::string& s) {
    std::unordered_set<char> seen;
    int left = 0, maxLen = 0;
    for (int right = 0; right < s.length(); ++right) {
        while (seen.count(s[right])) {
            seen.erase(s[left]);
            ++left;
        }
        seen.insert(s[right]);
        maxLen = std::max(maxLen, right - left + 1);
    }
    return maxLen;
}
```

### 递归与动态规划

```cpp
// 斐波那契数列（带记忆化）
std::unordered_map<int, long long> memo;
long long fib(int n) {
    if (n <= 1) return n;
    if (memo.count(n)) return memo[n];
    memo[n] = fib(n - 1) + fib(n - 2);
    return memo[n];
}

// 背包问题
int knapsack(int capacity, const std::vector<int>& weights,
             const std::vector<int>& values) {
    int n = weights.size();
    std::vector<int> dp(capacity + 1, 0);

    for (int i = 0; i < n; ++i) {
        for (int w = capacity; w >= weights[i]; --w) {
            dp[w] = std::max(dp[w], dp[w - weights[i]] + values[i]);
        }
    }
    return dp[capacity];
}
```

### 位运算技巧

```cpp
// 检查某位是否为 1
bool isBitSet(int n, int bit) {
    return (n & (1 << bit)) != 0;
}

// 设置某位为 1
int setBit(int n, int bit) {
    return n | (1 << bit);
}

// 清除某位
int clearBit(int n, int bit) {
    return n & ~(1 << bit);
}

// 统计置位数量
int countBits(int n) {
    int count = 0;
    while (n) {
        n &= (n - 1);  // 清除最低位的 1
        ++count;
    }
    return count;
}

// 判断是否为 2 的幂
bool isPowerOfTwo(int n) {
    return n > 0 && (n & (n - 1)) == 0;
}
```
