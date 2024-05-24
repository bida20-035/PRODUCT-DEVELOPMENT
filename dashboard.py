import streamlit as st
import plotly.express as px
import pandas as pd

# Set Streamlit page configuration
st.set_page_config(page_title="FunOlympics Games Analysis Dashboard!!!", page_icon=":bar_chart:", layout="wide")

# Load the CSV file into a DataFrame
df = pd.read_csv("olympic_web_logs.csv")

# Title and CSS styling
st.title(" :bar_chart: FunOlympics Games Analysis Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# File uploader for additional CSV files
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read uploaded file
    new_df = pd.read_csv(uploaded_file)
    # Display uploaded data
    st.write("Uploaded Data:")
    st.write(new_df)

st.markdown("---")

# Sidebar filters
st.sidebar.image("./images/olympicslogo.jpg", width=200, use_column_width=False)
st.sidebar.header("Filter Here:")

# Date filters
start_date = st.sidebar.date_input("Start Date", pd.to_datetime(df['Date']).min(), key="start_date_input")
end_date = st.sidebar.date_input("End Date", pd.to_datetime(df['Date']).max(), key="end_date_input")

# Country filter
country = st.sidebar.multiselect("Country", df["Country"].unique())

# Sport filter
Sport = st.sidebar.multiselect("Sport", df["Sport"].unique())

# Filter DataFrame based on sidebar inputs
filtered_df = df[
    (pd.to_datetime(df['Date']) >= pd.to_datetime(start_date)) &
    (pd.to_datetime(df['Date']) <= pd.to_datetime(end_date))
]

if country:
    filtered_df = filtered_df[filtered_df['Country'].isin(country)]

if Sport:
    filtered_df = filtered_df[filtered_df['Sport'].isin(Sport)]

# Display metrics in the main page
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_visits_by_url = filtered_df['URL'].value_counts()
    url_visits_df = pd.DataFrame({'URL': total_visits_by_url.index, 'Total Visits': total_visits_by_url.values})
    total_visits = url_visits_df['Total Visits'].sum()
    st.metric(label="Total Visits", value=total_visits)
    
with col2:
    total_females = (filtered_df['Gender'] == 'Female').sum()
    st.metric(label="Total Females Visited", value=total_females)

with col3:
    total_males = (filtered_df['Gender'] == 'Male').sum()
    st.metric(label="Total Males Visited", value=total_males)
    
with col4:
    avg_visits_per_day = filtered_df.groupby(filtered_df['Date']).size().mean()
    col4.metric(label="Avg Visits per Day", value=f"{avg_visits_per_day:.2f}", delta=0)

# Divider
st.markdown("---")

# First row of plots
col1, col2 = st.columns(2)

with col1:
    # Plotting the top 10 most viewed sports
    popular_sports = filtered_df['Sport'].value_counts().head(10)
    fig = px.bar(popular_sports, x=popular_sports.index, y=popular_sports.values, 
                 labels={'x': 'Sport', 'y': 'Number of Visits'},
                 title='Top 10 Most Viewed Sports')
    fig.update_layout(xaxis_title='Sport', yaxis_title='Number of Visits')
    st.plotly_chart(fig)
    
    # Add a button to download data
    with st.expander("View Data"):
        st.write(popular_sports)
        csv = popular_sports.reset_index().to_csv(index=False)
        st.download_button(label="Download Data", data=csv, file_name="popular_sports.csv", mime="text/csv")

with col2:
    # Plotting the distribution of content types
    content_type_by_ip = filtered_df.groupby('Content Type')['IP Address'].count()
    fig = px.pie(content_type_by_ip, values='IP Address', names=content_type_by_ip.index, 
                 title='Content Type Distribution')
    st.plotly_chart(fig)
    
    # Add a button to download data
    with st.expander("View Data"):
        st.write(content_type_by_ip)
        csv = content_type_by_ip.reset_index().to_csv(index=False)
        st.download_button(label="Download Data", data=csv, file_name="content_type_distribution.csv", mime="text/csv")

# Second row of plots
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    # Data preprocessing and plotting hourly traffic patterns
    filtered_df['Timestamp'] = pd.to_datetime(filtered_df['Timestamp'], errors='coerce')
    filtered_df = filtered_df.dropna(subset=['Timestamp'])
    filtered_df['Hour'] = filtered_df['Timestamp'].dt.hour
    hourly_traffic = filtered_df.groupby('Hour').size()

    fig = px.line(hourly_traffic, x=hourly_traffic.index, y=hourly_traffic.values, 
                  labels={'x': 'Hour of the Day', 'y': 'Number of Visits'},
                  title='Hourly Traffic Patterns')
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=0, dtick=1))
    st.plotly_chart(fig)

    # Add a button to download data
    with st.expander("View Data"):
        st.write(hourly_traffic)
        csv = hourly_traffic.reset_index().to_csv(index=False)
        st.download_button(label="Download Data", data=csv, file_name="hourly_traffic.csv", mime="text/csv")

with col2:
    # Plotting top 10 countries by number of visits
    country_visits = filtered_df['Country'].value_counts().head(10)
    fig = px.bar(country_visits, x=country_visits.values, y=country_visits.index, orientation='h', 
                 labels={'x': 'Number of Visits', 'y': 'Country'},
                 title='Top 10 Countries by Number of Visits')
    st.plotly_chart(fig)
    
    # Add a button to download data
    with st.expander("View Data"):
        st.write(country_visits)
        csv = country_visits.reset_index().to_csv(index=False)
        st.download_button(label="Download Data", data=csv, file_name="country_visits.csv", mime="text/csv")
# Third row of plots
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    # Plotting distribution of time spent on website
    fig = px.histogram(filtered_df, x='Time Spent (seconds)', nbins=30, 
                       title='Distribution of Time Spent on Website')
    fig.update_layout(xaxis_title='Time Spent (seconds)', yaxis_title='Frequency')
    st.plotly_chart(fig)

with col2:
    # Plotting HTTP status codes for GET requests
    http_status_counts = filtered_df[filtered_df['Request Method'] == 'GET']['HTTP Status'].value_counts()
    
    # Define custom colors manually
    custom_colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']

    fig = px.pie(
        http_status_counts, 
        values=http_status_counts, 
        names=http_status_counts.index, 
        title='HTTP Status Codes for GET Requests',
        color_discrete_sequence=custom_colors  # Apply the custom colors
    )
    st.plotly_chart(fig)
    
    # Add a button to download data
    with st.expander("View Data"):
        st.write(http_status_counts)
        csv = http_status_counts.reset_index().to_csv(index=False)
        st.download_button(label="Download Data", data=csv, file_name="http_status_counts.csv", mime="text/csv")
