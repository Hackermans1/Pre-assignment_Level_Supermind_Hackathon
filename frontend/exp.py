import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Social Media Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    backgroundColor="#222222"

    .metric-card {
        background: ##222222;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .stMetric {
        background-color: ##291616;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    .chart-container {
        background: ##222222;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    </style>
""", unsafe_allow_html=True)

def load_data():
    # Sample data generation with more realistic values
    df = pd.read_csv("esme.csv")
    df['Post_Date'] = pd.to_datetime(df['Post_Date'])
    
    # Add engagement rate calculation
    df['Engagement_Rate'] = ((df['Likes'] + df['Comments'] + df['Shares']) / 
                            df.groupby('Post_Type')['Likes'].transform('mean') * 100)
    return df

def main():
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = load_data()
    
    # Sidebar filters
    st.sidebar.title("📊 Dashboard Controls")
    
    # Date range filter
    st.sidebar.subheader("📅 Date Range")
    date_range = st.sidebar.date_input(
        "Select period",
        value=(
            st.session_state.data['Post_Date'].min(),
            st.session_state.data['Post_Date'].max()
        ),
        min_value=pd.to_datetime(st.session_state.data['Post_Date'].min()).date(),
        max_value=pd.to_datetime(st.session_state.data['Post_Date'].max()).date()
    )
    
    # Post type filter with "Select All" option
    st.sidebar.subheader("🏷️ Post Types")
    all_types = st.session_state.data['Post_Type'].unique().tolist()
    selected_types = st.sidebar.multiselect(
        "Select post types",
        options=['All'] + all_types,
        default=['All']
    )
    
    if 'All' in selected_types:
        selected_types = all_types
    
    # Time of day analysis
    st.sidebar.subheader("⏰ Time Analysis")
    show_time_analysis = st.sidebar.checkbox("Show posting time analysis")
    
    # Apply filters
    mask = (
        (pd.to_datetime(st.session_state.data['Post_Date']).dt.date >= date_range[0]) &
        (pd.to_datetime(st.session_state.data['Post_Date']).dt.date <= date_range[1]) &
        (st.session_state.data['Post_Type'].isin(selected_types))
    )
    filtered_df = st.session_state.data[mask]
    
    # Main dashboard area
    st.title("📱 Social Media Analytics Dashboard")
    st.markdown("---")
    
    # Top metrics row
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        st.metric(
            "Total Posts",
            len(filtered_df),
            delta=f"{len(filtered_df) - len(st.session_state.data[~mask])} from previous period"
        )
    
    with metrics_col2:
        total_engagement = filtered_df['Likes'].sum() + filtered_df['Comments'].sum() + filtered_df['Shares'].sum()
        st.metric(
            "Total Engagement",
            f"{total_engagement:,}",
            delta=f"{filtered_df['Engagement_Rate'].mean():.1f}% avg rate"
        )
    
    with metrics_col3:
        best_post = filtered_df.loc[filtered_df['Engagement_Rate'].idxmax()]
        st.metric(
            "Best Performing Post",
            f"Post {best_post['Post_ID']}",
            delta=f"{best_post['Engagement_Rate']:.1f}% engagement"
        )
    
    with metrics_col4:
        best_time = filtered_df.groupby('Post_Time')['Engagement_Rate'].mean().idxmax()
        st.metric(
            "Best Posting Time",
            best_time,
            delta="Based on engagement"
        )
    
    # Main dashboard sections
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Post Distribution")
        post_dist = filtered_df['Post_Type'].value_counts()
        fig_pie = px.pie(
            values=post_dist.values,
            names=post_dist.index,
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1'],
            hole=0.3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=False, margin=dict(t=0, b=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Add download button for distribution data
        st.download_button(
            "📥 Download Distribution Data",
            post_dist.to_csv().encode('utf-8'),
            "post_distribution.csv",
            "text/csv",
            key='download-dist'
        )
    
    with col2:
        st.subheader("Engagement Trends")
        
        # Add metric selector
        selected_metric = st.selectbox(
            "Select metric to display",
            ['Likes', 'Comments', 'Shares', 'Engagement_Rate'],
            key='metric_selector'
        )
        
        daily_metrics = filtered_df.groupby(['Post_Date', 'Post_Type'])[selected_metric].mean().reset_index()
        
        fig_trend = px.line(
            daily_metrics,
            x='Post_Date',
            y=selected_metric,
            color='Post_Type',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
        )
        
        fig_trend.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#E5E5E5'),
            yaxis=dict(showgrid=True, gridcolor='#E5E5E5')
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    # Time analysis section (conditional)
    if show_time_analysis:
        st.markdown("---")
        st.subheader("📊 Posting Time Analysis")
        
        time_analysis = filtered_df.groupby('Post_Time')['Engagement_Rate'].agg(['mean', 'count']).reset_index()
        
        fig_time = go.Figure(data=[
            go.Bar(
                x=time_analysis['Post_Time'],
                y=time_analysis['mean'],
                marker_color='#4ECDC4',
                name='Engagement Rate'
            ),
            go.Scatter(
                x=time_analysis['Post_Time'],
                y=time_analysis['count'],
                yaxis='y2',
                name='Post Count',
                line=dict(color='#FF6B6B')
            )
        ])
        
        fig_time.update_layout(
            yaxis2=dict(
                overlaying='y',
                side='right',
                title='Number of Posts'
            ),
            yaxis=dict(title='Average Engagement Rate (%)'),
            xaxis=dict(title='Posting Time'),
            showlegend=True,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        st.plotly_chart(fig_time, use_container_width=True)
    
    # Data table with search and filters
    st.markdown("---")
    st.subheader("📋 Detailed Post Analysis")
    
    # Search functionality
    search_term = st.text_input("🔍 Search posts by ID", "")
    if search_term:
        filtered_df = filtered_df[filtered_df['Post_ID'].str.contains(search_term, case=False)]
    
    # Display interactive table
    st.dataframe(
        filtered_df.style.format({
            'Engagement_Rate': '{:.1f}%',
            'Likes': '{:,.0f}',
            'Comments': '{:,.0f}',
            'Shares': '{:,.0f}'
        }),
        height=400
    )
    
    # Download full dataset button
    st.download_button(
        "📥 Download Full Report",
        filtered_df.to_csv().encode('utf-8'),
        "social_media_analytics.csv",
        "text/csv",
        key='download-full'
    )

if __name__ == "__main__":
    main()