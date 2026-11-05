# Java算法模板速查表

## 快速IO总结

### 1. BufferedReader + StringTokenizer（推荐）

```java
// 单行读取
BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
StringTokenizer st = new StringTokenizer(br.readLine());
int a = Integer.parseInt(st.nextToken());
int b = Integer.parseInt(st.nextToken());

// 多行读取
while ((line = br.readLine()) != null && !line.isEmpty()) {
    st = new StringTokenizer(line);
    // 处理
}

// StringTokenizer 常用方法
st.countTokens();           // 获取token数量
st.hasMoreTokens();         // 检查是否还有token
st.nextToken();             // 获取下一个token
```

### 2. StreamTokenizer（适合纯数字）

```java
StreamTokenizer st = new StreamTokenizer(new BufferedReader(new InputStreamReader(System.in)));
st.nextToken();
int n = (int) st.nval;
st.nextToken();
double d = st.nval;
st.nextToken();
String s = st.sval;
```

### 3. FastScanner（自定义快速类）

```java
class FastScanner {
    private final BufferedInputStream in = new BufferedInputStream(System.in);
    private final byte[] buffer = new byte[1 << 16];
    private int ptr = 0, len = 0;

    private int read() throws IOException {
        if (ptr >= len) {
            len = in.read(buffer);
            ptr = 0;
            if (len <= 0) return -1;
        }
        return buffer[ptr++];
    }

    Integer nextInt() throws IOException {
        int c, sign = 1, res = 0;
        do { c = read(); } while (c <= ' ' && c != -1);
        if (c == '-') { sign = -1; c = read(); }
        while (c > ' ') {
            res = res * 10 + (c - '0');
            c = read();
        }
        return res * sign;
    }
}
```

## 排序算法

### 内置排序
```java
// 一维数组
int[] arr = new int[n];
Arrays.sort(arr);

// 自定义比较
Arrays.sort(arr, (a, b) -> b - a);  // 降序
Arrays.sort(arr, Comparator.reverseOrder());

// 二维数组排序
int[][] arr = new int[m][2];
Arrays.sort(arr, (a, b) -> a[0] - b[0]);  // 按第一列排序
```

### 桶排序（数据范围已知）
```java
int max = Arrays.stream(arr).max().getAsInt();
int[] count = new int[max + 1];
for (int v : arr) count[v]++;
for (int i = 0, idx = 0; i <= max; i++) {
    while (count[i]-- > 0) arr[idx++] = i;
}
```

## 数据结构

### 优先队列
```java
// 最小堆（默认）
PriorityQueue<Integer> minHeap = new PriorityQueue<>();
PriorityQueue<Integer> minHeap = new PriorityQueue<>(Comparator.naturalOrder());

// 最大堆
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());

// 自定义对象
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[0] - b[0]);
```

### HashMap/HashSet
```java
HashMap<String, Integer> map = new HashMap<>();
map.put(key, map.getOrDefault(key, 0) + 1);
map.getOrDefault(key, defaultVal);

// 遍历
for (Map.Entry<String, Integer> e : map.entrySet()) {
    // e.getKey(), e.getValue()
}

// 按值排序
List<Map.Entry<String, Integer>> list = new ArrayList<>(map.entrySet());
list.sort((a, b) -> b.getValue() - a.getValue());
```

### 链表
```java
class ListNode {
    int val;
    ListNode next;
    ListNode(int x) { val = x; }
}

// 虚拟头节点
ListNode dummy = new ListNode(0);
dummy.next = head;

// 快慢指针找中点
ListNode slow = head, fast = head;
while (fast.next != null && fast.next.next != null) {
    slow = slow.next;
    fast = fast.next.next;
}
```

### 树
```java
class TreeNode {
    int val;
    TreeNode left, right;
    TreeNode(int x) { val = x; }
}

// BFS层序遍历
Queue<TreeNode> q = new LinkedList<>();
q.offer(root);
while (!q.isEmpty()) {
    TreeNode node = q.poll();
    // 处理node
    if (node.left != null) q.offer(node.left);
    if (node.right != null) q.offer(node.right);
}

// DFS前序遍历
void dfs(TreeNode node) {
    if (node == null) return;
    // 处理
    dfs(node.left);
    dfs(node.right);
}
```

## 图论

### 邻接表
```java
List<Integer>[] graph = new ArrayList[n];
for (int i = 0; i < n; i++) graph[i] = new ArrayList<>();
graph[u].add(v);
graph[v].add(u);  // 无向图

// 遍历
for (int neighbor : graph[u]) {
    // 处理
}
```

### Dijkstra
```java
int[] dist = new int[n];
Arrays.fill(dist, Integer.MAX_VALUE);
dist[source] = 0;
PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> a[1] - b[1]);
pq.offer(new int[]{source, 0});

while (!pq.isEmpty()) {
    int[] cur = pq.poll();
    int u = cur[0], d = cur[1];
    if (d > dist[u]) continue;
    for (int v : graph[u]) {
        if (dist[v] > dist[u] + 1) {  // 假设边权为1
            dist[v] = dist[u] + 1;
            pq.offer(new int[]{v, dist[v]});
        }
    }
}
```

## 常用技巧

### 双指针
```java
// 左右指针
int l = 0, r = n - 1;
while (l < r) {
    // 处理
    l++; r--;
}

// 快慢指针
int slow = 0;
for (int fast = 0; fast < n; fast++) {
    // 根据条件处理
    if (condition) slow++;
}
```

### 前缀和
```java
int[] prefix = new int[n + 1];
for (int i = 0; i < n; i++) {
    prefix[i + 1] = prefix[i] + arr[i];
}
// [l, r] 的和 = prefix[r + 1] - prefix[l]
```

### 位运算
```java
n & (n - 1)      // 消除最低位的1
n & (-n)         // 获取最低位的1
n ^ n = 0        // 相同为0
a ^ 0 = a        // 任何数与0异或不变
```

### 字符串处理
```java
StringBuilder sb = new StringBuilder();
sb.append(ch);
sb.toString();

// 字符串分割
String[] parts = str.split(" ");
String s = str.trim();

// 字符相关
Character.isDigit(c);
Character.isLetter(c);
Character.toLowerCase(c);
```
