import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from dotenv import load_dotenv
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API credentials from environment variables with default values
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "486732ff-a748-4b68-a48b-e617028e9db9"
FLOW_ID = "d343821e-7751-4215-8afd-11f1071fd651"
APPLICATION_TOKEN = os.getenv("APPLICATION_TOKEN")
ENDPOINT = FLOW_ID

def run_flow(message, tweaks):
    """
    Run the langflow pipeline with the given message and tweaks.
    
    Args:
        message (str): The user's input message
        tweaks (dict): Configuration parameters for the flow
        
    Returns:
        dict: The response from the API
    """
    try:
        if not APPLICATION_TOKEN:
            raise ValueError("APPLICATION_TOKEN is not set in environment variables")

        headers = {
            "Authorization": f"Bearer {APPLICATION_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input_value": message,
            "output_type": "chat",
            "input_type": "chat",
            "tweaks": tweaks
        }

        logger.info(f"Payload: {payload}")

        
        response = requests.post(
            f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{ENDPOINT}",
            headers=headers,
            json=payload,
            timeout=30  # Add timeout
        )
        
        if response.status_code == 500:
            logger.error("Internal server error from API")
            return {"response": "The server encountered an internal error. Please try again later."}
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        return {"response": "The request timed out. Please try again."}
    except requests.exceptions.RequestException as e:
        logger.error(f"API Error: {str(e)}")
        return {"response": "Sorry, there was an error connecting to the API."}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"response": "An unexpected error occurred. Please try again."}

# Setup page config
st.set_page_config(page_title="Social Media Analytics Dashboard", layout="wide")

# Load the CSV file
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def load_data():
    try:
        df = pd.read_csv('jk.csv')
        df['Post_Date'] = pd.to_datetime(df['Post_Date'])
        return df
    except FileNotFoundError:
        logger.error("jk.csv file not found")
        raise FileNotFoundError("Data file 'jk.csv' not found. Please ensure it exists in the current directory.")
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}")
        raise Exception(f"Error loading data: {str(e)}")

try:
    df = load_data()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard", "Detailed Analysis", "Chat with Data"])

    # Date range selector in sidebar
    st.sidebar.title("Date Range")
    min_date = df['Post_Date'].min()
    max_date = df['Post_Date'].max()
    
    start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

    # Filter data based on date range
    mask = (df['Post_Date'].dt.date >= start_date) & (df['Post_Date'].dt.date <= end_date)
    filtered_df = df.loc[mask]

    if page == "Dashboard":
        st.title("Social Media Analytics Dashboard")
        
        # Key Metrics Row
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Posts", len(filtered_df))
        with col2:
            st.metric("Avg Likes", f"{filtered_df['Likes'].mean():,.0f}")
        with col3:
            st.metric("Avg Comments", f"{filtered_df['Comments'].mean():,.0f}")
        with col4:
            st.metric("Avg Shares", f"{filtered_df['Shares'].mean():,.0f}")
        with col5:
            st.metric("Avg Views", f"{filtered_df['Views'].mean():,.0f}")

        # Engagement by Post Type
        st.subheader("Engagement by Post Type")
        col1, col2 = st.columns(2)
        
        with col1:
            metric = st.selectbox("Select Metric", ['Likes', 'Comments', 'Shares', 'Views'])
            fig = px.bar(
                filtered_df.groupby('Post_Type')[metric].mean().reset_index(),
                x='Post_Type',
                y=metric,
                title=f'Average {metric.capitalize()} by Post Type',
                color='Post_Type'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Post Type Distribution
            fig = px.pie(
                filtered_df,
                names='Post_Type',
                title='Post Type Distribution',
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)

        # Time Series Analysis
        st.subheader("Engagement Trends Over Time")
        metrics = st.multiselect(
            "Select Metrics to Display",
            ['Likes', 'Comments', 'Shares', 'Views'],
            default=['Likes']
        )
        
        fig = go.Figure()
        for metric in metrics:
            daily_avg = filtered_df.groupby('Post_Date')[metric].mean()
            fig.add_trace(go.Scatter(
                x=daily_avg.index,
                y=daily_avg.values,
                name=metric.capitalize(),
                mode='lines+markers'
            ))
        fig.update_layout(title="Daily Engagement Metrics")
        st.plotly_chart(fig, use_container_width=True)

    elif page == "Detailed Analysis":
        st.title("Detailed Analysis")
        
        # Correlation Analysis
        st.subheader("Engagement Metrics Correlation")
        correlation = filtered_df[['Likes', 'Comments', 'Shares', 'Views']].corr()
        fig = px.imshow(
            correlation,
            aspect='auto',
            color_continuous_scale='RdBu'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Engagement Distribution
        st.subheader("Engagement Metrics Distribution")
        metric = st.selectbox("Select Metric to Analyze", ['Likes', 'Comments', 'Shares', 'Views'])
        
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(
                filtered_df,
                x=metric,
                color='Post_Type',
                title=f'{metric.capitalize()} Distribution'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.box(
                filtered_df,
                x='Post_Type',
                y=metric,
                title=f'{metric.capitalize()} by Post Type'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Top Posts Analysis
        st.subheader("Top Performing Posts")
        metric_for_top = st.selectbox("Select Metric for Top Posts", ['Likes', 'Comments', 'Shares', 'Views'])
        top_n = st.slider("Number of top posts to show", 5, 20, 10)
        
        top_posts = filtered_df.nlargest(top_n, metric_for_top)
        fig = px.bar(
            top_posts,
            x='Post_ID',
            y=metric_for_top,
            color='Post_Type',
            title=f'Top {top_n} Posts by {metric_for_top.capitalize()}'
        )
        st.plotly_chart(fig, use_container_width=True)

    elif page == "Chat with Data":
        st.title("Chat with Your Data")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about your social media data"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.spinner("Thinking..."):
                response = run_flow(
                    message=prompt,
                    tweaks={
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
                )
            
            if response:
                response_content = response.get('response', 'Sorry, I could not process your request.')
                st.session_state.messages.append({"role": "assistant", "content": response_content})
                with st.chat_message("assistant"):
                    st.markdown(response_content)

except Exception as e:
    st.error(f"Error loading or processing data: {str(e)}")
    st.info("Please ensure your data file 'jk.csv' exists and is properly formatted.")

# Add CSS for styling
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)