from full_scanner import scan_stocks
import pandas as pd

print("Testing scanner without volume profile...")
tickers = ['AAPL', 'MSFT']
results = scan_stocks(tickers, 'Test', 60, 52, 2)

print(f"\n✓ Scanned {len(results)} stocks")
print(f"\nColumns: {list(results.columns)}")
print(f"\nHas confluence: {'confluence' in results.columns}")
print(f"Has daily_poc: {'daily_poc' in results.columns}")
print(f"Has daily_vah: {'daily_vah' in results.columns}")
print(f"Has daily_val: {'daily_val' in results.columns}")

if not results.empty:
    print(f"\nFirst result:")
    print(results.iloc[0].to_dict())
