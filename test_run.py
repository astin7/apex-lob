import time
import struct
import apex_lob

def generate_mock_binary_data(num_orders):
    order_format = struct.Struct('Q I I c 15x')
    byte_array = bytearray()
    for i in range(num_orders):
        side = b'B' if i % 2 == 0 else b'S'
        byte_array.extend(order_format.pack(i, 15000 + (i % 100), 100, side))
    return bytes(byte_array)

def run_pipeline():
    total_orders = 10_000_000
    raw_data = generate_mock_binary_data(total_orders)
    
    print("--- STAGE 1: AVX-512 PARSING ---")
    start_parse = time.perf_counter()
    parsed_orders = apex_lob.parse_bytes(raw_data)
    parse_time = time.perf_counter() - start_parse
    print(f"Parsed {len(parsed_orders):,} orders in {parse_time:.4f}s")

    print("\n--- STAGE 2: LOB ENGINE EXECUTION ---")
    lob = apex_lob.OrderBook()
    
    print("Matching orders in cache-aligned memory pools...")
    start_route = time.perf_counter()
    
    for order in parsed_orders:
        lob.process_order(order)
        
    route_time = time.perf_counter() - start_route
    
    print(f"Execution Engine Time: {route_time:.4f} seconds")
    print(f"Total Bids Rested: {lob.get_total_bids():,}")
    print(f"Total Asks Rested: {lob.get_total_asks():,}")
    print(f"Total Trades Executed: {lob.get_total_trades():,}")
    print(f"Total Volume Cleared: {lob.get_volume_executed():,}")

if __name__ == "__main__":
    run_pipeline()