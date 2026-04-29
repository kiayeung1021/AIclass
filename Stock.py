import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import date, timedelta
import pandas as pd

# Page Config
st.set_page_config(page_title="Stock Analyzer 2026", layout="wide")

## --- SIDEBAR SETTINGS ---
st.sidebar.header("User Input")

# Top 10 most popular stocks
popular_stocks = {
    "AAPL - Apple Inc.": "AAPL",
    "MSFT - Microsoft Corporation": "MSFT",
    "GOOGL - Alphabet Inc.": "GOOGL",
    "AMZN - Amazon.com Inc.": "AMZN",
    "TSLA - Tesla Inc.": "TSLA",
    "NVDA - NVIDIA Corporation": "NVDA",
    "META - Meta Platforms Inc.": "META",
    "NFLX - Netflix Inc.": "NFLX",
    "AMD - Advanced Micro Devices": "AMD",
    "INTC - Intel Corporation": "INTC",
    "Custom - Enter manually": "CUSTOM"
}

selected_stock = st.sidebar.selectbox("Select Stock", list(popular_stocks.keys()))

if popular_stocks[selected_stock] == "CUSTOM":
    ticker_symbol = st.sidebar.text_input("Enter Stock Ticker", value="AAPL").upper()
else:
    ticker_symbol = popular_stocks[selected_stock]

# Time Period Selection
st.sidebar.markdown("---")
st.sidebar.subheader("Time Period")

# Define time periods
time_periods = {
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365,
    "5Y": 1825,
    "MAX": None
}

# Use radio buttons for time period selection
selected_period = st.sidebar.radio("Select Period", list(time_periods.keys()), horizontal=True)

# Calculate dates based on selected period
if time_periods[selected_period] is not None:
    end_date = date.today()
    start_date = end_date - timedelta(days=time_periods[selected_period])
else:
    # MAX - use a very early start date
    end_date = date.today()
    start_date = date(2000, 1, 1)

# Allow manual override with date inputs
st.sidebar.markdown("---")
use_custom_dates = st.sidebar.checkbox("Use Custom Date Range")

if use_custom_dates:
    start_date = st.sidebar.date_input("Start Date", value=start_date)
    end_date = st.sidebar.date_input("End Date", value=end_date)

## --- DATA FETCHING ---
@st.cache_data
def load_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data

data = load_data(ticker_symbol, start_date, end_date)

## --- MAIN DASHBOARD ---
st.title(f"📈 {ticker_symbol} Stock Analysis")
st.caption(f"Time Period: {selected_period} | {start_date} to {end_date}")

if not data.empty:
    # 1. Metric Row
    last_close = data['Close'].iloc[-1].values[0]
    prev_close = data['Close'].iloc[-2].values[0]
    change = last_close - prev_close
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Current Price", f"${last_close:,.2f}", f"{change:,.2f}")
    col2.metric("High (Period)", f"${data['High'].max().values[0]:,.2f}")
    col3.metric("Low (Period)", f"${data['Low'].min().values[0]:,.2f}")

    # 2. Candlestick Chart
    st.subheader("Interactive Price Chart")
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'].iloc[:,0],
        high=data['High'].iloc[:,0],
        low=data['Low'].iloc[:,0],
        close=data['Close'].iloc[:,0],
        name="Candlestick"
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # 3. Stock Comparison Table
    st.subheader("Stock Comparison")
    
    # Get the list of other stocks to compare (excluding current selection and CUSTOM)
    other_stocks = {k: v for k, v in popular_stocks.items() 
                    if v != ticker_symbol and v != "CUSTOM"}
    
    comparison_data = []
    
    for stock_name, stock_ticker in other_stocks.items():
        try:
            stock_data = yf.download(stock_ticker, start=start_date, end=end_date, progress=False)
            if not stock_data.empty:
                # Get first and last close prices for the period
                first_close = stock_data['Close'].iloc[0].values[0]
                last_close = stock_data['Close'].iloc[-1].values[0]
                price_change = last_close - first_close
                change_percent = (price_change / first_close) * 100
                
                comparison_data.append({
                    'Stock': stock_ticker,
                    'Name': stock_name.split(' - ')[0],
                    'Current Price': f"${last_close:,.2f}",
                    'Period Change': f"${price_change:,.2f}",
                    'Change %': f"{change_percent:+.2f}%"
                })
        except:
            continue
    
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data)
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    else:
        st.info("Could not load comparison data for other stocks.")
else:
    st.error("Invalid Ticker or No Data Found. Please try again.")