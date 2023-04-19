
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <string>
#include <stdlib.h>
#include <cuda_runtime.h>

using namespace std;
__global__ void double_add(double *a, double *b, double *c, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    // int smID;
    // 获取当前线程所在的SM ID
    // asm("mov.u32 %0, %smid;" : "=r"(smID));
    // printf("Thread %d is running on SM %d\n", threadIdx.x, smID);
    if (i < n) {
        c[i] = a[i] + b[i];
    }
}

int main(int argc, char** argv) {
    int n = 1024;
    size_t size = n * sizeof(double);
    double *h_a = (double *)malloc(size);
    double *h_b = (double *)malloc(size);
    double *h_c = (double *)malloc(size);

    // 初始化输入数据
    for (int i = 0; i < n; i++) {
        h_a[i] = double(i);
        h_b[i] = double(2 * i);
    }

    double *d_a = NULL;
    double *d_b = NULL;
    double *d_c = NULL;

    cudaError_t err = cudaSuccess;
    // 分配内存
    err=cudaMalloc((void **)&d_a, size);
    if (err != cudaSuccess){
        err=cudaMalloc((void **)&d_a, size);
    }
    err=cudaMalloc((void **)&d_b, size);
    if(err != cudaSuccess){
        err=cudaMalloc((void **)&d_b, size);
    }
    err=cudaMalloc((void **)&d_c, size);
    if (err != cudaSuccess){
        err=cudaMalloc((void **)&d_c, size);
    }


    // Copy  主机的数组内容 to the gpu arrays
    err = cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    if (err != cudaSuccess){
        err = cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    }

    err = cudaMemcpy(d_b, h_b, size, cudaMemcpyHostToDevice);
    if (err != cudaSuccess){
        err = cudaMemcpy(d_b, h_b, size, cudaMemcpyHostToDevice);
    }

    // 调用CUDA核函数
    int block_size = 32; //256
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
        double_add<<<grid_size, block_size>>>(d_a, d_b, d_c, n);
    }

    
    // 将计算结果从设备内存复制回主机内存
    cudaMemcpy(h_c, d_c, size, cudaMemcpyDeviceToHost);


    // 释放内存
    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);
    free(h_a);
    free(h_b);
    free(h_c);
    return 0;
}
            