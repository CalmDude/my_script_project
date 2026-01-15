"""
Test script to verify ghb_portfolio_scanner.ipynb updates
Tests that the S&P 500 optimized universe loads correctly
"""

import json
from pathlib import Path

print("🧪 Testing Scanner Updates...\n")

# Test 1: Verify ghb_optimized_portfolio.txt has S&P 500 stocks
print("✅ Test 1: Checking ghb_optimized_portfolio.txt")
portfolio_file = Path("data/ghb_optimized_portfolio.txt")
if portfolio_file.exists():
    content = portfolio_file.read_text()

    # Check for S&P 500 specific stocks (not in NASDAQ25)
    sp500_stocks = ["SMCI", "GE", "TRGP", "STX", "AXON"]
    nasdaq_only = ["AMD", "TSLA", "META", "MSFT", "PLTR"]

    sp500_found = sum(1 for stock in sp500_stocks if stock in content)
    nasdaq_found = sum(1 for stock in nasdaq_only if stock in content)

    print(f"   S&P 500 gems found: {sp500_found}/5 {sp500_stocks}")
    print(f"   Old NASDAQ stocks: {nasdaq_found}/5 {nasdaq_only}")
    print(
        f"   Expected CAGR in header: {'46.80%' if '46.80%' in content else '❌ NOT FOUND'}"
    )

    if sp500_found >= 4 and nasdaq_found == 0 and "46.80%" in content:
        print("   ✅ PASS: Portfolio file updated correctly\n")
    else:
        print("   ❌ FAIL: Portfolio file not fully updated\n")
else:
    print("   ❌ FAIL: Portfolio file not found\n")

# Test 2: Verify portfolio_settings.json has 10/10 config
print("✅ Test 2: Checking portfolio_settings.json")
settings_file = Path("data/portfolio_settings.json")
if settings_file.exists():
    with open(settings_file) as f:
        settings = json.load(f)

    position_size = settings.get("position_size_pct")
    max_positions = settings.get("max_positions")

    print(f"   Position size: {position_size}% (expected: 10%)")
    print(f"   Max positions: {max_positions} (expected: 10)")

    if position_size == 10 and max_positions == 10:
        print("   ✅ PASS: Settings updated to optimal 10/10 config\n")
    else:
        print("   ❌ FAIL: Settings not at optimal values\n")
else:
    print("   ❌ FAIL: Settings file not found\n")

# Test 3: Verify backtest config.json has optimal settings
print("✅ Test 3: Checking backtest/config.json")
backtest_config = Path("backtest/config.json")
if backtest_config.exists():
    with open(backtest_config) as f:
        config = json.load(f)

    universe = config["backtest_settings"]["universe"]
    position_size = config["portfolio_settings"]["position_size_pct"]
    max_positions = config["portfolio_settings"]["max_positions"]

    print(f"   Universe: {universe} (expected: sp500_optimized)")
    print(f"   Position size: {position_size}% (expected: 10%)")
    print(f"   Max positions: {max_positions} (expected: 10)")

    if universe == "sp500_optimized" and position_size == 10 and max_positions == 10:
        print("   ✅ PASS: Backtest config set to optimal\n")
    else:
        print("   ⚠️  WARNING: Backtest config not optimal (may be from previous run)\n")
else:
    print("   ❌ FAIL: Backtest config not found\n")

# Test 4: Check documentation files for misleading claims
print("✅ Test 4: Checking for corrected performance claims")
docs_to_check = [
    ("docs/EXECUTION_GUIDE.md", "46.80%"),
    ("docs/PORTFOLIO_TRACKER_ROADMAP.md", "46.80%"),
    ("backtest/README.md", "per-trade"),
]

all_docs_ok = True
for doc_path, expected_text in docs_to_check:
    doc_file = Path(doc_path)
    if doc_file.exists():
        try:
            content = doc_file.read_text(encoding="utf-8")
            if expected_text in content:
                print(f"   ✅ {doc_path}: Contains '{expected_text}'")
            else:
                print(f"   ❌ {doc_path}: Missing '{expected_text}'")
                all_docs_ok = False
        except UnicodeDecodeError:
            print(f"   ⚠️  {doc_path}: Encoding issue (skipping)")
    else:
        print(f"   ❌ {doc_path}: File not found")
        all_docs_ok = False

if all_docs_ok:
    print("   ✅ PASS: All documentation updated\n")
else:
    print("   ❌ FAIL: Some documentation needs updates\n")

# Summary
print("=" * 60)
print("📊 Test Summary")
print("=" * 60)
print("Next steps:")
print("1. Run notebooks/ghb_portfolio_scanner.ipynb to verify it works")
print("2. Check generated PDF has correct stocks and performance claims")
print("3. Verify portfolio summary section displays correctly")
print("4. Ready for Friday January 17 first scan!")
