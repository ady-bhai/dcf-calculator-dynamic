import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="DCF Valuation Tool",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced styling with modern design elements
st.markdown("""
<style>
    /* Main container styling */
    .main {
        padding: 2rem;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f487e;
        margin-bottom: 1.5rem;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 10px;
    }
    
    /* Section headers */
    .section-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1f487e;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #dee2e6;
    }
    
    /* Metric containers */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1f487e;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1.1rem;
        color: #6c757d;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
    }
    
    /* Input fields */
    .stNumberInput {
        background: white;
        border-radius: 8px;
        padding: 0.5rem;
    }
    
    /* Charts */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 2rem 0;
    }
    
    /* Info cards */
    .info-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f487e;
        margin: 1rem 0;
    }
    
    /* Status messages */
    .status-success {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Alpha Vantage API settings
API_KEY = "YOUR_API_KEY"
BASE_URL = "https://www.alphavantage.co/query"

# Main header
st.markdown('<h1 class="main-header">💰 Discounted Cash Flow Valuation Tool</h1>', unsafe_allow_html=True)

# Sidebar with improved organization
with st.sidebar:
    st.markdown('<h2 style="color: #1f487e;">Input Parameters</h2>', unsafe_allow_html=True)
    
    # Company Information Section
    st.markdown('<div class="info-card">Company Information</div>', unsafe_allow_html=True)
    ticker = st.text_input("Stock Ticker Symbol:", value="AAPL", help="Enter the stock symbol (e.g., AAPL for Apple)")
    
    # Data Fetching Section
    if st.button("🔄 Fetch Financial Data", help="Retrieve latest financial data from Alpha Vantage"):
        with st.spinner("Fetching data..."):
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

                if "annualReports" in fcf_data:
                    annual_reports = fcf_data["annualReports"]
                    latest_fcf = int(annual_reports[0]["operatingCashflow"]) - int(annual_reports[0].get("capitalExpenditures", 0))
                    st.markdown(f'<div class="status-success">✅ Data fetched successfully for {ticker.upper()}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="status-error">❌ No data available for {ticker.upper()}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.markdown(f'<div class="status-error">❌ Error: {str(e)}</div>', unsafe_allow_html=True)

    # Financial Assumptions Section
    st.markdown('<div class="info-card">Financial Assumptions</div>', unsafe_allow_html=True)
    
    initial_cash_flow = st.number_input(
        "Initial Free Cash Flow ($M):",
        value=100.0,
        step=1.0,
        help="Latest annual free cash flow in millions"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        growth_rate = st.number_input(
            "Growth Rate (%)",
            value=5.0,
            step=0.1,
            help="Expected annual growth rate"
        )
    with col2:
        discount_rate = st.number_input(
            "Discount Rate (%)",
            value=10.0,
            step=0.1,
            help="Required rate of return"
        )
    
    # Forecast Parameters Section
    st.markdown('<div class="info-card">Forecast Parameters</div>', unsafe_allow_html=True)
    
    forecast_years = st.slider(
        "Forecast Period (Years)",
        min_value=5,
        max_value=20,
        value=10,
        step=1,
        help="Number of years to forecast"
    )
    
    terminal_growth_rate = st.number_input(
        "Terminal Growth Rate (%)",
        value=2.0,
        step=0.1,
        help="Long-term sustainable growth rate"
    )
    
    outstanding_shares = st.number_input(
        "Shares Outstanding (M)",
        value=1000.0,
        step=1.0,
        help="Total number of shares outstanding in millions"
    )

# DCF Calculation function (same as before)
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

    terminal_value = cash_flows[-1] * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)
    terminal_value_pv = terminal_value / (1 + discount_rate) ** forecast_years

    total_pv = sum(present_values) + terminal_value_pv
    return cash_flows, present_values, terminal_value, terminal_value_pv, total_pv

# Perform calculations
cash_flows, present_values, terminal_value, terminal_value_pv, total_pv = calculate_dcf(
    initial_cash_flow, growth_rate, discount_rate, forecast_years, terminal_growth_rate
)

# Calculate fair share value
fair_share_value = total_pv / outstanding_shares if outstanding_shares > 0 else None

# Results Display
st.markdown('<div class="section-header">Valuation Results</div>', unsafe_allow_html=True)

# Metrics Grid
st.markdown('<div class="metrics-grid">', unsafe_allow_html=True)

# Enterprise Value
st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">${total_pv:,.2f}M</div>
        <div class="metric-label">Enterprise Value</div>
    </div>
""", unsafe_allow_html=True)

# Terminal Value
st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">${terminal_value_pv:,.2f}M</div>
        <div class="metric-label">Terminal Value (PV)</div>
    </div>
""", unsafe_allow_html=True)

# Fair Share Value
if fair_share_value:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${fair_share_value:,.2f}</div>
            <div class="metric-label">Fair Share Value</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Enhanced Visualizations
st.markdown('<div class="section-header">Analysis & Visualizations</div>', unsafe_allow_html=True)

# Cash Flow Analysis Chart
with st.container():
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    fig = go.Figure()
    
    # Projected Cash Flows
    fig.add_trace(go.Bar(
        x=list(range(1, forecast_years + 1)),
        y=cash_flows,
        name="Projected Cash Flows",
        marker_color='#1f487e'
    ))
    
    # Present Values
    fig.add_trace(go.Bar(
        x=list(range(1, forecast_years + 1)),
        y=present_values,
        name="Present Value",
        marker_color='#4bb4de'
    ))
    
    fig.update_layout(
        title="Cash Flow Projection Analysis",
        xaxis_title="Forecast Year",
        yaxis_title="Value ($M)",
        barmode="group",
        template="plotly_white",
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sensitivity Analysis
with st.container():
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Create sensitivity matrix
    discount_rates = np.linspace(discount_rate - 5, discount_rate + 5, 10)
    growth_rates = np.linspace(growth_rate - 2, growth_rate + 2, 10)
    
    sensitivity = np.zeros((len(discount_rates), len(growth_rates)))
    for i, dr in enumerate(discount_rates):
        for j, gr in enumerate(growth_rates):
            _, _, _, _, pv = calculate_dcf(initial_cash_flow, gr, dr, forecast_years, terminal_growth_rate)
            sensitivity[i, j] = pv

    # Create heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(
        sensitivity,
        xticklabels=np.round(growth_rates, 2),
        yticklabels=np.round(discount_rates, 2),
        annot=True,
        fmt=".0f",
        cmap="viridis",
        ax=ax
    )
    
    plt.title("Enterprise Value Sensitivity Analysis ($M)")
    plt.xlabel("Growth Rate (%)")
    plt.ylabel("Discount Rate (%)")
    st.pyplot(fig)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer with timestamp
st.markdown(f"""
    <div style="text-align: center; color: #6c757d; padding: 2rem;">
        Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
""", unsafe_allow_html=True)
