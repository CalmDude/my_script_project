"""
Run Unbiased Backtest - Complete Workflow
Screens 2020 data, then backtests 2021-2025, then compares with biased results
"""

import subprocess
import sys
from pathlib import Path


def run_script(script_name, description):
    """Run a Python script and return success status"""
    print("\n" + "=" * 100)
    print(f"STEP: {description}")
    print("=" * 100)

    try:
        result = subprocess.run(
            [sys.executable, f"backtest/{script_name}"],
            check=True,
            capture_output=False,
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Script not found: backtest/{script_name}")
        return False


def main():
    """Run complete unbiased backtest workflow"""
    print("=" * 100)
    print("UNBIASED BACKTEST WORKFLOW")
    print("=" * 100)
    print("\nThis will:")
    print("1. Get historical S&P 500 constituents (Jan 1, 2021)")
    print("2. Screen stocks using 2020 data only")
    print("3. Run backtest on 2021-2025 with unbiased universe")
    print("4. Compare biased vs unbiased results")
    print("\n⏰ Estimated time: 20-30 minutes")
    print("\n" + "=" * 100)

    # Step 1: Get historical S&P 500
    if not run_script("get_historical_sp500.py", "Get Historical S&P 500 (Jan 2021)"):
        return

    # Step 2: Screen using 2020 data
    print(
        "\n⏰ Next step will take 15-20 minutes (downloading 2019-2020 data for ~300 stocks)"
    )
    input("\nPress Enter to continue or Ctrl+C to cancel...")

    if not run_script("screen_unbiased_2020.py", "Screen Stocks Using 2020 Data Only"):
        return

    # Step 3: Check if universe file was created
    universe_file = Path("backtest/data/sp500_unbiased_2020.txt")
    if not universe_file.exists():
        print(f"\n❌ Universe file not created: {universe_file}")
        return

    # Step 4: Update config to use unbiased universe
    print("\n" + "=" * 100)
    print("STEP: Update Config for Unbiased Backtest")
    print("=" * 100)

    import json

    config_file = Path("backtest/config.json")

    with open(config_file, "r") as f:
        config = json.load(f)

    # Backup original universe
    original_universe = config["backtest_settings"]["universe"]

    # Set to unbiased universe
    config["backtest_settings"]["universe"] = "sp500_unbiased_2020"

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"✅ Config updated: universe = sp500_unbiased_2020")
    print(f"   (Original: {original_universe})")

    # Step 5: Run unbiased backtest
    print("\n⏰ Running backtest on 2021-2025 with unbiased universe...")

    if not run_script("run_backtest.py", "Run Unbiased Backtest (2021-2025)"):
        # Restore original config
        config["backtest_settings"]["universe"] = original_universe
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        return

    # Step 6: Restore original config
    config["backtest_settings"]["universe"] = original_universe
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n✅ Config restored: universe = {original_universe}")

    # Step 7: Compare results
    if not run_script(
        "compare_biased_vs_unbiased.py", "Compare Biased vs Unbiased Results"
    ):
        return

    # Summary
    print("\n\n" + "=" * 100)
    print("✅ UNBIASED BACKTEST WORKFLOW COMPLETE")
    print("=" * 100)
    print("\n📊 Results saved in: backtest/results/")
    print("📄 Check comparison output above for bias impact analysis")
    print("\n🎯 Key Takeaways:")
    print("   - Biased CAGR includes survivorship + optimization bias")
    print("   - Unbiased CAGR is realistic for forward testing")
    print("   - Use unbiased metrics for strategy expectations")
    print("\n" + "=" * 100)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Workflow interrupted by user")
        sys.exit(1)
