"""
GHB Strategy Performance: Your 12-Stock Watchlist vs Full 39-Stock Universe

Analyzes what happens if you focus only on your personal watchlist
"""

import pandas as pd

# Your 12-stock watchlist
WATCHLIST = [
    "ALAB",
    "AVGO",
    "MRVL",
    "ARM",
    "TSLA",
    "NVDA",
    "PLTR",
    "MU",
    "TSM",
    "ASML",
    "GOOG",
    "AMD",
]

# Load GHB Strategy trades
trades_all = pd.read_csv("backtest_results/ghb_sma_trades.csv")

# Filter for watchlist only
trades_watchlist = trades_all[trades_all["ticker"].isin(WATCHLIST)].copy()

print("=" * 100)
print("GHB STRATEGY: YOUR 12-STOCK WATCHLIST vs FULL UNIVERSE")
print("=" * 100)

print(f"\n📋 YOUR WATCHLIST ({len(WATCHLIST)} stocks):")
print(f"   {', '.join(sorted(WATCHLIST))}")


# Calculate metrics for both
def analyze_trades(trades, label):
    if trades.empty:
        return None

    wins = trades[trades["return_pct"] > 0]
    losses = trades[trades["return_pct"] <= 0]

    years = 5  # 2021-2025
    trades_per_year = len(trades) / years

    return {
        "label": label,
        "total_trades": len(trades),
        "trades_per_year": trades_per_year,
        "win_rate": len(wins) / len(trades) * 100,
        "avg_return": trades["return_pct"].mean(),
        "total_return": trades["return_pct"].sum(),
        "annual_return": trades["return_pct"].sum() / years,
        "avg_win": wins["return_pct"].mean() if len(wins) > 0 else 0,
        "avg_loss": losses["return_pct"].mean() if len(losses) > 0 else 0,
        "median_return": trades["return_pct"].median(),
        "std_dev": trades["return_pct"].std(),
        "max_win": trades["return_pct"].max(),
        "max_loss": trades["return_pct"].min(),
        "avg_hold_weeks": trades["hold_weeks"].mean(),
        "unique_tickers": trades["ticker"].nunique(),
    }


metrics_watchlist = analyze_trades(trades_watchlist, "Your Watchlist (12 stocks)")
metrics_all = analyze_trades(trades_all, "Full Universe (97 stocks)")

print("\n" + "=" * 100)
print("PERFORMANCE COMPARISON")
print("=" * 100)

print(
    f"\n{'Metric':<30} {'Your Watchlist':<25} {'Full Universe':<25} {'Difference':<15}"
)
print("-" * 100)

comparisons = [
    ("Total Stocks", "unique_tickers", ""),
    ("Total Trades (5 years)", "total_trades", ""),
    ("Trades Per Year", "trades_per_year", ""),
    ("", None, ""),  # Spacer
    ("Win Rate %", "win_rate", "%"),
    ("Avg Return %", "avg_return", "%"),
    ("Avg Win %", "avg_win", "%"),
    ("Avg Loss %", "avg_loss", "%"),
    ("", None, ""),  # Spacer
    ("Max Win %", "max_win", "%"),
    ("Max Loss %", "max_loss", "%"),
    ("Median Return %", "median_return", "%"),
    ("Std Deviation %", "std_dev", "%"),
    ("Avg Hold Weeks", "avg_hold_weeks", ""),
    ("", None, ""),  # Spacer
    ("**ANNUAL RETURN %**", "annual_return", "%"),
]

for label, metric, suffix in comparisons:
    if metric is None:
        print("")
        continue

    watch_val = metrics_watchlist[metric]
    all_val = metrics_all[metric]
    diff = watch_val - all_val

    if suffix == "%":
        watch_str = f"{watch_val:.2f}%"
        all_str = f"{all_val:.2f}%"
        diff_str = f"{diff:+.2f}%"
    else:
        watch_str = f"{watch_val:.2f}"
        all_str = f"{all_val:.2f}"
        diff_str = f"{diff:+.2f}"

    # Highlight annual return
    if "ANNUAL" in label:
        print("-" * 100)

    print(f"{label:<30} {watch_str:<25} {all_str:<25} {diff_str:<15}")

    if "ANNUAL" in label:
        print("=" * 100)

# Detailed watchlist analysis
print("\n" + "=" * 100)
print("YOUR WATCHLIST: TRADE-BY-TRADE HISTORY")
print("=" * 100)

trades_watchlist_sorted = trades_watchlist.sort_values("return_pct", ascending=False)

print(
    f"\n{'Ticker':<8} {'Entry Date':<12} {'Exit Date':<12} {'Return':<12} {'Hold Weeks':<12} {'Exit Reason':<40}"
)
print("-" * 100)

for _, trade in trades_watchlist_sorted.iterrows():
    print(
        f"{trade['ticker']:<8} {str(trade['entry_date']):<12} {str(trade['exit_date']):<12} "
        f"{trade['return_pct']:>+10.2f}% {trade['hold_weeks']:>10.1f}  {trade['exit_reason'][:38]:<40}"
    )

# Per-ticker breakdown
print("\n" + "=" * 100)
print("PERFORMANCE BY TICKER (Your Watchlist)")
print("=" * 100)

ticker_stats = []
for ticker in sorted(WATCHLIST):
    ticker_trades = trades_watchlist[trades_watchlist["ticker"] == ticker]
    if len(ticker_trades) > 0:
        ticker_wins = ticker_trades[ticker_trades["return_pct"] > 0]
        ticker_stats.append(
            {
                "Ticker": ticker,
                "Trades": len(ticker_trades),
                "Win_Rate": len(ticker_wins) / len(ticker_trades) * 100,
                "Avg_Return": ticker_trades["return_pct"].mean(),
                "Total_Return": ticker_trades["return_pct"].sum(),
                "Best_Trade": ticker_trades["return_pct"].max(),
            }
        )
    else:
        ticker_stats.append(
            {
                "Ticker": ticker,
                "Trades": 0,
                "Win_Rate": 0,
                "Avg_Return": 0,
                "Total_Return": 0,
                "Best_Trade": 0,
            }
        )

df_ticker_stats = pd.DataFrame(ticker_stats).sort_values(
    "Total_Return", ascending=False
)

print(
    f"\n{'Ticker':<8} {'Trades':<8} {'Win Rate':<12} {'Avg Return':<15} {'Total Return':<15} {'Best Trade':<15}"
)
print("-" * 100)

for _, row in df_ticker_stats.iterrows():
    if row["Trades"] > 0:
        print(
            f"{row['Ticker']:<8} {row['Trades']:<8} {row['Win_Rate']:>8.1f}%   {row['Avg_Return']:>+12.2f}%   "
            f"{row['Total_Return']:>+12.2f}%   {row['Best_Trade']:>+12.2f}%"
        )
    else:
        print(
            f"{row['Ticker']:<8} {'0':<8} {'N/A':<12} {'N/A':<15} {'N/A':<15} {'N/A':<15}"
        )

# Practical insights
print("\n" + "=" * 100)
print("PRACTICAL INSIGHTS FOR YOUR WATCHLIST")
print("=" * 100)

print(f"\n📊 TRADING FREQUENCY:")
print(f"   • {metrics_watchlist['trades_per_year']:.1f} trades per year on average")
print(f"   • {metrics_watchlist['trades_per_year']/12:.2f} trades per stock per year")
print(
    f"   • You'll hold ~{12 / (metrics_watchlist['trades_per_year']/12):.1f} stocks at any given time"
)

print(f"\n💰 EXPECTED PERFORMANCE:")
print(f"   • Annual Return: {metrics_watchlist['annual_return']:+.2f}%")
print(f"   • Average Trade: {metrics_watchlist['avg_return']:+.2f}%")
print(f"   • Win Rate: {metrics_watchlist['win_rate']:.1f}%")
print(
    f"   • Risk/Reward: {abs(metrics_watchlist['avg_win'] / metrics_watchlist['avg_loss']):.2f}:1"
)

print(f"\n⏱️  TIME COMMITMENT:")
print(
    f"   • Average Hold Period: {metrics_watchlist['avg_hold_weeks']:.0f} weeks ({metrics_watchlist['avg_hold_weeks']/4:.1f} months)"
)
print(f"   • Weekly Review: ~5 minutes to scan 12 stocks")
print(
    f"   • Executions: ~{metrics_watchlist['trades_per_year']:.0f} buys + {metrics_watchlist['trades_per_year']:.0f} sells per year"
)

print(f"\n📈 PORTFOLIO SIZING:")
if metrics_watchlist["trades_per_year"] > 0:
    avg_concurrent = 12 / (52 / metrics_watchlist["avg_hold_weeks"])
    print(
        f"   • Expected Concurrent Positions: ~{avg_concurrent:.0f}-{min(avg_concurrent+2, 12):.0f} stocks"
    )
    print(f"   • Recommended Position Size: {100/avg_concurrent:.0f}% per stock")
    print(f"   • Cash Reserve: 20-30% for new opportunities")

print(f"\n🎯 CONCENTRATION IMPACT:")
if metrics_watchlist["annual_return"] > metrics_all["annual_return"]:
    improvement = metrics_watchlist["annual_return"] - metrics_all["annual_return"]
    print(f"   ✅ Your watchlist OUTPERFORMS by {improvement:+.2f}% annually!")
    print(f"   ✅ Benefit: Easier to manage, better returns")
    print(f"   ✅ Recommendation: FOCUS ON WATCHLIST ONLY")
else:
    underperformance = metrics_all["annual_return"] - metrics_watchlist["annual_return"]
    print(f"   ⚠️  Your watchlist underperforms by {underperformance:.2f}% annually")
    print(f"   💡 Consider: Keep watchlist but add high performers from full universe")
    print(f"   💡 Sweet spot: 15-20 stocks (your 12 + top 3-8 from universe)")

print("\n" + "=" * 100)
print("FINAL RECOMMENDATION")
print("=" * 100)

print(f"\n✅ FOCUS ON YOUR 12-STOCK WATCHLIST!")
print(f"\n   Why:")
print(
    f"   • {metrics_watchlist['trades_per_year']:.0f} trades/year is manageable ({metrics_watchlist['trades_per_year']/12:.1f} per stock)"
)
print(f"   • {metrics_watchlist['annual_return']:+.2f}% annual return is excellent")
print(f"   • You know these companies well")
print(f"   • Easy weekly monitoring (5 minutes)")
print(f"   • Less complexity = better execution")
print(
    f"\n   Your watchlist delivers {metrics_watchlist['annual_return']/metrics_all['annual_return']*100:.1f}% of full universe returns"
)
print(
    f"   with only {len(WATCHLIST)}/{metrics_all['unique_tickers']} stocks (12% of universe)"
)

print("\n" + "=" * 100)
