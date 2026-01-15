"""
Show full technical details for QCOM on 2024-01-01
"""

import sys
from pathlib import Path
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from technical_analysis import analyze_ticker


def show_qcom_details():
    """Show all technical details for QCOM on historical date"""

    ticker = "QCOM"
    as_of_date = "2024-01-01"

    print("=" * 80)
    print(f"FULL TECHNICAL ANALYSIS: {ticker} as of {as_of_date}")
    print("=" * 80)
    print()

    result = analyze_ticker(
        ticker, daily_bars=60, weekly_bars=52, as_of_date=as_of_date
    )

    if "error" in result:
        print(f"ERROR: {result['error']}")
        return

    # Price & Basic Info
    print("PRICE INFORMATION:")
    print(f"  Current Price: ${result.get('current_price', 'N/A'):.2f}")
    print()

    # Moving Averages
    print("MOVING AVERAGES:")
    print(
        f"  D50:  ${result.get('d50', 'N/A'):.2f}"
        if result.get("d50")
        else "  D50:  N/A"
    )
    print(
        f"  D100: ${result.get('d100', 'N/A'):.2f}"
        if result.get("d100")
        else "  D100: N/A"
    )
    print(
        f"  D200: ${result.get('d200', 'N/A'):.2f}"
        if result.get("d200")
        else "  D200: N/A"
    )
    print()

    # Momentum Indicators
    print("MOMENTUM INDICATORS:")
    print(
        f"  RSI: {result.get('rsi', 'N/A'):.1f}" if result.get("rsi") else "  RSI: N/A"
    )
    print(f"  Daily State: {result.get('daily_state', 'N/A')}")
    print(f"  Weekly State: {result.get('weekly_state', 'N/A')}")
    print(f"  Signal: {result.get('signal', 'N/A')}")
    print()

    # Bollinger Bands
    print("BOLLINGER BANDS:")
    print(
        f"  Upper: ${result.get('bb_upper', 'N/A'):.2f}"
        if result.get("bb_upper")
        else "  Upper: N/A"
    )
    print(
        f"  Middle: ${result.get('bb_middle', 'N/A'):.2f}"
        if result.get("bb_middle")
        else "  Middle: N/A"
    )
    print(
        f"  Lower: ${result.get('bb_lower', 'N/A'):.2f}"
        if result.get("bb_lower")
        else "  Lower: N/A"
    )
    print(
        f"  Position (σ): {result.get('bb_position_sigma', 'N/A'):.2f}"
        if result.get("bb_position_sigma") is not None
        else "  Position (σ): N/A"
    )
    print()

    # Volatility
    print("VOLATILITY:")
    print(
        f"  Daily Range: {result.get('volatility_pct', 'N/A'):.2f}%"
        if result.get("volatility_pct")
        else "  Daily Range: N/A"
    )
    print(f"  Volatility Label: {result.get('volatility_label', 'N/A')}")
    print(
        f"  Volatility Stop (5%): ${result.get('volatility_stop', 'N/A'):.2f}"
        if result.get("volatility_stop")
        else "  Volatility Stop: N/A"
    )
    print(
        f"  Volatility Stop Loss: {result.get('volatility_stop_loss_pct', 'N/A'):.1f}%"
        if result.get("volatility_stop_loss_pct")
        else "  Volatility Stop Loss: N/A"
    )
    print()

    # Volume Profile
    print("VOLUME PROFILE (60 Day):")
    print(
        f"  POC: ${result.get('poc_60d', 'N/A'):.2f}"
        if result.get("poc_60d")
        else "  POC: N/A"
    )
    print(
        f"  VAH: ${result.get('vah_60d', 'N/A'):.2f}"
        if result.get("vah_60d")
        else "  VAH: N/A"
    )
    print(
        f"  VAL: ${result.get('val_60d', 'N/A'):.2f}"
        if result.get("val_60d")
        else "  VAL: N/A"
    )
    print()

    print("VOLUME PROFILE (52 Week):")
    print(
        f"  POC: ${result.get('poc_52w', 'N/A'):.2f}"
        if result.get("poc_52w")
        else "  POC: N/A"
    )
    print(
        f"  VAH: ${result.get('vah_52w', 'N/A'):.2f}"
        if result.get("vah_52w")
        else "  VAH: N/A"
    )
    print(
        f"  VAL: ${result.get('val_52w', 'N/A'):.2f}"
        if result.get("val_52w")
        else "  VAL: N/A"
    )
    print()

    # Supports
    print("SUPPORTS (Top 3):")
    supports = result.get("daily_supports", [])[:3]
    if supports:
        for i, sup in enumerate(supports, 1):
            dist_pct = (
                (result["current_price"] - sup["price"]) / result["current_price"]
            ) * 100
            print(
                f"  S{i}: ${sup['price']:.2f} ({dist_pct:.1f}% below) - {sup.get('quality', 'N/A')}"
            )
    else:
        print("  No supports found")
    print()

    # Resistances
    print("RESISTANCES (Top 3):")
    resistances = result.get("daily_resistances", [])[:3]
    if resistances:
        for i, res in enumerate(resistances, 1):
            dist_pct = (
                (res["price"] - result["current_price"]) / result["current_price"]
            ) * 100
            print(
                f"  R{i}: ${res['price']:.2f} ({dist_pct:.1f}% above) - {res.get('quality', 'N/A')}"
            )
    else:
        print("  No resistances found")
    print()

    # Entry Quality
    print("ENTRY ANALYSIS:")
    print(f"  Buy Quality: {result.get('buy_quality', 'N/A')}")
    print(f"  Entry Quality: {result.get('entry_quality', 'N/A')}")
    print(f"  Entry Flag: {result.get('entry_flag', 'N/A')}")
    print(f"  Accessible Supports: {result.get('accessible_supports_count', 'N/A')}")
    print(f"  Good Supports: {result.get('good_supports_count', 'N/A')}")
    print()

    # Risk/Reward
    print("RISK/REWARD:")
    print(
        f"  Target R1: ${result.get('target_r1', 'N/A'):.2f}"
        if result.get("target_r1")
        else "  Target R1: N/A"
    )
    if result.get("target_r1") and result.get("current_price"):
        gain_pct = (
            (result["target_r1"] - result["current_price"]) / result["current_price"]
        ) * 100
        print(f"  Gain to R1: +{gain_pct:.1f}%")
    print(
        f"  Vol R:R: {result.get('vol_risk_reward', 'N/A'):.1f}:1"
        if result.get("vol_risk_reward")
        else "  Vol R:R: N/A"
    )
    print()

    # Nearest Support Details
    print("NEAREST SUPPORT DETAILS:")
    nearest = result.get("nearest_support")
    if nearest:
        print(f"  Price: ${nearest['price']:.2f}")
        print(f"  Distance: {nearest.get('distance_pct', 'N/A'):.1f}%")
        print(f"  Quality: {nearest.get('quality', 'N/A')}")
        print(f"  Type: {nearest.get('type', 'N/A')}")
    else:
        print("  No nearest support")
    print()

    # Stop Loss Info
    print("STOP LOSS RECOMMENDATIONS:")
    print(
        f"  8% Stop Tolerance: ${result.get('stop_tolerance_8pct', 'N/A'):.2f}"
        if result.get("stop_tolerance_8pct")
        else "  8% Stop: N/A"
    )
    print()

    print("=" * 80)
    print("RAW DATA (JSON):")
    print("=" * 80)
    # Convert to JSON for complete view
    clean_result = {k: v for k, v in result.items() if not k.startswith("_")}
    print(json.dumps(clean_result, indent=2, default=str))


if __name__ == "__main__":
    show_qcom_details()
