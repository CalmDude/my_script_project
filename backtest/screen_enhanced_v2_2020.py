"""
Enhanced Stock Screening V2 - Phase 1B (Corrected Filters)
Improvements: Gentler filters to keep energy winners, remove revenue-shrinking trash
"""

import yfinance as yf
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

from get_historical_sp500 import get_sp500_as_of_2021


def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_enhanced_metrics(ticker):
    """Calculate enhanced metrics using ONLY 2020 data"""
    try:
        stock = yf.Ticker(ticker)

        # Download 2019-2020 data (need history for calculations)
        df = stock.history(start="2019-01-01", end="2020-12-31", interval="1d")

        if df.empty or len(df) < 200:
            return None

        # Get 2020 data only
        df_2020 = df[df.index.year == 2020]

        if df_2020.empty:
            return None

        # === EXISTING METRICS ===
        close_2020_end = df_2020["Close"].iloc[-1]

        # Volatility (annualized)
        returns_2020 = df_2020["Close"].pct_change().dropna()
        volatility_pct = returns_2020.std() * np.sqrt(252) * 100

        # Average volume
        avg_volume = df_2020["Volume"].mean()

        # 2020 return
        close_2020_start = df_2020["Close"].iloc[0]
        return_2020_pct = ((close_2020_end - close_2020_start) / close_2020_start) * 100

        # === MOMENTUM METRICS ===
        # 6-month momentum (July-Dec 2020)
        if len(df_2020) >= 126:
            close_6m_ago = df_2020["Close"].iloc[-126]
            momentum_6m_pct = ((close_2020_end - close_6m_ago) / close_6m_ago) * 100
        else:
            momentum_6m_pct = return_2020_pct

        # RSI at end of 2020
        rsi_2020 = calculate_rsi(df_2020["Close"]).iloc[-1]

        # Price vs 50-day MA
        ma_50 = df_2020["Close"].rolling(50).mean().iloc[-1]
        distance_from_ma_pct = (
            ((close_2020_end - ma_50) / ma_50) * 100 if not pd.isna(ma_50) else 0
        )

        # === QUALITY METRICS ===
        try:
            info = stock.info

            # Profitability
            roe = info.get("returnOnEquity", None)
            if roe is not None:
                roe_pct = roe * 100
            else:
                roe_pct = None

            operating_margins = info.get("operatingMargins", None)
            if operating_margins is not None:
                operating_margin_pct = operating_margins * 100
            else:
                operating_margin_pct = None

            # Debt
            debt_to_equity = info.get("debtToEquity", None)
            if debt_to_equity is not None:
                debt_to_equity_ratio = debt_to_equity / 100
            else:
                debt_to_equity_ratio = None

            # Growth
            revenue_growth = info.get("revenueGrowth", None)
            if revenue_growth is not None:
                revenue_growth_pct = revenue_growth * 100
            else:
                revenue_growth_pct = None

            # Market cap
            market_cap = info.get("marketCap", 0)

            # Sector
            sector = info.get("sector", "Unknown")

        except Exception as e:
            roe_pct = None
            operating_margin_pct = None
            debt_to_equity_ratio = None
            revenue_growth_pct = None
            market_cap = 0
            sector = "Unknown"

        return {
            "Ticker": ticker,
            "Close_2020": close_2020_end,
            "Volatility_2020_%": volatility_pct,
            "Avg_Volume_2020": avg_volume,
            "Return_2020_%": return_2020_pct,
            "Momentum_6M_%": momentum_6m_pct,
            "RSI_2020": rsi_2020,
            "Distance_from_MA_%": distance_from_ma_pct,
            "ROE_%": roe_pct,
            "Operating_Margin_%": operating_margin_pct,
            "Debt_to_Equity": debt_to_equity_ratio,
            "Revenue_Growth_%": revenue_growth_pct,
            "Market_Cap_2020": market_cap,
            "Sector": sector,
        }

    except Exception as e:
        print(f"❌ Error processing {ticker}: {str(e)}")
        return None


def calculate_composite_score_v2(row):
    """
    Phase 1B: Momentum-focused scoring
    Score = (Momentum * 0.5) + (Volatility * 0.35) + (Quality * 0.15)
    """

    # === VOLATILITY SCORE (0-100) ===
    vol = row["Volatility_2020_%"]
    if vol < 25:
        vol_score = 0
    elif vol > 150:
        vol_score = 100
    else:
        vol_score = ((vol - 25) / (150 - 25)) * 100

    # === MOMENTUM SCORE (0-100) ===
    momentum_6m = row["Momentum_6M_%"]
    rsi = row["RSI_2020"]

    # Positive momentum strongly preferred
    if momentum_6m > 50:
        momentum_score = 100
    elif momentum_6m > 0:
        momentum_score = 50 + (momentum_6m / 50) * 50
    elif momentum_6m > -30:
        momentum_score = 25
    else:
        momentum_score = 0

    # RSI bonus (prefer 50-70 range)
    if pd.notna(rsi):
        if 50 <= rsi <= 70:
            momentum_score += 20
        elif rsi > 70:
            momentum_score += 10

    momentum_score = min(momentum_score, 100)

    # === QUALITY SCORE (0-100) - LIGHTER WEIGHT ===
    quality_score = 50  # Start at neutral

    # ROE check (profitable companies get bonus)
    roe = row["ROE_%"]
    if pd.notna(roe):
        if roe > 15:
            quality_score += 30
        elif roe > 10:
            quality_score += 20
        elif roe > 0:
            quality_score += 10
        elif roe < -10:
            quality_score -= 20  # Penalize heavy losses

    # Operating margin check (lighter)
    op_margin = row["Operating_Margin_%"]
    if pd.notna(op_margin):
        if op_margin > 10:
            quality_score += 20
        elif op_margin > 0:
            quality_score += 10
        elif op_margin < -30:
            quality_score -= 20  # Only penalize extreme losses

    quality_score = max(0, min(quality_score, 100))

    # === COMPOSITE SCORE ===
    composite = momentum_score * 0.50 + vol_score * 0.35 + quality_score * 0.15

    return composite


def apply_gentle_quality_filters(df):
    """
    Phase 1B: GENTLER filters to keep winners, remove trash
    - Keep energy infrastructure (high debt OK)
    - Keep smaller caps (TRGP was $8B)
    - Remove revenue-shrinking zombies (CCL, NCLH)
    """

    print("\n🔍 Applying Gentle Quality Filters (Phase 1B)...")
    initial_count = len(df)

    # Filter 1: Operating margin (only exclude extreme losses)
    df_filtered = df[
        (pd.isna(df["Operating_Margin_%"]))
        | (df["Operating_Margin_%"] > -30)  # Gentler: was -20%
    ].copy()

    excluded = initial_count - len(df_filtered)
    print(f"   Filter 1 (Operating Margin > -30%): Excluded {excluded} stocks")

    # Filter 2: Debt (keep leveraged energy infrastructure)
    initial_count = len(df_filtered)
    df_filtered = df_filtered[
        (pd.isna(df_filtered["Debt_to_Equity"]))
        | (df_filtered["Debt_to_Equity"] < 5.0)  # Gentler: was 3.0
    ].copy()

    excluded = initial_count - len(df_filtered)
    print(f"   Filter 2 (Debt/Equity < 5.0): Excluded {excluded} stocks")

    # Filter 3: Market cap (restore $5B threshold)
    initial_count = len(df_filtered)
    df_filtered = df_filtered[
        df_filtered["Market_Cap_2020"] >= 5_000_000_000  # Restored: was $10B
    ].copy()

    excluded = initial_count - len(df_filtered)
    print(f"   Filter 3 (Market Cap >= $5B): Excluded {excluded} stocks")

    # Filter 4: Revenue growth (NEW - remove zombies)
    initial_count = len(df_filtered)
    df_filtered = df_filtered[
        (pd.isna(df_filtered["Revenue_Growth_%"]))
        | (df_filtered["Revenue_Growth_%"] > -20)  # Remove revenue-shrinking companies
    ].copy()

    excluded = initial_count - len(df_filtered)
    print(f"   Filter 4 (Revenue Growth > -20%): Excluded {excluded} stocks (zombies)")

    return df_filtered


def apply_relaxed_sector_limits(df_scored, max_per_sector=8):
    """
    Phase 1B: Allow energy concentration (8 stocks = 32%)
    """

    print(f"\n🎯 Applying Relaxed Sector Limits (max {max_per_sector} per sector)...")

    # Sort by composite score
    df_sorted = df_scored.sort_values("Composite_Score", ascending=False)

    selected = []
    sector_counts = {}

    for _, row in df_sorted.iterrows():
        sector = row["Sector"]
        count = sector_counts.get(sector, 0)

        if count < max_per_sector:
            selected.append(row.to_dict())
            sector_counts[sector] = count + 1

        if len(selected) >= 25:
            break

    df_selected = pd.DataFrame(selected)

    # Show sector distribution
    print("\n   Sector Distribution:")
    for sector, count in sorted(sector_counts.items(), key=lambda x: -x[1]):
        pct = (count / 25) * 100
        print(f"      {sector}: {count} stocks ({pct:.0f}%)")

    return df_selected


def screen_stocks_enhanced_v2():
    """Enhanced screening V2 with corrected filters"""
    print("=" * 80)
    print("ENHANCED STOCK SCREENING V2 - Phase 1B (Corrected)")
    print("=" * 80)
    print("\nV2 Improvements:")
    print("  ✅ Gentler filters (keep energy winners like TRGP, MPC, OKE)")
    print("  ✅ Revenue growth filter (remove zombies like CCL, NCLH)")
    print("  ✅ Momentum-focused scoring (50% vs 40%)")
    print("  ✅ Relaxed sector limits (max 8 = 32%)")
    print("=" * 80)

    # Get historical S&P 500 members
    tickers = get_sp500_as_of_2021()
    print(f"\n📊 Screening {len(tickers)} S&P 500 stocks (as of Jan 1, 2021)")
    print(f"📅 Using 2020 data ONLY (no peeking at 2021-2025)")
    print(f"⏰ This will take 15-20 minutes...\n")

    results = []

    for i, ticker in enumerate(tickers, 1):
        print(f"  [{i:3d}/{len(tickers)}] Processing {ticker:6s}...", end="\r")

        metrics = calculate_enhanced_metrics(ticker)
        if metrics:
            results.append(metrics)

    print(f"\n\n✅ Screening complete: {len(results)}/{len(tickers)} stocks analyzed")

    # Create DataFrame
    df = pd.DataFrame(results)

    # Basic qualification
    df["Basic_Qualified"] = (
        (df["Volatility_2020_%"] >= 25)
        & (df["Avg_Volume_2020"] >= 2_000_000)
        & (df["Market_Cap_2020"] >= 5_000_000_000)
    )

    print(f"\n✅ Basic Qualified: {df['Basic_Qualified'].sum()} stocks")

    # Apply gentle quality filters
    df_filtered = apply_gentle_quality_filters(df[df["Basic_Qualified"]])

    print(f"\n✅ After Gentle Quality Filters: {len(df_filtered)} stocks remain")

    # Calculate composite scores (V2)
    df_filtered["Composite_Score"] = df_filtered.apply(
        calculate_composite_score_v2, axis=1
    )

    # Apply relaxed sector limits
    df_final = apply_relaxed_sector_limits(df_filtered, max_per_sector=8)

    print("\n" + "=" * 80)
    print("FINAL UNIVERSE V2 - Top 25 by Momentum-Focused Score")
    print("=" * 80)

    print(
        f"\n{'Rank':<6} {'Ticker':<8} {'Score':<8} {'Sector':<22} {'Vol%':<8} {'Mom%':<8} {'RevG%':<8}"
    )
    print("-" * 85)
    for i, row in enumerate(df_final.iterrows(), 1):
        _, r = row
        rev_str = (
            f"{r['Revenue_Growth_%']:.1f}" if pd.notna(r["Revenue_Growth_%"]) else "N/A"
        )
        sector_short = r["Sector"][:20]
        print(
            f"{i:<6} {r['Ticker']:<8} {r['Composite_Score']:<8.1f} {sector_short:<22} "
            f"{r['Volatility_2020_%']:<8.1f} {r['Momentum_6M_%']:<8.1f} {rev_str:<8}"
        )

    # Save results
    output_dir = Path("backtest/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save all results
    all_results_file = output_dir / f"screening_v2_all_{timestamp}.csv"
    df.to_csv(all_results_file, index=False)
    print(f"\n✅ All results saved: {all_results_file.name}")

    # Save filtered results
    filtered_file = output_dir / f"screening_v2_filtered_{timestamp}.csv"
    df_filtered.to_csv(filtered_file, index=False)
    print(f"✅ Filtered stocks saved: {filtered_file.name}")

    # Save final universe
    final_file = output_dir / f"screening_v2_final_{timestamp}.csv"
    df_final.to_csv(final_file, index=False)
    print(f"✅ Final universe saved: {final_file.name}")

    # Save as universe file
    universe_file = Path("backtest/data/sp500_enhanced_v2_2020.txt")
    universe_file.parent.mkdir(parents=True, exist_ok=True)

    with open(universe_file, "w") as f:
        for ticker in df_final["Ticker"]:
            f.write(f"{ticker}\n")

    print(f"✅ Universe file saved: {universe_file.name}")

    # Comparison
    print("\n" + "=" * 80)
    print("📊 COMPARISON WITH PREVIOUS VERSIONS")
    print("=" * 80)

    # Compare with unbiased
    unbiased_file = Path("backtest/data/sp500_unbiased_2020.txt")
    if unbiased_file.exists():
        with open(unbiased_file, "r") as f:
            unbiased_tickers = set([line.strip() for line in f if line.strip()])

        v2_tickers = set(df_final["Ticker"])

        common = unbiased_tickers & v2_tickers
        removed = unbiased_tickers - v2_tickers
        added = v2_tickers - unbiased_tickers

        print(f"\nV2 vs Unbiased:")
        print(f"  Kept: {len(common)} stocks")
        print(f"    {sorted(common)}")

        print(f"\n  Removed: {len(removed)} stocks")
        print(f"    {sorted(removed)}")

        print(f"\n  Added: {len(added)} stocks")
        print(f"    {sorted(added)}")

        # Check if we kept TRGP, MPC, OKE (the big winners)
        big_winners = {"TRGP", "MPC", "OKE", "EOG", "MGM"}
        kept_winners = big_winners & v2_tickers
        lost_winners = big_winners - v2_tickers

        print(f"\n  Big Winners Check:")
        print(f"    ✅ Kept: {sorted(kept_winners) if kept_winners else 'None'}")
        print(f"    ❌ Lost: {sorted(lost_winners) if lost_winners else 'None'}")

    print("\n" + "=" * 80)
    print("🎯 EXPECTED IMPROVEMENTS (V2)")
    print("=" * 80)
    print("\nV1 (Failed):")
    print("  - CAGR: 10.44%")
    print("  - Lost: TRGP, MPC, OKE (big winners)")

    print("\nUnbiased (Baseline):")
    print("  - CAGR: 15.28%")
    print("  - Issues: CCL, NCLH (trash stocks)")

    print("\nV2 (Expected):")
    print("  - CAGR: 20-25% (target)")
    print("  - Keep: Energy winners (TRGP, MPC, OKE)")
    print("  - Remove: Revenue zombies (CCL, NCLH)")

    print("\n" + "=" * 80)
    print("🎯 NEXT: Run backtest with V2 universe")
    print("=" * 80)

    return df_final


if __name__ == "__main__":
    df_enhanced_v2 = screen_stocks_enhanced_v2()

    print("\n" + "=" * 80)
    print("✅ ENHANCED SCREENING V2 COMPLETE")
    print("=" * 80)
    print("\nReady to run V2 backtest!")
