"""
Portfolio Management UI - Streamlit Web Interface
Run with: streamlit run src/portfolio_ui.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(page_title="Portfolio Manager", page_icon="📊", layout="wide")

# File paths
DATA_DIR = Path("data")
HOLDINGS_FILE = DATA_DIR / "holdings.csv"
TARGETS_FILE = DATA_DIR / "targets.csv"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"


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


def load_transactions():
    """Load transaction history from CSV"""
    try:
        df = pd.read_csv(TRANSACTIONS_FILE)
        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return pd.DataFrame(
            columns=[
                "date",
                "type",
                "ticker",
                "quantity",
                "price",
                "total_value",
                "notes",
            ]
        )


def log_transaction(trans_type, ticker, quantity, price, notes=""):
    """Log a transaction to the transactions file"""
    try:
        df = load_transactions()
        new_transaction = pd.DataFrame(
            {
                "date": [datetime.now()],
                "type": [trans_type],
                "ticker": [ticker],
                "quantity": [quantity],
                "price": [price],
                "total_value": [quantity * price],
                "notes": [notes],
            }
        )
        df = pd.concat([df, new_transaction], ignore_index=True)
        df.to_csv(TRANSACTIONS_FILE, index=False)
    except Exception as e:
        st.error(f"Error logging transaction: {str(e)}")


def get_current_price(ticker):
    """Fetch current price for a ticker (with cache bypass)"""
    try:
        # Create new ticker instance to avoid caching
        stock = yf.Ticker(ticker)
        # Try to get most recent data
        hist = stock.history(period="5d")  # Use 5d to ensure we get data
        if not hist.empty:
            latest_price = hist["Close"].iloc[-1]
            latest_date = hist.index[-1]
            # Debug: show what we fetched
            # st.write(f"DEBUG {ticker}: ${latest_price:.2f} from {latest_date.date()}")
            return latest_price
        return None
    except Exception as e:
        st.warning(f"Failed to fetch {ticker} price: {str(e)}")
        return None


def calculate_new_average(old_qty, old_cost, new_qty, new_price):
    """Calculate new average cost after purchase"""
    if old_qty == 0:
        return new_price
    total_qty = old_qty + new_qty
    total_cost = (old_qty * old_cost) + (new_qty * new_price)
    return total_cost / total_qty


def calculate_sell_average(old_qty, old_cost, sell_qty):
    """Calculate new average cost after selling (remains the same)"""
    return old_cost  # Average cost per share doesn't change when selling


# Main Title
st.title("📊 Portfolio Manager")
st.markdown("---")

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["➕ Buy", "➖ Sell", "📈 Holdings", "📊 Charts", "🎯 Targets", "📜 History"]
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

    # Notes field
    notes = st.text_input(
        "Notes (optional)",
        placeholder="e.g., Buying the dip, Adding to position, etc.",
        help="Add custom notes to track why you made this trade",
    )

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

                    # Log transaction
                    transaction_note = (
                        f"Updated position. {notes}" if notes else "Updated position"
                    )
                    log_transaction("BUY", ticker, quantity, price, transaction_note)

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

                    # Log transaction
                    transaction_note = (
                        f"New position. {notes}" if notes else "New position"
                    )
                    log_transaction("BUY", ticker, quantity, price, transaction_note)

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

# TAB 2: Sell Stocks
with tab2:
    st.header("Sell Stock Position")

    try:
        holdings_df = load_holdings()
        active_holdings = holdings_df[holdings_df["quantity"] > 0].copy()

        if len(active_holdings) == 0:
            st.warning("No active positions to sell")
        else:
            col1, col2 = st.columns(2)

            with col1:
                # Dropdown of available tickers
                sell_ticker = st.selectbox(
                    "Select Stock to Sell",
                    options=active_holdings["ticker"].tolist(),
                    help="Select from your current holdings",
                )

                # Show current position
                if sell_ticker:
                    current_pos = active_holdings[
                        active_holdings["ticker"] == sell_ticker
                    ].iloc[0]
                    st.info(
                        f"**Current Position:** {current_pos['quantity']:,.4f} shares @ ${current_pos['avg_cost']:,.2f} avg cost"
                    )

                sell_quantity = st.number_input(
                    "Quantity to Sell",
                    min_value=0.0,
                    max_value=float(current_pos["quantity"]) if sell_ticker else 0.0,
                    step=1.0,
                    format="%.4f",
                    help="Cannot exceed current holdings",
                )

            with col2:
                sell_price = st.number_input(
                    "Sell Price ($)", min_value=0.0, step=0.01, format="%.2f"
                )
                sell_date = st.date_input("Sell Date", datetime.now(), key="sell_date")

            # Notes field
            sell_notes = st.text_input(
                "Notes (optional)",
                key="sell_notes",
                placeholder="e.g., Taking profits, Rebalancing, Stop loss, etc.",
                help="Add custom notes to track why you made this trade",
            )

            # Get current price button
            if sell_ticker:
                col_price1, col_price2 = st.columns([1, 3])
                with col_price1:
                    if st.button("Get Current Price", key="sell_get_price"):
                        with st.spinner(f"Fetching {sell_ticker} price..."):
                            current_price = get_current_price(sell_ticker)
                            if current_price:
                                st.session_state["sell_fetched_price"] = current_price
                                st.success(f"Current: ${current_price:.2f}")
                            else:
                                st.error("Could not fetch price")

                with col_price2:
                    if "sell_fetched_price" in st.session_state:
                        st.info(
                            f"💡 Current market price: ${st.session_state['sell_fetched_price']:.2f}"
                        )

            # Calculate gain/loss preview
            if sell_ticker and sell_quantity > 0 and sell_price > 0:
                cost_basis = current_pos["avg_cost"] * sell_quantity
                proceeds = sell_price * sell_quantity
                gain_loss = proceeds - cost_basis
                gain_loss_pct = (gain_loss / cost_basis * 100) if cost_basis > 0 else 0

                st.markdown("---")
                st.subheader("Transaction Preview")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Cost Basis", f"${cost_basis:,.2f}")
                with col_b:
                    st.metric("Proceeds", f"${proceeds:,.2f}")
                with col_c:
                    st.metric(
                        "Gain/Loss",
                        f"${gain_loss:,.2f}",
                        delta=f"{gain_loss_pct:+.2f}%",
                    )

            st.markdown("---")

            if st.button(
                "➖ Sell Stock", type="primary", width="stretch", key="sell_button"
            ):
                if not sell_ticker:
                    st.error("⚠️ Please select a stock to sell")
                elif sell_quantity <= 0:
                    st.error("⚠️ Quantity must be greater than 0")
                elif sell_quantity > current_pos["quantity"]:
                    st.error(
                        f"⚠️ Cannot sell more than you own ({current_pos['quantity']:,.4f})"
                    )
                elif sell_price <= 0:
                    st.error("⚠️ Price must be greater than 0")
                else:
                    try:
                        df = load_holdings()
                        idx = df[df["ticker"] == sell_ticker].index[0]

                        old_qty = df.loc[idx, "quantity"]
                        old_cost = df.loc[idx, "avg_cost"]
                        new_qty = old_qty - sell_quantity

                        # Update holdings
                        df.loc[idx, "quantity"] = new_qty
                        df.loc[idx, "last_updated"] = sell_date.strftime("%Y-%m-%d")
                        # Avg cost stays the same when selling

                        # Calculate realized gain/loss
                        cost_basis = old_cost * sell_quantity
                        proceeds = sell_price * sell_quantity
                        realized_gain = proceeds - cost_basis
                        realized_gain_pct = (
                            (realized_gain / cost_basis * 100) if cost_basis > 0 else 0
                        )

                        # Log transaction
                        pnl_note = f"Realized P/L: ${realized_gain:,.2f} ({realized_gain_pct:+.2f}%)"
                        transaction_note = (
                            f"{pnl_note}. {sell_notes}" if sell_notes else pnl_note
                        )
                        log_transaction(
                            "SELL",
                            sell_ticker,
                            sell_quantity,
                            sell_price,
                            transaction_note,
                        )

                        # Save
                        save_holdings(df)

                        st.success(
                            f"✅ Sold {sell_quantity:,.4f} shares of {sell_ticker}!"
                        )
                        st.info(
                            f"""
                        **Sold:** {sell_quantity:,.4f} shares @ ${sell_price:,.2f}  
                        **Cost Basis:** ${cost_basis:,.2f} (@ ${old_cost:,.2f}/share)  
                        **Proceeds:** ${proceeds:,.2f}  
                        **Realized Gain/Loss:** ${realized_gain:,.2f} ({realized_gain_pct:+.2f}%)  
                        **Remaining:** {new_qty:,.4f} shares
                        """
                        )

                        st.balloons()

                        # Clear fetched price
                        if "sell_fetched_price" in st.session_state:
                            del st.session_state["sell_fetched_price"]

                        # Prompt to rerun
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

    except Exception as e:
        st.error(f"❌ Error loading holdings: {str(e)}")

# TAB 3: View Holdings
with tab3:
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

# TAB 4: Charts & Visualizations
with tab4:
    st.header("Portfolio Visualizations")

    try:
        holdings_df = load_holdings()
        active_holdings = holdings_df[holdings_df["quantity"] > 0].copy()

        if len(active_holdings) > 0:
            # Get current prices
            price_errors = []
            with st.spinner("Fetching current prices..."):
                for idx, row in active_holdings.iterrows():
                    price = get_current_price(row["ticker"])
                    if price and price > 0:
                        active_holdings.loc[idx, "current_price"] = price
                    else:
                        price_errors.append(row["ticker"])
                        active_holdings.loc[idx, "current_price"] = 0

            if price_errors:
                st.error(
                    f"⚠️ Failed to fetch prices for: {', '.join(price_errors)}. Click 'Refresh Data' or check your internet connection."
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

            total_value = active_holdings["market_value"].sum()
            total_cost = active_holdings["cost_basis"].sum()
            total_gain = total_value - total_cost
            total_gain_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0

            # Quick Stats at top
            st.subheader("📊 Quick Stats")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Portfolio Value", f"${total_value:,.2f}")
            with col2:
                st.metric("Total Cost", f"${total_cost:,.2f}")
            with col3:
                st.metric(
                    "Total Gain/Loss",
                    f"${total_gain:,.2f}",
                    delta=f"{total_gain_pct:+.2f}%",
                )
            with col4:
                st.metric("# Positions", len(active_holdings))

            st.markdown("---")

            # Charts in two columns
            col_left, col_right = st.columns(2)

            with col_left:
                st.subheader("Allocation by Market Value")

                # Pie chart for allocation
                fig_pie = px.pie(
                    active_holdings,
                    values="market_value",
                    names="ticker",
                    title="Current Portfolio Allocation",
                    hole=0.4,
                )
                fig_pie.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig_pie, use_container_width=True)

                st.subheader("Position Sizes")

                # Bar chart for position values
                fig_bar = px.bar(
                    active_holdings.sort_values("market_value", ascending=True),
                    x="market_value",
                    y="ticker",
                    orientation="h",
                    title="Market Value by Position",
                    labels={"market_value": "Market Value ($)", "ticker": "Ticker"},
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_right:
                st.subheader("Gain/Loss by Position")

                # Bar chart for gains/losses
                active_holdings_sorted = active_holdings.sort_values("gain_loss")
                colors = [
                    "red" if x < 0 else "green"
                    for x in active_holdings_sorted["gain_loss"]
                ]

                fig_gl = go.Figure(
                    data=[
                        go.Bar(
                            x=active_holdings_sorted["gain_loss"],
                            y=active_holdings_sorted["ticker"],
                            orientation="h",
                            marker_color=colors,
                            text=active_holdings_sorted["gain_loss"].apply(
                                lambda x: f"${x:,.2f}"
                            ),
                            textposition="auto",
                        )
                    ]
                )
                fig_gl.update_layout(
                    title="Unrealized Gain/Loss by Position",
                    xaxis_title="Gain/Loss ($)",
                    yaxis_title="Ticker",
                    showlegend=False,
                )
                st.plotly_chart(fig_gl, use_container_width=True)

                st.subheader("Performance %")

                # Bar chart for performance percentage
                fig_perf = px.bar(
                    active_holdings.sort_values("gain_loss_pct"),
                    x="gain_loss_pct",
                    y="ticker",
                    orientation="h",
                    title="Return % by Position",
                    labels={"gain_loss_pct": "Return %", "ticker": "Ticker"},
                    color="gain_loss_pct",
                    color_continuous_scale=["red", "yellow", "green"],
                    color_continuous_midpoint=0,  # Fix: Set midpoint at 0% so negative=red, positive=green
                    hover_data={
                        "current_price": ":.2f",
                        "avg_cost": ":.2f",
                        "gain_loss_pct": ":.2f",
                    },
                )
                st.plotly_chart(fig_perf, use_container_width=True)

                # Show price details table
                st.caption("Price Details:")
                price_details = active_holdings[
                    ["ticker", "current_price", "avg_cost", "gain_loss_pct"]
                ].copy()
                price_details.columns = [
                    "Ticker",
                    "Current Price",
                    "Avg Cost",
                    "Return %",
                ]
                st.dataframe(price_details, hide_index=True)

            # Transaction history chart if available
            st.markdown("---")
            st.subheader("Transaction History")

            transactions_df = load_transactions()
            if not transactions_df.empty:
                # Group by type
                trans_summary = (
                    transactions_df.groupby("type")["total_value"].sum().reset_index()
                )

                col_t1, col_t2 = st.columns(2)

                with col_t1:
                    # Transaction count by type
                    trans_count = transactions_df["type"].value_counts().reset_index()
                    trans_count.columns = ["Type", "Count"]

                    fig_trans = px.pie(
                        trans_count,
                        values="Count",
                        names="Type",
                        title="Transactions by Type",
                        color="Type",
                        color_discrete_map={"BUY": "green", "SELL": "red"},
                    )
                    st.plotly_chart(fig_trans, use_container_width=True)

                with col_t2:
                    # Transaction volume by type
                    fig_vol = px.bar(
                        trans_summary,
                        x="type",
                        y="total_value",
                        title="Transaction Volume by Type",
                        labels={"total_value": "Total Value ($)", "type": "Type"},
                        color="type",
                        color_discrete_map={"BUY": "green", "SELL": "red"},
                    )
                    st.plotly_chart(fig_vol, use_container_width=True)

                # Recent transactions timeline
                if len(transactions_df) > 1:
                    st.subheader("Recent Transaction Activity")
                    recent_trans = transactions_df.sort_values(
                        "date", ascending=False
                    ).head(20)

                    fig_timeline = px.scatter(
                        recent_trans,
                        x="date",
                        y="ticker",
                        size="total_value",
                        color="type",
                        title="Recent Transactions Timeline",
                        labels={
                            "date": "Date",
                            "ticker": "Ticker",
                            "total_value": "Value ($)",
                        },
                        color_discrete_map={"BUY": "green", "SELL": "red"},
                        hover_data=["quantity", "price"],
                    )
                    st.plotly_chart(fig_timeline, use_container_width=True)
            else:
                st.info("No transaction history available yet")
        else:
            st.info("No holdings to visualize. Add some transactions first!")

    except Exception as e:
        st.error(f"❌ Error generating charts: {str(e)}")

# TAB 5: Targets
with tab5:
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

# TAB 6: Transaction History
with tab6:
    st.header("Transaction History")

    try:
        transactions_df = load_transactions()

        if transactions_df.empty:
            st.info("No transactions yet. Start by buying or selling stocks!")
        else:
            # Summary stats
            total_buys = len(transactions_df[transactions_df["type"] == "BUY"])
            total_sells = len(transactions_df[transactions_df["type"] == "SELL"])
            total_buy_value = transactions_df[transactions_df["type"] == "BUY"][
                "total_value"
            ].sum()
            total_sell_value = transactions_df[transactions_df["type"] == "SELL"][
                "total_value"
            ].sum()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Buys", total_buys, delta=f"${total_buy_value:,.2f}")
            with col2:
                st.metric("Total Sells", total_sells, delta=f"${total_sell_value:,.2f}")
            with col3:
                net_flow = total_buy_value - total_sell_value
                st.metric(
                    "Net Cash Flow",
                    f"${abs(net_flow):,.2f}",
                    delta="Invested" if net_flow > 0 else "Withdrawn",
                )
            with col4:
                st.metric("Total Transactions", len(transactions_df))

            st.markdown("---")

            # Filters
            col_f1, col_f2, col_f3 = st.columns(3)

            with col_f1:
                filter_type = st.multiselect(
                    "Filter by Type", options=["BUY", "SELL"], default=["BUY", "SELL"]
                )

            with col_f2:
                unique_tickers = transactions_df["ticker"].unique().tolist()
                filter_ticker = st.multiselect(
                    "Filter by Ticker", options=unique_tickers, default=unique_tickers
                )

            with col_f3:
                date_range = st.date_input(
                    "Date Range",
                    value=(
                        transactions_df["date"].min().date(),
                        transactions_df["date"].max().date(),
                    ),
                    key="trans_date_range",
                )

            # Apply filters
            filtered_df = transactions_df[
                (transactions_df["type"].isin(filter_type))
                & (transactions_df["ticker"].isin(filter_ticker))
            ]

            if len(date_range) == 2:
                filtered_df = filtered_df[
                    (filtered_df["date"].dt.date >= date_range[0])
                    & (filtered_df["date"].dt.date <= date_range[1])
                ]

            st.markdown("---")

            # Display transactions
            if filtered_df.empty:
                st.warning("No transactions match the selected filters")
            else:
                st.subheader(f"Showing {len(filtered_df)} transaction(s)")

                # Format for display
                display_trans = filtered_df.copy()
                display_trans["date"] = display_trans["date"].dt.strftime("%Y-%m-%d")
                display_trans = display_trans.sort_values("date", ascending=False)

                # Style the dataframe
                def color_trans_type(val):
                    if val == "BUY":
                        return "color: green"
                    elif val == "SELL":
                        return "color: red"
                    return ""

                styled_trans = display_trans.style.format(
                    {
                        "quantity": "{:,.4f}",
                        "price": "${:,.2f}",
                        "total_value": "${:,.2f}",
                    }
                ).map(color_trans_type, subset=["type"])

                st.dataframe(styled_trans, width="stretch", hide_index=True)

                # Download button
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                )

                # Transaction details in expander
                with st.expander("📋 Detailed Transaction View"):
                    for idx, row in filtered_df.sort_values(
                        "date", ascending=False
                    ).iterrows():
                        trans_type_color = "🟢" if row["type"] == "BUY" else "🔴"
                        st.markdown(
                            f"""
                        **{trans_type_color} {row['type']}** | {row['date'].strftime('%Y-%m-%d %H:%M')}  
                        **Ticker:** {row['ticker']} | **Quantity:** {row['quantity']:,.4f} | **Price:** ${row['price']:,.2f} | **Total:** ${row['total_value']:,.2f}  
                        **Notes:** {row['notes'] if row['notes'] else 'N/A'}
                        ---
                        """
                        )

    except Exception as e:
        st.error(f"❌ Error loading transaction history: {str(e)}")

# TAB 7: Summary (formerly TAB 4)
with st.container():
    # This is a hidden tab but keeping the old summary logic for reference
    # The summary is now incorporated into Charts tab
    pass

# Sidebar
with st.sidebar:
    st.header("⚙️ Quick Info")

    # Quick portfolio summary
    try:
        holdings_df = load_holdings()
        active_holdings = holdings_df[holdings_df["quantity"] > 0]

        if len(active_holdings) > 0:
            with st.spinner("Loading..."):
                total_positions = len(active_holdings)

                st.metric("Active Positions", total_positions)

                # Show tickers
                st.markdown("**Holdings:**")
                for ticker in active_holdings["ticker"].tolist():
                    st.caption(f"• {ticker}")
        else:
            st.info("No active positions")
    except:
        pass

    st.markdown("---")

    st.markdown("### Data Files")
    st.code(str(HOLDINGS_FILE), language="text")
    st.code(str(TARGETS_FILE), language="text")
    st.code(str(TRANSACTIONS_FILE), language="text")

    st.markdown("---")

    st.markdown("### Quick Actions")
    if st.button("🔄 Refresh Data"):
        st.rerun()

    st.markdown("---")

    st.markdown("### About")
    st.info(
        """
    **Portfolio Manager UI v2.0**
    
    Enhanced with:
    - Buy & Sell transactions
    - Transaction history logging
    - Interactive charts
    - Performance tracking
    """
    )

    st.markdown("---")
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
