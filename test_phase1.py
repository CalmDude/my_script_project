"""Quick test of Phase 1 enhancements"""
import shutil
from pathlib import Path
from technical_analysis import analyze_ticker

# Clear cache
cache_dir = Path('scanner_cache')
if cache_dir.exists():
    shutil.rmtree(cache_dir)
    print("✓ Cleared cache\n")

# Test on a real stock
print("Testing AAPL...")
result = analyze_ticker('AAPL')

print(f"\n=== Basic Info ===")
print(f"Ticker: {result['ticker']}")
print(f"Signal: {result['signal']}")
print(f"Price: ${result['current_price']:.2f}")

print(f"\n=== Moving Averages ===")
print(f"D50:  ${result.get('d50', 'N/A'):.2f}" if result.get('d50') else "D50:  N/A")
print(f"D100: ${result.get('d100', 'N/A'):.2f}" if result.get('d100') else "D100: N/A")
print(f"D200: ${result.get('d200', 'N/A'):.2f}" if result.get('d200') else "D200: N/A")

print(f"\n=== Support Levels ===")
print(f"S1: ${result.get('s1', 'N/A'):.2f}" if result.get('s1') else "S1: N/A")
print(f"S2: ${result.get('s2', 'N/A'):.2f}" if result.get('s2') else "S2: N/A")
print(f"S3: ${result.get('s3', 'N/A'):.2f}" if result.get('s3') else "S3: N/A")

print(f"\n=== Buy Quality Assessment ===")
print(f"Quality: {result.get('buy_quality', 'N/A')}")
print(f"Note: {result.get('buy_quality_note', 'N/A')}")

print(f"\n=== Resistance Levels ===")
print(f"R1: ${result.get('r1', 'N/A'):.2f}" if result.get('r1') else "R1: N/A")
print(f"R2: ${result.get('r2', 'N/A'):.2f}" if result.get('r2') else "R2: N/A")
print(f"R3: ${result.get('r3', 'N/A'):.2f}" if result.get('r3') else "R3: N/A")

print(f"\n=== Adjusted Sell Levels ===")
print(f"Adjusted R1: ${result.get('adjusted_r1', 'N/A'):.2f}" if result.get('adjusted_r1') else "Adj R1: N/A")
print(f"Adjusted R2: ${result.get('adjusted_r2', 'N/A'):.2f}" if result.get('adjusted_r2') else "Adj R2: N/A")
print(f"Adjusted R3: ${result.get('adjusted_r3', 'N/A'):.2f}" if result.get('adjusted_r3') else "Adj R3: N/A")
print(f"Feasibility: {result.get('sell_feasibility_note', 'N/A')}")

print("\n✅ Phase 1 Complete!")
