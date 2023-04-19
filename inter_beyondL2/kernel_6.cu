
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <string>
#include <stdlib.h>
#include <cuda_runtime.h>
__global__ void kernel(float* data) {
    extern __shared__ float cache[];

    int tid = threadIdx.x;
    int bid = blockIdx.x;
    int i = bid * blockDim.x + tid;

    // Load data into shared memory
    for (int j = tid; j < 3145728; j += blockDim.x) {
        cache[j] = data[i + j];
    }

    __syncthreads();

    // Process data
    for (int j = tid; j < 3145728; j += blockDim.x) {
        cache[j] += 1.0f;
    }

    __syncthreads();

    // Write data back to global memory
    for (int j = tid; j < 3145728; j += blockDim.x) {
        data[i + j] = cache[j];
    }
}

int main() {
    // Allocate device memory
    float* d_data;
    cudaMalloc((void**)&d_data, 18874368 * sizeof(float));

    // Initialize data on host
    float* h_data = (float*)malloc(18874368 * sizeof(float));
    for (int i = 0; i < 18874368; i++) {
        h_data[i] = i;
    }

    // Copy data to device
    cudaMemcpy(d_data, h_data, 18874368 * sizeof(float), cudaMemcpyHostToDevice);

    // Launch kernel
    int block_size = 256;
    int num_blocks = 6;
    int shared_mem_size = 3145728 * sizeof(float);
    while(true){
        kernel<<<num_blocks, block_size, shared_mem_size>>>(d_data);
    }

    // Copy result back to host
    cudaMemcpy(h_data, d_data, 18874368 * sizeof(float), cudaMemcpyDeviceToHost);

    // Verify result
    for (int i = 0; i < 18874368; i++) {
        if (h_data[i] != i + 1.0f) {
            printf("Error: h_data[%d] = %f, expected %f\n", i, h_data[i], i + 1.0f);
            break;
        }
    }

    // Free memory
    cudaFree(d_data);
    free(h_data);

    return 0;
}