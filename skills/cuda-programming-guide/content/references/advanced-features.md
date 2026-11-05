# Advanced CUDA Features

Detailed reference for advanced CUDA programming features including cooperative groups, CUDA graphs, dynamic parallelism, and more.

## Cooperative Groups

Cooperative groups enable flexible thread synchronization and collective operations.

### Basic Group Operations

```cpp
#include <cooperative_groups.h>

using namespace cooperative_groups;

// Within kernel
__global__ void cooperativeKernel(const float* data, float* result, int N)
{
    // Create thread group
    cg::thread_block block = cg::this_thread_block();

    // Create grid group
    cg::grid_group grid = cg::this_grid();

    // Thread block synchronization
    cg::sync(block);

    // Grid synchronization (requires cooperative launch)
    cg::sync(grid);

    // Cooperatively load data
    unsigned int rank = block.thread_rank();
    unsigned int block_rank = block.group_index().x;
}
```

### Cooperative Launch

```cpp
// Must launch with cooperative launch flag
void* args[] = {&d_data, &d_result, &N};
cudaLaunchCooperativeKernel(
    (void*)cooperativeKernel,
    dim3(blocksPerGrid),
    dim3(threadsPerBlock),
    args
);
```

## CUDA Graphs

CUDA Graphs reduce kernel launch overhead for repetitive workloads.

### Graph Creation

```cpp
// Method 1: Explicit graph construction
cudaGraph_t graph;
cudaGraphExec_t graphExec;

cudaGraphCreate(&graph, 0);

// Add kernel node
cudaGraphAddKernelNode(&kernelNode, graph, NULL, 0, &kernelNodeParams);

// Add memory copy node
cudaGraphAddMemcpyNode(&memcpyNode, graph, NULL, 0, &memcpyParams);

// Instantiate and execute
cudaGraphInstantiate(&graphExec, graph, NULL, NULL, 0);
cudaGraphLaunch(graphExec, stream);

// Method 2: Capture from stream
cudaStreamBeginCapture(stream, cudaStreamCaptureModeGlobal);
kernel1<<<grid, block>>>(data1);
kernel2<<<grid, block>>>(data2);
cudaStreamEndCapture(stream, &graph);
cudaGraphInstantiate(&graphExec, graph, NULL, NULL, 0);
```

## Dynamic Parallelism

Parent kernels can launch child kernels directly from GPU.

### Nested Kernel Launch

```cpp
__global__ void parentKernel(int* data, int depth)
{
    int tid = threadIdx.x;

    // Process data at this level
    data[tid] *= 2;

    // Launch child kernel if within depth limit
    if (depth < 2) {
        int childBlocks = 2;
        int childThreads = blockDim.x / 2;
        childKernel<<<childBlocks, childThreads>>>(data, depth + 1);
    }

    cudaDeviceSynchronize();
}
```

## Stream-Ordered Memory Allocator

Memory allocation within streams for better concurrency.

```cpp
cudaMallocAsync(&d_ptr, size, stream);
cudaFreeAsync(d_ptr, stream);

// Pool-based allocation for reduced overhead
cudaMemPoolProps poolProps = {};
poolProps.allocType = cudaMemAllocationTypePinned;
poolProps.location.type = cudaMemLocationTypeDevice;
poolProps.location.id = 0;
poolProps.handleTypes = cudaMemHandleTypeNone;
poolProps.mempoolProps.captureAccess = cudaMemPoolAccessPatternHostPrefer;

cudaMemPool_t memPool;
cudaCreateMemPool(&memPool, &poolProps);
```

## Asynchronous Data Copies

Overlapping memory transfers with computation.

```cpp
// Async copy from host to device
cudaMemcpyAsync(d_data, h_data, size, cudaMemcpyHostToDevice, stream);

// Async copy from device to host
cudaMemcpyAsync(h_result, d_result, size, cudaMemcpyDeviceToHost, stream);

// 2D async copy
cudaMemcpy2DAsync(d_data, pitch, h_data, host_pitch,
                  width * sizeof(float), height,
                  cudaMemcpyHostToDevice, stream);
```

## L2 Cache Control

Control L2 cache utilization for better performance.

```cpp
// Persistance access for L2 cache
cudaAccessPersistingWindowSize;

// Set L2 cache access policy
cudaDeviceSetCacheConfig(cudaFuncCachePreferShared);  // Prefer L1
cudaDeviceSetCacheConfig(cudaFuncCachePreferL1);      // Prefer L1
cudaDeviceSetCacheConfig(cudaFuncCachePreferNone);    // Equal preference

// L2 cache residency control
cudaStreamAttrValue streamAttr;
streamAttr.accessPolicyWindow.base_ptr = d_data;
streamAttr.accessPolicyWindow.num_bytes = size;
streamAttr.accessPolicyWindow.hitRatio = 0.9;  // 90% cache hit target
cudaStreamSetAttribute(stream, cudaStreamAttributeAccessPolicyWindow, &streamAttr);

// Reset access policy
cudaResetDevicePTDS(0);
```

## Warp-Level Primitives

Efficient communication within warps.

```cpp
// Warp shuffle operations
unsigned int val = threadData[threadIdx.x];

// Shuffle down: get value from thread + offset
float result = __shfl_down_sync(mask, val, offset);

// Shuffle up
float result = __shfl_up_sync(mask, val, offset);

// Shuffle across (specific lane)
float result = __shfl_sync(mask, val, srcLane);

// XOR shuffle (useful for butterfly reductions)
float result = __shfl_xor_sync(mask, val, laneMask);

// Warp vote functions
bool vote = __all_sync(mask, condition);
bool vote = __any_sync(mask, condition);
bool vote = __ballot_sync(mask, condition);

// Warp-level barrier
__syncwarp(mask);

// Warp reduction
template<typename T>
__device__ T warpReduceSum(T val) {
    for (int offset = warpSize/2; offset > 0; offset /= 2) {
        val += __shfl_down_sync(FULL_MASK, val, offset);
    }
    return val;
}
```

## Memory Synchronization Domains

Control memory ordering between groups of operations.

```cpp
cudaEvent_t event1, event2;

// Create events
cudaEventCreate(&event1);
cudaEventCreate(&event2);

// Record event in stream
cudaEventRecord(event1, stream1);

// Make stream2 wait for event1
cudaStreamWaitEvent(stream2, event1, 0);

// Memory fence for synchronization
cudaDeviceSynchronize();  // Global
__threadfence();          // Block
__threadfence_block();    // Block (weaker)

// Stream ordering with events
cudaEventRecord(event1, stream1);
kernel1<<<grid, block, 0, stream1>>>(data);
cudaEventRecord(event2, stream1);
cudaStreamWaitEvent(stream2, event2, 0);
kernel2<<<grid, block, 0, stream2>>>(data);
```

## Inter-Process Communication

Sharing GPU memory between processes.

```cpp
// Export memory to IPC handle
cudaIpcMemHandle_t handle;
cudaIpcGetMemHandle(&handle, d_data);

// Open IPC memory in another process
void* remote_ptr;
cudaIpcOpenMemHandle(&remote_ptr, handle, cudaIpcMemLazyEnablePeerAccess);

// Close IPC memory
cudaIpcCloseMemHandle(remote_ptr);

// Enable peer access
cudaDeviceEnablePeerAccess(deviceId, 0);
cudaCanAccessPeer(&canAccess, device0, device1);
```