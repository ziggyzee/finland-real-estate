import streamlit as st
from datetime import datetime
from estimate_square_meter_price.helpers import (
    process_postal_codes,
    format_currency,
    call_api,
    build_where_clause,
    generate_key,
    display_kde_plot,
)
import pandas as pd


def render_price_per_square_meter_estimations_tab():
    st.markdown(
        "<h2 style='text-align: center;'>Price per Square Meter Estimation</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h5 style='text-align: center;'>Filter the property transactions to run the estimation on relevant transactions</h5>",
        unsafe_allow_html=True,
    )

    # Initialize session state for plots
    if 'plots' not in st.session_state:
        st.session_state.plots = None

    # Create placeholders for the charts
    top_plot_placeholder = st.empty()
    top_text_placeholder = st.empty()

    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

    # Add the button at the top of the page
    top_button_clicked = st.button("Get Estimates", key=generate_key("top_button"))

    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

    st.markdown(
        "<h5 style='text-align: center;'>Select postal codes:</h5>",
        unsafe_allow_html=True,
    )
    # Add a text input for postal codes
    postal_codes_input_text = st.text_input(
        "Enter postal codes separated by commas (e.g., 00740, 02320)",
        key=generate_key("postal_codes_input_text"),
    )

    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

    st.markdown(
        "<h5 style='text-align: center;'>Select the built year range:</h5>",
        unsafe_allow_html=True,
    )
    # Calculate the current year and the year 2 years from now
    current_year = datetime.now().year
    end_year = current_year + 2

    # Create two columns
    col1, col2 = st.columns(2)

    # Place the number inputs in the columns
    with col1:
        selected_start_year = st.number_input("Select the starting year built", value=1965, min_value=1880,
                                              max_value=end_year, key=generate_key("selected_start_year"))

    with col2:
        selected_end_year = st.number_input("Select the ending year built", value=1985, min_value=1880,
                                            max_value=end_year, key=generate_key("selected_end_year"))

    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
    st.markdown(
        "<h5 style='text-align: center;'>Select the square meters range:</h5>",
        unsafe_allow_html=True,
    )

    # Create two columns
    col1, col2 = st.columns(2)

    # Place the number inputs in the columns
    with col1:
        selected_min_square_meter = st.number_input("Select the minimum square meters", value=25, min_value=0,
                                              max_value=400, key=generate_key("selected_min_square_meter"))

    with col2:
        selected_max_square_meter = st.number_input("Select the maximum square meters", value=85, min_value=0,
                                                    max_value=400, key=generate_key("selected_max_square_meter"))


    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
    # Define the list of cities
    cities = [
        "espoo",
        "vantaa",
        "helsinki",
        "tampere",
        "jarvenpaa",
        "kerava",
        "jyvaskyla",
        "oulu",
        "kuopio",
        "joensuu",
        "turku",
        "kouvola",
        "lahti",
        "porvoo",
        "tuusula",
        "kauniainen",
    ]
    st.markdown(
        "<h5 style='text-align: center;'>Select city:</h5>", unsafe_allow_html=True
    )
    # Add a multiselect widget to select cities
    selected_cities = st.multiselect(
        "Select cities",
        options=cities,
        default=None,
        label_visibility="hidden",
        key=generate_key("selected_cities"),
    )

    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
    # Add text above the checkboxes
    st.markdown(
        "<h5 style='text-align: center;'>Select the property ownership type:</h5>",
        unsafe_allow_html=True,
    )

    # Create columns for side-by-side checkboxes
    col1, col2 = st.columns(2)

    # Add checkboxes in each column
    with col1:
        own = st.checkbox(
            "Own",
            key=generate_key("Own"),
        )
    with col2:
        rented = st.checkbox(
            "Rented (Leased)",
            key=generate_key("rented"),
        )

    # Display the selected options
    selected_property_ownership_options = []
    if own:
        selected_property_ownership_options.append("oma")
    if rented:
        selected_property_ownership_options.append("vuokra")

    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
    # Add text above the checkboxes
    st.markdown(
        "<h5 style='text-align: center;'>Select the number of rooms:</h5>",
        unsafe_allow_html=True,
    )

    # Create columns for side-by-side checkboxes
    col1, col2, col3, col4 = st.columns(4)

    # Add checkboxes in each column
    with col1:
        one = st.checkbox(
            "Studio (Yksiö)",
            key=generate_key("Studio"),
        )
    with col2:
        two = st.checkbox(
            "2 (Kaksiot)",
            key=generate_key("Kaksiot"),
        )
    with col3:
        three = st.checkbox(
            "3 (Kolmiot)",
            key=generate_key("Kolmiot"),
        )
    with col4:
        four = st.checkbox(
            "4 or more",
            key=generate_key("4-or-more"),
        )

    # Display the selected options
    selected_room_number_options = []
    if one:
        selected_room_number_options.extend(["Yksiö", "Yksiöt"])
    if two:
        selected_room_number_options.extend(["Kaksiot", "Kaksi huonetta"])
    if three:
        selected_room_number_options.extend(["Kolmiot", "Kolme huonetta"])
    if four:
        selected_room_number_options.append("Neljä huonetta tai enemmän")

    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
    st.markdown(
        "<h5 style='text-align: center;'>Select the property type:</h5>",
        unsafe_allow_html=True,
    )

    # Create columns for side-by-side checkboxes
    col1, col2, col3 = st.columns(3)

    # Add checkboxes in each column
    with col1:
        kerostalo = st.checkbox(
            "Apartment Building (Kerostalo)",
            key=generate_key("Kerostalo"),
        )
    with col2:
        rivitalo = st.checkbox(
            "Row House (Rivitalo)",
            key=generate_key("Rivitalo"),
        )
    with col3:
        omakotitalo = st.checkbox(
            "Own Home (Omakotitalo)",
            key=generate_key("Omakotitalo"),
        )

    # Display the selected options
    selected_property_type_options = []
    if kerostalo:
        selected_property_type_options.append("kt")
    if rivitalo:
        selected_property_type_options.append("rt")
    if omakotitalo:
        selected_property_type_options.append("ok")

    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
    st.markdown(
        "<h5 style='text-align: center;'>Select the property condition:</h5>",
        unsafe_allow_html=True,
    )

    # Create columns for side-by-side checkboxes
    col1, col2, col3 = st.columns(3)

    # Add checkboxes in each column
    with col1:
        good = st.checkbox(
            "Good",
            key=generate_key("state-Good"),
        )
    with col2:
        ok = st.checkbox(
            "Satisfying",
            key=generate_key("state-Satisfying"),
        )
    with col3:
        bad = st.checkbox(
            "Passable",
            key=generate_key("state-Passable"),
        )

    # Display the selected options
    selected_property_condition_options = []
    if good:
        selected_property_condition_options.append("hyvä")
    if ok:
        selected_property_condition_options.append("tyyd.")
    if bad:
        selected_property_condition_options.append("huono")

    st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

    # Add the button at the bottom of the page
    bottom_button_clicked = st.button("Get Estimates", key=generate_key("bottom_button"))

    # Check if either button was clicked
    if top_button_clicked or bottom_button_clicked:
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
                    <span style='color: black;'>The plot and metrics are based on {sample_size} relevant property transactions</span> <br>
                    </h6>
                    """,
                    unsafe_allow_html=True,
                )

            if sample_size > 4:
                # Display the plot at the bottom
                display_kde_plot(min_prices, max_prices, "bottom")
                st.markdown(
                    f"""
                    <h6 style='text-align: left; color: red;'>Average square meter price: {format_currency(mean_value)} <br>
                    <span style='color: blue;'>Median square meter price: {format_currency(median_value)}</span> <br> 
                    <span style='color: green;'>50% of the relevant properties have a square meter price between {format_currency(q25_value)}
                    and {format_currency(q75_value)} (25-75 percentiles)</span> <br>
                    <span style='color: Purple;'>The lowest price per square meter is {format_currency(min_value)}
                    and the highest is {format_currency(max_value)}</span> <br>
                    <span style='color: black;'>The plot and metrics are based on {sample_size} relevant property transactions</span> <br>
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
