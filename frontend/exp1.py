import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from plotly.subplots import make_subplots

# Set page configuration and styling
st.set_page_config(page_title="Social Media Analytics", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
    <style>
        .metric-card {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .chart-container {
            background-color: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        .stMetric {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Sample data generation with post_time
    # data = {
    #     'Post_ID': [f'P{str(i).zfill(3)}' for i in range(50)],
    #     'Post_Type': ['Reel', 'Carousel', 'Static'] * 17,
    #     'Likes': [
    #         *[round(x) for x in np.random.normal(3000, 1000, 17)],
    #         *[round(x) for x in np.random.normal(2000, 800, 17)],
    #         *[round(x) for x in np.random.normal(1500, 600, 16)]
    #     ],
    #     'Shares': [
    #         *[round(x) for x in np.random.normal(800, 200, 17)],
    #         *[round(x) for x in np.random.normal(600, 150, 17)],
    #         *[round(x) for x in np.random.normal(400, 100, 16)]
    #     ],
    #     'Comments': [
    #         *[round(x) for x in np.random.normal(500, 150, 17)],
    #         *[round(x) for x in np.random.normal(300, 100, 17)],
    #         *[round(x) for x in np.random.normal(200, 50, 16)]
    #     ],
    #     'Post_Date': [(datetime.now() - timedelta(days=x)) for x in range(50)],
    #     'Post_Time': [f"{np.random.randint(1, 12)}:{np.random.randint(0, 59):02d} {'AM' if np.random.random() > 0.5 else 'PM'}" 
    #                  for _ in range(50)]
    # }
    df = pd.read_csv("fsed.csv")
    df['Post_Date'] = pd.to_datetime(df['Post_Date'])
    # Calculate engagement metrics
    df['Engagement_Rate'] = ((df['Likes'] + df['Comments'] + df['Shares']) / 
                            df.groupby('Post_Type')['Likes'].transform('mean') * 100)
    df['Total_Engagement'] = df['Likes'] + df['Comments'] + df['Shares']
    
    return df

def create_time_heatmap(df):
    # Convert string time to datetime for proper handling
    df['Hour'] = pd.to_datetime(df['Post_Time'], format='%H:%M').dt.hour

    
    # Create hour bins and calculate average engagement
    time_engagement = df.groupby(['Hour', 'Post_Type'])['Engagement_Rate'].mean().reset_index()
    pivot_table = time_engagement.pivot(index='Post_Type', columns='Hour', values='Engagement_Rate')
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_table.values,
        x=[f"{hour:02d}:00" for hour in pivot_table.columns],
        y=pivot_table.index,
        colorscale='Viridis',
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Engagement Rate by Hour and Content Type",
        xaxis_title="Hour of Day",
        yaxis_title="Content Type",
        height=300
    )
    return fig

def main():
    # Load data
    df = load_data()
    
    # Sidebar filters
    with st.sidebar:
        st.title("📊 Dashboard Controls")
        
        # Date range filter
        st.subheader("📅 Date Range")
        date_range = st.date_input(
            "Select period",
            value=(df['Post_Date'].min().date(), df['Post_Date'].max().date()),
            min_value=df['Post_Date'].min().date(),
            max_value=df['Post_Date'].max().date()
        )
        
        # Post type filter
        st.subheader("🏷️ Content Type")
        selected_types = st.multiselect(
            "Select content types",
            options=df['Post_Type'].unique(),
            default=df['Post_Type'].unique()
        )
    
    # Apply filters
    mask = (
        (df['Post_Date'].dt.date >= date_range[0]) &
        (df['Post_Date'].dt.date <= date_range[1]) &
        (df['Post_Type'].isin(selected_types))
    )
    filtered_df = df[mask]
    
    # Main dashboard
    st.title("📱 Social Media Analytics Dashboard")
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    metrics = {
        "Total Posts": len(filtered_df),
        "Total Engagement": f"{filtered_df['Total_Engagement'].sum():,}",
        "Avg. Engagement Rate": f"{filtered_df['Engagement_Rate'].mean():.1f}%",
        "Best Performing Type": filtered_df.groupby('Post_Type')['Engagement_Rate'].mean().idxmax()
    }
    
    for col, (metric, value) in zip([col1, col2, col3, col4], metrics.items()):
        with col:
            st.metric(label=metric, value=value, delta=f"{value} from previous period", delta_color="inverse")
    
    # First row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Content Type Distribution")
        fig_dist = px.pie(filtered_df, names='Post_Type', values='Total_Engagement',
                         color='Post_Type', hole=0.4,
                         color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        st.plotly_chart(fig_dist, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.subheader("Engagement by Content Type")
        fig_engage = px.bar(filtered_df.groupby('Post_Type').agg({
            'Likes': 'mean',
            'Comments': 'mean',
            'Shares': 'mean'
        }).reset_index(),
            x='Post_Type',
            y=['Likes', 'Comments', 'Shares'],
            barmode='group',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'])
        st.plotly_chart(fig_engage, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Time-based analysis
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Posting Time Analysis")
    time_heatmap = create_time_heatmap(filtered_df)
    st.plotly_chart(time_heatmap, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Engagement trends
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Engagement Trends Over Time")
    
    # Create subplot with two y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add traces
    fig.add_trace(
        go.Scatter(x=filtered_df['Post_Date'], y=filtered_df['Likes'],
                  name="Likes", line=dict(color='#FF6B6B')),
        secondary_y=False,
    )
    
    fig.add_trace(
        go.Scatter(x=filtered_df['Post_Date'], y=filtered_df['Engagement_Rate'],
                  name="Engagement Rate", line=dict(color='#45B7D1')),
        secondary_y=True,
    )
    
    fig.update_layout(
        height=400,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Likes", secondary_y=False)
    fig.update_yaxes(title_text="Engagement Rate (%)", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Detailed data table
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    st.subheader("Detailed Analytics")
    
    # Format the dataframe for display
    display_df = filtered_df.copy()
    display_df['Post_Date'] = display_df['Post_Date'].dt.strftime('%Y-%m-%d')
    display_df['Engagement_Rate'] = display_df['Engagement_Rate'].round(2).astype(str) + '%'
    
    st.dataframe(
        display_df[['Post_ID', 'Post_Type', 'Post_Date', 'Post_Time', 
                   'Likes', 'Comments', 'Shares', 'Engagement_Rate']],
        height=400
    )
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()