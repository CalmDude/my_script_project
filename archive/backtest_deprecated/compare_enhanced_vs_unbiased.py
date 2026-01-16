import pandas as pd
import json

print("=" * 80)
print("ENHANCED VS UNBIASED COMPARISON")
print("=" * 80)

# Load results
enhanced = json.load(open("backtest/results/summary_20260115_215538.json"))
unbiased = json.load(open("backtest/results/summary_20260115_213934.json"))

print(f"\nEnhanced Universe:")
print(f'  CAGR: {enhanced["Performance"]["CAGR_%"]:.2f}%')
print(f'  Win Rate: {enhanced["Trading_Stats"]["Win_Rate_%"]:.2f}%')
print(f'  Total Return: {enhanced["Performance"]["Total_Return_%"]:.2f}%')
print(f'  Max Drawdown: {enhanced["Performance"]["Max_Drawdown_%"]:.2f}%')
print(f'  Trades: {enhanced["Trading_Stats"]["Total_Trades"]}')

print(f"\nUnbiased Universe:")
print(f'  CAGR: {unbiased["Performance"]["CAGR_%"]:.2f}%')
print(f'  Win Rate: {unbiased["Trading_Stats"]["Win_Rate_%"]:.2f}%')
print(f'  Total Return: {unbiased["Performance"]["Total_Return_%"]:.2f}%')
print(f'  Max Drawdown: {unbiased["Performance"]["Max_Drawdown_%"]:.2f}%')
print(f'  Trades: {unbiased["Trading_Stats"]["Total_Trades"]}')

print(f"\nDifference:")
print(
    f'  CAGR: {enhanced["Performance"]["CAGR_%"] - unbiased["Performance"]["CAGR_%"]:.2f}%'
)
print(
    f'  Win Rate: {enhanced["Trading_Stats"]["Win_Rate_%"] - unbiased["Trading_Stats"]["Win_Rate_%"]:.2f}%'
)
print(
    f'  Max Drawdown: {enhanced["Performance"]["Max_Drawdown_%"] - unbiased["Performance"]["Max_Drawdown_%"]:.2f}%'
)

# Check which stocks are in each universe
print("\n" + "=" * 80)
print("UNIVERSE COMPARISON")
print("=" * 80)

enhanced_tickers = set(
    [
        line.strip()
        for line in open("backtest/data/sp500_enhanced_2020.txt")
        if line.strip()
    ]
)
unbiased_tickers = set(
    [
        line.strip()
        for line in open("backtest/data/sp500_unbiased_2020.txt")
        if line.strip()
    ]
)

print(f"\nEnhanced: {len(enhanced_tickers)} stocks")
print(f"Unbiased: {len(unbiased_tickers)} stocks")

common = enhanced_tickers & unbiased_tickers
removed = unbiased_tickers - enhanced_tickers
added = enhanced_tickers - unbiased_tickers

print(f"\nKept: {len(common)} stocks")
print(f"  {sorted(common)}")

print(f"\nRemoved (quality filters): {len(removed)} stocks")
print(f"  {sorted(removed)}")

print(f"\nAdded (better quality): {len(added)} stocks")
print(f"  {sorted(added)}")

# Analyze trades to see if we missed big winners
print("\n" + "=" * 80)
print("TOP WINNERS COMPARISON")
print("=" * 80)

enhanced_trades = pd.read_csv("backtest/results/trades_20260115_215538.csv")
unbiased_trades = pd.read_csv("backtest/results/trades_20260115_213934.csv")

enhanced_sells = enhanced_trades[enhanced_trades["Action"] == "SELL"].nlargest(
    10, "PnL_%"
)
unbiased_sells = unbiased_trades[unbiased_trades["Action"] == "SELL"].nlargest(
    10, "PnL_%"
)

print("\nEnhanced Top 10 Winners:")
for _, row in enhanced_sells.iterrows():
    print(f'  {row["Ticker"]}: +{row["PnL_%"]:.1f}% ({row["Hold_Days"]} days)')

print("\nUnbiased Top 10 Winners:")
for _, row in unbiased_sells.iterrows():
    print(f'  {row["Ticker"]}: +{row["PnL_%"]:.1f}% ({row["Hold_Days"]} days)')
