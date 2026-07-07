#pragma once
#include <vector>
#include <cstdint> 
#include "parser.hpp"

// Forward declaration of the wrapper function
void run_cuda_risk_checks(const std::vector<RawOrder>& host_orders, std::vector<uint8_t>& host_results);