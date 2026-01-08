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
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def get_sp500_tickers():
    """Fetch current S&P 500 ticker list from Wikipedia"""
    import urllib.request

    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    # Add user agent to avoid 403 Forbidden
    req = urllib.request.Request(url)
    req.add_header(
        "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    try:
        with urllib.request.urlopen(req) as response:
            tables = pd.read_html(response)
            sp500_table = tables[0]
            tickers = sp500_table["Symbol"].tolist()

            # Clean up tickers (some have special characters)
            tickers = [t.replace(".", "-") for t in tickers]
            print(f"[OK] Loaded {len(tickers)} S&P 500 tickers\n")
            return tickers
    except Exception as e:
        print(f"[X] Error fetching S&P 500 list: {e}")
        print("Using fallback list of major stocks...")
        # Fallback to major stocks if Wikipedia fails
        return [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "NVDA",
            "META",
            "TSLA",
            "BRK-B",
            "UNH",
            "JNJ",
            "XOM",
            "V",
            "PG",
            "MA",
            "HD",
            "CVX",
            "MRK",
            "ABBV",
            "PEP",
            "COST",
        ]


def get_nasdaq100_tickers():
    """Fetch current NASDAQ 100 ticker list from Wikipedia"""
    import urllib.request

    url = "https://en.wikipedia.org/wiki/Nasdaq-100"

    # Add user agent to avoid 403 Forbidden
    req = urllib.request.Request(url)
    req.add_header(
        "User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    try:
        with urllib.request.urlopen(req) as response:
            tables = pd.read_html(response)
            # Try different table indices and column names
            for table in tables:
                if "Ticker" in table.columns:
                    tickers = table["Ticker"].tolist()
                    tickers = [t.replace(".", "-") for t in tickers]
                    print(f"[OK] Loaded {len(tickers)} NASDAQ 100 tickers\n")
                    return tickers
                elif "Symbol" in table.columns:
                    tickers = table["Symbol"].tolist()
                    tickers = [t.replace(".", "-") for t in tickers]
                    print(f"[OK] Loaded {len(tickers)} NASDAQ 100 tickers\n")
                    return tickers

            # If no matching table found
            raise Exception("No table with 'Ticker' or 'Symbol' column found")
    except Exception as e:
        print(f"[X] Error fetching NASDAQ 100 list: {e}")
        print("Using fallback list of major tech stocks...")
        # Fallback to major tech stocks if Wikipedia fails
        return [
            "AAPL",
            "MSFT",
            "GOOGL",
            "GOOG",
            "AMZN",
            "NVDA",
            "META",
            "TSLA",
            "AVGO",
            "COST",
            "ASML",
            "AMD",
            "NFLX",
            "PEP",
            "ADBE",
            "CSCO",
            "TMUS",
            "CMCSA",
            "INTC",
            "TXN",
            "QCOM",
            "INTU",
            "HON",
            "AMAT",
            "AMGN",
            "BKNG",
            "ADP",
            "ISRG",
            "VRTX",
            "SBUX",
            "GILD",
            "ADI",
            "REGN",
            "LRCX",
            "MU",
            "PANW",
            "MDLZ",
            "PYPL",
            "MELI",
            "SNPS",
            "KLAC",
            "CDNS",
            "MAR",
            "MRVL",
            "CRWD",
            "ORLY",
            "CSX",
            "ADSK",
            "ABNB",
            "FTNT",
            "DASH",
            "NXPI",
            "PCAR",
            "ROP",
            "WDAY",
            "MNST",
            "CHTR",
            "CPRT",
            "PAYX",
            "AEP",
            "ROST",
            "ODFL",
            "FAST",
            "KDP",
            "EA",
            "BKR",
            "VRSK",
            "CTSH",
            "DDOG",
            "GEHC",
            "EXC",
            "XEL",
            "CCEP",
            "TEAM",
            "IDXX",
            "KHC",
            "CSGP",
            "ZS",
            "LULU",
            "ON",
            "TTWO",
            "ANSS",
            "DXCM",
            "CDW",
            "BIIB",
            "MDB",
            "WBD",
            "GFS",
            "ILMN",
            "ARM",
            "MRNA",
            "SMCI",
            "DLTR",
        ]


def get_portfolio_tickers():
    """Load portfolio tickers from stocks.txt (exclude baskets)"""
    try:
        # Go up to root, then into data folder
        stocks_file = Path(__file__).parent.parent / "data" / "stocks.txt"

        if not stocks_file.exists():
            print(f"[X] stocks.txt not found")
            return []

        tickers = []
        with open(stocks_file, "r") as f:
            for line in f:
                line = line.strip()
                # Skip comments, empty lines, and basket definitions
                if line and not line.startswith("#") and not line.startswith("["):
                    tickers.append(line)

        print(f"[OK] Loaded {len(tickers)} portfolio tickers from stocks.txt\n")
        return tickers
    except Exception as e:
        print(f"[X] Error reading stocks.txt: {e}")
        return []


def scan_stocks(
    tickers, category="stocks", daily_bars=60, weekly_bars=52, concurrency=2
):
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
    print(
        f"Parameters: {daily_bars} daily bars, {weekly_bars} weekly bars, {concurrency} threads"
    )
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

                if "error" not in result:
                    results.append(result)
                    signal = result.get("signal", "N/A")

                    # Only print FULL HOLD + ADD signals with buy quality
                    if signal == "FULL HOLD + ADD":
                        price = result.get("current_price", 0)
                        buy_quality = result.get("buy_quality", "N/A")
                        quality_indicator = (
                            "✓" if buy_quality in ["EXCELLENT", "GOOD", "OK"] else "⚠"
                        )
                        print(
                            f"[OK] [{completed}/{total}] {ticker:6s} -> {signal:20s} ${price:,.2f} | Quality: {buy_quality:10s} {quality_indicator}"
                        )
                        buy_signals.append(result)
                    elif completed % 50 == 0:  # Progress update
                        print(f"  [{completed}/{total}] Scanning...")

            except Exception as e:
                error_msg = str(e).lower()
                if (
                    "rate limit" in error_msg
                    or "429" in error_msg
                    or "too many requests" in error_msg
                ):
                    rate_limit_errors += 1
                if completed % 50 == 0:
                    print(f"  [{completed}/{total}] Scanning...")

    print("=" * 80)
    print(
        f"\n[OK] Scan complete: {len(results)} analyzed, {len(buy_signals)} FULL HOLD + ADD signals found\n"
    )

    # Rate limit warning
    if rate_limit_errors > 0:
        print(f"[!] WARNING: {rate_limit_errors} rate limit errors detected!")
        print(
            f"   Yahoo Finance may be blocking requests. Wait 5-10 minutes before next scan.\n"
        )
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


def filter_buy_signals(df, signal="FULL HOLD + ADD", quality_filter=True):
    """
    Filter for FULL HOLD + ADD signals (strongest bullish alignment)

    Args:
        df: DataFrame with scan results
        signal: Signal to filter for (default: 'FULL HOLD + ADD')
        quality_filter: If True, only include EXCELLENT/GOOD/OK quality (exclude EXTENDED/WEAK)

    Returns:
        Filtered DataFrame sorted by ticker
    """
    if df.empty:
        return df

    # Filter by signal
    filtered = df[df["signal"] == signal].copy()

    # Optionally filter by buy quality
    if quality_filter and "buy_quality" in filtered.columns:
        filtered = filtered[filtered["buy_quality"].isin(["EXCELLENT", "GOOD", "OK"])]

    return filtered.sort_values("ticker")


def filter_sell_signals(df, quality_filter=False):
    """
    Filter for bearish signals that warrant selling.
    Matches portfolio_analysis logic: ANY bearish signal = SELL

    Args:
        df: DataFrame with scan results
        quality_filter: If True, only include STRONG/MODERATE R1 quality.
                       Default False to match portfolio_analysis (all bearish signals)

    Returns:
        Filtered DataFrame sorted by ticker
    """
    if df.empty:
        return df

    # Filter for bearish signals (same as determine_portfolio_action in technical_analysis.py)
    bearish_signals = [
        "HOLD MOST + REDUCE",
        "REDUCE",
        "LIGHT / CASH",
        "CASH",
        "FULL CASH / DEFEND",
    ]
    filtered = df[df["signal"].isin(bearish_signals)].copy()

    # Optionally filter by R1 quality (disabled by default to match portfolio behavior)
    if quality_filter and "r1_quality" in filtered.columns:
        filtered = filtered[filtered["r1_quality"].isin(["STRONG", "MODERATE"])]

    return filtered.sort_values("ticker")


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

    archive_dir = results_dir / "archive"
    archive_dir.mkdir(exist_ok=True)

    total_archived = 0

    # Define categories and their file patterns
    categories = [
        ("sp500", "sp500_analysis_*.xlsx", "scanner_report_sp500_*.pdf"),
        ("nasdaq100", "nasdaq100_analysis_*.xlsx", "scanner_report_nasdaq100_*.pdf"),
        ("portfolio", "portfolio_scanner_*.xlsx", "scanner_report_portfolio_*.pdf"),
    ]

    # Process each category separately
    for cat_name, xlsx_pattern, pdf_pattern in categories:
        # Get files for this category
        xlsx_files = sorted(
            results_dir.glob(xlsx_pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        pdf_files = sorted(
            results_dir.glob(pdf_pattern), key=lambda p: p.stat().st_mtime, reverse=True
        )

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
    cutoff_time = time.time() - (
        archive_retention_days * 86400
    )  # 86400 seconds per day
    deleted_count = 0

    for archive_file in archive_dir.glob("*"):
        if archive_file.is_file() and archive_file.stat().st_mtime < cutoff_time:
            try:
                archive_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"  âš ï¸  Could not delete {archive_file.name}: {e}")

    if deleted_count > 0:
        print(
            f"  ðŸ—‘ï¸  Deleted {deleted_count} archive file(s) older than {archive_retention_days} days"
        )


def create_excel_output(buy_df, sell_df, output_file, category=""):
    """
    Create Excel workbook with tabs for buy and sell opportunities.
    Matches portfolio_tracker format from portfolio_reports.py

    Args:
        buy_df: DataFrame with FULL HOLD + ADD results (quality-filtered)
        sell_df: DataFrame with bearish signal results
        output_file: Path to output Excel file
        category: Category label (e.g., 'S&P 500', 'NASDAQ 100')
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment

    wb = Workbook()
    if "Sheet" in wb.sheetnames:
        del wb["Sheet"]

    # Define styles (matching portfolio_reports)
    header_fill = PatternFill(
        start_color="4472C4", end_color="4472C4", fill_type="solid"
    )
    header_font = Font(bold=True, color="FFFFFF")
    center_align = Alignment(horizontal="center", vertical="center")

    # === TAB 1: BUY OPPORTUNITIES ===
    if not buy_df.empty:
        ws_buy = wb.create_sheet("Buy Opportunities")

        # Title
        ws_buy.cell(1, 1, f"{category} - BUY OPPORTUNITIES").font = Font(
            bold=True, size=14
        )
        ws_buy.cell(
            2, 1, f"FULL HOLD + ADD signals with EXCELLENT/GOOD/OK quality"
        ).font = Font(italic=True, color="666666")

        # Headers at row 4
        buy_headers = [
            "Ticker",
            "Signal",
            "Price",
            "Buy Quality",
            "S1",
            "S2",
            "S3",
            "R1",
            "R2",
            "R3",
            "D50 MA",
            "D100 MA",
            "D200 MA",
        ]

        for col_num, header in enumerate(buy_headers, 1):
            cell = ws_buy.cell(4, col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align

        # Data rows
        row = 5
        for _, stock in buy_df.sort_values("ticker").iterrows():
            ws_buy.cell(row, 1, stock["ticker"])
            ws_buy.cell(row, 2, stock["signal"])
            ws_buy.cell(row, 3, stock.get("current_price"))
            ws_buy.cell(row, 4, stock.get("buy_quality"))
            ws_buy.cell(row, 5, stock.get("s1"))
            ws_buy.cell(row, 6, stock.get("s2"))
            ws_buy.cell(row, 7, stock.get("s3"))
            ws_buy.cell(row, 8, stock.get("r1"))
            ws_buy.cell(row, 9, stock.get("r2"))
            ws_buy.cell(row, 10, stock.get("r3"))
            ws_buy.cell(row, 11, stock.get("d50"))
            ws_buy.cell(row, 12, stock.get("d100"))
            ws_buy.cell(row, 13, stock.get("d200"))
            row += 1

        # Auto-size columns
        for col in ws_buy.columns:
            max_length = 12
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws_buy.column_dimensions[col[0].column_letter].width = min(
                max_length + 2, 50
            )

    # === TAB 2: SELL SIGNALS ===
    if not sell_df.empty:
        ws_sell = wb.create_sheet("Sell Signals")

        # Title
        ws_sell.cell(1, 1, f"{category} - SELL SIGNALS").font = Font(bold=True, size=14)
        ws_sell.cell(2, 1, f"Bearish signals - reduce exposure").font = Font(
            italic=True, color="666666"
        )

        # Headers at row 4
        sell_headers = [
            "Ticker",
            "Signal",
            "Price",
            "R1 Quality",
            "R1",
            "R2",
            "R3",
            "D50 MA",
            "D100 MA",
            "D200 MA",
        ]

        for col_num, header in enumerate(sell_headers, 1):
            cell = ws_sell.cell(4, col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align

        # Data rows
        row = 5
        for _, stock in sell_df.sort_values("ticker").iterrows():
            ws_sell.cell(row, 1, stock["ticker"])
            ws_sell.cell(row, 2, stock["signal"])
            ws_sell.cell(row, 3, stock.get("current_price"))
            ws_sell.cell(row, 4, stock.get("r1_quality"))
            ws_sell.cell(row, 5, stock.get("r1"))
            ws_sell.cell(row, 6, stock.get("r2"))
            ws_sell.cell(row, 7, stock.get("r3"))
            ws_sell.cell(row, 8, stock.get("d50"))
            ws_sell.cell(row, 9, stock.get("d100"))
            ws_sell.cell(row, 10, stock.get("d200"))
            row += 1

        # Auto-size columns
        for col in ws_sell.columns:
            max_length = 12
            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws_sell.column_dimensions[col[0].column_letter].width = min(
                max_length + 2, 50
            )

    # Save workbook
    wb.save(output_file)

    print(f"[OK] Excel file created: {output_file}")
    if not buy_df.empty:
        print(f"  - Buy Opportunities: {len(buy_df)} stocks")
    if not sell_df.empty:
        print(f"  - Sell Signals: {len(sell_df)} stocks")


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
        "ticker",
        "signal",
        "current_price",
        "s1",
        "s2",
        "s3",  # Support levels (Zones)
        "r1",
        "r2",
        "r3",  # Resistance levels (Targets)
    ]

    # Keep only columns that exist in the dataframe
    available_cols = [col for col in columns if col in all_df.columns]

    # Sort alphabetically by ticker
    all_df = all_df.sort_values("ticker")

    # Filter by signal (matching portfolio PDF format exactly)
    df_full_hold_add = all_df[all_df["signal"] == "FULL HOLD + ADD"][
        available_cols
    ].copy()
    df_hold_reduce = all_df[all_df["signal"] == "HOLD MOST + REDUCE"][
        available_cols
    ].copy()
    df_hold = all_df[all_df["signal"] == "HOLD"][available_cols].copy()
    df_cash = all_df[all_df["signal"] == "CASH"][available_cols].copy()
    df_all = all_df[available_cols].copy()

    # Create Excel writer
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        # Sheet 1: All stocks
        df_all.to_excel(writer, sheet_name="All", index=False)

        # Sheet 2: FULL HOLD + ADD (detailed in PDF)
        df_full_hold_add.to_excel(writer, sheet_name="FULL HOLD + ADD", index=False)

        # Sheet 3: HOLD MOST + REDUCE (summary in PDF)
        df_hold_reduce.to_excel(writer, sheet_name="HOLD + REDUCE", index=False)

        # Sheet 4: HOLD (summary in PDF)
        df_hold.to_excel(writer, sheet_name="HOLD", index=False)

        # Sheet 5: CASH (summary in PDF)
        df_cash.to_excel(writer, sheet_name="CASH", index=False)

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


def create_pdf_report(buy_df, sell_df, output_file, timestamp_str, category=""):
    """
    Create comprehensive PDF trading report matching portfolio_reports format.
    Adapted for scanner (no holdings/targets data)

    Args:
        buy_df: DataFrame with quality-filtered buy signals
        sell_df: DataFrame with sell signals
        output_file: Path to output PDF file
        timestamp_str: Timestamp string for report header
        category: Category label (e.g., 'S&P 500', 'NASDAQ 100')
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        PageBreak,
    )
    from reportlab.lib.enums import TA_CENTER

    if buy_df.empty and sell_df.empty:
        print(f"No data to create PDF report for {category}")
        return

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30,
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles (matching portfolio_reports)
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.HexColor("#2980b9"),
        spaceAfter=12,
        spaceBefore=20,
    )

    subsection_style = ParagraphStyle(
        "Subsection",
        parent=styles["Heading3"],
        fontSize=12,
        textColor=colors.HexColor("#34495e"),
        spaceAfter=6,
        spaceBefore=10,
    )

    # === PAGE 1: DASHBOARD ===
    report_title = category.replace("&", "&amp;")
    cover_title = f"Trading Playbook - {report_title}<br/><font size=14>{datetime.now().strftime('%B %d, %Y')}</font>"
    elements.append(Paragraph(cover_title, title_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Scanner summary
    summary_text = f"""
    <b>Market Scan Summary</b><br/>
    <br/>
    <b>Buy Opportunities:</b> {len(buy_df)} stocks (FULL HOLD + ADD with quality)<br/>
    <b>Sell Signals:</b> {len(sell_df)} stocks (Bearish - reduce exposure)<br/>
    <br/>
    <b>Report Contents:</b><br/>
    - Section 1: Buy Opportunities (detailed entry plans)<br/>
    - Section 2: Sell Signals (exit recommendations)<br/>
    <br/>
    <i>Generated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}</i>
    """
    elements.append(Paragraph(summary_text, styles["Normal"]))
    elements.append(PageBreak())

    # === SECTION 1: BUY OPPORTUNITIES ===
    if not buy_df.empty:
        elements.append(
            Paragraph(f"BUY OPPORTUNITIES ({len(buy_df)} stocks)", section_style)
        )
        elements.append(Spacer(1, 0.1 * inch))

        for _, stock in buy_df.sort_values("ticker").iterrows():
            ticker = stock["ticker"]
            price = stock["current_price"]
            signal = stock["signal"]
            buy_quality = stock.get("buy_quality", "N/A")

            # Stock header
            header_text = f"<b>{ticker}</b> - ${price:,.2f} ({signal})"
            elements.append(Paragraph(header_text, subsection_style))

            # Support levels (entry zones)
            s1 = stock.get("s1")
            s2 = stock.get("s2")
            s3 = stock.get("s3")

            support_text = "<b>Entry Zones (Support Levels):</b><br/>"
            if s1:
                support_text += f"- S1: ${s1:,.2f}<br/>"
            if s2:
                support_text += f"- S2: ${s2:,.2f}<br/>"
            if s3:
                support_text += f"- S3: ${s3:,.2f}<br/>"
            elements.append(Paragraph(support_text, styles["Normal"]))
            elements.append(Spacer(1, 0.05 * inch))

            # Buy quality for each support level (matching portfolio format)
            s1_quality = stock.get("s1_quality", "N/A")
            s1_quality_note = stock.get("s1_quality_note", "")
            s2_quality = stock.get("s2_quality", "N/A")
            s2_quality_note = stock.get("s2_quality_note", "")
            s3_quality = stock.get("s3_quality", "N/A")
            s3_quality_note = stock.get("s3_quality_note", "")

            quality_text = f"""
            <b>Buy Quality S1:</b> {s1_quality} - {s1_quality_note}<br/>
            <b>Buy Quality S2:</b> {s2_quality} - {s2_quality_note}<br/>
            <b>Buy Quality S3:</b> {s3_quality} - {s3_quality_note}
            """
            elements.append(Paragraph(quality_text, styles["Normal"]))
            elements.append(Spacer(1, 0.05 * inch))

            # Resistance levels (targets)
            r1 = stock.get("r1")
            r2 = stock.get("r2")
            r3 = stock.get("r3")

            target_text = "<b>Upside Targets (Resistance Levels):</b><br/>"
            if r1:
                gain1 = (r1 / price - 1) * 100 if price > 0 else 0
                target_text += f"- R1: ${r1:,.2f} ({gain1:.1f}% gain)<br/>"
            if r2:
                gain2 = (r2 / price - 1) * 100 if price > 0 else 0
                target_text += f"- R2: ${r2:,.2f} ({gain2:.1f}% gain)<br/>"
            if r3:
                gain3 = (r3 / price - 1) * 100 if price > 0 else 0
                target_text += f"- R3: ${r3:,.2f} ({gain3:.1f}% gain)<br/>"
            elements.append(Paragraph(target_text, styles["Normal"]))
            elements.append(Spacer(1, 0.05 * inch))

            # Sell quality for resistance levels (exit quality assessment)
            r1_quality = stock.get("r1_quality", "N/A")
            r1_quality_note = stock.get("r1_quality_note", "")
            r2_quality = stock.get("r2_quality", "N/A")
            r2_quality_note = stock.get("r2_quality_note", "")
            r3_quality = stock.get("r3_quality", "N/A")
            r3_quality_note = stock.get("r3_quality_note", "")

            sell_quality_text = f"""
            <b>Sell Quality R1:</b> {r1_quality} - {r1_quality_note}<br/>
            <b>Sell Quality R2:</b> {r2_quality} - {r2_quality_note}<br/>
            <b>Sell Quality R3:</b> {r3_quality} - {r3_quality_note}
            """
            elements.append(Paragraph(sell_quality_text, styles["Normal"]))
            elements.append(Spacer(1, 0.05 * inch))

            # Moving averages
            d50 = stock.get("d50")
            d100 = stock.get("d100")
            d200 = stock.get("d200")
            if d50 or d100 or d200:
                ma_text = "<b>Moving Averages:</b> "
                ma_parts = []
                if d50:
                    ma_parts.append(f"D50 ${d50:,.2f}")
                if d100:
                    ma_parts.append(f"D100 ${d100:,.2f}")
                if d200:
                    ma_parts.append(f"D200 ${d200:,.2f}")
                ma_text += " | ".join(ma_parts)
                elements.append(Paragraph(ma_text, styles["Normal"]))

            # Volume Profile (matching portfolio format)
            poc = stock.get("poc_60d")
            val = stock.get("val_60d")
            vah = stock.get("vah_60d")
            if poc or val or vah:
                volume_text = f"""
                <b>Volume Profile (60d):</b> POC ${poc:,.2f} | VAL ${val:,.2f} - VAH ${vah:,.2f}
                """
                elements.append(Paragraph(volume_text, styles["Normal"]))

            elements.append(Spacer(1, 0.15 * inch))
    else:
        elements.append(Paragraph("BUY OPPORTUNITIES (0 stocks)", section_style))
        elements.append(
            Paragraph("No quality buy signals at this time.", styles["Normal"])
        )
        elements.append(PageBreak())

    # === SECTION 2: SELL SIGNALS ===
    if not sell_df.empty:
        elements.append(PageBreak())
        elements.append(
            Paragraph(f"SELL SIGNALS ({len(sell_df)} stocks)", section_style)
        )
        elements.append(Spacer(1, 0.1 * inch))

        for _, stock in sell_df.sort_values("ticker").iterrows():
            ticker = stock["ticker"]
            price = stock["current_price"]
            signal = stock["signal"]
            r1_quality = stock.get("r1_quality", "N/A")
            r2_quality = stock.get("r2_quality", "N/A")
            r3_quality = stock.get("r3_quality", "N/A")

            # Stock header
            header_text = f"<b>{ticker}</b> - ${price:,.2f} ({signal})"
            elements.append(Paragraph(header_text, subsection_style))

            # Resistance levels (exit targets)
            r1 = stock.get("r1")
            r2 = stock.get("r2")
            r3 = stock.get("r3")

            exit_text = "<b>Exit Targets (Resistance Levels):</b><br/>"
            if r1:
                exit_text += f"- R1: ${r1:,.2f} - Primary exit level<br/>"
            if r2:
                exit_text += f"- R2: ${r2:,.2f} - Secondary exit<br/>"
            if r3:
                exit_text += f"- R3: ${r3:,.2f} - Final exit<br/>"
            elements.append(Paragraph(exit_text, styles["Normal"]))
            elements.append(Spacer(1, 0.05 * inch))

            # R1/R2/R3 quality assessments (matching portfolio format)
            r1_quality_note = stock.get("r1_quality_note", "")
            r2_quality_note = stock.get("r2_quality_note", "")
            r3_quality_note = stock.get("r3_quality_note", "")

            quality_text = f"""
            <b>Sell Quality R1:</b> {r1_quality} - {r1_quality_note}<br/>
            <b>Sell Quality R2:</b> {r2_quality} - {r2_quality_note}<br/>
            <b>Sell Quality R3:</b> {r3_quality} - {r3_quality_note}
            """
            elements.append(Paragraph(quality_text, styles["Normal"]))
            elements.append(Spacer(1, 0.05 * inch))

            # Moving averages
            d50 = stock.get("d50")
            d100 = stock.get("d100")
            d200 = stock.get("d200")
            if d50 or d100 or d200:
                ma_text = "<b>Moving Averages:</b> "
                ma_parts = []
                if d50:
                    ma_parts.append(f"D50 ${d50:,.2f}")
                if d100:
                    ma_parts.append(f"D100 ${d100:,.2f}")
                if d200:
                    ma_parts.append(f"D200 ${d200:,.2f}")
                ma_text += " | ".join(ma_parts)
                elements.append(Paragraph(ma_text, styles["Normal"]))

            elements.append(Spacer(1, 0.15 * inch))
    else:
        elements.append(PageBreak())
        elements.append(Paragraph("SELL SIGNALS (0 stocks)", section_style))
        elements.append(Paragraph("No bearish signals at this time.", styles["Normal"]))

    # Build PDF
    doc.build(elements)
    print(f"[OK] PDF report created: {output_file}")


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Scan stocks for FULL HOLD + ADD signals"
    )
    parser.add_argument(
        "--daily-bars", type=int, default=60, help="Daily bars (default: 60)"
    )
    parser.add_argument(
        "--weekly-bars", type=int, default=52, help="Weekly bars (default: 52)"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=2,
        help="Threads (default: 2, higher values risk rate limiting)",
    )

    args = parser.parse_args()

    # Setup results directory
    results_dir = Path.cwd() / "scanner_results"
    results_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    overall_start = datetime.now()

    # === SCAN 1: S&P 500 ===
    print("\n" + "=" * 80)
    print("SCAN 1 of 3: S&P 500")
    print("=" * 80 + "\n")

    print("Fetching S&P 500 ticker list...")
    sp500_tickers = get_sp500_tickers()
    print(f"Found {len(sp500_tickers)} S&P 500 stocks\n")

    start_time = datetime.now()
    sp500_results = scan_stocks(
        sp500_tickers,
        category="S&P 500",
        daily_bars=args.daily_bars,
        weekly_bars=args.weekly_bars,
        concurrency=args.concurrency,
    )
    sp500_elapsed = (datetime.now() - start_time).total_seconds()

    if not sp500_results.empty:
        sp500_buy = filter_buy_signals(sp500_results, "FULL HOLD + ADD")
        print(f"\nðŸŽ¯ S&P 500: {len(sp500_buy)} FULL HOLD + ADD signals found")

        if not sp500_buy.empty:
            # Save S&P 500 results
            xlsx_path = results_dir / f"sp500_analysis_{timestamp}.xlsx"
            pdf_path = results_dir / f"scanner_report_sp500_{timestamp}.pdf"

            create_excel_output(sp500_buy, xlsx_path, category="S&P 500")
            create_pdf_report(
                sp500_buy, sp500_results, pdf_path, timestamp, category="S&P 500"
            )

            print(f"  âœ“ Excel: {xlsx_path.name}")
            print(f"  âœ“ PDF: {pdf_path.name}")

    # === SCAN 2: NASDAQ 100 ===
    print("\n" + "=" * 80)
    print("SCAN 2 of 3: NASDAQ 100")
    print("=" * 80 + "\n")

    print("Fetching NASDAQ 100 ticker list...")
    nasdaq100_tickers = get_nasdaq100_tickers()
    print(f"Found {len(nasdaq100_tickers)} NASDAQ 100 stocks\n")

    start_time = datetime.now()
    nasdaq100_results = scan_stocks(
        nasdaq100_tickers,
        category="NASDAQ 100",
        daily_bars=args.daily_bars,
        weekly_bars=args.weekly_bars,
        concurrency=args.concurrency,
    )
    nasdaq100_elapsed = (datetime.now() - start_time).total_seconds()

    if not nasdaq100_results.empty:
        nasdaq100_buy = filter_buy_signals(nasdaq100_results, "FULL HOLD + ADD")
        print(f"\nðŸŽ¯ NASDAQ 100: {len(nasdaq100_buy)} FULL HOLD + ADD signals found")

        if not nasdaq100_buy.empty:
            # Save NASDAQ 100 results
            xlsx_path = results_dir / f"nasdaq100_analysis_{timestamp}.xlsx"
            pdf_path = results_dir / f"scanner_report_nasdaq100_{timestamp}.pdf"

            create_excel_output(nasdaq100_buy, xlsx_path, category="NASDAQ 100")
            create_pdf_report(
                nasdaq100_buy,
                nasdaq100_results,
                pdf_path,
                timestamp,
                category="NASDAQ 100",
            )

            print(f"  âœ“ Excel: {xlsx_path.name}")
            print(f"  âœ“ PDF: {pdf_path.name}")

    # === SCAN 3: PORTFOLIO STOCKS ===
    print("\n" + "=" * 80)
    print("SCAN 3 of 3: PORTFOLIO STOCKS")
    print("=" * 80 + "\n")

    print("Loading portfolio tickers from stocks.txt...")
    portfolio_tickers = get_portfolio_tickers()

    if portfolio_tickers:
        print(f"Found {len(portfolio_tickers)} portfolio stocks\n")

        start_time = datetime.now()
        portfolio_results = scan_stocks(
            portfolio_tickers,
            category="Portfolio",
            daily_bars=args.daily_bars,
            weekly_bars=args.weekly_bars,
            concurrency=args.concurrency,
        )
        portfolio_elapsed = (datetime.now() - start_time).total_seconds()

        if not portfolio_results.empty:
            # For portfolio, include ALL stocks (not just FULL HOLD + ADD)
            # But still create separate sheets by signal type
            print(
                f"\nðŸŽ¯ Portfolio: {len(portfolio_results)} stocks scanned (all included)"
            )

            # Count FULL HOLD + ADD for display
            portfolio_buy = filter_buy_signals(portfolio_results, "FULL HOLD + ADD")
            print(f"  - {len(portfolio_buy)} with FULL HOLD + ADD signal")

            # Save ALL portfolio results (not filtered)
            xlsx_path = results_dir / f"portfolio_scanner_{timestamp}.xlsx"
            pdf_path = results_dir / f"scanner_report_portfolio_{timestamp}.pdf"

            # Pass ALL results for portfolio
            create_portfolio_excel(portfolio_results, xlsx_path, category="Portfolio")

            # For PDF, still show FULL HOLD + ADD in detail (with all stocks in summary)
            if not portfolio_buy.empty:
                create_pdf_report(
                    portfolio_buy,
                    portfolio_results,
                    pdf_path,
                    timestamp,
                    category="Portfolio",
                )

            print(f"  âœ“ Excel: {xlsx_path.name}")
            print(f"  âœ“ PDF: {pdf_path.name}")
    else:
        print("âš ï¸  No portfolio tickers found in stocks.txt")

    # === FINAL SUMMARY ===
    total_elapsed = (datetime.now() - overall_start).total_seconds()

    print("\n" + "=" * 80)
    print("SCAN COMPLETE - SUMMARY")
    print("=" * 80)
    print(f"[TIME] Total time: {total_elapsed:.1f}s")
    print(f"\nðŸ“Š Results by Category:")

    if not sp500_results.empty:
        sp500_buy_count = len(filter_buy_signals(sp500_results, "FULL HOLD + ADD"))
        print(
            f"  S&P 500:     {sp500_buy_count:3d} FULL HOLD + ADD signals ({sp500_elapsed:.1f}s)"
        )

    if not nasdaq100_results.empty:
        nasdaq100_buy_count = len(
            filter_buy_signals(nasdaq100_results, "FULL HOLD + ADD")
        )
        print(
            f"  NASDAQ 100:  {nasdaq100_buy_count:3d} FULL HOLD + ADD signals ({nasdaq100_elapsed:.1f}s)"
        )

    if portfolio_tickers and not portfolio_results.empty:
        portfolio_buy_count = len(
            filter_buy_signals(portfolio_results, "FULL HOLD + ADD")
        )
        print(
            f"  Portfolio:   {portfolio_buy_count:3d} FULL HOLD + ADD signals ({portfolio_elapsed:.1f}s)"
        )

    # Cleanup old scans (keep 1 most recent per category)
    print("\nðŸ“ Managing scan history...")
    cleanup_old_scans(results_dir, max_files=1)
