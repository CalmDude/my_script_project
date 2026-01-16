import pandas as pd

base = pd.read_csv("backtest/results/equity_curve_20260116_113016.csv")
scanner = pd.read_csv("backtest/results/equity_curve_20260116_112854.csv")

print("BASE ENGINE:")
print(f"  Rows: {len(base)}")
print(f"  Start value: ${base.iloc[0]['Portfolio_Value']:.2f}")
print(f"  End value: ${base.iloc[-1]['Portfolio_Value']:.2f}")

print("\nSCANNER ENGINE:")
print(f"  Rows: {len(scanner)}")
print(f"  Start value: ${scanner.iloc[0]['Portfolio_Value']:.2f}")
print(f"  End value: ${scanner.iloc[-1]['Portfolio_Value']:.2f}")

print("\nLast 5 rows of BASE:")
print(base.tail())

print("\nLast 5 rows of SCANNER:")
print(scanner.tail())
