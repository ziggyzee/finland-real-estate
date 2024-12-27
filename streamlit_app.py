import streamlit as st
from property_valuation.property_valuation_tab import render_property_valuation_tab
from estimate_square_meter_price.get_price_per_square_meter_estimates import render_price_per_square_meter_estimations_tab

# Create tabs
price_per_square_meter_estimations_tab, property_valuation_tab = st.tabs(["Price per Square Meter Estimation", "Property Valuation"])

with price_per_square_meter_estimations_tab:
    render_price_per_square_meter_estimations_tab()

with property_valuation_tab:
    render_property_valuation_tab()
