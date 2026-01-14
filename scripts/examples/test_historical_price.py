"""
Quick test to verify historical price fetching is working correctly
Tests that as_of_date properly limits data to historical dates
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from technical_analysis import analyze_ticker


def test_historical_prices():
    """Test a few known tickers on historical dates"""

    test_cases = [
        {
            "ticker": "QCOM",
            "date": "2024-01-01",
            "expected_range": (135, 150),  # Approximate expected price range
            "description": "QCOM on Jan 1, 2024 (should be ~$142)",
        },
        {
            "ticker": "AAPL",
            "date": "2024-01-01",
            "expected_range": (180, 195),  # Approximate expected price range
            "description": "AAPL on Jan 1, 2024 (should be ~$185)",
        },
        {
            "ticker": "MSFT",
            "date": "2024-01-01",
            "expected_range": (365, 380),  # Approximate expected price range
            "description": "MSFT on Jan 1, 2024 (should be ~$370)",
        },
    ]

    print("=" * 80)
    print("TESTING HISTORICAL PRICE ACCURACY")
    print("=" * 80)
    print()

    all_passed = True

    for test in test_cases:
        ticker = test["ticker"]
        as_of_date = test["date"]
        expected_min, expected_max = test["expected_range"]

        print(f"Testing: {test['description']}")
        print(f"  Fetching data for {ticker} as of {as_of_date}...")

        result = analyze_ticker(
            ticker, daily_bars=60, weekly_bars=52, as_of_date=as_of_date
        )

        if "error" in result:
            print(f"  ❌ ERROR: {result['error']}")
            all_passed = False
            continue

        current_price = result.get("current_price")

        if current_price is None:
            print(f"  ❌ ERROR: No price returned")
            all_passed = False
            continue

        print(f"  Price returned: ${current_price:.2f}")

        # Check if price is in expected range
        if expected_min <= current_price <= expected_max:
            print(
                f"  ✅ PASS - Price is in expected range (${expected_min}-${expected_max})"
            )
        else:
            print(
                f"  ❌ FAIL - Price ${current_price:.2f} is outside expected range (${expected_min}-${expected_max})"
            )
            print(
                f"     This likely means the fix didn't work and current prices are being used"
            )
            all_passed = False

        # Show some calculated values to verify they're reasonable
        if "volatility_stop" in result:
            vol_stop = result["volatility_stop"]
            vol_stop_expected = current_price * 0.95  # 5% stop
            print(
                f"  Volatility Stop: ${vol_stop:.2f} (should be ~${vol_stop_expected:.2f})"
            )

        if "nearest_support" in result and result["nearest_support"]:
            support = result["nearest_support"]["price"]
            print(
                f"  Nearest Support: ${support:.2f} (should be < ${current_price:.2f})"
            )

        print()

    print("=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Historical data is being fetched correctly!")
        print("You can now safely regenerate historical reports.")
    else:
        print(
            "❌ SOME TESTS FAILED - There may still be issues with historical data fetching."
        )
        print("Review the errors above before regenerating reports.")
    print("=" * 80)

    return all_passed


if __name__ == "__main__":
    test_historical_prices()
