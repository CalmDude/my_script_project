import pandas as pd

# Your watchlist
watchlist = [
    "ALAB",
    "AVGO",
    "MRVL",
    "ARM",
    "TSLA",
    "NVDA",
    "PLTR",
    "MU",
    "TSM",
    "ASML",
    "GOOG",
    "AMD",
]

# Load latest weekly report
df = pd.read_excel(
    "scanner_results/weekly_larsson/nasdaq100_weekly_20260115.xlsx",
    sheet_name="Weekly Data",
)

# Filter for watchlist tickers
watchlist_data = df[df["Ticker"].isin(watchlist)].copy()
watchlist_data = watchlist_data.sort_values("Weekly_Larsson", ascending=False)

print("=" * 100)
print("YOUR WATCHLIST - WEEKLY LARSSON ANALYSIS (Week of Jan 15, 2026)")
print("=" * 100)

# GHB Strategy signals
p1_stocks = watchlist_data[watchlist_data["Weekly_Larsson"] == "P1"]
p2_stocks = watchlist_data[watchlist_data["Weekly_Larsson"] == "P2"]
n1_stocks = watchlist_data[watchlist_data["Weekly_Larsson"] == "N1"]
n2_stocks = watchlist_data[watchlist_data["Weekly_Larsson"] == "N2"]

print(f"\n🟡 P1 (GOLD - STRONG BUY): {len(p1_stocks)} stocks")
if len(p1_stocks) > 0:
    print("-" * 100)
    print(
        f"{'Ticker':<8} {'Price':<10} {'D200':<10} {'Above D200':<12} {'ROC 4W':<10} {'Signal':<20}"
    )
    print("-" * 100)
    for _, row in p1_stocks.iterrows():
        distance = (row["Close"] - row["D200"]) / row["D200"] * 100
        print(
            f"{row['Ticker']:<8} ${row['Close']:<9.2f} ${row['D200']:<9.2f} {distance:>+10.1f}% {row['ROC_4W']:>+8.2f}% {'>>> BUY (GHB Strategy)':<20}"
        )

print(f"\n⚪ P2 (GRAY - HOLD/CONSOLIDATION): {len(p2_stocks)} stocks")
if len(p2_stocks) > 0:
    print("-" * 100)
    print(
        f"{'Ticker':<8} {'Price':<10} {'D200':<10} {'Above D200':<12} {'ROC 4W':<10} {'Signal':<20}"
    )
    print("-" * 100)
    for _, row in p2_stocks.iterrows():
        distance = (row["Close"] - row["D200"]) / row["D200"] * 100
        print(
            f"{row['Ticker']:<8} ${row['Close']:<9.2f} ${row['D200']:<9.2f} {distance:>+10.1f}% {row['ROC_4W']:>+8.2f}% {'HOLD if in position':<20}"
        )

print(f"\n⚪ N1 (GRAY - WEAK/HOLD): {len(n1_stocks)} stocks")
if len(n1_stocks) > 0:
    print("-" * 100)
    print(
        f"{'Ticker':<8} {'Price':<10} {'D200':<10} {'Below D200':<12} {'ROC 4W':<10} {'Signal':<20}"
    )
    print("-" * 100)
    for _, row in n1_stocks.iterrows():
        distance = (row["Close"] - row["D200"]) / row["D200"] * 100
        print(
            f"{row['Ticker']:<8} ${row['Close']:<9.2f} ${row['D200']:<9.2f} {distance:>+10.1f}% {row['ROC_4W']:>+8.2f}% {'HOLD if in position':<20}"
        )

print(f"\n🔵 N2 (BLUE - SELL ZONE): {len(n2_stocks)} stocks")
if len(n2_stocks) > 0:
    print("-" * 100)
    print(
        f"{'Ticker':<8} {'Price':<10} {'D200':<10} {'Below D200':<12} {'ROC 4W':<10} {'Signal':<20}"
    )
    print("-" * 100)
    for _, row in n2_stocks.iterrows():
        distance = (row["Close"] - row["D200"]) / row["D200"] * 100
        print(
            f"{row['Ticker']:<8} ${row['Close']:<9.2f} ${row['D200']:<9.2f} {distance:>+10.1f}% {row['ROC_4W']:>+8.2f}% {'>>> SELL (Exit)':<20}"
        )

print("\n" + "=" * 100)
print("GHB STRATEGY SUMMARY")
print("=" * 100)
print(f"BUY Signals (P1): {len(p1_stocks)} stocks")
print(f"HOLD Positions (P2/N1): {len(p2_stocks) + len(n1_stocks)} stocks")
print(f"SELL Signals (N2 + below D200): {len(n2_stocks)} stocks")
print(f"\nMissing from report: {len(watchlist) - len(watchlist_data)} stocks")
if len(watchlist) > len(watchlist_data):
    missing = set(watchlist) - set(watchlist_data["Ticker"].tolist())
    print(f"  Not found: {', '.join(missing)}")
print("=" * 100)
