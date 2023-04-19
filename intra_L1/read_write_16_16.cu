
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <string>
#include <stdlib.h>
#include <cuda_runtime.h>

// 全读，128KB array,128B/行，warp
using namespace std;
__global__ void read_write_16_16(int *a, int n) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int val;
    if (tid<n){
        if(tid%2==0){
            val=a[tid];
            val++;
        }else{
            a[tid]++;
        }
        
    }
}

int main(int argc, char** argv) {
    int n = 1024*32;
    size_t size = n * sizeof(int);
    int *h_a = (int *)malloc(size);

    // 初始化输入数据
    for (int i = 0; i < n; i++) {
        h_a[i] = int(i);
    }

    int *d_a = NULL;

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

    // 调用CUDA核函数
    int block_size = 1024; //threads per block
    int grid_size = 28; //(n + block_size - 1) / block_size;


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

    while(true){
        read_write_16_16<<<grid_size, block_size>>>(d_a, n);
    }

    
    // 将计算结果从设备内存复制回主机内存
    cudaMemcpy(h_a, d_a, size, cudaMemcpyDeviceToHost);


    // 释放内存
    cudaFree(d_a);
    free(h_a);
    return 0;
}
            