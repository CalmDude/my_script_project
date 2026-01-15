"""
Build Optimized 20-25 Stock Portfolio for GHB Strategy

Combines your 12-stock watchlist with top performers from the 39-stock universe
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

# Full 39-stock moderate volatile universe
FULL_UNIVERSE = [
    "ALAB",
    "AMAT",
    "AMD",
    "AMZN",
    "ARM",
    "ASML",
    "AVGO",
    "BKNG",
    "CEG",
    "COST",
    "CPRT",
    "CRWD",
    "CTAS",
    "DASH",
    "FANG",
    "FTNT",
    "GOOG",
    "GOOGL",
    "ISRG",
    "KLAC",
    "LRCX",
    "MDB",
    "META",
    "MRNA",
    "MRVL",
    "MSFT",
    "MU",
    "NFLX",
    "NVDA",
    "ON",
    "PANW",
    "PCAR",
    "PLTR",
    "QCOM",
    "ROST",
    "TMUS",
    "TSLA",
    "TSM",
    "VRTX",
]

# Load GHB Strategy trades
trades_all = pd.read_csv("backtest_results/ghb_sma_trades.csv")

print("=" * 100)
print("BUILD OPTIMIZED 20-25 STOCK PORTFOLIO FOR GHB STRATEGY")
print("=" * 100)

# Analyze performance by ticker
ticker_performance = []

for ticker in FULL_UNIVERSE:
    ticker_trades = trades_all[trades_all["ticker"] == ticker]

    if len(ticker_trades) == 0:
        continue

    wins = ticker_trades[ticker_trades["return_pct"] > 0]

    ticker_performance.append(
        {
            "Ticker": ticker,
            "Total_Return": ticker_trades["return_pct"].sum(),
            "Trades": len(ticker_trades),
            "Win_Rate": len(wins) / len(ticker_trades) * 100,
            "Avg_Return": ticker_trades["return_pct"].mean(),
            "Best_Trade": ticker_trades["return_pct"].max(),
            "In_Watchlist": ticker in WATCHLIST,
            "Annual_Contribution": ticker_trades["return_pct"].sum() / 5,
        }
    )

df_perf = pd.DataFrame(ticker_performance).sort_values("Total_Return", ascending=False)

print("\n📊 TOP PERFORMERS FROM 39-STOCK UNIVERSE")
print("=" * 100)
print(
    f"\n{'Rank':<6} {'Ticker':<8} {'Total Return':<15} {'Annual':<12} {'Trades':<8} {'Avg Return':<12} {'In Watchlist':<15}"
)
print("-" * 100)

for i, row in df_perf.iterrows():
    watchlist_flag = "✓ YES" if row["In_Watchlist"] else ""
    print(
        f"{df_perf.index.get_loc(i)+1:<6} {row['Ticker']:<8} {row['Total_Return']:>+12.2f}%  {row['Annual_Contribution']:>+8.2f}%  {row['Trades']:<8} {row['Avg_Return']:>+9.2f}%  {watchlist_flag:<15}"
    )

# Identify top performers NOT in watchlist
candidates = df_perf[~df_perf["In_Watchlist"]].head(15)

print("\n" + "=" * 100)
print("RECOMMENDED STOCKS TO ADD (Top Performers Not in Your Watchlist)")
print("=" * 100)

print(
    f"\n{'Ticker':<8} {'Annual Return':<15} {'Total Trades':<15} {'Win Rate':<12} {'Avg Return':<12} {'Best Trade':<15}"
)
print("-" * 100)

for _, row in candidates.head(13).iterrows():
    print(
        f"{row['Ticker']:<8} {row['Annual_Contribution']:>+12.2f}%  {row['Trades']:<15} {row['Win_Rate']:>8.1f}%  {row['Avg_Return']:>+9.2f}%  {row['Best_Trade']:>+12.2f}%"
    )

# Build optimized portfolio
top_additions = candidates.head(13)["Ticker"].tolist()
optimized_portfolio = sorted(set(WATCHLIST + top_additions))

print("\n" + "=" * 100)
print(f"YOUR OPTIMIZED {len(optimized_portfolio)}-STOCK PORTFOLIO")
print("=" * 100)

print(f"\n🎯 CORE HOLDINGS (Your Original Watchlist - {len(WATCHLIST)} stocks):")
print(f"   {', '.join(sorted(WATCHLIST))}")

print(f"\n⭐ ADDITIONS (Top Performers - {len(top_additions)} stocks):")
print(f"   {', '.join(sorted(top_additions))}")

print(f"\n📋 COMPLETE LIST ({len(optimized_portfolio)} stocks):")
wrapped_list = ", ".join(sorted(optimized_portfolio))
# Wrap at 90 chars
lines = []
current_line = "   "
for ticker in sorted(optimized_portfolio):
    if len(current_line) + len(ticker) + 2 > 90:
        lines.append(current_line.rstrip(", "))
        current_line = "   " + ticker + ", "
    else:
        current_line += ticker + ", "
lines.append(current_line.rstrip(", "))
for line in lines:
    print(line)

# Calculate expected performance
trades_optimized = trades_all[trades_all["ticker"].isin(optimized_portfolio)]


def analyze_trades(trades, label):
    wins = trades[trades["return_pct"] > 0]
    losses = trades[trades["return_pct"] <= 0]
    years = 5

    return {
        "label": label,
        "stocks": trades["ticker"].nunique(),
        "total_trades": len(trades),
        "trades_per_year": len(trades) / years,
        "win_rate": len(wins) / len(trades) * 100,
        "avg_return": trades["return_pct"].mean(),
        "annual_return": trades["return_pct"].sum() / years,
        "avg_win": wins["return_pct"].mean() if len(wins) > 0 else 0,
        "avg_loss": losses["return_pct"].mean() if len(losses) > 0 else 0,
    }


metrics_watchlist = analyze_trades(
    trades_all[trades_all["ticker"].isin(WATCHLIST)], "Original Watchlist (12)"
)
metrics_optimized = analyze_trades(
    trades_optimized, f"Optimized Portfolio ({len(optimized_portfolio)})"
)
metrics_full = analyze_trades(trades_all, "Full Universe (39)")

print("\n" + "=" * 100)
print("PERFORMANCE COMPARISON")
print("=" * 100)

print(
    f"\n{'Metric':<30} {'Original (12)':<20} {'Optimized ({len(optimized_portfolio)})':<20} {'Full (39)':<20}"
)
print("-" * 100)

comparisons = [
    ("Stocks", "stocks"),
    ("Trades Per Year", "trades_per_year"),
    ("Win Rate %", "win_rate"),
    ("Avg Return %", "avg_return"),
    ("**ANNUAL RETURN %**", "annual_return"),
]

for label, metric in comparisons:
    if "ANNUAL" in label:
        print("-" * 100)

    watch_val = metrics_watchlist[metric]
    opt_val = metrics_optimized[metric]
    full_val = metrics_full[metric]

    if metric in ["win_rate", "avg_return", "annual_return"]:
        watch_str = f"{watch_val:.2f}%"
        opt_str = f"{opt_val:.2f}%"
        full_str = f"{full_val:.2f}%"
    else:
        watch_str = f"{watch_val:.1f}"
        opt_str = f"{opt_val:.1f}"
        full_str = f"{full_val:.1f}"

    print(f"{label:<30} {watch_str:<20} {opt_str:<20} {full_str:<20}")

    if "ANNUAL" in label:
        print("=" * 100)

# Practical insights
print("\n" + "=" * 100)
print("WHAT THIS MEANS FOR YOU")
print("=" * 100)

print(f"\n📊 TRADING ACTIVITY:")
print(
    f"   • ~{metrics_optimized['trades_per_year']:.0f} trades per year (vs 5 with watchlist only)"
)
print(f"   • ~{metrics_optimized['trades_per_year']/52:.1f} trades per week")
print(f"   • ~{metrics_optimized['trades_per_year']/12:.1f} trades per month")
print(
    f"   • {metrics_optimized['trades_per_year']/len(optimized_portfolio):.2f} trades per stock per year"
)

print(f"\n💰 EXPECTED RETURNS:")
print(f"   • Annual Return: {metrics_optimized['annual_return']:+.2f}%")
print(
    f"   • {(metrics_optimized['annual_return']/metrics_watchlist['annual_return']-1)*100:+.1f}% better than watchlist only"
)
print(
    f"   • {(metrics_optimized['annual_return']/metrics_full['annual_return'])*100:.1f}% of full universe performance"
)
print(f"   • Win Rate: {metrics_optimized['win_rate']:.1f}%")

print(f"\n⏱️  TIME COMMITMENT:")
print(f"   • Weekly Review: ~10-15 minutes (scan {len(optimized_portfolio)} stocks)")
print(
    f"   • Trade Executions: ~{metrics_optimized['trades_per_year']:.0f} buys + ~{metrics_optimized['trades_per_year']:.0f} sells per year"
)
print(f"   • Still very manageable!")

print(f"\n📈 PORTFOLIO MANAGEMENT:")
print(
    f"   • Expect to hold {int(metrics_optimized['trades_per_year']/2.5)}-{int(metrics_optimized['trades_per_year']/2)} stocks concurrently"
)
print(f"   • Position Size: 8-10% per stock")
print(f"   • Cash Reserve: 20-30% for new opportunities")

print("\n" + "=" * 100)
print("FINAL RECOMMENDATION")
print("=" * 100)

print(f"\n✅ USE THE OPTIMIZED {len(optimized_portfolio)}-STOCK PORTFOLIO")
print(f"\n   Perfect Balance:")
print(
    f"   • Captures {(metrics_optimized['annual_return']/metrics_full['annual_return'])*100:.0f}% of full universe returns"
)
print(
    f"   • Only {len(optimized_portfolio)} stocks vs {metrics_full['stocks']:.0f} (easy to manage)"
)
print(
    f"   • ~{metrics_optimized['trades_per_year']:.0f} trades/year (1-2 per month, very manageable)"
)
print(f"   • {metrics_optimized['annual_return']:+.2f}% annual return (excellent!)")
print(f"   • Includes ALL your watchlist stocks (no tough choices)")
print(f"\n   This is the sweet spot: High returns + Low complexity")

# Save to file
print("\n" + "=" * 100)
print("SAVING YOUR OPTIMIZED PORTFOLIO")
print("=" * 100)

# Save list to text file
with open("data/ghb_optimized_portfolio.txt", "w") as f:
    f.write("# GHB Strategy Optimized Portfolio (25 stocks)\n")
    f.write("# Created: 2026-01-15\n")
    f.write("#\n")
    f.write("# Expected Performance:\n")
    f.write(f"# - Annual Return: {metrics_optimized['annual_return']:+.2f}%\n")
    f.write(f"# - Trades Per Year: ~{metrics_optimized['trades_per_year']:.0f}\n")
    f.write(f"# - Win Rate: {metrics_optimized['win_rate']:.1f}%\n")
    f.write("#\n")
    f.write("# Stocks (sorted alphabetically):\n")
    for ticker in sorted(optimized_portfolio):
        f.write(f"{ticker}\n")

print(f"\n✅ Portfolio saved to: data/ghb_optimized_portfolio.txt")

# Update notebook universe variable
print(f"\n💡 NEXT STEPS:")
print(f"   1. Review your {len(optimized_portfolio)}-stock optimized portfolio above")
print(f"   2. Update ghb_portfolio_scanner.ipynb to use this list")
print(f"   3. Run the scanner to see current signals")
print(f"   4. Start trading!")

print("\n" + "=" * 100)
