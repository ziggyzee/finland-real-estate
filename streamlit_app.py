import streamlit as st
from datetime import datetime
from helpers import process_postal_codes, plot_normal_distribution, format_currency, call_api, build_where_clause

st.markdown("<h2 style='text-align: center;'>Find out how much a property is worth:</h2>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;'>Fill in the data on the property you are looking into, and click the button below</h5>", unsafe_allow_html=True)

call_api_and_plot = st.empty()

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)

st.markdown("<h5 style='text-align: center;'>Select postal codes:</h5>", unsafe_allow_html=True)
# Add a text input for postal codes
postal_codes_input_text = st.text_input("Enter postal codes separated by commas (e.g., 00740, 02320)")

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
# Calculate the current year and the year 2 years from now
current_year = datetime.now().year
end_year = current_year + 2

# Define the range of years
start_year = 1880
year_range = (start_year, end_year)

st.markdown("<h5 style='text-align: center;'>Select the built year range:</h5>", unsafe_allow_html=True)
# Add a select slider to choose a year range
selected_built_year_range = st.slider(
    "selected_built_year_range",
    min_value=start_year,
    max_value=end_year,
    value=(1975, current_year),
    step=1,
    label_visibility="hidden",
)

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;'>Select the square meters range:</h5>", unsafe_allow_html=True)
selected_square_meter_range = st.slider(
    "selected_square_meter_range",
    min_value=0,
    max_value=400,
    value=(25, 85),
    step=1,
    label_visibility="hidden",
)

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
# Define the list of cities
cities = [
    'espoo',
    'vantaa',
    'helsinki',
    'tampere',
    'jarvenpaa',
    'kerava',
    'jyvaskyla',
    'oulu',
    'kuopio',
    'joensuu',
    'turku',
    'kouvola',
    'lahti',
    'porvoo',
    'tuusula',
    'kauniainen'
]
st.markdown("<h5 style='text-align: center;'>Select city:</h5>", unsafe_allow_html=True)
# Add a multiselect widget to select cities
selected_cities = st.multiselect(
    "Select cities",
    options=cities,
    default=None,
    label_visibility="hidden"
)

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
# Add text above the checkboxes
st.markdown("<h5 style='text-align: center;'>Select the property ownership type:</h5>", unsafe_allow_html=True)

# Create columns for side-by-side checkboxes
col1, col2, col3 = st.columns(3)

# Add checkboxes in each column
with col1:
    own = st.checkbox("Own")
with col2:
    rented = st.checkbox("Rented (Leased)")
with col3:
    unknown = st.checkbox("Unknown")

# Display the selected options
selected_property_ownership_options = []
if own:
    selected_property_ownership_options.append("oma")
if rented:
    selected_property_ownership_options.append("vuokra")
if unknown:
    selected_property_ownership_options.append("unknown")

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
# Add text above the checkboxes
st.markdown("<h5 style='text-align: center;'>Select the number of rooms:</h5>", unsafe_allow_html=True)

# Create columns for side-by-side checkboxes
col1, col2, col3, col4 = st.columns(4)

# Add checkboxes in each column
with col1:
    one = st.checkbox("Studio (Yksiö)")
with col2:
    two = st.checkbox("2 (Kolmiot)")
with col3:
    three = st.checkbox("3 (Kaksiot)")
with col4:
    four = st.checkbox("4 or more")

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
st.markdown("<h5 style='text-align: center;'>Select the property type:</h5>", unsafe_allow_html=True)

# Create columns for side-by-side checkboxes
col1, col2, col3 = st.columns(3)

# Add checkboxes in each column
with col1:
    kerostalo = st.checkbox("Apartment Building (Kerostalo)")
with col2:
    rivitalo = st.checkbox("Row House (Rivitalo)")
with col3:
    omakotitalo = st.checkbox("Own Home (Omakotitalo)")

# Display the selected options
selected_property_type_options = []
if kerostalo:
    selected_property_type_options.append("kt")
if rivitalo:
    selected_property_type_options.append("rt")
if omakotitalo:
    selected_property_type_options.append("ok")

st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)
st.markdown("<h5 style='text-align: center;'>Select the property condition:</h5>", unsafe_allow_html=True)

# Create columns for side-by-side checkboxes
col1, col2, col3 = st.columns(3)

# Add checkboxes in each column
with col1:
    good = st.checkbox("Good")
with col2:
    ok = st.checkbox("Satisfying")
with col3:
    bad = st.checkbox("Passable")

# Display the selected options
selected_property_condition_options = []
if good:
    selected_property_condition_options.append("hyvä")
if ok:
    selected_property_condition_options.append("tyyd.")
if bad:
    selected_property_condition_options.append("huono")

# Container for the button and plot
with call_api_and_plot.container():
    # Add a button to trigger the API call
    if st.button("Get Price Valuation"):

        where_clause = build_where_clause(
            postal_codes_input_text,
            selected_built_year_range,
            selected_square_meter_range,
            selected_cities,
            selected_property_ownership_options,
            selected_room_number_options,
            selected_property_type_options,
            selected_property_condition_options,
            process_postal_codes
        )

        payload = {
            "where_clause": where_clause
        }

        response_data, error = call_api(payload)
        if error:
            st.error(f"API call failed: {error}")
        else:
            mean = response_data["mean"]
            std_dev = response_data["standard_deviation"]
            sample_size = response_data["sample_size"]
            plot_normal_distribution(mean, std_dev, sample_size)
            st.success("Data Retrieved Successfully! Here is the bottom line:")
            st.success(f"The most likely price for the property is {format_currency(mean)}")
            st.success(f"70% of properties like this would be priced between {format_currency(mean-std_dev)} and {format_currency(mean+std_dev)}")
            st.success(f"This price estimation is based on {sample_size} transactions from the last 2 years")
