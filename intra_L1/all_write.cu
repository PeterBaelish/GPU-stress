
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <string>
#include <stdlib.h>
#include <cuda_runtime.h>
#include <time.h>  

// 全读，128KB array,128B/行，warp
using namespace std;
__global__ void all_write(int *a, int n) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid<n){
        // printf("%d\n",a[tid]);
        a[tid]--;
        // printf("%d\n",a[tid]);
    }
}



int main(int argc, char** argv) {
    int n = 1024*32;
    size_t size = n * sizeof(int);
    int *h_a = (int *)malloc(size);
    // printf("分配h_a内存\n");
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
    // printf("分配d_a内存\n");
    // Copy  主机的数组内容 to the gpu arrays
    err = cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    while (err != cudaSuccess){
        err = cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    }

    // 调用CUDA核函数
    int block_size = 1024; //threads per block
    int grid_size = 28; //(n + block_size - 1) / block_size;

    // printf("解析命令行参数\n");
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
    // printf("开始all_write\n");

    while(true){
        all_write<<<grid_size, block_size>>>(d_a, n);
    }


    // 将计算结果从设备内存复制回主机内存
    cudaMemcpy(h_a, d_a, size, cudaMemcpyDeviceToHost);


    // 释放内存
    cudaFree(d_a);
    free(h_a);
    return 0;
}
            