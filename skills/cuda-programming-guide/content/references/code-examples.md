# CUDA Code Examples

Practical CUDA code examples for common parallel computing patterns.

## Matrix Multiplication

### Basic Implementation

```cpp
#include <cuda_runtime.h>
#include <stdio.h>

#define TILE_SIZE 16

// Matrix multiplication kernel
__global__ void matrixMul(float* A, float* B, float* C, int M, int N, int K)
{
    // Shared memory for tiles
    __shared__ float As[TILE_SIZE][TILE_SIZE];
    __shared__ float Bs[TILE_SIZE][TILE_SIZE];

    int row = blockIdx.y * TILE_SIZE + threadIdx.y;
    int col = blockIdx.x * TILE_SIZE + threadIdx.x;

    float sum = 0.0f;

    // Loop over tiles
    for (int t = 0; t < (N + TILE_SIZE - 1) / TILE_SIZE; t++) {
        // Load tiles into shared memory
        if (row < M && (t * TILE_SIZE + threadIdx.x) < N) {
            As[threadIdx.y][threadIdx.x] = A[row * N + t * TILE_SIZE + threadIdx.x];
        } else {
            As[threadIdx.y][threadIdx.x] = 0.0f;
        }

        if ((t * TILE_SIZE + threadIdx.y) < N && col < K) {
            Bs[threadIdx.y][threadIdx.x] = B[(t * TILE_SIZE + threadIdx.y) * K + col];
        } else {
            Bs[threadIdx.y][threadIdx.x] = 0.0f;
        }

        __syncthreads();

        // Compute partial result
        for (int i = 0; i < TILE_SIZE; i++) {
            sum += As[threadIdx.y][i] * Bs[i][threadIdx.x];
        }

        __syncthreads();
    }

    // Store result
    if (row < M && col < K) {
        C[row * K + col] = sum;
    }
}

int main() {
    int M = 1024, N = 1024, K = 1024;
    size_t bytesA = M * N * sizeof(float);
    size_t bytesB = N * K * sizeof(float);
    size_t bytesC = M * K * sizeof(float);

    float *h_A = (float*)malloc(bytesA);
    float *h_B = (float*)malloc(bytesB);
    float *h_C = (float*)malloc(bytesC);

    float *d_A, *d_B, *d_C;
    cudaMalloc(&d_A, bytesA);
    cudaMalloc(&d_B, bytesB);
    cudaMalloc(&d_C, bytesC);

    // Initialize matrices
    for (int i = 0; i < M * N; i++) h_A[i] = rand() / (float)RAND_MAX;
    for (int i = 0; i < N * K; i++) h_B[i] = rand() / (float)RAND_MAX;

    cudaMemcpy(d_A, h_A, bytesA, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B, bytesB, cudaMemcpyHostToDevice);

    dim3 block(TILE_SIZE, TILE_SIZE);
    dim3 grid((K + TILE_SIZE - 1) / TILE_SIZE, (M + TILE_SIZE - 1) / TILE_SIZE);

    matrixMul<<<grid, block>>>(d_A, d_B, d_C, M, N, K);

    cudaMemcpy(h_C, d_C, bytesC, cudaMemcpyDeviceToHost);

    printf("Matrix multiplication completed\n");

    cudaFree(d_A); cudaFree(d_B); cudaFree(d_C);
    free(h_A); free(h_B); free(h_C);

    return 0;
}
```

## Parallel Reduction

### Sum Reduction

```cpp
// Sequential reduction on host
float reduceCPU(float* data, int N) {
    float sum = 0;
    for (int i = 0; i < N; i++) sum += data[i];
    return sum;
}

// Parallel reduction - naive
__global__ void reduceNaive(float* input, float* output, int N) {
    extern __shared__ float sdata[];
    int tid = threadIdx.x;
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    sdata[tid] = (i < N) ? input[i] : 0;
    __syncthreads();

    for (int s = 1; s < blockDim.x; s *= 2) {
        if (tid % (2 * s) == 0) {
            sdata[tid] += sdata[tid + s];
        }
        __syncthreads();
    }

    if (tid == 0) output[blockIdx.x] = sdata[0];
}

// Parallel reduction - optimized (fewer bank conflicts)
__global__ void reduceOptimized(float* input, float* output, int N) {
    extern __shared__ float sdata[];
    int tid = threadIdx.x;
    int i = blockIdx.x * (blockDim.x * 2) + threadIdx.x;

    // Load and perform first level of reduction
    float sum = 0;
    if (i < N) sum = input[i];
    if (i + blockDim.x < N) sum += input[i + blockDim.x];
    sdata[tid] = sum;
    __syncthreads();

    // Reduction in shared memory
    for (int s = blockDim.x / 2; s > 0; s /= 2) {
        if (tid < s) {
            sdata[tid] += sdata[tid + s];
        }
        __syncthreads();
    }

    if (tid == 0) output[blockIdx.x] = sdata[0];
}
```

## Histogram

### Atomic Histogram

```cpp
// Atomic histogram
__global__ void histogramAtomic(int* data, int* histogram, int N, int numBins) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        int bin = data[i] % numBins;
        atomicAdd(&histogram[bin], 1);
    }
}

// Shared memory histogram with final reduction
__global__ void histogramShared(int* data, int* histogram, int N, int numBins) {
    __shared__ int privateHist[256];

    int tid = threadIdx.x;
    int i = blockIdx.x * blockDim.x + threadIdx.x;

    // Initialize shared memory
    if (tid < numBins) privateHist[tid] = 0;
    __syncthreads();

    // Local histogram in shared memory
    if (i < N) {
        int bin = data[i] % numBins;
        atomicAdd(&privateHist[bin], 1);
    }
    __syncthreads();

    // Merge to global histogram
    if (tid < numBins) {
        atomicAdd(&histogram[tid], privateHist[tid]);
    }
}
```

## Prefix Sum (Scan)

### Parallel Scan

```cpp
// Work-efficient parallel prefix sum
__global__ void prescan(float* input, float* output, int N) {
    extern __shared__ float temp[];
    int tid = threadIdx.x;
    int offset = 1;

    // Load into shared memory
    if (2 * tid < N) temp[2 * tid] = input[2 * tid];
    if (2 * tid + 1 < N) temp[2 * tid + 1] = input[2 * tid + 1];
    __syncthreads();

    // Build upsweep (reduction)
    for (int d = blockDim.x; d > 0; d /= 2) {
        __syncthreads();
        if (tid < d) {
            int ai = offset * (2 * tid + 1) - 1;
            int bi = offset * (2 * tid + 2) - 1;
            temp[bi] += temp[ai];
        }
        offset *= 2;
    }

    // Clear last element
    if (tid == 0) temp[blockDim.x * 2 - 1] = 0;

    // Downsweep
    for (int d = 1; d < blockDim.x * 2; d *= 2) {
        offset /= 2;
        __syncthreads();
        if (tid < d) {
            int ai = offset * (2 * tid + 1) - 1;
            int bi = offset * (2 * tid + 2) - 1;
            float t = temp[ai];
            temp[ai] = temp[bi];
            temp[bi] += t;
        }
    }
    __syncthreads();

    // Write result
    if (2 * tid < N) output[2 * tid] = temp[2 * tid];
    if (2 * tid + 1 < N) output[2 * tid + 1] = temp[2 * tid + 1];
}
```

## Convolution

### 1D Convolution

```cpp
__global__ void convolution1D(float* input, float* kernel, float* output,
                              int N, int K) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        float sum = 0;
        int kHalf = K / 2;

        for (int j = 0; j < K; j++) {
            int inputIdx = i - kHalf + j;
            if (inputIdx >= 0 && inputIdx < N) {
                sum += input[inputIdx] * kernel[j];
            }
        }
        output[i] = sum;
    }
}

// Shared memory optimized convolution
__global__ void convolution1DShared(float* input, float* kernel, float* output,
                                    int N, int K) {
    __shared__ float inputTile[256 + 32];  // Tile + halo
    __shared__ float kernelTile[32];

    int tid = threadIdx.x;
    int i = blockIdx.x * blockDim.x + tid;
    int kHalf = K / 2;

    // Load input tile
    inputTile[tid + kHalf] = (i < N) ? input[i] : 0;
    if (tid < kHalf) {
        inputTile[tid] = (i - kHalf >= 0) ? input[i - kHalf] : 0;
        inputTile[tid + blockDim.x + kHalf] = (i + blockDim.x < N) ? input[i + blockDim.x] : 0;
    }
    __syncthreads();

    // Load kernel
    if (tid < K) kernelTile[tid] = kernel[tid];

    // Compute convolution
    if (i < N) {
        float sum = 0;
        for (int j = 0; j < K; j++) {
            sum += inputTile[tid + j] * kernelTile[j];
        }
        output[i] = sum;
    }
}
```

## Image Processing

### Grayscale Conversion

```cpp
__global__ void rgbToGrayscale(unsigned char* rgb, unsigned char* gray,
                               int width, int height) {
    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;

    if (x < width && y < height) {
        int rgbIdx = (y * width + x) * 3;
        unsigned char r = rgb[rgbIdx];
        unsigned char g = rgb[rgbIdx + 1];
        unsigned char b = rgb[rgbIdx + 2];

        // Luminance formula
        gray[y * width + x] = (unsigned char)(0.299f * r + 0.587f * g + 0.114f * b);
    }
}

// Apply Gaussian blur
__global__ void gaussianBlur(unsigned char* input, unsigned char* output,
                             int width, int height, float* kernel, int kSize) {
    __shared__ unsigned char tile[18][18];  // 16x16 block + 1 pixel border

    int x = blockIdx.x * blockDim.x + threadIdx.x;
    int y = blockIdx.y * blockDim.y + threadIdx.y;
    int kHalf = kSize / 2;

    // Load tile with halo
    for (int dy = -1; dy <= 1; dy++) {
        for (int dx = -1; dx <= 1; dx++) {
            int tx = threadIdx.x + 1 + dx;
            int ty = threadIdx.y + 1 + dy;
            int gx = x + dx;
            int gy = y + dy;

            if (tx >= 0 && tx < 18 && ty >= 0 && ty < 18) {
                if (gx >= 0 && gx < width && gy >= 0 && gy < height) {
                    tile[ty][tx] = input[gy * width + gx];
                } else {
                    tile[ty][tx] = 0;
                }
            }
        }
    }
    __syncthreads();

    // Apply kernel
    if (x < width && y < height && threadIdx.x >= 1 && threadIdx.x < 17 &&
        threadIdx.y >= 1 && threadIdx.y < 17) {
        float sum = 0;
        for (int j = -kHalf; j <= kHalf; j++) {
            for (int i = -kHalf; i <= kHalf; i++) {
                sum += tile[threadIdx.y + j + 1][threadIdx.x + i + 1] *
                       kernel[(j + kHalf) * kSize + (i + kHalf)];
            }
        }
        output[y * width + x] = (unsigned char)sum;
    }
}
```

## Sort (Bitonic Sort)

```cpp
__global__ void bitonicSort(int* data, int N, int j, int k) {
    unsigned int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i >= N) return;

    unsigned int ixj = i ^ j;

    if (ixj > i) {
        if ((i & k) == 0) {
            // Ascending order
            if (data[i] > data[ixj]) {
                int temp = data[i];
                data[i] = data[ixj];
                data[ixj] = temp;
            }
        } else {
            // Descending order
            if (data[i] < data[ixj]) {
                int temp = data[i];
                data[i] = data[ixj];
                data[ixj] = temp;
            }
        }
    }
}

void bitonicSortWrapper(int* d_data, int N) {
    dim3 block(256);
    dim3 grid((N + block.x - 1) / block.x);

    for (int k = 2; k <= N; k *= 2) {
        for (int j = k / 2; j > 0; j /= 2) {
            bitonicSort<<<grid, block>>>(d_data, N, j, k);
        }
    }
}
```

## Stream Triad (Memory Bandwidth Test)

```cpp
__global__ void streamTriad(float* a, float* b, float* c, float* d,
                            float scalar, int N) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < N) {
        d[i] = a[i] + scalar * b[i] + c[i];
    }
}

void runStreamTriad(int N, int iterations) {
    float *d_a, *d_b, *d_c, *d_d;

    size_t bytes = N * sizeof(float);
    cudaMalloc(&d_a, bytes);
    cudaMalloc(&d_b, bytes);
    cudaMalloc(&d_c, bytes);
    cudaMalloc(&d_d, bytes);

    // Initialize arrays
    // ...

    dim3 block(256);
    dim3 grid((N + block.x - 1) / block.x);

    cudaEvent_t start, stop;
    cudaEventCreate(&start);
    cudaEventCreate(&stop);

    cudaEventRecord(start);
    for (int i = 0; i < iterations; i++) {
        streamTriad<<<grid, block>>>(d_a, d_b, d_c, d_d, 2.0f, N);
    }
    cudaEventRecord(stop);
    cudaEventSynchronize(stop);

    float milliseconds = 0;
    cudaEventElapsedTime(&milliseconds, start, stop);

    double bytesTransferred = (double)N * sizeof(float) * 3 * iterations;
    double bandwidth = bytesTransferred / (milliseconds / 1000.0) / 1e9;

    printf("Stream Triad Bandwidth: %.2f GB/s\n", bandwidth);

    cudaFree(d_a); cudaFree(d_b); cudaFree(d_c); cudaFree(d_d);
}
```