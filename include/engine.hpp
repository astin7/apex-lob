#pragma once
#include "parser.hpp"
#include <vector>
#include <iostream>
#include <algorithm>

struct alignas(64) PriceLevel {
    uint32_t price;
    uint32_t total_volume;
    std::vector<RawOrder> order_queue; 

    PriceLevel() : price(0), total_volume(0) {}
};

class OrderBook {
private:
    std::vector<PriceLevel> bids; 
    std::vector<PriceLevel> asks; 
    
    uint32_t best_bid = 0;
    uint32_t best_ask = 20000; 
    
    uint64_t total_bids_rested = 0;
    uint64_t total_asks_rested = 0;
    
    uint64_t total_trades_executed = 0;
    uint64_t total_volume_executed = 0;

public:
    OrderBook() {
        bids.resize(20000);
        asks.resize(20000);

        for(int i = 15000; i <= 15100; ++i) {
            bids[i].order_queue.reserve(100000);
            asks[i].order_queue.reserve(100000);
        }
    }

    void process_order(const RawOrder& incoming_order) {
        uint32_t price = incoming_order.price;
        uint32_t remaining_qty = incoming_order.quantity;

        if (incoming_order.side == 'B') {
            while (remaining_qty > 0 && best_ask <= price) {
                PriceLevel& ask_level = asks[best_ask];
                
                if (ask_level.total_volume > 0) {
                    uint32_t fill_qty = std::min(remaining_qty, ask_level.total_volume);
                    remaining_qty -= fill_qty;
                    ask_level.total_volume -= fill_qty;
                    
                    total_trades_executed++;
                    total_volume_executed += fill_qty;
                    
                    if (ask_level.total_volume == 0) {
                        ask_level.order_queue.clear();
                    }
                }
                
                if (ask_level.total_volume == 0) {
                    best_ask++;
                    if(best_ask >= 20000) break;
                }
            }

            if (remaining_qty > 0) {
                bids[price].price = price;
                bids[price].order_queue.push_back(incoming_order);
                bids[price].total_volume += remaining_qty;
                total_bids_rested++;
                
                if (price > best_bid) {
                    best_bid = price;
                }
            }
        } else {
            while (remaining_qty > 0 && best_bid >= price && best_bid > 0) {
                PriceLevel& bid_level = bids[best_bid];
                
                if (bid_level.total_volume > 0) {
                    uint32_t fill_qty = std::min(remaining_qty, bid_level.total_volume);
                    remaining_qty -= fill_qty;
                    bid_level.total_volume -= fill_qty;
                    
                    total_trades_executed++;
                    total_volume_executed += fill_qty;
                    
                    if (bid_level.total_volume == 0) {
                        bid_level.order_queue.clear();
                    }
                }
                
                if (bid_level.total_volume == 0) {
                    best_bid--;
                }
            }

            if (remaining_qty > 0) {
                asks[price].price = price;
                asks[price].order_queue.push_back(incoming_order);
                asks[price].total_volume += remaining_qty;
                total_asks_rested++;
                
                if (price < best_ask) {
                    best_ask = price;
                }
            }
        }
    }

    uint64_t get_total_bids() const { return total_bids_rested; }
    uint64_t get_total_asks() const { return total_asks_rested; }
    uint64_t get_total_trades() const { return total_trades_executed; }
    uint64_t get_volume_executed() const { return total_volume_executed; }
    uint32_t get_best_bid() const { return best_bid; }
    uint32_t get_best_ask() const { return best_ask; }
};