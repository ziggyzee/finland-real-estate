import streamlit as st
import plotly.graph_objs as go
import numpy as np
import requests


def generate_key(unique_str: str):
    return str(f"property-valuation-{unique_str}")


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


api_url = "http://51.20.64.222:8000/property-price-valuation/"

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
    value_in_thousands = round(value / 1000)

    # Format the value as a string with the currency symbol
    formatted_value = f"€{value_in_thousands}k"

    return formatted_value


def plot_normal_distribution(mean, std_dev, sample_size):
    # Generate data for the normal distribution
    x = np.linspace(mean - 3 * std_dev, mean + 3 * std_dev, 1000)
    y = (1 / (std_dev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mean) / std_dev) ** 2)
    y_scaled = y / y.max() * 0.5

    # Create the plotly figure
    fig = go.Figure()

    hover_text = [f'The price of {format_currency(val)} has a likelihood of {prob:.0%}' for val, prob in zip(x, y_scaled)]

    # Add the normal distribution curve
    fig.add_trace(go.Scatter(
        x=x,
        y=y_scaled,
        mode='lines',
        name='',
        fill='tozeroy',
        hovertemplate='%{text}<extra></extra>',
        text=hover_text,
    ))

    # Update the layout
    fig.update_layout(
        title=f'Estimated Price Distribution, based on {sample_size} transactions within the last 2 years',
        xaxis_title='Price',
        xaxis=dict(
            tickprefix='€',  # Add the € symbol as a prefix to the tick labels
            tickformat=',.0f'  # Format the tick labels as integers with thousands separators
        ),
        yaxis_title='Probability Density',
        yaxis=dict(
            tickformat='.0%',  # Format y-axis ticks as percentages
            range=[0, 0.5]  # Ensure the y-axis range is from 0 to 0.5
        ),
        hoverlabel = dict(
            font_size=16,  # Set the font size for hover text
            font_family="Arial"
        ),
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig)