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
        "FULL HOLD + ADD": "Strongest bullish alignment â€“ macro and short-term trends fully confirmed. Hold full position and gradually add on dips for compounding. Prioritize capital preservation: adds only in confirmed strength.",

        "HOLD": "Macro bull intact, short-term pause or inconclusive. Hold full position patiently â€“ no need to act. Avoid new adds or reductions; wait for daily resolution back to strength.",

        "HOLD MOST â†’ REDUCE": "Macro bull with short-term correction. Hold majority position but make gradual reductions into strength if pullback deepens. Lighten to preserve profits â€“ scale out on rallies.",

        "SCALE IN": "Potential emerging bull â€“ short-term strength without macro confirmation yet. Scale in gradually on dips, building position in small increments. Stay disciplined: only add if daily remains strong; keep significant cash reserve.",

        "LIGHT / CASH": "Inconclusive â€“ no clear trend on either timeframe. Remain mostly in cash or very light position. Wait patiently for alignment; tiny probes only on extreme conviction signals.",

        "CASH": "Uncertain or weak conditions. Stay mostly or fully in cash â€“ no new buys. Make reductions to any remaining exposure if weakness persists. Wait for clearer signal before re-engaging.",

        "REDUCE": "Macro bear risk despite short-term bounce. Make gradual reductions into strength/rallies. De-risk toward majority cash â€“ do not add. Bounces are opportunities to exit.",

        "FULL CASH / DEFEND": "Strongest bearish alignment â€“ macro and short-term trends fully down. Full cash position; aggressively protect capital. Exit any remaining longs through disciplined reductions."
    }
    return descriptions.get(signal, "No guidance available for this signal.")

# Capital Protection - Reduction Calculations
def calculate_reduction_amounts(signal, current_value):
    """Calculate position reduction amounts based on signal severity"""
    reduction_targets = {
        "HOLD MOST â†’ REDUCE": 0.20,  # Keep 80% - weekly bull intact
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

        # Pivots
        daily_highs, daily_lows = detect_swings(daily)
        daily_supports, daily_resistances = select_top_sr(daily_highs, daily_lows, current_price)
        weekly_highs, weekly_lows = detect_swings(weekly)
        weekly_supports, weekly_resistances = select_top_sr(weekly_highs, weekly_lows, current_price)

        # Signal
        daily_state = get_larsson_state(daily)
        weekly_state = get_larsson_state(weekly)
        mapping = {
            (1,1): "FULL HOLD + ADD", (1,0): "HOLD", (1,-1): "HOLD MOST â†’ REDUCE",
            (0,1): "SCALE IN", (0,0): "LIGHT / CASH", (0,-1): "CASH",
            (-1,1): "REDUCE", (-1,0): "CASH", (-1,-1): "FULL CASH / DEFEND"
        }
        signal = mapping.get((weekly_state, daily_state), "UNKNOWN")

        result = {
            'ticker': ticker,
            'signal': signal,
            'current_price': current_price,
            'price_note': price_note,
            'date': today,
            's1': float(daily_supports[0]) if not pd.isna(daily_supports[0]) else None,
            's2': float(daily_supports[1]) if not pd.isna(daily_supports[1]) else None,
            's3': float(daily_supports[2]) if not pd.isna(daily_supports[2]) else None,
            'r1': float(daily_resistances[0]) if not pd.isna(daily_resistances[0]) else None,
            'r2': float(daily_resistances[1]) if not pd.isna(daily_resistances[1]) else None,
            'r3': float(daily_resistances[2]) if not pd.isna(daily_resistances[2]) else None,
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
