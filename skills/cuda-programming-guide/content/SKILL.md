---
name: cuda-programming-guide
description: Comprehensive CUDA GPU parallel programming skill. Use when users ask about CUDA programming, GPU kernel development, CUDA syntax (threadIdx, blockIdx, gridDim, blockDim), memory management (cudaMalloc, cudaMemcpy, unified memory), SIMT execution model (warps), CUDA streams, or want to learn GPU parallel computing with NVIDIA. Triggers include: "CUDA programming", "GPU kernel", "CUDA tutorial", "parallel computing on GPU", "CUDA memory management", "CUDA concurrent programming", etc.
---

# CUDA Programming Guide

A comprehensive skill for mastering NVIDIA CUDA parallel programming, covering programming model, kernel development, memory management, and advanced features.

## Core Concepts

### Programming Model Overview

CUDA (Compute Unified Device Architecture) extends C/C++ for parallel computing on NVIDIA GPUs.

**Key Architecture Components:**
- **Host (CPU)**: Controls program flow, memory allocation
- **Device (GPU)**: Executes parallel kernels
- **Kernel**: Function that runs on GPU, called from host

```
Host Code (CPU)                    Device Code (GPU)
┌─────────────────────┐            ┌─────────────────────┐
│  Memory Allocation  │───────────▶│  Global Memory      │
│  Data Transfer      │            │  Shared Memory      │
│  Kernel Launch      │            │  Registers          │
└─────────────────────┘            └─────────────────────┘
```

### Thread Hierarchy

CUDA uses a hierarchical thread organization:

```
Grid (1D/2D/3D)
├── Block 0 (1D/2D/3D)
│   ├── Thread 0
│   ├── Thread 1
│   └── ... (up to 1024 threads per block)
├── Block 1
│   └── ...
└── Block N
```

**Built-in Variables:**
- `threadIdx.{x,y,z}`: Thread index within block (0-based)
- `blockIdx.{x,y,z}`: Block index within grid
- `blockDim.{x,y,z}`: Block dimensions
- `gridDim.{x,y,z}`: Grid dimensions

### Memory Model

| Memory Type | Scope | Speed | Persistence |
|-------------|-------|-------|-------------|
| Register | Thread | Fastest | Thread lifetime |
| Local Memory | Thread | Slow | Thread lifetime |
| Shared Memory | Block | Fast | Block lifetime |
| Global Memory | Grid/Device | Slow | Application |
| Constant Memory | Grid/Device | Fast (cached) | Application |
| Texture Memory | Grid/Device | Fast (cached) | Application |

## Kernel Development

### Basic Kernel Syntax

```cpp
// Kernel definition
__global__ void vectorAdd(const float* A, const float* B, float* C, int N)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        C[i] = A[i] + B[i];
    }
}

// Kernel launch from host
int threadsPerBlock = 256;
int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;
vectorAdd<<<blocksPerGrid, threadsPerBlock>>>(d_A, d_B, d_C, N);
```

### Common CUDA Functions

```cpp
// Memory allocation
cudaMalloc((void**)&d_ptr, size);      // Device memory
cudaMallocManaged(&ptr, size);          // Unified memory
cudaFree(d_ptr);                        // Free device memory

// Memory copy
cudaMemcpy(d_dst, h_src, size, cudaMemcpyHostToDevice);
cudaMemcpy(h_dst, d_src, size, cudaMemcpyDeviceToHost);
cudaMemcpy(d_dst, d_src, size, cudaMemcpyDeviceToDevice);

// Synchronization
cudaDeviceSynchronize();                // Wait for device completion
__syncthreads();                        // Block-level synchronization
```

## Execution Configuration

### Grid and Block Sizing

```cpp
// 1D configuration
dim3 blockSize(256);
dim3 gridSize((N + blockSize.x - 1) / blockSize.x);
kernel<<<gridSize, blockSize>>>(args);

// 2D configuration for image processing
dim3 blockSize(16, 16);
dim3 gridSize((width + 15) / 16, (height + 15) / 16);
processImage<<<gridSize, blockSize>>>(image, width, height);

// 3D configuration for volume data
dim3 blockSize(8, 8, 8);
dim3 gridSize((depth + 7) / 8, (height + 7) / 8, (width + 7) / 8);
processVolume<<<gridSize, blockSize>>>(volume, depth, height, width);
```

## Shared Memory & Cooperation

### Shared Memory Usage

```cpp
__global__ void sharedMemoryKernel(const float* data, float* result, int N)
{
    __shared__ float sharedData[256];

    int tid = threadIdx.x;
    int gid = blockIdx.x * blockDim.x + threadIdx.x;

    // Load data to shared memory
    sharedData[tid] = (gid < N) ? data[gid] : 0;
    __syncthreads();

    // Parallel reduction in shared memory
    for (int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (tid < s && gid + s < N) {
            sharedData[tid] += sharedData[tid + s];
        }
        __syncthreads();
    }

    // Write result
    if (tid == 0) {
        result[blockIdx.x] = sharedData[0];
    }
}
```

## Unified Memory

### Simplified Memory Management

```cpp
// Traditional approach (explicit copy)
float *h_data, *d_data;
h_data = (float*)malloc(N * sizeof(float));
cudaMalloc(&d_data, N * sizeof(float));
cudaMemcpy(d_data, h_data, N * sizeof(float), cudaMemcpyHostToDevice);
// ... kernel execution ...
cudaMemcpy(h_data, d_data, N * sizeof(float), cudaMemcpyDeviceToHost);

// Unified memory approach (CUDA 6.0+)
float *data;
cudaMallocManaged(&data, N * sizeof(float));
// Single pointer works on both CPU and GPU
fillData(data, N);           // CPU can access
processKernel<<<...>>>(data, N);  // GPU can access
cudaDeviceSynchronize();
useResults(data, N);         // CPU can access again
cudaFree(data);
```

## CUDA Streams

### Concurrent Execution

```cpp
cudaStream_t stream1, stream2;
cudaStreamCreate(&stream1);
cudaStreamCreate(&stream2);

// Concurrent kernel execution
kernel1<<<gridSize, blockSize, 0, stream1>>>(data1, N);
kernel2<<<gridSize, blockSize, 0, stream2>>>(data2, N);

// Async memory operations
cudaMemcpyAsync(d_data, h_data, size, cudaMemcpyHostToDevice, stream1);

// Wait for specific stream
cudaStreamSynchronize(stream1);
cudaStreamDestroy(stream1);
cudaStreamDestroy(stream2);
```

## SIMT Architecture

### Warp Execution

- Warp: Group of 32 threads executing together
- All threads in a warp execute same instruction
- Branch divergence reduces efficiency:

```cpp
// This causes divergence
if (threadIdx.x % 2 == 0) {
    // Warp executes this for half threads
} else {
    // Warp executes this for other half
}
// Both paths executed sequentially
```

**Best Practice:** Avoid divergent branches within a warp when possible.

## Performance Optimization

### Key Principles

1. **Memory Coalescing**: Access global memory in contiguous patterns
2. **Shared Memory Bank Conflicts**: Avoid accessing same bank simultaneously
3. **Occupancy**: Maximize active warps per SM
4. **Register Pressure**: Limit local variables per thread

```cpp
// Good: Coalesced memory access
__global__ void coalescedAccess(float* data, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        float val = data[i];  // Contiguous access per warp
        data[i] = val * 2.0f;
    }
}

// Bad: Non-coalesced memory access
__global__ void scatteredAccess(float* data, int N) {
    int i = threadIdx.x;
    if (i < N) {
        float val = data[i * 32];  // Strided access causes inefficiency
        data[i * 32] = val * 2.0f;
    }
}
```

## Complete Example: Vector Addition

```cpp
#include <cuda_runtime.h>
#include <stdio.h>

#define N 1000000

__global__ void vectorAdd(const float* A, const float* B, float* C, int N)
{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        C[i] = A[i] + B[i];
    }
}

int main()
{
    float *h_A, *h_B, *h_C;
    float *d_A, *d_B, *d_C;
    size_t bytes = N * sizeof(float);

    // Host allocation
    h_A = (float*)malloc(bytes);
    h_B = (float*)malloc(bytes);
    h_C = (float*)malloc(bytes);

    // Initialize data
    for (int i = 0; i < N; i++) {
        h_A[i] = i * 1.0f;
        h_B[i] = i * 2.0f;
    }

    // Device allocation
    cudaMalloc(&d_A, bytes);
    cudaMalloc(&d_B, bytes);
    cudaMalloc(&d_C, bytes);

    // Copy to device
    cudaMemcpy(d_A, h_A, bytes, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B, bytes, cudaMemcpyHostToDevice);

    // Launch kernel
    int threadsPerBlock = 256;
    int blocksPerGrid = (N + threadsPerBlock - 1) / threadsPerBlock;
    vectorAdd<<<blocksPerGrid, threadsPerBlock>>>(d_A, d_B, d_C, N);

    // Copy result back
    cudaMemcpy(h_C, d_C, bytes, cudaMemcpyDeviceToHost);

    // Verify
    for (int i = 0; i < N; i++) {
        if (abs(h_C[i] - (h_A[i] + h_B[i])) > 1e-5) {
            printf("Error at index %d\n", i);
            break;
        }
    }

    // Cleanup
    cudaFree(d_A);
    cudaFree(d_B);
    cudaFree(d_C);
    free(h_A);
    free(h_B);
    free(h_C);

    printf("Vector addition completed successfully!\n");
    return 0;
}
```

## Compilation

```bash
# Basic compilation
nvcc -o program program.cu

# With optimization
nvcc -O3 -arch=sm_80 -o program program.cu

# Separate compilation for large projects
nvcc -arch=sm_80 -dc device.cu
nvcc -arch=sm_80 -c host.cpp
nvcc -dlink -arch=sm_80 -o device_link.o device.cu host.o
```

## Reference Quick Lookup

For detailed information on:
- Advanced features (cooperative groups, CUDA graphs, dynamic parallelism) → `references/advanced-features.md`
- Compute capabilities and hardware specs → `references/hardware-specs.md`
- Common pitfalls and debugging → `references/debugging.md`
- Additional code examples → `references/code-examples.md`

## Quick Commands Reference

| Task | Command/Function |
|------|------------------|
| Allocate device memory | `cudaMalloc(&ptr, size)` |
| Copy memory | `cudaMemcpy(dst, src, size, direction)` |
| Launch kernel | `kernel<<<grid, block>>>(args)` |
| Device sync | `cudaDeviceSynchronize()` |
| Block sync | `__syncthreads()` |
| Unified memory | `cudaMallocManaged(&ptr, size)` |
| Create stream | `cudaStreamCreate(&stream)` |
| Compile | `nvcc -o out source.cu` |