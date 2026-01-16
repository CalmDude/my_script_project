import pandas as pd
import json

print("=" * 80)
print("PHASE 2 VS UNBIASED COMPARISON")
print("=" * 80)

# Load results
phase2 = json.load(open("backtest/results/summary_20260115_220929.json"))
unbiased = json.load(open("backtest/results/summary_20260115_213934.json"))

print(f"\nPhase 2 (Stop Losses + Entry Filters):")
print(f'  CAGR: {phase2["Performance"]["CAGR_%"]:.2f}%')
print(f'  Win Rate: {phase2["Trading_Stats"]["Win_Rate_%"]:.2f}%')
print(f'  Total Return: {phase2["Performance"]["Total_Return_%"]:.2f}%')
print(f'  Max Drawdown: {phase2["Performance"]["Max_Drawdown_%"]:.2f}%')
print(f'  Trades: {phase2["Trading_Stats"]["Total_Trades"]}')
print(
    f'  Best: {phase2["Trading_Stats"]["Best_Trade_Ticker"]} +{phase2["Trading_Stats"]["Best_Trade_%"]:.1f}%'
)

print(f"\nUnbiased Baseline:")
print(f'  CAGR: {unbiased["Performance"]["CAGR_%"]:.2f}%')
print(f'  Win Rate: {unbiased["Trading_Stats"]["Win_Rate_%"]:.2f}%')
print(f'  Total Return: {unbiased["Performance"]["Total_Return_%"]:.2f}%')
print(f'  Max Drawdown: {unbiased["Performance"]["Max_Drawdown_%"]:.2f}%')
print(f'  Trades: {unbiased["Trading_Stats"]["Total_Trades"]}')

print(f"\nDifference:")
print(
    f'  CAGR: {phase2["Performance"]["CAGR_%"] - unbiased["Performance"]["CAGR_%"]:.2f}%'
)
print(
    f'  Win Rate: {phase2["Trading_Stats"]["Win_Rate_%"] - unbiased["Trading_Stats"]["Win_Rate_%"]:.2f}%'
)
print(
    f'  Trades: {phase2["Trading_Stats"]["Total_Trades"] - unbiased["Trading_Stats"]["Total_Trades"]}'
)

# Analyze trades
print("\n" + "=" * 80)
print("TRADE ANALYSIS")
print("=" * 80)

phase2_trades = pd.read_csv("backtest/results/trades_20260115_220929.csv")
unbiased_trades = pd.read_csv("backtest/results/trades_20260115_213934.csv")

# Count different exit types
phase2_exits = phase2_trades[phase2_trades["Action"] == "SELL"][
    "Entry_State"
].value_counts()
print(f"\nPhase 2 Exit Types:")
print(phase2_exits)

# Check how many trades were filtered
phase2_buys = len(phase2_trades[phase2_trades["Action"] == "BUY"])
unbiased_buys = len(unbiased_trades[unbiased_trades["Action"] == "BUY"])
print(f"\nTrades Entered:")
print(f"  Phase 2: {phase2_buys} trades")
print(f"  Unbiased: {unbiased_buys} trades")
print(
    f"  Filtered out: {unbiased_buys - phase2_buys} trades ({(unbiased_buys - phase2_buys) / unbiased_buys * 100:.1f}%)"
)

# Check if we caught TRGP
phase2_tickers = set(phase2_trades[phase2_trades["Action"] == "BUY"]["Ticker"])
unbiased_tickers = set(unbiased_trades[unbiased_trades["Action"] == "BUY"]["Ticker"])

print(f"\nBig Winners Check:")
big_winners = ["TRGP", "MPC", "RCL", "FANG", "DVN"]
for ticker in big_winners:
    phase2_has = ticker in phase2_tickers
    unbiased_has = ticker in unbiased_tickers
    print(
        f'  {ticker}: Phase 2 = {"✅" if phase2_has else "❌"}, Unbiased = {"✅" if unbiased_has else "❌"}'
    )

# Check Phase 2 TRGP trade details
if "TRGP" in phase2_tickers:
    trgp_trades = phase2_trades[phase2_trades["Ticker"] == "TRGP"]
    print(f"\nPhase 2 TRGP Trade:")
    for _, trade in trgp_trades[trgp_trades["Action"] == "SELL"].iterrows():
        print(
            f'  Entry: {trade["Entry_Date"]}, Exit: {trade["Date"]}, Return: {trade["PnL_%"]:.1f}%'
        )
