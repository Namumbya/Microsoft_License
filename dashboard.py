import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Database connection configuration
DB_HOST = "localhost"
DB_NAME = "microsoft_licensing"
DB_USER = "postgres"  
DB_PASS = "1234567890"  
DB_PORT = "5432"  

# Define the SQLAlchemy engine for PostgreSQL
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Page title
st.title("Microsoft Licensing Costs Dashboard")

# Query and load data into DataFrames
@st.cache_data(ttl=10)  # Cache data for 10 seconds
def load_data():
    with engine.connect() as conn:
        licenses_df = pd.read_sql("SELECT * FROM licenses", conn)
        usage_df = pd.read_sql("SELECT * FROM subscription_usage", conn)
    return licenses_df, usage_df

# Loading data
licenses_df, usage_df = load_data()

# License Information Table
st.header("License Information")
st.write(licenses_df)

# Assigned Users and Total Costs
st.header("Subscription Usage Summary")
usage_summary = usage_df.groupby('license_id').agg(
    total_users=('assigned_users', 'sum'),
    total_cost=('total_cost', 'sum'),
    average_users=('assigned_users', 'mean')  # Calculate average users
).reset_index()

# Merging to include license names
usage_summary = usage_summary.merge(
    licenses_df[['license_id', 'license_name']], 
    on='license_id', 
    how='left'
)
st.write(usage_summary)

# Visualizations
st.header("Visualizations")

# Bar chart for total users per license
st.subheader("Total Assigned Users per License")
st.bar_chart(usage_summary.set_index('license_name')['total_users'])

# Bar chart for total costs per license
st.subheader("Total Costs per License")
st.bar_chart(usage_summary.set_index('license_name')['total_cost'])

# Bar chart for average users per license
st.subheader("Average Assigned Users per License")
st.bar_chart(usage_summary.set_index('license_name')['average_users'])

# Overall Total Costs
st.header("Overall Total Costs")
st.write(f"Total cost of licenses: ${usage_summary['total_cost'].sum():,.2f}")

# Overall Total Users
st.header("Overall Total Users")
st.write(f"Total assigned users: {usage_summary['total_users'].sum()}")

# Refresh data button
if st.button("Refresh Data"):
    licenses_df, usage_df = load_data()
