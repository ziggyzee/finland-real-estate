import streamlit as st
import requests
from typing import List
import pandas as pd
import plotly.figure_factory as ff

def generate_key(unique_str: str):
    return str(f"get-transactions-{unique_str}")

def build_where_clause(
    postal_codes_input_text,
    selected_built_year_range,
    selected_square_meter_range,
    selected_cities,
    selected_property_ownership_options,
    selected_room_number_options,
    selected_property_type_options,
    selected_property_condition_options,
    process_postal_codes
):
    where_clause = []

    # Process the input and validate it
    if postal_codes_input_text:
        postal_codes, error = process_postal_codes(postal_codes_input_text)
        if error:
            st.error(error)
        else:
            postal_code_sql = "postal_code in ({})".format(", ".join("'{}'".format(postal_code) for postal_code in postal_codes))
            where_clause.append(postal_code_sql)

    built_year_range_sql = [f"year_built >= {selected_built_year_range[0]}", f"year_built <= {selected_built_year_range[1]}"]
    square_meter_range_sql = [f"square_meters >= {selected_square_meter_range[0]}", f"square_meters <= {selected_square_meter_range[1]}"]
    where_clause.extend(built_year_range_sql)
    where_clause.extend(square_meter_range_sql)

    if selected_cities:
        selected_cities_sql = "city in ({})".format(", ".join("'{}'".format(city) for city in selected_cities))
        where_clause.append(selected_cities_sql)

    if selected_property_ownership_options:
        property_ownership_sql = "plot_ownership in ({})".format(", ".join("'{}'".format(ownership_type) for ownership_type in selected_property_ownership_options))
        where_clause.append(property_ownership_sql)

    if selected_room_number_options:
        room_number_sql = "room_category in ({})".format(", ".join("'{}'".format(room_number) for room_number in selected_room_number_options))
        where_clause.append(room_number_sql)

    if selected_property_type_options:
        building_type_sql = "building_type in ({})".format(", ".join("'{}'".format(building_type) for building_type in selected_property_type_options))
        where_clause.append(building_type_sql)

    if selected_property_condition_options:
        property_condition_sql = "state in ({})".format(", ".join("'{}'".format(state) for state in selected_property_condition_options))
        where_clause.append(property_condition_sql)

    return where_clause


api_url = "http://51.20.64.222:8000/get-price-per-square-meters/"

# Function to call the API
def call_api(payload):
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)


def process_postal_codes(input_text):
    # Split the input text by commas
    postal_codes = [code.strip() for code in input_text.split(",")]

    # Validate each postal code
    for code in postal_codes:
        if not code.isdigit() or len(code) != 5:
            return None, f"Invalid postal code: {code}"

    return postal_codes, None


def format_currency(value):
    # Convert the value to thousands and round it
    value_in_thousands = round((value / 1000), 1)

    # Format the value as a string with the currency symbol
    formatted_value = f"€{value_in_thousands}k"

    return formatted_value


def display_kde_plot(min_prices_per_square_meter: List[float], max_prices_per_square_meter: List[float], key: str):
    # Calculate the average price per square meter for each transaction
    avg_prices_per_square_meter = [
        (min_price + max_price) / 2
        for min_price, max_price in zip(min_prices_per_square_meter, max_prices_per_square_meter)
    ]

    # Calculate statistics
    mean_value = pd.Series(avg_prices_per_square_meter).mean()
    median_value = pd.Series(avg_prices_per_square_meter).median()
    q25_value = pd.Series(avg_prices_per_square_meter).quantile(0.25)
    q75_value = pd.Series(avg_prices_per_square_meter).quantile(0.75)
    min_value = min(avg_prices_per_square_meter)
    max_value = max(avg_prices_per_square_meter)

    # Create the KDE plot
    fig = ff.create_distplot([avg_prices_per_square_meter], group_labels=['Average Price per Square Meter'], show_hist=False, show_rug=False)

    # Convert density to percentage points and set custom hover text
    for trace in fig.data:
        trace.y = trace.y * 100
        trace.hovertemplate = 'Price per square meter: %{x:,.0f}<extra></extra>'


    # Add vertical lines for the statistics
    for value, label, color, spacing in zip(
        [mean_value, median_value, q25_value, q75_value, min_value, max_value],
        ['Mean', 'Median', 'Q25', 'Q75', 'Min', 'Max'],
        ['Red', 'Blue', 'Green', 'Green', 'Purple', 'Purple'],
        [1, 0.9, 0.1, 0.1, 0.4, 0.4]
    ):
        fig.add_shape(
            type="line",
            x0=value,
            y0=0,
            x1=value,
            y1=1,
            xref='x',
            yref='paper',
            line=dict(color=color, width=2, dash="dash"),
        )

    # Find the maximum y value of the KDE plot
    max_y_value = max(y for trace in fig.data for y in trace.y)

    # Customize the layout
    fig.update_layout(
        title='KDE Plot of Prices per Square Meter',
        xaxis_title='Price per Square Meter',
        yaxis_title='Density (%)',
        yaxis=dict(range=[0, max_y_value * 1.1]),  # Set y-axis range slightly larger than the max y value
        xaxis=dict(
            tickmode='linear',
            tick0=0,
            dtick=500  # Set tick interval to 500 euros
        ),
        showlegend=False,
    )

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray', tickmode='linear', tick0=0, dtick=500)
    # Display the chart in Streamlit
    st.plotly_chart(fig, key=key)
