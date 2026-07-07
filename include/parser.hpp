#pragma once
#include <immintrin.h>
#include <vector>
#include <cstdint>

struct alignas(32) RawOrder {
    uint64_t order_id;     
    uint32_t price;        
    uint32_t quantity;     
    char side;             
    char padding[15];      
};

class SIMDParser {
public:
    static void parse_buffer(const uint8_t* buffer, size_t num_bytes, std::vector<RawOrder>& out_orders) {
        size_t chunks = num_bytes / 64;
        out_orders.reserve(out_orders.size() + (chunks * 2));

        for (size_t i = 0; i < chunks; ++i) {
            __m512i data_chunk = _mm512_loadu_si512(reinterpret_cast<const void*>(buffer + (i * 64)));
            const RawOrder* orders = reinterpret_cast<const RawOrder*>(&data_chunk);
            out_orders.push_back(orders[0]);
            out_orders.push_back(orders[1]);
        }
    }
};