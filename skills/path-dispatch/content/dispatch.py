#!/usr/bin/env python3
"""
dispatch.py — Discrete Hamiltonian Path Dispatcher (Hypergraph Normalised)

All edges (including binary) are normalized through a virtual node.
An original logical step = 2 physical steps in the expanded graph.
Triples format: <<{[s1,s2,...], predicate, [o1,o2,...]}.
Supports hyperedges natively.

Usage:
  python dispatch.py <triples_file> query <current> <target> <logical_budget>
  python dispatch.py <triples_file> path   <start>    <end>
  python dispatch.py <triples_file> matrix
"""

import sys
import os
from collections import deque


def parse_list(s):
    s = s.strip()
    if s.startswith('[') and s.endswith(']'):
        inner = s[1:-1].strip()
        return [x.strip() for x in inner.split(',')] if inner else []
    return [s]

def smart_split(content):
    parts, current, depth = [], [], 0
    for ch in content:
        if ch == ',' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
        else:
            if ch == '[': depth += 1
            elif ch == ']': depth -= 1
            current.append(ch)
    if current:
        parts.append(''.join(current).strip())
    return parts if len(parts) == 3 else None

def parse_triples(filepath):
    triples = []
    with open(filepath, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not (line.startswith('<<{') and line.endswith('}.')):
                continue
            content = line[3:-2]
            parts = smart_split(content)
            if not parts:
                continue
            s_str, p_str, o_str = parts
            triples.append((parse_list(s_str), p_str, parse_list(o_str)))
    return triples

def build_graph(triples):
    orig_set = set()
    for s_list, _, o_list in triples:
        for n in s_list: orig_set.add(n)
        for n in o_list: orig_set.add(n)
    orig_nodes = sorted(orig_set)
    idx = {n: i for i, n in enumerate(orig_nodes)}
    orig_n = len(orig_nodes)
    total_nodes = orig_n + len(triples)
    A = [[False] * total_nodes for _ in range(total_nodes)]
    for rel_id, (s_list, _, o_list) in enumerate(triples):
        v_node = orig_n + rel_id
        for s in s_list: A[idx[s]][v_node] = True
        for o in o_list: A[v_node][idx[o]] = True
    names = orig_nodes + [f"__rel_{i}__" for i in range(len(triples))]
    return names, idx, A, orig_n

def bool_mul(A, B, n):
    C = [[False] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if A[i][k]:
                row_k = B[k]
                for j in range(n):
                    if row_k[j]: C[i][j] = True
    return C

def bool_or(A, B, n):
    return [[A[i][j] or B[i][j] for j in range(n)] for i in range(n)]

def matrices_equal(A, B, n):
    return all(A[i][j] == B[i][j] for i in range(n) for j in range(n))

def precompute_reachability(A, n, max_physical_k=None):
    if max_physical_k is None: max_physical_k = n
    R = []
    A_power = [row[:] for row in A]
    R_cumul = [row[:] for row in A]
    R.append([row[:] for row in R_cumul])
    for k in range(1, max_physical_k):
        A_power = bool_mul(A_power, A, n)
        R_new = bool_or(R_cumul, A_power, n)
        R.append([row[:] for row in R_new])
        if matrices_equal(R_new, R_cumul, n): break
        R_cumul = R_new
    return R

def next_hops(v, T_phys, phys_budget, A, R, n):
    if phys_budget <= 0: return []
    neighbors = [w for w in range(n) if A[v][w]]
    if phys_budget == 1:
        return [w for w in neighbors if w == T_phys]
    r_idx = min(phys_budget - 2, len(R) - 1)
    return [w for w in neighbors if R[r_idx][w][T_phys]]

def bfs_shortest_path(start_phys, end_phys, A, n, orig_n, names):
    if start_phys == end_phys:
        return ([names[start_phys]], 0)
    queue = deque([(start_phys, [start_phys])])
    visited = {start_phys}
    while queue:
        node, path = queue.popleft()
        # 遍历所有邻居（严格按照 A 的方向：node -> w）
        for w in range(n):
            if A[node][w] and w not in visited:
                new_path = path + [w]
                if w == end_phys:
                    # 过滤出原始节点（去掉虚拟节点），计算逻辑步数
                    logical_path = [names[p] for p in new_path if p < orig_n]
                    logical_hops = (len(new_path) - 1) // 2   # 每 2 个物理步 = 1 逻辑步
                    return logical_path, logical_hops
                visited.add(w)
                queue.append((w, new_path))
    return None, -1
    
def cmd_matrix(names, A, R, orig_n):
    total_n = len(names)
    print("=== Original Nodes ===")
    for i in range(orig_n): print(f"  {i:3d}  {names[i]}")
    print(f"\n=== Virtual Nodes ({total_n - orig_n}) ===")
    for i in range(orig_n, total_n): print(f"  {i:3d}  {names[i]}")
    print("\n=== Adjacency Matrix (A) ===")
    header = "     " + " ".join(f"{i:2d}" for i in range(total_n))
    print(header)
    for i, row in enumerate(A):
        bits = " ".join(" 1" if v else " 0" for v in row)
        print(f"{i:3d}  {bits}   {names[i]}")
    TC = R[-1]
    print("\n=== Transitive Closure (R*) ===")
    print(header)
    for i, row in enumerate(TC):
        bits = " ".join(" 1" if v else " 0" for v in row)
        print(f"{i:3d}  {bits}   {names[i]}")
    print(f"\nNodes: {total_n}  |  Convergence depth: {len(R)}")

def cmd_path(start_name, end_name, names, idx, A, orig_n):
    if start_name not in idx or end_name not in idx:
        print("Unknown node."); return
    s, e = idx[start_name], idx[end_name]
    total_n = len(names)
    logical_path, logical_hops = bfs_shortest_path(s, e, A, total_n, orig_n, names)
    if logical_path is None:
        print(f"No path from '{start_name}' to '{end_name}'")
    else:
        print(f"Shortest logical path ({logical_hops} hops):")
        print("  " + " → ".join(logical_path))

def cmd_query(current_name, target_name, logical_budget, names, idx, A, R, orig_n):
    if current_name not in idx or target_name not in idx:
        print("Unknown node."); return
    v, T = idx[current_name], idx[target_name]
    total_n = len(names)
    phys_budget = 2 * logical_budget
    result = next_hops(v, T, phys_budget, A, R, total_n)
    readable = []
    for w in result:
        if w >= orig_n:
            targets = [names[t] for t in range(orig_n) if A[w][t]]
            if len(targets) == 1:
                readable.append(targets[0])  # binary edge: direct
            else:
                readable.append("{" + ", ".join(targets) + "}")  # hyperedge: set notation
        else:
            readable.append(names[w])
    print(f"next_hops(current={current_name}, target={target_name}, logical_budget={logical_budget})")
    if not result:
        print("  ∅")
    else:
        print("  →", readable)

def usage():
    print(__doc__); sys.exit(1)

def main():
    if len(sys.argv) < 3: usage()
    filepath = sys.argv[1]
    command  = sys.argv[2]
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}"); sys.exit(1)
    triples = parse_triples(filepath)
    if not triples:
        print("No triples found."); sys.exit(1)
    names, idx, A, orig_n = build_graph(triples)
    total_n = len(names)
    R = precompute_reachability(A, total_n)
    if command == "matrix":
        cmd_matrix(names, A, R, orig_n)
    elif command == "path":
        if len(sys.argv) < 5: usage()
        cmd_path(sys.argv[3], sys.argv[4], names, idx, A, orig_n)
    elif command == "query":
        if len(sys.argv) < 6: usage()
        cmd_query(sys.argv[3], sys.argv[4], int(sys.argv[5]), names, idx, A, R, orig_n)
    else:
        usage()

if __name__ == "__main__":
    main()
