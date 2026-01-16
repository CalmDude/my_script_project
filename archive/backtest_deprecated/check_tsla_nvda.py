"""
Check TSLA and NVDA individual performance vs equal-weighted portfolio
"""

import pandas as pd
import yfinance as yf

# Download data
print("Downloading TSLA and NVDA data...")
start = "2021-07-16"
end = "2025-12-26"

tsla = yf.download("TSLA", start=start, end=end, progress=False)["Close"]
nvda = yf.download("NVDA", start=start, end=end, progress=False)["Close"]

# Calculate returns
tsla_start = float(tsla.iloc[0])
tsla_end = float(tsla.iloc[-1])
nvda_start = float(nvda.iloc[0])
nvda_end = float(nvda.iloc[-1])

tsla_return = (tsla_end / tsla_start - 1) * 100
nvda_return = (nvda_end / nvda_start - 1) * 100

# Calculate annualized returns (4.45 years)
years = 4.45
tsla_cagr = ((tsla_end / tsla_start) ** (1 / years) - 1) * 100
nvda_cagr = ((nvda_end / nvda_start) ** (1 / years) - 1) * 100

print("\n" + "=" * 60)
print("TSLA & NVDA Performance (2021-07-16 to 2025-12-26)")
print("=" * 60)
print(f"\nTSLA:")
print(f"  Start: ${tsla_start:.2f}")
print(f"  End:   ${tsla_end:.2f}")
print(f"  Total Return: {tsla_return:+.2f}%")
print(f"  CAGR: {tsla_cagr:+.2f}%")

print(f"\nNVDA:")
print(f"  Start: ${nvda_start:.2f}")
print(f"  End:   ${nvda_end:.2f}")
print(f"  Total Return: {nvda_return:+.2f}%")
print(f"  CAGR: {nvda_cagr:+.2f}%")

print(f"\n" + "=" * 60)
print("Comparison to Backtest Results:")
print("=" * 60)
print(f"  Base (equal allocation):  34.62% CAGR")
print(f"  Scanner (50% TSLA, 20% NVDA): 16.89% CAGR")
print(f"\nConclusion:")
if tsla_cagr < 34.62 or nvda_cagr < 34.62:
    print(f"  ❌ Variable allocation HURT performance")
    print(f"     50% TSLA ({tsla_cagr:.2f}% CAGR) dragged down portfolio")
else:
    print(f"  ✅ Both beat base CAGR - issue must be elsewhere")
