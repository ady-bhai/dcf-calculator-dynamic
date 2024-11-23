import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Discounted Cash Flow Calculator",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Inputs
with st.sidebar:
    st.title("📉 Discounted Cash Flow Calculator")
    st.write("Customize your parameters or fetch data:")

    # Ticker Input
    ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT):", value="AAPL")

    # Fetch Data Button
    if st.button("Fetch Financial Data"):
        try:
            stock = yf.Ticker(ticker)

            # Extract Financial Data
            financials = stock.financials.T
            cashflow = stock.cashflow.T
            info = stock.info

            # Extract Key Metrics
            revenue = financials["Total Revenue"].iloc[-1]
            operating_cash_flow = cashflow["Total Cash From Operating Activities"].iloc[-1]
            capex = abs(cashflow["Capital Expenditures"].iloc[-1])  # Make positive
            fcf = operating_cash_flow - capex  # Free Cash Flow

            # Set Default Inputs
            initial_cash_flow = fcf / 1e6  # Convert to millions
            growth_rate = 5.0
            discount_rate = 10.0
            forecast_years = 10
            terminal_growth_rate = 2.0

            st.success(f"Data fetched successfully for {ticker.upper()}!")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            initial_cash_flow = 100.0
    else:
        # Default Inputs (if no data fetched)
        initial_cash_flow = st.number_input("Initial Cash Flow ($M)", value=100.0, step=1.0)
        growth_rate = st.number_input("Annual Growth Rate (%)", value=5.0, step=0.1)
        discount_rate = st.number_input("Discount Rate (%)", value=10.0, step=0.1)
        forecast_years = st.slider("Forecast Period (Years)", min_value=1, max_value=20, value=10, step=1)
        terminal_growth_rate = st.number_input("Terminal Growth Rate (%)", value=2.0, step=0.1)

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

# Perform DCF Calculations
cash_flows, present_values, terminal_value, terminal_value_pv, total_pv = calculate_dcf(
    initial_cash_flow, growth_rate, discount_rate, forecast_years, terminal_growth_rate
)

# Results Display
st.subheader("Results")
st.metric(label="Total Present Value (Enterprise Value)", value=f"${total_pv:,.2f}M")
st.metric(label="Terminal Value (PV)", value=f"${terminal_value_pv:,.2f}M")

# Visualization: Cash Flows and Present Values
st.subheader("Cash Flow Analysis")
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

# Heatmap Visualization for Sensitivity Analysis
st.subheader("Sensitivity Analysis")
discount_rates = np.linspace(discount_rate - 5, discount_rate + 5, 10)
growth_rates = np.linspace(growth_rate - 2, growth_rate + 2, 10)

sensitivity = np.zeros((len(discount_rates), len(growth_rates)))
for i, dr in enumerate(discount_rates):
    for j, gr in enumerate(growth_rates):
        _, _, _, _, pv = calculate_dcf(initial_cash_flow, gr, dr, forecast_years, terminal_growth_rate)
        sensitivity[i, j] = pv

fig, ax = plt.subplots(figsize=(10, 8))
sns.heatmap(sensitivity, xticklabels=np.round(growth_rates, 2), yticklabels=np.round(discount_rates, 2),
            annot=True, fmt=".2f", cmap="viridis", ax=ax)
ax.set_title("Sensitivity Analysis: Total PV by Growth and Discount Rates")
ax.set_xlabel("Growth Rate (%)")
ax.set_ylabel("Discount Rate (%)")
st.pyplot(fig)
