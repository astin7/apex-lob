import struct
import numpy as np
import matplotlib.pyplot as plt
import apex_lob

def generate_mock_binary_data(num_orders):
    order_format = struct.Struct('Q I I c 15x')
    byte_array = bytearray()
    for i in range(num_orders):
        side = b'B' if i % 2 == 0 else b'S'
        byte_array.extend(order_format.pack(i, 15000 + (i % 100), 100, side))
    return bytes(byte_array)

def run_benchmark():
    total_orders = 1_000_000
    print(f"Generating {total_orders:,} orders & booting engine...")
    raw_data = generate_mock_binary_data(total_orders)
    parsed_orders = apex_lob.parse_bytes(raw_data)
    
    engine = apex_lob.OrderBook()
    
    print("Running Hardware Micro-Benchmark (Capturing Nanoseconds)...")
    # Execute the C++ high-resolution clock wrapper
    latencies_ns = apex_lob.benchmark_engine(engine, parsed_orders)
    
    latencies = np.array(latencies_ns)
    
    # Calculate HFT industry standard percentiles
    p50 = np.percentile(latencies, 50)
    p90 = np.percentile(latencies, 90)
    p99 = np.percentile(latencies, 99)
    p999 = np.percentile(latencies, 99.9)
    
    print("\n--- LATENCY RESULTS (Ryzen 9800X3D) ---")
    print(f"p50 (Median) : {p50:.2f} ns")
    print(f"p90          : {p90:.2f} ns")
    print(f"p99          : {p99:.2f} ns")
    print(f"p99.9 (Tail) : {p999:.2f} ns")
    
    # Generate the Professional Distribution Chart
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Filter extreme OS-level context switch outliers for a clean visualization
    plot_data = latencies[latencies < p999 * 1.5]
    
    ax.hist(plot_data, bins=100, color='cyan', alpha=0.7, edgecolor='black')
    ax.axvline(p50, color='lime', linestyle='dashed', linewidth=2, label=f'p50: {p50:.1f}ns')
    ax.axvline(p99, color='magenta', linestyle='dashed', linewidth=2, label=f'p99: {p99:.1f}ns')
    
    ax.set_title('Apex-LOB: Matching Engine Latency Distribution', fontsize=14, pad=15)
    ax.set_xlabel('Latency (Nanoseconds)', fontsize=12)
    ax.set_ylabel('Frequency (Number of Orders)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    plt.savefig('latency_distribution.png', dpi=300)
    print("\nSaved high-resolution benchmark graph to 'latency_distribution.png'")
    plt.show()

if __name__ == "__main__":
    run_benchmark()