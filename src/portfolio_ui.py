"""
Portfolio Management UI - Streamlit Web Interface
Run with: streamlit run src/portfolio_ui.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import yfinance as yf

# Configure page
st.set_page_config(page_title="Portfolio Manager", page_icon="📊", layout="wide")

# File paths
DATA_DIR = Path("data")
HOLDINGS_FILE = DATA_DIR / "holdings.csv"
TARGETS_FILE = DATA_DIR / "targets.csv"


def load_holdings():
    """Load holdings data from CSV"""
    return pd.read_csv(HOLDINGS_FILE)


def save_holdings(df):
    """Save holdings data to CSV"""
    df.to_csv(HOLDINGS_FILE, index=False)


def load_targets():
    """Load targets data from CSV"""
    return pd.read_csv(TARGETS_FILE)


def save_targets(df):
    """Save targets data to CSV"""
    df.to_csv(TARGETS_FILE, index=False)


def get_current_price(ticker):
    """Fetch current price for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        return stock.history(period="1d")["Close"].iloc[-1]
    except:
        return None


def calculate_new_average(old_qty, old_cost, new_qty, new_price):
    """Calculate new average cost after purchase"""
    if old_qty == 0:
        return new_price
    total_qty = old_qty + new_qty
    total_cost = (old_qty * old_cost) + (new_qty * new_price)
    return total_cost / total_qty


# Main Title
st.title("📊 Portfolio Manager")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["➕ Add Transaction", "📈 Holdings", "🎯 Targets", "📊 Summary"]
)

# TAB 1: Add Transaction
with tab1:
    st.header("Add Stock Purchase")

    col1, col2 = st.columns(2)

    with col1:
        ticker = st.text_input(
            "Ticker Symbol", help="e.g., TSLA, NVDA, BTC-USD"
        ).upper()
        quantity = st.number_input("Quantity", min_value=0.0, step=1.0, format="%.4f")

    with col2:
        price = st.number_input(
            "Purchase Price ($)", min_value=0.0, step=0.01, format="%.2f"
        )
        date = st.date_input("Purchase Date", datetime.now())

    # Get current price button
    if ticker:
        col_price1, col_price2 = st.columns([1, 3])
        with col_price1:
            if st.button("Get Current Price"):
                with st.spinner(f"Fetching {ticker} price..."):
                    current_price = get_current_price(ticker)
                    if current_price:
                        st.session_state["fetched_price"] = current_price
                        st.success(f"Current: ${current_price:.2f}")
                    else:
                        st.error("Could not fetch price")

        with col_price2:
            if "fetched_price" in st.session_state:
                st.info(
                    f"💡 Current market price: ${st.session_state['fetched_price']:.2f}"
                )

    st.markdown("---")

    if st.button("➕ Add Transaction", type="primary", width="stretch"):
        if not ticker:
            st.error("⚠️ Please enter a ticker symbol")
        elif quantity <= 0:
            st.error("⚠️ Quantity must be greater than 0")
        elif price <= 0:
            st.error("⚠️ Price must be greater than 0")
        else:
            try:
                df = load_holdings()

                # Check if ticker exists
                if ticker in df["ticker"].values:
                    # Update existing position
                    idx = df[df["ticker"] == ticker].index[0]
                    old_qty = df.loc[idx, "quantity"]
                    old_cost = df.loc[idx, "avg_cost"]

                    new_total_qty = old_qty + quantity
                    new_avg_cost = calculate_new_average(
                        old_qty, old_cost, quantity, price
                    )

                    df.loc[idx, "quantity"] = new_total_qty
                    df.loc[idx, "avg_cost"] = round(new_avg_cost, 2)
                    df.loc[idx, "last_updated"] = date.strftime("%Y-%m-%d")

                    st.success(f"✅ Updated {ticker} position!")
                    st.info(
                        f"""
                    **Previous:** {old_qty:,.4f} shares @ ${old_cost:,.2f}  
                    **Added:** {quantity:,.4f} shares @ ${price:,.2f}  
                    **New Total:** {new_total_qty:,.4f} shares @ ${new_avg_cost:,.2f}
                    """
                    )
                else:
                    # Add new position
                    new_row = pd.DataFrame(
                        {
                            "ticker": [ticker],
                            "quantity": [quantity],
                            "avg_cost": [round(price, 2)],
                            "last_updated": [date.strftime("%Y-%m-%d")],
                            "min_quantity": [0],
                        }
                    )
                    df = pd.concat([df, new_row], ignore_index=True)

                    st.success(f"✅ Added new position: {ticker}")
                    st.info(f"**{quantity:,.4f} shares @ ${price:,.2f}**")

                # Save to file
                save_holdings(df)
                st.balloons()

                # Clear fetched price
                if "fetched_price" in st.session_state:
                    del st.session_state["fetched_price"]

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# TAB 2: View Holdings
with tab2:
    st.header("Current Holdings")

    try:
        df = load_holdings()

        # Filter out zero positions
        active_holdings = df[df["quantity"] > 0].copy()

        if len(active_holdings) > 0:
            # Get current prices for active holdings
            with st.spinner("Fetching current prices..."):
                current_prices = {}
                for ticker in active_holdings["ticker"]:
                    price = get_current_price(ticker)
                    current_prices[ticker] = price if price else 0

            # Add calculated columns
            active_holdings["current_price"] = active_holdings["ticker"].map(
                current_prices
            )
            active_holdings["market_value"] = (
                active_holdings["quantity"] * active_holdings["current_price"]
            )
            active_holdings["cost_basis"] = (
                active_holdings["quantity"] * active_holdings["avg_cost"]
            )
            active_holdings["gain_loss"] = (
                active_holdings["market_value"] - active_holdings["cost_basis"]
            )
            active_holdings["gain_loss_pct"] = (
                active_holdings["gain_loss"] / active_holdings["cost_basis"] * 100
            )

            # Format for display
            display_df = active_holdings[
                [
                    "ticker",
                    "quantity",
                    "avg_cost",
                    "current_price",
                    "market_value",
                    "gain_loss",
                    "gain_loss_pct",
                    "last_updated",
                ]
            ].copy()

            # Display summary metrics
            col1, col2, col3, col4 = st.columns(4)

            total_value = active_holdings["market_value"].sum()
            total_cost = active_holdings["cost_basis"].sum()
            total_gain = total_value - total_cost
            total_gain_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0

            with col1:
                st.metric("Total Portfolio Value", f"${total_value:,.2f}")
            with col2:
                st.metric("Total Cost Basis", f"${total_cost:,.2f}")
            with col3:
                st.metric(
                    "Total Gain/Loss",
                    f"${total_gain:,.2f}",
                    delta=f"{total_gain_pct:.2f}%",
                )
            with col4:
                st.metric("Number of Positions", len(active_holdings))

            st.markdown("---")

            # Style the dataframe
            def highlight_gains(val):
                if isinstance(val, (int, float)):
                    color = "green" if val > 0 else "red" if val < 0 else "gray"
                    return f"color: {color}"
                return ""

            styled_df = display_df.style.format(
                {
                    "quantity": "{:,.4f}",
                    "avg_cost": "${:,.2f}",
                    "current_price": "${:,.2f}",
                    "market_value": "${:,.2f}",
                    "gain_loss": "${:,.2f}",
                    "gain_loss_pct": "{:+.2f}%",
                }
            ).map(highlight_gains, subset=["gain_loss", "gain_loss_pct"])

            st.dataframe(styled_df, width="stretch", hide_index=True)

            # Show all holdings (including zeros)
            with st.expander("Show All Holdings (including zero positions)"):
                st.dataframe(df, width="stretch", hide_index=True)
        else:
            st.info("📭 No active holdings. Add a transaction to get started!")

    except Exception as e:
        st.error(f"❌ Error loading holdings: {str(e)}")

# TAB 3: Targets
with tab3:
    st.header("Portfolio Target Allocations")

    try:
        targets_df = load_targets()

        st.info(
            "💡 Edit the table below to adjust your target allocations. Click 'Save Targets' when done."
        )

        # Make the dataframe editable
        edited_df = st.data_editor(
            targets_df,
            width="stretch",
            num_rows="dynamic",
            column_config={
                "ticker": st.column_config.TextColumn("Ticker", required=True),
                "target_pct": st.column_config.NumberColumn(
                    "Target %",
                    help="Target percentage of portfolio (0.5 = 50%)",
                    format="%.2f",
                    min_value=0.0,
                    max_value=1.0,
                ),
                "target_value": st.column_config.NumberColumn(
                    "Target Value ($)",
                    help="Target dollar amount",
                    format="$%.2f",
                    min_value=0.0,
                ),
            },
        )

        # Check if target percentages sum properly
        total_pct = edited_df["target_pct"].sum()
        if total_pct > 0:
            if abs(total_pct - 1.0) < 0.01:
                st.success(f"✅ Target percentages sum to {total_pct:.1%}")
            else:
                st.warning(f"⚠️ Target percentages sum to {total_pct:.1%} (not 100%)")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("💾 Save Targets", type="primary"):
                save_targets(edited_df)
                st.success("✅ Targets saved successfully!")
                st.rerun()

    except Exception as e:
        st.error(f"❌ Error loading targets: {str(e)}")

# TAB 4: Summary
with tab4:
    st.header("Portfolio Summary")

    try:
        holdings_df = load_holdings()
        targets_df = load_targets()

        active_holdings = holdings_df[holdings_df["quantity"] > 0].copy()

        if len(active_holdings) > 0:
            # Get current prices
            with st.spinner("Calculating portfolio metrics..."):
                for idx, row in active_holdings.iterrows():
                    price = get_current_price(row["ticker"])
                    active_holdings.loc[idx, "current_price"] = price if price else 0

                active_holdings["market_value"] = (
                    active_holdings["quantity"] * active_holdings["current_price"]
                )
                active_holdings["cost_basis"] = (
                    active_holdings["quantity"] * active_holdings["avg_cost"]
                )

            total_value = active_holdings["market_value"].sum()

            # Calculate actual vs target allocation
            active_holdings["actual_pct"] = (
                active_holdings["market_value"] / total_value
            )

            # Merge with targets
            summary = active_holdings.merge(
                targets_df[["ticker", "target_pct"]], on="ticker", how="left"
            )
            summary["target_pct"] = summary["target_pct"].fillna(0)
            summary["allocation_diff"] = summary["actual_pct"] - summary["target_pct"]

            # Display allocation comparison
            st.subheader("Allocation vs Targets")

            for _, row in summary.iterrows():
                col1, col2, col3 = st.columns([1, 2, 1])

                with col1:
                    st.write(f"**{row['ticker']}**")

                with col2:
                    actual_pct = row["actual_pct"] * 100
                    target_pct = row["target_pct"] * 100

                    st.progress(min(row["actual_pct"], 1.0))
                    st.caption(f"Actual: {actual_pct:.1f}% | Target: {target_pct:.1f}%")

                with col3:
                    diff = row["allocation_diff"] * 100
                    if abs(diff) < 1:
                        st.success("✓ On target")
                    elif diff > 0:
                        st.warning(f"↑ {diff:+.1f}%")
                    else:
                        st.info(f"↓ {diff:+.1f}%")

            st.markdown("---")

            # Position details
            st.subheader("Position Details")

            detail_df = summary[
                [
                    "ticker",
                    "quantity",
                    "avg_cost",
                    "current_price",
                    "market_value",
                    "actual_pct",
                    "target_pct",
                ]
            ].copy()

            styled_detail = detail_df.style.format(
                {
                    "quantity": "{:,.4f}",
                    "avg_cost": "${:,.2f}",
                    "current_price": "${:,.2f}",
                    "market_value": "${:,.2f}",
                    "actual_pct": "{:.1%}",
                    "target_pct": "{:.1%}",
                }
            )

            st.dataframe(styled_detail, width="stretch", hide_index=True)

        else:
            st.info("📭 No positions to display")

    except Exception as e:
        st.error(f"❌ Error generating summary: {str(e)}")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    st.markdown("### Data Files")
    st.code(str(HOLDINGS_FILE))
    st.code(str(TARGETS_FILE))

    st.markdown("---")

    st.markdown("### Quick Actions")
    if st.button("🔄 Refresh Data"):
        st.rerun()

    st.markdown("---")

    st.markdown("### About")
    st.info(
        """
    **Portfolio Manager UI**
    
    A simple web interface for managing your stock portfolio.
    
    - Add transactions
    - View holdings
    - Update targets
    - Track performance
    """
    )

    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
