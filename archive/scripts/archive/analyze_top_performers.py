import pandas as pd
import numpy as np

# Load GHB Strategy and F results
trades_d = pd.read_csv("backtest_results/weekly_ghb_strategy_trades.csv")
trades_f = pd.read_csv("backtest_results/weekly_strategy_f_trades.csv")

print("=" * 100)
print("PROFIT ANALYSIS: VOLATILE STOCKS vs STABLE STOCKS")
print("=" * 100)

for strategy_name, trades in [
    ("GHB Strategy (Gold-Gray-Blue)", trades_d),
    ("Strategy F (D + 20% Trailing Stop)", trades_f),
]:
    print(f"\n{strategy_name}")
    print("=" * 100)

    # Calculate per-ticker performance
    ticker_stats = (
        trades.groupby("ticker")
        .agg({"return_pct": ["sum", "mean", "count"], "hold_weeks": "mean"})
        .round(2)
    )

    ticker_stats.columns = [
        "Total_Return",
        "Avg_Return",
        "Trade_Count",
        "Avg_Hold_Weeks",
    ]
    ticker_stats = ticker_stats.sort_values("Total_Return", ascending=False)

    # Calculate annualized return (approximate)
    # Annualized = (Total_Return / # years active)
    # Assume ~5 years of data (2021-2025)
    years = 5
    ticker_stats["Annual_Return_Est"] = ticker_stats["Total_Return"] / years

    # Calculate trades per year
    ticker_stats["Trades_Per_Year"] = ticker_stats["Trade_Count"] / years

    print(f"\nTop 20 Most Profitable Tickers:")
    print("-" * 100)
    print(
        f"{'Ticker':<8} {'Total Return':<14} {'Annual Est':<13} {'Avg Return':<13} {'# Trades':<11} {'Trades/Yr':<12} {'Avg Hold':<10}"
    )
    print("-" * 100)

    top_20 = ticker_stats.head(20)
    for ticker, row in top_20.iterrows():
        print(
            f"{ticker:<8} {row['Total_Return']:>+12.2f}% {row['Annual_Return_Est']:>+11.2f}% {row['Avg_Return']:>+11.2f}% {int(row['Trade_Count']):>9} {row['Trades_Per_Year']:>10.1f} {row['Avg_Hold_Weeks']:>8.1f}w"
        )

    print(f'\n{"-" * 100}')
    print(
        f"{'SUMMARY':<8} {top_20['Total_Return'].sum():>+12.2f}% {top_20['Annual_Return_Est'].sum():>+11.2f}% {top_20['Avg_Return'].mean():>+11.2f}% {int(top_20['Trade_Count'].sum()):>9} {top_20['Trades_Per_Year'].sum():>10.1f} {top_20['Avg_Hold_Weeks'].mean():>8.1f}w"
    )

    # Identify volatile tech stocks (known high volatility)
    volatile_stocks = [
        "NVDA",
        "TSLA",
        "AMD",
        "AVGO",
        "SMCI",
        "MRVL",
        "NFLX",
        "META",
        "GOOGL",
        "AMZN",
    ]
    volatile_trades = trades[trades["ticker"].isin(volatile_stocks)]
    stable_trades = trades[~trades["ticker"].isin(volatile_stocks)]

    print(f"\n\nVOLATILE TECH STOCKS Analysis:")
    print(f"Stocks: {', '.join(volatile_stocks)}")
    print("-" * 100)
    print(
        f"Metric                     Volatile Stocks      Stable Stocks        Difference"
    )
    print("-" * 100)
    print(
        f"Total Trades               {len(volatile_trades):>15}      {len(stable_trades):>15}      {len(volatile_trades) - len(stable_trades):>+10}"
    )
    print(
        f"Win Rate                   {len(volatile_trades[volatile_trades['return_pct']>0])/len(volatile_trades)*100:>14.1f}%     {len(stable_trades[stable_trades['return_pct']>0])/len(stable_trades)*100:>14.1f}%     {(len(volatile_trades[volatile_trades['return_pct']>0])/len(volatile_trades) - len(stable_trades[stable_trades['return_pct']>0])/len(stable_trades))*100:>+9.1f}%"
    )
    print(
        f"Avg Return/Trade           {volatile_trades['return_pct'].mean():>+14.2f}%     {stable_trades['return_pct'].mean():>+14.2f}%     {volatile_trades['return_pct'].mean() - stable_trades['return_pct'].mean():>+9.2f}%"
    )
    print(
        f"Total Return               {volatile_trades['return_pct'].sum():>+14.2f}%     {stable_trades['return_pct'].sum():>+14.2f}%     {volatile_trades['return_pct'].sum() - stable_trades['return_pct'].sum():>+9.2f}%"
    )
    print(
        f"Avg Win                    {volatile_trades[volatile_trades['return_pct']>0]['return_pct'].mean():>+14.2f}%     {stable_trades[stable_trades['return_pct']>0]['return_pct'].mean():>+14.2f}%     {volatile_trades[volatile_trades['return_pct']>0]['return_pct'].mean() - stable_trades[stable_trades['return_pct']>0]['return_pct'].mean():>+9.2f}%"
    )
    print(
        f"Avg Loss                   {volatile_trades[volatile_trades['return_pct']<=0]['return_pct'].mean():>+14.2f}%     {stable_trades[stable_trades['return_pct']<=0]['return_pct'].mean():>+14.2f}%     {volatile_trades[volatile_trades['return_pct']<=0]['return_pct'].mean() - stable_trades[stable_trades['return_pct']<=0]['return_pct'].mean():>+9.2f}%"
    )
    print(
        f"Max Win                    {volatile_trades['return_pct'].max():>+14.2f}%     {stable_trades['return_pct'].max():>+14.2f}%     {volatile_trades['return_pct'].max() - stable_trades['return_pct'].max():>+9.2f}%"
    )
    print(
        f"Avg Hold (weeks)           {volatile_trades['hold_weeks'].mean():>14.1f}      {stable_trades['hold_weeks'].mean():>14.1f}      {volatile_trades['hold_weeks'].mean() - stable_trades['hold_weeks'].mean():>+9.1f}"
    )

    # Calculate contribution to total profits
    total_profit = trades["return_pct"].sum()
    volatile_profit = volatile_trades["return_pct"].sum()
    volatile_contribution = (
        (volatile_profit / total_profit) * 100 if total_profit != 0 else 0
    )

    print(f'\n{"-" * 100}')
    print(
        f"Volatile Stocks Contribution: {volatile_profit:+.2f}% out of {total_profit:+.2f}% total ({volatile_contribution:.1f}% of profits)"
    )
    print(
        f"Per Trade: Volatile = {volatile_profit/len(volatile_trades):+.2f}% vs Stable = {stable_trades['return_pct'].sum()/len(stable_trades):+.2f}%"
    )

print("\n" + "=" * 100)
print("CONCLUSION")
print("=" * 100)

# Overall analysis
d_volatile = trades_d[trades_d["ticker"].isin(volatile_stocks)]
d_annual_volatile = d_volatile["return_pct"].sum() / 5  # 5 years

print(f"\nGHB Strategy - Volatile Stocks Annual Return: {d_annual_volatile:+.2f}%")
print(f'GHB Strategy - Overall Annual Return: {trades_d["return_pct"].sum() / 5:+.2f}%')
print(f"\nTo achieve 14%+ annual returns:")

if d_annual_volatile > 14:
    print(
        f"  ✓ Volatile stocks ALONE can deliver {d_annual_volatile:.1f}% annual returns"
    )
    print(f"  ✓ Focus on high-volatility tech stocks is key to alpha generation")
else:
    total_annual = trades_d["return_pct"].sum() / 5
    trades_needed = 14 / (
        trades_d["return_pct"].mean() if trades_d["return_pct"].mean() > 0 else 1
    )
    print(f"  Current avg: {total_annual:.1f}% annual return across all stocks")
    print(f"  Need {trades_needed:.1f} trades/year at current avg return to hit 14%")
    print(f"  OR focus on stocks with higher volatility and bigger moves")

print(f'\n  Current avg return/trade: {trades_d["return_pct"].mean():.2f}%')
print(f'  Current avg hold: {trades_d["hold_weeks"].mean():.1f} weeks')
print(f"  Current trades/year: ~{len(trades_d) / 5:.1f} trades across portfolio")
print(f"\n  To hit 14% annual with current strategy:")
print(f"    Option 1: Increase position sizing (use leverage or concentration)")
print(f"    Option 2: Focus portfolio on top 10-15 volatile performers")
print(f"    Option 3: Trade more frequently (shorter holds)")
print(f"    Option 4: Use options/leverage on high-conviction setups")

print("=" * 100)
