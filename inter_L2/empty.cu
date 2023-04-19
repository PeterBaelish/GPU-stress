#include <stdio.h>
#include <cuda_runtime.h>
#include <limits>
#include <stdint.h>

#define NUM_BLOCKS 28
#define THREADS_PER_BLOCK 1024
#define MAX 0xFFFFFFFFFFFFFFF
__global__ void myKernel() {
    if (threadIdx.x == 0) {
    }
    __syncthreads();
}

int main() {
    // int i=0;
    while (true){
        myKernel<<<NUM_BLOCKS, THREADS_PER_BLOCK>>>();
        // printf("%d",i++);
        cudaDeviceSynchronize();
    }
    return 0;
}
