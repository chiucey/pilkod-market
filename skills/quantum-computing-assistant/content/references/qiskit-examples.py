#!/usr/bin/env python3
"""
Qiskit 量子计算示例集
演示基础量子门、纠缠、搜索算法
"""

from qiskit import QuantumCircuit, Aer, execute, transpile
from qiskit.circuit.library import *
from qiskit.quantum_info import Statevector, Operator
from qiskit.visualization import plot_bloch_multivector, plot_histogram
import numpy as np

print("=" * 60)
print("Qiskit 量子计算示例")
print("=" * 60)

# ============================================
# 示例1: Hello Quantum - Bell态纠缠
# ============================================
print("\n[示例1] Bell态纠缠")
print("-" * 40)

qc = QuantumCircuit(2, 2)
qc.h(0)        # Hadamard门将q[0]变为叠加态
qc.cx(0, 1)    # CNOT门创建纠缠

print("电路图:")
print(qc.draw())

# 获取量子态向量
sv = Statevector(qc)
print(f"\n量子态向量: {sv}")
print(f"解释: |Φ+⟩ = (|00⟩ + |11⟩)/√2  Bell态")

# 模拟测量
qc.measure([0, 1], [0, 1])
backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=1000)
result = job.result()
counts = result.get_counts(qc)
print(f"\n测量结果 (1000次): {counts}")

# ============================================
# 示例2: Grover 搜索算法
# ============================================
print("\n[示例2] Grover 搜索算法")
print("-" * 40)

def grover_oracle_3bit(circuit, target):
    """
    创建3比特Oracle，标记目标态
    这里标记状态 |111⟩
    """
    if target == '111':
        circuit.ccx(0, 1, 2)
        circuit.x(2)
    elif target == '000':
        circuit.x([0, 1, 2])
        circuit.ccx(0, 1, 2)
        circuit.x([0, 1, 2])

def grover_diffusion(circuit, n):
    """Grover扩散算子"""
    circuit.h(range(n))
    circuit.x(range(n))
    circuit.h(n-1)
    circuit.ccx(0, 1, 2)
    circuit.h(n-1)
    circuit.x(range(n))
    circuit.h(range(n))

# 2比特Grover搜索
n = 2
qc = QuantumCircuit(n, n)

# 初始化叠加态
qc.h(range(n))

# Oracle标记 |11⟩
qc.cz(0, 1)

# 扩散算子
qc.h(range(n))
qc.x(range(n))
qc.h(n-1)
qc.x(n-1)
qc.h(n-1)
qc.x(range(n))
qc.h(range(n))

qc.measure(range(n), range(n))

print(f"电路图 (搜索 |11⟩):")
print(qc.draw())

job = execute(qc, backend, shots=1000)
result = job.result()
counts = result.get_counts(qc)
print(f"\n测量结果: {counts}")

# ============================================
# 示例3: 量子傅里叶变换 (QFT)
# ============================================
print("\n[示例3] 量子傅里叶变换")
print("-" * 40)

def qft_circuit(n):
    """创建QFT电路"""
    qc = QuantumCircuit(n)
    for i in range(n):
        qc.h(i)
        for j in range(i+1, n):
            qc.cp(np.pi/(2**(j-i)), j, i)
    # 反转量子比特顺序
    for i in range(n//2):
        qc.swap(i, n-i-1)
    return qc

n = 3
qc = qft_circuit(n)
print(f"3比特QFT电路:")
print(qc.draw())

# ============================================
# 示例4: 变分量子本征求解器 (VQE) 概念
# ============================================
print("\n[示例4] VQE 参数化电路")
print("-" * 40)

def ansatz_circuit(params, n_qubits):
    """简单的参数化量子电路"""
    qc = QuantumCircuit(n_qubits)
    for i in range(n_qubits):
        qc.rx(params[i*2], i)
        qc.rz(params[i*2+1], i)
    # 纠缠层
    for i in range(n_qubits-1):
        qc.cx(i, i+1)
    qc.cx(n_qubits-1, 0)
    return qc

params = [np.pi/4, np.pi/2] * 2
n_qubits = 2
qc = ansatz_circuit(params, n_qubits)
print("VQE Ansatz电路:")
print(qc.draw())

# ============================================
# 示例5: 量子态可视化
# ============================================
print("\n[示例5] 量子态Bloch球表示")
print("-" * 40)

# 创建均匀叠加态
qc = QuantumCircuit(1)
qc.h(0)
sv = Statevector(qc)
print(f"叠加态 |+⟩ = (|0⟩ + |1⟩)/√2")
print(f"态向量: {sv}")

# Bloch球坐标
theta = np.pi/2  # 90度
phi = 0
print(f"\nBloch球坐标:")
print(f"θ = {np.degrees(theta):.1f}°, φ = {np.degrees(phi):.1f}°")
print(f"对应Bloch球上 (+X) 轴方向")

print("\n" + "=" * 60)
print("运行完成!")
print("=" * 60)
