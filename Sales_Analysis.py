import streamlit as st       # For creating the dashboard interface
import pandas as pd          # For handling data (reading, manipulating)
import plotly.express as px  # For creating interactive plots with Plotly
from itertools import combinations
from collections import Counter

# Load your dataset (ensure the correct path)
file_path = 'exported_data.csv' 
df = pd.read_csv(file_path)

# filters of the dashboard

# Sidebar Filters
st.sidebar.header("Filters")

# Sidebar Filters, each in its own collapsible drop-down

# City Filter inside its own drop-down
with st.sidebar.expander("City Filter", expanded=False):
    city_filter = st.multiselect(
        "Select Cities",
        options=df['City'].unique(),
        default=df['City'].unique()  # Default to all cities selected
    )

# Product Filter inside its own drop-down
with st.sidebar.expander("Product Filter", expanded=False):
    product_filter = st.multiselect(
        "Select Products",
        options=df['Product'].unique(),
        default=df['Product'].unique()  # Default to all products selected
    )

# Hour of the Day Filter inside its own drop-down
with st.sidebar.expander("Hour Filter", expanded=False):
    hour_filter = st.slider(
        "Select Hour of the Day",
        min_value=1,
        max_value=24,
        value=(1, 24)  # Default to full range from 1 to 24
    )

# Month Filter inside its own drop-down
with st.sidebar.expander("Month Filter", expanded=False):
    month_filter = st.multiselect(
        "Select Months",
        options=df['Month'].unique(),
        default=df['Month'].unique()  # Default to all months selected
    )



# Apply filters to the dataset

df_filtered = df[
    (df['City'].isin(city_filter)) &  # Filter by selected cities
    (df['Product'].isin(product_filter)) &  # Filter by selected products
    (df['Hour'] >= hour_filter[0]) & (df['Hour'] <= hour_filter[1]) &  # Filter by selected hours
    (df['Month'].isin(month_filter))  # Filter by selected months
]

# Compute Sales Summary
total_sales = df_filtered['Sales'].sum()  # Total sales
total_quantity = df_filtered['Quantity Ordered'].sum()  # Total quantity ordered
total_orders = df_filtered['Order ID'].nunique()  # Total number of unique orders
average_sales_per_order = total_sales / total_orders if total_orders > 0 else 0  # Average sales per order



#FIGURE 1

# Group the filtered data by 'Month' and calculate total sales and total units sold
monthly_sales = df_filtered.groupby('Month').agg({'Sales': 'sum', 'Quantity Ordered': 'sum'}).reset_index()

# Create the Plotly bar chart for Monthly Sales with hover tips
fig = px.bar(
    monthly_sales,
    x='Month',
    y='Sales',
    title='Monthly Sales',
    labels={'Sales': 'Sales (USD)', 'Month': 'Month'},
    hover_data={'Quantity Ordered': True}  # Include total units sold in hover data
)


#FIGURE 2
# Group the filtered data by 'City' and calculate total sales and total units sold
sales_by_city = df_filtered.groupby('City').agg({'Sales': 'sum', 'Quantity Ordered': 'sum'}).reset_index()

# Create the Plotly bar chart for Total Sales by City with hover tips
fig_city = px.bar(
    sales_by_city,
    x='City',
    y='Sales',
    title='Total Sales by City',
    labels={'Sales': 'Sales (USD)', 'City': 'City'},
    hover_data={'Quantity Ordered': True}  # Include total units sold in hover data
)


#FIGURE 3

# Group the filtered data by 'Hour' and calculate total sales and total units sold
orders_by_hour = df_filtered.groupby('Hour').agg({
    'Sales': 'sum',
    'Quantity Ordered': 'sum'
}).reset_index()

# Create the Plotly line chart
fig_hour = px.line(
    orders_by_hour,
    x='Hour',
    y='Quantity Ordered',
    title='Number of Orders by Hour',
    labels={'Quantity Ordered': 'Number of Orders', 'Hour': 'Hour of the Day'},
    markers=True
)

# Customize hover tips using hovertemplate
fig_hour.update_traces(
    hovertemplate=
    '<b>Hour: %{x}</b><br>' +
    'Number of Orders: %{y:,}<br>' +  # Formats numbers with commas
    'Total Sales: $%{customdata[0]:,.2f}'  # Formats sales as currency with 2 decimal places
)

# Add custom data (Total Sales) for hover
fig_hour.update_traces(customdata=orders_by_hour[['Sales']].values)

# Ensure all hours from 1 to 24 are displayed on the x-axis
fig_hour.update_xaxes(tickmode='linear', dtick=1)


# TABLE PLOT

# Initialize a Counter object to keep track of pair frequencies
count = Counter()

# Loop through each row in the 'Grouped' column of df_filtered
for row in df_filtered['Grouped']:
    row_list = row.split(',')  # Split the grouped product string into a list of individual products
    count.update(Counter(combinations(row_list, 2)))  # Create all possible pairs of two products, count them, and update the Counter

# Get the 5 most common product pairs along with their counts
common_pairs = count.most_common(5)

# Convert the result into a dataframe for better display in Streamlit
pair_data = pd.DataFrame(common_pairs, columns=['Product Pair', 'Count'])

# Format the 'Product Pair' column to remove parentheses and quotes
pair_data['Product Pair'] = pair_data['Product Pair'].apply(lambda x: ' & '.join(x))  # Replace comma with '&'

# Set index to start from 1
pair_data.index = pair_data.index + 1


# FIGURE 4

# Ensure 'Quantity Ordered' and 'Price Each' are numeric in the filtered dataset
df_filtered['Quantity Ordered'] = pd.to_numeric(df_filtered['Quantity Ordered'], errors='coerce')
df_filtered['Price Each'] = pd.to_numeric(df_filtered['Price Each'], errors='coerce')

# Drop rows with missing or invalid data from the filtered data
cleaned_data_filtered = df_filtered.dropna(subset=['Quantity Ordered', 'Price Each'])

# Create the Plotly scatter plot for Price vs Quantity Ordered with larger dots
fig_scatter = px.scatter(
    cleaned_data_filtered,
    x='Price Each',
    y='Quantity Ordered',
    title='Price vs Quantity Ordered',
    labels={'Price Each': 'Price (USD)', 'Quantity Ordered': 'Quantity Ordered'},
    hover_data={'Sales': True},  # Optionally include total sales in the hover data
    size='Quantity Ordered',  # You can use size to reflect the quantity ordered
    size_max=20  # Adjust this value to make the dots larger
)

# Update the x-axis to skip by 250 instead of 500
fig_scatter.update_xaxes(tickmode='linear', dtick=250)


#FIGURE 5

# Group the filtered data by 'Product' and calculate total sales and total quantity ordered
sales_by_product = df_filtered.groupby('Product').agg({
    'Sales': 'sum',
    'Quantity Ordered': 'sum'
}).reset_index()

# Sort the data by 'Quantity Ordered' in descending order
sales_by_product = sales_by_product.sort_values(by='Quantity Ordered', ascending=False)

# Create the Plotly bar chart for Quantity Ordered by Product with hover tips for total sales
fig_product = px.bar(
    sales_by_product,
    x='Product',
    y='Quantity Ordered',  # Use 'Quantity Ordered' for the y-axis
    title='Quantity Ordered by Product',
    labels={'Quantity Ordered': 'Quantity Ordered', 'Product': 'Product'},
    hover_data={'Sales': True},  # Include total sales in hover data
)

# Rotate the x-axis labels for better readability
fig_product.update_xaxes(tickangle=45)


# Title and Introduction
st.markdown("<h1 style='text-align: center;'>Sales Analysis Dashboard</h1>", unsafe_allow_html=True)
st.write("This dashboard provides a detailed analysis of sales trends, product performance, and customer behavior across different cities, products, and time periods.")

# Section 1: Sales Summary
# Center the "Sales Summary" heading
st.markdown("<h2 style='text-align: center;'>Sales Summary</h2>", unsafe_allow_html=True)

# Custom HTML for displaying metrics with reduced font size for values and headers
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"<h4 style='text-align: center; font-size: 22px;'>Total Sales (USD)</h4><p style='text-align: center; font-size: 20px;'>${total_sales:,.2f}</p>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<h4 style='text-align: center; font-size: 22px;'>Total Quantity Sold</h4><p style='text-align: center; font-size: 20px;'>{total_quantity:,}</p>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<h4 style='text-align: center; font-size: 22px;'>Total Number of Orders</h4><p style='text-align: center; font-size: 20px;'>{total_orders:,}</p>", unsafe_allow_html=True)

with col4:
    st.markdown(f"<h4 style='text-align: center; font-size: 22px;'>Avg Sales per Order (USD)</h4><p style='text-align: center; font-size: 20px;'>${average_sales_per_order:,.2f}</p>", unsafe_allow_html=True)




# Section 2: Monthly and City Sales Trends
st.markdown("<h2 style='text-align: center;'>Monthly and City Sales Trends</h2>", unsafe_allow_html=True)

# Monthly Sales Plot
st.plotly_chart(fig)

# Sales by City Plot
st.plotly_chart(fig_city)

# Section 3: Product-Level Analysis
st.markdown("<h2 style='text-align: center;'>Product-Level Analysis</h2>", unsafe_allow_html=True)

# Sales by Product or Quantity Ordered by Product Plot
st.plotly_chart(fig_product)

# Section 4: Hourly Analysis
st.markdown("<h2 style='text-align: center;'>Hourly Analysis</h2>", unsafe_allow_html=True)

# Orders by Hour Plot
st.plotly_chart(fig_hour)

# Section 5: Price vs Quantity Ordered
st.markdown("<h2 style='text-align: center;'>Price vs Quantity Ordered</h2>", unsafe_allow_html=True)
st.plotly_chart(fig_scatter)

# Optional Conclusion
st.write("## Key Insights")
st.write("""
- USB-C Charging Cable is the highest-selling item, contributing the most to overall sales.
- Sales peak during the evening hours (between 6 PM and 9 PM).
- San Francisco (CA) City has consistently higher sales compared to other regions with total sales of $878,836.78 .
- Pricing has a noticeable impact on sales volumes, especially for products priced between $100 and $250.
""")

