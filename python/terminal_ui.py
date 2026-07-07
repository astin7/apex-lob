import time
import struct
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich import box
import apex_lob

def generate_mock_binary_data(num_orders):
    order_format = struct.Struct('Q I I c 15x')
    byte_array = bytearray()
    for i in range(num_orders):
        qty = 999_999 if (i == 50_000) else 100
        side = b'B' if i % 2 == 0 else b'S'
        byte_array.extend(order_format.pack(i, 15000 + (i % 100), qty, side))
    return bytes(byte_array)

def make_layout(lob, total_orders, processed, start_time):
    """Generates the Bloomberg-style terminal layout"""
    elapsed = time.perf_counter() - start_time if start_time else 0.001
    ops_sec = processed / elapsed

    # Limit Order Book Table
    lob_table = Table(box=box.MINIMAL_DOUBLE_HEAD, expand=True, style="blue")
    lob_table.add_column("Level", justify="left", style="cyan")
    lob_table.add_column("Price", justify="right", style="green")
    
    lob_table.add_row("Best Ask (Sell)", f"${lob.get_best_ask():,}")
    lob_table.add_row("---", "---")
    lob_table.add_row("Best Bid (Buy)", f"${lob.get_best_bid():,}")

    # Metrics Table
    metrics_table = Table(box=box.SIMPLE, expand=True)
    metrics_table.add_column("Metric", style="magenta")
    metrics_table.add_column("Value", justify="right", style="yellow")
    
    metrics_table.add_row("Total Trades Executed", f"{lob.get_total_trades():,}")
    metrics_table.add_row("Volume Cleared", f"{lob.get_volume_executed():,}")
    metrics_table.add_row("Active Bids Rested", f"{lob.get_total_bids():,}")
    metrics_table.add_row("Active Asks Rested", f"{lob.get_total_asks():,}")

    # Engine Status Table
    status_table = Table(box=box.SIMPLE, expand=True)
    status_table.add_column("System", style="white")
    status_table.add_column("Status", justify="right", style="bold green")
    
    status_table.add_row("CPU Matching Engine", "ONLINE (Cache-Aligned)")
    status_table.add_row("RTX 3090 Risk Core", "ONLINE (CUDA Parallel)")
    status_table.add_row("Live Throughput", f"{ops_sec:,.0f} ops/sec")
    status_table.add_row("Processing Queue", f"{(processed/total_orders)*100:.1f}%")

    layout = Layout()
    layout.split_column(
        Layout(Panel(lob_table, title="[bold white]APEX-LOB // LIVE MARKET FEED", border_style="blue"), ratio=1),
        Layout(Panel(metrics_table, title="[bold white]EXECUTION METRICS", border_style="magenta"), ratio=1),
        Layout(Panel(status_table, title="[bold white]SYSTEM HARDWARE STATUS", border_style="green"), ratio=1)
    )
    return layout

def run_terminal():
    total_orders = 1_000_000
    raw_data = generate_mock_binary_data(total_orders)
    
    print("Booting Core Engines...")
    parsed_orders = apex_lob.parse_bytes(raw_data)
    risk_results = apex_lob.gpu_risk_check(parsed_orders)
    lob = apex_lob.OrderBook()
    
    # Live UI Loop

    # Process 10k orders per UI refresh
    chunk_size = 10_000
    start_time = time.perf_counter()
    
    with Live(make_layout(lob, total_orders, 0, start_time), refresh_per_second=15, screen=True) as live:
        for i in range(0, total_orders, chunk_size):
            chunk = parsed_orders[i:i+chunk_size]
            risk_chunk = risk_results[i:i+chunk_size]
            
            for j, order in enumerate(chunk):
                if risk_chunk[j]:
                    lob.process_order(order)
            
            # Update the screen
            processed = min(i + chunk_size, total_orders)
            live.update(make_layout(lob, total_orders, processed, start_time))

            # Artificial throttle so you can actually watch it
            time.sleep(0.05)

if __name__ == "__main__":
    run_terminal()