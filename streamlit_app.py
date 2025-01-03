import streamlit as st
from experimental.experimental import display_estimation

# Set the page layout to wide
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    /* Target the specific element */
    #root > div:nth-child(1) > div.withScreencast > div > div > section > div.stMainBlockContainer.block-container.st-emotion-cache-1ibsh2c.ekr3hml4 {
        padding: 1rem !important;  /* Set minimal padding */
        height: 100vh;  /* Set height to full viewport height */
        box-sizing: border-box;  /* Ensure padding and border are included in the element's total width and height */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Get the query parameters
query_params = st.query_params.to_dict()

# Create placeholders for the charts
top_plot_placeholder = st.empty()

# Check if the 'page' parameter is set to 'estimation'
if query_params.get('page') == 'estimation':
    # Import and run the estimation page
    top_plot_placeholder = display_estimation(query_params)

else:
    # Default content for the main page
    st.title("Welcome to the Real Estate App")
    st.write("Use the navigation to go to different pages.")
    if st.button("Go to Estimation Page"):
        query_params['page'] = 'estimation'
        top_plot_placeholder = display_estimation(query_params)
