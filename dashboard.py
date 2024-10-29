import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Database connection configuration
DB_CONNECTION_STRING = 'postgresql://tsdbadmin:am9tn6slp7sb72r4@sfo4sscri4.jev7qsi3kr.tsdb.cloud.timescale.com:33121/tsdb?sslmode=require'

# Create SQLAlchemy engine
engine = create_engine(DB_CONNECTION_STRING)

# Function to load data from the database
def load_data():
    with engine.connect() as conn:
        licenses_df = pd.read_sql("SELECT * FROM licenses", conn)
        usage_df = pd.read_sql("SELECT * FROM subscription_usage", conn)
    return licenses_df, usage_df

# Function to display license information
def display_license_info(licenses_df):
    st.header("License Information")
    st.write(licenses_df)

# Function to display subscription usage summary
def display_usage_summary(licenses_df, usage_df):
    st.header("Subscription Usage Summary")
    usage_summary = usage_df.groupby('license_id').agg(
        total_users=('assigned_users', 'sum'),
        total_cost=('total_cost', 'sum')
    ).reset_index()

    usage_summary = usage_summary.merge(
        licenses_df[['license_id', 'license_name']], 
        on='license_id', 
        how='left'
    )
    st.write(usage_summary)
    return usage_summary

# Function to display visualizations
def display_visualizations(usage_summary):
    st.header("Visualizations")
    st.subheader("Total Assigned Users per License")
    st.bar_chart(usage_summary.set_index('license_name')['total_users'])

    st.subheader("Total Costs per License")
    st.bar_chart(usage_summary.set_index('license_name')['total_cost'])

    avg_users = usage_summary['total_users'].mean()
    st.header("Average Number of Users per License")
    st.write(f"The average number of users per license is: {avg_users:.2f}")

# Main application flow
def main():
    st.title("Microsoft Licensing Costs Dashboard")

    # Load data
    licenses_df, usage_df = load_data()

    # Display data
    display_license_info(licenses_df)
    usage_summary = display_usage_summary(licenses_df, usage_df)
    display_visualizations(usage_summary)

    # Add a refresh button
    # if st.button("Refresh Data"):
    #     licenses_df, usage_df = load_data()  # Reload data on button press
    #     display_license_info(licenses_df)
    #     usage_summary = display_usage_summary(licenses_df, usage_df)
    #     display_visualizations(usage_summary)

if __name__ == "__main__":
    main()
