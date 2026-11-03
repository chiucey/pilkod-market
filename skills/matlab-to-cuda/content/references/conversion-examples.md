# MATLAB to CUDA Conversion Examples

## Example 1: Vector Addition

### MATLAB
```matlab
function C = vectorAdd(A, B)
    C = A + B;
end

% Usage
a = 1:1000;
b = 1000:-1:1;
c = vectorAdd(a, b);
```

### CUDA
```cpp
#include <cuda_runtime.h>

__global__
void vectorAdd(const float* A, const float* B, float* C, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        C[idx] = A[idx] + B[idx];
    }
}

void vectorAddHost(float* h_A, float* h_B, float* h_C, int n) {
    float *d_A, *d_B, *d_C;
    size_t size = n * sizeof(float);

    cudaMalloc(&d_A, size);
    cudaMalloc(&d_B, size);
    cudaMalloc(&d_C, size);

    cudaMemcpy(d_A, h_A, size, cudaMemcpyHostToDevice);
    cudaMemcpy(d_B, h_B, size, cudaMemcpyHostToDevice);

    int blockSize = 256;
    int gridSize = (n + blockSize - 1) / blockSize;
    vectorAdd<<<gridSize, blockSize>>>(d_A, d_B, d_C, n);

    cudaMemcpy(h_C, d_C, size, cudaMemcpyDeviceToHost);

    cudaFree(d_A);
    cudaFree(d_B);
    cudaFree(d_C);
}
```

---

## Example 2: Element-wise Squaring

### MATLAB
```matlab
function Y = squareElements(X)
    Y = X .^ 2;
end
```

### CUDA
```cpp
__global__
void squareElements(const float* X, float* Y, int n) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        Y[idx] = X[idx] * X[idx];
    }
}
```

---

## Example 3: Matrix Transpose

### MATLAB
```matlab
function B = transposeMatrix(A)
    B = A';
end
```

### CUDA (with Shared Memory Optimization)
```cpp
#define TILE_SIZE 16

__global__
void transpose(const float* A, float* B, int rows, int cols) {
    __shared__ float tile[TILE_SIZE][TILE_SIZE];

    int x = blockIdx.x * TILE_SIZE + threadIdx.x;
    int y = blockIdx.y * TILE_SIZE + threadIdx.y;

    if (x < cols && y < rows) {
        tile[threadIdx.y][threadIdx.x] = A[y * cols + x];
    }
    __syncthreads();

    x = blockIdx.y * TILE_SIZE + threadIdx.x;
    y = blockIdx.x * TILE_SIZE + threadIdx.y;

    if (x < rows && y < cols) {
        B[y * rows + x] = tile[threadIdx.x][threadIdx.y];
    }
}
```

---

## Example 4: Histogram Computation

### MATLAB
```matlab
function hist = computeHistogram(data, numBins, minVal, maxVal)
    hist = zeros(1, numBins);
    binWidth = (maxVal - minVal) / numBins;

    for i = 1:length(data)
        binIdx = ceil((data(i) - minVal) / binWidth);
        binIdx = max(1, min(binIdx, numBins));
        hist(binIdx) = hist(binIdx) + 1;
    end
end
```

### CUDA (with Atomic Operations)
```cpp
__global__
void histogram(const float* data, int* hist, int n, int numBins,
               float minVal, float binWidth) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        int binIdx = (int)((data[idx] - minVal) / binWidth);
        binIdx = max(0, min(binIdx, numBins - 1));
        atomicAdd(&hist[binIdx], 1);
    }
}
```

---

## Example 5: 1D Convolution

### MATLAB
```matlab
function y = conv1d(x, kernel)
    n = length(x);
    k = length(kernel);
    y = zeros(1, n);

    for i = 1:n
        for j = 1:k
            if i - j + 1 > 0
                y(i) = y(i) + x(i - j + 1) * kernel(j);
            end
        end
    end
end
```

### CUDA
```cpp
__global__
void conv1d(const float* x, const float* kernel, float* y,
            int n, int k) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        float sum = 0.0f;
        int kHalf = k / 2;

        for (int j = 0; j < k; ++j) {
            int xIdx = idx - kHalf + j;
            if (xIdx >= 0 && xIdx < n) {
                sum += x[xIdx] * kernel[j];
            }
        }
        y[idx] = sum;
    }
}
```

---

## Example 6: Euclidean Distance Matrix

### MATLAB
```matlab
function D = euclideanDistance(A, B)
    [m, ~] = size(A);
    [n, ~] = size(B);
    D = zeros(m, n);

    for i = 1:m
        for j = 1:n
            D(i,j) = sqrt(sum((A(i,:) - B(j,:)).^2));
        end
    end
end
```

### CUDA
```cpp
__global__
void euclideanDistance(const float* A, const float* B, float* D,
                       int m, int n, int dim) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < m && col < n) {
        float sum = 0.0f;
        for (int d = 0; d < dim; ++d) {
            float diff = A[row * dim + d] - B[col * dim + d];
            sum += diff * diff;
        }
        D[row * n + col] = sqrtf(sum);
    }
}
```

---

## Example 7: Max Pooling (2D)

### MATLAB
```matlab
function output = maxPooling(input, poolSize)
    [h, w, c] = size(input);
    outH = floor(h / poolSize);
    outW = floor(w / poolSize);
    output = zeros(outH, outW, c);

    for ch = 1:c
        for i = 1:outH
            for j = 1:outW
                pool = input((i-1)*poolSize+1:i*poolSize, ...
                             (j-1)*poolSize+1:j*poolSize, ch);
                output(i, j, ch) = max(pool(:));
            end
        end
    end
end
```

### CUDA
```cpp
#define POOL_SIZE 2

__global__
void maxPooling(const float* input, float* output,
                int inHeight, int inWidth, int channels,
                int outHeight, int outWidth) {
    int outRow = blockIdx.y * blockDim.y + threadIdx.y;
    int outCol = blockIdx.x * blockDim.x + threadIdx.x;
    int ch = blockIdx.z;

    if (outRow < outHeight && outCol < outWidth && ch < channels) {
        int inRow = outRow * POOL_SIZE;
        int inCol = outCol * POOL_SIZE;

        float maxVal = -INFINITY;
        for (int i = 0; i < POOL_SIZE; ++i) {
            for (int j = 0; j < POOL_SIZE; ++j) {
                int idx = (inRow + i) * inWidth + (inCol + j);
                maxVal = fmaxf(maxVal, input[idx * channels + ch]);
            }
        }
        output[(outRow * outWidth + outCol) * channels + ch] = maxVal;
    }
}
```

---

## Example 8: Softmax Function

### MATLAB
```matlab
function y = softmax(x)
    x = x - max(x);  % Numerical stability
    y = exp(x);
    y = y / sum(y);
end
```

### CUDA
```cpp
__global__
void softmaxKernel(const float* input, float* output, int n) {
    extern __shared__ float sdata[];

    int tid = threadIdx.x;
    int idx = blockIdx.x;

    // Find max (parallel reduction)
    sdata[tid] = input[idx * n + tid];
    __syncthreads();

    for (int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (tid < s) {
            sdata[tid] = fmaxf(sdata[tid], sdata[tid + s]);
        }
        __syncthreads();
    }

    float maxVal = sdata[0];

    // Compute sum of exponentials
    sdata[tid] = expf(input[idx * n + tid] - maxVal);
    __syncthreads();

    for (int s = blockDim.x / 2; s > 0; s >>= 1) {
        if (tid < s) {
            sdata[tid] += sdata[tid + s];
        }
        __syncthreads();
    }

    float sum = sdata[0];
    output[idx * n + tid] = expf(input[idx * n + tid] - maxVal) / sum;
}
```

---

## Example 9: Batch Normalization

### MATLAB
```matlab
function y = batchNorm(x, gamma, beta, epsilon)
    mu = mean(x);
    sigma2 = var(x);
    x_norm = (x - mu) / sqrt(sigma2 + epsilon);
    y = gamma * x_norm + beta;
end
```

### CUDA
```cpp
__global__
void batchNormKernel(const float* x, float* y,
                      const float* gamma, const float* beta,
                      int n, int channels, float epsilon) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n * channels) {
        int ch = idx / n;
        int i = idx % n;

        // Simplified single-sample normalization
        float mean = 0.0f;
        for (int j = 0; j < n; ++j) {
            mean += x[ch * n + j];
        }
        mean /= n;

        float var = 0.0f;
        for (int j = 0; j < n; ++j) {
            float diff = x[ch * n + j] - mean;
            var += diff * diff;
        }
        var /= n;

        float x_norm = (x[idx] - mean) / sqrtf(var + epsilon);
        y[idx] = gamma[ch] * x_norm + beta[ch];
    }
}
```

---

## Example 10: Dropout

### MATLAB
```matlab
function [y, mask] = dropout(x, probability)
    mask = rand(size(x)) > probability;
    y = x .* mask / (1 - probability);
end
```

### CUDA
```cpp
__global__
void dropoutKernel(const float* x, float* y, unsigned int* mask,
                    int n, float probability, float scale, unsigned int seed) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < n) {
        // Simple hash-based random (for demonstration)
        unsigned int random = hash(idx ^ seed);
        bool keep = (random % 1000) > (probability * 1000);
        y[idx] = keep ? x[idx] * scale : 0.0f;
        mask[idx] = keep ? 1 : 0;
    }
}

unsigned int hash(unsigned int x) {
    x = ((x >> 16) ^ x) * 0x45d9f3b;
    x = ((x >> 16) ^ x) * 0x45d9f3b;
    return x;
}
```
