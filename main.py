import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Define constants
VDV_ANNUAL_SALARY = 36000  # Annual salary per VDV

# Revised function to adjust VDVs based on specified logic
def adjust_vdvs(count):
    if count <= 1:
        return 1  # If VDVs are <= 1, keep 1 VDV
    elif 2 <= count <= 3:
        return 1  # Reduce to 1
    elif 4 <= count <= 10:
        return int(count * 0.6)  # Keep approximately 50% of VDVs
    else:
        return int(count * 0.6)  # Keep approximately 50% of VDVs

# Adjust the 'No of VDVs' column in the old clusters dataframe
def apply_vdv_adjustment(df):
    df['Adjusted VDVs'] = df['No of VDVs'].apply(adjust_vdvs)  # Create Adjusted VDVs column
    return df

# Load datasets for VDV analysis
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

    # Calculate expenses for both datasets
    total_expenses_new = calculate_total_salaries(new_clusters_df, 'No of VDVs')  # New clusters
    total_expenses_old = calculate_total_salaries(old_clusters_df, 'Adjusted VDVs')  # Old clusters

    # Streamlit app layout
    st.title('VDV Cluster Analysis & Expense Overview (With Adjusted VDVs)')

    # Sidebar for district selection
    st.sidebar.header('Select District')
    districts = list(set(new_clusters_df['District']).union(set(old_clusters_df['District'])))
    selected_district = st.sidebar.selectbox('Select a District', districts)

    # Filter the data for the selected district
    filtered_new_df = new_clusters_df[new_clusters_df['District'] == selected_district]
    filtered_old_df = old_clusters_df[old_clusters_df['District'] == selected_district]

    # Show VDV numbers for the selected district
    st.subheader(f'VDV Comparison in {selected_district}')
    new_vdvs = filtered_new_df['No of VDVs'].sum()
    old_adjusted_vdvs = filtered_old_df['Adjusted VDVs'].sum()

    st.write(f"**New Clusters (VDVs)**: {new_vdvs}")
    st.write(f"**Old Clusters (Adjusted VDVs)**: {old_adjusted_vdvs}")

    # Summary table
    summary_data = {
        'Metric': ['New Clusters (VDVs)', 'Old Clusters (Adjusted VDVs)', 'Total Expenses New', 'Total Expenses Old'],
        'Values': [new_vdvs, old_adjusted_vdvs, total_expenses_new, total_expenses_old]
    }
    summary_df = pd.DataFrame(summary_data)
    
    st.subheader("Summary Table")
    st.dataframe(summary_df)

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

    # 1-Year Expenses Analysis
    total_expenses_new_district = calculate_total_salaries(filtered_new_df, 'No of VDVs')
    total_expenses_old_district = calculate_total_salaries(filtered_old_df, 'Adjusted VDVs')

    st.subheader(f'Annual Salary Expenses Comparison in {selected_district}')
    st.write(f'Total Annual Expenses for New Clusters: ₹{total_expenses_new_district:,.2f}')
    st.write(f'Total Annual Expenses for Old Clusters (Adjusted VDVs): ₹{total_expenses_old_district:,.2f}')

    # Trade-off analysis: Total expenses comparison for all districts
    st.subheader('Total Expenses for All Districts (New vs Old Clusters with Adjusted VDVs)')
    st.write(f'Total Annual Expenses for New Clusters: ₹{total_expenses_new:,.2f}')
    st.write(f'Total Annual Expenses for Old Clusters (Adjusted VDVs): ₹{total_expenses_old:,.2f}')

    # Trade-off analysis text
    if total_expenses_new < total_expenses_old:
        st.write("**Observation:** The new clusters have a lower overall expense compared to the old clusters.")
    else:
        st.write("**Observation:** The new clusters have a higher overall expense compared to the old clusters.")

    # Savings or additional costs
    expense_difference = total_expenses_old - total_expenses_new
    if expense_difference > 0:
        st.write(f"By moving to the new clusters, there's a potential saving of ₹{expense_difference:,.2f} annually.")
    else:
        st.write(f"By moving to the new clusters, there's an additional cost of ₹{-expense_difference:,.2f} annually.")

    # Add footer
    st.markdown("---")
    st.write("© 2024 ResGov. All Rights Reserved.")


# Travel Allowance Dashboard
@st.cache_data
def load_travel_data():
    new_clusters_path = 'NewClusters27.xlsx'
    old_clusters_path = 'OldClusters27.xlsx'
    new_clusters = pd.read_excel(new_clusters_path)
    old_clusters = pd.read_excel(old_clusters_path)
    return old_clusters, new_clusters

# Calculate travel allowances based on the cost per km
def calculate_travel_allowances(data, cost_per_km):
    data['Travel Allowance'] = data['Distance'] * cost_per_km
    return data

# Calculate the total annual travel cost based on the number of trips
def calculate_annual_cost(data, trips_per_year):
    data['Annual Travel Cost'] = data['Travel Allowance'] * trips_per_year
    return data

def run_travel_allowance_analysis():
    # Load the cluster data
    old_clusters, new_clusters = load_travel_data()

    # Streamlit app layout
    st.title("Travel Allowance and Annual Cost Comparison for Old and New Clusters")

    # User input for cost per km and number of trips
    cost_per_km = st.number_input("Enter the cost per Km", min_value=0.0, value=1.0, step=0.1)
    trips_per_year = st.number_input("Enter the number of trips per year", min_value=1, value=4, step=1)

    # Calculate travel allowances and annual cost for old and new clusters
    old_clusters = calculate_travel_allowances(old_clusters, cost_per_km)
    new_clusters = calculate_travel_allowances(new_clusters, cost_per_km)

    old_clusters = calculate_annual_cost(old_clusters, trips_per_year)
    new_clusters = calculate_annual_cost(new_clusters, trips_per_year)

    # Display the data for both clusters
    st.subheader("Old Clusters Travel Allowances")
    st.write(old_clusters)

    st.subheader("New Clusters Travel Allowances")
    st.write(new_clusters)

    # Group by district and calculate the total travel allowances per district
    old_district_summary = old_clusters.groupby('District')['Annual Travel Cost'].sum().reset_index()
    new_district_summary = new_clusters.groupby('District')['Annual Travel Cost'].sum().reset_index()

    # Merging for comparison
    comparison = old_district_summary.merge(new_district_summary, on='District', suffixes=('_Old', '_New'))

    # Plotting the comparison of annual travel costs
    fig_bar = px.bar(comparison, x='District', y=['Annual Travel Cost_Old', 'Annual Travel Cost_New'], 
                     barmode='group', title='Annual Travel Cost Comparison by District',
                     labels={'value': 'Annual Travel Cost', 'District': 'District'})
    st.plotly_chart(fig_bar)

    # Calculate the overall total cost for old and new clusters
    total_old_cost = old_clusters['Annual Travel Cost'].sum()
    total_new_cost = new_clusters['Annual Travel Cost'].sum()

    # Display overall total costs
    st.subheader("Overall Total Annual Travel Cost")
    st.write(f"Total Cost for Old Clusters: ₹{total_old_cost:,.2f}")
    st.write(f"Total Cost for New Clusters: ₹{total_new_cost:,.2f}")

    # Pie chart to show the proportion of total cost for old and new clusters
    st.subheader("Proportion of Total Annual Travel Cost (Old vs New Clusters)")
    fig_pie = px.pie(names=['Old Clusters', 'New Clusters'], values=[total_old_cost, total_new_cost],
                     title='Proportion of Total Annual Travel Cost')
    st.plotly_chart(fig_pie)

    # Line chart for trends in total cost per district
    st.subheader("Trend Analysis of Annual Travel Cost by District")
    fig_line = px.line(comparison, x='District', y=['Annual Travel Cost_Old', 'Annual Travel Cost_New'], 
                       title='Trend of Annual Travel Cost (Old vs New Clusters)',
                       labels={'value': 'Annual Travel Cost', 'District': 'District'})

    # Heatmap of travel cost differences between old and new clusters
    st.subheader("Heatmap of Travel Allowance Difference")
    comparison['Allowance Difference'] = comparison['Annual Travel Cost_New'] - comparison['Annual Travel Cost_Old']

    fig_heatmap = go.Figure(data=go.Heatmap(
            z=[comparison['Allowance Difference']],
            x=comparison['District'],
            y=['Allowance Difference'],
            colorscale='Viridis',
            hoverongaps=False
    ))

    fig_heatmap.update_layout(title='Heatmap of Travel Allowance Difference (New vs Old)', 
                              xaxis_title='District', 
                              yaxis_title='Metric')

    st.plotly_chart(fig_line)
    st.plotly_chart(fig_heatmap)

# Main function to run the Streamlit app
def run():
    st.set_page_config(page_title="VDV Cluster Analysis", layout="wide")  # Set page config here
    st.sidebar.title("Navigation")
    app_selection = st.sidebar.radio("Go to", ("VDV Analysis", "Travel Allowance Analysis"))

    if app_selection == "VDV Analysis":
        run_vdv_analysis()
    else:
        run_travel_allowance_analysis()

if __name__ == "__main__":
    run()
