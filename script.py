import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import re

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


# Confluence Decision Tree (exact classification - mandatory)
def confluence_decision_tree(row):
    """Exact confluence classification using the mandatory Decision Tree from Larsson Master Summary."""
    price = row['current_price']
    if price is None or pd.isna(price):
        return "UNKNOWN"

    # Required fields — return UNKNOWN if any missing
    required_fields = ['daily_val', 'daily_vah', 'daily_poc', 'd50', 'w10']
    if any(row.get(field) is None or pd.isna(row.get(field)) for field in required_fields):
        return "UNKNOWN"

    daily_val = row['daily_val']
    daily_vah = row['daily_vah']
    daily_poc = row['daily_poc']
    d50 = row['d50']
    w10 = row['w10']

    inside_va = daily_val <= price <= daily_vah
    at_above_poc = price >= daily_poc
    above_d50 = price > d50
    above_w10 = price > w10

    if inside_va and at_above_poc and above_d50 and above_w10:
        return "EXTENDED"
    elif inside_va and not at_above_poc and (not above_d50 or not above_w10):
        return "BALANCED"
    else:
        return "WEAK"  # or Bearish/Pause

# Signal descriptions for portfolio guidance
def get_signal_description(signal):
    """Return detailed guidance for each Larsson signal based on weekly/daily state combination."""
    descriptions = {
        "FULL HOLD + ADD": "Strongest bullish alignment – macro and short-term trends fully confirmed. Hold full position and gradually add on dips for compounding. Prioritize capital preservation: adds only in confirmed strength.",

        "HOLD": "Macro bull intact, short-term pause or inconclusive. Hold full position patiently – no need to act. Avoid new adds or reductions; wait for daily resolution back to strength.",

        "HOLD MOST → REDUCE": "Macro bull with short-term correction. Hold majority position but make gradual reductions into strength if pullback deepens. Lighten to preserve profits – scale out on rallies.",

        "SCALE IN": "Potential emerging bull – short-term strength without macro confirmation yet. Scale in gradually on dips, building position in small increments. Stay disciplined: only add if daily remains strong; keep significant cash reserve.",

        "LIGHT / CASH": "Inconclusive – no clear trend on either timeframe. Remain mostly in cash or very light position. Wait patiently for alignment; tiny probes only on extreme conviction signals.",

        "CASH": "Uncertain or weak conditions. Stay mostly or fully in cash – no new buys. Make reductions to any remaining exposure if weakness persists. Wait for clearer signal before re-engaging.",

        "REDUCE": "Macro bear risk despite short-term bounce. Make gradual reductions into strength/rallies. De-risk toward majority cash – do not add. Bounces are opportunities to exit.",

        "FULL CASH / DEFEND": "Strongest bearish alignment – macro and short-term trends fully down. Full cash position; aggressively protect capital. Exit any remaining longs through disciplined reductions."
    }
    return descriptions.get(signal, "No guidance available for this signal.")

# Conservative recommendation (global - no starters in Extended zones)
def conservative_recommendation(row):
    signal = row['signal']
    confluence = row.get('confluence', 'UNKNOWN')

    if "FULL HOLD + ADD" not in signal:
        return "No Buy"

    if confluence == "EXTENDED":
        return "Wait for Support"
    elif confluence == "BALANCED":
        return "Enter on Dip"
    else:
        return "Skip – Poor Setup"

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

        # Calculate weighted averages for numeric fields
        numeric_fields = ['d20', 'd50', 'd100', 'd200', 'w10', 'w20', 'w200']
        basket_result = {'ticker': basket_name}
        basket_result['notes'] = f"Constituents: {', '.join(constituent_signals)}"
        market_caps = [cd['market_cap'] for cd in constituent_data]
        total_market_cap = sum(market_caps)
        weights = [mc / total_market_cap for mc in market_caps]
        for field in numeric_fields:
            # Filter both values and weights together to maintain correspondence
            paired_data = [(cd['result'][field], cd['market_cap'] / total_market_cap)
                          for cd in constituent_data if cd['result'][field] is not None]
            if paired_data:
                field_values = [v for v, w in paired_data]
                field_weights = [w for v, w in paired_data]
                # Renormalize weights to sum to 1.0 after filtering
                weight_sum = sum(field_weights)
                if weight_sum > 0:
                    field_weights = [w / weight_sum for w in field_weights]
                    basket_result[field] = np.average(field_values, weights=field_weights)
                else:
                    basket_result[field] = None
            else:
                basket_result[field] = None

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

        # Set VPVR and pivots to None for baskets
        for field in ['daily_poc', 'daily_vah', 'daily_val', 'weekly_poc', 'weekly_vah', 'weekly_val', 's1', 's2', 's3', 'r1', 'r2', 'r3']:
            basket_result[field] = None

        result = basket_result

        # Add confluence and recommendation
        result['confluence'] = confluence_decision_tree(result)
        result['recommendation'] = conservative_recommendation(result)

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

# Volume Profile
def calculate_volume_profile(df, bins=50, value_area_pct=0.7):
    price_min = df['Low'].min()
    price_max = df['High'].max()
    bin_edges = np.linspace(price_min, price_max, bins + 1)
    volume_profile = np.zeros(bins)
    for i in range(bins):
        bin_low, bin_high = bin_edges[i], bin_edges[i+1]
        mask = (df['High'] >= bin_low) & (df['Low'] <= bin_high)
        volume_profile[i] = df.loc[mask, 'Volume'].sum()
    poc_idx = np.argmax(volume_profile)
    poc = (bin_edges[poc_idx] + bin_edges[poc_idx + 1]) / 2
    total_volume = volume_profile.sum()
    target = total_volume * value_area_pct
    vah_idx = val_idx = poc_idx
    current_vol = volume_profile[poc_idx]
    while current_vol < target and (vah_idx < bins-1 or val_idx > 0):
        up_vol = volume_profile[vah_idx + 1] if vah_idx < bins-1 else 0
        down_vol = volume_profile[val_idx - 1] if val_idx > 0 else 0
        if up_vol >= down_vol and vah_idx < bins-1:
            vah_idx += 1
            current_vol += up_vol
        elif val_idx > 0:
            val_idx -= 1
            current_vol += down_vol
    vah = bin_edges[vah_idx + 1]
    val = bin_edges[val_idx]
    return poc, vah, val

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
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('regularMarketPrice') or info.get('preMarketPrice') or info.get('previousClose')
        price_note = "pre-market" if 'preMarketPrice' in info else "last close"
        today = datetime.now().strftime("%Y-%m-%d")

        # Daily data
        daily = stock.history(period="3y")
        if daily.empty:
            return {"ticker": ticker, "error": "no daily data"}
        d20 = daily['Close'].rolling(20).mean().iloc[-1]
        d50 = daily['Close'].rolling(50).mean().iloc[-1]
        d100 = daily['Close'].rolling(100).mean().iloc[-1]
        d200 = daily['Close'].rolling(200).mean().iloc[-1]

        # Weekly data
        weekly = stock.history(period="10y", interval="1wk")
        if weekly.empty:
            return {"ticker": ticker, "error": "no weekly data"}
        w10 = weekly['Close'].rolling(10).mean().iloc[-1]
        w20 = weekly['Close'].rolling(20).mean().iloc[-1]
        w200 = weekly['Close'].rolling(200).mean().iloc[-1]

        # VPVR
        daily_vp_df = daily.iloc[-daily_bars:]
        daily_poc, daily_vah, daily_val = calculate_volume_profile(daily_vp_df)
        weekly_vp_df = weekly.iloc[-weekly_bars:]
        weekly_poc, weekly_vah, weekly_val = calculate_volume_profile(weekly_vp_df)

        # Pivots
        daily_highs, daily_lows = detect_swings(daily)
        daily_supports, daily_resistances = select_top_sr(daily_highs, daily_lows, current_price)
        weekly_highs, weekly_lows = detect_swings(weekly)
        weekly_supports, weekly_resistances = select_top_sr(weekly_highs, weekly_lows, current_price)

        # Signal
        daily_state = get_larsson_state(daily)
        weekly_state = get_larsson_state(weekly)
        mapping = {
            (1,1): "FULL HOLD + ADD", (1,0): "HOLD", (1,-1): "HOLD MOST → REDUCE",
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
            'd20': float(d20) if not pd.isna(d20) else None,
            'd50': float(d50) if not pd.isna(d50) else None,
            'd100': float(d100) if not pd.isna(d100) else None,
            'd200': float(d200) if not pd.isna(d200) else None,
            'w10': float(w10) if not pd.isna(w10) else None,
            'w20': float(w20) if not pd.isna(w20) else None,
            'w200': float(w200) if not pd.isna(w200) else None,
            'daily_poc': float(daily_poc), 'daily_vah': float(daily_vah), 'daily_val': float(daily_val),
            'weekly_poc': float(weekly_poc), 'weekly_vah': float(weekly_vah), 'weekly_val': float(weekly_val),
            's1': float(daily_supports[0]) if not pd.isna(daily_supports[0]) else None,
            's2': float(daily_supports[1]) if not pd.isna(daily_supports[1]) else None,
            's3': float(daily_supports[2]) if not pd.isna(daily_supports[2]) else None,
            'r1': float(daily_resistances[0]) if not pd.isna(daily_resistances[0]) else None,
            'r2': float(daily_resistances[1]) if not pd.isna(daily_resistances[1]) else None,
            'r3': float(daily_resistances[2]) if not pd.isna(daily_resistances[2]) else None,
            'notes': ''
        }

        # Replace your existing confluence/recommendation with the conservative versions
        result['confluence'] = confluence_decision_tree(result)
        result['recommendation'] = conservative_recommendation(result)

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
