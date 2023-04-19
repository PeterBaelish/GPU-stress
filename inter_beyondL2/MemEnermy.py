import jinja2
import numpy as np
from numba import cuda

# Define the CUDA code template
cuda_template = """
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
    for (int j = tid; j < {{ cache_size }}; j += blockDim.x) {
        cache[j] = data[i + j];
    }

    __syncthreads();

    // Process data
    for (int j = tid; j < {{ cache_size }}; j += blockDim.x) {
        cache[j] += 1.0f;
    }

    __syncthreads();

    // Write data back to global memory
    for (int j = tid; j < {{ cache_size }}; j += blockDim.x) {
        data[i + j] = cache[j];
    }
}

int main() {
    // Allocate device memory
    float* d_data;
    cudaMalloc((void**)&d_data, {{ data_size }} * sizeof(float));

    // Initialize data on host
    float* h_data = (float*)malloc({{ data_size }} * sizeof(float));
    for (int i = 0; i < {{ data_size }}; i++) {
        h_data[i] = i;
    }

    // Copy data to device
    cudaMemcpy(d_data, h_data, {{ data_size }} * sizeof(float), cudaMemcpyHostToDevice);

    // Launch kernel
    int block_size = 256;
    int num_blocks = {{ data_size // cache_size }};
    int shared_mem_size = {{ cache_size }} * sizeof(float);
    while(true){
        kernel<<<num_blocks, block_size, shared_mem_size>>>(d_data);
    }

    // Copy result back to host
    cudaMemcpy(h_data, d_data, {{ data_size }} * sizeof(float), cudaMemcpyDeviceToHost);

    // Verify result
    for (int i = 0; i < {{ data_size }}; i++) {
        if (h_data[i] != i + 1.0f) {
            printf("Error: h_data[%d] = %f, expected %f\\n", i, h_data[i], i + 1.0f);
            break;
        }
    }

    // Free memory
    cudaFree(d_data);
    free(h_data);

    return 0;
}
"""

# Define array sizes as multiples of 3MB
array_sizes = [3, 6, 12, 18, 24]
cache_size = 3 * 1024 * 1024

# Render the CUDA code template for each array size
for size in array_sizes:
    data_size = size * cache_size
    template = jinja2.Template(cuda_template)
    rendered_code = template.render(cache_size=cache_size, data_size=data_size)

    # Write the rendered code to a file
    with open(f"kernel_{size}.cu", "w") as f:
        f.write(rendered_code)

    # # Compile the CUDA code
    # cuda.compile_and_load(rendered_code, f"kernel_{size}.ptx")

    # # Run the generated kernel function on the GPU
    # kernel_func = cuda.jit("void(float[:])")(cuda.driver.module_from_file(f"kernel_{size}.ptx").get_function("kernel"))
   
