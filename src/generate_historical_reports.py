"""
Historical Scanner Report Generator

Generates scanner reports for historical dates to build backtest data.
Uses only data available as-of each historical date (no look-ahead bias).

RATE LIMITING WARNING:
- Historical scans bypass cache (need fresh data for each date)
- Default concurrency=2 with 1-2s delays is safe
- NASDAQ 100 (~100 stocks) recommended for testing vs S&P 500 (~500 stocks)
- Expect ~100 stocks × 26 weeks = 2,600 API calls for 6 months
- If rate limited, wait 1 hour and resume with later --start date

Usage:
    # Test with NASDAQ 100 (recommended)
    python generate_historical_reports.py --start 2025-07-01 --end 2026-01-01 --interval 7 --category nasdaq100

    # Conservative: 3 months only
    python generate_historical_reports.py --start 2025-10-01 --category nasdaq100
"""

import argparse
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

from full_scanner import (
    get_sp500_tickers,
    get_nasdaq100_tickers,
    get_portfolio_tickers,
    scan_stocks,
    filter_buy_signals,
    filter_sell_signals,
    create_best_trades_excel,
    create_best_trades_pdf,
    analyze_market_regime,
)


def generate_historical_report(
    tickers,
    as_of_date,
    category,
    results_dir,
    daily_bars=60,
    weekly_bars=52,
    concurrency=2,
    use_cache=False,
):
    """
    Generate a scanner report as-of a historical date

    Args:
        tickers: List of tickers to scan
        as_of_date: Date to generate report for (uses only data up to this date)
        category: Category name (S&P 500, NASDAQ 100, Portfolio)
        results_dir: Directory to save results
        daily_bars: Number of daily bars
        weekly_bars: Number of weekly bars
        concurrency: Parallel workers (default 2, reduce to 1 if rate limited)
        use_cache: If True, uses cached data (for regenerating reports with new format)

    Rate Limiting:
        - Cache doesn't help (need fresh data per date) unless use_cache=True
        - Each ticker = 2-3 API calls (daily + weekly data)
        - 100 tickers × 3 calls = 300 API calls per report
        - With 1-2s delays and concurrency=2, expect ~2-5 min per report
    """
    print(f"\n{'='*80}")
    print(f"Generating Historical Report: {category}")
    print(f"As-of Date: {as_of_date.strftime('%Y-%m-%d')}")
    print(f"{'='*80}")

    # Create timestamp for filename
    timestamp = as_of_date.strftime("%Y%m%d_0900")

    # Analyze market regime first (mandatory for filtering)
    regime = analyze_market_regime(
        daily_bars=daily_bars,
        weekly_bars=weekly_bars,
        as_of_date=as_of_date.strftime("%Y-%m-%d") if not use_cache else None,
    )

    # Run scan with date limit
    if use_cache:
        print(f"\nScanning {len(tickers)} tickers (using cached data)...")
    else:
        print(
            f"\nScanning {len(tickers)} tickers (data up to {as_of_date.strftime('%Y-%m-%d')})..."
        )

    # Pass as_of_date and regime to scan_stocks (skip as_of_date if using cache)
    results = scan_stocks(
        tickers,
        category=category,
        daily_bars=daily_bars,
        weekly_bars=weekly_bars,
        concurrency=concurrency,
        as_of_date=as_of_date.strftime("%Y-%m-%d") if not use_cache else None,
        regime=regime,
    )

    if results.empty:
        print(f"[WARN] No results for {category} on {as_of_date.strftime('%Y-%m-%d')}")
        return

    # Filter signals with regime
    buy_signals = filter_buy_signals(
        results, "FULL HOLD + ADD", quality_filter=True, regime=regime
    )
    sell_signals = filter_sell_signals(results, quality_filter=False)

    print(f"\n[OK] {len(buy_signals)} buy signals, {len(sell_signals)} sell signals")

    if buy_signals.empty and sell_signals.empty:
        print(
            f"[WARN] No quality signals for {category} on {as_of_date.strftime('%Y-%m-%d')}"
        )
        return

    # Create category subfolder
    category_folder = category.lower().replace(" ", "").replace("&", "")
    output_dir = results_dir / category_folder
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate watchlist reports
    xlsx_file = output_dir / f"{category_folder}_watchlist_{timestamp}.xlsx"
    pdf_file = output_dir / f"{category_folder}_watchlist_{timestamp}.pdf"

    create_best_trades_excel(buy_signals, sell_signals, xlsx_file, category=category)
    create_best_trades_pdf(
        buy_signals, sell_signals, pdf_file, category=category, regime=regime
    )

    print(f"\n[OK] Reports saved:")
    print(f"  Excel: {xlsx_file.name}")
    print(f"  PDF: {pdf_file.name}")


def generate_date_range(start_date, end_date, interval_days=7):
    """
    Generate list of dates between start and end

    Args:
        start_date: Start date
        end_date: End date
        interval_days: Days between each date

    Returns:
        List of datetime objects
    """
    dates = []
    current = start_date

    while current <= end_date:
        dates.append(current)
        current += timedelta(days=interval_days)

    return dates


def main():
    parser = argparse.ArgumentParser(
        description="Generate historical scanner reports for backtesting"
    )
    parser.add_argument(
        "--start",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end",
        type=str,
        default=None,
        help="End date (YYYY-MM-DD), defaults to today",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=7,
        help="Days between reports (default: 7)",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="nasdaq100",
        choices=["sp500", "nasdaq100", "portfolio", "all"],
        help="Category to scan (default: nasdaq100 - recommended for testing)",
    )
    parser.add_argument(
        "--daily-bars",
        type=int,
        default=60,
        help="Daily bars for analysis (default: 60)",
    )
    parser.add_argument(
        "--weekly-bars",
        type=int,
        default=52,
        help="Weekly bars for analysis (default: 52)",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=1,
        help="Parallel workers (default: 1 for safety, use 2 if no rate limit issues)",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="Use cached data instead of fetching fresh (for regenerating reports with new format)",
    )

    args = parser.parse_args()

    # Parse dates
    start_date = datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.strptime(args.end, "%Y-%m-%d") if args.end else datetime.now()

    if start_date > end_date:
        print("[ERROR] Start date must be before end date")
        return

    # Generate date range
    dates = generate_date_range(start_date, end_date, args.interval)

    print(f"\n{'='*80}")
    print(f"HISTORICAL REPORT GENERATION")
    print(f"{'='*80}")
    print(f"Start Date: {start_date.strftime('%Y-%m-%d')}")
    print(f"End Date: {end_date.strftime('%Y-%m-%d')}")
    print(f"Interval: {args.interval} days")
    print(f"Total Reports: {len(dates)}")
    print(f"Category: {args.category}")
    print(f"Concurrency: {args.concurrency} workers")

    # Setup results directory
    results_dir = Path("scanner_results") / "historical_simulation"
    if not args.use_cache:
        print(f"\n{'='*80}")
        print(f"RATE LIMITING INFO")
        print(f"{'='*80}")
        if args.category == "nasdaq100":
            ticker_est = 100
        elif args.category == "sp500":
            ticker_est = 500
        elif args.category == "portfolio":
            ticker_est = 20
        else:  # all
            ticker_est = 620

        total_calls = ticker_est * len(dates) * 2  # 2 calls per ticker (daily + weekly)
        print(
            f"Estimated API calls: ~{total_calls:,} ({ticker_est} tickers × {len(dates)} dates × 2)"
        )
        print(f"Estimated time: ~{len(dates) * 2}-{len(dates) * 5} minutes")
        print(
            f"Rate limit strategy: {args.concurrency} concurrent workers + 1-2s random delays"
        )
        print(f"\nIf rate limited:")
        print(f"  1. Wait 1 hour")
        print(
            f"  2. Resume with --start {dates[len(dates)//2].strftime('%Y-%m-%d')} (skip completed dates)"
        )
        print(f"  3. Or reduce --concurrency to 1")
    else:
        print(f"\n{'='*80}")
        print(f"USING CACHED DATA - FAST REGENERATION MODE")
        print(f"{'='*80}")
        print(f"This will regenerate reports with new format using cached data.")
        print(
            f"Estimated time: ~{len(dates) * 0.5}-{len(dates) * 2} minutes (much faster!)"
        )

    # Determine which categories to scan
    categories = []
    if args.category == "all":
        categories = ["sp500", "nasdaq100", "portfolio"]
    else:
        categories = [args.category]

    # Generate reports for each date
    for i, report_date in enumerate(dates, 1):
        print(f"\n{'='*80}")
        print(f"REPORT {i}/{len(dates)} - {report_date.strftime('%Y-%m-%d')}")
        print(f"{'='*80}")

        for cat in categories:
            # Get tickers
            if cat == "sp500":
                tickers = get_sp500_tickers()
                category_name = "S&P 500"
            elif cat == "nasdaq100":
                tickers = get_nasdaq100_tickers()
                category_name = "NASDAQ 100"
            else:  # portfolio
                tickers = get_portfolio_tickers()
                category_name = "Portfolio"

            if not tickers:
                print(f"[WARN] No tickers found for {category_name}")
                continue

            try:
                generate_historical_report(
                    tickers,
                    report_date,
                    category_name,
                    results_dir,
                    args.daily_bars,
                    args.weekly_bars,
                    args.concurrency,
                    args.use_cache,
                )
            except Exception as e:
                print(f"[ERROR] Failed to generate {category_name} report: {e}")
                continue

    print(f"\n{'='*80}")
    print(f"HISTORICAL GENERATION COMPLETE")
    print(f"{'='*80}")
    print(f"Total reports generated: {len(dates) * len(categories)}")
    print(f"Output directory: {results_dir}")
    print(f"\nNext steps:")
    print(f"1. Run backtest on historical_simulation folder:")
    print(
        f"   python src/backtest_best_trades.py --results-dir scanner_results/historical_simulation"
    )
    print(f"2. Or use the backtest notebook and point to historical_simulation folder")


if __name__ == "__main__":
    main()
