"""Test full end-to-end portfolio analysis workflow"""
from pathlib import Path
from datetime import datetime
import pandas as pd
import technical_analysis as ta
from portfolio_reports import create_trading_playbook_pdf, create_portfolio_tracker_excel

print("=" * 80)
print("PORTFOLIO ANALYSIS V2.0 - END-TO-END TEST")
print("=" * 80)

# Setup
ROOT = Path.cwd()
RESULTS_DIR = ROOT / 'portfolio_results'
RESULTS_DIR.mkdir(exist_ok=True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M")

print(f"\n✓ Results directory: {RESULTS_DIR}")
print(f"✓ Timestamp: {TIMESTAMP}")

# Load portfolio configuration
print("\n" + "=" * 80)
print("STEP 1: Load Portfolio Configuration")
print("=" * 80)

stocks_file = ROOT / 'stocks.txt'
individual_tickers, baskets = ta.parse_stocks_file(stocks_file)
print(f"\nIndividual tickers: {individual_tickers}")

# Load holdings
holdings_file = ROOT / 'holdings.csv'
holdings_df = pd.read_csv(holdings_file)
print(f"\n✓ Loaded {len(holdings_df)} holdings")

# Load targets
targets_file = ROOT / 'targets.csv'
targets_df = pd.read_csv(targets_file)
if targets_df['target_pct'].max() > 1.0:
    targets_df['target_pct'] = targets_df['target_pct'] / 100.0
print(f"✓ Loaded {len(targets_df)} target allocations")

# Calculate initial portfolio total
PORTFOLIO_TOTAL = 0
for _, row in holdings_df.iterrows():
    if row['quantity'] > 0:
        PORTFOLIO_TOTAL += row['quantity'] * row['avg_cost']

print(f"✓ Portfolio total (avg cost): ${PORTFOLIO_TOTAL:,.0f}")

# Analyze stocks (limit to first 3 for speed)
print("\n" + "=" * 80)
print("STEP 2: Analyze Stocks (limiting to first 3 for test)")
print("=" * 80)

test_tickers = individual_tickers[:3]  # Just test first 3
results = []

for ticker in test_tickers:
    print(f"\nAnalyzing {ticker}...")
    try:
        result = ta.analyze_ticker(ticker)
        if result:
            results.append(result)
            print(f"  ✓ {result['signal']}")
        else:
            print(f"  ✗ No data")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print(f"\n✓ Analyzed {len(results)} stocks successfully")

# Calculate positions
print("\n" + "=" * 80)
print("STEP 3: Calculate Portfolio Positions")
print("=" * 80)

portfolio_positions = []

for result in results:
    ticker = result['ticker']

    # Get current holdings
    holding = holdings_df[holdings_df['ticker'] == ticker]
    if len(holding) > 0:
        quantity = holding.iloc[0]['quantity']
        min_quantity = holding.iloc[0].get('min_quantity', 0)
        current_value = quantity * result['current_price']
        tradeable_quantity = max(0, quantity - min_quantity)
        tradeable_value = tradeable_quantity * result['current_price']
    else:
        quantity = 0
        min_quantity = 0
        current_value = 0
        tradeable_quantity = 0
        tradeable_value = 0

    # Get target allocation
    target = targets_df[targets_df['ticker'] == ticker]
    if len(target) > 0:
        target_pct = target.iloc[0]['target_pct']
    else:
        target_pct = 0

    # Calculate gap using tradeable value
    position_gap = ta.calculate_position_gap(
        current_value=tradeable_value,
        target_pct=target_pct,
        portfolio_total=PORTFOLIO_TOTAL
    )
    gap_value = position_gap['gap_value']

    # Determine action
    action = ta.determine_portfolio_action(
        signal=result['signal'],
        position_gap=position_gap,
        buy_quality=result.get('buy_quality', 'UNKNOWN')
    )

    # Calculate tranches
    buy_tranches = []
    if action == 'BUY' and gap_value > 0:
        buy_tranches = ta.calculate_buy_tranches(
            gap_value=gap_value,
            s1=result.get('s1'),
            s2=result.get('s2'),
            s3=result.get('s3'),
            current_price=result['current_price'],
            buy_quality=result.get('buy_quality', 'UNKNOWN')
        )

    sell_tranches = []
    if action == 'SELL' and gap_value < 0:
        sell_tranches = ta.calculate_sell_tranches(
            signal=result['signal'],
            current_value=current_value,
            r1=result.get('r1'),
            r2=result.get('r2'),
            r3=result.get('r3')
        )

    position = {
        'ticker': ticker,
        'signal': result['signal'],
        'current_price': result['current_price'],
        'target_pct': target_pct,
        'current_value': current_value,
        'gap_value': gap_value,
        's1': result.get('s1'),
        's2': result.get('s2'),
        's3': result.get('s3'),
        'r1': result.get('r1'),
        'r2': result.get('r2'),
        'r3': result.get('r3'),
        'd50': result.get('d50'),
        'd100': result.get('d100'),
        'd200': result.get('d200'),
        'buy_quality': result.get('buy_quality'),
        'buy_quality_note': result.get('buy_quality_note'),
        'sell_feasibility_note': result.get('sell_feasibility_note'),
        'action': action,
        'buy_tranches': buy_tranches,
        'sell_tranches': sell_tranches
    }

    portfolio_positions.append(position)
    print(f"{ticker}: {action} (Gap: ${gap_value:+,.0f})")

print(f"\n✓ Calculated {len(portfolio_positions)} positions")

# Generate reports
print("\n" + "=" * 80)
print("STEP 4: Generate Reports")
print("=" * 80)

buy_count = sum(1 for p in portfolio_positions if p['action'] == 'BUY')
sell_count = sum(1 for p in portfolio_positions if p['action'] == 'SELL')
hold_count = sum(1 for p in portfolio_positions if p['action'] in ['HOLD', 'WAIT'])

portfolio_data = {
    'portfolio_total': PORTFOLIO_TOTAL,
    'positions': portfolio_positions,
    'summary': {
        'buy_count': buy_count,
        'sell_count': sell_count,
        'hold_count': hold_count
    }
}

# Generate PDF
print("\nGenerating Trading Playbook PDF...")
pdf_path = RESULTS_DIR / f'trading_playbook_{TIMESTAMP}.pdf'
create_trading_playbook_pdf(portfolio_data, pdf_path, TIMESTAMP)
print(f"✓ Created: {pdf_path.name}")

# Generate Excel
print("\nGenerating Portfolio Tracker Excel...")
excel_path = RESULTS_DIR / f'portfolio_tracker_{TIMESTAMP}.xlsx'
create_portfolio_tracker_excel(portfolio_data, excel_path)
print(f"✓ Created: {excel_path.name}")

print("\n" + "=" * 80)
print("✅ END-TO-END TEST COMPLETE")
print("=" * 80)
print(f"\nGenerated Files:")
print(f"  1. {pdf_path.name}")
print(f"  2. {excel_path.name}")
print(f"\nLocation: {RESULTS_DIR.absolute()}")
