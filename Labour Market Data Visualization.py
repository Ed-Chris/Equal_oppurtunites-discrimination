import streamlit as st
import pandas as pd
import plotly.express as px
from stats_can import StatsCan

# Initialize StatsCan
sc = StatsCan()

# Load data
try:
    df = sc.table_to_df("14-10-0023-01")
except Exception as e:
    st.error(f"Error loading data: {e}")
    df = pd.DataFrame()

# Check if the DataFrame is empty
if df.empty:
    st.error("No data available to display.")
else:
    # Clean and rename DataFrame
    df_clean = df[['REF_DATE', 'Labour force characteristics', 'North American Industry Classification System (NAICS)', 'Sex', 'Age group', 'VALUE']]
    df_main = df_clean.rename(columns={
        'REF_DATE': 'Year',
        'Labour force characteristics': 'Characteristics',
        'North American Industry Classification System (NAICS)': 'Industry',
        'VALUE': 'Value'
    })

    # Convert 'Year' column to string to keep it plain
    df_main['Year'] = df_main['Year'].astype(str)

    # Aggregate data to yearly level by taking the mean (or sum)
    df_main['Year'] = df_main['Year'].str[:4]  # Keep only the year part
    df_yearly = df_main.groupby(['Year', 'Characteristics', 'Industry', 'Sex', 'Age group'], as_index=False).mean()

    # Define the list of characteristics
    characteristics = ['Labour force', 'Employment', 'Unemployment', 'Unemployment rate', 'Full-time employment', 'Part-time employment']

    # Streamlit app
    st.title('Labour Market Characteristics Visualization')

    # Sidebar for user input
    st.sidebar.header('Select Visualization Options')
    selected_characteristic = st.sidebar.selectbox('Select a characteristic', characteristics)
    selected_industry = st.sidebar.selectbox('Select an industry', df_yearly['Industry'].unique())
    selected_sex = st.sidebar.selectbox('Select sex', df_yearly['Sex'].unique())
    selected_age_group = st.sidebar.selectbox('Select age group', df_yearly['Age group'].unique())

    # Filter data based on selected options
    filtered_data = df_yearly[
        (df_yearly['Characteristics'] == selected_characteristic) & 
        (df_yearly['Industry'] == selected_industry) &
        (df_yearly['Sex'] == selected_sex) &
        (df_yearly['Age group'] == selected_age_group)
    ]

    if filtered_data.empty:
        st.warning("No data available for the selected options.")
    else:
        # Create interactive visualization using Plotly
        fig = px.line(filtered_data, x='Year', y='Value', title=f'{selected_characteristic} Over Time', 
                      labels={'Value': 'Value (x1000)'}, color_discrete_sequence=['#FFA07A'])
        st.plotly_chart(fig)
        
        # Button to download data as CSV
        csv = filtered_data.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='filtered_data.csv',
            mime='text/csv',
        )
