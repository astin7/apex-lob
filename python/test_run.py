import time
import struct
import apex_lob

def generate_mock_binary_data(num_orders):
    order_format = struct.Struct('Q I I c 15x')
    byte_array = bytearray()
    
    print(f"Generating {num_orders:,} mock binary orders...")
    for i in range(num_orders):
        # Intentionally inject a few invalid "fat-finger" orders to test the GPU risk logic
        qty = 999_999 if (i == 500_000 or i == 5_000_000) else 100
        side = b'B' if i % 2 == 0 else b'S'
        byte_array.extend(order_format.pack(i, 15000 + (i % 100), qty, side))
        
    return bytes(byte_array)

def run_pipeline():
    total_orders = 10_000_000
    raw_data = generate_mock_binary_data(total_orders)
    
    print("\n--- STAGE 1: AVX-512 PARSING (CPU) ---")
    start_parse = time.perf_counter()
    parsed_orders = apex_lob.parse_bytes(raw_data)
    parse_time = time.perf_counter() - start_parse
    print(f"Parsed {len(parsed_orders):,} orders in {parse_time:.4f}s")

    print("\n--- STAGE 3: CUDA PRE-TRADE RISK ENGINE (RTX 3090) ---")
    print(f"Transferring data to VRAM & spawning 10,000,000 GPU threads...")
    start_gpu = time.perf_counter()
    
    # Fire data at the RTX 3090
    risk_results = apex_lob.gpu_risk_check(parsed_orders)
    
    gpu_time = time.perf_counter() - start_gpu
    rejected_count = risk_results.count(False)
    print(f"GPU Risk Analysis Time: {gpu_time:.4f} seconds")
    print(f"Orders Assessed: {len(risk_results):,}")
    print(f"Malicious/Fat-Finger Orders Rejected: {rejected_count}")

    print("\n--- STAGE 2: LOB MATCHING ENGINE (RYZEN CPU) ---")
    lob = apex_lob.OrderBook()
    print("Streaming valid orders into cache-aligned memory pools...")
    
    start_route = time.perf_counter()
    for i, order in enumerate(parsed_orders):
        if risk_results[i]: # Only process if the GPU marked it valid
            lob.process_order(order)
    route_time = time.perf_counter() - start_route
    
    print(f"Matching Engine Time: {route_time:.4f} seconds")
    print(f"Total Trades Executed: {lob.get_total_trades():,}")
    print(f"Total Volume Cleared: {lob.get_volume_executed():,}")

if __name__ == "__main__":
    run_pipeline()