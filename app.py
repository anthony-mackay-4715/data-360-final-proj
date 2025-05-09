import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

#Set the page configuration
st.set_page_config(page_title="Luxury Watches", layout="wide")

#Create a title and subheader
st.title('Luxury Watches For Sale Online')
st.write("This app displays watches listed on [Bob's Watches](https://www.bobswatches.com/) as well as pricing visualizations." )

#Read in the data
# Ensure the path is correct relative to where you run streamlit
try:
    data = pd.read_csv('final_watches.csv')
    data = data[data['Price ($)'] != 'Not listed']
    data['Price ($)'] = data['Price ($)'].astype(float)
    filter_cols = ['Manufacturer', 'Model', 'Metal', 'Year']
    for col in filter_cols:
        if col in data.columns:
            data[col].fillna('N/A', inplace=True)
            # Ensure consistent data types, especially for 'Year' if it might be mixed
            if col == 'Year':
                 data[col] = data[col].astype(str) # Convert Year to string for consistent filtering
        else:
            st.error(f"Column '{col}' not found in the data. Please check your CSV file.")
            # Add a dummy column to prevent errors later, or stop execution
            data[col] = 'N/A' 
            
except FileNotFoundError:
    st.error("Error: 'data-360-final-proj/final_watches.csv' not found. Please ensure the file exists in the correct location.")
    st.stop() # Stop execution if data can't be loaded
except Exception as e:
    st.error(f"An error occurred while loading or processing the data: {e}")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filter Watch Listings")

# Manufacturer filter (Dropdown)
manufacturers = ['All'] + sorted(data['Manufacturer'].unique())
selected_manufacturer = st.sidebar.selectbox("Manufacturer", manufacturers, index=0) # index=0 selects 'All' by default

# Filter data based on selected manufacturer before populating model filter
if selected_manufacturer == 'All':
    filtered_by_manufacturer = data
else:
    filtered_by_manufacturer = data[data['Manufacturer'] == selected_manufacturer]

# Model filter (Dropdown - dynamic based on selected manufacturer)
available_models = ['All'] + sorted(filtered_by_manufacturer['Model'].unique())
selected_model = st.sidebar.selectbox("Model", available_models, index=0)

# Apply manufacturer and model filters to get data for metal filter
filtered_for_metal = filtered_by_manufacturer.copy()
if selected_model != 'All':
    filtered_for_metal = filtered_for_metal[filtered_for_metal['Model'] == selected_model]

metal_types = ['All'] + sorted(filtered_for_metal['Metal'].unique())
selected_metal_type = st.sidebar.selectbox("Metal Type", metal_types, index=0)

# Apply manufacturer, model, and metal filters to get data for year filter
filtered_for_year = filtered_for_metal.copy()
if selected_metal_type != 'All':
    filtered_for_year = filtered_for_year[filtered_for_year['Metal'] == selected_metal_type]

years = ['All'] + sorted(filtered_for_year['Year'].unique())
selected_year = st.sidebar.selectbox("Year", years, index=0)

# Apply all filters to get data for price slider
filtered_for_price = filtered_for_year.copy()
if selected_year != 'All':
    filtered_for_price = filtered_for_price[filtered_for_price['Year'] == selected_year]

# Price Range Slider with dynamic min/max based on filtered data
if len(filtered_for_price) > 0:
    min_price = int(filtered_for_price['Price ($)'].min())
    max_price = int(filtered_for_price['Price ($)'].max())
else:
    min_price = int(data['Price ($)'].min())
    max_price = int(data['Price ($)'].max())

st.sidebar.subheader("Price Range")
price_range = st.sidebar.slider(
    "Select Price Range ($)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=1000
)

# --- Apply Filters ---
filtered_data = data.copy()

# Apply filters sequentially only if a specific option (not 'All') is selected
if selected_manufacturer != 'All':
    filtered_data = filtered_data[filtered_data['Manufacturer'] == selected_manufacturer]

if selected_model != 'All':
    filtered_data = filtered_data[filtered_data['Model'] == selected_model]

if selected_metal_type != 'All':
    filtered_data = filtered_data[filtered_data['Metal'] == selected_metal_type]

if selected_year != 'All':
    filtered_data = filtered_data[filtered_data['Year'] == selected_year]

# Apply price range filter
filtered_data = filtered_data[(filtered_data['Price ($)'] >= price_range[0]) & 
                             (filtered_data['Price ($)'] <= price_range[1])]

# --- Main Page Display ---

# Add in a subheader for the filtered data
st.header('List of Watches')

# Display the filtered data
column_config = None
if 'Link' in filtered_data.columns: # Changed 'url' to 'Link'
    column_config={"Link": st.column_config.LinkColumn("Link", display_text="View Listing")} # Changed 'url' to 'Link'

st.dataframe(filtered_data, hide_index=True, column_config=column_config)

# Show number of watches after filtering
st.write(f"Showing {len(filtered_data)} watches out of {len(data)} total watches based on current filters.")

# Initialize the session state for chart visibility if it doesn't exist
if 'show_chart' not in st.session_state:
    st.session_state.show_chart = False

# Add a button to toggle the price by brand visualization
if st.button("Display/Hide Visualizations"):
    st.session_state.show_chart = not st.session_state.show_chart

# Display the chart based on the session state
if st.session_state.show_chart:
    st.header("Average Watch Price by Selected Grouping")

    groupings = ['Manufacturer', 'Metal', 'Year', 'Bezel Type', 'Discontinued']
    selected_grouping = st.selectbox("Grouping Method", groupings, index=0)
    
    # Calculate average price by selected grouping
    group_avg_price = data.groupby(f'{selected_grouping}')['Price ($)'].mean().reset_index().sort_values('Price ($)', ascending=False)
    
    # Create a bar chart 
    fig = px.bar(
        group_avg_price, 
        x=selected_grouping, 
        y='Price ($)',
        title=f'Average Price by {selected_grouping}',
        labels={selected_grouping: selected_grouping, 'Price ($)': 'Average Price ($)'},
        color='Price ($)',  # Add color gradient based on price
    )
    
    # Customize layout
    fig.update_layout(
        xaxis_title=selected_grouping,
        yaxis_title='Average Price ($)',
        xaxis_tickangle=-45,
        height=650,
        width=850
    )
    
    # Display the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)