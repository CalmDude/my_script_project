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

def cleanup_old_scans(results_dir, max_files=1, archive_retention_days=60):
    """
    Keep only the most recent scan files (both Excel and PDF), move older ones to archive
    Delete archive files older than archive_retention_days (default: 60 days)
    """
    from datetime import datetime, timedelta
    import time

    archive_dir = results_dir / 'archive'
    archive_dir.mkdir(exist_ok=True)

    # Get all xlsx and pdf files in results directory (not archive)
    xlsx_files = sorted(results_dir.glob('sp500_analysis_*.xlsx'), key=lambda p: p.stat().st_mtime, reverse=True)
    pdf_files = sorted(results_dir.glob('scanner_report_*.pdf'), key=lambda p: p.stat().st_mtime, reverse=True)

    total_archived = 0

    # Move files beyond max_files to archive
    for old_file in xlsx_files[max_files:]:
        archive_path = archive_dir / old_file.name
        old_file.rename(archive_path)
        print(f"  📦 Archived: {old_file.name}")
        total_archived += 1

    for old_file in pdf_files[max_files:]:
        archive_path = archive_dir / old_file.name
        old_file.rename(archive_path)
        print(f"  📦 Archived: {old_file.name}")
        total_archived += 1

    if total_archived > 0:
        print(f"  ✅ Archived {total_archived} file(s), kept {max_files} most recent")
    else:
        print(f"  ✅ No files to archive (only {max_files} most recent exist)")

    # Delete archive files older than retention period
    cutoff_time = time.time() - (archive_retention_days * 86400)  # 86400 seconds per day
    deleted_count = 0

    for archive_file in archive_dir.glob('*'):
        if archive_file.is_file() and archive_file.stat().st_mtime < cutoff_time:
            try:
                archive_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"  ⚠️  Could not delete {archive_file.name}: {e}")

    if deleted_count > 0:
        print(f"  🗑️  Deleted {deleted_count} archive file(s) older than {archive_retention_days} days")

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

def create_pdf_report(buy_df, all_results_df, output_file, timestamp_str):
    """
    Create comprehensive PDF research document for BALANCED opportunities
    """
    if buy_df.empty:
        print("No data to create PDF report")
        return

    # Filter dataframes
    balanced_df = buy_df[buy_df['confluence'] == 'BALANCED'].sort_values('ticker')
    extended_df = buy_df[buy_df['confluence'] == 'EXTENDED'].sort_values('ticker')

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
    cover_title = f"S&P 500 Scanner Report<br/><font size=14>{datetime.now().strftime('%B %d, %Y, %I:%M %p')}</font>"
    elements.append(Paragraph(cover_title, title_style))
    elements.append(Spacer(1, 0.3*inch))

    cover_text = f"""
    <b>Analysis Parameters:</b><br/>
    • Total S&P 500 stocks analyzed: {len(all_results_df)}<br/>
    • FULL HOLD + ADD signals found: {len(buy_df)} ({len(buy_df)/len(all_results_df)*100:.1f}%)<br/>
    <br/>
    <b>Confluence Breakdown:</b><br/>
    • <b>{len(balanced_df)} BALANCED</b> ({len(balanced_df)/len(all_results_df)*100:.1f}%) - Priority buy candidates<br/>
    • {len(extended_df)} EXTENDED ({len(extended_df)/len(all_results_df)*100:.1f}%) - Wait for pullback<br/>
    • {len(buy_df[buy_df['confluence'] == 'WEAK'])} WEAK - Skip (poor setup)<br/>
    <br/>
    <b>This Report Focus:</b><br/>
    Detailed analysis of the {len(balanced_df)} BALANCED stocks with:<br/>
    ✓ Strongest bullish signal (Weekly P1 + Daily P1)<br/>
    ✓ Healthy technical setup (not overbought)<br/>
    ✓ Clear entry zones and risk management<br/>
    <br/>
    <i>Purpose: Research and evaluation tool for potential portfolio additions</i>
    """
    elements.append(Paragraph(cover_text, styles['Normal']))
    elements.append(PageBreak())

    # === SECTION 1: BALANCED OVERVIEW TABLE ===
    elements.append(Paragraph("BALANCED Opportunities Overview", section_style))
    elements.append(Spacer(1, 0.1*inch))

    if not balanced_df.empty:
        overview_text = f"<b>{len(balanced_df)} stocks</b> with FULL HOLD + ADD signal and BALANCED confluence (healthy technical setup).<br/><br/>"
        elements.append(Paragraph(overview_text, styles['Normal']))

        # Create summary table
        table_data = [['Ticker', 'Price', 'D50', 'D200', 'W10', 'Entry Zone']]
        for _, row in balanced_df.head(15).iterrows():  # Show first 15 in summary
            ticker = row['ticker']
            price = f"${row['current_price']:.2f}" if not pd.isna(row['current_price']) else 'N/A'
            d50 = f"${row['d50']:.0f}" if not pd.isna(row.get('d50')) else 'N/A'
            d200 = f"${row['d200']:.0f}" if not pd.isna(row.get('d200')) else 'N/A'
            w10 = f"${row['w10']:.0f}" if not pd.isna(row.get('w10')) else 'N/A'
            entry = f"${row['d50']*0.97:.0f}-${row['current_price']:.0f}" if not pd.isna(row.get('d50')) else 'N/A'
            table_data.append([ticker, price, d50, d200, w10, entry])

        if len(balanced_df) > 15:
            table_data.append(['...', f'+{len(balanced_df)-15} more', '...', '...', '...', 'See details'])

        overview_table = Table(table_data, colWidths=[0.8*inch, 0.9*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1.2*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980b9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(overview_table)

    elements.append(PageBreak())

    # === SECTION 2: DETAILED ANALYSIS (1 page per BALANCED stock) ===
    for idx, row in balanced_df.iterrows():
        ticker = row['ticker']
        price = row['current_price']
        signal = row['signal']
        confluence = row['confluence']

        # Stock header
        stock_title = f"{ticker}<br/><font size=10>${price:.2f} | {signal} | {confluence}</font>"
        elements.append(Paragraph(stock_title, title_style))
        elements.append(Spacer(1, 0.1*inch))

        # Why BALANCED section
        d50 = row.get('d50', 0)
        d200 = row.get('d200', 0)
        w10 = row.get('w10', 0)
        daily_poc = row.get('daily_poc', 0)
        daily_val = row.get('daily_val', 0)
        daily_vah = row.get('daily_vah', 0)

        # Check actual conditions
        in_value_area = (daily_val <= price <= daily_vah) if not pd.isna(daily_val) and not pd.isna(daily_vah) else False
        near_poc = (price >= daily_poc * 0.95) if not pd.isna(daily_poc) else False
        above_d50 = (price >= d50) if not pd.isna(d50) else False
        above_w10 = (price >= w10) if not pd.isna(w10) else False

        check_mark = lambda cond: "✓" if cond else "✗"

        why_balanced = f"""
        <b>Why BALANCED? (Confluence Check)</b><br/>
        {check_mark(in_value_area)} Inside Value Area: ${daily_val:.0f} ≤ ${price:.2f} ≤ ${daily_vah:.0f}<br/>
        {check_mark(near_poc)} Near POC Support: ${price:.2f} ≥ ${daily_poc:.0f}<br/>
        {check_mark(above_d50)} Above D50: ${price:.2f} vs ${d50:.0f}<br/>
        {check_mark(above_w10)} Above W10: ${price:.2f} vs ${w10:.0f}<br/>
        <br/>
        <b>Status:</b> Healthy setup, not overbought, safe entry zone
        """
        elements.append(Paragraph(why_balanced, styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))

        # Entry strategy - Use actual support levels in descending order
        entry_title = Paragraph("<b>Entry Strategy (3 Zones)</b>", section_style)
        elements.append(entry_title)

        # Zone 1: Near current price (1% below)
        zone1_high = price
        zone1_low = price * 0.99

        # Zone 2: Lower Value Area or near D50
        zone2_high = zone1_low
        zone2_low = min(daily_val if not pd.isna(daily_val) else d50, d50) if not pd.isna(d50) else price * 0.95

        # Zone 3: D200 area (strongest support)
        zone3_high = zone2_low
        zone3_low = d200 * 1.02 if not pd.isna(d200) else price * 0.90

        entry_text = f"""
        <b>Zone 1 (Aggressive):</b> ${zone1_low:.2f}-${zone1_high:.2f} (current area, near support)<br/>
        <b>Zone 2 (Patient):</b> ${zone2_low:.2f}-${zone2_high:.2f} (pullback to stronger support)<br/>
        <b>Zone 3 (Deep Value):</b> ${zone3_low:.2f}-${zone3_high:.2f} (near major support)<br/>
        <br/>
        <b>Recommendation:</b> Scale in across zones, don't chase. Build position gradually.
        """
        elements.append(Paragraph(entry_text, styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))

        # Risk management
        stop_price = d200 * 0.95 if not pd.isna(d200) else price * 0.85
        elements.append(Paragraph("<b>Risk Management</b>", section_style))
        risk_text = f"""
        <b>Suggested Stop:</b> ${stop_price:.2f} (5% below D200, major support break)<br/>
        <b>Risk per entry:</b> Max 2% of portfolio per zone<br/>
        <b>Position sizing:</b> Build across 3 entries, average down on weakness
        """
        elements.append(Paragraph(risk_text, styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))

        # Upside targets - Get resistances and sort them correctly (closest first)
        r1 = row.get('r1', price * 1.05)
        r2 = row.get('r2', price * 1.10)
        r3 = row.get('r3', price * 1.15)

        # Sort resistances in ascending order (R1 should be closest/lowest)
        resistances = sorted([r1, r2, r3])
        r1_sorted, r2_sorted, r3_sorted = resistances[0], resistances[1], resistances[2]

        elements.append(Paragraph("<b>Upside Targets (Resistance Map)</b>", section_style))
        targets_text = f"""
        <b>R1:</b> ${r1_sorted:.2f} ({(r1_sorted/price-1)*100:.1f}% gain) - First profit target<br/>
        <b>R2:</b> ${r2_sorted:.2f} ({(r2_sorted/price-1)*100:.1f}% gain) - Major resistance<br/>
        <b>R3:</b> ${r3_sorted:.2f} ({(r3_sorted/price-1)*100:.1f}% gain) - Full rally target<br/>
        <br/>
        <b>Strategy:</b> Take partial profits at each level, trail stops higher
        """
        elements.append(Paragraph(targets_text, styles['Normal']))
        elements.append(Spacer(1, 0.15*inch))

        # Technical structure table
        elements.append(Paragraph("<b>Technical Structure</b>", section_style))
        tech_data = [
            ['Level', 'Price', 'Type', 'Note'],
            ['R3', f"${r3_sorted:.2f}", 'Major Resistance', 'Full rally target'],
            ['R2', f"${r2_sorted:.2f}", 'Key Resistance', 'Strong profit zone'],
            ['R1', f"${r1_sorted:.2f}", 'Minor Resistance', 'First exit'],
            ['Current', f"${price:.2f}", 'Market Price', 'Entry consideration'],
            ['POC', f"${daily_poc:.2f}" if not pd.isna(daily_poc) else 'N/A', 'Volume Node', 'Support'],
            ['D50', f"${d50:.2f}" if not pd.isna(d50) else 'N/A', 'MA Support', 'Short-term trend'],
            ['D200', f"${d200:.2f}" if not pd.isna(d200) else 'N/A', 'Major Support', 'Long-term floor'],
        ]

        tech_table = Table(tech_data, colWidths=[1.0*inch, 1.0*inch, 1.5*inch, 2.0*inch])
        tech_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2980b9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('BACKGROUND', (0, 4), (-1, 4), colors.lightyellow),  # Highlight current price
        ]))
        elements.append(tech_table)

        elements.append(PageBreak())

    # === SECTION 3: EXTENDED WATCH LIST ===
    if not extended_df.empty:
        elements.append(Paragraph(f"EXTENDED Watch List ({len(extended_df)} stocks)", section_style))
        elements.append(Spacer(1, 0.1*inch))

        watch_text = """
        <b>These stocks have FULL HOLD + ADD signals but are technically overbought.</b><br/>
        Wait for pullback to support levels before entering.<br/><br/>
        """
        elements.append(Paragraph(watch_text, styles['Normal']))

        # Extended table (show first 20)
        extended_data = [['Ticker', 'Price', 'D50', 'Pullback Target', 'Status']]
        for _, row in extended_df.head(20).iterrows():
            ticker = row['ticker']
            price = f"${row['current_price']:.2f}"
            d50 = f"${row['d50']:.0f}" if not pd.isna(row.get('d50')) else 'N/A'
            target = f"${row['d50']:.0f}" if not pd.isna(row.get('d50')) else 'N/A'
            pct_above = ((row['current_price']/row['d50']-1)*100) if not pd.isna(row.get('d50')) else 0
            status = f"{pct_above:.1f}% above D50"
            extended_data.append([ticker, price, d50, target, status])

        if len(extended_df) > 20:
            extended_data.append(['...', f'+{len(extended_df)-20} more', '...', '...', 'See Excel'])

        extended_table = Table(extended_data, colWidths=[0.8*inch, 1.0*inch, 0.9*inch, 1.2*inch, 1.5*inch])
        extended_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e67e22')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(extended_table)

        elements.append(PageBreak())

    # === SECTION 4: METHODOLOGY ===
    elements.append(Paragraph("Scan Methodology & Definitions", section_style))
    elements.append(Spacer(1, 0.1*inch))

    methodology_text = """
    <b>FULL HOLD + ADD Signal:</b><br/>
    • Weekly Larsson State = +1 (P1 Bullish trend)<br/>
    • Daily Larsson State = +1 (P1 Bullish trend)<br/>
    • Both timeframes in maximum bullish alignment<br/>
    <br/>
    <b>BALANCED Confluence:</b><br/>
    Stock must meet all 4 criteria:<br/>
    1. Inside Value Area (not outside institutional range)<br/>
    2. At or above POC (volume-supported price)<br/>
    3. Above 50-day MA (short-term uptrend intact)<br/>
    4. Above 10-week MA (weekly trend confirmed)<br/>
    <br/>
    <b>Why EXTENDED is excluded:</b><br/>
    Stock is technically overbought despite strong signal. Wait for pullback to avoid buying tops.<br/>
    <br/>
    <b>Why WEAK is excluded:</b><br/>
    Despite bullish signal, technical setup is poor (outside value area, below key MAs).<br/>
    <br/>
    <b>How to use this report:</b><br/>
    1. Review BALANCED stocks for research<br/>
    2. Compare entry zones with current market prices<br/>
    3. Use stop levels for risk management<br/>
    4. Scale into positions across 3 zones<br/>
    5. Monitor EXTENDED list for pullback opportunities<br/>
    <br/>
    <b>Disclaimer:</b> This is a technical analysis tool for research purposes only.
    Not financial advice. Do your own due diligence before investing.
    """
    elements.append(Paragraph(methodology_text, styles['Normal']))

    # Build PDF
    doc.build(elements)
    print(f"✓ PDF report created: {output_file}")
    print(f"  - {len(balanced_df)} BALANCED stocks detailed")
    print(f"  - {len(extended_df)} EXTENDED stocks in watch list")

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

            # Create PDF report
            pdf_filename = f"scanner_report_{timestamp_str}.pdf"
            pdf_path = results_dir / pdf_filename
            print(f"\n📄 Creating PDF research document...")
            create_pdf_report(buy_df, results_df, pdf_path, timestamp_str)

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
