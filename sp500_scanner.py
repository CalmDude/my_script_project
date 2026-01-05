"""
S&P 500 Scanner - Find stocks with FULL HOLD + ADD signal
Scans all S&P 500 stocks for strongest bullish alignment (weekly P1 + daily P1)
Only outputs stocks with "FULL HOLD + ADD" signal
"""

import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from technical_analysis import analyze_ticker
from datetime import datetime
import yfinance as yf

def get_sp500_tickers():
    """Fetch current S&P 500 ticker list from Wikipedia"""
    import urllib.request

    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

    # Add user agent to avoid 403 Forbidden
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        with urllib.request.urlopen(req) as response:
            tables = pd.read_html(response)
            sp500_table = tables[0]
            tickers = sp500_table['Symbol'].tolist()

            # Clean up tickers (some have special characters)
            tickers = [t.replace('.', '-') for t in tickers]
            print(f"✓ Loaded {len(tickers)} S&P 500 tickers\n")
            return tickers
    except Exception as e:
        print(f"❌ Error fetching S&P 500 list: {e}")
        print("Using fallback list of major stocks...")
        # Fallback to major stocks if Wikipedia fails
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
                'UNH', 'JNJ', 'XOM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
                'PEP', 'COST']

def scan_sp500(daily_bars=60, weekly_bars=52, concurrency=10):
    """
    Scan all S&P 500 stocks for buy opportunities

    Args:
        daily_bars: Number of daily bars to analyze
        weekly_bars: Number of weekly bars to analyze
        concurrency: Number of concurrent API requests

    Returns:
        DataFrame with results sorted by signal strength
    """
    print("Fetching S&P 500 ticker list...")
    tickers = get_sp500_tickers()
    print(f"Found {len(tickers)} S&P 500 stocks\n")

    results = []
    buy_signals = []  # Track FULL HOLD + ADD signals
    total = len(tickers)
    completed = 0

    print(f"🔍 Scanning {total} stocks for 'FULL HOLD + ADD' signals...")
    print(f"Parameters: {daily_bars} daily bars, {weekly_bars} weekly bars, {concurrency} threads")
    print("=" * 80)

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        # Submit all jobs
        future_to_ticker = {
            executor.submit(analyze_ticker, ticker, daily_bars, weekly_bars): ticker
            for ticker in tickers
        }

        # Process results as they complete
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            completed += 1

            try:
                result = future.result()

                if 'error' not in result:
                    results.append(result)
                    signal = result.get('signal', 'N/A')

                    # Only print FULL HOLD + ADD signals
                    if signal == 'FULL HOLD + ADD':
                        price = result.get('current_price', 0)
                        print(f"✓ [{completed}/{total}] {ticker:6s} -> {signal:20s} ${price:.2f}")
                        buy_signals.append(result)
                    elif completed % 50 == 0:  # Progress update
                        print(f"  [{completed}/{total}] Scanning...")

            except Exception as e:
                if completed % 50 == 0:
                    print(f"  [{completed}/{total}] Scanning...")

    print("=" * 80)
    print(f"\n✓ Scan complete: {len(results)} analyzed, {len(buy_signals)} FULL HOLD + ADD signals found\n")

    # Convert to DataFrame
    if not results:
        print("No results found.")
        return pd.DataFrame()

    df = pd.DataFrame(results)
    return df

def filter_buy_signals(df, signal='FULL HOLD + ADD'):
    """Filter for FULL HOLD + ADD signals (strongest bullish alignment)"""
    if df.empty:
        return df
    return df[df['signal'] == signal].sort_values('ticker')

def cleanup_old_scans(results_dir, max_files=7):
    """
    Keep only the 7 most recent scan files, move older ones to archive
    """
    archive_dir = results_dir / 'archive'
    archive_dir.mkdir(exist_ok=True)

    # Get all xlsx files in results directory (not archive)
    scan_files = sorted(results_dir.glob('sp500_analysis_*.xlsx'), key=lambda p: p.stat().st_mtime, reverse=True)

    # Move files beyond max_files to archive
    for old_file in scan_files[max_files:]:
        archive_path = archive_dir / old_file.name
        old_file.rename(archive_path)
        print(f"  Archived: {old_file.name}")

def create_excel_output(buy_df, output_file):
    """
    Create Excel workbook with 4 sheets: All, Balanced, Extended, Weak
    All fields included, sorted alphabetically by ticker
    """
    if buy_df.empty:
        print("No data to export to Excel")
        return

    # Define column order (all technical fields)
    columns = [
        'ticker', 'signal', 'current_price', 'confluence', 'recommendation',
        'd20', 'd50', 'd100', 'd200',
        'w10', 'w20', 'w50', 'w200',
        'daily_poc', 'daily_val', 'daily_vah',
        's1', 's2', 's3',
        'r1', 'r2', 'r3',
        'notes'
    ]

    # Keep only columns that exist in the dataframe
    available_cols = [col for col in columns if col in buy_df.columns]

    # Sort alphabetically by ticker
    buy_df = buy_df.sort_values('ticker')

    # Filter by confluence
    df_balanced = buy_df[buy_df['confluence'] == 'BALANCED'][available_cols].copy()
    df_extended = buy_df[buy_df['confluence'] == 'EXTENDED'][available_cols].copy()
    df_weak = buy_df[buy_df['confluence'] == 'WEAK'][available_cols].copy()
    df_all = buy_df[available_cols].copy()

    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: All (overview)
        df_all.to_excel(writer, sheet_name='All', index=False)

        # Sheet 2: Balanced (priority buys)
        df_balanced.to_excel(writer, sheet_name='Balanced', index=False)

        # Sheet 3: Extended (watch list)
        df_extended.to_excel(writer, sheet_name='Extended', index=False)

        # Sheet 4: Weak (skip list)
        df_weak.to_excel(writer, sheet_name='Weak', index=False)

        # Auto-adjust column widths for all sheets
        for sheet_name in ['All', 'Balanced', 'Extended', 'Weak']:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

    print(f"✓ Excel file created: {output_file}")
    print(f"  - All: {len(df_all)} stocks")
    print(f"  - Balanced: {len(df_balanced)} stocks")
    print(f"  - Extended: {len(df_extended)} stocks")
    print(f"  - Weak: {len(df_weak)} stocks")

if __name__ == '__main__':
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Scan S&P 500 for FULL HOLD + ADD stocks')
    parser.add_argument('--daily-bars', type=int, default=60, help='Daily bars (default: 60)')
    parser.add_argument('--weekly-bars', type=int, default=52, help='Weekly bars (default: 52)')
    parser.add_argument('--concurrency', type=int, default=10, help='Threads (default: 10)')
    parser.add_argument('--test', type=int, help='Test mode: scan only first N tickers')

    args = parser.parse_args()

    # Run scan
    start_time = datetime.now()
    results_df = scan_sp500(args.daily_bars, args.weekly_bars, args.concurrency)
    elapsed = (datetime.now() - start_time).total_seconds()

    if not results_df.empty:
        # Filter for FULL HOLD + ADD only
        buy_df = filter_buy_signals(results_df, 'FULL HOLD + ADD')

        print(f"{'='*80}")
        print(f"🎯 FULL HOLD + ADD SIGNALS: {len(buy_df)} stocks")
        print(f"{'='*80}\n")

        if not buy_df.empty:
            # Display summary by confluence
            print("📊 Breakdown by Confluence:")
            confluence_counts = buy_df['confluence'].value_counts()
            for conf, count in confluence_counts.items():
                print(f"  {conf:12s}: {count:3d} stocks")
            print()

            # Save to workspace scanner_results folder
            results_dir = Path.cwd() / 'scanner_results'
            results_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            output_path = results_dir / f'sp500_analysis_{timestamp}.xlsx'

            create_excel_output(buy_df, output_path)
            print(f"\n✓ Results saved to: {output_path}")

            # Cleanup old scans (keep 7 most recent, archive rest)
            print("\n📁 Managing scan history...")
            cleanup_old_scans(results_dir, max_files=7)

            # Display top 10 BALANCED stocks
            balanced = buy_df[buy_df['confluence'] == 'BALANCED'].head(10)
            if not balanced.empty:
                print(f"\n🎯 Top 10 BALANCED Stocks (Priority Buys):")
                display_cols = ['ticker', 'current_price', 'd50', 'd200', 'w10', 'w200']
                available_cols = [col for col in display_cols if col in balanced.columns]
                print(balanced[available_cols].to_string(index=False))
        else:
            print("No FULL HOLD + ADD signals found.\n")

        # Summary
        print(f"\n⏱️  Total time: {elapsed:.1f}s")
        print(f"📊 Overall signal distribution:")
        print(results_df['signal'].value_counts().to_string())
    else:
        print("No results found.")
