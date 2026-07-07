#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <chrono>
#include "parser.hpp"
#include "engine.hpp"
#include "risk_engine.hpp" 

namespace py = pybind11;

std::vector<RawOrder> parse_python_bytes(py::bytes python_bytes) {
    std::string str_bytes = python_bytes;
    const uint8_t* buffer = reinterpret_cast<const uint8_t*>(str_bytes.data());
    size_t length = str_bytes.size();

    std::vector<RawOrder> orders;
    SIMDParser::parse_buffer(buffer, length, orders);
    
    return orders;
}

std::vector<bool> execute_gpu_risk_checks(const std::vector<RawOrder>& orders) {
    std::vector<uint8_t> raw_results;
    run_cuda_risk_checks(orders, raw_results);
    std::vector<bool> results(raw_results.begin(), raw_results.end());
    return results;
}

// Hardware Benchmarking Loop
std::vector<double> benchmark_engine(OrderBook& engine, const std::vector<RawOrder>& orders) {
    std::vector<double> latencies;
    latencies.reserve(orders.size());
    
    for (const auto& order : orders) {
        // Start the nanosecond clock
        auto start = std::chrono::high_resolution_clock::now();
        
        engine.process_order(order);
        
        // Stop the clock and record the duration
        auto end = std::chrono::high_resolution_clock::now();
        latencies.push_back(std::chrono::duration<double, std::nano>(end - start).count());
    }
    
    // Blast the array of latencies back to Python
    return latencies; 
}

PYBIND11_MODULE(apex_lob, m) {
    py::class_<RawOrder>(m, "RawOrder")
        .def_readonly("order_id", &RawOrder::order_id)
        .def_readonly("price", &RawOrder::price)
        .def_readonly("quantity", &RawOrder::quantity)
        .def_readonly("side", &RawOrder::side);

    py::class_<OrderBook>(m, "OrderBook")
        .def(py::init<>())
        .def("process_order", &OrderBook::process_order)
        .def("get_total_bids", &OrderBook::get_total_bids)
        .def("get_total_asks", &OrderBook::get_total_asks)
        .def("get_total_trades", &OrderBook::get_total_trades)
        .def("get_volume_executed", &OrderBook::get_volume_executed)
        .def("get_best_bid", &OrderBook::get_best_bid)
        .def("get_best_ask", &OrderBook::get_best_ask);

    m.def("parse_bytes", &parse_python_bytes, "Parse a raw binary stream using AVX-512");
    m.def("gpu_risk_check", &execute_gpu_risk_checks, "Run pre-trade risk checks on the RTX 3090");
    
    m.def("benchmark_engine", &benchmark_engine, "Measure per-order nanosecond latency");
}