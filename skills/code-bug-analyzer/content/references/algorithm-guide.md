# Algorithm Guide - 竞赛算法知识库

## 目录

1. [复杂度分析](#复杂度分析)
2. [数据结构](#数据结构)
3. [排序算法](#排序算法)
4. [搜索与二分](#搜索与二分)
5. [图论算法](#图论算法)
6. [动态规划](#动态规划)
7. [字符串算法](#字符串算法)
8. [数学算法](#数学算法)
9. [竞赛题型分类](#竞赛题型分类)

---

## 复杂度分析

### 复杂度速查表

| 复杂度 | 10 | 100 | 1000 | 10^5 | 10^6 | 10^7 |
|--------|-----|------|------|------|------|------|
| O(1) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| O(log n) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| O(n) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| O(n log n) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| O(n^2) | ✅ | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| O(n^3) | ✅ | ⚠️ | ❌ | ❌ | ❌ | ❌ |
| O(2^n) | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ |
| O(n!) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

### 常见数据结构操作复杂度

| 数据结构 | 访问 | 搜索 | 插入 | 删除 |
|----------|------|------|------|------|
| 数组 | O(1) | O(n) | O(n) | O(n) |
| 链表 | O(n) | O(n) | O(1) | O(1) |
| 栈 | - | - | O(1) | O(1) |
| 队列 | - | - | O(1) | O(1) |
| 哈希表 | - | O(1) | O(1) | O(1) |
| 二叉搜索树 | O(log n) | O(log n) | O(log n) | O(log n) |
| 平衡树 | O(log n) | O(log n) | O(log n) | O(log n) |
| 堆 | - | O(1) | O(log n) | O(log n) |
| 图(邻接矩阵) | O(1) | O(V) | O(1) | O(1) |
| 图(邻接表) | O(V) | O(V+E) | O(1) | O(1) |

---

## 数据结构

### 1. 线性结构

#### 数组与指针
```cpp
// 数组基本操作
int arr[100];
arr[i] = value;           // O(1) 访问
for(int i=0; i<n; i++)    // O(n) 遍历

// 指针操作
int* p = arr;
*(p + i);                 // 等价于 arr[i]
```

#### 链表
```cpp
struct ListNode {
    int val;
    ListNode* next;
    ListNode(int x) : val(x), next(nullptr) {}
};

// 遍历
ListNode* curr = head;
while(curr) { curr = curr->next; }

// 反转
ListNode* reverse(ListNode* head) {
    ListNode *prev = nullptr, *curr = head;
    while(curr) {
        ListNode* next = curr->next;
        curr->next = prev;
        prev = curr;
        curr = next;
    }
    return prev;
}
```

### 2. 栈与队列

#### 单调栈
```cpp
// 下一个更大元素
vector<int> nextGreaterElement(vector<int>& nums) {
    vector<int> res(nums.size(), -1);
    stack<int> st;
    for(int i = 0; i < nums.size(); i++) {
        while(!st.empty() && nums[i] > nums[st.top()]) {
            res[st.top()] = nums[i];
            st.pop();
        }
        st.push(i);
    }
    return res;
}
```

#### 队列优化
```cpp
// 滑动窗口最大值（单调队列）
vector<int> maxSlidingWindow(vector<int>& nums, int k) {
    deque<int> dq;
    vector<int> res;
    for(int i = 0; i < nums.size(); i++) {
        if(!dq.empty() && dq.front() <= i - k) dq.pop_front();
        while(!dq.empty() && nums[i] > nums[dq.back()]) dq.pop_back();
        dq.push_back(i);
        if(i >= k - 1) res.push_back(nums[dq.front()]);
    }
    return res;
}
```

### 3. 树结构

#### 二叉树遍历
```cpp
// 前序遍历（递归）
void preorder(TreeNode* root) {
    if(!root) return;
    cout << root->val;
    preorder(root->left);
    preorder(root->right);
}

// 前序遍历（迭代）
vector<int> preorderTraversal(TreeNode* root) {
    vector<int> res;
    stack<TreeNode*> st;
    if(root) st.push(root);
    while(!st.empty()) {
        TreeNode* node = st.top(); st.pop();
        res.push_back(node->val);
        if(node->right) st.push(node->right);
        if(node->left) st.push(node->left);
    }
    return res;
}

// 层序遍历
vector<vector<int>> levelOrder(TreeNode* root) {
    vector<vector<int>> res;
    queue<TreeNode*> q;
    if(root) q.push(root);
    while(!q.empty()) {
        int size = q.size();
        vector<int> level;
        for(int i = 0; i < size; i++) {
            TreeNode* node = q.front(); q.pop();
            level.push_back(node->val);
            if(node->left) q.push(node->left);
            if(node->right) q.push(node->right);
        }
        res.push_back(level);
    }
    return res;
}
```

#### 堆（优先队列）
```cpp
// 小根堆
priority_queue<int, vector<int>, greater<int>> minHeap;

// 大根堆（默认）
priority_queue<int> maxHeap;

// 自定义比较
struct Node {
    int x, y;
    bool operator<(const Node& other) const {
        return x < other.x;  // 按 x 降序
    }
};
priority_queue<Node> pq;
```

### 4. 并查集

```cpp
class UnionFind {
    vector<int> parent, rank;
public:
    UnionFind(int n) {
        parent.resize(n);
        rank.resize(n, 0);
        iota(parent.begin(), parent.end(), 0);
    }
    int find(int x) {
        return parent[x] == x ? x : parent[x] = find(parent[x]);
    }
    void unite(int x, int y) {
        x = find(x); y = find(y);
        if(x == y) return;
        if(rank[x] < rank[y]) swap(x, y);
        parent[y] = x;
        if(rank[x] == rank[y]) rank[x]++;
    }
    bool connected(int x, int y) { return find(x) == find(y); }
};
```

---

## 排序算法

### 复杂度对比

| 算法 | 平均 | 最坏 | 最好 | 空间 | 稳定 |
|------|------|------|------|------|------|
| 冒泡 | O(n^2) | O(n^2) | O(n) | O(1) | ✅ |
| 选择 | O(n^2) | O(n^2) | O(n^2) | O(1) | ❌ |
| 插入 | O(n^2) | O(n^2) | O(n) | O(1) | ✅ |
| 希尔 | O(n^1.3) | O(n^2) | O(n) | O(1) | ❌ |
| 归并 | O(n log n) | O(n log n) | O(n log n) | O(n) | ✅ |
| 快速 | O(n log n) | O(n^2) | O(n log n) | O(log n) | ❌ |
| 堆排序 | O(n log n) | O(n log n) | O(n log n) | O(1) | ❌ |
| 计数 | O(n+k) | O(n+k) | O(n+k) | O(k) | ✅ |
| 基数 | O(nk) | O(nk) | O(nk) | O(n+k) | ✅ |

### 快速排序模板
```cpp
void quickSort(vector<int>& arr, int left, int right) {
    if(left >= right) return;
    int pivot = arr[left];
    int i = left, j = right;
    while(i < j) {
        while(i < j && arr[j] >= pivot) j--;
        arr[i] = arr[j];
        while(i < j && arr[i] <= pivot) i++;
        arr[j] = arr[i];
    }
    arr[i] = pivot;
    quickSort(arr, left, i - 1);
    quickSort(arr, i + 1, right);
}
```

### 归并排序模板
```cpp
void mergeSort(vector<int>& arr, int left, int right) {
    if(left >= right) return;
    int mid = (left + right) / 2;
    mergeSort(arr, left, mid);
    mergeSort(arr, mid + 1, right);
    
    vector<int> temp(right - left + 1);
    int i = left, j = mid + 1, k = 0;
    while(i <= mid && j <= right)
        temp[k++] = arr[i] <= arr[j] ? arr[i++] : arr[j++];
    while(i <= mid) temp[k++] = arr[i++];
    while(j <= right) temp[k++] = arr[j++];
    for(int p = 0; p < k; p++) arr[left + p] = temp[p];
}
```

---

## 搜索与二分

### 二分查找模板

```cpp
// 标准二分
int binarySearch(vector<int>& nums, int target) {
    int left = 0, right = nums.size() - 1;
    while(left <= right) {
        int mid = left + (right - left) / 2;
        if(nums[mid] == target) return mid;
        else if(nums[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}

// 左边界二分
int lowerBound(vector<int>& nums, int target) {
    int left = 0, right = nums.size();
    while(left < right) {
        int mid = left + (right - left) / 2;
        if(nums[mid] < target) left = mid + 1;
        else right = mid;
    }
    return left;
}

// 右边界二分
int upperBound(vector<int>& nums, int target) {
    int left = 0, right = nums.size();
    while(left < right) {
        int mid = left + (right - left) / 2;
        if(nums[mid] <= target) left = mid + 1;
        else right = mid;
    }
    return left;
}
```

### 二分答案模板

```cpp
// 判断函数
bool canSolve(long long mid, vector<int>& params) {
    // 根据 mid 判断能否满足条件
}

// 二分搜索最优解
long long binarySearchAnswer(long long lo, long long hi) {
    while(lo < hi) {
        long long mid = (lo + hi) / 2;
        if(canSolve(mid, params)) hi = mid;
        else lo = mid + 1;
    }
    return lo;
}
```

### DFS 与 BFS

```cpp
// DFS（递归）
void dfs(int node, vector<int>& visited, vector<vector<int>>& graph) {
    visited[node] = true;
    for(int neighbor : graph[node]) {
        if(!visited[neighbor]) {
            dfs(neighbor, visited, graph);
        }
    }
}

// DFS（迭代/栈）
void dfsIterative(int start, vector<vector<int>>& graph) {
    vector<int> visited(graph.size(), false);
    stack<int> st;
    st.push(start);
    while(!st.empty()) {
        int node = st.top(); st.pop();
        if(visited[node]) continue;
        visited[node] = true;
        for(int neighbor : graph[node]) {
            if(!visited[neighbor]) st.push(neighbor);
        }
    }
}

// BFS（队列）
void bfs(int start, vector<vector<int>>& graph) {
    vector<int> visited(graph.size(), false);
    queue<int> q;
    q.push(start);
    visited[start] = true;
    while(!q.empty()) {
        int node = q.front(); q.pop();
        for(int neighbor : graph[node]) {
            if(!visited[neighbor]) {
                visited[neighbor] = true;
                q.push(neighbor);
            }
        }
    }
}
```

---

## 图论算法

### 最短路算法

| 算法 | 复杂度 | 适用场景 |
|------|--------|----------|
| Dijkstra | O(V^2) / O(E log V) | 非负权图 |
| Bellman-Ford | O(VE) | 负权图，检测负环 |
| SPFA | O(VE) | 一般情况（可能退化） |
| Floyd | O(V^3) | 全源最短路 |
| BFS | O(V+E) | 无权图/01边权 |

### Dijkstra 模板
```cpp
vector<int> dijkstra(int start, vector<vector<pair<int,int>>>& graph) {
    int n = graph.size();
    vector<int> dist(n, INT_MAX);
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;
    dist[start] = 0;
    pq.push({0, start});
    while(!pq.empty()) {
        auto [d, u] = pq.top(); pq.pop();
        if(d > dist[u]) continue;
        for(auto [v, w] : graph[u]) {
            if(dist[v] > dist[u] + w) {
                dist[v] = dist[u] + w;
                pq.push({dist[v], v});
            }
        }
    }
    return dist;
}
```

### Bellman-Ford 模板
```cpp
bool bellmanFord(int start, vector<tuple<int,int,int>>& edges, vector<int>& dist) {
    int n = dist.size();
    dist[start] = 0;
    for(int i = 0; i < n - 1; i++) {
        bool updated = false;
        for(auto [u, v, w] : edges) {
            if(dist[u] != INT_MAX && dist[v] > dist[u] + w) {
                dist[v] = dist[u] + w;
                updated = true;
            }
        }
        if(!updated) break;
    }
    // 检测负环
    for(auto [u, v, w] : edges) {
        if(dist[u] != INT_MAX && dist[v] > dist[u] + w)
            return false;  // 存在负环
    }
    return true;
}
```

### 拓扑排序
```cpp
vector<int> topologicalSort(vector<vector<int>>& graph) {
    int n = graph.size();
    vector<int> indegree(n, 0);
    for(int i = 0; i < n; i++)
        for(int j : graph[i]) indegree[j]++;
    
    queue<int> q;
    for(int i = 0; i < n; i++)
        if(indegree[i] == 0) q.push(i);
    
    vector<int> order;
    while(!q.empty()) {
        int u = q.front(); q.pop();
        order.push_back(u);
        for(int v : graph[u]) {
            if(--indegree[v] == 0) q.push(v);
        }
    }
    return order.size() == n ? order : {};
}
```

### 最小生成树
```cpp
// Kruskal
int kruskal(int n, vector<tuple<int,int,int>>& edges) {
    sort(edges.begin(), edges.end());
    UnionFind uf(n);
    int mst = 0;
    for(auto [w, u, v] : edges) {
        if(!uf.connected(u, v)) {
            uf.unite(u, v);
            mst += w;
        }
    }
    return mst;
}

// Prim
int prim(int start, vector<vector<pair<int,int>>>& graph) {
    int n = graph.size();
    vector<int> minEdge(n, INT_MAX);
    vector<bool> visited(n, false);
    minEdge[start] = 0;
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;
    pq.push({0, start});
    int mst = 0;
    while(!pq.empty()) {
        auto [w, u] = pq.top(); pq.pop();
        if(visited[u]) continue;
        visited[u] = true;
        mst += w;
        for(auto [v, cost] : graph[u]) {
            if(!visited[v] && cost < minEdge[v]) {
                minEdge[v] = cost;
                pq.push({cost, v});
            }
        }
    }
    return mst;
}
```

---

## 动态规划

### 经典问题模板

#### 1. 背包问题
```cpp
// 0-1 背包
vector<int> knapsack01(int capacity, vector<int>& weight, vector<int>& value) {
    int n = weight.size();
    vector<int> dp(capacity + 1, 0);
    for(int i = 0; i < n; i++) {
        for(int j = capacity; j >= weight[i]; j--) {
            dp[j] = max(dp[j], dp[j - weight[i]] + value[i]);
        }
    }
    return dp;
}

// 完全背包
vector<int> knapsackComplete(int capacity, vector<int>& weight, vector<int>& value) {
    int n = weight.size();
    vector<int> dp(capacity + 1, 0);
    for(int i = 0; i < n; i++) {
        for(int j = weight[i]; j <= capacity; j++) {
            dp[j] = max(dp[j], dp[j - weight[i]] + value[i]);
        }
    }
    return dp;
}
```

#### 2. 最长公共子序列
```cpp
int LCS(string& s1, string& s2) {
    int m = s1.size(), n = s2.size();
    vector<vector<int>> dp(m + 1, vector<int>(n + 1, 0));
    for(int i = 1; i <= m; i++) {
        for(int j = 1; j <= n; j++) {
            if(s1[i-1] == s2[j-1]) dp[i][j] = dp[i-1][j-1] + 1;
            else dp[i][j] = max(dp[i-1][j], dp[i][j-1]);
        }
    }
    return dp[m][n];
}
```

#### 3. 最长递增子序列
```cpp
int LIS(vector<int>& nums) {
    int n = nums.size();
    vector<int> dp(n, 1), tails;
    for(int num : nums) {
        auto it = lower_bound(tails.begin(), tails.end(), num);
        if(it == tails.end()) tails.push_back(num);
        else *it = num;
    }
    return tails.size();
}
```

#### 4. 编辑距离
```cpp
int editDistance(string& s1, string& s2) {
    int m = s1.size(), n = s2.size();
    vector<vector<int>> dp(m + 1, vector<int>(n + 1, 0));
    for(int i = 0; i <= m; i++) dp[i][0] = i;
    for(int j = 0; j <= n; j++) dp[0][j] = j;
    for(int i = 1; i <= m; i++) {
        for(int j = 1; j <= n; j++) {
            if(s1[i-1] == s2[j-1]) dp[i][j] = dp[i-1][j-1];
            else dp[i][j] = min({dp[i-1][j], dp[i][j-1], dp[i-1][j-1]}) + 1;
        }
    }
    return dp[m][n];
}
```

### DP 状态分类

| 类型 | 状态定义 | 典型问题 |
|------|----------|----------|
| 线性DP | dp[i] = 前i个... | LIS, 斐波那契 |
| 区间DP | dp[i][j] = i到j... | 石子合并, 括号序列 |
| 树形DP | dp[u] = 以u为根... | 树直径, 树上最大独立集 |
| 状压DP | dp[mask] = 状态mask... | 旅行商, 集合划分 |
| 数位DP | dp[pos][state]... | 数字统计, 数值计算 |
| 概率DP | dp[state] = 期望... | 期望计算, 博弈 |

---

## 字符串算法

### KMP
```cpp
vector<int> buildNext(const string& p) {
    int m = p.size();
    vector<int> next(m, 0);
    for(int i = 1, j = 0; i < m; i++) {
        while(j > 0 && p[i] != p[j]) j = next[j-1];
        if(p[i] == p[j]) j++;
        next[i] = j;
    }
    return next;
}

int kmp(const string& s, const string& p) {
    vector<int> next = buildNext(p);
    for(int i = 0, j = 0; i < (int)s.size(); i++) {
        while(j > 0 && s[i] != p[j]) j = next[j-1];
        if(s[i] == p[j]) j++;
        if(j == (int)p.size()) return i - j + 1;
    }
    return -1;
}
```

### Trie（字典树）
```cpp
struct TrieNode {
    TrieNode* children[26];
    bool isEnd;
    TrieNode() {
        memset(children, 0, sizeof(children));
        isEnd = false;
    }
};

void insert(TrieNode* root, const string& word) {
    TrieNode* node = root;
    for(char c : word) {
        int idx = c - 'a';
        if(!node->children[idx]) node->children[idx] = new TrieNode();
        node = node->children[idx];
    }
    node->isEnd = true;
}
```

### 哈希算法
```cpp
// 字符串哈希
struct StringHash {
    const int base = 131;
    vector<long long> h, p;
    StringHash(const string& s) {
        int n = s.size();
        h.resize(n + 1), p.resize(n + 1);
        p[0] = 1;
        for(int i = 0; i < n; i++) {
            h[i+1] = h[i] * base + s[i];
            p[i+1] = p[i] * base;
        }
    }
    long long get(int l, int r) {  // [l, r)
        return h[r] - h[l] * p[r-l];
    }
};
```

### Manacher（回文串）
```cpp
string manacher(const string& s) {
    string t = "#";
    for(char c : s) { t += c; t += '#'; }
    int n = t.size();
    vector<int> d(n);
    int l = 0, r = -1, maxLen = 0, center = 0;
    for(int i = 0; i < n; i++) {
        int k = (i > r) ? 1 : min(d[l + r - i], r - i + 1);
        while(i - k >= 0 && i + k < n && t[i-k] == t[i+k]) k++;
        d[i] = k--;
        if(i + k > r) { l = i - k; r = i + k; }
        if(d[i] > maxLen) { maxLen = d[i]; center = i; }
    }
    int start = (center - maxLen + 1) / 2;
    return s.substr(start, maxLen - 1);
}
```

---

## 数学算法

### 快速幂
```cpp
long long fastPower(long long a, long long b, long long mod) {
    long long res = 1;
    a %= mod;
    while(b > 0) {
        if(b & 1) res = res * a % mod;
        a = a * a % mod;
        b >>= 1;
    }
    return res;
}
```

### 最大公约数
```cpp
long long gcd(long long a, long long b) {
    return b == 0 ? a : gcd(b, a % b);
}

// 扩展欧几里得（求逆元）
long long extgcd(long long a, long long b, long long& x, long long& y) {
    if(b == 0) { x = 1; y = 0; return a; }
    long long x1, y1;
    long long g = extgcd(b, a % b, x1, y1);
    x = y1;
    y = x1 - (a / b) * y1;
    return g;
}
```

### 素数筛
```cpp
vector<int> sieve(int n) {
    vector<bool> isPrime(n + 1, true);
    isPrime[0] = isPrime[1] = false;
    vector<int> primes;
    for(int i = 2; i <= n; i++) {
        if(isPrime[i]) {
            primes.push_back(i);
            if((long long)i * i <= n)
                for(int j = i * i; j <= n; j += i)
                    isPrime[j] = false;
        }
    }
    return primes;
}
```

### 矩阵快速幂
```cpp
struct Matrix {
    vector<vector<long long>> a;
    int n, m;
    Matrix(int n_, int m_, bool identity = false) : n(n_), m(m_) {
        a.resize(n, vector<long long>(m, 0));
        if(identity) for(int i = 0; i < min(n, m); i++) a[i][i] = 1;
    }
    Matrix operator*(const Matrix& other) {
        Matrix res(n, other.m);
        for(int i = 0; i < n; i++)
            for(int k = 0; k < m; k++)
                if(a[i][k])
                    for(int j = 0; j < other.m; j++)
                        res.a[i][j] = (res.a[i][j] + a[i][k] * other.a[k][j]) % MOD;
        return res;
    }
};

Matrix power(Matrix a, long long b) {
    Matrix res(a.n, a.m, true);
    while(b > 0) {
        if(b & 1) res = res * a;
        a = a * a;
        b >>= 1;
    }
    return res;
}
```

---

## 竞赛题型分类

### 1. 搜索类
| 题型 | 关键词 | 典型算法 |
|------|--------|----------|
| 全排列 | permutation, arrangement | DFS, next_permutation |
| 组合 | combination | DFS, 回溯 |
| 子集 | subset, power set | DFS, 位运算 |
| 棋盘问题 | N-Queens, Sudoku | DFS + 剪枝 |

### 2. 图论类
| 题型 | 关键词 | 典型算法 |
|------|--------|----------|
| 最短路 | shortest path, distance | Dijkstra, Bellman-Ford, Floyd |
| 连通性 | connected, component | DFS, BFS, 并查集 |
| 生成树 | spanning tree, MST | Kruskal, Prim |
| 匹配 | matching, assignment | 二分图最大匹配 |
| 网络流 | flow, max flow | Dinic, Edmonds-Karp |

### 3. 动态规划类
| 题型 | 关键词 | 典型算法 |
|------|--------|----------|
| 背包 | knapsack, weight | 0-1背包, 完全背包, 多重背包 |
| 序列 | subsequence, substring | LIS, LCS, 编辑距离 |
| 区间 | interval, segment | 区间DP |
| 状态压缩 | bitmask, mask | 状压DP |
| 树形 | tree, rooted | 树形DP |

### 4. 字符串类
| 题型 | 关键词 | 典型算法 |
|------|--------|----------|
| 匹配 | match, search | KMP, Sunday, BM |
| 统计 | count, frequency | 哈希, Trie |
| 回文 | palindrome | Manacher, 区间DP |
| 自动机 | automaton | AC自动机, 后缀数组 |

### 5. 数学类
| 题型 | 关键词 | 典型算法 |
|------|--------|----------|
| 数论 | prime, gcd, mod | 素数筛, 扩展欧几里得 |
| 组合数学 | binomial, permutation | 排列组合, 卡特兰数 |
| 概率 | probability, expected | 概率DP |
| 矩阵 | matrix, exponentiation | 矩阵快速幂 |

### 6. 数据结构类
| 题型 | 关键词 | 典型算法 |
|------|--------|----------|
| 区间查询 | RMQ, segment tree | 线段树, 树状数组 |
| 排序 | order, k-th | 堆, nth_element |
| 模拟 | simulation, process | 队列, 栈 |
| 合并 | merge, union | 并查集 |

---

## 常见陷阱与优化

### 边界情况清单
- 空数组/空图
- 单元素情况
- 最大/最小边界值
- 负数处理
- 整数溢出
- 除零错误

### 优化方向
1. **降低复杂度**: O(n^2) -> O(n log n) -> O(n)
2. **减少空间**: 滚动数组, 压缩状态
3. **剪枝**: 可行性剪枝, 最优性剪枝
4. **记忆化**: 递归 -> DP
5. **IO优化**: fastio, sync_with_stdio(false)

### 竞赛代码特征检测
```
竞赛代码标志:
- main 函数有输入/输出
- 使用 scanf/printf 或 cin/cout
- 变量名简单: n, m, a, b, i, j
- 存在数组/向量存储数据
- 算法结构清晰，有明确的循环模式
```
