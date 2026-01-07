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
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT

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
            print(f"[OK] Loaded {len(tickers)} S&P 500 tickers\n")
            return tickers
    except Exception as e:
        print(f"[X] Error fetching S&P 500 list: {e}")
        print("Using fallback list of major stocks...")
        # Fallback to major stocks if Wikipedia fails
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
                'UNH', 'JNJ', 'XOM', 'V', 'PG', 'MA', 'HD', 'CVX', 'MRK', 'ABBV',
                'PEP', 'COST']

def get_nasdaq100_tickers():
    """Fetch current NASDAQ 100 ticker list from Wikipedia"""
    import urllib.request

    url = 'https://en.wikipedia.org/wiki/Nasdaq-100'

    # Add user agent to avoid 403 Forbidden
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    try:
        with urllib.request.urlopen(req) as response:
            tables = pd.read_html(response)
            # Try different table indices and column names
            for table in tables:
                if 'Ticker' in table.columns:
                    tickers = table['Ticker'].tolist()
                    tickers = [t.replace('.', '-') for t in tickers]
                    print(f"[OK] Loaded {len(tickers)} NASDAQ 100 tickers\n")
                    return tickers
                elif 'Symbol' in table.columns:
                    tickers = table['Symbol'].tolist()
                    tickers = [t.replace('.', '-') for t in tickers]
                    print(f"[OK] Loaded {len(tickers)} NASDAQ 100 tickers\n")
                    return tickers

            # If no matching table found
            raise Exception("No table with 'Ticker' or 'Symbol' column found")
    except Exception as e:
        print(f"[X] Error fetching NASDAQ 100 list: {e}")
        print("Using fallback list of major tech stocks...")
        # Fallback to major tech stocks if Wikipedia fails
        return ['AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO',
                'COST', 'ASML', 'AMD', 'NFLX', 'PEP', 'ADBE', 'CSCO', 'TMUS', 'CMCSA',
                'INTC', 'TXN', 'QCOM', 'INTU', 'HON', 'AMAT', 'AMGN', 'BKNG', 'ADP',
                'ISRG', 'VRTX', 'SBUX', 'GILD', 'ADI', 'REGN', 'LRCX', 'MU', 'PANW',
                'MDLZ', 'PYPL', 'MELI', 'SNPS', 'KLAC', 'CDNS', 'MAR', 'MRVL', 'CRWD',
                'ORLY', 'CSX', 'ADSK', 'ABNB', 'FTNT', 'DASH', 'NXPI', 'PCAR', 'ROP',
                'WDAY', 'MNST', 'CHTR', 'CPRT', 'PAYX', 'AEP', 'ROST', 'ODFL', 'FAST',
                'KDP', 'EA', 'BKR', 'VRSK', 'CTSH', 'DDOG', 'GEHC', 'EXC', 'XEL',
                'CCEP', 'TEAM', 'IDXX', 'KHC', 'CSGP', 'ZS', 'LULU', 'ON', 'TTWO',
                'ANSS', 'DXCM', 'CDW', 'BIIB', 'MDB', 'WBD', 'GFS', 'ILMN', 'ARM',
                'MRNA', 'SMCI', 'DLTR']

def get_portfolio_tickers():
    """Load portfolio tickers from stocks.txt (exclude baskets)"""
    try:
        # Go up to root, then into data folder
        stocks_file = Path(__file__).parent.parent / 'data' / 'stocks.txt'

        if not stocks_file.exists():
            print(f"[X] stocks.txt not found")
            return []

        tickers = []
        with open(stocks_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments, empty lines, and basket definitions
                if line and not line.startswith('#') and not line.startswith('['):
                    tickers.append(line)

        print(f"[OK] Loaded {len(tickers)} portfolio tickers from stocks.txt\n")
        return tickers
    except Exception as e:
        print(f"[X] Error reading stocks.txt: {e}")
        return []

def scan_stocks(tickers, category="stocks", daily_bars=60, weekly_bars=52, concurrency=2):
    """
    Scan a list of stocks for buy opportunities

    Args:
        tickers: List of ticker symbols to scan
        category: Label for this scan (e.g., 'S&P 500', 'NASDAQ 100', 'Portfolio')
        daily_bars: Number of daily bars to analyze
        weekly_bars: Number of weekly bars to analyze
        concurrency: Number of concurrent API requests (default 2 to avoid rate limits)

    Returns:
        DataFrame with results sorted by signal strength
    """
    results = []
    buy_signals = []  # Track FULL HOLD + ADD signals
    total = len(tickers)
    completed = 0
    rate_limit_errors = 0  # Track rate limit hits

    print(f"[SCAN] Scanning {total} {category} stocks for 'FULL HOLD + ADD' signals...")
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
                        print(f"[OK] [{completed}/{total}] {ticker:6s} -> {signal:20s} ${price:.2f}")
                        buy_signals.append(result)
                    elif completed % 50 == 0:  # Progress update
                        print(f"  [{completed}/{total}] Scanning...")

            except Exception as e:
                error_msg = str(e).lower()
                if 'rate limit' in error_msg or '429' in error_msg or 'too many requests' in error_msg:
                    rate_limit_errors += 1
                if completed % 50 == 0:
                    print(f"  [{completed}/{total}] Scanning...")

    print("=" * 80)
    print(f"\n[OK] Scan complete: {len(results)} analyzed, {len(buy_signals)} FULL HOLD + ADD signals found\n")

    # Rate limit warning
    if rate_limit_errors > 0:
        print(f"[!] WARNING: {rate_limit_errors} rate limit errors detected!")
        print(f"   Yahoo Finance may be blocking requests. Wait 5-10 minutes before next scan.\n")
    elif len(results) == 0 and total > 0:
        print(f"[!] WARNING: No results returned from {total} tickers!")
        print(f"   This usually indicates Yahoo Finance rate limiting.")
        print(f"   Wait 5-10 minutes before retrying.\n")

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

def cleanup_old_scans(results_dir, max_files=1, archive_retention_days=60):
    """
    Keep only the most recent scan files for EACH category (SP500, NASDAQ100, Portfolio)
    Move older ones to archive, delete archive files older than archive_retention_days

    Args:
        results_dir: Directory containing scan results
        max_files: Number of most recent files to keep per category
        archive_retention_days: Days to keep files in archive before deletion
    """
    from datetime import datetime, timedelta
    import time

    archive_dir = results_dir / 'archive'
    archive_dir.mkdir(exist_ok=True)

    total_archived = 0

    # Define categories and their file patterns
    categories = [
        ('sp500', 'sp500_analysis_*.xlsx', 'scanner_report_sp500_*.pdf'),
        ('nasdaq100', 'nasdaq100_analysis_*.xlsx', 'scanner_report_nasdaq100_*.pdf'),
        ('portfolio', 'portfolio_scanner_*.xlsx', 'scanner_report_portfolio_*.pdf')
    ]

    # Process each category separately
    for cat_name, xlsx_pattern, pdf_pattern in categories:
        # Get files for this category
        xlsx_files = sorted(results_dir.glob(xlsx_pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        pdf_files = sorted(results_dir.glob(pdf_pattern), key=lambda p: p.stat().st_mtime, reverse=True)

        # Move files beyond max_files to archive
        for old_file in xlsx_files[max_files:]:
            archive_path = archive_dir / old_file.name
            old_file.rename(archive_path)
            print(f"  ðŸ“¦ Archived ({cat_name}): {old_file.name}")
            total_archived += 1

        for old_file in pdf_files[max_files:]:
            archive_path = archive_dir / old_file.name
            old_file.rename(archive_path)
            print(f"  ðŸ“¦ Archived ({cat_name}): {old_file.name}")
            total_archived += 1

    if total_archived > 0:
        print(f"  âœ… Archived {total_archived} file(s), kept {max_files} most recent")
    else:
        print(f"  âœ… No files to archive (only {max_files} most recent exist)")

    # Delete archive files older than retention period
    cutoff_time = time.time() - (archive_retention_days * 86400)  # 86400 seconds per day
    deleted_count = 0

    for archive_file in archive_dir.glob('*'):
        if archive_file.is_file() and archive_file.stat().st_mtime < cutoff_time:
            try:
                archive_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"  âš ï¸  Could not delete {archive_file.name}: {e}")

    if deleted_count > 0:
        print(f"  ðŸ—‘ï¸  Deleted {deleted_count} archive file(s) older than {archive_retention_days} days")

def create_excel_output(buy_df, output_file, category=""):
    """
    Create Excel workbook with single sheet for FULL HOLD + ADD signals
    (S&P 500 and NASDAQ 100 reports only show FULL HOLD + ADD in PDFs)

    Args:
        buy_df: DataFrame with FULL HOLD + ADD results
        output_file: Path to output Excel file
        category: Category label (e.g., 'S&P 500', 'NASDAQ 100')
    """
    if buy_df.empty:
        print(f"No data to export to Excel for {category}")
        return

    # Define column order (simplified, 9 columns)
    columns = [
        'ticker', 'signal', 'current_price',
        's1', 's2', 's3',       # Support levels (Zones)
        'r1', 'r2', 'r3'        # Resistance levels (Targets)
    ]

    # Keep only columns that exist in the dataframe
    available_cols = [col for col in columns if col in buy_df.columns]

    # Sort alphabetically by ticker
    buy_df_sorted = buy_df.sort_values('ticker')[available_cols].copy()

    # Create Excel writer with single sheet
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Single sheet: FULL HOLD + ADD
        buy_df_sorted.to_excel(writer, sheet_name='FULL HOLD + ADD', index=False)

        # Auto-adjust column widths
        worksheet = writer.sheets['FULL HOLD + ADD']
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

    print(f"[OK] Excel file created: {output_file}")
    print(f"  - FULL HOLD + ADD: {len(buy_df_sorted)} stocks")

def create_portfolio_excel(all_df, output_file, category="Portfolio"):
    """
    Create Excel workbook for portfolio with ALL stocks organized by signal

    Args:
        all_df: DataFrame with ALL portfolio results (not filtered)
        output_file: Path to output Excel file
        category: Category label (default: 'Portfolio')
    """
    if all_df.empty:
        print(f"No data to export to Excel for {category}")
        return

    # Define column order (only columns used in portfolio PDF report)
    columns = [
        'ticker', 'signal', 'current_price',
        's1', 's2', 's3',       # Support levels (Zones)
        'r1', 'r2', 'r3'        # Resistance levels (Targets)
    ]

    # Keep only columns that exist in the dataframe
    available_cols = [col for col in columns if col in all_df.columns]

    # Sort alphabetically by ticker
    all_df = all_df.sort_values('ticker')

    # Filter by signal (matching portfolio PDF format exactly)
    df_full_hold_add = all_df[all_df['signal'] == 'FULL HOLD + ADD'][available_cols].copy()
    df_hold_reduce = all_df[all_df['signal'] == 'HOLD MOST + REDUCE'][available_cols].copy()
    df_hold = all_df[all_df['signal'] == 'HOLD'][available_cols].copy()
    df_cash = all_df[all_df['signal'] == 'CASH'][available_cols].copy()
    df_all = all_df[available_cols].copy()

    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: All stocks
        df_all.to_excel(writer, sheet_name='All', index=False)

        # Sheet 2: FULL HOLD + ADD (detailed in PDF)
        df_full_hold_add.to_excel(writer, sheet_name='FULL HOLD + ADD', index=False)

        # Sheet 3: HOLD MOST + REDUCE (summary in PDF)
        df_hold_reduce.to_excel(writer, sheet_name='HOLD + REDUCE', index=False)

        # Sheet 4: HOLD (summary in PDF)
        df_hold.to_excel(writer, sheet_name='HOLD', index=False)

        # Sheet 5: CASH (summary in PDF)
        df_cash.to_excel(writer, sheet_name='CASH', index=False)

        # Auto-adjust column widths for all sheets
        for sheet_name in writer.sheets:
            if sheet_name in writer.sheets:
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

    print(f"âœ“ Excel file created: {output_file}")
    print(f"  - All: {len(df_all)} stocks")
    print(f"  - FULL HOLD + ADD: {len(df_full_hold_add)} stocks")
    print(f"  - HOLD MOST + REDUCE: {len(df_hold_reduce)} stocks")
    print(f"  - HOLD: {len(df_hold)} stocks")
    print(f"  - CASH: {len(df_cash)} stocks")

def create_pdf_report(buy_df, all_results_df, output_file, timestamp_str, category=""):
    """
    Create comprehensive PDF research document
    For Portfolio: Organized by SIGNAL (not confluence) using S1/S2/S3 as zones
    For S&P 500/NASDAQ 100: Focus on BALANCED opportunities with calculated zones

    Args:
        buy_df: DataFrame with buy signals
        all_results_df: DataFrame with all scan results
        output_file: Path to output PDF file
        timestamp_str: Timestamp string for report header
        category: Category label (e.g., 'S&P 500', 'NASDAQ 100', 'Portfolio')
    """
    if buy_df.empty:
        print(f"No data to create PDF report for {category}")
        return

    # All reports now use signal-based organization (like Portfolio)
    # Group by signal - for S&P/NASDAQ use buy_df (FULL HOLD + ADD only), for Portfolio use all_results_df
    is_portfolio = (category == "Portfolio")
    source_df = all_results_df if is_portfolio else buy_df

    buy_signals_df = source_df[source_df['signal'] == 'FULL HOLD + ADD'].sort_values('ticker')
    hold_reduce_df = source_df[source_df['signal'] == 'HOLD MOST + REDUCE'].sort_values('ticker') if is_portfolio else pd.DataFrame()
    hold_df = source_df[source_df['signal'] == 'HOLD'].sort_values('ticker') if is_portfolio else pd.DataFrame()
    cash_df = source_df[source_df['signal'] == 'CASH'].sort_values('ticker') if is_portfolio else pd.DataFrame()

    doc = SimpleDocTemplate(str(output_file), pagesize=letter,
                           rightMargin=30, leftMargin=30,
                           topMargin=30, bottomMargin=30)

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=20,
        alignment=TA_CENTER
    )

    section_style = ParagraphStyle(
        'Section',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2980b9'),
        spaceAfter=8,
        spaceBefore=12
    )

    # === COVER PAGE ===
    report_title = category if category else "S&P 500"
    # Escape ampersands properly for PDF display
    report_title_display = report_title.replace("&", "&amp;")
    cover_title = f"{report_title_display} Scanner Report<br/><font size=14>{datetime.now().strftime('%B %d, %Y, %I:%M %p')}</font>"
    elements.append(Paragraph(cover_title, title_style))
    elements.append(Spacer(1, 0.3*inch))

    # Signal-based breakdown for all reports
    total_stocks = len(source_df)
    cover_text = f"""
    <b>Analysis Parameters:</b><br/>
    - Total {report_title_display} stocks analyzed: {total_stocks}<br/>
    - FULL HOLD + ADD signals found: {len(buy_signals_df)} ({len(buy_signals_df)/total_stocks*100:.1f}%)<br/>
    <br/>
    <b>Report Contents:</b><br/>
    - <b>{len(buy_signals_df)} FULL HOLD + ADD</b> - Maximum bullish alignment (detailed analysis)<br/>
    """

    if is_portfolio:
        cover_text += f"""
    - <b>{len(hold_reduce_df)} HOLD MOST → REDUCE</b> - Weakening momentum (summary)<br/>
    - <b>{len(hold_df)} HOLD</b> - Neutral trend (summary)<br/>
    - <b>{len(cash_df)} CASH</b> - Bearish trend (summary)<br/>
        """

    cover_text += f"""
    <br/>
    <b>Each FULL HOLD + ADD stock includes:</b><br/>
    - Entry zones using Support levels (S1, S2, S3)<br/>
    - Upside targets using Resistance levels (R1, R2, R3)<br/>
    - Risk management with stops 5% below S3<br/>
    - Trailing stop guidelines for profit taking<br/>
    <br/>
    <i>Purpose: Actionable trading levels for strongest setups</i>
    """
    elements.append(Paragraph(cover_text, styles['Normal']))
    elements.append(PageBreak())

    # === SECTION 1: FULL HOLD + ADD (ALL REPORTS) ===
    if not buy_signals_df.empty:
        elements.append(Paragraph(f"FULL HOLD + ADD ({len(buy_signals_df)} stocks)", section_style))
        elements.append(Spacer(1, 0.1*inch))

        buy_intro = """
        <b>Maximum bullish alignment - Add aggressively on pullbacks</b><br/>
        Both weekly and daily trends are strongly bullish (P1). These are your core growth positions.<br/><br/>
        """
        elements.append(Paragraph(buy_intro, styles['Normal']))

        # Detailed analysis for each FULL HOLD + ADD stock
        for _, row in buy_signals_df.iterrows():
            ticker = row['ticker']
            price = row['current_price']
            signal = row['signal']

            # Stock header
            elements.append(Paragraph(f"<b>{ticker}</b> - ${price:,.2f} ({signal})", section_style))
            elements.append(Spacer(1, 0.05*inch))

            # Get support/resistance levels
            s1 = row.get('s1', price * 0.98)
            s2 = row.get('s2', price * 0.95)
            s3 = row.get('s3', price * 0.90)
            r1 = row.get('r1', price * 1.05)
            r2 = row.get('r2', price * 1.10)
            r3 = row.get('r3', price * 1.15)

            # Entry zones using support levels
            zones_text = f"""
            <b>Entry Zones (Support Levels):</b><br/>
            - <b>Zone 1 (Aggressive):</b> ${s1:,.2f} (S1 - Near current price)<br/>
            - <b>Zone 2 (Patient):</b> ${s2:,.2f} (S2 - Stronger support)<br/>
            - <b>Zone 3 (Deep Value):</b> ${s3:,.2f} (S3 - Major support)<br/>
            <br/>
            <b>Strategy:</b> Scale in across zones - don't chase. Build position gradually.
            """
            elements.append(Paragraph(zones_text, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

            # Risk management
            stop_price = s3 * 0.95  # 5% below S3
            elements.append(Paragraph("<b>Risk Management</b>", section_style))
            risk_text = f"""
            <b>Suggested Stop:</b> ${stop_price:,.2f} (5% below S3 at ${s3:,.2f})<br/>
            <b>Risk per entry:</b> Max 2% of portfolio per zone<br/>
            <b>Position sizing:</b> Build across 3 entries, average down on weakness
            """
            elements.append(Paragraph(risk_text, styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))

            # Upside targets (resistance levels)
            elements.append(Paragraph("<b>Upside Targets (Resistance Levels)</b>", section_style))

            # Check for NaN resistance levels (means clear skies / breaking highs)
            nan_count = sum([pd.isna(r1), pd.isna(r2), pd.isna(r3)])

            if nan_count > 0:
                targets_text = f"""
                <b>R1:</b> {'N/A - Clear Skies' if pd.isna(r1) else f'${r1:,.2f} ({(r1/price-1)*100:.1f}% gain)'} - First profit target<br/>
                <b>R2:</b> {'N/A - Clear Skies' if pd.isna(r2) else f'${r2:,.2f} ({(r2/price-1)*100:.1f}% gain)'} - Major resistance<br/>
                <b>R3:</b> {'N/A - Clear Skies' if pd.isna(r3) else f'${r3:,.2f} ({(r3/price-1)*100:.1f}% gain)'} - Full rally target<br/>
                <br/>
                <b>Note:</b> (*) N/A means limited overhead resistance - stock breaking into new highs!<br/>
                <b>Strategy:</b> Trail stops higher, use % gains instead of fixed targets
                """
            else:
                targets_text = f"""
                <b>R1:</b> ${r1:,.2f} ({(r1/price-1)*100:.1f}% gain) - First profit target<br/>
                <b>R2:</b> ${r2:,.2f} ({(r2/price-1)*100:.1f}% gain) - Major resistance<br/>
                <b>R3:</b> ${r3:,.2f} ({(r3/price-1)*100:.1f}% gain) - Full rally target<br/>
                <br/>
                <b>Strategy:</b> Take partial profits at each level, trail stops higher
                """
            elements.append(Paragraph(targets_text, styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))

            # Technical structure table
            elements.append(Paragraph("<b>Technical Structure</b>", section_style))
            tech_data = [
                ['Level', 'Price', 'Type', 'Action'],
                ['R3', 'Clear Skies (*)' if pd.isna(r3) else f"${r3:,.2f}", 'Major Resistance', 'Full exit target'],
                ['R2', 'Clear Skies (*)' if pd.isna(r2) else f"${r2:,.2f}", 'Key Resistance', 'Take 50% profits'],
                ['R1', 'Clear Skies (*)' if pd.isna(r1) else f"${r1:,.2f}", 'Minor Resistance', 'Take 25% profits'],
                ['Current', f"${price:,.2f}", 'Market Price', 'Monitor for entry'],
                ['S1', f"${s1:,.2f}", 'Near Support', 'Zone 1 entry'],
                ['S2', f"${s2:,.2f}", 'Strong Support', 'Zone 2 entry'],
                ['S3', f"${s3:,.2f}", 'Major Support', 'Zone 3 entry'],
                ['Stop', f"${stop_price:,.2f}", 'Stop Loss', '5% below S3'],
            ]

            tech_table = Table(tech_data, colWidths=[1.0*inch, 1.2*inch, 1.5*inch, 2.0*inch])
            tech_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('BACKGROUND', (0, 4), (-1, 4), colors.lightyellow),  # Highlight current price
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightcoral),  # Highlight stop
            ]))
            elements.append(tech_table)
            elements.append(Spacer(1, 0.15*inch))

            # Trailing stop guidelines for profit-taking
            elements.append(Paragraph("<b>Trailing Stop Guidelines (Profit Taking)</b>", section_style))
            trailing_text = """
            <b>Tiered trailing stops to protect gains while capturing upside:</b><br/>
            - <b>1st tranche (25% at R1):</b> 8-10% trailing stop - Lock in quick gains<br/>
            - <b>2nd tranche (25% at R2):</b> 12-15% trailing stop - Room for volatility<br/>
            - <b>Core position (50%):</b> 15-20% trailing stop - Let winners run<br/>
            <br/>
            <b>Why these percentages:</b> Growth stocks can swing 5-8% daily. 10%+ trailing stops avoid whipsaws
            while protecting profits. Strong uptrends typically hold 21-day MA (~12% below highs).
            """
            elements.append(Paragraph(trailing_text, styles['Normal']))

            elements.append(PageBreak())

        # SECTION 2: HOLD MOST + REDUCE
        if not hold_reduce_df.empty:
            elements.append(Paragraph(f"HOLD MOST + REDUCE ({len(hold_reduce_df)} stocks)", section_style))
            elements.append(Spacer(1, 0.1*inch))

            reduce_text = """
            <b>Weakening momentum - Hold majority but trim on rallies</b><br/>
            Trend is starting to weaken. Maintain core position but reduce exposure on strength.<br/>
            <b>Trailing stops:</b> Use tighter 5-8% stops on rallies - goal is to exit/reduce, not maximize gains.<br/><br/>
            """
            elements.append(Paragraph(reduce_text, styles['Normal']))

            # Summary table for HOLD MOST + REDUCE
            reduce_data = [['Ticker', 'Price', 'S3 (Stop)', 'Action']]
            for _, row in hold_reduce_df.iterrows():
                ticker = row['ticker']
                price = f"${row['current_price']:,.2f}"
                s3 = row.get('s3', row['current_price'] * 0.90)
                stop = s3 * 0.95
                action = f"Hold 60-70%, trim rest at R1 (${row.get('r1', row['current_price']*1.05):,.2f})"
                reduce_data.append([ticker, price, f"${stop:,.2f}", action])

            reduce_table = Table(reduce_data, colWidths=[1.0*inch, 1.0*inch, 1.2*inch, 3.3*inch])
            reduce_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f39c12')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(reduce_table)
            elements.append(PageBreak())

        # SECTION 3: HOLD
        if not hold_df.empty:
            elements.append(Paragraph(f"HOLD ({len(hold_df)} stocks)", section_style))
            elements.append(Spacer(1, 0.1*inch))

            hold_text = """
            <b>Neutral - Maintain current position, no action needed</b><br/>
            Trend is unclear. Hold full position patiently and wait for resolution.<br/><br/>
            """
            elements.append(Paragraph(hold_text, styles['Normal']))

            # Summary table for HOLD
            hold_data = [['Ticker', 'Price', 'S3 (Stop)', 'Action']]
            for _, row in hold_df.iterrows():
                ticker = row['ticker']
                price = f"${row['current_price']:,.2f}"
                s3 = row.get('s3', row['current_price'] * 0.90)
                stop = s3 * 0.95
                action = "Hold 100%, no trades"
                hold_data.append([ticker, price, f"${stop:,.2f}", action])

            hold_table = Table(hold_data, colWidths=[1.0*inch, 1.0*inch, 1.2*inch, 3.3*inch])
            hold_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#95a5a6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(hold_table)
            elements.append(PageBreak())

        # SECTION 4: CASH
        if not cash_df.empty:
            elements.append(Paragraph(f"CASH ({len(cash_df)} stocks)", section_style))
            elements.append(Spacer(1, 0.1*inch))

            cash_text = """
            <b>Bearish - Exit positions or stay in cash</b><br/>
            Trend is bearish. Protect capital by exiting or avoiding new positions.<br/><br/>
            """
            elements.append(Paragraph(cash_text, styles['Normal']))

            # Summary table for CASH
            cash_data = [['Ticker', 'Price', 'Last S3', 'Action']]
            for _, row in cash_df.iterrows():
                ticker = row['ticker']
                price = f"${row['current_price']:,.2f}"
                s3 = row.get('s3', row['current_price'] * 0.90)
                action = "Exit or avoid - bearish trend"
                cash_data.append([ticker, price, f"${s3:,.2f}", action])

            cash_table = Table(cash_data, colWidths=[1.0*inch, 1.0*inch, 1.2*inch, 3.3*inch])
            cash_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            elements.append(cash_table)
            elements.append(PageBreak())

    # === METHODOLOGY ===
    elements.append(Paragraph("Methodology", section_style))
    methodology_text = """
    <b>Signal Generation:</b> Larsson Market Phases on both weekly and daily timeframes.<br/>
    <b>Support/Resistance:</b> Swing pivot detection with 12-bar strength parameter.<br/>
    <br/>
    Not financial advice. Do your own due diligence before investing.
    """
    elements.append(Paragraph(methodology_text, styles['Normal']))

    # Build PDF
    doc.build(elements)
    print(f"[OK] PDF report created: {output_file}")
    if is_portfolio:
        print(f"  - {len(buy_signals_df)} FULL HOLD + ADD (detailed)")
        print(f"  - {len(hold_reduce_df)} HOLD MOST + REDUCE (summary)")
        print(f"  - {len(hold_df)} HOLD (summary)")
        print(f"  - {len(cash_df)} CASH (summary)")
    else:
        print(f"  - {len(buy_signals_df)} FULL HOLD + ADD (detailed)")

if __name__ == '__main__':
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Scan stocks for FULL HOLD + ADD signals')
    parser.add_argument('--daily-bars', type=int, default=60, help='Daily bars (default: 60)')
    parser.add_argument('--weekly-bars', type=int, default=52, help='Weekly bars (default: 52)')
    parser.add_argument('--concurrency', type=int, default=2, help='Threads (default: 2, higher values risk rate limiting)')

    args = parser.parse_args()

    # Setup results directory
    results_dir = Path.cwd() / 'scanner_results'
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    overall_start = datetime.now()

    # === SCAN 1: S&P 500 ===
    print("\n" + "="*80)
    print("SCAN 1 of 3: S&P 500")
    print("="*80 + "\n")

    print("Fetching S&P 500 ticker list...")
    sp500_tickers = get_sp500_tickers()
    print(f"Found {len(sp500_tickers)} S&P 500 stocks\n")

    start_time = datetime.now()
    sp500_results = scan_stocks(sp500_tickers, category="S&P 500",
                                daily_bars=args.daily_bars,
                                weekly_bars=args.weekly_bars,
                                concurrency=args.concurrency)
    sp500_elapsed = (datetime.now() - start_time).total_seconds()

    if not sp500_results.empty:
        sp500_buy = filter_buy_signals(sp500_results, 'FULL HOLD + ADD')
        print(f"\nðŸŽ¯ S&P 500: {len(sp500_buy)} FULL HOLD + ADD signals found")

        if not sp500_buy.empty:
            # Save S&P 500 results
            xlsx_path = results_dir / f'sp500_analysis_{timestamp}.xlsx'
            pdf_path = results_dir / f'scanner_report_sp500_{timestamp}.pdf'

            create_excel_output(sp500_buy, xlsx_path, category="S&P 500")
            create_pdf_report(sp500_buy, sp500_results, pdf_path, timestamp, category="S&P 500")

            print(f"  âœ“ Excel: {xlsx_path.name}")
            print(f"  âœ“ PDF: {pdf_path.name}")

    # === SCAN 2: NASDAQ 100 ===
    print("\n" + "="*80)
    print("SCAN 2 of 3: NASDAQ 100")
    print("="*80 + "\n")

    print("Fetching NASDAQ 100 ticker list...")
    nasdaq100_tickers = get_nasdaq100_tickers()
    print(f"Found {len(nasdaq100_tickers)} NASDAQ 100 stocks\n")

    start_time = datetime.now()
    nasdaq100_results = scan_stocks(nasdaq100_tickers, category="NASDAQ 100",
                                    daily_bars=args.daily_bars,
                                    weekly_bars=args.weekly_bars,
                                    concurrency=args.concurrency)
    nasdaq100_elapsed = (datetime.now() - start_time).total_seconds()

    if not nasdaq100_results.empty:
        nasdaq100_buy = filter_buy_signals(nasdaq100_results, 'FULL HOLD + ADD')
        print(f"\nðŸŽ¯ NASDAQ 100: {len(nasdaq100_buy)} FULL HOLD + ADD signals found")

        if not nasdaq100_buy.empty:
            # Save NASDAQ 100 results
            xlsx_path = results_dir / f'nasdaq100_analysis_{timestamp}.xlsx'
            pdf_path = results_dir / f'scanner_report_nasdaq100_{timestamp}.pdf'

            create_excel_output(nasdaq100_buy, xlsx_path, category="NASDAQ 100")
            create_pdf_report(nasdaq100_buy, nasdaq100_results, pdf_path, timestamp, category="NASDAQ 100")

            print(f"  âœ“ Excel: {xlsx_path.name}")
            print(f"  âœ“ PDF: {pdf_path.name}")

    # === SCAN 3: PORTFOLIO STOCKS ===
    print("\n" + "="*80)
    print("SCAN 3 of 3: PORTFOLIO STOCKS")
    print("="*80 + "\n")

    print("Loading portfolio tickers from stocks.txt...")
    portfolio_tickers = get_portfolio_tickers()

    if portfolio_tickers:
        print(f"Found {len(portfolio_tickers)} portfolio stocks\n")

        start_time = datetime.now()
        portfolio_results = scan_stocks(portfolio_tickers, category="Portfolio",
                                       daily_bars=args.daily_bars,
                                       weekly_bars=args.weekly_bars,
                                       concurrency=args.concurrency)
        portfolio_elapsed = (datetime.now() - start_time).total_seconds()

        if not portfolio_results.empty:
            # For portfolio, include ALL stocks (not just FULL HOLD + ADD)
            # But still create separate sheets by signal type
            print(f"\nðŸŽ¯ Portfolio: {len(portfolio_results)} stocks scanned (all included)")

            # Count FULL HOLD + ADD for display
            portfolio_buy = filter_buy_signals(portfolio_results, 'FULL HOLD + ADD')
            print(f"  - {len(portfolio_buy)} with FULL HOLD + ADD signal")

            # Save ALL portfolio results (not filtered)
            xlsx_path = results_dir / f'portfolio_scanner_{timestamp}.xlsx'
            pdf_path = results_dir / f'scanner_report_portfolio_{timestamp}.pdf'

            # Pass ALL results for portfolio
            create_portfolio_excel(portfolio_results, xlsx_path, category="Portfolio")

            # For PDF, still show FULL HOLD + ADD in detail (with all stocks in summary)
            if not portfolio_buy.empty:
                create_pdf_report(portfolio_buy, portfolio_results, pdf_path, timestamp, category="Portfolio")

            print(f"  âœ“ Excel: {xlsx_path.name}")
            print(f"  âœ“ PDF: {pdf_path.name}")
    else:
        print("âš ï¸  No portfolio tickers found in stocks.txt")

    # === FINAL SUMMARY ===
    total_elapsed = (datetime.now() - overall_start).total_seconds()

    print("\n" + "="*80)
    print("SCAN COMPLETE - SUMMARY")
    print("="*80)
    print(f"[TIME] Total time: {total_elapsed:.1f}s")
    print(f"\nðŸ“Š Results by Category:")

    if not sp500_results.empty:
        sp500_buy_count = len(filter_buy_signals(sp500_results, 'FULL HOLD + ADD'))
        print(f"  S&P 500:     {sp500_buy_count:3d} FULL HOLD + ADD signals ({sp500_elapsed:.1f}s)")

    if not nasdaq100_results.empty:
        nasdaq100_buy_count = len(filter_buy_signals(nasdaq100_results, 'FULL HOLD + ADD'))
        print(f"  NASDAQ 100:  {nasdaq100_buy_count:3d} FULL HOLD + ADD signals ({nasdaq100_elapsed:.1f}s)")

    if portfolio_tickers and not portfolio_results.empty:
        portfolio_buy_count = len(filter_buy_signals(portfolio_results, 'FULL HOLD + ADD'))
        print(f"  Portfolio:   {portfolio_buy_count:3d} FULL HOLD + ADD signals ({portfolio_elapsed:.1f}s)")

    # Cleanup old scans (keep 1 most recent per category)
    print("\nðŸ“ Managing scan history...")
    cleanup_old_scans(results_dir, max_files=1)
