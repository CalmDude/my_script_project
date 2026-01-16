"""
Compare Biased vs Unbiased Backtest Results
Shows the impact of survivorship and optimization bias
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime


def load_backtest_summary(summary_file):
    """Load backtest summary JSON"""
    with open(summary_file, "r") as f:
        return json.load(f)


def compare_results():
    """Compare biased (original) vs unbiased (2020-based) backtest results"""

    results_dir = Path("backtest/results")

    print("=" * 100)
    print("BACKTEST COMPARISON: Biased vs Unbiased Methodology")
    print("=" * 100)

    # Find latest summary files
    biased_summaries = list(results_dir.glob("summary_*_sp500_optimized.json"))
    unbiased_summaries = list(results_dir.glob("summary_*_sp500_unbiased_2020.json"))

    if not biased_summaries:
        print("\n❌ No biased backtest results found")
        print("   Run: python backtest/run_backtest.py (with universe=sp500_optimized)")
        return

    if not unbiased_summaries:
        print("\n❌ No unbiased backtest results found")
        print(
            "   Run: python backtest/run_backtest.py (with universe=sp500_unbiased_2020)"
        )
        return

    # Load latest of each
    biased_file = sorted(biased_summaries)[-1]
    unbiased_file = sorted(unbiased_summaries)[-1]

    biased = load_backtest_summary(biased_file)
    unbiased = load_backtest_summary(unbiased_file)

    print("\n📊 METHODOLOGY COMPARISON")
    print("=" * 100)

    # Methodology
    print("\n🔴 BIASED BACKTEST (Original):")
    print("   - Universe: Current S&P 500 survivors (as of 2025)")
    print("   - Selection: Top 25 by CAGR from 2021-2025 backtest")
    print("   - Issues: Survivorship bias + optimization bias")
    print("   - Reality: You couldn't have picked these stocks in Jan 2021")

    print("\n✅ UNBIASED BACKTEST (Corrected):")
    print("   - Universe: S&P 500 members as of Jan 1, 2021")
    print("   - Selection: Top 25 by 2020 volatility (using 2020 data only)")
    print("   - Benefits: No survivorship, no optimization bias")
    print("   - Reality: You COULD have picked these stocks in Jan 2021")

    # Performance comparison
    print("\n\n📈 PERFORMANCE COMPARISON")
    print("=" * 100)

    metrics = [
        ("Starting Capital", "Starting_Cash", "$", 0),
        ("Final Value", "Final_Value", "$", 2),
        ("Total Return", "Total_Return_%", "%", 2),
        ("CAGR", "CAGR_%", "%", 2),
        ("Max Drawdown", "Max_Drawdown_%", "%", 2),
        ("Total Trades", "Total_Trades", "", 0),
        ("Win Rate", "Win_Rate_%", "%", 2),
        ("Avg Win", "Avg_Win_%", "%", 2),
        ("Avg Loss", "Avg_Loss_%", "%", 2),
    ]

    print(
        f"\n{'Metric':<25} {'Biased (Original)':<25} {'Unbiased (2020)':<25} {'Difference':<20}"
    )
    print("-" * 100)

    for name, key, unit, decimals in metrics:
        biased_val = biased.get(key, 0)
        unbiased_val = unbiased.get(key, 0)

        if unit == "$":
            biased_str = f"${biased_val:,.{decimals}f}"
            unbiased_str = f"${unbiased_val:,.{decimals}f}"
            diff = biased_val - unbiased_val
            diff_str = f"${diff:+,.{decimals}f}" if name != "Starting Capital" else "-"
        elif unit == "%":
            biased_str = f"{biased_val:.{decimals}f}%"
            unbiased_str = f"{unbiased_val:.{decimals}f}%"
            diff = biased_val - unbiased_val
            diff_str = f"{diff:+.{decimals}f}%" if name != "Starting Capital" else "-"
        else:
            biased_str = f"{int(biased_val)}"
            unbiased_str = f"{int(unbiased_val)}"
            diff = biased_val - unbiased_val
            diff_str = f"{diff:+.0f}" if name != "Starting Capital" else "-"

        print(f"{name:<25} {biased_str:<25} {unbiased_str:<25} {diff_str:<20}")

    # Bias impact analysis
    print("\n\n🎯 BIAS IMPACT ANALYSIS")
    print("=" * 100)

    cagr_biased = biased.get("CAGR_%", 0)
    cagr_unbiased = unbiased.get("CAGR_%", 0)
    cagr_diff = cagr_biased - cagr_unbiased
    bias_pct = (cagr_diff / cagr_biased * 100) if cagr_biased > 0 else 0

    print(f"\n📊 CAGR Impact:")
    print(f"   Biased CAGR:     {cagr_biased:.2f}%")
    print(f"   Unbiased CAGR:   {cagr_unbiased:.2f}%")
    print(f"   Inflation:       {cagr_diff:+.2f}% ({bias_pct:.1f}% overstatement)")

    if cagr_diff > 15:
        severity = "🔴 SEVERE"
        conclusion = (
            "Original backtest was heavily biased. Unbiased CAGR is more realistic."
        )
    elif cagr_diff > 8:
        severity = "🟡 MODERATE"
        conclusion = (
            "Original backtest had moderate bias. Unbiased CAGR is more reliable."
        )
    else:
        severity = "🟢 MINOR"
        conclusion = (
            "Original backtest was relatively clean. Both results are reasonable."
        )

    print(f"\n   Bias Severity:   {severity}")
    print(f"   Conclusion:      {conclusion}")

    # Forward expectations
    print("\n\n🔮 FORWARD TESTING EXPECTATIONS (2026+)")
    print("=" * 100)

    print(f"\n❌ DON'T expect {cagr_biased:.1f}% CAGR (biased result)")
    print(f"✅ DO expect ~{cagr_unbiased:.1f}% CAGR (unbiased result)")

    if cagr_unbiased > 20:
        assessment = "Excellent (2-3X market)"
    elif cagr_unbiased > 15:
        assessment = "Good (1.5-2X market)"
    elif cagr_unbiased > 10:
        assessment = "Moderate (1-1.5X market)"
    else:
        assessment = "Poor (below market)"

    print(f"\nRealistic Assessment: {assessment}")

    # Comparison with market
    sp500_cagr = 14.0  # Approximate S&P 500 2021-2025

    print(f"\n📊 vs S&P 500 (2021-2025 ~{sp500_cagr}% CAGR):")
    print(
        f"   Biased outperformance:   {cagr_biased - sp500_cagr:+.1f}% ({cagr_biased/sp500_cagr:.1f}X)"
    )
    print(
        f"   Unbiased outperformance: {cagr_unbiased - sp500_cagr:+.1f}% ({cagr_unbiased/sp500_cagr:.1f}X)"
    )

    # Universe comparison
    print("\n\n📋 UNIVERSE COMPARISON")
    print("=" * 100)

    biased_trades_file = biased_file.parent / biased_file.name.replace(
        "summary_", "trades_"
    )
    unbiased_trades_file = unbiased_file.parent / unbiased_file.name.replace(
        "summary_", "trades_"
    )

    if biased_trades_file.exists() and unbiased_trades_file.exists():
        df_biased_trades = pd.read_csv(biased_trades_file)
        df_unbiased_trades = pd.read_csv(unbiased_trades_file)

        biased_tickers = set(df_biased_trades["Ticker"].unique())
        unbiased_tickers = set(df_unbiased_trades["Ticker"].unique())

        common = biased_tickers & unbiased_tickers
        biased_only = biased_tickers - unbiased_tickers
        unbiased_only = unbiased_tickers - biased_tickers

        print(f"\n🔄 Stock Overlap:")
        print(f"   Common to both:     {len(common)} stocks - {sorted(common)[:10]}...")
        print(
            f"   Biased only:        {len(biased_only)} stocks - {sorted(biased_only)[:10]}..."
        )
        print(
            f"   Unbiased only:      {len(unbiased_only)} stocks - {sorted(unbiased_only)[:10]}..."
        )

        # Check for SMCI (the problematic mega-winner)
        if "SMCI" in biased_only:
            print(f"\n   ⚠️  SMCI (biased mega-winner) NOT in unbiased universe")
            print(
                f"       Reason: SMCI added to S&P 500 in March 2024 (unavailable Jan 2021)"
            )

    # Action items
    print("\n\n✅ RECOMMENDATIONS")
    print("=" * 100)

    print("\n1. Use UNBIASED results for forward testing expectations")
    print(
        f"   → Expect ~{cagr_unbiased:.1f}% CAGR going forward (not {cagr_biased:.1f}%)"
    )

    print("\n2. Update strategy documentation")
    print("   → Replace biased metrics in notebook and docs")

    print("\n3. Continue forward testing with realistic expectations")
    print(
        f"   → If you achieve {cagr_unbiased-5:.1f}%-{cagr_unbiased+5:.1f}% CAGR, you're on track"
    )

    print("\n4. Re-screen annually using PREVIOUS YEAR data only")
    print("   → Dec 2026: Screen using 2026 data, select for 2027+")
    print("   → Maintain unbiased methodology")

    print("\n\n" + "=" * 100)
    print(f"📊 Biased backtest:   {biased_file.name}")
    print(f"📊 Unbiased backtest: {unbiased_file.name}")
    print("=" * 100)


if __name__ == "__main__":
    compare_results()
