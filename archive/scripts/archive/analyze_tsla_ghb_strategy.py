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
print("TSLA - GHB STRATEGY (Gold-Gray-Blue) - 5 YEAR ANALYSIS")
print("=" * 80)
print("\nGHB Strategy Rules:")
print("  BUY: Enter when state is P1 (Gold)")
print("  HOLD: Continue holding in P2 (Gray) or N1 (Gray)")
print("  SELL: Exit when state is N2 (Blue) AND price < D200 SMA")
print("\n" + "=" * 100)

for idx, trade in tsla_trades.iterrows():
    entry = pd.to_datetime(trade["entry_date"])
    exit_date = pd.to_datetime(trade["exit_date"])

    print(f"\n### TRADE #{idx+1} ###")
    print(f'Entry: {entry.strftime("%Y-%m-%d")} at ${trade["entry_price"]:.2f}')
    print(f'Exit:  {exit_date.strftime("%Y-%m-%d")} at ${trade["exit_price"]:.2f}')
    print(f'Return: {trade["return_pct"]:.2f}% over {int(trade["hold_weeks"])} weeks')
    print(f'Exit Reason: {trade["exit_reason"]}')

    # Get weekly states during this trade
    trade_data = tsla_df[
        (tsla_df["Week_End"] >= entry) & (tsla_df["Week_End"] <= exit_date)
    ]

    print(f"\nWeekly State Progression ({len(trade_data)} weeks):")
    print("-" * 100)
    print(
        f'{"Date":<12} {"Close":<10} {"D200":<10} {"State":<8} {"ROC_4W":<10} {"Action":<15}'
    )
    print("-" * 100)

    for i, (_, row) in enumerate(trade_data.iterrows()):
        date_str = row["Week_End"].strftime("%Y-%m-%d")
        close = row["Close"]
        d200 = row["D200"]
        state = row["Weekly_Larsson"]
        roc = row["ROC_4W"]

        if i == 0:
            action = ">>> BUY (P1)"
        elif i == len(trade_data) - 1:
            action = ">>> SELL (N2+<D200)"
        elif state == "P2":
            action = "HOLD (P2)"
        elif state == "N1":
            action = "HOLD (N1)"
        elif state == "P1":
            action = "HOLD (P1)"
        else:
            action = ""

        print(
            f"{date_str:<12} ${close:<9.2f} ${d200:<9.2f} {state:<8} {roc:>6.2f}%   {action:<15}"
        )

print("\n" + "=" * 100)
print("SUMMARY")
print("=" * 100)
print(f"Total Trades: {len(tsla_trades)}")
print(
    f'Winners: {len(tsla_trades[tsla_trades["return_pct"] > 0])} ({len(tsla_trades[tsla_trades["return_pct"] > 0])/len(tsla_trades)*100:.1f}%)'
)
print(f'Avg Return: {tsla_trades["return_pct"].mean():.2f}%')
print(f'Total Return: {tsla_trades["return_pct"].sum():.2f}%')
print(f'Avg Hold: {tsla_trades["hold_weeks"].mean():.1f} weeks')
print("=" * 100)
