import pandas as pd
import json

trades = pd.read_csv("backtest/results/trades_20260115_221603.csv")
sells = trades[trades["Action"] == "SELL"].copy()

print("=" * 80)
print("CUSTOM TECH STOCKS BACKTEST - DETAILED RESULTS")
print("=" * 80)

print("\n📊 Top Winners:")
print(
    sells.nlargest(10, "PnL_%")[
        ["Ticker", "Entry_Date", "Date", "PnL_%", "Hold_Days"]
    ].to_string(index=False)
)

print("\n📊 Losers:")
print(
    sells.nsmallest(5, "PnL_%")[
        ["Ticker", "Entry_Date", "Date", "PnL_%", "Hold_Days"]
    ].to_string(index=False)
)

print("\n📊 Stock Frequency:")
print(sells["Ticker"].value_counts().head(10))

print("\n📊 Summary:")
summary = json.load(open("backtest/results/summary_20260115_221603.json"))
print(
    f"  Period: {summary['Backtest_Period']['Start_Date']} to {summary['Backtest_Period']['End_Date']}"
)
print(f"  Duration: {summary['Backtest_Period']['Years']:.1f} years")
print(f"  Starting Value: ${summary['Performance']['Starting_Value']:,.0f}")
print(f"  Final Value: ${summary['Performance']['Final_Value']:,.0f}")
print(f"  Total Return: {summary['Performance']['Total_Return_%']:.2f}%")
print(f"  CAGR: {summary['Performance']['CAGR_%']:.2f}%")
print(f"  Max Drawdown: {summary['Performance']['Max_Drawdown_%']:.2f}%")
print(f"  Win Rate: {summary['Trading_Stats']['Win_Rate_%']:.2f}%")
print(f"  Total Trades: {summary['Trading_Stats']['Total_Trades']}")
print(f"  Avg Win: {summary['Trading_Stats']['Avg_Win_%']:.2f}%")
print(f"  Avg Loss: {summary['Trading_Stats']['Avg_Loss_%']:.2f}%")
print(
    f"  Best Trade: {summary['Trading_Stats']['Best_Trade_Ticker']} +{summary['Trading_Stats']['Best_Trade_%']:.1f}%"
)
print(
    f"  Worst Trade: {summary['Trading_Stats']['Worst_Trade_Ticker']} {summary['Trading_Stats']['Worst_Trade_%']:.1f}%"
)

print("\n📊 Stocks in Universe:")
with open("backtest/data/custom_tech_stocks.txt", "r") as f:
    stocks = [line.strip() for line in f if line.strip()]
print(f"  {', '.join(stocks)}")
print(f"  Note: AYGO failed to download (delisted/invalid ticker)")
