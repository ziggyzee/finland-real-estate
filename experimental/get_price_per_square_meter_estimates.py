import streamlit as st
from datetime import datetime
from experimental.helpers import (
    process_postal_codes,
    format_currency,
    call_api,
    build_where_clause,
    display_kde_plot,
    string_to_list,
)
import pandas as pd


def render_experimental_tab():
    query_params = st.query_params.to_dict()

    # Initialize session state for plots
    if 'plots' not in st.session_state:
        st.session_state.plots = None

    # Create placeholders for the charts
    top_plot_placeholder = st.empty()
    top_text_placeholder = st.empty()

    postal_codes_input_text = query_params.get('postal_code', [])

    current_year = datetime.now().year
    end_year = current_year + 2
    selected_start_year = query_params.get('start_year', 1880)
    selected_end_year = query_params.get('end_year', end_year)

    selected_min_square_meter = query_params.get('min_m2', 25)
    selected_max_square_meter = query_params.get('max_m2', 85)

    selected_cities = string_to_list(query_params.get('cities', None))

    selected_property_ownership_options = string_to_list(query_params.get('ownership_types', None))

    selected_room_number_input = string_to_list(query_params.get('room_numbers', None))

    # Display the selected options
    selected_room_number_options = []
    if '1' in selected_room_number_input:
        selected_room_number_options.extend(["Yksiö", "Yksiöt"])
    if '2' in selected_room_number_input:
        selected_room_number_options.extend(["Kaksiot", "Kaksi huonetta"])
    if '3' in selected_room_number_input:
        selected_room_number_options.extend(["Kolmiot", "Kolme huonetta"])
    if '4' in selected_room_number_input:
        selected_room_number_options.append("Neljä huonetta tai enemmän")

    selected_property_type_options = string_to_list(query_params.get('prop_type', None))

    selected_room_number_input = string_to_list(query_params.get('condition', None))
    selected_property_condition_options = []
    if "good" in selected_room_number_input:
        selected_property_condition_options.append("hyvä")
    if "ok" in selected_room_number_input:
        selected_property_condition_options.append("tyyd.")
    if "bad" in selected_room_number_input:
        selected_property_condition_options.append("huono")


    where_clause = build_where_clause(
        postal_codes_input_text,
        [selected_start_year, selected_end_year],
        [selected_min_square_meter, selected_max_square_meter],
        selected_cities,
        selected_property_ownership_options,
        selected_room_number_options,
        selected_property_type_options,
        selected_property_condition_options,
        process_postal_codes,
    )

    payload = {"where_clause": where_clause}

    response_data, error = call_api(payload)
    if error:
        st.error(f"API call failed: {error}")
    else:
        avg_prices_per_square_meter = [
            (min_price + max_price) / 2
            for min_price, max_price in zip(
                response_data["min_prices_per_square_meter"],
                response_data["max_prices_per_square_meter"],
            )
        ]
        transactions = response_data["transactions"]
        sample_size = sum(transactions)
        if sample_size > 4:
            mean_value = pd.Series(avg_prices_per_square_meter).mean()
            median_value = pd.Series(avg_prices_per_square_meter).median()
            q25_value = pd.Series(avg_prices_per_square_meter).quantile(0.25)
            q75_value = pd.Series(avg_prices_per_square_meter).quantile(0.75)
            min_value = min(avg_prices_per_square_meter)
            max_value = max(avg_prices_per_square_meter)
            min_prices = response_data["min_prices_per_square_meter"]
            max_prices = response_data["max_prices_per_square_meter"]
            st.session_state.plots = {
                "min_prices": min_prices,
                "max_prices": max_prices,
                "mean_value": mean_value,
                "median_value": median_value,
                "q25_value": q25_value,
                "q75_value": q75_value,
                "min_value": min_value,
                "max_value": max_value,
                "sample_size": sample_size,
            }
        else:
            st.session_state.plots = None
            st.markdown(
                f"""
                <h6 style='text-align: left; color: red;'> 
                Your search parameters yielded less than 4 property transactions.
                Please widen your filters in order to see results
                </h6>
                """,
                unsafe_allow_html=True,
            )

    # Display the plots if they exist in session state
    if st.session_state.plots:
        min_prices = st.session_state.plots["min_prices"]
        max_prices = st.session_state.plots["max_prices"]
        mean_value = st.session_state.plots["mean_value"]
        median_value = st.session_state.plots["median_value"]
        q25_value = st.session_state.plots["q25_value"]
        q75_value = st.session_state.plots["q75_value"]
        min_value = st.session_state.plots["min_value"]
        max_value = st.session_state.plots["max_value"]
        sample_size = st.session_state.plots["sample_size"]

        # Display the plot at the top
        with top_plot_placeholder:
            if sample_size > 4:
                display_kde_plot(min_prices, max_prices, "top")

            with top_text_placeholder:
                st.markdown(
                    f"""
                    <h6 style='text-align: left; color: red;'>Average square meter price: {format_currency(mean_value)} <br>
                    <span style='color: blue;'>Median square meter price: {format_currency(median_value)}</span> <br> 
                    <span style='color: green;'>50% of the relevant properties have a square meter price between {format_currency(q25_value)}
                    and {format_currency(q75_value)} (25-75 percentiles)</span> <br>
                    <span style='color: Purple;'>The lowest price per square meter is {format_currency(min_value)}
                    and the highest is {format_currency(max_value)}</span> <br>
                    <span style='color: grey;'>The plot and metrics are based on {sample_size} relevant property transactions</span> <br>
                    </h6>
                    """,
                    unsafe_allow_html=True,
                )

    else:
        with top_text_placeholder:
            st.markdown(
                f"""
                <h6 style='text-align: left; color: red;'> 
                Your search parameters yielded less than 4 property transactions.
                Please widen your filters in order to see results
                </h6>
                """,
                unsafe_allow_html=True,
            )
