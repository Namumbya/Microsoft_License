import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Access the database URL from the database section
database_url = st.secrets["database"]["DATABASE_URL"]
# Create SQLAlchemy engine

engine = create_engine(database_url)

def load_data():
    with engine.connect() as conn:
        licenses_df = pd.read_sql("SELECT * FROM licenses", conn)
        usage_df = pd.read_sql("SELECT * FROM subscription_usage", conn)
    return licenses_df, usage_df

def display_license_info(licenses_df):
    st.header("License Information")
    st.write(licenses_df)

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

def display_visualizations(usage_summary):
    st.header("Visualizations")
    st.subheader("Total Assigned Users per License")
    st.bar_chart(usage_summary.set_index('license_name')['total_users'])

    st.subheader("Total Costs per License")
    st.bar_chart(usage_summary.set_index('license_name')['total_cost'])

    avg_users = usage_summary['total_users'].mean()
    st.header("Average Number of Users per License")
    st.write(f"The average number of users per license is: {avg_users:.2f}")

def main():
    st.title("Microsoft Licensing Costs Dashboard")

    # Load data
    licenses_df, usage_df = load_data()

    # Display data
    display_license_info(licenses_df)
    usage_summary = display_usage_summary(licenses_df, usage_df)
    display_visualizations(usage_summary)

if __name__ == "__main__":
    main()
