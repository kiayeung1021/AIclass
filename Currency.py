import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# Frankfurter is a free, open-source API (No key required!)
BASE_URL = "https://api.frankfurter.app"
POPULAR_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "HKD", "NZD"]

st.set_page_config(page_title="Currency Tracker", page_icon="📈", layout="wide")

# --- FUNCTIONS ---
def get_latest_rate(base, target):
    """Fetches the current exchange rate from the free API."""
    try:
        url = f"{BASE_URL}/latest?from={base}&to={target}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['rates'][target]
    except Exception as e:
        return None

def get_historical_data(base, target, days=30):
    """Fetches real historical trend data for the last 30 days."""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    try:
        url = f"{BASE_URL}/{start_date}..{end_date}?from={base}&to={target}"
        response = requests.get(url)
        if response.status_code == 200:
            rates = response.json()['rates']
            # Convert the dictionary to a DataFrame for plotting
            df = pd.DataFrame.from_dict(rates, orient='index').reset_index()
            df.columns = ['Date', 'Rate']
            df['Date'] = pd.to_datetime(df['Date'])
            return df.sort_values("Date")
    except Exception:
        return pd.DataFrame()

# --- STREAMLIT UI ---
st.title("💱 Free Currency Converter & Analyzer")
st.info("Using real-time data from the Frankfurter Open API (No Key Needed).")

# Sidebar for inputs
st.sidebar.header("Settings")
from_curr = st.sidebar.selectbox("Base Currency", POPULAR_CURRENCIES, index=0)
to_curr = st.sidebar.selectbox("Target Currency", POPULAR_CURRENCIES, index=1)
amount = st.sidebar.number_input("Amount to Convert", min_value=1.0, value=100.0)

if from_curr == to_curr:
    st.error("Please select two different currencies to see a conversion.")
else:
    # Action Button
    if st.sidebar.button("Update Data"):
        with st.spinner("Fetching market rates..."):
            current_rate = get_latest_rate(from_curr, to_curr)
            df_trend = get_historical_data(from_curr, to_curr)

            if current_rate:
                # Layout for metrics
                total_converted = amount * current_rate
                
                col1, col2 = st.columns(2)
                col1.metric(f"Total in {to_curr}", f"{total_converted:,.2f}")
                col2.metric(f"Exchange Rate", f"1 {from_curr} = {current_rate:.4f} {to_curr}")

                st.divider()

                # Trend Graph
                if not df_trend.empty:
                    st.subheader(f"📊 {from_curr} to {to_curr} Trend (Last 30 Days)")
                    fig = px.line(df_trend, x="Date", y="Rate", 
                                  labels={"Rate": f"Value of 1 {from_curr}"},
                                  title=f"Market fluctuations for {from_curr}/{to_curr}")
                    fig.update_traces(line_color='#00CC96')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Historical data currently unavailable.")
            else:
                st.error("Could not connect to the API. Please try again later.")