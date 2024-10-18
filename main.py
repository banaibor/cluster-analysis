import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Define constants
VDV_ANNUAL_SALARY = 36000  # Annual salary per VDV

# Function to adjust VDVs based on the specified logic
def adjust_vdvs(count):
    if count <= 1:
        return 1  # If VDVs are <= 1, keep 1 VDV
    elif 2 <= count <= 3:
        return 1  # Reduce to 1
    elif 4 <= count <= 10:
        return int(count * 0.6)  # Keep approximately 60% of VDVs
    else:
        return int(count * 0.6)  # Keep approximately 60% of VDVs

# Adjust the 'No of VDVs' column in the old clusters dataframe
def apply_vdv_adjustment(df):
    df['Adjusted VDVs'] = df['No of VDVs'].apply(adjust_vdvs)  # Create Adjusted VDVs column
    return df

# Count the single village clusters (where 'Number of Villages' is 1) district-wise
def count_single_village_clusters_district_wise(df):
    return df[df['Number of Villages'] == 1].groupby('District').size()

# Get detailed single village cluster data for a specific district
def get_single_village_clusters_details(df, district):
    return df[(df['District'] == district) & (df['Number of Villages'] == 1)]

# Load datasets for VDV analysis
@st.cache_data
def load_vdv_data():
    new_clusters_path = 'NewClustersWithVDV.xlsx'
    old_clusters_path = 'OldClustersWithVDV.xlsx'
    
    new_clusters_df = pd.read_excel(new_clusters_path)
    old_clusters_df = pd.read_excel(old_clusters_path)
    
    # Adjust the old clusters by removing VDVs
    old_clusters_df = apply_vdv_adjustment(old_clusters_df)
    
    return new_clusters_df, old_clusters_df

# Calculate total annual salary for New and Old Clusters
def calculate_total_salaries(df, vdvs_column):
    total_salary = (df[vdvs_column] * VDV_ANNUAL_SALARY).sum()
    return total_salary

# VDV Analysis Dashboard
def run_vdv_analysis():
    new_clusters_df, old_clusters_df = load_vdv_data()

    # Sidebar for district selection
    st.sidebar.header('Select District')
    districts = list(set(new_clusters_df['District']).union(set(old_clusters_df['District'])))
    selected_district = st.sidebar.selectbox('Select a District', districts)

    # Filter the data for the selected district
    filtered_new_df = new_clusters_df[new_clusters_df['District'] == selected_district]
    filtered_old_df = old_clusters_df[old_clusters_df['District'] == selected_district]

    # Calculate district-specific expenses for the selected district
    total_expenses_new_district = calculate_total_salaries(filtered_new_df, 'No of VDVs')
    total_expenses_old_district = calculate_total_salaries(filtered_old_df, 'Adjusted VDVs')

    # Count single village clusters district-wise
    single_village_counts_new = count_single_village_clusters_district_wise(new_clusters_df)
    single_village_counts_old = count_single_village_clusters_district_wise(old_clusters_df)

    # Show VDV numbers for the selected district
    st.subheader(f'VDV Comparison in {selected_district}')
    new_vdvs = filtered_new_df['No of VDVs'].sum()
    old_adjusted_vdvs = filtered_old_df['Adjusted VDVs'].sum()

    st.write(f"**New Clusters (VDVs)**: {new_vdvs}")
    st.write(f"**Old Clusters (Adjusted VDVs)**: {old_adjusted_vdvs}")

    # Summary table with district-wise expenses
    summary_data = {
        'Metric': ['Total Expenses New (District)', 'Total Expenses Old (District)', 
                'Single Village Clusters (New)', 'Single Village Clusters (Old)'],
        'Values': [total_expenses_new_district, total_expenses_old_district, 
                single_village_counts_new.get(selected_district, 0), 
                single_village_counts_old.get(selected_district, 0)]
    }
    summary_df = pd.DataFrame(summary_data)
    
    st.subheader("Summary Table")
    st.dataframe(summary_df)

    # Display detailed single village clusters for new and old clusters
    st.subheader("Single Village Clusters Details")

    # Get details for single village clusters
    single_village_details_new = get_single_village_clusters_details(new_clusters_df, selected_district)
    single_village_details_old = get_single_village_clusters_details(old_clusters_df, selected_district)

    if not single_village_details_new.empty:
        st.write(f"**Single Village Clusters in New Clusters ({selected_district})**")
        st.dataframe(single_village_details_new)
    else:
        st.write(f"No single village clusters found in New Clusters for {selected_district}.")

    if not single_village_details_old.empty:
        st.write(f"**Single Village Clusters in Old Clusters ({selected_district})**")
        st.dataframe(single_village_details_old)
    else:
        st.write(f"No single village clusters found in Old Clusters for {selected_district}.")

    # Capacity analysis for old clusters
    st.subheader(f'Capacity Analysis of Old Clusters (Adjusted VDVs) in {selected_district}')
    fig_old = px.box(filtered_old_df, y='Adjusted VDVs', title=f'Capacity Analysis of Old Clusters (Adjusted VDVs) in {selected_district}',
                     labels={'Adjusted VDVs': 'No of VDVs'})
    st.plotly_chart(fig_old)

    # Capacity analysis for new clusters
    st.subheader(f'Capacity Analysis of New Clusters in {selected_district}')
    fig_new = px.box(filtered_new_df, y='No of VDVs', title=f'Capacity Analysis of New Clusters in {selected_district}',
                     labels={'No of VDVs': 'No of VDVs'})
    st.plotly_chart(fig_new)

    # Distribution Analysis: Bar chart comparison of VDVs
    st.subheader(f'Distribution of VDVs in {selected_district}')
    combined_df = pd.concat([filtered_new_df.assign(Source='New Clusters'), 
                             filtered_old_df.assign(Source='Old Clusters (Adjusted VDVs)')])
    fig_distribution = px.histogram(combined_df, x='No of VDVs', color='Source',
                                    title=f'Distribution of VDVs in {selected_district}',
                                    labels={'No of VDVs': 'Number of VDVs'})
    st.plotly_chart(fig_distribution)

    # Annual Salary Expenses Comparison
    st.subheader(f'Annual Salary Expenses Comparison in {selected_district}')
    st.write(f'Total Annual Expenses for New Clusters: ₹{total_expenses_new_district:,.2f}')
    st.write(f'Total Annual Expenses for Old Clusters (Adjusted VDVs): ₹{total_expenses_old_district:,.2f}')

    # Add footer
    st.markdown("---")
    st.write("© 2024 ResGov. All Rights Reserved.")

# Main function to run the appropriate dashboard based on selection
def main():
    st.sidebar.title("VDV & Travel Allowance Analysis")

    app_mode = st.sidebar.selectbox("Choose the analysis", ["VDV Analysis", "Travel Allowance Analysis"])

    if app_mode == "VDV Analysis":
        run_vdv_analysis()

if __name__ == "__main__":
    main()
