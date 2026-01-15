"""
Simple script to add a new position to portfolio_positions.csv
Run after executing Monday trades
"""

import pandas as pd
from pathlib import Path
from datetime import datetime


def add_position():
    """Interactive script to add a position"""

    # Load existing positions
    positions_path = Path("../data/portfolio_positions.csv")
    df = pd.read_csv(positions_path)

    print("\n" + "=" * 60)
    print("ADD NEW POSITION TO PORTFOLIO")
    print("=" * 60)
    print(f"Current positions: {len(df)}")
    if len(df) > 0:
        print(f"Holdings: {', '.join(df['Ticker'].tolist())}")
    print("=" * 60)

    # Get user input
    ticker = input("\nTicker Symbol (e.g., TSLA): ").strip().upper()

    # Check if already exists
    if ticker in df["Ticker"].values:
        print(f"⚠️ Warning: {ticker} already exists in portfolio!")
        overwrite = input("Continue anyway? (y/n): ").strip().lower()
        if overwrite != "y":
            print("Cancelled.")
            return

    entry_date = input("Entry Date (YYYY-MM-DD or press Enter for today): ").strip()
    if not entry_date:
        entry_date = datetime.now().strftime("%Y-%m-%d")

    entry_price = float(input("Entry Price: $").strip())
    shares = int(input("Number of Shares: ").strip())

    entry_state = input("Entry State (P1/P2/N1/N2, usually P1): ").strip().upper()
    if not entry_state:
        entry_state = "P1"

    # Default signal based on state
    signal_map = {"P1": "🟡 BUY", "P2": "⚪ HOLD", "N1": "⚪ HOLD", "N2": "🔵 SELL"}
    entry_signal = signal_map.get(entry_state, "🟡 BUY")

    # Summary
    cost_basis = entry_price * shares
    print("\n" + "=" * 60)
    print("CONFIRM NEW POSITION:")
    print("=" * 60)
    print(f"Ticker: {ticker}")
    print(f"Entry Date: {entry_date}")
    print(f"Entry Price: ${entry_price:.2f}")
    print(f"Shares: {shares}")
    print(f"Cost Basis: ${cost_basis:,.2f}")
    print(f"Entry State: {entry_state}")
    print(f"Entry Signal: {entry_signal}")
    print("=" * 60)

    confirm = input("\nAdd this position? (y/n): ").strip().lower()

    if confirm == "y":
        # Add to dataframe
        new_row = pd.DataFrame(
            {
                "Ticker": [ticker],
                "Entry_Date": [entry_date],
                "Entry_Price": [entry_price],
                "Shares": [shares],
                "Entry_State": [entry_state],
                "Current_State": [entry_state],  # Same as entry initially
                "Entry_Signal": [entry_signal],
            }
        )

        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(positions_path, index=False)

        print(f"\n✅ {ticker} added successfully!")
        print(f"Portfolio now has {len(df)} position(s)")
        print(f"\nNext: Run Friday scanner to update states and calculate P&L")
    else:
        print("Cancelled.")


if __name__ == "__main__":
    try:
        add_position()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
