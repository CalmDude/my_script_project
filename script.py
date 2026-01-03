import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

# SMMA function (for Larsson)
def smma(series, length):
    smma = pd.Series(np.nan, index=series.index)
    sma_val = series.rolling(length).mean()
    smma.iloc[length-1] = sma_val.iloc[length-1]
    for i in range(length, len(series)):
        smma.iloc[i] = (smma.iloc[i-1] * (length - 1) + series.iloc[i]) / length
    return smma

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

# Main
ticker = input("Enter ticker (e.g., PLTR): ").upper()
stock = yf.Ticker(ticker)

# Current price
info = stock.info
current_price = info.get('regularMarketPrice') or info.get('preMarketPrice') or info['previousClose']
price_note = "pre-market" if 'preMarketPrice' in info else "last close"
today = datetime.now().strftime("%Y-%m-%d")

# Daily data (3y for SMAs/VP/pivots)
daily = stock.history(period="3y")
d20 = daily['Close'].rolling(20).mean().iloc[-1]
d50 = daily['Close'].rolling(50).mean().iloc[-1]
d100 = daily['Close'].rolling(100).mean().iloc[-1]
d200 = daily['Close'].rolling(200).mean().iloc[-1]

# Weekly data
weekly = stock.history(period="10y", interval="1wk")
w10 = weekly['Close'].rolling(10).mean().iloc[-1]
w20 = weekly['Close'].rolling(20).mean().iloc[-1]
w200 = weekly['Close'].rolling(200).mean().iloc[-1]

# VPVR
daily_vp_df = daily.iloc[-60:]
daily_poc, daily_vah, daily_val = calculate_volume_profile(daily_vp_df)
weekly_vp_df = weekly.iloc[-52:]
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

# Output
print(f"Decision Table Signal: {signal}")
print(f"Current Price: ~${current_price:.2f} ({price_note} as of {today})")
print(f"Daily SMA: D20: {d20:.2f}, D50: {d50:.2f}, D100: {d100:.2f}, D200: {d200:.2f}")
print(f"Weekly SMA: W10: {w10:.2f}, W20: {w20:.2f}, W200: {w200:.2f}")
print(f"Daily VPVR: POC: {daily_poc:.2f}, VAH: {daily_vah:.2f}, VAL: {daily_val:.2f}")
print(f"Weekly VPVR: POC: {weekly_poc:.2f}, VAH: {weekly_vah:.2f}, VAL: {weekly_val:.2f}")
print(f"Daily Pivot S/R: Support 1: {daily_supports[0]:.2f}, Support 2: {daily_supports[1]:.2f}, Support 3: {daily_supports[2]:.2f} | Resistance 1: {daily_resistances[0]:.2f}, Resistance 2: {daily_resistances[1]:.2f}, Resistance 3: {daily_resistances[2]:.2f}")
print(f"Weekly Pivot S/R: Support 1: {weekly_supports[0]:.2f}, Support 2: {weekly_supports[1]:.2f}, Support 3: {weekly_supports[2]:.2f} | Resistance 1: {weekly_resistances[0]:.2f}, Resistance 2: {weekly_resistances[1]:.2f}, Resistance 3: {weekly_resistances[2]:.2f}")