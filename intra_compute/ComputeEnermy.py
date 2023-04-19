import os

# 存储不同数据类型和位宽的对应关系
# 数据类型和位宽的组合
data_types = [("int", "16_t"), ("int", "32_t"), ("int", "64_t"), ("float", ""), ("double", "")]

# 计算类型
calc_types = ["add", "mult"]
for data_type, bits in data_types:
    for calc_type in calc_types:
            # 生成CUDA核函数名称
            cuda_kernel_name = f"{data_type}{bits}_{calc_type}"
            # 生成CUDA核函数代码
            cuda_code = f"""
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <string>
#include <stdlib.h>
#include <cuda_runtime.h>

using namespace std;
__global__ void {cuda_kernel_name}({data_type}{bits} *a, {data_type}{bits} *b, {data_type}{bits} *c, int n) {{
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    // int smID;
    // 获取当前线程所在的SM ID
    // asm("mov.u32 %0, %smid;" : "=r"(smID));
    // printf("Thread %d is running on SM %d\\n", threadIdx.x, smID);
    if (i < n) {{
        c[i] = a[i] {'+' if calc_type == 'add' else '*'} b[i];
    }}
}}

int main(int argc, char** argv) {{
    int n = 1024;
    size_t size = n * sizeof({data_type}{bits});
    {data_type}{bits} *h_a = ({data_type}{bits} *)malloc(size);
    {data_type}{bits} *h_b = ({data_type}{bits} *)malloc(size);
    {data_type}{bits} *h_c = ({data_type}{bits} *)malloc(size);

    // 初始化输入数据
    for (int i = 0; i < n; i++) {{
        h_a[i] = {data_type}{bits}(i);
        h_b[i] = {data_type}{bits}(2 * i);
    }}

    {data_type}{bits} *d_a = NULL;
    {data_type}{bits} *d_b = NULL;
    {data_type}{bits} *d_c = NULL;

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
#     __global__ void {data_type}_{bits}_{calc_type}_{precision}(const {data_type}{bits}* a, const {data_type}{bits}* b, {data_type}{bits}* c, int size) {{
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
#             __global__ void {cuda_kernel_name}({data_type}{bits} *a, {data_type}{bits} *b, {data_type}{bits} *c, int n) {{
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
