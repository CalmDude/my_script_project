import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import time
import random
import json
from pathlib import Path
import hashlib
import logging

# Configure logging
logger = logging.getLogger(__name__)

# ============================================================================
# CACHING SYSTEM - Prevents rate limiting by caching results for 24 hours
# ============================================================================

# Determine project root (go up from src/ to portfolio_analyser/)
_MODULE_DIR = Path(__file__).parent
_PROJECT_ROOT = _MODULE_DIR.parent
CACHE_DIR = _PROJECT_ROOT / ".scanner_cache"
CACHE_TTL_HOURS = 24


def _get_cache_path(ticker, daily_bars, weekly_bars):
    """Generate cache file path for a ticker with specific parameters"""
    CACHE_DIR.mkdir(exist_ok=True)
    cache_key = f"{ticker}_{daily_bars}_{weekly_bars}"
    return CACHE_DIR / f"{cache_key}.json"


def _load_from_cache(ticker, daily_bars, weekly_bars):
    """Load cached result if it exists and is not expired"""
    cache_path = _get_cache_path(ticker, daily_bars, weekly_bars)

    if not cache_path.exists():
        return None

    try:
        with open(cache_path, "r") as f:
            cached = json.load(f)

        # Check if cache is expired
        cached_time = datetime.fromisoformat(cached["cached_at"])
        age_hours = (datetime.now() - cached_time).total_seconds() / 3600

        if age_hours > CACHE_TTL_HOURS:
            cache_path.unlink()  # Delete expired cache
            return None

        return cached["data"]
    except (IOError, json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Cache read failed for {ticker}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected cache read error for {ticker}: {e}")
        return None


def _save_to_cache(ticker, daily_bars, weekly_bars, data):
    """Save analysis result to cache"""
    cache_path = _get_cache_path(ticker, daily_bars, weekly_bars)

    try:
        cached = {"cached_at": datetime.now().isoformat(), "data": data}
        with open(cache_path, "w") as f:
            json.dump(cached, f)
    except (IOError, OSError) as e:
        logger.warning(f"Cache write failed for {ticker}: {e}")
    except Exception as e:
        logger.error(f"Unexpected cache write error for {ticker}: {e}")


def _smart_delay():
    """Add random delay between 1-2 seconds to avoid rate limiting"""
    time.sleep(random.uniform(1.0, 2.0))


# Parse stocks.txt file to extract individual tickers and baskets
def parse_stocks_file(filepath):
    """
    Parse stocks.txt file and return:
    - individual_tickers: list of individual ticker symbols
    - baskets: dict mapping basket name to list of constituent tickers
    """
    individual_tickers = []
    baskets = {}

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Check for basket definition: [Basket Name] ticker1, ticker2, ticker3
            basket_match = re.match(r"\[([^\]]+)\]\s*(.+)", line)
            if basket_match:
                basket_name = basket_match.group(1).strip()
                ticker_list = [
                    t.strip().upper() for t in basket_match.group(2).split(",")
                ]
                baskets[basket_name] = ticker_list
            else:
                # Individual ticker
                ticker = line.upper()
                if ticker:
                    individual_tickers.append(ticker)

    return individual_tickers, baskets


# Confluence logic removed - no longer used in reports


# Signal descriptions for portfolio guidance
def get_signal_description(signal):
    """Return detailed guidance for each Larsson signal based on weekly/daily state combination."""
    descriptions = {
        "FULL HOLD + ADD": "Strongest bullish alignment - macro and short-term trends fully confirmed. Hold full position and gradually add on dips for compounding. Prioritize capital preservation: adds only in confirmed strength.",
        "HOLD": "Macro bull intact, short-term pause or inconclusive. Hold full position patiently - no need to act. Avoid new adds or reductions; wait for daily resolution back to strength.",
        "HOLD MOST + REDUCE": "Macro bull with short-term correction. Hold majority position but make gradual reductions into strength if pullback deepens. Lighten to preserve profits - scale out on rallies.",
        "SCALE IN": "Potential emerging bull - short-term strength without macro confirmation yet. Scale in gradually on dips, building position in small increments. Stay disciplined: only add if daily remains strong; keep significant cash reserve.",
        "LIGHT / CASH": "Inconclusive - no clear trend on either timeframe. Remain mostly in cash or very light position. Wait patiently for alignment; tiny probes only on extreme conviction signals.",
        "CASH": "Uncertain or weak conditions. Stay mostly or fully in cash - no new buys. Make reductions to any remaining exposure if weakness persists. Wait for clearer signal before re-engaging.",
        "REDUCE": "Macro bear risk despite short-term bounce. Make gradual reductions into strength/rallies. De-risk toward majority cash - do not add. Bounces are opportunities to exit.",
        "FULL CASH / DEFEND": "Strongest bearish alignment - macro and short-term trends fully down. Full cash position; aggressively protect capital. Exit any remaining longs through disciplined reductions.",
    }
    return descriptions.get(signal, "No guidance available for this signal.")


# Capital Protection - Reduction Calculations
def calculate_reduction_amounts(signal, current_value):
    """Calculate position reduction amounts based on signal severity"""
    reduction_targets = {
        "HOLD MOST + REDUCE": 0.20,  # Keep 80% - weekly bull intact
        "REDUCE": 0.40,  # Keep 60% - weekly bearish, daily bounce
        "LIGHT / CASH": 0.60,  # Keep 40% - both neutral/unclear
        "CASH": 0.80,  # Keep 20% - serious warning
        "FULL CASH / DEFEND": 1.00,  # Full exit - both bearish (phased)
    }
    reduction_pct = reduction_targets.get(signal, 0)
    reduction_amount = current_value * reduction_pct
    keep_amount = current_value - reduction_amount
    return reduction_amount, keep_amount, reduction_pct


def get_reduction_tranches(signal, reduction_pct, reduction_amount):
    """Return phased tranches for position reductions to avoid panic selling"""

    # Single tranche for smaller reductions (20-40%)
    if reduction_pct <= 0.40:
        return [(reduction_amount, 1.0, "At resistance or current price")]

    # Two tranches for medium reductions (60%)
    elif reduction_pct <= 0.60:
        return [
            (reduction_amount * 0.67, 0.40, "Immediate - at R1 or current"),
            (reduction_amount * 0.33, 0.20, "On bounce - at R2+"),
        ]

    # Two tranches for heavy reductions (80%)
    elif reduction_pct <= 0.80:
        return [
            (reduction_amount * 0.625, 0.50, "Immediate - at R1 or current"),
            (reduction_amount * 0.375, 0.30, "On bounce - at R2+"),
        ]

    # Full exit (100%) - three tranches for best price realization
    else:  # FULL CASH / DEFEND
        return [
            (reduction_amount * 0.60, 0.60, "Immediate - at R1 or current"),
            (reduction_amount * 0.30, 0.30, "On bounce - at R2"),
            (reduction_amount * 0.10, 0.10, "Final - at R3 or any rally"),
        ]


# ============================================================================
# PORTFOLIO POSITION MANAGEMENT - Phase 2
# ============================================================================


def calculate_position_gap(current_value, target_pct, portfolio_total):
    """
    Calculate the gap between current position and target allocation.

    Args:
        current_value: Current $ value of position
        target_pct: Target allocation as decimal (e.g., 0.30 for 30%)
        portfolio_total: Total portfolio value

    Returns:
        dict with gap analysis
    """
    target_value = portfolio_total * target_pct
    gap_value = target_value - current_value
    current_pct = (current_value / portfolio_total) if portfolio_total > 0 else 0

    return {
        "current_value": current_value,
        "current_pct": current_pct,
        "target_value": target_value,
        "target_pct": target_pct,
        "gap_value": gap_value,
        "gap_pct": target_pct - current_pct,
        "action": "BUY" if gap_value > 0 else "SELL" if gap_value < 0 else "AT_TARGET",
    }


def calculate_buy_tranches(
    gap_value, s1, s2, s3, current_price, s1_quality, s2_quality, s3_quality
):
    """
    Calculate buy tranches at S3/S2/S1 support levels with individual quality ratings.

    Strategy: Deepest first (S3), patient buying on dips
    - Allocate more to higher quality levels
    - If extended or price > S1: WAIT for dip

    Args:
        gap_value: Dollar amount needed to reach target
        s1, s2, s3: Support levels
        current_price: Current stock price
        s1_quality, s2_quality, s3_quality: Tuples of (rating, note) for each level

    Returns:
        list of (price_level, dollar_amount, level_name, status, quality_rating, quality_note)
    """
    if gap_value <= 0:
        return []

    # Split buy across support levels (40% S3, 35% S2, 25% S1)
    # Prioritize deeper levels (better prices)
    tranches = []

    # Add tranches for levels we can reach (price above them)
    if s3 and s3_quality:
        if current_price > s1 if s1 else False:
            status = "Wait for dip to S3"
        else:
            status = "Pending"
        tranches.append(
            (s3, gap_value * 0.40, "S3", status, s3_quality[0], s3_quality[1])
        )

    if s2 and s2_quality:
        if current_price > s1 if s1 else False:
            status = "Wait for dip to S2"
        else:
            status = "Pending"
        tranches.append(
            (s2, gap_value * 0.35, "S2", status, s2_quality[0], s2_quality[1])
        )

    if s1 and s1_quality:
        if current_price > s1 if s1 else False:
            status = "Wait for dip to S1"
        else:
            status = "Pending"
        tranches.append(
            (s1, gap_value * 0.25, "S1", status, s1_quality[0], s1_quality[1])
        )

    # If price already below all supports, buy at current price
    if not tranches:
        tranches.append(
            (
                current_price,
                gap_value,
                "Current",
                "Execute now - below S3",
                "N/A",
                "Below all support levels",
            )
        )

    return tranches


def calculate_sell_tranches(
    current_value,
    signal,
    r1,
    r2,
    r3,
    adjusted_r1,
    adjusted_r2,
    adjusted_r3,
    r1_quality=None,
    r2_quality=None,
    r3_quality=None,
):
    """
    Calculate sell tranches at R1/R2/R3 resistance levels based on signal.

    Uses adjusted R-levels if MAs block original levels.

    Signal-based reduction targets:
    - HOLD MOST + REDUCE: 20% at R1
    - REDUCE: 20% R1, 15% R2, 5% R3
    - LIGHT/CASH: 30% R1, 20% R2, 10% R3
    - CASH: 40% R1, 30% R2, 10% R3
    - FULL CASH: 50% R1, 30% R2, 20% R3

    Args:
        current_value: Current $ value of position
        signal: Larsson signal
        r1, r2, r3: Original resistance levels
        adjusted_r1, adjusted_r2, adjusted_r3: MA-adjusted levels
        r1_quality, r2_quality, r3_quality: Quality tuples (rating, note)

    Returns:
        list of (price_level, dollar_amount, pct_of_position, level_name, status, quality, quality_note)
    """
    # Default quality values
    if r1_quality is None:
        r1_quality = ("N/A", "")
    if r2_quality is None:
        r2_quality = ("N/A", "")
    if r3_quality is None:
        r3_quality = ("N/A", "")

    quality_map = {"R1": r1_quality, "R2": r2_quality, "R3": r3_quality}

    # Signal to reduction mapping
    signal_reductions = {
        "HOLD MOST + REDUCE": [(adjusted_r1 or r1, 0.20, "R1")],
        "REDUCE": [
            (adjusted_r1 or r1, 0.20, "R1"),
            (adjusted_r2 or r2, 0.15, "R2"),
            (adjusted_r3 or r3, 0.05, "R3"),
        ],
        "LIGHT / CASH": [
            (adjusted_r1 or r1, 0.30, "R1"),
            (adjusted_r2 or r2, 0.20, "R2"),
            (adjusted_r3 or r3, 0.10, "R3"),
        ],
        "CASH": [
            (adjusted_r1 or r1, 0.40, "R1"),
            (adjusted_r2 or r2, 0.30, "R2"),
            (adjusted_r3 or r3, 0.10, "R3"),
        ],
        "FULL CASH / DEFEND": [
            (adjusted_r1 or r1, 0.50, "R1"),
            (adjusted_r2 or r2, 0.30, "R2"),
            (adjusted_r3 or r3, 0.20, "R3"),
        ],
    }

    if signal not in signal_reductions:
        return []  # No reduction needed

    tranches = []
    for price_level, pct, level_name in signal_reductions[signal]:
        if price_level is not None:
            dollar_amount = current_value * pct
            quality, quality_note = quality_map.get(level_name, ("N/A", ""))
            tranches.append(
                (
                    price_level,
                    dollar_amount,
                    pct,
                    level_name,
                    "Pending",
                    quality,
                    quality_note,
                )
            )

    return tranches


def determine_portfolio_action(signal, position_gap, buy_quality):
    """
    Determine what action to take based on signal and position gap.

    Logic:
    - FULL HOLD + ADD + under target = BUY at supports
    - Bearish signal + have position = SELL at resistance
    - HOLD = DO NOTHING
    - FULL HOLD + ADD but at target = HOLD (no buys)

    Returns:
        str: "BUY", "SELL", "HOLD", "WAIT"
    """
    gap_value = position_gap["gap_value"]

    # Cancel buys if signal weakens
    if signal != "FULL HOLD + ADD" and gap_value > 0:
        return "HOLD"  # Don't buy on weak signals

    # Execute buys only on FULL HOLD + ADD
    if signal == "FULL HOLD + ADD" and gap_value > 0:
        if buy_quality in ["EXCELLENT", "GOOD", "OK"]:
            return "BUY"
        elif buy_quality == "EXTENDED":
            return "WAIT"  # Wait for pullback
        else:
            return "HOLD"  # Caution - wait for better setup

    # Execute sells on bearish signals
    if signal in [
        "HOLD MOST + REDUCE",
        "REDUCE",
        "LIGHT / CASH",
        "CASH",
        "FULL CASH / DEFEND",
    ]:
        if gap_value < 0:  # Over target
            return "SELL"  # Reduce anyway (over-allocated)
        elif gap_value == 0:  # At target
            return "SELL"  # Still reduce per signal
        else:  # Under target but bearish
            return "SELL"  # Protect capital even if under target

    # At target or neutral signal
    return "HOLD"


# Recommendation logic removed - no longer used


def analyze_basket(basket_name, constituent_tickers, daily_bars=60, weekly_bars=52):
    """
    Analyze a basket of stocks by calculating market cap-weighted averages.
    Returns a dict with aggregated metrics similar to analyze_ticker format.
    """
    basket_name = f"[{basket_name}]"  # Mark as basket in output
    try:
        # Analyze each constituent and get market caps
        constituent_data = []
        constituent_signals = []  # To list signals in notes
        for ticker in constituent_tickers:
            result = analyze_ticker(ticker, daily_bars, weekly_bars)
            if "error" not in result:
                # Fetch market cap
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    market_cap = info.get("marketCap", 0)
                    if market_cap and market_cap > 0:
                        constituent_data.append(
                            {"result": result, "market_cap": market_cap}
                        )
                        constituent_signals.append(f"{ticker} {result['signal']}")
                except (KeyError, ValueError, TypeError) as e:
                    logger.warning(
                        f"Failed to get market cap for {ticker} in basket: {e}"
                    )
                except Exception as e:
                    logger.error(f"Unexpected error processing {ticker} in basket: {e}")

        if not constituent_data:
            return {
                "ticker": basket_name,
                "error": "no valid constituent data with market caps",
            }

        # Initialize basket result
        basket_result = {"ticker": basket_name}
        basket_result["notes"] = f"Constituents: {', '.join(constituent_signals)}"

        # Basket price as market-cap weighted average
        price_data = [
            (cd["result"]["current_price"], cd["market_cap"] / total_market_cap)
            for cd in constituent_data
            if cd["result"]["current_price"] is not None
        ]
        if price_data:
            price_values = [v for v, w in price_data]
            price_weights = [w for v, w in price_data]
            # Renormalize weights to sum to 1.0 after filtering
            weight_sum = sum(price_weights)
            if weight_sum > 0:
                price_weights = [w / weight_sum for w in price_weights]
                basket_result["current_price"] = np.average(
                    price_values, weights=price_weights
                )
            else:
                basket_result["current_price"] = None
            basket_result["price_note"] = "market cap weighted"
            basket_result["date"] = datetime.now().strftime("%Y-%m-%d")
        else:
            basket_result["current_price"] = None

        # Basket signal as dominant signal (most common or weighted by market cap)
        signals = [cd["result"]["signal"] for cd in constituent_data]
        basket_result["signal"] = max(
            set(signals), key=signals.count
        )  # Most common signal

        # Set pivots to None for baskets (no volume profile fields)
        for field in ["s1", "s2", "s3", "r1", "r2", "r3"]:
            basket_result[field] = None

        result = basket_result

        return result

    except Exception as e:
        return {"ticker": basket_name, "error": str(e)}


# SMMA function (for Larsson)
def smma(series, length):
    smma_result = pd.Series(np.nan, index=series.index)
    sma_val = series.rolling(length).mean()
    smma_result.iloc[length - 1] = sma_val.iloc[length - 1]
    for i in range(length, len(series)):
        smma_result.iloc[i] = (
            smma_result.iloc[i - 1] * (length - 1) + series.iloc[i]
        ) / length
    return smma_result


# Larsson state
def get_larsson_state(df, fast=15, slow=19, v1len=25, v2len=29):
    hl2 = (df["High"] + df["Low"]) / 2
    v1 = smma(hl2, fast).iloc[-1]
    m1 = smma(hl2, slow).iloc[-1]
    m2 = smma(hl2, v1len).iloc[-1]
    v2 = smma(hl2, v2len).iloc[-1]
    if np.isnan([v1, m1, m2, v2]).any():
        return 0
    p2 = ((v1 < m1) != (v1 < v2)) or ((m2 < v2) != (v1 < v2))
    p3 = not p2 and (v1 < v2)
    p1 = not p2 and not p3
    return 1 if p1 else -1 if p3 else 0


# ============================================================================
# MOMENTUM & VOLATILITY INDICATORS (RSI & BOLLINGER BANDS)
# ============================================================================


def calculate_rsi(df, period=14):
    """
    Calculate RSI (Relative Strength Index).

    Returns: float (current RSI value, 0-100)
    """
    if df.empty or len(df) < period + 1:
        return None

    close = df["Close"]
    delta = close.diff()

    # Separate gains and losses
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    # Calculate RS and RSI
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    current_rsi = rsi.iloc[-1]

    return float(current_rsi) if not np.isnan(current_rsi) else None


def calculate_bollinger_bands(df, period=20, num_std=2):
    """
    Calculate Bollinger Bands.

    Returns: tuple (upper_band, middle_band, lower_band, current_position_sigma)
    - current_position_sigma: how many standard deviations from middle band
    """
    if df.empty or len(df) < period:
        return None, None, None, None

    close = df["Close"]

    # Calculate middle band (SMA)
    middle_band = close.rolling(window=period).mean()

    # Calculate standard deviation
    std_dev = close.rolling(window=period).std()

    # Calculate upper and lower bands
    upper_band = middle_band + (num_std * std_dev)
    lower_band = middle_band - (num_std * std_dev)

    # Get current values
    current_price = close.iloc[-1]
    current_middle = middle_band.iloc[-1]
    current_upper = upper_band.iloc[-1]
    current_lower = lower_band.iloc[-1]
    current_std = std_dev.iloc[-1]

    # Calculate position in sigma units
    if not np.isnan(current_std) and current_std > 0:
        bb_position_sigma = (current_price - current_middle) / current_std
    else:
        bb_position_sigma = None

    # Return floats or None
    return (
        float(current_upper) if not np.isnan(current_upper) else None,
        float(current_middle) if not np.isnan(current_middle) else None,
        float(current_lower) if not np.isnan(current_lower) else None,
        (
            float(bb_position_sigma)
            if bb_position_sigma is not None and not np.isnan(bb_position_sigma)
            else None
        ),
    )


def calculate_daily_volatility(df, period=20):
    """
    Calculate average daily range as a volatility measure.

    Returns: dict with volatility metrics
    - avg_daily_range_pct: Average % range (High-Low)/Close over period
    - volatility_class: LOW/MEDIUM/HIGH/EXTREME
    - suggested_stop_pct: Recommended stop loss % (2-3x daily range, min 5%)
    - stop_risk: Risk level for 5% stop (SAFE/ACCEPTABLE/RISKY/VERY_RISKY)
    """
    if df is None or df.empty or len(df) < period:
        return None

    # Calculate daily range as percentage of close
    daily_range_pct = ((df["High"] - df["Low"]) / df["Close"]) * 100

    # Get average over period
    avg_daily_range_pct = daily_range_pct.tail(period).mean()

    # Classify volatility
    if avg_daily_range_pct < 2.0:
        volatility_class = "LOW"
        suggested_stop_pct = 5.0  # Default
        stop_risk = "SAFE"  # 5% is 2.5x+ daily range
    elif avg_daily_range_pct < 3.0:
        volatility_class = "MEDIUM"
        suggested_stop_pct = 5.0  # Acceptable
        stop_risk = "ACCEPTABLE"  # 5% is 1.7-2.5x daily range
    elif avg_daily_range_pct < 5.0:
        volatility_class = "HIGH"
        suggested_stop_pct = max(7.0, avg_daily_range_pct * 2)  # 2x daily range
        stop_risk = "RISKY"  # 5% is only 1-1.7x daily range
    else:
        volatility_class = "EXTREME"
        suggested_stop_pct = max(10.0, avg_daily_range_pct * 2)  # 2x daily range
        stop_risk = "VERY_RISKY"  # 5% likely to trigger on noise

    return {
        "avg_daily_range_pct": float(round(avg_daily_range_pct, 2)),
        "volatility_class": volatility_class,
        "suggested_stop_pct": float(round(suggested_stop_pct, 1)),
        "stop_risk": stop_risk,
    }


# ============================================================================
# VOLUME PROFILE (VRVP - Volume Range Visible Price)
# ============================================================================


def calculate_volume_profile(df, price_bins=50):
    """
    Calculate volume profile for the visible range (dataframe passed).

    Returns dict with:
    - poc: Point of Control (price with highest volume)
    - vah: Value Area High (top of 70% volume range)
    - val: Value Area Low (bottom of 70% volume range)
    - hvn_levels: High Volume Nodes (prices with significant volume clusters)
    - lvn_levels: Low Volume Nodes (prices with low volume - breakout zones)
    """
    if df.empty or "Volume" not in df.columns:
        return None

    # Get price range
    price_min = df["Low"].min()
    price_max = df["High"].max()

    # Create price bins
    bin_edges = np.linspace(price_min, price_max, price_bins + 1)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Accumulate volume at each price level
    volume_at_price = np.zeros(price_bins)

    for _, row in df.iterrows():
        # Find which bins this bar's price range covers
        low_idx = np.searchsorted(bin_edges, row["Low"], side="right") - 1
        high_idx = np.searchsorted(bin_edges, row["High"], side="left")

        # Distribute volume across the price range
        bins_covered = max(1, high_idx - low_idx)
        volume_per_bin = row["Volume"] / bins_covered

        for i in range(max(0, low_idx), min(price_bins, high_idx)):
            volume_at_price[i] += volume_per_bin

    # Point of Control (POC) - price with highest volume
    poc_idx = np.argmax(volume_at_price)
    poc = bin_centers[poc_idx]

    # Value Area (70% of total volume)
    total_volume = volume_at_price.sum()
    target_volume = total_volume * 0.70

    # Expand from POC until we reach 70% volume
    accumulated_volume = volume_at_price[poc_idx]
    val_idx = poc_idx
    vah_idx = poc_idx

    while accumulated_volume < target_volume:
        # Check which direction has more volume
        expand_down = val_idx > 0
        expand_up = vah_idx < price_bins - 1

        if not expand_down and not expand_up:
            break

        vol_below = volume_at_price[val_idx - 1] if expand_down else 0
        vol_above = volume_at_price[vah_idx + 1] if expand_up else 0

        if vol_below >= vol_above and expand_down:
            val_idx -= 1
            accumulated_volume += volume_at_price[val_idx]
        elif expand_up:
            vah_idx += 1
            accumulated_volume += volume_at_price[vah_idx]
        else:
            break

    val = bin_centers[val_idx]
    vah = bin_centers[vah_idx]

    # Identify High Volume Nodes (HVN) - top 20% volume bins
    volume_threshold_hvn = np.percentile(volume_at_price, 80)
    hvn_indices = np.where(volume_at_price >= volume_threshold_hvn)[0]
    hvn_levels = [bin_centers[i] for i in hvn_indices]

    # Identify Low Volume Nodes (LVN) - bottom 20% volume bins
    volume_threshold_lvn = np.percentile(volume_at_price, 20)
    lvn_indices = np.where(volume_at_price <= volume_threshold_lvn)[0]
    lvn_levels = [bin_centers[i] for i in lvn_indices]

    return {
        "poc": float(poc),
        "vah": float(vah),
        "val": float(val),
        "hvn_levels": hvn_levels,
        "lvn_levels": lvn_levels,
        "volume_profile": volume_at_price.tolist(),
        "price_bins": bin_centers.tolist(),
    }


def find_nearest_hvn_lvn(current_price, hvn_levels, lvn_levels):
    """
    Find nearest HVN above/below and LVN above/below current price.

    Returns:
    - hvn_above: Nearest HVN resistance above current price
    - hvn_below: Nearest HVN support below current price
    - lvn_above: Nearest LVN above (potential breakout target)
    - lvn_below: Nearest LVN below (potential breakdown level)
    """
    hvn_above = min([h for h in hvn_levels if h > current_price], default=None)
    hvn_below = max([h for h in hvn_levels if h < current_price], default=None)
    lvn_above = min([l for l in lvn_levels if l > current_price], default=None)
    lvn_below = max([l for l in lvn_levels if l < current_price], default=None)

    return hvn_above, hvn_below, lvn_above, lvn_below


# Swing pivots
def detect_swings(df, strength=12, strength_resistance=None):
    """
    Detect swing highs and lows.
    strength_resistance: Optional separate strength for resistance detection (lower = more recent levels)
    """
    highs = df["High"]
    lows = df["Low"]
    swing_highs = []
    swing_lows = []

    # Use separate strength for resistances if provided
    r_strength = strength_resistance if strength_resistance is not None else strength

    # Detect swing highs (resistances) with potentially lower strength
    for i in range(r_strength, len(df) - r_strength):
        if highs.iloc[i] == highs.iloc[i - r_strength : i + r_strength + 1].max():
            swing_highs.append(highs.iloc[i])

    # Detect swing lows (supports) with original strength
    for i in range(strength, len(df) - strength):
        if lows.iloc[i] == lows.iloc[i - strength : i + strength + 1].min():
            swing_lows.append(lows.iloc[i])

    return swing_highs, swing_lows


def select_top_sr(
    swing_highs,
    swing_lows,
    current_price,
    max_levels=3,
    poc=None,
    hvn_above=None,
    max_resistance_pct=30,
):
    """
    Select top support and resistance levels.

    Args:
        max_resistance_pct: Filter out resistances more than this % above current price (default 30%)
        poc: Point of Control from volume profile (priority resistance if available)
        hvn_above: High Volume Node above current price (priority resistance if available)
    """
    # Supports - unchanged logic
    supports = sorted([p for p in set(swing_lows) if p < current_price])[-max_levels:]

    # Resistances - blend swing highs with volume profile levels
    resistance_candidates = []

    # Add swing highs within reasonable distance
    max_price = current_price * (1 + max_resistance_pct / 100)
    for p in set(swing_highs):
        if current_price < p <= max_price:
            resistance_candidates.append(p)

    # Prioritize POC if it's above current price and within range
    if poc and current_price < poc <= max_price:
        resistance_candidates.append(poc)

    # Prioritize HVN above if available and within range
    if hvn_above and current_price < hvn_above <= max_price:
        resistance_candidates.append(hvn_above)

    # Sort resistances descending - R1 is furthest/strongest (primary target), R3 is closest
    resistances = sorted(set(resistance_candidates), reverse=True)[:max_levels]

    # Pad with NaN if needed
    while len(supports) < max_levels:
        supports.append(np.nan)
    while len(resistances) < max_levels:
        resistances.append(np.nan)

    supports = sorted(supports, reverse=True)  # S1 closest (highest)
    return supports, resistances


def assess_support_volume_backing(
    support_level, poc, vah, val, hvn_below, level_name="S1"
):
    """
    Assess volume backing for support level using VRVP data.
    Returns: ('STRONG', 'MODERATE', 'WEAK', note)
    """
    if support_level is None:
        return "WEAK", f"No {level_name} available"

    # Strong: Support aligns with POC or HVN (±3% tolerance)
    if poc is not None and abs(support_level - poc) / poc <= 0.03:
        return (
            "STRONG",
            f"{level_name} ${support_level:,.2f} aligns with POC ${poc:,.2f}",
        )

    if hvn_below is not None and abs(support_level - hvn_below) / hvn_below <= 0.03:
        return (
            "STRONG",
            f"{level_name} ${support_level:,.2f} aligns with HVN ${hvn_below:,.2f}",
        )

    # Moderate: Support within Value Area
    if val is not None and vah is not None:
        if val <= support_level <= vah:
            return (
                "MODERATE",
                f"{level_name} ${support_level:,.2f} in Value Area (${val:,.2f}-${vah:,.2f})",
            )

    # Support near but below Value Area (within 3% below VAL)
    if val is not None and val * 0.97 <= support_level < val:
        return (
            "MODERATE",
            f"{level_name} ${support_level:,.2f} near but below Value Area Low ${val:,.2f}",
        )

    # Weak: Support far from volume clusters (more than 3% below VAL)
    if val is not None and support_level < val * 0.97:
        return (
            "WEAK",
            f"{level_name} ${support_level:,.2f} well below Value Area Low ${val:,.2f}",
        )

    # Support near but above Value Area (within 3% above VAH)
    if vah is not None and vah < support_level <= vah * 1.03:
        return (
            "MODERATE",
            f"{level_name} ${support_level:,.2f} near but above Value Area High ${vah:,.2f}",
        )

    # Support far above Value Area (more than 3% above VAH)
    if vah is not None and support_level > vah * 1.03:
        return (
            "MODERATE",
            f"{level_name} ${support_level:,.2f} well above Value Area High ${vah:,.2f} - lower volume backing",
        )

    # Default: outside value area but not near any volume cluster
    return "MODERATE", f"{level_name} ${support_level:,.2f} has moderate volume backing"


def assess_stop_aware_entry_quality(
    current_price,
    stop_tolerance_pct,
    s1,
    s2,
    s3,
    s1_quality,
    s2_quality,
    s3_quality,
    d50,
    d100,
    d200,
    poc=None,
    vah=None,
    val=None,
):
    """
    Assess entry quality based on supports within stop tolerance range.

    Args:
        current_price: Current entry price
        stop_tolerance_pct: Maximum acceptable stop loss % (e.g., 8 for 8%)
        s1, s2, s3: Support levels
        s1_quality, s2_quality, s3_quality: Quality ratings for each support
        d50, d100, d200: Moving averages
        poc, vah, val: Volume profile levels

    Returns:
        (entry_quality, entry_flag, entry_note, accessible_supports)
    """
    stop_level = current_price * (1 - stop_tolerance_pct / 100)

    # Find all supports within stop range
    accessible_supports = []

    # Check moving averages
    if d50 and d50 >= stop_level:
        accessible_supports.append(("D50", d50, "WEAK"))
    if d100 and d100 >= stop_level:
        accessible_supports.append(("D100", d100, "MODERATE"))
    if d200 and d200 >= stop_level:
        accessible_supports.append(("D200", d200, "MODERATE"))

    # Check S-levels
    if s1 and s1 >= stop_level:
        accessible_supports.append(("S1", s1, s1_quality))
    if s2 and s2 >= stop_level:
        accessible_supports.append(("S2", s2, s2_quality))
    if s3 and s3 >= stop_level:
        accessible_supports.append(("S3", s3, s3_quality))

    # Check volume profile levels
    if poc and poc >= stop_level:
        accessible_supports.append(("POC", poc, "STRONG"))

    # Count quality of accessible supports
    excellent_count = sum(1 for _, _, q in accessible_supports if q == "EXCELLENT")
    good_count = sum(1 for _, _, q in accessible_supports if q == "GOOD")
    moderate_count = sum(
        1 for _, _, q in accessible_supports if q in ["MODERATE", "OK"]
    )

    total_count = len(accessible_supports)

    # Determine entry quality based on accessible supports
    if total_count == 0:
        entry_quality = "CAUTION"
        entry_flag = "\u26a0 EXTENDED"
        entry_note = (
            f"No supports within {stop_tolerance_pct}% stop range (${stop_level:.2f})"
        )

    elif excellent_count >= 2 or (excellent_count >= 1 and good_count >= 1):
        entry_quality = "EXCELLENT"
        entry_flag = "\u2713 SAFE ENTRY"
        entry_note = (
            f"{total_count} supports in range, including {excellent_count} EXCELLENT"
        )

    elif good_count >= 2 or (good_count >= 1 and moderate_count >= 2):
        entry_quality = "GOOD"
        entry_flag = "\u2713 SAFE ENTRY"
        entry_note = f"{total_count} supports in range, including {good_count} GOOD"

    elif good_count >= 1 or moderate_count >= 2:
        entry_quality = "OK"
        entry_flag = "\u2713 ACCEPTABLE"
        entry_note = f"{total_count} supports in range ({good_count} GOOD, {moderate_count} MODERATE)"

    elif moderate_count >= 1:
        entry_quality = "CAUTION"
        entry_flag = "\u26a0 THIN"
        entry_note = f"Only {total_count} support(s) in range - limited protection"

    else:
        entry_quality = "CAUTION"
        entry_flag = "\u26a0 EXTENDED"
        entry_note = f"Weak supports only in {stop_tolerance_pct}% range"

    # Check if best supports are out of range but close
    out_of_range_good = []
    if s1 and s1 < stop_level and s1_quality in ["EXCELLENT", "GOOD"]:
        out_of_range_good.append(("S1", s1, s1_quality))
    if s2 and s2 < stop_level and s2_quality in ["EXCELLENT", "GOOD"]:
        out_of_range_good.append(("S2", s2, s2_quality))
    if s3 and s3 < stop_level and s3_quality in ["EXCELLENT", "GOOD"]:
        out_of_range_good.append(("S3", s3, s3_quality))

    # If good supports exist but are out of range, suggest waiting
    if out_of_range_good and total_count <= 1:
        entry_flag = "\u26a0 WAIT"
        best_support = out_of_range_good[0]
        distance_pct = ((current_price - best_support[1]) / current_price) * 100
        entry_note += f" | {best_support[2]} support at ${best_support[1]:.2f} ({distance_pct:.1f}% down) - wait for pullback"

    # Special case: At ideal support levels
    if (
        s1
        and abs(current_price - s1) / current_price <= 0.02
        and s1_quality in ["EXCELLENT", "GOOD"]
    ):
        entry_flag = "\u2713 IDEAL"
        entry_note = f"At {s1_quality} support S1 (${s1:.2f})"

    return entry_quality, entry_flag, entry_note, accessible_supports


def assess_stop_aware_short_entry_quality(
    current_price,
    stop_tolerance_pct,
    r1,
    r2,
    r3,
    r1_quality,
    r2_quality,
    r3_quality,
    d50=None,
    d100=None,
    d200=None,
    poc=None,
    vah=None,
    val=None,
):
    """
    Assess SHORT entry quality based on accessible resistances within stop tolerance.
    For short positions, the stop is ABOVE the entry price.

    Args:
        current_price: Entry price for short
        stop_tolerance_pct: Maximum acceptable stop distance (e.g., 8%)
        r1, r2, r3: Resistance levels
        r1_quality, r2_quality, r3_quality: Quality ratings for resistances
        d50, d100, d200, poc, vah, val: Additional resistance levels

    Returns:
        (exit_quality, exit_flag, exit_note, accessible_resistances)
    """
    # Calculate stop level ABOVE entry (for shorts, you lose if price goes up)
    stop_level = current_price * (1 + stop_tolerance_pct / 100)

    # Collect all potential resistance levels ABOVE stop
    accessible_resistances = []

    # Check R1, R2, R3
    if r1 and r1 > stop_level and r1_quality in ["EXCELLENT", "GOOD"]:
        accessible_resistances.append(("R1", r1, r1_quality))
    if r2 and r2 > stop_level and r2_quality in ["EXCELLENT", "GOOD"]:
        accessible_resistances.append(("R2", r2, r2_quality))
    if r3 and r3 > stop_level and r3_quality in ["EXCELLENT", "GOOD"]:
        accessible_resistances.append(("R3", r3, r3_quality))

    # Check moving averages above stop
    if d50 and d50 > stop_level:
        accessible_resistances.append(("D50", d50, "GOOD"))
    if d100 and d100 > stop_level:
        accessible_resistances.append(("D100", d100, "GOOD"))
    if d200 and d200 > stop_level:
        accessible_resistances.append(("D200", d200, "GOOD"))

    # Check VRVP levels above stop
    if poc and poc > stop_level:
        accessible_resistances.append(("POC", poc, "EXCELLENT"))
    if vah and vah > stop_level:
        accessible_resistances.append(("VAH", vah, "GOOD"))

    # Count excellent resistances
    excellent_count = sum(
        1 for _, _, quality in accessible_resistances if quality == "EXCELLENT"
    )
    good_count = sum(1 for _, _, quality in accessible_resistances if quality == "GOOD")

    # Determine overall quality
    short_entry_quality = "CAUTION"
    short_entry_flag = "⏳ WAIT"
    short_entry_note = ""

    if excellent_count >= 2:
        short_entry_quality = "EXCELLENT"
        short_entry_flag = "\u2713 SAFE ENTRY"  # ✓ using Unicode escape
        short_entry_note = f"{len(accessible_resistances)} accessible resistances within stop tolerance ({stop_tolerance_pct}%)"
    elif excellent_count >= 1 or good_count >= 2:
        short_entry_quality = "GOOD"
        short_entry_flag = "\u2713 IDEAL"  # ✓ using Unicode escape
        short_entry_note = f"{len(accessible_resistances)} good resistances protect your short position"
    elif good_count >= 1 or len(accessible_resistances) >= 1:
        short_entry_quality = "OK"
        short_entry_flag = "\u2713 ACCEPTABLE"  # ✓ using Unicode escape
        short_entry_note = (
            f"Limited resistance structure ({len(accessible_resistances)} level)"
        )
    else:
        # Check if there ARE resistances but they're below the stop
        resistances_below_stop = []
        if r1 and r1 < stop_level:
            resistances_below_stop.append("R1")
        if r2 and r2 < stop_level:
            resistances_below_stop.append("R2")

        if resistances_below_stop:
            short_entry_quality = "CAUTION"
            short_entry_flag = "\u26a0 THIN"  # ⚠ using Unicode escape
            short_entry_note = f"Good resistances ({', '.join(resistances_below_stop)}) exist but are BELOW your stop level - cannot protect short"
        else:
            # Far from any resistances
            short_entry_quality = "CAUTION"
            short_entry_flag = "\u26a0 EXTENDED"  # ⚠ using Unicode escape
            short_entry_note = (
                "Price too far from resistances - high risk for short entry"
            )

    # Special case: very close to excellent resistance (within 2%)
    if (
        r1
        and abs(current_price - r1) / current_price <= 0.02
        and r1_quality in ["EXCELLENT", "GOOD"]
    ):
        short_entry_flag = "\u2713 IDEAL"  # ✓ using Unicode escape
        short_entry_note = (
            f"At {r1_quality} resistance R1 (${r1:.2f}) - ideal short entry"
        )

    return (
        short_entry_quality,
        short_entry_flag,
        short_entry_note,
        accessible_resistances,
    )


def assess_buy_quality(
    d50,
    d100,
    d200,
    s1,
    current_price,
    poc=None,
    vah=None,
    val=None,
    hvn_below=None,
    level_name="S1",
    rsi=None,
    bb_lower=None,
    bb_middle=None,
    support_level_price=None,
):
    """
    Assess buy quality based on MA positioning + VRVP volume backing + RSI + Bollinger Bands.
    Returns: (quality_rating, quality_note)

    EXCELLENT: All MAs below support + strong volume + RSI/BB favorable
    GOOD: D100 & D200 below support + strong/moderate volume + RSI/BB favorable
    OK: Partial MA support or good MA with only moderate volume backing
    CAUTION: No MA support or support in weak volume zone
    EXTENDED: Price >10% above all MAs or VAH
    """
    if s1 is None:
        return "N/A", f"No {level_name} support level available"

    # Step 1: Check for EXTENDED conditions
    mas_valid = [ma for ma in [d50, d100, d200] if ma is not None]

    # Extended above MAs
    if mas_valid and all(current_price > ma * 1.10 for ma in mas_valid):
        return "EXTENDED", "Price over 10% above all MAs - wait for pullback"

    # Extended above Value Area High
    if vah is not None and current_price > vah * 1.10:
        return (
            "EXTENDED",
            f"Price ${current_price:,.2f} over 10% above VAH ${vah:,.2f} - wait for pullback",
        )

    # Step 2: Assess S1 volume backing
    volume_quality, volume_note = assess_support_volume_backing(
        s1, poc, vah, val, hvn_below, level_name
    )

    # Step 3: Identify which MAs are below support level
    mas_below_s1 = []
    ma_names = ["D50", "D100", "D200"]
    ma_values = [d50, d100, d200]

    for ma_name, ma_value in zip(ma_names, ma_values):
        if ma_value is not None and ma_value <= s1:
            mas_below_s1.append(ma_name)

    mas_checked = sum(1 for ma in ma_values if ma is not None)

    if mas_checked == 0:
        return "N/A", "Insufficient MA data"

    # Format MA list for messages
    ma_list_str = ", ".join(mas_below_s1) if mas_below_s1 else "No MAs"

    # Step 4: Assess RSI and Bollinger Bands positioning
    rsi_boost = 0
    bb_boost = 0
    enhancements = []

    # Use support_level_price if provided, otherwise use current_price for evaluation
    eval_price = support_level_price if support_level_price is not None else s1

    if rsi is not None:
        if rsi < 30:
            rsi_boost = 2  # Strong oversold boost
            enhancements.append(f"RSI {rsi:.0f} oversold")
        elif rsi < 40:
            rsi_boost = 1  # Moderate oversold boost
            enhancements.append(f"RSI {rsi:.0f} near oversold")
        elif rsi > 70:
            rsi_boost = -1  # Overbought penalty
            enhancements.append(f"RSI {rsi:.0f} overbought")

    if bb_lower is not None and bb_middle is not None:
        # Check if support level is at or below lower BB
        if s1 <= bb_lower * 1.02:  # Within 2% of lower band
            bb_boost = 2  # Strong statistical support
            pct_below_mid = ((s1 - bb_middle) / bb_middle) * 100
            enhancements.append(
                f"{level_name} at/below lower BB ({pct_below_mid:.1f}%)"
            )
        elif s1 <= bb_lower * 1.05:  # Within 5% of lower band
            bb_boost = 1  # Near statistical support
            enhancements.append(f"{level_name} near lower BB")

    # Step 5: Combine MA position + Volume backing + RSI/BB enhancements
    base_quality = None
    base_note = ""

    # All MAs below support level?
    if len(mas_below_s1) == 3:
        # Is support near POC/HVN?
        if volume_quality == "STRONG":
            base_quality = "EXCELLENT"
            base_note = f"{ma_list_str} support {level_name} + {volume_note}"
        # Is support in Value Area?
        elif volume_quality == "MODERATE":
            base_quality = "GOOD"
            base_note = f"{ma_list_str} support {level_name} + {volume_note}"
        else:
            base_quality = "OK"
            base_note = f"{ma_list_str} support {level_name} but {volume_note}"

    # D100 & D200 below support level?
    elif "D100" in mas_below_s1 and "D200" in mas_below_s1:
        # Support volume quality?
        if volume_quality in ["STRONG", "MODERATE"]:
            base_quality = "GOOD"
            base_note = f"D100, D200 support {level_name} + {volume_note}"
        else:  # Weak
            base_quality = "OK"
            base_note = f"D100, D200 support {level_name} but {volume_note}"

    # Some MA support?
    elif len(mas_below_s1) >= 1:
        # Support volume quality?
        if volume_quality == "WEAK":
            base_quality = "CAUTION"
            base_note = f"{ma_list_str} support {level_name} but {volume_note}"
        else:
            base_quality = "OK"
            base_note = f"{ma_list_str} support {level_name}, {volume_note}"

    # No MA support + weak support
    else:
        base_quality = "CAUTION"
        base_note = f"No MA support + {volume_note}"

    # Apply RSI/BB boost to upgrade quality
    total_boost = rsi_boost + bb_boost

    quality_levels = ["CAUTION", "OK", "GOOD", "EXCELLENT"]
    current_level_idx = (
        quality_levels.index(base_quality) if base_quality in quality_levels else 0
    )

    # Apply boost
    if total_boost >= 3:
        # Strong boost: upgrade by 2 levels
        new_level_idx = min(current_level_idx + 2, len(quality_levels) - 1)
    elif total_boost >= 2:
        # Moderate boost: upgrade by 1 level
        new_level_idx = min(current_level_idx + 1, len(quality_levels) - 1)
    elif total_boost == 1:
        # Small boost: upgrade if OK -> GOOD
        new_level_idx = (
            min(current_level_idx + 1, len(quality_levels) - 1)
            if base_quality == "OK"
            else current_level_idx
        )
    elif total_boost <= -1:
        # Penalty: downgrade by 1 level
        new_level_idx = max(current_level_idx - 1, 0)
    else:
        new_level_idx = current_level_idx

    final_quality = quality_levels[new_level_idx]

    # Build final note
    if enhancements:
        enhancement_str = " + " + ", ".join(enhancements)
        final_note = base_note + enhancement_str
    else:
        final_note = base_note

    return final_quality, final_note


def assess_resistance_volume_backing(
    resistance_level, poc, vah, val, hvn_above, level_name="R1"
):
    """
    Assess volume backing for resistance level using VRVP data.
    Returns: ('STRONG', 'MODERATE', 'WEAK', note)

    High volume at resistance = strong ceiling (good for selling)
    """
    if resistance_level is None:
        return "WEAK", f"No {level_name} available"

    # Strong: Resistance aligns with POC or HVN (±3% tolerance) - strong ceiling
    if poc is not None and abs(resistance_level - poc) / poc <= 0.03:
        return (
            "STRONG",
            f"{level_name} ${resistance_level:,.2f} aligns with POC ${poc:,.2f} - strong ceiling",
        )

    if hvn_above is not None and abs(resistance_level - hvn_above) / hvn_above <= 0.03:
        return (
            "STRONG",
            f"{level_name} ${resistance_level:,.2f} aligns with HVN ${hvn_above:,.2f} - strong ceiling",
        )

    # Moderate: Resistance within Value Area
    if val is not None and vah is not None:
        if val <= resistance_level <= vah:
            return (
                "MODERATE",
                f"{level_name} ${resistance_level:,.2f} in Value Area (${val:,.2f}-${vah:,.2f})",
            )

    # Resistance near but above Value Area (within 3% above VAH)
    if vah is not None and vah < resistance_level <= vah * 1.03:
        return (
            "MODERATE",
            f"{level_name} ${resistance_level:,.2f} near but above Value Area High ${vah:,.2f}",
        )

    # Resistance far above Value Area (more than 3% above VAH) - untested zone
    if vah is not None and resistance_level > vah * 1.03:
        return (
            "WEAK",
            f"{level_name} ${resistance_level:,.2f} well above Value Area High ${vah:,.2f} - untested zone",
        )

    # Resistance near but below Value Area (within 3% below VAH)
    if vah is not None and vah * 0.97 <= resistance_level < vah:
        return (
            "MODERATE",
            f"{level_name} ${resistance_level:,.2f} near but below Value Area High ${vah:,.2f}",
        )

    # Weak: Resistance well below VAH (in low volume zone)
    if vah is not None and resistance_level < vah * 0.97:
        return (
            "WEAK",
            f"{level_name} ${resistance_level:,.2f} well below Value Area High ${vah:,.2f}",
        )

    # Default
    return (
        "MODERATE",
        f"{level_name} ${resistance_level:,.2f} has moderate volume resistance",
    )


def assess_sell_quality(
    d50,
    d100,
    d200,
    r1,
    current_price,
    poc=None,
    vah=None,
    val=None,
    hvn_above=None,
    level_name="R1",
    rsi=None,
    bb_upper=None,
    bb_middle=None,
    resistance_level_price=None,
):
    """
    Assess sell quality based on MA positioning + VRVP volume resistance + RSI + Bollinger Bands.
    Returns: (quality_rating, quality_note)

    EXCELLENT: All MAs above resistance + strong volume + RSI/BB favorable
    GOOD: D100 & D200 above resistance + strong/moderate volume + RSI/BB favorable
    OK: Partial MA resistance or good MA with only moderate volume
    CAUTION: No MA resistance or resistance in weak volume zone
    MISSED: Price already above resistance level
    """
    if r1 is None:
        return "N/A", f"No {level_name} resistance level available"

    # Step 1: Check if already above resistance
    if current_price >= r1:
        return (
            "MISSED",
            f"Price ${current_price:.2f} already above {level_name} ${r1:.2f}",
        )

    # Step 2: Assess resistance volume backing
    volume_quality, volume_note = assess_resistance_volume_backing(
        r1, poc, vah, val, hvn_above, level_name
    )

    # Step 3: Identify which MAs are ABOVE resistance (blocking upside)
    mas_above_r = []
    ma_names = ["D50", "D100", "D200"]
    ma_values = [d50, d100, d200]

    for ma_name, ma_value in zip(ma_names, ma_values):
        if ma_value is not None and ma_value >= r1:
            mas_above_r.append(ma_name)

    mas_checked = sum(1 for ma in ma_values if ma is not None)

    if mas_checked == 0:
        return "N/A", "Insufficient MA data"

    # Format MA list for messages
    ma_list_str = ", ".join(mas_above_r) if mas_above_r else "No MAs"

    # Step 4: Assess RSI and Bollinger Bands positioning
    rsi_boost = 0
    bb_boost = 0
    enhancements = []

    # Use resistance_level_price if provided, otherwise use current_price for evaluation
    eval_price = resistance_level_price if resistance_level_price is not None else r1

    if rsi is not None:
        if rsi > 70:
            rsi_boost = 2  # Strong overbought boost (good for selling)
            enhancements.append(f"RSI {rsi:.0f} overbought")
        elif rsi > 60:
            rsi_boost = 1  # Moderate overbought boost
            enhancements.append(f"RSI {rsi:.0f} elevated")
        elif rsi < 30:
            rsi_boost = -1  # Oversold penalty (may rally further)
            enhancements.append(f"RSI {rsi:.0f} oversold")

    if bb_upper is not None and bb_middle is not None:
        # Check if resistance level is at or above upper BB
        if r1 >= bb_upper * 0.98:  # Within 2% of upper band
            bb_boost = 2  # Strong statistical resistance
            pct_above_mid = ((r1 - bb_middle) / bb_middle) * 100
            enhancements.append(
                f"{level_name} at/above upper BB (+{pct_above_mid:.1f}%)"
            )
        elif r1 >= bb_upper * 0.95:  # Within 5% of upper band
            bb_boost = 1  # Near statistical resistance
            enhancements.append(f"{level_name} near upper BB")

    # Step 5: Combine MA resistance + Volume backing + RSI/BB enhancements
    base_quality = None
    base_note = ""

    # All MAs above resistance (strong ceiling)
    if len(mas_above_r) == 3:
        if volume_quality == "STRONG":
            base_quality = "EXCELLENT"
            base_note = f"{ma_list_str} block {level_name} + {volume_note}"
        elif volume_quality == "MODERATE":
            base_quality = "GOOD"
            base_note = f"{ma_list_str} block {level_name} + {volume_note}"
        else:
            base_quality = "OK"
            base_note = f"{ma_list_str} block {level_name} but {volume_note}"

    # D100 & D200 above resistance
    elif "D100" in mas_above_r and "D200" in mas_above_r:
        if volume_quality in ["STRONG", "MODERATE"]:
            base_quality = "GOOD"
            base_note = f"D100, D200 block {level_name} + {volume_note}"
        else:
            base_quality = "OK"
            base_note = f"D100, D200 block {level_name} but {volume_note}"

    # Some MA resistance
    elif len(mas_above_r) >= 1:
        if volume_quality == "WEAK":
            base_quality = "CAUTION"
            base_note = f"{ma_list_str} block {level_name} but {volume_note}"
        else:
            base_quality = "OK"
            base_note = f"{ma_list_str} block {level_name}, {volume_note}"

    # No MA resistance - might break through easily
    else:
        base_quality = "CAUTION"
        base_note = f"No MA resistance above {level_name} + {volume_note}"

    # Apply RSI/BB boost to upgrade quality
    total_boost = rsi_boost + bb_boost

    quality_levels = ["CAUTION", "OK", "GOOD", "EXCELLENT"]
    current_level_idx = (
        quality_levels.index(base_quality) if base_quality in quality_levels else 0
    )

    # Apply boost
    if total_boost >= 3:
        # Strong boost: upgrade by 2 levels
        new_level_idx = min(current_level_idx + 2, len(quality_levels) - 1)
    elif total_boost >= 2:
        # Moderate boost: upgrade by 1 level
        new_level_idx = min(current_level_idx + 1, len(quality_levels) - 1)
    elif total_boost == 1:
        # Small boost: upgrade if OK -> GOOD
        new_level_idx = (
            min(current_level_idx + 1, len(quality_levels) - 1)
            if base_quality == "OK"
            else current_level_idx
        )
    elif total_boost <= -1:
        # Penalty: downgrade by 1 level
        new_level_idx = max(current_level_idx - 1, 0)
    else:
        new_level_idx = current_level_idx

    final_quality = quality_levels[new_level_idx]

    # Build final note
    if enhancements:
        enhancement_str = " + " + ", ".join(enhancements)
        final_note = base_note + enhancement_str
    else:
        final_note = base_note

    return final_quality, final_note


def adjust_sell_levels_for_mas(d50, d100, d200, r1, r2, r3, current_price):
    """
    Check if MAs block path to resistance levels.
    Returns: (adjusted_r1, adjusted_r2, adjusted_r3, feasibility_note)

    If MA is between current price and resistance, suggest selling at MA instead.
    """
    adjusted_r1, adjusted_r2, adjusted_r3 = r1, r2, r3
    notes = []

    # Check each resistance level
    for r_level, r_name in [(r1, "R1"), (r2, "R2"), (r3, "R3")]:
        if r_level is None:
            continue

        # Find MAs between current price and resistance
        blocking_mas = []
        for ma, ma_name in [(d50, "D50"), (d100, "D100"), (d200, "D200")]:
            if ma is not None and current_price < ma < r_level:
                blocking_mas.append((ma, ma_name))

        if blocking_mas:
            # Suggest lowest blocking MA as alternate sell level
            lowest_ma, ma_name = min(blocking_mas, key=lambda x: x[0])
            notes.append(f"{r_name} blocked by {ma_name} ${lowest_ma:,.2f}")

            # Adjust level to MA
            if r_name == "R1":
                adjusted_r1 = lowest_ma
            elif r_name == "R2":
                adjusted_r2 = lowest_ma
            elif r_name == "R3":
                adjusted_r3 = lowest_ma

    feasibility_note = "; ".join(notes) if notes else "Clear path to all R-levels"
    return adjusted_r1, adjusted_r2, adjusted_r3, feasibility_note


def analyze_ticker(ticker, daily_bars=60, weekly_bars=52, as_of_date=None):
    """Fetch data and compute indicators for a single ticker. Returns a dict with results.

    Args:
        ticker: Stock ticker symbol
        daily_bars: Number of daily bars to analyze (default 60)
        weekly_bars: Number of weekly bars to analyze (default 52)
        as_of_date: Optional datetime or date string (YYYY-MM-DD) to limit data to historical point
                    If provided, only data up to this date will be used (for backtesting)
    """
    ticker = ticker.upper()

    # Skip cache for historical backtesting (as_of_date provided)
    # Cache only applies to live/current data
    if as_of_date is None:
        cached_result = _load_from_cache(ticker, daily_bars, weekly_bars)
        if cached_result is not None:
            return cached_result

    # Add delay before making API request to avoid rate limiting
    _smart_delay()

    try:
        stock = yf.Ticker(ticker)

        # Handle as_of_date for historical simulation
        if as_of_date:
            if isinstance(as_of_date, str):
                end_date = datetime.strptime(as_of_date, "%Y-%m-%d")
            else:
                end_date = as_of_date
            today = end_date.strftime("%Y-%m-%d")
        else:
            end_date = datetime.now()
            today = end_date.strftime("%Y-%m-%d")

        # Daily data - fetch up to end_date
        daily = stock.history(period="3y", end=end_date)
        if daily.empty:
            return {"ticker": ticker, "error": "no daily data"}

        # For historical backtesting, use the close price at as_of_date
        # For live data, use current market price from info
        if as_of_date:
            current_price = float(daily["Close"].iloc[-1])
            price_note = f"close as of {today}"
        else:
            info = stock.info
            # Check for rate limit indicators
            if not info or len(info) == 0:
                return {"ticker": ticker, "error": "rate_limit_possible"}

            current_price = (
                info.get("regularMarketPrice")
                or info.get("preMarketPrice")
                or info.get("previousClose")
            )
            price_note = "pre-market" if "preMarketPrice" in info else "last close"

        # Weekly data - fetch up to end_date
        weekly = stock.history(period="10y", interval="1wk", end=end_date)
        if weekly.empty:
            return {"ticker": ticker, "error": "no weekly data"}

        # Calculate daily SMAs (D50, D100, D200)
        d50 = daily["Close"].rolling(50).mean().iloc[-1] if len(daily) >= 50 else None
        d100 = (
            daily["Close"].rolling(100).mean().iloc[-1] if len(daily) >= 100 else None
        )
        d200 = (
            daily["Close"].rolling(200).mean().iloc[-1] if len(daily) >= 200 else None
        )

        # Calculate RSI and Bollinger Bands
        rsi = calculate_rsi(daily, period=14)
        bb_upper, bb_middle, bb_lower, bb_position_sigma = calculate_bollinger_bands(
            daily, period=20, num_std=2
        )

        # Calculate daily volatility metrics
        volatility = calculate_daily_volatility(daily, period=20)

        # Volume Profile (VRVP)
        vp_60d = calculate_volume_profile(daily, price_bins=60)
        vp_52w = calculate_volume_profile(weekly, price_bins=52)

        poc_60d = vp_60d["poc"] if vp_60d else None
        vah_60d = vp_60d["vah"] if vp_60d else None
        val_60d = vp_60d["val"] if vp_60d else None

        poc_52w = vp_52w["poc"] if vp_52w else None
        vah_52w = vp_52w["vah"] if vp_52w else None
        val_52w = vp_52w["val"] if vp_52w else None

        # Find nearest HVN/LVN levels for trading
        hvn_above_60d, hvn_below_60d, lvn_above_60d, lvn_below_60d = (
            None,
            None,
            None,
            None,
        )
        if vp_60d:
            hvn_above_60d, hvn_below_60d, lvn_above_60d, lvn_below_60d = (
                find_nearest_hvn_lvn(
                    current_price, vp_60d["hvn_levels"], vp_60d["lvn_levels"]
                )
            )

        # Pivots - use lower strength for resistance detection (6 vs 12 for more recent levels)
        daily_highs, daily_lows = detect_swings(
            daily, strength=12, strength_resistance=6
        )
        daily_supports, daily_resistances = select_top_sr(
            daily_highs,
            daily_lows,
            current_price,
            poc=poc_60d,
            hvn_above=hvn_above_60d,
            max_resistance_pct=30,
        )
        weekly_highs, weekly_lows = detect_swings(
            weekly, strength=12, strength_resistance=6
        )
        weekly_supports, weekly_resistances = select_top_sr(
            weekly_highs,
            weekly_lows,
            current_price,
            poc=poc_52w,
            hvn_above=None,
            max_resistance_pct=30,
        )

        # Signal
        daily_state = get_larsson_state(daily)
        weekly_state = get_larsson_state(weekly)
        mapping = {
            (1, 1): "FULL HOLD + ADD",
            (1, 0): "HOLD",
            (1, -1): "HOLD MOST + REDUCE",
            (0, 1): "SCALE IN",
            (0, 0): "LIGHT / CASH",
            (0, -1): "CASH",
            (-1, 1): "REDUCE",
            (-1, 0): "CASH",
            (-1, -1): "FULL CASH / DEFEND",
        }
        signal = mapping.get((weekly_state, daily_state), "UNKNOWN")

        # Extract support/resistance levels
        s1 = float(daily_supports[0]) if not pd.isna(daily_supports[0]) else None
        s2 = float(daily_supports[1]) if not pd.isna(daily_supports[1]) else None
        s3 = float(daily_supports[2]) if not pd.isna(daily_supports[2]) else None
        r1 = float(daily_resistances[0]) if not pd.isna(daily_resistances[0]) else None
        r2 = float(daily_resistances[1]) if not pd.isna(daily_resistances[1]) else None
        r3 = float(daily_resistances[2]) if not pd.isna(daily_resistances[2]) else None

        # Assess buy quality for each support level (MA confluence + VRVP volume backing + RSI + BB)
        s1_quality = assess_buy_quality(
            d50,
            d100,
            d200,
            s1,
            current_price,
            poc=poc_60d,
            vah=vah_60d,
            val=val_60d,
            hvn_below=hvn_below_60d,
            level_name="S1",
            rsi=rsi,
            bb_lower=bb_lower,
            bb_middle=bb_middle,
            support_level_price=s1,
        )
        s2_quality = assess_buy_quality(
            d50,
            d100,
            d200,
            s2,
            current_price,
            poc=poc_60d,
            vah=vah_60d,
            val=val_60d,
            hvn_below=hvn_below_60d,
            level_name="S2",
            rsi=rsi,
            bb_lower=bb_lower,
            bb_middle=bb_middle,
            support_level_price=s2,
        )
        s3_quality = assess_buy_quality(
            d50,
            d100,
            d200,
            s3,
            current_price,
            poc=poc_60d,
            vah=vah_60d,
            val=val_60d,
            hvn_below=hvn_below_60d,
            level_name="S3",
            rsi=rsi,
            bb_lower=bb_lower,
            bb_middle=bb_middle,
            support_level_price=s3,
        )

        # Assess sell quality for each resistance level (MA resistance + VRVP volume ceiling + RSI + BB)
        r1_quality = assess_sell_quality(
            d50,
            d100,
            d200,
            r1,
            current_price,
            poc=poc_60d,
            vah=vah_60d,
            val=val_60d,
            hvn_above=hvn_above_60d,
            level_name="R1",
            rsi=rsi,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            resistance_level_price=r1,
        )
        r2_quality = assess_sell_quality(
            d50,
            d100,
            d200,
            r2,
            current_price,
            poc=poc_60d,
            vah=vah_60d,
            val=val_60d,
            hvn_above=hvn_above_60d,
            level_name="R2",
            rsi=rsi,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            resistance_level_price=r2,
        )
        r3_quality = assess_sell_quality(
            d50,
            d100,
            d200,
            r3,
            current_price,
            poc=poc_60d,
            vah=vah_60d,
            val=val_60d,
            hvn_above=hvn_above_60d,
            level_name="R3",
            rsi=rsi,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            resistance_level_price=r3,
        )

        # Adjust sell levels for MA resistance
        adjusted_r1, adjusted_r2, adjusted_r3, sell_feasibility_note = (
            adjust_sell_levels_for_mas(d50, d100, d200, r1, r2, r3, current_price)
        )

        # Calculate stop-aware entry quality (Option 1 + 4: Entry-Relative Quality + Support Within Stop Range)
        # Use user's maximum stop tolerance (8%) as the standard
        # This represents the maximum acceptable risk for conservative traders
        stop_tolerance_pct = 8.0

        (
            entry_quality,
            entry_flag,
            entry_note,
            accessible_supports,
        ) = assess_stop_aware_entry_quality(
            current_price=current_price,
            stop_tolerance_pct=stop_tolerance_pct,
            s1=s1,
            s2=s2,
            s3=s3,
            s1_quality=s1_quality[0],
            s2_quality=s2_quality[0],
            s3_quality=s3_quality[0],
            d50=d50,
            d100=d100,
            d200=d200,
            poc=poc_60d,
            vah=vah_60d,
            val=val_60d,
        )

        # Calculate stop-aware short entry quality for SELL/SHORT positions
        try:
            (
                short_entry_quality,
                short_entry_flag,
                short_entry_note,
                accessible_resistances,
            ) = assess_stop_aware_short_entry_quality(
                current_price=current_price,
                stop_tolerance_pct=stop_tolerance_pct,
                r1=r1,
                r2=r2,
                r3=r3,
                r1_quality=r1_quality[0],
                r2_quality=r2_quality[0],
                r3_quality=r3_quality[0],
                d50=d50,
                d100=d100,
                d200=d200,
                poc=poc_60d,
                vah=vah_60d,
                val=val_60d,
            )
        except Exception as e:
            print(
                f"[ERROR] assess_stop_aware_short_entry_quality failed for {ticker}: {e}"
            )
            short_entry_quality = "N/A"
            short_entry_flag = ""
            short_entry_note = f"Error: {str(e)}"
            accessible_resistances = []

        # Calculate Volatility Risk:Reward ratio
        vol_rr = 0.0
        if signal == "FULL HOLD + ADD" and r1 and current_price > 0:
            # For buys: reward to R1 vs volatility stop risk
            reward_pct = ((r1 - current_price) / current_price) * 100
            risk_pct = (
                volatility["suggested_stop_pct"]
                if volatility and volatility.get("suggested_stop_pct")
                else 8.0
            )
            if risk_pct > 0:
                vol_rr = reward_pct / risk_pct
        elif (
            signal in ["REDUCE", "CASH", "HOLD MOST + REDUCE", "FULL CASH / DEFEND"]
            and s1
            and current_price > 0
        ):
            # For shorts: reward to S1 vs 8% stop above
            reward_pct = ((current_price - s1) / current_price) * 100
            risk_pct = 8.0  # Standard short stop
            if risk_pct > 0 and s1 < current_price:
                vol_rr = reward_pct / risk_pct

        result = {
            "ticker": ticker,
            "signal": signal,
            "current_price": current_price,
            "price_note": price_note,
            "date": today,
            # Support/Resistance levels
            "s1": s1,
            "s2": s2,
            "s3": s3,
            "r1": r1,
            "r2": r2,
            "r3": r3,
            # Moving averages
            "d50": float(d50) if d50 is not None and not pd.isna(d50) else None,
            "d100": float(d100) if d100 is not None and not pd.isna(d100) else None,
            "d200": float(d200) if d200 is not None and not pd.isna(d200) else None,
            # RSI and Bollinger Bands
            "rsi": rsi,
            "bb_upper": bb_upper,
            "bb_middle": bb_middle,
            "bb_lower": bb_lower,
            "bb_position_sigma": bb_position_sigma,
            # Volatility metrics
            "avg_daily_range_pct": (
                volatility["avg_daily_range_pct"] if volatility else None
            ),
            "volatility_class": volatility["volatility_class"] if volatility else None,
            "suggested_stop_pct": (
                volatility["suggested_stop_pct"] if volatility else None
            ),
            "stop_risk": volatility["stop_risk"] if volatility else None,
            "vol_rr": vol_rr,  # Volatility Risk:Reward ratio
            # Volume Profile - 60 day
            "poc_60d": float(poc_60d) if poc_60d is not None else None,
            "vah_60d": float(vah_60d) if vah_60d is not None else None,
            "val_60d": float(val_60d) if val_60d is not None else None,
            "hvn_above_60d": float(hvn_above_60d) if hvn_above_60d else None,
            "hvn_below_60d": float(hvn_below_60d) if hvn_below_60d else None,
            "lvn_above_60d": float(lvn_above_60d) if lvn_above_60d else None,
            "lvn_below_60d": float(lvn_below_60d) if lvn_below_60d else None,
            # Volume Profile - 52 week
            "poc_52w": float(poc_52w) if poc_52w is not None else None,
            "vah_52w": float(vah_52w) if vah_52w is not None else None,
            "val_52w": float(val_52w) if val_52w is not None else None,
            # Buy quality assessment (per support level)
            "buy_quality": s1_quality[0],  # Overall based on S1 (nearest level)
            "buy_quality_note": s1_quality[1],
            "s1_quality": s1_quality[0],
            "s1_quality_note": s1_quality[1],
            "s2_quality": s2_quality[0],
            "s2_quality_note": s2_quality[1],
            "s3_quality": s3_quality[0],
            "s3_quality_note": s3_quality[1],
            # Sell quality assessment (per resistance level)
            "r1_quality": r1_quality[0],
            "r1_quality_note": r1_quality[1],
            "r2_quality": r2_quality[0],
            "r2_quality_note": r2_quality[1],
            "r3_quality": r3_quality[0],
            "r3_quality_note": r3_quality[1],
            # Adjusted sell levels (MA-aware)
            "adjusted_r1": float(adjusted_r1) if adjusted_r1 is not None else r1,
            "adjusted_r2": float(adjusted_r2) if adjusted_r2 is not None else r2,
            "adjusted_r3": float(adjusted_r3) if adjusted_r3 is not None else r3,
            "sell_feasibility_note": sell_feasibility_note,
            # Stop-aware entry quality (NEW - Options 1 + 4 + Flag System)
            "entry_quality": entry_quality,
            "entry_flag": entry_flag,
            "entry_note": entry_note,
            "stop_tolerance_pct": stop_tolerance_pct,
            "stop_level": current_price * (1 - stop_tolerance_pct / 100),
            "accessible_supports_count": len(accessible_supports),
            # Stop-aware short entry quality for SELL/SHORT positions
            "short_entry_quality": short_entry_quality,
            "short_entry_flag": short_entry_flag,
            "short_entry_note": short_entry_note,
            "short_stop_level": current_price * (1 + stop_tolerance_pct / 100),
            "accessible_resistances_count": len(accessible_resistances),
            "notes": "",
        }

        # Save to cache only for live data (not historical backtesting)
        if as_of_date is None:
            _save_to_cache(ticker, daily_bars, weekly_bars, result)

        return result
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


if __name__ == "__main__":
    import argparse
    from concurrent.futures import ThreadPoolExecutor, as_completed

    parser = argparse.ArgumentParser(
        description="Analyze tickers and save results to CSV"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--tickers", nargs="+", help="Space-separated list of tickers to analyze"
    )
    group.add_argument("--file", help="Path to file with one ticker per line")
    parser.add_argument(
        "--output", "-o", default="results.csv", help="Output CSV file path"
    )
    parser.add_argument(
        "--concurrency", "-c", type=int, default=4, help="Number of concurrent workers"
    )
    parser.add_argument(
        "--save-per-symbol",
        action="store_true",
        help="Save individual CSVs per ticker in ./results",
    )
    args = parser.parse_args()

    # Build ticker list
    tickers = []
    if args.tickers:
        tickers = [t.upper() for t in args.tickers]
    else:
        with open(args.file, "r", encoding="utf-8") as f:
            tickers = [line.strip().upper() for line in f if line.strip()]

    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {ex.submit(analyze_ticker, t, 60, 52): t for t in tickers}
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            t = res.get("ticker")
            if "error" in res:
                print(f"{t}: ERROR: {res['error']}")
            else:
                print(f"{t}: {res['signal']} @ {res['current_price']}")
                if args.save_per_symbol:
                    import os

                    os.makedirs("results", exist_ok=True)
                    import csv

                    path = os.path.join("results", f"{t}.csv")
                    with open(path, "w", newline="", encoding="utf-8") as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=list(res.keys()))
                        writer.writeheader()
                        writer.writerow(res)

    # Save combined CSV
    import csv

    keys = set().union(*(r.keys() for r in results))
    keys = sorted(keys)
    with open(args.output, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=keys)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"Wrote {len(results)} rows to {args.output}")
