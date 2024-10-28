import streamlit as st
import pandas as pd
import psycopg

# Database connection configuration
DB_CONNECTION_STRING = "postgresql://neondb_owner:UhABYS0JKFx6@ep-lively-firefly-a8n4qxbu.eastus2.azure.neon.tech/neondb?sslmode=require"

# Connect to Neon PostgreSQL database
with psycopg.connect(DB_CONNECTION_STRING) as conn:
    # Page title
    st.title("Microsoft Licensing Costs Dashboard")

    # Query and load data into DataFrames
    @st.cache_data
    def load_data():
        # Fetching data
        licenses_df = pd.read_sql("SELECT * FROM licenses", conn)
        usage_df = pd.read_sql("SELECT * FROM subscription_usage", conn)
        return licenses_df, usage_df

    # Load data
    licenses_df, usage_df = load_data()

    # Display License Information Table
    st.header("License Information")
    st.write(licenses_df)

    # Input form for new licenses
    st.header("Add New License")
    with st.form("license_form"):
        license_name = st.text_input("License Name")
        user_type = st.text_input("User Type")
        office_suite = st.text_input("Office Suite")
        price_per_user = st.number_input("Price Per User", min_value=0.0, step=0.01)
        submit_button = st.form_submit_button("Add License")
        
        if submit_button:
            insert_query = f"""
            INSERT INTO licenses (license_name, user_type, office_suite, price_per_user)
            VALUES ('{license_name}', '{user_type}', '{office_suite}', {price_per_user});
            """
            with conn.cursor() as cursor:
                cursor.execute(insert_query)
                conn.commit()
            st.success("License added successfully!")

    # Display Assigned Users and Total Costs
    st.header("Subscription Usage Summary")
    usage_summary = usage_df.groupby('license_id').agg(
        total_users=('assigned_users', 'sum'),
        total_cost=('total_cost', 'sum')
    ).reset_index()

    # Merge to include license names
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

    # Average number of users per license
    st.header("Average Number of Users per License")
    avg_users = usage_summary['total_users'].mean()
    st.write(f"The average number of users per license is: {avg_users:.2f}")

    # Optionally, you can add more visualizations as needed
