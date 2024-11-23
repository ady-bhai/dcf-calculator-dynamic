import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Discounted Cash Flow Calculator",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Alpha Vantage API settings
API_KEY = "ALH36ZVG26EVQNYP"  # Replace with your Alpha Vantage API key
BASE_URL = "https://www.alphavantage.co/query"

# Styling for headers and sections
st.markdown("""
<style>
.section-header {
    font-size: 1.5rem;
    font-weight: bold;
    color: #2e86c1;
    margin-top: 20px;
    margin-bottom: 10px;
}
.metric-container {
    display: flex;
    justify-content: space-around;
    margin-top: 20px;
}
.metric-box {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}
.metric-value {
    font-size: 1.8rem;
    font-weight: bold;
    color: #2e86c1;
}
.metric-label {
    font-size: 1rem;
    color: #555;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for fetched data
if "initial_cash_flow" not in st.session_state:
    st.session_state["initial_cash_flow"] = 100.0
if "outstanding_shares" not in st.session_state:
    st.session_state["outstanding_shares"] = 1000.0
if "fetched" not in st.session_state:
    st.session_state["fetched"] = False

# Sidebar Inputs
with st.sidebar:
    st.title("📉 Discounted Cash Flow Calculator")
    st.write("Use the options below to customize or fetch financial data:")

    # Ticker Input
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT):", value="AAPL")

    # Fetch Data Button
    if st.button("Fetch Financial Data"):
        try:
            # Fetch free cash flow data
            fcf_response = requests.get(
                BASE_URL,
                params={
                    "function": "CASH_FLOW",
                    "symbol": ticker,
                    "apikey": API_KEY,
                }
            )
            fcf_data = fcf_response.json()

            # Fetch company overview
            overview_response = requests.get(
                BASE_URL,
                params={
                    "function": "OVERVIEW",
                    "symbol": ticker,
                    "apikey": API_KEY,
                }
            )
            overview_data = overview_response.json()

            # Extract financial data
            if "annualReports" in fcf_data:
                annual_reports = fcf_data["annualReports"]
                latest_fcf = int(annual_reports[0]["operatingCashflow"]) - int(annual_reports[0].get("capitalExpenditures", 0))
                st.session_state["initial_cash_flow"] = latest_fcf / 1e6  # Convert to millions
                st.success(f"Free Cash Flow fetched successfully for {ticker.upper()}!")
            else:
                st.error(f"Financial data for {ticker.upper()} is not available. Please enter manually.")

            # Extract outstanding shares
            outstanding_shares = float(overview_data.get("SharesOutstanding", 0)) / 1e6  # Convert to millions
            if outstanding_shares > 0:
                st.session_state["outstanding_shares"] = outstanding_shares
            else:
                st.error(f"Outstanding shares for {ticker.upper()} are unavailable. Please enter manually.")

            st.session_state["fetched"] = True

        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {e}")

    # Manual input fallback for all fields
    initial_cash_flow = st.number_input("Initial Cash Flow ($M):", value=st.session_state["initial_cash_flow"], step=1.0)
    growth_rate = st.number_input("Annual Growth Rate (%)", value=5.0, step=0.1)
    discount_rate = st.number_input("Discount Rate (%)", value=10.0, step=0.1)
    forecast_years = st.slider("Forecast Period (Years)", min_value=1, max_value=20, value=10, step=1)
    terminal_growth_rate = st.number_input("Terminal Growth Rate (%)", value=2.0, step=0.1)
    outstanding_shares = st.number_input("Outstanding Shares (in Millions):", value=st.session_state["outstanding_shares"], step=1.0)

# DCF Calculation
def calculate_dcf(initial_cash_flow, growth_rate, discount_rate, forecast_years, terminal_growth_rate):
    growth_rate /= 100
    discount_rate /= 100
    terminal_growth_rate /= 100

    cash_flows = []
    present_values = []
    for year in range(1, forecast_years + 1):
        cash_flow = initial_cash_flow * (1 + growth_rate) ** year
        present_value = cash_flow / (1 + discount_rate) ** year
        cash_flows.append(cash_flow)
        present_values.append(present_value)

    # Terminal Value Calculation
    terminal_value = cash_flows[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    terminal_value_pv = terminal_value / (1 + discount_rate) ** forecast_years

    total_pv = sum(present_values) + terminal_value_pv

    return cash_flows, present_values, terminal_value, terminal_value_pv, total_pv

# Use session state to persist fetched or manually input data
cash_flows, present_values, terminal_value, terminal_value_pv, total_pv = calculate_dcf(
    initial_cash_flow, growth_rate, discount_rate, forecast_years, terminal_growth_rate
)

# Calculate Fair Share Value
fair_share_value = None
if outstanding_shares > 0:
    fair_share_value = total_pv / outstanding_shares

# Display Results
st.markdown('<div class="section-header">DCF Results</div>', unsafe_allow_html=True)
st.metric(label="Enterprise Value", value=f"${total_pv:,.2f}M")
st.metric(label="Terminal Value (PV)", value=f"${terminal_value_pv:,.2f}M")
if fair_share_value:
    st.metric(label="Fair Share Value", value=f"${fair_share_value:,.2f}")

# Visualization: Cash Flows and Present Values
st.markdown('<div class="section-header">Cash Flow Analysis</div>', unsafe_allow_html=True)
fig = go.Figure()
fig.add_trace(go.Bar(x=list(range(1, forecast_years + 1)), y=cash_flows, name="Projected Cash Flows"))
fig.add_trace(go.Bar(x=list(range(1, forecast_years + 1)), y=present_values, name="Present Value of Cash Flows"))
fig.update_layout(
    title="Projected and Present Values of Cash Flows",
    xaxis_title="Year",
    yaxis_title="Value ($M)",
    barmode="group"
)
st.plotly_chart(fig)
