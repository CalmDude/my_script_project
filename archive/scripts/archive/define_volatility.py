import pandas as pd
import numpy as np

# Load GHB Strategy results
trades = pd.read_csv("backtest_results/weekly_ghb_strategy_trades.csv")

# Calculate volatility metrics per ticker
ticker_metrics = []

for ticker in trades["ticker"].unique():
    ticker_trades = trades[trades["ticker"] == ticker]

    returns = ticker_trades["return_pct"]

    metrics = {
        "Ticker": ticker,
        "Trade_Count": len(ticker_trades),
        "Avg_Return": returns.mean(),
        "Std_Dev": returns.std(),
        "Max_Win": returns.max(),
        "Max_Loss": returns.min(),
        "Range": returns.max() - returns.min(),
        "Win_Rate": (returns > 0).sum() / len(returns) * 100,
        "Avg_Win": returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0,
        "Avg_Loss": (
            returns[returns <= 0].mean() if len(returns[returns <= 0]) > 0 else 0
        ),
    }

    ticker_metrics.append(metrics)

df_metrics = pd.DataFrame(ticker_metrics)

# Sort by different criteria
print("=" * 120)
print("VOLATILITY DEFINITIONS - DATA-DRIVEN APPROACH")
print("=" * 120)

print("\n1. BY STANDARD DEVIATION OF RETURNS (Classic Volatility):")
print("-" * 120)
top_std = df_metrics.nlargest(15, "Std_Dev")
print(
    f"{'Ticker':<8} {'Trades':<8} {'Avg Return':<12} {'Std Dev':<12} {'Max Win':<12} {'Win Rate':<10}"
)
print("-" * 120)
for _, row in top_std.iterrows():
    print(
        f"{row['Ticker']:<8} {int(row['Trade_Count']):<8} {row['Avg_Return']:>+10.2f}% {row['Std_Dev']:>10.2f}% {row['Max_Win']:>+10.2f}% {row['Win_Rate']:>8.1f}%"
    )

print("\n2. BY MAXIMUM WIN (Explosive Upside Potential):")
print("-" * 120)
top_maxwin = df_metrics.nlargest(15, "Max_Win")
print(
    f"{'Ticker':<8} {'Trades':<8} {'Avg Return':<12} {'Max Win':<12} {'Range':<12} {'Win Rate':<10}"
)
print("-" * 120)
for _, row in top_maxwin.iterrows():
    print(
        f"{row['Ticker']:<8} {int(row['Trade_Count']):<8} {row['Avg_Return']:>+10.2f}% {row['Max_Win']:>+10.2f}% {row['Range']:>10.2f}% {row['Win_Rate']:>8.1f}%"
    )

print("\n3. BY RANGE (Max Win - Max Loss):")
print("-" * 120)
top_range = df_metrics.nlargest(15, "Range")
print(
    f"{'Ticker':<8} {'Trades':<8} {'Avg Return':<12} {'Range':<12} {'Max Win':<12} {'Max Loss':<12}"
)
print("-" * 120)
for _, row in top_range.iterrows():
    print(
        f"{row['Ticker']:<8} {int(row['Trade_Count']):<8} {row['Avg_Return']:>+10.2f}% {row['Range']:>10.2f}% {row['Max_Win']:>+10.2f}% {row['Max_Loss']:>+10.2f}%"
    )

print("\n4. BY AVERAGE WIN SIZE (Big Winners):")
print("-" * 120)
top_avgwin = df_metrics.nlargest(15, "Avg_Win")
print(
    f"{'Ticker':<8} {'Trades':<8} {'Avg Return':<12} {'Avg Win':<12} {'Win Rate':<10} {'Max Win':<12}"
)
print("-" * 120)
for _, row in top_avgwin.iterrows():
    print(
        f"{row['Ticker']:<8} {int(row['Trade_Count']):<8} {row['Avg_Return']:>+10.2f}% {row['Avg_Win']:>+10.2f}% {row['Win_Rate']:>8.1f}% {row['Max_Win']:>+10.2f}%"
    )

# Define quantitative thresholds
print("\n" + "=" * 120)
print("PROPOSED VOLATILITY CRITERIA")
print("=" * 120)

criteria = {
    "Conservative": {"std_dev": 20, "max_win": 100, "avg_win": 30, "range": 100},
    "Moderate": {"std_dev": 30, "max_win": 150, "avg_win": 40, "range": 150},
    "Aggressive": {"std_dev": 40, "max_win": 200, "avg_win": 50, "range": 200},
}

for level, thresholds in criteria.items():
    volatile = df_metrics[
        (df_metrics["Std_Dev"] >= thresholds["std_dev"])
        | (df_metrics["Max_Win"] >= thresholds["max_win"])
        | (df_metrics["Avg_Win"] >= thresholds["avg_win"])
    ].sort_values("Avg_Return", ascending=False)

    print(
        f'\n{level} Definition (Std Dev ≥{thresholds["std_dev"]}% OR Max Win ≥{thresholds["max_win"]}% OR Avg Win ≥{thresholds["avg_win"]}%):'
    )
    print(f"Qualifies: {len(volatile)} stocks")
    print(f"Stocks: {', '.join(volatile['Ticker'].head(20).tolist())}")

    if len(volatile) > 0:
        total_return = trades[trades["ticker"].isin(volatile["Ticker"])][
            "return_pct"
        ].sum()
        total_trades = len(trades[trades["ticker"].isin(volatile["Ticker"])])
        avg_return = total_return / total_trades if total_trades > 0 else 0
        print(f"Avg Return/Trade: {avg_return:+.2f}%")
        print(f"Total Trades: {total_trades}")

print("\n" + "=" * 120)
print("RECOMMENDATION")
print("=" * 120)

# Use moderate as default
moderate_volatile = df_metrics[
    (df_metrics["Std_Dev"] >= 30)
    | (df_metrics["Max_Win"] >= 150)
    | (df_metrics["Avg_Win"] >= 40)
].sort_values("Avg_Return", ascending=False)

print("\nRECOMMENDED: Moderate Definition")
print(f"\nCriteria: Std Dev ≥30% OR Max Win ≥150% OR Avg Win ≥40%")
print(f"\nQualifying Stocks ({len(moderate_volatile)}):")
print(", ".join(moderate_volatile["Ticker"].head(30).tolist()))

print("\n" + "=" * 120)
