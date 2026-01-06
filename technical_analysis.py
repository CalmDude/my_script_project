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

# ============================================================================
# CACHING SYSTEM - Prevents rate limiting by caching results for 24 hours
# ============================================================================

CACHE_DIR = Path('scanner_cache')
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
        with open(cache_path, 'r') as f:
            cached = json.load(f)

        # Check if cache is expired
        cached_time = datetime.fromisoformat(cached['cached_at'])
        age_hours = (datetime.now() - cached_time).total_seconds() / 3600

        if age_hours > CACHE_TTL_HOURS:
            cache_path.unlink()  # Delete expired cache
            return None

        return cached['data']
    except:
        return None

def _save_to_cache(ticker, daily_bars, weekly_bars, data):
    """Save analysis result to cache"""
    cache_path = _get_cache_path(ticker, daily_bars, weekly_bars)

    try:
        cached = {
            'cached_at': datetime.now().isoformat(),
            'data': data
        }
        with open(cache_path, 'w') as f:
            json.dump(cached, f)
    except:
        pass  # Silently fail if caching doesn't work

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

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            # Check for basket definition: [Basket Name] ticker1, ticker2, ticker3
            basket_match = re.match(r'\[([^\]]+)\]\s*(.+)', line)
            if basket_match:
                basket_name = basket_match.group(1).strip()
                ticker_list = [t.strip().upper() for t in basket_match.group(2).split(',')]
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

        "FULL CASH / DEFEND": "Strongest bearish alignment - macro and short-term trends fully down. Full cash position; aggressively protect capital. Exit any remaining longs through disciplined reductions."
    }
    return descriptions.get(signal, "No guidance available for this signal.")

# Capital Protection - Reduction Calculations
def calculate_reduction_amounts(signal, current_value):
    """Calculate position reduction amounts based on signal severity"""
    reduction_targets = {
        "HOLD MOST + REDUCE": 0.20,  # Keep 80% - weekly bull intact
        "REDUCE": 0.40,              # Keep 60% - weekly bearish, daily bounce
        "LIGHT / CASH": 0.60,        # Keep 40% - both neutral/unclear
        "CASH": 0.80,                # Keep 20% - serious warning
        "FULL CASH / DEFEND": 1.00   # Full exit - both bearish (phased)
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
            (reduction_amount * 0.33, 0.20, "On bounce - at R2+")
        ]

    # Two tranches for heavy reductions (80%)
    elif reduction_pct <= 0.80:
        return [
            (reduction_amount * 0.625, 0.50, "Immediate - at R1 or current"),
            (reduction_amount * 0.375, 0.30, "On bounce - at R2+")
        ]

    # Full exit (100%) - three tranches for best price realization
    else:  # FULL CASH / DEFEND
        return [
            (reduction_amount * 0.60, 0.60, "Immediate - at R1 or current"),
            (reduction_amount * 0.30, 0.30, "On bounce - at R2"),
            (reduction_amount * 0.10, 0.10, "Final - at R3 or any rally")
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
        'current_value': current_value,
        'current_pct': current_pct,
        'target_value': target_value,
        'target_pct': target_pct,
        'gap_value': gap_value,
        'gap_pct': target_pct - current_pct,
        'action': 'BUY' if gap_value > 0 else 'SELL' if gap_value < 0 else 'AT_TARGET'
    }

def calculate_buy_tranches(gap_value, s1, s2, s3, current_price, buy_quality):
    """
    Calculate buy tranches at S3/S2/S1 support levels.

    Strategy: Deepest first (S3), patient buying on dips
    - If extended or price > S1: WAIT for dip
    - Split gap across 3 levels

    Args:
        gap_value: Dollar amount needed to reach target
        s1, s2, s3: Support levels
        current_price: Current stock price
        buy_quality: Quality rating (EXCELLENT/GOOD/CAUTION/EXTENDED)

    Returns:
        list of (price_level, dollar_amount, level_name, status)
    """
    if gap_value <= 0:
        return []

    # Split buy across support levels (40% S3, 35% S2, 25% S1)
    # Prioritize deeper levels (better prices)
    tranches = []

    # Add tranches for levels we can reach (price above them)
    if s3:
        if current_price > s1 if s1 else False:
            status = "Wait for dip to S3"
        else:
            status = "Pending"
        tranches.append((s3, gap_value * 0.40, "S3", status))

    if s2:
        if current_price > s1 if s1 else False:
            status = "Wait for dip to S2"
        else:
            status = "Pending"
        tranches.append((s2, gap_value * 0.35, "S2", status))

    if s1:
        if current_price > s1 if s1 else False:
            status = "Wait for dip to S1"
        else:
            status = "Pending"
        tranches.append((s1, gap_value * 0.25, "S1", status))

    # If price already below all supports, buy at current price
    if not tranches:
        tranches.append((current_price, gap_value, "Current", "Execute now - below S3"))

    return tranches

def calculate_sell_tranches(current_value, signal, r1, r2, r3, adjusted_r1, adjusted_r2, adjusted_r3):
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

    Returns:
        list of (price_level, dollar_amount, pct_of_position, level_name, status)
    """
    # Signal to reduction mapping
    signal_reductions = {
        "HOLD MOST + REDUCE": [(adjusted_r1 or r1, 0.20, "R1")],
        "REDUCE": [
            (adjusted_r1 or r1, 0.20, "R1"),
            (adjusted_r2 or r2, 0.15, "R2"),
            (adjusted_r3 or r3, 0.05, "R3")
        ],
        "LIGHT / CASH": [
            (adjusted_r1 or r1, 0.30, "R1"),
            (adjusted_r2 or r2, 0.20, "R2"),
            (adjusted_r3 or r3, 0.10, "R3")
        ],
        "CASH": [
            (adjusted_r1 or r1, 0.40, "R1"),
            (adjusted_r2 or r2, 0.30, "R2"),
            (adjusted_r3 or r3, 0.10, "R3")
        ],
        "FULL CASH / DEFEND": [
            (adjusted_r1 or r1, 0.50, "R1"),
            (adjusted_r2 or r2, 0.30, "R2"),
            (adjusted_r3 or r3, 0.20, "R3")
        ]
    }

    if signal not in signal_reductions:
        return []  # No reduction needed

    tranches = []
    for price_level, pct, level_name in signal_reductions[signal]:
        if price_level is not None:
            dollar_amount = current_value * pct
            tranches.append((price_level, dollar_amount, pct, level_name, "Pending"))

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
    gap_value = position_gap['gap_value']

    # Cancel buys if signal weakens
    if signal != "FULL HOLD + ADD" and gap_value > 0:
        return "HOLD"  # Don't buy on weak signals

    # Execute buys only on FULL HOLD + ADD
    if signal == "FULL HOLD + ADD" and gap_value > 0:
        if buy_quality in ["EXCELLENT", "GOOD"]:
            return "BUY"
        elif buy_quality == "EXTENDED":
            return "WAIT"  # Wait for pullback
        else:
            return "HOLD"  # Caution - wait for better setup

    # Execute sells on bearish signals
    if signal in ["HOLD MOST + REDUCE", "REDUCE", "LIGHT / CASH", "CASH", "FULL CASH / DEFEND"]:
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
            if 'error' not in result:
                # Fetch market cap
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    market_cap = info.get('marketCap', 0)
                    if market_cap and market_cap > 0:
                        constituent_data.append({
                            'result': result,
                            'market_cap': market_cap
                        })
                        constituent_signals.append(f"{ticker} {result['signal']}")
                except:
                    # If can't get market cap, skip this constituent
                    pass

        if not constituent_data:
            return {"ticker": basket_name, "error": "no valid constituent data with market caps"}

        # Initialize basket result
        basket_result = {'ticker': basket_name}
        basket_result['notes'] = f"Constituents: {', '.join(constituent_signals)}"

        # Basket price as market-cap weighted average
        price_data = [(cd['result']['current_price'], cd['market_cap'] / total_market_cap)
                     for cd in constituent_data if cd['result']['current_price'] is not None]
        if price_data:
            price_values = [v for v, w in price_data]
            price_weights = [w for v, w in price_data]
            # Renormalize weights to sum to 1.0 after filtering
            weight_sum = sum(price_weights)
            if weight_sum > 0:
                price_weights = [w / weight_sum for w in price_weights]
                basket_result['current_price'] = np.average(price_values, weights=price_weights)
            else:
                basket_result['current_price'] = None
            basket_result['price_note'] = "market cap weighted"
            basket_result['date'] = datetime.now().strftime("%Y-%m-%d")
        else:
            basket_result['current_price'] = None

        # Basket signal as dominant signal (most common or weighted by market cap)
        signals = [cd['result']['signal'] for cd in constituent_data]
        basket_result['signal'] = max(set(signals), key=signals.count)  # Most common signal

        # Set pivots to None for baskets (no volume profile fields)
        for field in ['s1', 's2', 's3', 'r1', 'r2', 'r3']:
            basket_result[field] = None

        result = basket_result

        return result

    except Exception as e:
        return {'ticker': basket_name, 'error': str(e)}


# SMMA function (for Larsson)
def smma(series, length):
    smma_result = pd.Series(np.nan, index=series.index)
    sma_val = series.rolling(length).mean()
    smma_result.iloc[length-1] = sma_val.iloc[length-1]
    for i in range(length, len(series)):
        smma_result.iloc[i] = (smma_result.iloc[i-1] * (length - 1) + series.iloc[i]) / length
    return smma_result

# Larsson state
def get_larsson_state(df, fast=15, slow=19, v1len=25, v2len=29):
    hl2 = (df['High'] + df['Low']) / 2
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

# Volume Profile calculation removed - no longer needed

# Swing pivots
def detect_swings(df, strength=12):
    highs = df['High']
    lows = df['Low']
    swing_highs = []
    swing_lows = []
    for i in range(strength, len(df) - strength):
        if highs.iloc[i] == highs.iloc[i-strength:i+strength+1].max():
            swing_highs.append(highs.iloc[i])
        if lows.iloc[i] == lows.iloc[i-strength:i+strength+1].min():
            swing_lows.append(lows.iloc[i])
    return swing_highs, swing_lows

def select_top_sr(swing_highs, swing_lows, current_price, max_levels=3):
    resistances = sorted([p for p in set(swing_highs) if p > current_price], reverse=True)[:max_levels]
    supports = sorted([p for p in set(swing_lows) if p < current_price])[-max_levels:]
    while len(supports) < max_levels:
        supports.append(np.nan)
    while len(resistances) < max_levels:
        resistances.append(np.nan)
    supports = sorted(supports, reverse=True)  # S1 closest (highest)
    return supports, resistances

def assess_buy_quality(d50, d100, d200, s1, current_price):
    """
    Assess buy quality based on MA positioning relative to S1 support.
    Returns: (quality_rating, quality_note)

    EXCELLENT: All MAs below S1 (clear path to support)
    GOOD: D100 and D200 below S1 (strong support)
    CAUTION: D100 or D200 above S1 (resistance blocking support)
    EXTENDED: Price > 10% above all MAs (too high to buy)
    """
    if s1 is None:
        return "N/A", "No S1 support level available"

    # Check for extended condition (price way above all MAs)
    mas_valid = [ma for ma in [d50, d100, d200] if ma is not None]
    if mas_valid and all(current_price > ma * 1.10 for ma in mas_valid):
        return "EXTENDED", "Price >10% above all MAs - wait for pullback"

    # Count MAs below S1
    mas_below_s1 = 0
    mas_checked = 0

    for ma in [d50, d100, d200]:
        if ma is not None:
            mas_checked += 1
            if ma <= s1:
                mas_below_s1 += 1

    if mas_checked == 0:
        return "N/A", "Insufficient MA data"

    # Rate quality
    if mas_below_s1 == 3:
        return "EXCELLENT", "D50, D100, D200 all support S1"
    elif d100 is not None and d200 is not None and d100 <= s1 and d200 <= s1:
        return "GOOD", "D100 & D200 support S1"
    elif mas_below_s1 >= 1:
        return "GOOD", f"{mas_below_s1} of {mas_checked} MAs support S1"
    else:
        return "CAUTION", "MAs above S1 - resistance blocking support"

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
            notes.append(f"{r_name} blocked by {ma_name} ${lowest_ma:.2f}")

            # Adjust level to MA
            if r_name == "R1":
                adjusted_r1 = lowest_ma
            elif r_name == "R2":
                adjusted_r2 = lowest_ma
            elif r_name == "R3":
                adjusted_r3 = lowest_ma

    feasibility_note = "; ".join(notes) if notes else "Clear path to all R-levels"
    return adjusted_r1, adjusted_r2, adjusted_r3, feasibility_note

def analyze_ticker(ticker, daily_bars=60, weekly_bars=52):
    """Fetch data and compute indicators for a single ticker. Returns a dict with results."""
    ticker = ticker.upper()

    # Check cache first
    cached_result = _load_from_cache(ticker, daily_bars, weekly_bars)
    if cached_result is not None:
        return cached_result

    # Add delay before making API request to avoid rate limiting
    _smart_delay()

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Check for rate limit indicators
        if not info or len(info) == 0:
            return {"ticker": ticker, "error": "rate_limit_possible"}

        current_price = info.get('regularMarketPrice') or info.get('preMarketPrice') or info.get('previousClose')
        price_note = "pre-market" if 'preMarketPrice' in info else "last close"
        today = datetime.now().strftime("%Y-%m-%d")

        # Daily data
        daily = stock.history(period="3y")
        if daily.empty:
            return {"ticker": ticker, "error": "no daily data"}

        # Weekly data
        weekly = stock.history(period="10y", interval="1wk")
        if weekly.empty:
            return {"ticker": ticker, "error": "no weekly data"}

        # Calculate daily SMAs (D50, D100, D200)
        d50 = daily['Close'].rolling(50).mean().iloc[-1] if len(daily) >= 50 else None
        d100 = daily['Close'].rolling(100).mean().iloc[-1] if len(daily) >= 100 else None
        d200 = daily['Close'].rolling(200).mean().iloc[-1] if len(daily) >= 200 else None

        # Pivots
        daily_highs, daily_lows = detect_swings(daily)
        daily_supports, daily_resistances = select_top_sr(daily_highs, daily_lows, current_price)
        weekly_highs, weekly_lows = detect_swings(weekly)
        weekly_supports, weekly_resistances = select_top_sr(weekly_highs, weekly_lows, current_price)

        # Signal
        daily_state = get_larsson_state(daily)
        weekly_state = get_larsson_state(weekly)
        mapping = {
            (1,1): "FULL HOLD + ADD", (1,0): "HOLD", (1,-1): "HOLD MOST + REDUCE",
            (0,1): "SCALE IN", (0,0): "LIGHT / CASH", (0,-1): "CASH",
            (-1,1): "REDUCE", (-1,0): "CASH", (-1,-1): "FULL CASH / DEFEND"
        }
        signal = mapping.get((weekly_state, daily_state), "UNKNOWN")

        # Extract support/resistance levels
        s1 = float(daily_supports[0]) if not pd.isna(daily_supports[0]) else None
        s2 = float(daily_supports[1]) if not pd.isna(daily_supports[1]) else None
        s3 = float(daily_supports[2]) if not pd.isna(daily_supports[2]) else None
        r1 = float(daily_resistances[0]) if not pd.isna(daily_resistances[0]) else None
        r2 = float(daily_resistances[1]) if not pd.isna(daily_resistances[1]) else None
        r3 = float(daily_resistances[2]) if not pd.isna(daily_resistances[2]) else None

        # Assess buy quality (MA confluence with S1)
        buy_quality, buy_quality_note = assess_buy_quality(d50, d100, d200, s1, current_price)

        # Adjust sell levels for MA resistance
        adjusted_r1, adjusted_r2, adjusted_r3, sell_feasibility_note = adjust_sell_levels_for_mas(
            d50, d100, d200, r1, r2, r3, current_price
        )

        result = {
            'ticker': ticker,
            'signal': signal,
            'current_price': current_price,
            'price_note': price_note,
            'date': today,
            # Support/Resistance levels
            's1': s1,
            's2': s2,
            's3': s3,
            'r1': r1,
            'r2': r2,
            'r3': r3,
            # Moving averages
            'd50': float(d50) if d50 is not None and not pd.isna(d50) else None,
            'd100': float(d100) if d100 is not None and not pd.isna(d100) else None,
            'd200': float(d200) if d200 is not None and not pd.isna(d200) else None,
            # Buy quality assessment
            'buy_quality': buy_quality,
            'buy_quality_note': buy_quality_note,
            # Adjusted sell levels (MA-aware)
            'adjusted_r1': float(adjusted_r1) if adjusted_r1 is not None else r1,
            'adjusted_r2': float(adjusted_r2) if adjusted_r2 is not None else r2,
            'adjusted_r3': float(adjusted_r3) if adjusted_r3 is not None else r3,
            'sell_feasibility_note': sell_feasibility_note,
            'notes': ''
        }

        # Save to cache
        _save_to_cache(ticker, daily_bars, weekly_bars, result)

        return result
    except Exception as e:
        return {'ticker': ticker, 'error': str(e)}


if __name__ == '__main__':
    import argparse
    from concurrent.futures import ThreadPoolExecutor, as_completed
    parser = argparse.ArgumentParser(description='Analyze tickers and save results to CSV')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--tickers', nargs='+', help='Space-separated list of tickers to analyze')
    group.add_argument('--file', help='Path to file with one ticker per line')
    parser.add_argument('--output', '-o', default='results.csv', help='Output CSV file path')
    parser.add_argument('--concurrency', '-c', type=int, default=4, help='Number of concurrent workers')
    parser.add_argument('--save-per-symbol', action='store_true', help='Save individual CSVs per ticker in ./results')
    args = parser.parse_args()

    # Build ticker list
    tickers = []
    if args.tickers:
        tickers = [t.upper() for t in args.tickers]
    else:
        with open(args.file, 'r', encoding='utf-8') as f:
            tickers = [line.strip().upper() for line in f if line.strip()]

    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {ex.submit(analyze_ticker, t, 60, 52): t for t in tickers}
        for fut in as_completed(futures):
            res = fut.result()
            results.append(res)
            t = res.get('ticker')
            if 'error' in res:
                print(f"{t}: ERROR: {res['error']}")
            else:
                print(f"{t}: {res['signal']} @ {res['current_price']}")
                if args.save_per_symbol:
                    import os
                    os.makedirs('results', exist_ok=True)
                    import csv
                    path = os.path.join('results', f"{t}.csv")
                    with open(path, 'w', newline='', encoding='utf-8') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=list(res.keys()))
                        writer.writeheader()
                        writer.writerow(res)

    # Save combined CSV
    import csv
    keys = set().union(*(r.keys() for r in results))
    keys = sorted(keys)
    with open(args.output, 'w', newline='', encoding='utf-8') as out:
        writer = csv.DictWriter(out, fieldnames=keys)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    print(f"Wrote {len(results)} rows to {args.output}")
