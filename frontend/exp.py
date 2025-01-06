import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import requests
import json
import os
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "486732ff-a748-4b68-a48b-e617028e9db9"
FLOW_ID = "d343821e-7751-4215-8afd-11f1071fd651"
APPLICATION_TOKEN = os.getenv("APPLICATION_TOKEN")
def validate_api_response(response: requests.Response) -> tuple[bool, str]:
    """
    Validate the API response and return status and message
    """
    try:
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "result" in data:
                return True, "Success"
            return False, "Invalid response format"
        elif response.status_code == 401:
            return False, "Authentication failed. Please check your API token."
        elif response.status_code == 404:
            return False, "API endpoint not found. Please check your configuration."
        else:
            return False, f"API request failed with status code: {response.status_code}"
    except json.JSONDecodeError:
        return False, "Invalid JSON response from API"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def run_chatbot_query(message: str) -> dict:
    """
    Send a message to the chatbot API and get the response with enhanced error handling
    """
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{FLOW_ID}"
    
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "File-jxj7K": {},
            "SplitText-7gH6I": {},
            "ChatInput-Rpb6P": {},
            "ParseData-EJyoR": {},
            "CombineText-GqK4e": {},
            "TextInput-OUxuk": {},
            "GoogleGenerativeAIModel-xLOg8": {},
            "ChatOutput-EPD4q": {},
            "AstraDB-brZ4Z": {}
        }
    }
    
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        with st.spinner("Processing your request..."):
            start_time = time.time()
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            end_time = time.time()
            
            # Validate response
            is_valid, message = validate_api_response(response)
            
            if is_valid:
                response_data = response.json()
                response_data["_metadata"] = {
                    "response_time": round(end_time - start_time, 2),
                    "status_code": response.status_code,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                return response_data
            else:
                return {
                    "error": message,
                    "_metadata": {
                        "response_time": round(end_time - start_time, 2),
                        "status_code": response.status_code,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
    except requests.Timeout:
        return {"error": "Request timed out after 30 seconds"}
    except requests.ConnectionError:
        return {"error": "Failed to connect to the API. Please check your internet connection."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

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
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'api_metrics' not in st.session_state:
        st.session_state.api_metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0
        }

    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = load_data()
    tabs = st.tabs(["📊 Analytics", "💬 Chat Assistant"])
    
    with tabs[0]:

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
    with tabs[1]:
        st.header("💬 Analytics Assistant")
        st.markdown("Ask questions about your social media performance!")
        
        # Chat interface
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**Assistant:** {message['content']}")
        
        # Chat input
        user_message = st.text_input("Type your question here...", key="chat_input")
        
        if st.button("Send", key="send_button"):
            if user_message:
                # Add user message to chat history
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_message
                })
                
                # Get chatbot response
                response = run_chatbot_query(user_message)
                
                if "error" not in response:
                    # Extract the actual response from the API response
                    bot_message = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                    
                    # Add bot response to chat history
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": bot_message
                    })
                else:
                    st.error(f"Error: {response['error']}")
                
                # Clear input
                st.session_state.chat_input = ""
                
                # Rerun to update the chat display
                st.experimental_rerun()
        
        # Add a clear chat button
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.experimental_rerun()

if __name__ == "__main__":
    main()
