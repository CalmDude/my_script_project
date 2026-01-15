import pandas as pd
from pathlib import Path
import glob

# Load TSLA GHB Strategy trades
trades = pd.read_csv("backtest_results/weekly_ghb_strategy_trades.csv")
tsla_trades = trades[trades["ticker"] == "TSLA"].sort_values("entry_date")

# Load all weekly reports to get TSLA state history
reports_dir = Path("scanner_results/weekly_larsson")
files = sorted(glob.glob(str(reports_dir / "nasdaq100_weekly_*.xlsx")))

tsla_history = []
for file in files:
    df = pd.read_excel(file, sheet_name="Weekly Data")
    tsla = df[df["Ticker"] == "TSLA"]
    if not tsla.empty:
        tsla_history.append(tsla)

tsla_df = pd.concat(tsla_history, ignore_index=True)
tsla_df = tsla_df.sort_values("Week_End")
tsla_df["Week_End"] = pd.to_datetime(tsla_df["Week_End"])

print("=" * 100)
print("TSLA - TRAILING STOP ANALYSIS")
print("=" * 100)
print("\nComparing exit strategies:")
print("  Original: Exit on N2 + Price < D200")
print("  Option 1: Exit on 20% trailing stop from peak OR N2+<D200")
print("  Option 2: Exit on 25% trailing stop from peak OR N2+<D200")
print("  Option 3: Exit on 30% trailing stop from peak OR N2+<D200")
print("\n" + "=" * 100)

trailing_stops = [0.20, 0.25, 0.30]
results_summary = []

for idx, trade in tsla_trades.iterrows():
    entry = pd.to_datetime(trade["entry_date"])
    exit_date = pd.to_datetime(trade["exit_date"])
    entry_price = trade["entry_price"]
    original_exit_price = trade["exit_price"]
    original_return = trade["return_pct"]

    print(f"\n### TRADE #{idx+1} ###")
    print(f'Entry: {entry.strftime("%Y-%m-%d")} at ${entry_price:.2f}')
    print(
        f'Original Exit: {exit_date.strftime("%Y-%m-%d")} at ${original_exit_price:.2f} ({original_return:.2f}%)'
    )

    # Get weekly states during this trade
    trade_data = tsla_df[
        (tsla_df["Week_End"] >= entry) & (tsla_df["Week_End"] <= exit_date)
    ]

    # Calculate peak price during trade
    peak_price = trade_data["Close"].max()
    peak_date = trade_data.loc[trade_data["Close"].idxmax(), "Week_End"]
    peak_return = (peak_price - entry_price) / entry_price * 100

    print(
        f'Peak: {peak_date.strftime("%Y-%m-%d")} at ${peak_price:.2f} ({peak_return:.2f}% from entry)'
    )
    print(
        f"Drawdown from peak: {(original_exit_price - peak_price) / peak_price * 100:.2f}%"
    )

    print("\nTrailing Stop Scenarios:")

    trade_results = {
        "trade_num": idx + 1,
        "entry_date": entry.strftime("%Y-%m-%d"),
        "entry_price": entry_price,
        "peak_price": peak_price,
        "peak_date": peak_date.strftime("%Y-%m-%d"),
        "original_exit": original_exit_price,
        "original_return": original_return,
    }

    for stop_pct in trailing_stops:
        # Simulate trailing stop
        peak_so_far = entry_price
        exit_triggered = False
        exit_price_ts = original_exit_price
        exit_date_ts = exit_date
        exit_reason = "Original N2+<D200"

        for i, (_, row) in enumerate(trade_data.iterrows()):
            current_price = row["Close"]
            current_date = row["Week_End"]

            # Update peak
            if current_price > peak_so_far:
                peak_so_far = current_price

            # Check trailing stop
            drawdown_from_peak = (peak_so_far - current_price) / peak_so_far
            if drawdown_from_peak >= stop_pct:
                exit_triggered = True
                exit_price_ts = current_price
                exit_date_ts = current_date
                exit_reason = f"{stop_pct*100:.0f}% Trailing Stop"
                break

        return_ts = (exit_price_ts - entry_price) / entry_price * 100
        hold_weeks_ts = (exit_date_ts - entry).days / 7
        improvement = return_ts - original_return

        trade_results[f"stop_{int(stop_pct*100)}"] = return_ts
        trade_results[f"stop_{int(stop_pct*100)}_exit"] = exit_price_ts
        trade_results[f"stop_{int(stop_pct*100)}_date"] = exit_date_ts.strftime(
            "%Y-%m-%d"
        )

        print(
            f'  {stop_pct*100:.0f}% Stop: Exit ${exit_price_ts:.2f} on {exit_date_ts.strftime("%Y-%m-%d")} '
            f"= {return_ts:>6.2f}% ({improvement:>+6.2f}% vs original) [{exit_reason}]"
        )

    results_summary.append(trade_results)

# Summary comparison
print("\n" + "=" * 100)
print("SUMMARY COMPARISON")
print("=" * 100)

df_results = pd.DataFrame(results_summary)

print(f"\nOriginal GHB Strategy:")
print(f'  Total Return: {df_results["original_return"].sum():.2f}%')
print(f'  Avg Return: {df_results["original_return"].mean():.2f}%')
print(f'  Winners: {len(df_results[df_results["original_return"] > 0])}/4')

for stop_pct in [20, 25, 30]:
    col = f"stop_{stop_pct}"
    print(f"\n{stop_pct}% Trailing Stop:")
    print(f"  Total Return: {df_results[col].sum():.2f}%")
    print(f"  Avg Return: {df_results[col].mean():.2f}%")
    print(f"  Winners: {len(df_results[df_results[col] > 0])}/4")
    print(
        f'  Improvement: {df_results[col].sum() - df_results["original_return"].sum():>+.2f}%'
    )

print("\n" + "=" * 100)
print("RECOMMENDATION:")

# Find best performing stop
best_stop = None
best_return = df_results["original_return"].sum()
for stop_pct in [20, 25, 30]:
    col = f"stop_{stop_pct}"
    if df_results[col].sum() > best_return:
        best_return = df_results[col].sum()
        best_stop = stop_pct

if best_stop:
    improvement = best_return - df_results["original_return"].sum()
    print(
        f"  {best_stop}% trailing stop shows best results (+{improvement:.2f}% improvement)"
    )
    print(
        f"  Consider backtesting Strategy F: GHB Strategy + {best_stop}% trailing stop on all tickers"
    )
else:
    print("  Original GHB Strategy performed best for TSLA")
    print(
        "  However, trailing stops may still benefit other tickers with different volatility"
    )

print("=" * 100)
