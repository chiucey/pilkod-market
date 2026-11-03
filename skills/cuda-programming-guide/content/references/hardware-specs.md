# CUDA Hardware Specifications

Reference for NVIDIA GPU architectures, compute capabilities, and hardware limits.

## Compute Capabilities

### Summary Table

| Architecture | Compute Capability | SMs | CUDA Cores/SM | Global Memory | Shared Memory/SM | Registers/SM | L1 Cache | L2 Cache |
|--------------|-------------------|-----|---------------|---------------|------------------|--------------|----------|----------|
| Fermi GF100 | 2.0 | 16 | 32 | 6 GB | 48 KB | 32768 | 64 KB | 768 KB |
| Kepler GK110 | 3.0/3.5 | 15 | 192 | 12 GB | 48 KB | 65536 | 16/48 KB | 1536 KB |
| Maxwell GM200 | 5.0/5.2 | 24 | 128 | 12 GB | 64 KB | 65536 | 24/48 KB | 2048 KB |
| Pascal GP100 | 6.0 | 60 | 64 | 16 GB | 64 KB | 65536 | 24/64 KB | 4096 KB |
| Volta GV100 | 7.0 | 80 | 64 | 16 GB | 96 KB | 65536 | Inst/RO/128 KB | 6144 KB |
| Turing TU102 | 7.5 | 72 | 64 | 24 GB | 96 KB | 65536 | Inst/RO/128 KB | 6144 KB |
| Ampere GA100 | 8.0 | 108 | 64 | 80 GB | 164 KB | 65536 | 192 KB | 40960 KB |
| Ada AD102 | 8.9 | 144 | 128 | 24 GB | 128 KB | 65536 | 128 KB | 98304 KB |
| Hopper H100 | 9.0 | 132 | 128 | 80 GB | 228 KB | 65536 | 256 KB | 51200 KB |

## Hardware Limits

### Per-Block Constraints

| Resource | Maxwell+ | Older |
|----------|----------|-------|
| Max threads per block | 1024 | 512/1024 |
| Max block dimensions | (1024, 1024, 64) | (512/1024, ...) |
| Shared memory per block | 48 KB | 48 KB |
| Registers per block | 65536 | 32768/65536 |
| Constant memory | 64 KB | 64 KB |

### Per-Thread Constraints

| Resource | Limit |
|----------|-------|
| Registers | 255 |
| Local memory | 512 KB |
| Stack frame | Limited by registers |

### Grid Constraints

| Resource | Limit |
|----------|-------|
| Max grid dimensions | (2^31-1, 65535, 65535) |
| Max blocks per grid | Limited by threads/block |

## Streaming Multiprocessor (SM) Architecture

### SM Components (Modern GPU)

```
┌─────────────────────────────────────────┐
│           Streaming Multiprocessor      │
│  ┌─────────────────────────────────┐    │
│  │     Instruction Cache / I-cache │    │
│  └─────────────────────────────────┘    │
│  ┌──────────┐  ┌──────────┐            │
│  │ Warp     │  │ Dispatch │            │
│  │ Scheduler│  │ Units    │            │
│  └──────────┘  └──────────┘            │
│  ┌─────────────────────────────────┐    │
│  │   CUDA Cores (ALU/INT/FP64/FP16)│    │
│  │   ┌─┐ ┌─┐ ┌─┐ ┌─┐ ... (64/128)  │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │   Tensor Cores (Volta+)         │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │   RT Cores (Turing+)            │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │   Shared Memory / L1 Cache      │    │
│  │   (16-164 KB configurable)      │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │   Registers (65536 x 32-bit)    │    │
│  └─────────────────────────────────┘    │
│  ┌─────────────────────────────────┐    │
│  │   Load/Store Units              │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Warp Scheduling

- Each SM has 4 warp schedulers (modern GPUs)
- Each scheduler can issue one instruction per cycle
- Warps are 32 threads executing in lockstep
- Maximum concurrent warps per SM: 64 (varies by architecture)

## Memory Hierarchy

### Memory Bandwidth Comparison

| Memory Type | Bandwidth (GB/s) | Latency (cycles) |
|-------------|-----------------|------------------|
| Register | ~8000 | 1 |
| Shared Memory | ~8000 | 1 |
| L1 Cache | ~8000 | 1-2 |
| L2 Cache | ~2000 | 20-30 |
| Global Memory | 500-2000 | 200-400 |
| Host Memory (PCIe 4.0) | ~32 | ~1000 |

### Memory Access Patterns

```
Global Memory (DRAM)
        │
        ▼
    L2 Cache (Shared by all SMs)
        │
        ▼
    L1/Texture Cache (per SM)
        │
        ▼
    Shared Memory (per SM, programmable)
        │
        ▼
    Registers (per thread)
```

## Occupancy Calculator

### Threads per Block Formula

```cpp
// Maximum threads = min(1024, registers_limit / registers_per_thread)
// Example for 64 registers per thread:
// max_threads = min(1024, 65536 / 64) = min(1024, 1024) = 1024

// Shared memory constraint
// shared_per_block = threads * shared_per_thread
// max_threads = min(1024, 49152 / shared_per_thread)
```

### Register Spilling

When registers exceed limits, data spills to local memory (slow):
- Local memory uses global memory bandwidth
- Register pressure increases with complex expressions
- Use `__launch_bounds__` to control occupancy

```cpp
// Suggest occupancy to compiler
__global__ __launch_bounds__(256, 8) void kernel(...) {
    // Forces compiler to use max 256 threads per block
    // Compiler may increase register usage for performance
}
```

## Device Query Example

```cpp
#include <cuda_runtime.h>
#include <stdio.h>

int main() {
    int deviceCount;
    cudaGetDeviceCount(&deviceCount);

    for (int i = 0; i < deviceCount; i++) {
        cudaDeviceProp prop;
        cudaGetDeviceProperties(&prop, i);

        printf("Device %d: %s\n", i, prop.name);
        printf("  Compute Capability: %d.%d\n", prop.major, prop.minor);
        printf("  Total Global Memory: %.2f GB\n", prop.totalGlobalMem / 1e9);
        printf("  Shared Memory per Block: %zu KB\n", prop.sharedMemPerBlock / 1024);
        printf("  Registers per Block: %d\n", prop.regsPerBlock);
        printf("  Warps per Multiprocessor: %d\n", prop.warpSize);
        printf("  Memory Pitch: %zu MB\n", prop.memPitch / 1024 / 1024);
        printf("  Max Threads per Block: %d\n", prop.maxThreadsPerBlock);
        printf("  Max Threads Dim: (%d, %d, %d)\n",
               prop.maxThreadsDim[0], prop.maxThreadsDim[1], prop.maxThreadsDim[2]);
        printf("  Max Grid Size: (%d, %d, %d)\n",
               prop.maxGridSize[0], prop.maxGridSize[1], prop.maxGridSize[2]);
        printf("  Clock Rate: %.2f GHz\n", prop.clockRate / 1e6);
        printf("  Memory Clock Rate: %.2f GHz\n", prop.memoryClockRate / 1e6);
        printf("  Memory Bus Width: %d bits\n", prop.memoryBusWidth);
        printf("  L2 Cache Size: %d KB\n", prop.l2CacheSize / 1024);
        printf("  Concurrent Kernels: %d\n", prop.concurrentKernels);
        printf("  Unified Memory: %s\n", prop.unifiedAddressing ? "Yes" : "No");
    }
    return 0;
}
```