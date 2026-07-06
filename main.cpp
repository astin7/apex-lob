#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "parser.hpp"
#include "engine.hpp"

namespace py = pybind11;

std::vector<RawOrder> parse_python_bytes(py::bytes python_bytes) {
    std::string str_bytes = python_bytes;
    const uint8_t* buffer = reinterpret_cast<const uint8_t*>(str_bytes.data());
    size_t length = str_bytes.size();

    std::vector<RawOrder> orders;
    SIMDParser::parse_buffer(buffer, length, orders);
    
    return orders;
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
        .def("get_total_trades", &OrderBook::get_total_trades) // NEW
        .def("get_volume_executed", &OrderBook::get_volume_executed); // NEW

    m.def("parse_bytes", &parse_python_bytes, "Parse a raw binary stream using AVX-512");
}