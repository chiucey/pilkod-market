# CUDA Programming Guide Key Concepts Reference

Based on [NVIDIA CUDA Programming Guide v13.2](https://docs.nvidia.com/cuda/cuda-programming-guide/)

## 1. Programming Model

### 1.1 Kernels (Section 2.2)
CUDA extends C++ by allowing the programmer to define C++ functions called **kernels**. When called, these kernels are executed N times in parallel by N different CUDA threads.

**Kernel Definition Syntax:**
```cpp
__global__ void kernelName(float* param) { ... }
```

- `__global__`: Indicates a kernel that can be called from host (CPU) and executed on device (GPU)
- `__device__`: Function executed on device only, callable from device only
- `__host__`: Function executed on host only (default)

### 1.2 Thread Hierarchy

```
Grid (整个GPU)
  └── Block (SM - Streaming Multiprocessor)
        └── Thread (CUDA Core)
```

**Thread Identification:**
- `threadIdx`: 3-component thread index within a block
- `blockIdx`: 3-component block index within the grid
- `blockDim`: Dimensions of the block
- `gridDim`: Dimensions of the grid

**Common Patterns:**
```cpp
// 1D thread index
int idx = blockIdx.x * blockDim.x + threadIdx.x;

// 2D thread index (for 2D data like images)
int row = blockIdx.y * blockDim.y + threadIdx.y;
int col = blockIdx.x * blockDim.x + threadIdx.x;
int index = row * width + col;

// 3D thread index (for 3D volumes)
int z = blockIdx.z * blockDim.z + threadIdx.z;
int idx = (z * height + row) * width + col;
```

### 1.3 Memory Hierarchy

| Memory Type | Scope | Speed | Persistence |
|------------|-------|-------|-------------|
| Register | Thread | Fastest | Thread lifetime |
| Local Memory | Thread | Slow | Thread lifetime |
| Shared Memory | Block | Fast | Block lifetime |
| Global Memory | Grid | Slow | Application lifetime |
| Constant Memory | Grid | Fast (cached) | Application lifetime |
| Texture Memory | Grid | Fast (cached) | Application lifetime |

### 1.4 SIMT Execution Model

CUDA uses **Single Instruction, Multiple Thread (SIMT)** architecture:
- Threads are executed in groups called **warps** (32 threads)
- All threads in a warp execute the same instruction
- Divergent branches cause serialization

## 2. Memory Management

### 2.1 Device Memory Allocation
```cpp
// Allocation
float* d_ptr;
cudaMalloc(&d_ptr, size * sizeof(float));

// Copy
cudaMemcpy(d_ptr, h_ptr, size * sizeof(float), cudaMemcpyHostToDevice);
cudaMemcpy(h_ptr, d_ptr, size * sizeof(float), cudaMemcpyDeviceToHost);

// Free
cudaFree(d_ptr);
```

### 2.2 Unified Memory (Section 4.1)
Unified Memory creates a pool of managed memory that is accessible from both CPU and GPU with a single pointer.

```cpp
float* data;
cudaMallocManaged(&data, size * sizeof(float));

// Automatic data migration between devices
// No explicit memcpy needed
kernel<<<gridSize, blockSize>>>(data, size);
cudaDeviceSynchronize();

// CPU can directly read the data after synchronization
```

### 2.3 Memory Copy Types
- `cudaMemcpyHostToDevice`
- `cudaMemcpyDeviceToHost`
- `cudaMemcpyDeviceToDevice`
- `cudaMemcpyHostToHost`

## 3. Thread Synchronization

### 3.1 Intra-Block Synchronization
```cpp
__syncthreads(); // All threads in a block wait here
```

### 3.2 Device-Level Synchronization
```cpp
cudaDeviceSynchronize(); // Host waits for all GPU operations
```

### 3.3 Memory Fence
```cpp
__threadfence(); // Ensures memory ordering
__threadfence_block(); // Block-scoped fence
```

## 4. Common CUDA Functions

### 4.1 Math Functions
```cpp
// Trigonometric
sinf(x), cosf(x), tanf(x), asinf(x), acosf(x)

// Exponential/Logarithmic
expf(x), logf(x), exp2f(x), log2f(x), powf(x, y)

// Square Root
sqrtf(x), rsqrtf(x) // 1/sqrt(x)

// Absolute Value
fabsf(x), fabsf(-5.0f)

// Max/Min
fmaxf(x, y), fminf(x, y)

// Rounding
floorf(x), ceilf(x), roundf(x)
```

### 4.2 Atomic Operations
```cpp
atomicAdd(address, val);     // Atomic addition
atomicExch(address, val);   // Atomic exchange
atomicMin(address, val);     // Atomic minimum
atomicMax(address, val);     // Atomic maximum
atomicCAS(address, compare, val); // Atomic compare-and-swap
```

### 4.3 Warp Shuffle
```cpp
__shfl_sync(mask, var, srcLane);     // Exchange values between threads
__shfl_up_sync(mask, var, delta);     // Shift up
__shfl_down_sync(mask, var, delta);  // Shift down
__shfl_xor_sync(mask, var, laneMask); // XOR shuffle
```

## 5. Execution Configuration

### 5.1 Kernel Launch Syntax
```cpp
kernelName<<<numBlocks, threadsPerBlock, sharedMemBytes, stream>>>(args...);
```

### 5.2 Common Configurations

| Data Size | Block Size | Grid Calculation |
|-----------|------------|-----------------|
| 1D (N) | 256 or 512 | (N + 255) / 256 |
| 2D (HxW) | 16x16 | ((H+15)/16, (W+15)/16) |
| 3D (DxHxW) | 8x8x8 or 4x8x8 | ((D+7)/8, (H+7)/8, (W+7)/8) |

### 5.3 Maximum Thread per Block
- Maximum threads per block: 1024
- Maximum block dimensions: (1024, 1024, 64)
- Maximum grid dimensions: (2^31-1, 65535, 65535)

## 6. Compute Capabilities

| Capability | Architecture | Max Threads/Block | Shared Memory | Registers |
|------------|-------------|-------------------|---------------|-----------|
| 7.0 | Volta | 1024 | 96 KB | 65536 |
| 8.0 | Ampere | 1024 | 164 KB | 65536 |
| 9.0 | Hopper | 1024 | 228 KB | 65536 |

## 7. Error Handling

```cpp
#define CUDA_CHECK(call) \
    do { \
        cudaError_t error = call; \
        if (error != cudaSuccess) { \
            printf("CUDA error at %s:%d: %s\n", __FILE__, __LINE__, \
                   cudaGetErrorString(error)); \
            exit(1); \
        } \
    } while(0)

// Usage
CUDA_CHECK(cudaMalloc(&ptr, size));
CUDA_CHECK(cudaMemcpy(dst, src, size, kind));
CUDA_CHECK(cudaDeviceSynchronize());
```

## 8. Shared Memory Example

```cpp
#define TILE_WIDTH 16

__global__
void sharedMemoryKernel(const float* A, const float* B, float* C, int n) {
    __shared__ float tileA[TILE_WIDTH][TILE_WIDTH];
    __shared__ float tileB[TILE_WIDTH][TILE_WIDTH];

    int row = blockIdx.y * TILE_WIDTH + threadIdx.y;
    int col = blockIdx.x * TILE_WIDTH + threadIdx.x;
    float sum = 0.0f;

    for (int m = 0; m < (n + TILE_WIDTH - 1) / TILE_WIDTH; ++m) {
        // Load tile into shared memory
        if (row < n && (m * TILE_WIDTH + threadIdx.x) < n)
            tileA[threadIdx.y][threadIdx.x] = A[row * n + m * TILE_WIDTH + threadIdx.x];
        else
            tileA[threadIdx.y][threadIdx.x] = 0.0f;

        if ((m * TILE_WIDTH + threadIdx.y) < n && col < n)
            tileB[threadIdx.y][threadIdx.x] = B[(m * TILE_WIDTH + threadIdx.y) * n + col];
        else
            tileB[threadIdx.y][threadIdx.x] = 0.0f;

        __syncthreads();

        // Compute tile multiplication
        for (int k = 0; k < TILE_WIDTH; ++k)
            sum += tileA[threadIdx.y][k] * tileB[k][threadIdx.x];

        __syncthreads();
    }

    if (row < n && col < n)
        C[row * n + col] = sum;
}
```

## 9. Reduction (Sum/Max/etc.)

```cpp
// Parallel reduction for sum
__global__
void reduceSum(const float* input, float* output, int n) {
    __shared__ float sdata[256];

    int tid = threadIdx.x;
    int idx = blockIdx.x * blockDim.x + threadIdx.x;

    sdata[tid] = (idx < n) ? input[idx] : 0.0f;
    __syncthreads();

    // In-place reduction in shared memory
    for (int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (tid < s && idx + s < n) {
            sdata[tid] += sdata[tid + s];
        }
        __syncthreads();
    }

    if (tid == 0) {
        atomicAdd(output, sdata[0]);
    }
}
```

## 10. Key References

- [NVIDIA CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/)
- [CUDA C++ Programming Guide - Memory Model](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/cuda-cpp-memory-model.html)
- [CUDA C++ Programming Guide - Execution Model](https://docs.nvidia.com/cuda/cuda-programming-guide/05-appendices/cuda-cpp-execution-model.html)
