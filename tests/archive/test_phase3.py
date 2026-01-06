"""Test Phase 3: Report Generation"""
from pathlib import Path
from portfolio_reports import create_trading_playbook_pdf, create_portfolio_tracker_excel
from datetime import datetime

print("=" * 80)
print("PHASE 3 TEST: Report Generation")
print("=" * 80)

# Create test portfolio data
portfolio_data = {
    'portfolio_total': 100000,
    'positions': [
        {
            'ticker': 'TSLA',
            'signal': 'FULL HOLD + ADD',
            'current_price': 450,
            'target_pct': 0.30,
            'current_value': 20000,
            'gap_value': 10000,
            's1': 440, 's2': 420, 's3': 400,
            'r1': 488, 'r2': 474, 'r3': 470,
            'd50': 430, 'd100': 410, 'd200': 390,
            'buy_quality': 'EXCELLENT',
            'buy_quality_note': 'All MAs support S1',
            'sell_feasibility_note': 'Clear path to all R-levels',
            'action': 'BUY',
            'buy_tranches': [
                (400, 4000, 'S3', 'Pending'),
                (420, 3500, 'S2', 'Pending'),
                (440, 2500, 'S1', 'Pending')
            ],
            'sell_tranches': []
        },
        {
            'ticker': 'NVDA',
            'signal': 'REDUCE',
            'current_price': 188,
            'target_pct': 0.15,
            'current_value': 20000,
            'gap_value': -5000,
            's1': 177, 's2': 170, 's3': 164,
            'r1': 212, 'r2': None, 'r3': None,
            'd50': 180, 'd100': 175, 'd200': 170,
            'buy_quality': 'GOOD',
            'buy_quality_note': 'D100 & D200 support S1',
            'sell_feasibility_note': 'Clear path to R1',
            'action': 'SELL',
            'buy_tranches': [],
            'sell_tranches': [
                (212, 4000, 0.20, 'R1', 'Pending'),
                (None, 3000, 0.15, 'R2', 'Pending'),
                (None, 1000, 0.05, 'R3', 'Pending')
            ]
        },
        {
            'ticker': 'BTC-USD',
            'signal': 'HOLD',
            'current_price': 95000,
            'target_pct': 0.20,
            'current_value': 20000,
            'gap_value': 0,
            's1': 90000, 's2': 85000, 's3': 80000,
            'r1': 100000, 'r2': 105000, 'r3': 110000,
            'd50': 92000, 'd100': 88000, 'd200': 82000,
            'buy_quality': 'GOOD',
            'buy_quality_note': 'D100 & D200 support S1',
            'sell_feasibility_note': 'Clear path to all R-levels',
            'action': 'HOLD',
            'buy_tranches': [],
            'sell_tranches': []
        }
    ],
    'summary': {
        'buy_count': 1,
        'sell_count': 1,
        'hold_count': 1
    }
}

# Create output directory
output_dir = Path('portfolio_results')
output_dir.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M")

# Generate PDF
print("\n=== Generating Trading Playbook PDF ===")
pdf_path = output_dir / f'trading_playbook_{timestamp}.pdf'
create_trading_playbook_pdf(portfolio_data, pdf_path, timestamp)
print(f"✓ Created: {pdf_path}")

# Generate Excel
print("\n=== Generating Portfolio Tracker Excel ===")
excel_path = output_dir / f'portfolio_tracker_{timestamp}.xlsx'
create_portfolio_tracker_excel(portfolio_data, excel_path)
print(f"✓ Created: {excel_path}")

print("\n" + "=" * 80)
print("✅ Phase 3 Complete!")
print("=" * 80)
print("\nGenerated Files:")
print(f"  1. {pdf_path.name}")
print(f"  2. {excel_path.name}")
print(f"\nLocation: {output_dir.absolute()}")
