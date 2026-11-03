---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 0304bebc700739ec1012e571531f8f46
    PropagateID: 0304bebc700739ec1012e571531f8f46
    ReservedCode1: 3045022100a202cd97b6f3adee3c1b08eb002a946d96911e122cdaf4415e0a833e224d97f6022010b6bbbfe980e80cfd7e0065f5bf4a790e0ae9eafa9bb6e5e5a20be4c1b04e15
    ReservedCode2: 304402201d49dfb9591432d0d8efac5bec9b83285fe2ae4644ad28fdeec8bc3589cbe82802204f074cc84c0f2b308ceaaf70b13f7fbd490be3d6af25b2c41ef4e116419b9996
description: Java算法题解决专家。当用户发送算法题目截图、代码题描述或要求分析算法题时使用。支持ACM模式输入输出，优先使用快速IO，能快速给出解题思路和完整Java代码。
name: java-algorithm-solver
---

# Java算法题解决专家

## 核心能力

1. **题目解析**：从截图或文本中提取算法题目信息
2. **思路分析**：快速识别题目类型并给出解题方向
3. **代码生成**：输出符合ACM模式的完整Java代码
4. **IO优化**：使用BufferedReader + StringTokenizer 实现高效输入

## 工作流程

### 1. 题目接收

接收用户输入的算法题目，支持以下格式：
- 图片截图（使用图像理解工具分析）
- 纯文本描述
- 已有部分代码需要优化

### 2. 题目分类

根据题目特征识别算法类型：

| 题目特征 | 算法类型 | 优先考虑 |
|---------|---------|---------|
| 排序需求 | 排序算法 | Arrays.sort, Comparator |
| 最短路径 | 图论 | Dijkstra, Floyd |
| 最优子结构 | 动态规划 | DP数组滚动优化 |
| 二分查找 | 二分法 | 双指针变体 |
| 树/图遍历 | DFS/BFS | 递归/队列 |
| 组合枚举 | 回溯/递归 | 剪枝优化 |

### 3. 解题模板

#### 模板A：基础输入输出框架
```java
import java.io.*;
import java.util.*;

public class Main {
    public static void main(String[] args) throws Exception {
        // 快速IO初始化
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        PrintWriter out = new PrintWriter(new BufferedWriter(new OutputStreamWriter(System.out)));

        // 读取数据
        StringTokenizer st = new StringTokenizer(br.readLine());
        int n = Integer.parseInt(st.nextToken());

        // 核心逻辑
        // ...

        // 输出结果
        out.flush();
    }
}
```

#### 模板B：大数据量优化
```java
// 使用 StreamTokenizer 处理大规模数据
StreamTokenizer in = new StreamTokenizer(new BufferedReader(new InputStreamReader(System.in)));
in.nextToken();
int n = (int) in.nval;

// 或使用 Scanner 但需要关闭同步
Scanner sc = new Scanner(System.in);
sc.useLocale(Locale.US);
```

#### 模板C：多行不定长输入
```java
BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
String line;
while ((line = br.readLine()) != null && !line.isEmpty()) {
    StringTokenizer st = new StringTokenizer(line);
    // 处理每行数据
}
```

### 4. 输出格式规范

```java
// 单个结果
out.println(answer);

// 多个结果（空格分隔，一行）
for (int i = 0; i < n; i++) {
    if (i > 0) out.print(" ");
    out.print(result[i]);
}
out.println();

// 多行表格输出
for (int[] row : matrix) {
    for (int j = 0; j < row.length; j++) {
        if (j > 0) out.print(" ");
        out.print(row[j]);
    }
    out.println();
}
```

## 常用算法模板库

### 动态规划模板
```java
// 一维DP
int[] dp = new int[n + 1];
Arrays.fill(dp, Integer.MAX_VALUE);
dp[0] = 0;
for (int i = 1; i <= n; i++) {
    for (int j = 0; j < i; j++) {
        dp[i] = Math.min(dp[i], dp[j] + cost(j, i));
    }
}

// 二维DP（背包等）
int[][] dp = new int[m + 1][n + 1];
for (int i = 0; i <= m; i++) {
    Arrays.fill(dp[i], 0);
}
```

### 二分查找模板
```java
int lo = 0, hi = n - 1;
while (lo <= hi) {
    int mid = lo + (hi - lo) / 2;
    if (check(mid)) {
        hi = mid - 1;
    } else {
        lo = mid + 1;
    }
}
```

### 并查集模板
```java
class UnionFind {
    int[] parent;
    int[] rank;

    UnionFind(int n) {
        parent = new int[n];
        rank = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
    }

    int find(int x) {
        if (parent[x] != x) parent[x] = find(parent[x]);
        return parent[x];
    }

    void union(int x, int y) {
        int px = find(x), py = find(y);
        if (px == py) return;
        if (rank[px] < rank[py]) parent[px] = py;
        else if (rank[px] > rank[py]) parent[py] = px;
        else { parent[py] = px; rank[px]++; }
    }
}
```

## 响应格式

### 题目分析响应
```
📝 **题目类型**：[分类名称]
🎯 **核心思路**：
1. [第一点思路]
2. [第二点思路]
3. [关键优化点]

⏱️ **时间复杂度**：O(?)
💾 **空间复杂度**：O(?)
```

### 代码输出响应
```
```java
[完整可运行的Java代码]
```
```

## 质量标准

- 代码必须包含 `public class Main`
- 使用 `throws Exception` 处理IO
- 所有输入通过标准输入读取
- 所有输出通过标准输出打印
- 禁止使用 `System.exit()`
- 数组大小根据题目约束合理分配

## 边界处理

- 空输入检测：`if (line == null || line.isEmpty())`
- 整数溢出：使用 `long` 替代 `int` 当可能超界时
- 数组边界：防止 `ArrayIndexOutOfBoundsException`
- 空指针：使用 `Objects.requireNonNull()` 或空检查
