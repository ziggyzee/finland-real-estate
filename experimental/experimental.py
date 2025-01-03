import streamlit as st
from datetime import datetime
from experimental.helpers import (
    process_postal_codes,
    call_api,
    build_where_clause,
    display_kde_plot,
    string_to_list,
)
import pandas as pd


def show_popup():
    st.markdown(
        """
        <div id="popup" style="display: block; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); 
        background-color: white; padding: 20px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); z-index: 1000;">
            <h2>Minimal Result Violation</h2>
            <p>
                Your search parameters yielded less than 4 property transactions.
                In order to see results, please widen your filters and try again 
            </p>
        </div>
        <div id="overlay" style="display: block; position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
        background-color: rgba(0, 0, 0, 0.5); z-index: 999;"></div>
        """,
        unsafe_allow_html=True
    )

def display_estimation(query_params):
    postal_codes_input_text = query_params.get('postal_code', [])

    current_year = datetime.now().year
    end_year = current_year + 2
    selected_start_year = query_params.get('start_year', 1880)
    selected_end_year = query_params.get('end_year', end_year)
    if (int(selected_end_year) - int(selected_start_year)) < 5:
        selected_start_year = str(int(selected_start_year) - 2)
        selected_end_year = str(int(selected_end_year) + 2)

    selected_min_square_meter = query_params.get('min_m2', 25)
    selected_max_square_meter = query_params.get('max_m2', 85)
    if (int(selected_max_square_meter) - int(selected_min_square_meter)) < 4:
        selected_min_square_meter = str(int(selected_min_square_meter) - 2)
        selected_max_square_meter = str(int(selected_max_square_meter) + 2)

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
        return st.markdown(
            f"""
                <h6 style='text-align: center; color: black;font-family: Arial, sans-serif; font-size: 20px; font-weight: bold;'> 
                Your search parameters yielded less than 4 property transactions.
                Please widen your filters in order to see results
                </h6>
                """,
            unsafe_allow_html=True,
        )
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

            return display_kde_plot(min_prices, max_prices, "top")

        else:
            show_popup()
