# CUDA Debugging and Common Pitfalls

Common issues, debugging techniques, and best practices for CUDA development.

## Common Errors

### Memory Errors

```cpp
// ❌ Error: Using uninitialized device memory
float* d_data;
kernel<<<grid, block>>>(d_data, N);  // d_data not allocated!

// ✅ Fix: Allocate before use
cudaMalloc(&d_data, N * sizeof(float));
kernel<<<grid, block>>>(d_data, N);
cudaFree(d_data);

// ❌ Error: Memory leak
cudaMalloc(&d_data, size);
// ... use d_data ...
return;  // Forgot cudaFree!

// ✅ Fix: Always free
cudaMalloc(&d_data, size);
// ... use d_data ...
cudaFree(d_data);
```

### Index Errors

```cpp
// ❌ Error: Out of bounds access
__global__ void kernel(float* data, int N) {
    int i = threadIdx.x;
    data[i] = 0;  // Assumes N <= blockDim.x, not guaranteed!
}

// ✅ Fix: Always check bounds
__global__ void kernel(float* data, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        data[i] = 0;
    }
}

// ❌ Error: Wrong index calculation
__global__ void kernel(float* data, int width, int height) {
    int x = blockIdx.x;  // Wrong! Uses block index
    int y = threadIdx.y;
    data[y * width + x] = 0;  // Wrong indexing

    // ✅ Fix
    int x = threadIdx.x + blockIdx.x * blockDim.x;
    int y = threadIdx.y + blockIdx.y * blockDim.y;
    if (x < width && y < height) {
        data[y * width + x] = 0;
    }
}
```

### Synchronization Errors

```cpp
// ❌ Error: Race condition without sync
__global__ void badKernel(float* data) {
    if (threadIdx.x > 0) {
        data[0] += data[threadIdx.x];  // Multiple threads writing data[0]
    }
}

// ✅ Fix: Use atomic operations or reduction
__global__ void goodKernel(float* data) {
    atomicAdd(&data[0], data[threadIdx.x]);
}

// ❌ Error: Forgetting device synchronize
cudaMalloc(&d_data, size);
kernel<<<grid, block>>>(d_data);
memcpy(h_data, d_data, size);  // Wrong! GPU may not have finished

// ✅ Fix: Synchronize before copying
cudaMalloc(&d_data, size);
kernel<<<grid, block>>>(d_data);
cudaDeviceSynchronize();  // Wait for kernel completion
memcpy(h_data, d_data, size);
```

### Type Errors

```cpp
// ❌ Error: Pointer type mismatch
int* h_ptr;
float* d_ptr;
cudaMemcpy(d_ptr, h_ptr, size, cudaMemcpyHostToDevice);  // Type mismatch!

// ✅ Fix: Ensure types match
float* h_ptr;
float* d_ptr;
cudaMemcpy(d_ptr, h_ptr, size, cudaMemcpyHostToDevice);

// ❌ Error: Division in index (integer truncation)
int i = blockIdx.x * blockDim.x + threadIdx.x;
float normalized = i / N;  // Always 0 if i < N!

// ✅ Fix: Cast to float first
float normalized = (float)i / N;
```

## Debugging Tools

### cuda-gdb

```bash
# Compile with debug symbols
nvcc -g -G -o program program.cu

# -g: Generate debug symbols
# -G: Disable optimizations (preserves variable values)

# Run debugger
cuda-gdb ./program

# Common commands
(cuda-gdb) break kernel  # Set breakpoint
(cuda-gdb) run           # Start execution
(cuda-gdb) print var     # Print variable
(cuda-gdb) next          # Step line
(cuda-gdb) continue      # Continue execution
(cuda-gdb) info threads  # List threads
(cuda-gdb) thread apply all print var  # Print across all threads
```

### Nsight Visual Studio/Nsight Eclipse

- GUI debugging with CUDA support
- Register and memory inspection
- Warp-level divergence visualization

### cuda-memcheck

```bash
# Check for memory errors
cuda-memcheck ./program

# Options
cuda-memcheck --leak-check yes ./program  # Check for memory leaks
cuda-memcheck --tool memcheck ./program   # Memory access checking
cuda-memcheck --tool racecheck ./program  # Check for race conditions
```

### Compute Sanitizer

```bash
# Comprehensive runtime checking
compute-sanitizer ./program

# Useful for finding:
# - Out of bounds memory access
# - Race conditions
# - Memory leaks
# - Uninitialized memory usage
```

### Nsight Compute

```bash
# GPU kernel profiling
ncu -o profile_result ./program

# Specific metric collection
ncu --metrics sm__throughput.avg.pct_of_peak_sustained,\
               dram__bytes.sum,\
               sm__warps_active.avg.pct_of_peak_sustained \
               ./program

# Interactive UI
ncu-ui profile_result.ncu-rep
```

### Nsight Systems

```bash
# System-wide profiling
nsys profile -o system_profile ./program

# Multi-process profiling
nsys profile --trace=cuda,nvtx,osrt -o profile ./program
```

## Error Handling

### Proper CUDA Error Checking

```cpp
#include <cuda_runtime.h>
#include <stdio.h>

#define CHECK_CUDA(call) \
    do { \
        cudaError_t err = call; \
        if (err != cudaSuccess) { \
            fprintf(stderr, "CUDA error at %s:%d: %s\n", \
                    __FILE__, __LINE__, \
                    cudaGetErrorString(err)); \
            exit(EXIT_FAILURE); \
        } \
    } while(0)

// Usage
CHECK_CUDA(cudaMalloc(&d_ptr, size));
CHECK_CUDA(cudaMemcpy(d_ptr, h_ptr, size, cudaMemcpyHostToDevice));
kernel<<<grid, block>>>(d_ptr);
CHECK_CUDA(cudaGetLastError());  // Check kernel launch
CHECK_CUDA(cudaDeviceSynchronize());  // Check kernel execution
```

### Kernel Error Detection

```cpp
__global__ void kernel(float* data, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;

    // Your computation
    if (data[i] < 0) {
        // Should not happen
        // printf can be used for debugging (slow)
        printf("Error at index %d: value=%f\n", i, data[i]);
    }
}

int main() {
    kernel<<<grid, block>>>(d_data, N);
    cudaDeviceSynchronize();

    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) {
        printf("Kernel error: %s\n", cudaGetErrorString(err));
    }
}
```

## Performance Pitfalls

### Misaligned Memory Access

```cpp
// ❌ Slow: Misaligned access
__global__ void badKernel(float* data, int stride, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        float val = data[i * stride];  // Strided access
    }
}

// ✅ Fast: Aligned/contiguous access
__global__ void goodKernel(float* data, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        float val = data[i];  // Contiguous access
    }
}
```

### Bank Conflicts in Shared Memory

```cpp
// ❌ Bad: Bank conflicts (all threads accessing same bank)
__global__ void badShared(float* data) {
    __shared__ float shared[256];
    int tid = threadIdx.x;
    shared[tid] = data[tid];
    __syncthreads();
    float val = shared[tid * 4];  // Conflicts!
}

// ✅ Good: Staggered access pattern
__global__ void goodShared(float* data) {
    __shared__ float shared[256];
    int tid = threadIdx.x;
    shared[tid] = data[tid];
    __syncthreads();
    // Access with stride avoiding bank conflicts
    float val = shared[(tid + threadIdx.x) & 255];
}
```

### Constant Memory Broadcast

```cpp
// ❌ Bad: Large constant array (may not fit cache)
__constant__ float largeArray[1024];

// ✅ Good: Small constant array (efficient broadcast)
__constant__ float smallArray[64];  // Fits in constant cache
```

## Best Practices Checklist

- [ ] Always check bounds in kernel
- [ ] Use cudaMallocManaged for simpler memory management
- [ ] Prefer contiguous memory access patterns
- [ ] Minimize host-device transfers
- [ ] Use appropriate block size (multiples of 32)
- [ ] Check cudaGetLastError after kernel launch
- [ ] Synchronize before reading device results
- [ ] Enable error checking during development
- [ ] Profile to identify bottlenecks
- [ ] Use unified memory for simpler programming
- [ ] Avoid thread divergence when possible
- [ ] Optimize shared memory access patterns