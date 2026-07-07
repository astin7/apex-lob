#include <cuda_runtime.h>
#include <iostream>
#include <vector>
#include <cstdint>
#include "parser.hpp"

__global__ void risk_check_kernel(const RawOrder* orders, uint8_t* results, int num_orders) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (i < num_orders) {
        uint8_t is_valid = 1; // 1 = True, 0 = False
        
        if (orders[i].quantity > 10000) {
            is_valid = 0;
        }
        
        if (orders[i].price < 10000 || orders[i].price > 20000) {
            is_valid = 0;
        }

        results[i] = is_valid;
    }
}

void run_cuda_risk_checks(const std::vector<RawOrder>& host_orders, std::vector<uint8_t>& host_results) {
    int num_orders = host_orders.size();
    size_t orders_bytes = num_orders * sizeof(RawOrder);
    size_t results_bytes = num_orders * sizeof(uint8_t);
    
    host_results.resize(num_orders);

    RawOrder* device_orders;
    uint8_t* device_results;
    cudaMalloc(&device_orders, orders_bytes);
    cudaMalloc(&device_results, results_bytes);

    cudaMemcpy(device_orders, host_orders.data(), orders_bytes, cudaMemcpyHostToDevice);

    int threads_per_block = 256;
    int blocks_per_grid = (num_orders + threads_per_block - 1) / threads_per_block;

    risk_check_kernel<<<blocks_per_grid, threads_per_block>>>(device_orders, device_results, num_orders);
    cudaDeviceSynchronize();

    cudaMemcpy(host_results.data(), device_results, results_bytes, cudaMemcpyDeviceToHost);

    cudaFree(device_orders);
    cudaFree(device_results);
}