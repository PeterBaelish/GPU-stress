
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <string>
#include <stdlib.h>
#include <cuda_runtime.h>
__global__ void my_kernel(float *data) {
    
    int index = threadIdx.x + (blockIdx.x * blockDim.x * warpSize);
    
    
    float value = data[index];
    
}

int main(int argc, char** argv) {
    // 定义数组大小和步长
    const int array_size = 3 * 1024 * 1024; // 3MB
    const int stride = 128; // 行大小
    size_t size = array_size * sizeof(float);
    // 分配数组
    float *h_a=(float *)malloc(size);
    for (int i = 0; i < array_size; i++) {
        h_a[i] = 123;
    }
    float *d_a = NULL;
    cudaError_t err = cudaSuccess;
    // 分配内存
    err=cudaMalloc((void **)&d_a, size);
    while (err != cudaSuccess){
        err=cudaMalloc((void **)&d_a, size);
    }
     // Copy  主机的数组内容 to the gpu arrays
    err = cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    while (err != cudaSuccess){
        err = cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    }

    // 定义网格和块大小
    int block_size = 256;
    int grid_size = (array_size + (block_size * stride) - 1) / (block_size * stride);

    // 解析命令行参数
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--block-size") == 0) {
            i++;
            block_size = atoi(argv[i]);
        } else if (strcmp(argv[i], "--grid-size") == 0) {
            i++;
            grid_size = atoi(argv[i]);
        }
        
    }

    // 调用CUDA核函数
    while(true){
        my_kernel<<<grid_size, block_size>>>(d_a);
    }
    cudaDeviceSynchronize();

    // 释放数组
    cudaFree(d_a);
    free(h_a);
    return 0;
}