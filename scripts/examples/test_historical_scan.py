"""
Quick test of historical scanning functionality
"""

from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from full_scanner import scan_stocks

# Test with a few tickers on a historical date
test_tickers = ["AAPL", "MSFT", "GOOGL"]
test_date = "2025-07-01"  # Historical date from 6 months ago

print(f"Testing historical scan for {test_date}")
print(f"Tickers: {test_tickers}")
print("=" * 80)

results = scan_stocks(
    test_tickers,
    category="Test",
    daily_bars=60,
    weekly_bars=52,
    concurrency=1,  # Single thread for testing
    as_of_date=test_date,
)

print("\n" + "=" * 80)
print("RESULTS:")
print("=" * 80)

if not results.empty:
    print(f"Successfully scanned {len(results)} tickers")
    print("\nSample results:")
    for _, row in results.head(3).iterrows():
        print(f"  {row['ticker']}: {row['signal']} @ ${row['current_price']:.2f}")
else:
    print("No results returned")

print("\n[OK] Historical scan test complete")
