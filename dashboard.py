import streamlit as st
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")

def load_data():
    lic_path = DATA_DIR / "licenses.csv"
    use_path = DATA_DIR / "subscription_usage.csv"
    if not lic_path.exists() or not use_path.exists():
        st.error("CSV files not found. Please add data/licenses.csv and data/subscription_usage.csv.")
        st.stop()
    licenses_df = pd.read_csv(lic_path)
    usage_df = pd.read_csv(use_path)
    return licenses_df, usage_df

def display_license_info(licenses_df):
    st.header("License Information")
    st.dataframe(licenses_df, use_container_width=True)

def display_usage_summary(licenses_df, usage_df):
    st.header("Subscription Usage Summary")
    usage_summary = usage_df.groupby('license_id', as_index=False).agg(
        total_users=('assigned_users', 'sum'),
        total_cost=('total_cost', 'sum')
    ).merge(
        licenses_df[['license_id', 'license_name']],
        on='license_id',
        how='left'
    )
    st.dataframe(usage_summary, use_container_width=True)
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
    licenses_df, usage_df = load_data()
    display_license_info(licenses_df)
    usage_summary = display_usage_summary(licenses_df, usage_df)
    display_visualizations(usage_summary)

if __name__ == "__main__":
    main()
