from jinja2 import Template
# printf("Thread %d: value=%f\\n", index, value);
# 定义模板
template = Template('''
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <string>
#include <stdlib.h>
#include <cuda_runtime.h>
__global__ void my_kernel(float *data) {
    {% if access_mode == 'per_thread' %}
    int index = threadIdx.x + blockIdx.x * blockDim.x;
    {% else %}
    int index = threadIdx.x + (blockIdx.x * blockDim.x * warpSize);
    {% endif %}
    {% if operation == 'read' %}
    float value = data[index];
    {% else %}
    data[index] = index;
    {% endif %}
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
''')

# 定义访问模式和操作类型列表
access_modes = ['per_thread', 'per_warp']
operations = ['read', 'write']

# 遍历所有组合
for access_mode in access_modes:
    for operation in operations:
        # 定义参数
        parameters = {
            'access_mode': access_mode,
            'operation': operation
        }

        # 生成CUDA代码
        generated_code = template.render(parameters)
        cuda_kernel_name = f"{access_mode}_{operation}"
        # 输出生成的代码
        # print(generated_code)
        # 保存CUDA代码到文件
        file_name = f"{cuda_kernel_name}.cu"
        with open(file_name, "w") as f:
            f.write(generated_code)

# import os
# from numba import cuda
# def generate_cuda_template(array_size, stride_length, per_thread_access, memory_access_operation):
#     stride=stride_length
#     template = f"""
# #include <stdio.h>
# #include <cuda_runtime.h>
# __global__ void kernel(float *data) {{
#     int tid = blockIdx.x * blockDim.x + threadIdx.x;
#     int num_threads = gridDim.x * blockDim.x;
#     int stride = {stride_length};
#     int num_iterations = {array_size // (stride * num_threads)};
#     {'float val;' if memory_access_operation == 'write' else ''}
#     for (int i = 0; i < {{"{num_iterations}"}}; i++) {{
#         {'val = data[tid * stride];' if per_thread_access == 'thread' else ''}
#         {'__syncthreads();' if per_thread_access == 'warp' else ''}
#         {'data[tid * stride] = val;' if memory_access_operation == 'write' else ''}
#     }}
# }}
# """

# #     template = f"""
# # #include <stdio.h>
# # #include <cuda_runtime.h>
# # __global__ void kernel(float *data) {{
# #     int tid = blockIdx.x * blockDim.x + threadIdx.x;
# #     int num_threads = gridDim.x * blockDim.x;
# #     int stride = {stride_length};
# #     int num_iterations = {array_size // (stride * num_threads)};
# #     {'float val;' if memory_access_operation == 'write' else ''}
# #     for (int i = 0; i < {num_iterations}; i++) {{
# #         {'val = data[tid * stride];' if per_thread_access == 'thread' else ''}
# #         {'__syncthreads();' if per_thread_access == 'warp' else ''}
# #         {'data[tid * stride] = val;' if memory_access_operation == 'write' else ''}
# #     }}
# # }}

# #     """
#     return template

# def write_cuda_file(array_size, stride_length, per_thread_access, memory_access_operation):
#     file_name = f"cuda_{array_size}_{stride_length}_{per_thread_access}_{memory_access_operation}.cu"
#     with open(file_name, "w") as f:
        
#         f.write(generate_cuda_template(array_size, stride_length, per_thread_access, memory_access_operation))
#         f.write("int main() {\n")
#         f.write("    const int N = 1024;\n")
#         f.write(f"   float *a;\n")
#         f.write("    cudaMalloc((void**)&a, N * sizeof(float));\n")
#         f.write("    for (int i = 0; i < N; i++) {\n")
#         f.write("        a[i] = i;\n")
#         f.write("    }\n")
#         f.write("    dim3 block(256);\n")
#         f.write("    dim3 grid((N + block.x - 1) / block.x);\n")
#         f.write("    kernel<<<grid, block>>>(a);\n")
#         f.write(f"    float result[N];\n")
#         f.write("    cudaMemcpyAsync(result, a, N * sizeof(float), cudaMemcpyDeviceToHost);\n")
#         f.write("    for (int i = 0; i < N; i++) {\n")
#         f.write("        printf(\"%f\\n\", result[i]);\n")
#         f.write("    }\n")
#         f.write("    cudaFree(a);\n")
#         f.write("    return 0;\n")
#         f.write("}\n")
#     print(f"Generated CUDA file: {file_name}")

# # Example usage
# #array_sizes = [960 * 1024, 1 * 1024 * 1024, 4 * 1024 * 1024, 16 * 1024 * 1024]
# array_sizes = [32 * 1024]
# stride_lengths = [8, 16, 32, 64, 128]
# per_thread_access_options = ['thread', 'warp']
# memory_access_operation_options = ['read', 'write']

# for array_size in array_sizes:
#     for stride_length in stride_lengths:
#         for per_thread_access in per_thread_access_options:
#             for memory_access_operation in memory_access_operation_options:
#                 write_cuda_file(array_size, stride_length, per_thread_access, memory_access_operation)

# 
#include <cuda_runtime.h>
#include <stdio.h>

# #define ARRAY_SIZE (1024 * 1024) // 默认数组大小为1MB
# #define STRIDE (32) // 默认步长为32 bytes

# // 定义访问模式
# #define ACCESS_PER_THREAD // 每个线程访问
# //#define ACCESS_PER_WARP

# // 定义内存访问操作
# #define MEMORY_READ // 读取操作
# //#define MEMORY_WRITE

# __global__ void enemy_kernel(char *d_array, int stride, int access_mode) {
#     int tid = blockIdx.x * blockDim.x + threadIdx.x;
#     int idx;
#     char temp;
#     if (access_mode == 0) { // 每个线程访问
#         for (int i = tid; i < ARRAY_SIZE / stride; i += blockDim.x * gridDim.x) {
#             idx = i * stride;
#             temp = d_array[idx];
#         }
#     } else { // 每个warp访问
#         int warp_id = tid / warpSize;
#         int lane_id = tid % warpSize;
#         for (int i = warp_id; i < ARRAY_SIZE / stride / warpSize; i += blockDim.x * gridDim.x / warpSize) {
#             idx = i * stride * warpSize + lane_id * stride;
#             temp = d_array[idx];
#         }
#     }
# }

# int main() {
#     char *d_array;
#     cudaMalloc(&d_array, ARRAY_SIZE * sizeof(char));
#     cudaMemset(d_array, 0, ARRAY_SIZE * sizeof(char));

#     enemy_kernel<<<dim3(128), dim3(128)>>>(d_array, STRIDE, (ACCESS_PER_THREAD ? 0 : 1));
#     cudaDeviceSynchronize();

#     cudaFree(d_array);
#     return 0;
# }


# import os

# # 设置参数范围
# array_sizes = [960*1024, 1024*1024, 4096*1024, 8192*1024, 16384*1024]
# stride_lengths = [8, 16, 32, 64, 128]
# access_types = ['read', 'write']
# access_patterns = ['per-thread', 'per-warp']

# # 生成CUDA代码模板
# cuda_template = """
# __global__ void kernel(int *data) {
#     int tid = threadIdx.x + blockIdx.x * blockDim.x;
#     int stride = {stride};
#     int n = {size} / sizeof(int);
#     {access} {
#         for (int i = tid; i < n; i += blockDim.x * gridDim.x * stride) {
#             int index = i * stride;
#             {operation};
#         }
#     }
# }
# """

# # 生成CUDA文件
# for size in array_sizes:
#     for stride in stride_lengths:
#         for access in access_patterns:
#             for operation in access_types:
#                 # 设置文件名
#                 filename = f"kernel_{size}_{stride}_{access}_{operation}.cu"
#                 # 生成CUDA代码
#                 cuda_code = cuda_template.format(size=size, stride=stride, access=f"if ({access}())", operation=f"data[index] = {operation}(data[index]);")
#                 # 写入文件
#                 with open(filename, "w") as f:
#                     f.write(cuda_code)
#                 print(f"{filename} generated.")


# import argparse


# # python generate_cuda_code.py --size_min 960000 --size_max 16000000 --stride_min 8 --stride_max 128 --output_dir ./cuda_code
# #
# def generate_cuda_code(size_min, size_max, stride_min, stride_max, output_dir):
#     access_types = ['read', 'write']
#     access_patterns = ['per-thread', 'per-warp']

#     # Generate CUDA code for different sizes, strides, access types, and access patterns
#     for size in range(size_min, size_max+1, size_min):
#         for stride in range(stride_min, stride_max+1, stride_min):
#             for access_type in access_types:
#                 for access_pattern in access_patterns:
#                     # Generate CUDA code here
#                     cuda_code = f"""
#                     __global__ void kernel() {{
#                         int idx = blockIdx.x * blockDim.x + threadIdx.x;
#                         int stride_idx = idx * {stride};
#                         {access_type} data = i[stride_idx];
#                         {access_pattern}_syncthreads();
#                         i[stride_idx] = data;
#                     }}
#                     """

#                     # Write the generated code to a file
#                     file_name = f"{output_dir}/cuda_code_{size}_{stride}_{access_type}_{access_pattern}.cu"
#                     with open(file_name, 'w') as f:
#                         f.write(cuda_code)

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Generate CUDA code')
#     parser.add_argument('--size_min', type=int, default=960000, help='minimum size of the array')
#     parser.add_argument('--size_max', type=int, default=16000000, help='maximum size of the array')
#     parser.add_argument('--stride_min', type=int, default=8, help='minimum stride length')
#     parser.add_argument('--stride_max', type=int, default=128, help='maximum stride length')
#     parser.add_argument('--output_dir', type=str, default='./', help='output directory')
#     args = parser.parse_args()

# generate_cuda_code(args.size_min, args.size_max, args.stride_min, args.stride_max, args.output_dir)
