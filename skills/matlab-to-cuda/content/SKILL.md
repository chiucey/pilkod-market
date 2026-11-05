---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: f360fa26508948bdd54e46beee8300ce
    PropagateID: f360fa26508948bdd54e46beee8300ce
    ReservedCode1: 3046022100f6112667bd07ddf68eafc41cbdc28d8d92c6950587d9f185743f55fc0188b5c5022100b840ff28dbad635f08600dcb8e8fcb19926f0e489ed76ffd69fe7f61eddb7a13
    ReservedCode2: 30450221008fcb360e37709770db16e70e1099f2f2587662fb17bf654053814d88d3c4724702203679cc1fa581cfebdf4eec7e4d57ab4e89a0a50d62fc59c1f266ea5f2acc2616
description: Converts MATLAB code to CUDA C++ code. Use when users request converting MATLAB to CUDA, porting MATLAB algorithms to GPU acceleration, or rewriting MATLAB programs in CUDA.
name: matlab-to-cuda
---

# MATLAB to CUDA Code Converter

基于 NVIDIA CUDA 官方编程指南 (v13.2) 的 MATLAB 到 CUDA 转换技能。

## 核心转换原则

### 1. MATLAB 函数到 CUDA Kernel 的映射

| MATLAB 概念 | CUDA 对应 | 说明 |
|------------|----------|------|
| 向量化操作 | Parallel Kernel | GPU 并行执行 |
| for 循环 | Thread/Block 组织 | 多线程并行处理 |
| 数组索引 | threadIdx, blockIdx | CUDA 线程寻址 |
| gpuArray | Unified Memory/cudaMalloc | GPU 内存管理 |
| parfor | gridDim/blockDim | 线程网格配置 |

### 2. 基本转换模式

#### 2.1 简单元素运算

**MATLAB:**
```matlab
function y = compute(x)
    y = sin(x) .* cos(x);
end
```

**CUDA:**
```cpp
__global__
void compute(const float* x, float* y, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        y[idx] = sinf(x[idx]) * cosf(x[idx]);
    }
}
```

#### 2.2 矩阵运算

**MATLAB:**
```matlab
function C = matMul(A, B, n)
    C = A * B;  % 矩阵乘法
end
```

**CUDA (使用共享内存优化):**
```cpp
__global__
void matMulKernel(const float* A, const float* B, float* C, int n) {
    __shared__ float As[TILE_WIDTH][TILE_WIDTH];
    __shared__ float Bs[TILE_WIDTH][TILE_WIDTH];

    int row = blockIdx.y * TILE_WIDTH + threadIdx.y;
    int col = blockIdx.x * TILE_WIDTH + threadIdx.x;
    float sum = 0.0f;

    for (int m = 0; m < (n + TILE_WIDTH - 1) / TILE_WIDTH; ++m) {
        if (row < n && (m * TILE_WIDTH + threadIdx.x) < n)
            As[threadIdx.y][threadIdx.x] = A[row * n + m * TILE_WIDTH + threadIdx.x];
        else
            As[threadIdx.y][threadIdx.x] = 0.0f;

        if (col < n && (m * TILE_WIDTH + threadIdx.y) < n)
            Bs[threadIdx.y][threadIdx.x] = B[(m * TILE_WIDTH + threadIdx.y) * n + col];
        else
            Bs[threadIdx.y][threadIdx.x] = 0.0f;

        __syncthreads();

        for (int k = 0; k < TILE_WIDTH; ++k)
            sum += As[threadIdx.y][k] * Bs[k][threadIdx.x];

        __syncthreads();
    }

    if (row < n && col < n)
        C[row * n + col] = sum;
}
```

#### 2.3 2D 卷积

**MATLAB:**
```matlab
function output = conv2d(input, kernel)
    output = conv2(input, kernel, 'same');
end
```

**CUDA:**
```cpp
__global__
void conv2dKernel(const float* input, const float* kernel, float* output,
                  int imgHeight, int imgWidth, int kernelSize) {
    int outRow = blockIdx.y * blockDim.y + threadIdx.y;
    int outCol = blockIdx.x * blockDim.x + threadIdx.x;

    if (outRow < imgHeight && outCol < imgWidth) {
        float sum = 0.0f;
        int kHalf = kernelSize / 2;

        for (int i = -kHalf; i <= kHalf; ++i) {
            for (int j = -kHalf; j <= kHalf; ++j) {
                int inRow = outRow + i;
                int inCol = outCol + j;

                if (inRow >= 0 && inRow < imgHeight && inCol >= 0 && inCol < imgWidth) {
                    int inIdx = inRow * imgWidth + inCol;
                    int kerIdx = (i + kHalf) * kernelSize + (j + kHalf);
                    sum += input[inIdx] * kernel[kerIdx];
                }
            }
        }
        output[outRow * imgWidth + outCol] = sum;
    }
}
```

### 3. 线程组织策略

根据数据规模和操作类型选择合适的线程配置：

```
Host Code (CPU):
┌─────────────────────────────────────────────┐
│  // 定义线程块和网格维度                      │
│  dim3 blockSize(16, 16);                    │
│  dim3 gridSize((n + 15) / 16, (n + 15) / 16);│
│                                             │
│  // 调用 kernel                              │
│  kernelName<<<gridSize, blockSize>>>(...);  │
└─────────────────────────────────────────────┘

GPU Execution Model (SIMT):
┌─────────────────────────────────────────────┐
│  Grid = {Block0, Block1, Block2, ...}       │
│  Block = {Thread0, Thread1, Thread2, ...}  │
│                                             │
│  threadIdx: 本地线程 ID (0-255 通常)         │
│  blockIdx: 线程块 ID                         │
│  blockDim: 每块线程数                        │
│  gridDim:  总块数                            │
└─────────────────────────────────────────────┘
```

### 4. 内存管理

#### 4.1 Unified Memory (简化版)
```cpp
// 统一内存 - CPU和GPU共享访问
float *d_data;
cudaMallocManaged(&d_data, n * sizeof(float));
cudaMemcpy(d_data, h_data, n * sizeof(float), cudaMemcpyHostToDevice);

// Kernel执行后自动同步到CPU
compute<<<gridSize, blockSize>>>(d_data, n);
cudaDeviceSynchronize();

// 可直接在CPU使用结果
printf("Result: %f\n", d_data[0]);

cudaFree(d_data);
```

#### 4.2 显式内存管理
```cpp
// GPU内存分配
float *d_input, *d_output;
cudaMalloc(&d_input, n * sizeof(float));
cudaMalloc(&d_output, n * sizeof(float));

// Host到Device数据传输
cudaMemcpy(d_input, h_input, n * sizeof(float), cudaMemcpyHostToDevice);

// Kernel执行
kernel<<<gridSize, blockSize>>>(d_input, d_output, n);

// Device到Host数据回传
cudaMemcpy(h_output, d_output, n * sizeof(float), cudaMemcpyDeviceToHost);

// 释放内存
cudaFree(d_input);
cudaFree(d_output);
```

### 5. 常用MATLAB函数到CUDA映射

| MATLAB 函数 | CUDA 实现 | 头文件 |
|------------|----------|--------|
| `sin()`, `cos()` | `sinf()`, `cosf()` | math.h |
| `exp()` | `expf()` | math.h |
| `sqrt()` | `sqrtf()` | math.h |
| `abs()` | `fabsf()` (float) / `abs()` (int) | math.h / stdlib.h |
| `max()` | 循环 + `fmaxf()` | math.h |
| `min()` | 循环 + `fminf()` | math.h |
| `sum()` | 归约操作 (Reduction) | 自定义 |
| `dot()` | 归约或 thrust::inner_product | thrust header |

### 6. 完整转换示例

**MATLAB 主程序:**
```matlab
% 图像滤波处理
img = imread('input.png');
gray = rgb2gray(img);
kernel = fspecial('gaussian', [5 5], 2);
filtered = imfilter(gray, kernel);
result = uint8(filtered);
imwrite(result, 'output.png');
```

**CUDA 完整实现:**
```cpp
#include <stdio.h>
#include <cuda_runtime.h>
#include <device_launch_parameters.h>

#define TILE_SIZE 16
#define KERNEL_SIZE 5
#define KERNEL_HALF 2

// Gaussian Kernel 生成
__global__
void generateGaussianKernel(float* kernel, int size, float sigma) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < size * size) {
        int row = idx / size;
        int col = idx % size;
        int x = row - size / 2;
        int y = col - size / 2;
        kernel[idx] = expf(-(x*x + y*y) / (2.0f * sigma * sigma));
    }
}

// 归一化 kernel
__global__
void normalizeKernel(float* kernel, float* sum, int size) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < size * size && *sum > 0) {
        kernel[idx] /= *sum;
    }
}

// 2D Gaussian Filter
__global__
void gaussianFilter(const unsigned char* input, const float* kernel,
                    unsigned char* output, int height, int width, int kSize) {
    __shared__ float sharedKernel[KERNEL_SIZE * KERNEL_SIZE];

    int tid = threadIdx.x;
    if (tid < kSize * kSize) {
        sharedKernel[tid] = kernel[tid];
    }
    __syncthreads();

    int outRow = blockIdx.y * TILE_SIZE + threadIdx.y;
    int outCol = blockIdx.x * TILE_SIZE + threadIdx.x;
    int kHalf = kSize / 2;

    if (outRow < height && outCol < width) {
        float sum = 0.0f;

        for (int i = -kHalf; i <= kHalf; ++i) {
            for (int j = -kHalf; j <= kHalf; ++j) {
                int inRow = outRow + i;
                int inCol = outCol + j;

                inRow = max(0, min(height - 1, inRow));
                inCol = max(0, min(width - 1, inCol));

                int inIdx = inRow * width + inCol;
                int kerIdx = (i + kHalf) * kSize + (j + kHalf);
                sum += static_cast<float>(input[inIdx]) * sharedKernel[kerIdx];
            }
        }
        output[outRow * width + outCol] = static_cast<unsigned char>(fminf(255.0f, sum));
    }
}

int main() {
    // 图像尺寸
    int width = 1920;
    int height = 1080;
    size_t imgSize = width * height * sizeof(unsigned char);

    // Host内存分配
    unsigned char *h_input, *h_output;
    h_input = (unsigned char*)malloc(imgSize);
    h_output = (unsigned char*)malloc(imgSize);

    // 初始化输入图像 (示例: 灰度梯度)
    for (int i = 0; i < height * width; ++i) {
        h_input[i] = (i % 256);
    }

    // Device内存分配
    unsigned char *d_input, *d_output;
    float *d_kernel, *d_sum;
    cudaMalloc(&d_input, imgSize);
    cudaMalloc(&d_output, imgSize);
    cudaMalloc(&d_kernel, KERNEL_SIZE * KERNEL_SIZE * sizeof(float));
    cudaMalloc(&d_sum, sizeof(float));

    // 拷贝输入数据
    cudaMemcpy(d_input, h_input, imgSize, cudaMemcpyHostToDevice);

    // 生成 Gaussian Kernel
    dim3 kernelBlock(256);
    dim3 kernelGrid((KERNEL_SIZE * KERNEL_SIZE + 255) / 256);
    generateGaussianKernel<<<kernelGrid, kernelBlock>>>(d_kernel, KERNEL_SIZE, 2.0f);

    // 计算 kernel 总和并归一化
    float sum = 0.0f;
    cudaMemcpy(d_sum, &sum, sizeof(float), cudaMemcpyHostToDevice);
    // 简化: 假设已知 sum = 1.0 用于演示
    normalizeKernel<<<kernelGrid, kernelBlock>>>(d_kernel, d_sum, KERNEL_SIZE);

    // 设置 Filter 执行参数
    dim3 blockSize(TILE_SIZE, TILE_SIZE);
    dim3 gridSize((width + TILE_SIZE - 1) / TILE_SIZE,
                  (height + TILE_SIZE - 1) / TILE_SIZE);

    // 执行 Filter
    gaussianFilter<<<gridSize, blockSize>>>(d_input, d_kernel, d_output,
                                            height, width, KERNEL_SIZE);
    cudaDeviceSynchronize();

    // 拷贝结果
    cudaMemcpy(h_output, d_output, imgSize, cudaMemcpyDeviceToHost);

    // 保存输出 (需要实现文件写入)
    printf("Filtering complete. First pixel: %d\n", h_output[0]);

    // 释放内存
    cudaFree(d_input);
    cudaFree(d_output);
    cudaFree(d_kernel);
    cudaFree(d_sum);
    free(h_input);
    free(h_output);

    return 0;
}
```

### 7. 性能优化要点

1. **内存合并 (Coalesced Memory Access)**
   - 连续线程访问连续内存地址
   - `threadIdx.x` 作为内层索引

2. **共享内存 (Shared Memory)**
   - 用于重复访问的数据
   - 减少全局内存带宽压力

3. **占用率 (Occupancy)**
   - 每个块 128-256 线程通常最优
   - 避免线程资源浪费

4. **避免分支分歧 (Branch Divergence)**
   - 同一 warp 内线程走相同分支
   - 使用掩码操作替代条件分支

## 转换检查清单

- [ ] 识别可并行化的向量化操作
- [ ] 确定合适的数据划分策略 (1D/2D/3D)
- [ ] 设计线程块和网格维度
- [ ] 选择内存管理策略 (Unified vs 显式)
- [ ] 映射 MATLAB 内置函数到 CUDA math 函数
- [ ] 添加边界检查防止越界访问
- [ ] 验证数据类型一致性 (single vs double)

---

## 附录 A: MATLAB GPU Computing 与 CUDA 对照

基于 [MATLAB GPU Computing Documentation](https://www.mathworks.com/help/parallel-computing/gpu-computing-in-matlab.html)

### A.1 MATLAB GPU 数据类型

| MATLAB 函数 | CUDA 对应 | 说明 |
|------------|----------|------|
| `gpuArray(data)` | `cudaMalloc` + `cudaMemcpy` | 将数据传送到 GPU |
| `gather(gpuData)` | `cudaMemcpy` (Device→Host) | 将数据从 GPU 传回 CPU |
| `gpuDevice` | `cudaGetDevice` | 查询/选择 GPU 设备 |
| `gpuDeviceCount` | `cudaGetDeviceCount` | 获取可用 GPU 数量 |
| `gpuDeviceTable` | 设备属性查询 | 获取 GPU 设备属性表 |
| `parallel.gpu.CUDAKernel` | 加载 PTX/Cubin | 加载预编译 CUDA 内核 |

### A.2 MATLAB 数组创建函数映射

| MATLAB 函数 | CUDA 实现 |
|------------|----------|
| `zeros(n)` | `cudaMalloc` + `memset(0)` |
| `ones(n)` | Kernel 初始化或 `cudaMemset` |
| `rand(n)` | CURAND library (`curandGenerateUniform`) |
| `eye(n)` | Kernel 初始化对角线 |
| `linspace(a,b,n)` | Host 计算或 Kernel |
| `meshgrid(x,y)` | Kernel 二维网格生成 |
| `reshape(A,sz)` | 索引计算转换 |

### A.3 MATLAB arrayfun 与 CUDA Kernel 对照

**MATLAB:**
```matlab
% 使用 arrayfun 在 GPU 上执行元素级操作
A = gpuArray(rand(1000));
B = gpuArray(rand(1000));
C = arrayfun(@(a,b) sin(a) * cos(b), A, B);
```

**CUDA (等效 Kernel):**
```cpp
__global__
void sinCosKernel(const float* A, const float* B, float* C, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        C[idx] = sinf(A[idx]) * cosf(B[idx]);
    }
}
```

### A.4 MATLAB 矩阵运算函数映射

| MATLAB 函数 | CUDA 实现 | 说明 |
|------------|----------|------|
| `A * B` (矩阵乘法) | cuBLAS `cublasSgemm` | 矩阵-矩阵乘法 |
| `A \ b` (线性系统) | cuBLAS `cublasSgetrf/sgetrs` | LU 分解求解 |
| `A' * B` | cuBLAS `cublasSgemm` (转置) | 矩阵乘法 |
| `dot(a,b)` | cuBLAS `cublasSdot` | 向量点积 |
| `cross(a,b)` | 自定义 Kernel | 向量叉积 |
| `norm(v)` | 自定义 Kernel + Reduction | 向量范数 |
| `det(A)` | cuBLAS + 计算 | 行列式 |
| `eig(A)` | cuSOLVER `cusolverDnSsyevd` | 特征值分解 |
| `svd(A)` | cuSOLVER `cusolverDnSgesvd` | 奇异值分解 |

---

## 附录 B: MATLAB 图像处理 Toolbox 函数映射

基于 [MATLAB Image Processing Toolbox](https://www.mathworks.com/help/images/)

### B.1 图像输入输出

| MATLAB 函数 | CUDA/OpenCV 实现 |
|------------|-----------------|
| `imread(filename)` | OpenCV `cv::imread` |
| `imwrite(img, filename)` | OpenCV `cv::imwrite` |
| `rgb2gray(RGB)` | 自定义 Kernel |
| `gray2rgb(I)` | 自定义 Kernel (通道复制) |

### B.2 图像滤波函数

| MATLAB 函数 | CUDA 实现 | 说明 |
|------------|----------|------|
| `imfilter(img, kernel)` | Separable convolution Kernel | 二维滤波 |
| `conv2(A, B)` | Separable convolution | 二维卷积 |
| `convn(A, B)` | 3D convolution Kernel | 三维卷积 |
| `fspecial('gaussian')` | Gaussian Kernel 生成 | 高斯滤波器 |
| `fspecial('sobel')` | Sobel Kernel | 边缘检测 |
| `medfilt2(img)` | Sorting network / Histogram | 中值滤波 |
| `wiener2(img)` | Wiener filter Kernel | 自适应滤波 |

### B.3 图像变换函数

| MATLAB 函数 | CUDA/cuFFT 实现 |
|------------|----------------|
| `fft(x)` | cuFFT `cufftPlan1d` + `cufftExecC2C` |
| `fft2(A)` | cuFFT `cufftPlan2d` |
| `ifft(x)` | cuFFT `cufftExecC2C` (逆变换) |
| `dct(A)` | cuDCT 或自实现 Kernel |
| `idct(A)` | cuDCT 或自实现 Kernel |

### B.4 图像分析和增强

| MATLAB 函数 | CUDA 实现 |
|------------|----------|
| `edge(img, 'sobel')` | 自定义边缘检测 Kernel |
| `histeq(img)` | 直方图均衡化 Kernel |
| `imadjust(img, [low high])` | 亮度调整 Kernel |
| `histogram(data, nbins)` | 直方图统计 Kernel |
| `regionprops(L, 'Area')` | 连通域分析 |

### B.5 图像几何变换

| MATLAB 函数 | CUDA 实现 |
|------------|----------|
| `imresize(img, scale)` | 双线性/双三次插值 Kernel |
| `imrotate(img, angle)` | 旋转 + 插值 Kernel |
| `imtranslate(img, [dx dy])` | 平移 Kernel |
| `flipdim(img, dim)` | 数组翻转 |

---

## 附录 C: 完整 MATLAB 函数映射表

### C.1 数学函数 (Elementary Math)

| MATLAB 函数 | CUDA 函数 | 备注 |
|------------|----------|------|
| `sin(x)` | `sinf(x)` / `sin(x)` | float/double |
| `cos(x)` | `cosf(x)` / `cos(x)` | float/double |
| `tan(x)` | `tanf(x)` / `tan(x)` | float/double |
| `asin(x)` | `asinf(x)` / `asin(x)` | float/double |
| `acos(x)` | `acosf(x)` / `acos(x)` | float/double |
| `atan(x)` | `atanf(x)` / `atan(x)` | float/double |
| `atan2(y,x)` | `atan2f(y,x)` / `atan2(y,x)` | 四象限 |
| `sinh(x)` | `sinhf(x)` / `sinh(x)` | 双曲正弦 |
| `cosh(x)` | `coshf(x)` / `cosh(x)` | 双曲余弦 |
| `exp(x)` | `expf(x)` / `exp(x)` | 指数函数 |
| `log(x)` | `logf(x)` / `log(x)` | 自然对数 |
| `log10(x)` | `log10f(x)` / `log10(x)` | 常用对数 |
| `sqrt(x)` | `sqrtf(x)` / `sqrt(x)` | 平方根 |
| `pow2(x)` | `exp2f(x)` / `exp2(x)` | 2^x |
| `abs(x)` | `fabsf(x)` / `fabs(x)` | 绝对值 |
| `floor(x)` | `floorf(x)` / `floor(x)` | 向下取整 |
| `ceil(x)` | `ceilf(x)` / `ceil(x)` | 向上取整 |
| `round(x)` | `roundf(x)` / `round(x)` | 四舍五入 |
| `mod(a,b)` | `fmodf(a,b)` / `fmod(a,b)` | 取模 |
| `rem(a,b)` | 计算实现 | 余数 |

### C.2 数组操作函数

| MATLAB 函数 | CUDA/算法实现 |
|------------|--------------|
| `sum(A)` | Parallel Reduction |
| `prod(A)` | Parallel Reduction (乘法) |
| `min(A)` | Parallel Reduction (min) |
| `max(A)` | Parallel Reduction (max) |
| `cumsum(A)` | Inclusive Scan |
| `sort(A)` | Parallel Sort (Bitonic/GPU Sort) |
| `unique(A)` | Sort + Deduplication |
| `find(A > 0)` | Predicate + Compact |
| `sub2ind(sz,row,col)` | 计算实现 |
| `ind2sub(sz,idx)` | 计算实现 |
| `transpose(A)` | 矩阵转置 Kernel |
| `reshape(A,sz)` | 索引映射 |

### C.3 逻辑和比较运算

| MATLAB | CUDA | 说明 |
|--------|------|------|
| `A > B` | `A > B` (elementwise) | 大于比较 |
| `A < B` | `A < B` | 小于比较 |
| `A == B` | `A == B` | 等于比较 |
| `A & B` | `A && B` (按位需 `&`) | 逻辑与 |
| `A \| B` | `A \|\| B` | 逻辑或 |
| `~A` | `!A` | 逻辑非 |
| `any(A)` | Reduction (OR) | 任一为真 |
| `all(A)` | Reduction (AND) | 全部为真 |
| `isnan(A)` | `isnan()` | NaN 检测 |
| `isinf(A)` | `isinf()` | 无穷检测 |

---

## 附录 D: 转换工作流示例

### D.1 端到端转换流程

```
┌─────────────────────────────────────────────────────────────┐
│  Step 1: 分析 MATLAB 代码                                    │
│  - 识别可并行化的向量化操作                                 │
│  - 确定数据依赖关系                                         │
│  - 评估算法复杂度                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 2: 设计 CUDA 架构                                      │
│  - 选择线程组织 (1D/2D/3D)                                  │
│  - 决定内存策略 (Unified/Explicit)                          │
│  - 规划 kernel 划分                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 3: 实现转换                                           │
│  - 编写 Host 代码 (内存管理, Kernel 调用)                   │
│  - 编写 Device Kernel (核心计算逻辑)                        │
│  - 添加错误处理                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Step 4: 优化验证                                           │
│  - 正确性验证 (与 MATLAB 结果对比)                          │
│  - 性能分析 (profiling)                                      │
│  - 内存访问优化                                             │
└─────────────────────────────────────────────────────────────┘
```

### D.2 实际项目转换示例

**MATLAB (信号处理):**
```matlab
function [filtSignal] = bandpassFilter(signal, fs, lowcut, highcut)
    % 带通滤波
    [b, a] = butter(4, [lowcut highcut]/(fs/2));
    filtSignal = filtfilt(b, a, signal);

    % FFT 分析
    N = length(signal);
    Y = fft(signal);
    P2 = abs(Y/N);
    P1 = P2(1:N/2+1);
    P1(2:end-1) = 2*P1(2:end-1);
    f = fs*(0:(N/2))/N;
end
```

**CUDA 转换:**
```cpp
// Bandpass Filter Kernel (简化版 - 实际需用 FFT)
__global__
void bandpassKernel(const float* signal, float* output, int n,
                    float lowcut, float highcut, float fs) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        // 简化: 仅演示结构，实际需实现完整滤波器
        output[idx] = signal[idx];  // 占位
    }
}

// FFT Kernel (需要复杂实现，建议使用 cuFFT 库)
// 此处展示概念结构
__global__
void fftKernel(cuComplex* data, int n, int stride, int batch) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    // Cooley-Tukey FFT 实现
    // 使用 cuFFT 库更高效
}
```

---

## 参考资源

### 官方文档
- [NVIDIA CUDA Programming Guide v13.2](https://docs.nvidia.com/cuda/cuda-programming-guide/)
- [MATLAB GPU Computing](https://www.mathworks.com/help/parallel-computing/gpu-computing-in-matlab.html)
- [MATLAB Image Processing Toolbox](https://www.mathworks.com/help/images/)
- [MATLAB Mathematics](https://www.mathworks.com/help/matlab/math.html)
- [MATLAB Language Fundamentals](https://www.mathworks.com/help/matlab/language-fundamentals.html)

### CUDA 库
- [cuBLAS](https://docs.nvidia.com/cuda/cublas/) - 基础线性代数
- [cuFFT](https://docs.nvidia.com/cuda/cufft/) - 傅里叶变换
- [cuSOLVER](https://docs.nvidia.com/cuda/cusolver/) - 稀疏/稠密求解器
- [cuDNN](https://docs.nvidia.com/deeplearning/cudnn/) - 深度学习原语
- [Thrust](https://thrust.github.io/) - C++ 模板库
