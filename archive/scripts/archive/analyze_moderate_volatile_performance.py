import pandas as pd

# Load GHB Strategy results
trades = pd.read_csv("backtest_results/weekly_ghb_strategy_trades.csv")

# Calculate moderate volatility stocks from backtest data
ticker_metrics = []

for ticker in trades["ticker"].unique():
    ticker_trades = trades[trades["ticker"] == ticker]
    returns = ticker_trades["return_pct"]

    metrics = {
        "Ticker": ticker,
        "Std_Dev": returns.std(),
        "Max_Win": returns.max(),
        "Avg_Win": returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0,
    }

    ticker_metrics.append(metrics)

df_metrics = pd.DataFrame(ticker_metrics)

# Apply moderate definition
moderate_volatile = df_metrics[
    (df_metrics["Std_Dev"] >= 30)
    | (df_metrics["Max_Win"] >= 150)
    | (df_metrics["Avg_Win"] >= 40)
]["Ticker"].tolist()

# Split trades
moderate_trades = trades[trades["ticker"].isin(moderate_volatile)]
non_moderate_trades = trades[~trades["ticker"].isin(moderate_volatile)]

print("=" * 100)
print("GHB STRATEGY PERFORMANCE: MODERATE VOLATILE vs NON-VOLATILE STOCKS")
print("=" * 100)

print(f"\nModerate Volatile Definition:")
print(f"  - Standard Deviation ≥30% OR")
print(f"  - Max Win ≥150% OR")
print(f"  - Avg Win ≥40%")
print(f"\nQualifying Stocks ({len(moderate_volatile)}):")
print(", ".join(sorted(moderate_volatile)))

print("\n" + "=" * 100)
print("DETAILED COMPARISON")
print("=" * 100)


def analyze_trades(trades_df, label):
    if len(trades_df) == 0:
        return

    returns = trades_df["return_pct"]
    winners = returns[returns > 0]
    losers = returns[returns <= 0]

    print(f"\n{label}:")
    print("-" * 100)
    print(f"{'Metric':<30} {'Value':<20}")
    print("-" * 100)
    print(f"{'Total Trades':<30} {len(trades_df):<20}")
    print(f"{'Winners':<30} {len(winners)} ({len(winners)/len(trades_df)*100:.1f}%)")
    print(f"{'Losers':<30} {len(losers)} ({len(losers)/len(trades_df)*100:.1f}%)")
    print(f"{'Win Rate':<30} {len(winners)/len(trades_df)*100:.2f}%")
    print()
    print(f"{'Avg Return per Trade':<30} {returns.mean():>+18.2f}%")
    print(f"{'Median Return':<30} {returns.median():>+18.2f}%")
    print(f"{'Total Return':<30} {returns.sum():>+18.2f}%")
    print()
    print(f"{'Avg Win':<30} {winners.mean() if len(winners) > 0 else 0:>+18.2f}%")
    print(f"{'Avg Loss':<30} {losers.mean() if len(losers) > 0 else 0:>+18.2f}%")
    print(f"{'Max Win':<30} {returns.max():>+18.2f}%")
    print(f"{'Max Loss':<30} {returns.min():>+18.2f}%")
    print()
    print(f"{'Avg Hold (weeks)':<30} {trades_df['hold_weeks'].mean():.1f}")
    print(f"{'Median Hold (weeks)':<30} {trades_df['hold_weeks'].median():.1f}")
    print()
    print(f"{'Std Dev of Returns':<30} {returns.std():.2f}%")
    print(
        f"{'Sharpe Ratio (approx)':<30} {returns.mean() / returns.std() if returns.std() > 0 else 0:.3f}"
    )

    # Annualized estimates
    years = 5
    annual_return = returns.sum() / years
    trades_per_year = len(trades_df) / years

    print()
    print(f"{'Annual Return (est)':<30} {annual_return:>+18.2f}%")
    print(f"{'Trades per Year':<30} {trades_per_year:>18.1f}")


analyze_trades(moderate_trades, "📊 MODERATE VOLATILE STOCKS")
analyze_trades(non_moderate_trades, "📊 NON-VOLATILE STOCKS")

print("\n" + "=" * 100)
print("SIDE-BY-SIDE SUMMARY")
print("=" * 100)


def calc_metrics(trades_df):
    if len(trades_df) == 0:
        return {}
    returns = trades_df["return_pct"]
    winners = returns[returns > 0]
    return {
        "trades": len(trades_df),
        "win_rate": len(winners) / len(trades_df) * 100,
        "avg_return": returns.mean(),
        "total_return": returns.sum(),
        "avg_win": winners.mean() if len(winners) > 0 else 0,
        "avg_loss": (
            returns[returns <= 0].mean() if len(returns[returns <= 0]) > 0 else 0
        ),
        "max_win": returns.max(),
        "avg_hold": trades_df["hold_weeks"].mean(),
        "annual_est": returns.sum() / 5,
    }


mod_metrics = calc_metrics(moderate_trades)
non_metrics = calc_metrics(non_moderate_trades)

print(
    f"\n{'Metric':<30} {'Moderate Volatile':<20} {'Non-Volatile':<20} {'Difference':<20}"
)
print("-" * 100)
print(
    f"{'Total Trades':<30} {mod_metrics['trades']:<20} {non_metrics['trades']:<20} {mod_metrics['trades'] - non_metrics['trades']:>+19}"
)
print(
    f"{'Win Rate':<30} {mod_metrics['win_rate']:<19.1f}% {non_metrics['win_rate']:<19.1f}% {mod_metrics['win_rate'] - non_metrics['win_rate']:>+18.1f}%"
)
print(
    f"{'Avg Return/Trade':<30} {mod_metrics['avg_return']:<+19.2f}% {non_metrics['avg_return']:<+19.2f}% {mod_metrics['avg_return'] - non_metrics['avg_return']:>+18.2f}%"
)
print(
    f"{'Total Return':<30} {mod_metrics['total_return']:<+19.2f}% {non_metrics['total_return']:<+19.2f}% {mod_metrics['total_return'] - non_metrics['total_return']:>+18.2f}%"
)
print(
    f"{'Avg Win':<30} {mod_metrics['avg_win']:<+19.2f}% {non_metrics['avg_win']:<+19.2f}% {mod_metrics['avg_win'] - non_metrics['avg_win']:>+18.2f}%"
)
print(
    f"{'Avg Loss':<30} {mod_metrics['avg_loss']:<+19.2f}% {non_metrics['avg_loss']:<+19.2f}% {mod_metrics['avg_loss'] - non_metrics['avg_loss']:>+18.2f}%"
)
print(
    f"{'Max Win':<30} {mod_metrics['max_win']:<+19.2f}% {non_metrics['max_win']:<+19.2f}% {mod_metrics['max_win'] - non_metrics['max_win']:>+18.2f}%"
)
print(
    f"{'Avg Hold (weeks)':<30} {mod_metrics['avg_hold']:<19.1f} {non_metrics['avg_hold']:<19.1f} {mod_metrics['avg_hold'] - non_metrics['avg_hold']:>+18.1f}"
)
print(
    f"{'Annual Return (est)':<30} {mod_metrics['annual_est']:<+19.2f}% {non_metrics['annual_est']:<+19.2f}% {mod_metrics['annual_est'] - non_metrics['annual_est']:>+18.2f}%"
)

print("\n" + "=" * 100)
print("CONCLUSION")
print("=" * 100)

if mod_metrics["avg_return"] > non_metrics["avg_return"] * 1.5:
    print("\n✅ MODERATE VOLATILE STOCKS SIGNIFICANTLY OUTPERFORM")
    print(
        f"   - {mod_metrics['avg_return']/non_metrics['avg_return']:.1f}x better avg return per trade"
    )
    print(
        f"   - {mod_metrics['annual_est']:.1f}% annual return vs {non_metrics['annual_est']:.1f}%"
    )
    print(f"\n💡 STRATEGY: Focus 70-80% of capital on moderate volatile stocks")
elif mod_metrics["avg_return"] > non_metrics["avg_return"]:
    print("\n✅ MODERATE VOLATILE STOCKS OUTPERFORM")
    print(
        f"   - {mod_metrics['avg_return'] - non_metrics['avg_return']:+.2f}% better per trade"
    )
    print(f"\n💡 STRATEGY: Overweight moderate volatile stocks in portfolio")
else:
    print("\n⚠️  NON-VOLATILE STOCKS PERFORM BETTER")
    print(f"   - Moderate definition may need adjustment")

print("\n" + "=" * 100)
