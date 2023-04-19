import os

# 比例
# proportions = ["32:0", "24:8","16:16","8:24","0:32"]
proportions = ["1:0", "2:1","1:1","1:2","0:1"]
# memory access
memory_access_operations=["read", "write"]

for proportion in proportions:
    for memory_access_operation in memory_access_operations:
            # 生成CUDA核函数名称
            cuda_kernel_name = f"{proportion}_{memory_access_operation}"
            # 生成CUDA核函数代码
            cuda_code = f"""
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <string>
#include <stdlib.h>
#include <cuda_runtime.h>

using namespace std;
__global__ void {cuda_kernel_name}(int *data) {{
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    int num_threads = gridDim.x * blockDim.x;

    
    int stride = {stride_length};
    {'int val=22;' if memory_access_operation == 'write' else ''}
    for (int i = 0; i < {{"{num_iterations}"}}; i++) {{
        {'data[tid * stride] = val;' if memory_access_operation == 'write' else ''}
    }}
}}

int main(int argc, char** argv) {{
    int n = 1024*32;
    size_t size = n * sizeof(int);
    int *h_a = (int *)malloc(size);
    int *h_b = (int *)malloc(size);
    int *h_c = (int *)malloc(size);

    // 初始化输入数据
    for (int i = 0; i < n; i++) {{
        h_a[i] = int(i);
        h_b[i] = int(2 * i);
    }}

    int *d_a = NULL;
    int *d_b = NULL;
    int *d_c = NULL;

    cudaError_t err = cudaSuccess;
    // 分配内存
    err=cudaMalloc((void **)&d_a, size);
    if (err != cudaSuccess){{
        err=cudaMalloc((void **)&d_a, size);
    }}
    err=cudaMalloc((void **)&d_b, size);
    if(err != cudaSuccess){{
        err=cudaMalloc((void **)&d_b, size);
    }}
    err=cudaMalloc((void **)&d_c, size);
    if (err != cudaSuccess){{
        err=cudaMalloc((void **)&d_c, size);
    }}


    // Copy  主机的数组内容 to the gpu arrays
    err = cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    if (err != cudaSuccess){{
        err = cudaMemcpy(d_a, h_a, size, cudaMemcpyHostToDevice);
    }}

    err = cudaMemcpy(d_b, h_b, size, cudaMemcpyHostToDevice);
    if (err != cudaSuccess){{
        err = cudaMemcpy(d_b, h_b, size, cudaMemcpyHostToDevice);
    }}

    // 调用CUDA核函数
    int block_size = 32; //256
    int grid_size = 28; //(n + block_size - 1) / block_size;


    // 解析命令行参数
    for (int i = 1; i < argc; i++) {{
        if (strcmp(argv[i], "--block-size") == 0) {{
            i++;
            block_size = atoi(argv[i]);
        }} else if (strcmp(argv[i], "--grid-size") == 0) {{
            i++;
            grid_size = atoi(argv[i]);
        }}
        
    }}

    while(true){{
        {cuda_kernel_name}<<<grid_size, block_size>>>(d_a, d_b, d_c, n);
    }}

    
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
}}
            """

            # 保存CUDA代码到文件
            file_name = f"{cuda_kernel_name}.cu"
            with open(file_name, "w") as f:
                f.write(cuda_code)

# import os

# data_types = ["int", "float"]
# bitss = [16, 32, 64]
# calc_types = ["add", "mult"]

# def generate_cuda_code(data_type, bits, calc_type):
#     # 根据数据类型和位宽选择变量类型和精度
#     if data_type == "int":
#         if bits == 16:
#             var_type = "short"
#             precision = "h"
#         elif bits == 32:
#             var_type = "int"
#             precision = ""
#         elif bits == 64:
#             var_type = "long long"
#             precision = "ll"
#     elif data_type == "float":
#         if bits == 16:
#             var_type = "half"
#             precision = ""
#         elif bits == 32:
#             var_type = "float"
#             precision = "f"
#         elif bits == 64:
#             var_type = "double"
#             precision = ""

#     # 根据计算类型生成不同的计算表达式
#     if calc_type == "add":
#         calc_expr = "a + b"
#     elif calc_type == "mult":
#         calc_expr = "a * b"

#     # 生成CUDA核函数代码
#     cuda_code = f"""
#     __global__ void {data_type}_{bits}_{calc_type}_{precision}(const int* a, const int* b, int* c, int size) {{
#         int tid = blockIdx.x * blockDim.x + threadIdx.x;
#         if (tid < size) {{
#             c[tid] = {calc_expr};
#         }}
#     }}
#     """

#     return cuda_code


# for data_type in data_types:
#     for bits in bitss:
#         for calc_type in calc_types:
#             # 生成CUDA核函数名称
#             cuda_kernel_name = f"{data_type}_{bits}_{calc_type}"

#             # 生成CUDA核函数代码
#             cuda_code = f"""
#             __global__ void {cuda_kernel_name}(int *a, int *b, int *c, int n) {{
#                 int i = blockIdx.x * blockDim.x + threadIdx.x;
#                 if (i < n) {{
#                     c[i] = a[i] {'+' if calc_type == 'add' else '*'} b[i];
#                 }}
#             }}
#             """

#             # 保存CUDA代码到文件
#             file_name = f"{cuda_kernel_name}.cu"
#             with open(file_name, "w") as f:
#                 f.write(cuda_code)
