import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title='Stock Analysis Viewer', layout='wide')

st.title('Stock Analysis Viewer')

# Load combined CSV
@st.cache_data
def load_combined(path='batch_results.csv'):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

@st.cache_data
def load_symbol(ticker):
    path = os.path.join('results', f"{ticker}.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame()

df = load_combined()
if df.empty:
    st.warning('No combined results file found (batch_results.csv). Run the batch analysis first.')
else:
    tickers = sorted(df['ticker'].astype(str).unique())
    col1, col2 = st.columns([1,3])
    with col1:
        selected = st.selectbox('Select ticker', tickers)
        st.write('Signal:', df.loc[df['ticker']==selected, 'signal'].iloc[0])
        st.write('Current price:', df.loc[df['ticker']==selected, 'current_price'].iloc[0])
        if st.button('Download row as CSV'):
            row = df.loc[df['ticker']==selected]
            st.download_button('Download', row.to_csv(index=False), f"{selected}.csv")

    with col2:
        st.subheader('Combined Data (filtered)')
        st.dataframe(df[df['ticker']==selected].T)

    # Plot SMAs
    sym = load_symbol(selected)
    sma_cols = [c for c in df.columns if c in ['d20','d50','d100','d200']]
    values = df[df['ticker']==selected][sma_cols].melt(var_name='sma', value_name='value')
    if not values.empty:
        fig = px.bar(values, x='sma', y='value', title=f'SMAs for {selected}')
        st.plotly_chart(fig, use_container_width=True)

    # VPVR POC/VAH/VAL
    if 'daily_poc' in df.columns:
        poc = df.loc[df['ticker']==selected, 'daily_poc'].iloc[0]
        vah = df.loc[df['ticker']==selected, 'daily_vah'].iloc[0]
        val = df.loc[df['ticker']==selected, 'daily_val'].iloc[0]
        vp = pd.DataFrame({'level': ['VAL','POC','VAH'], 'price': [val, poc, vah]})
        fig2 = px.bar(vp, x='level', y='price', title=f'VPVR Levels ({selected})')
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader('Per-symbol detailed CSV (if available)')
    if not sym.empty:
        st.dataframe(sym)
        st.download_button('Download symbol CSV', sym.to_csv(index=False), f"{selected}-detail.csv")
    else:
        st.info('No per-symbol CSV found in ./results for this ticker.')

    st.sidebar.header('Summary')
    st.sidebar.write('Tickers analyzed:', len(tickers))
    signal_counts = df['signal'].value_counts().to_dict()
    st.sidebar.write(signal_counts)