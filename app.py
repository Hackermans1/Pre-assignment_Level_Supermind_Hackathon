import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import requests
import json
import warnings
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get credentials from environment variables
BASE_API_URL = os.getenv("BASE_API_URL")
LANGFLOW_ID = os.getenv("LANGFLOW_ID")
FLOW_ID = os.getenv("FLOW_ID")
APPLICATION_TOKEN = os.getenv("APPLICATION_TOKEN")
ENDPOINT = FLOW_ID

# Validate environment variables
if not all([BASE_API_URL, LANGFLOW_ID, FLOW_ID, APPLICATION_TOKEN]):
    st.error("""
    Missing required environment variables. Please check your .env file.
    Required variables:
    - BASE_API_URL
    - LANGFLOW_ID
    - FLOW_ID
    - APPLICATION_TOKEN
    """)
    st.stop()


def run_flow(message: str,
             endpoint: str = ENDPOINT,
             output_type: str = "chat",
             input_type: str = "chat",
             tweaks: dict = None) -> dict:
    """Run the Langflow RAG endpoint with the given message."""
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{endpoint}"
    
    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    
    if tweaks:
        payload["tweaks"] = tweaks
    
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Show debug information in expander
        with st.expander("Debug Information", expanded=False):
            st.write("API URL:", api_url)
            st.write("Payload:", payload)
        
        response = requests.post(api_url, json=payload, headers=headers)
        
        with st.expander("Response Information", expanded=False):
            st.write("Response Status Code:", response.status_code)
        
        if response.status_code == 401:
            st.error("Authentication failed. Please check your APPLICATION_TOKEN in .env file.")
            return None
        elif response.status_code == 404:
            st.error("Endpoint not found. Please check your LANGFLOW_ID and FLOW_ID in .env file.")
            return None
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with Langflow: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            with st.expander("Error Details", expanded=False):
                st.write("Response content:", e.response.content)
        return None

# [Rest of the Streamlit app code remains the same]



# Replace generate_sample_data() with data loading from API
st.title("Social Media Analytics Dashboard")

# Add a loading state
with st.spinner('Loading data...'):
    df = pd.read_csv("jk.csv")
if df is None:
    st.error("Could not load data. Please check your API configuration.")
    st.stop()

# Display data refresh button in sidebar
if st.sidebar.button("Refresh Data"):
    with st.spinner('Refreshing data...'):
        df = pd.read_csv("jk.csv")




# Generate sample data if needed
# def generate_sample_data():
#     dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
#     Post_Types = ['Carousel', 'Reel', 'Static']
    
#     data = []
#     for date in dates:
#         for Post_Type in Post_Types:
#             data.append({
#                 'date': date,
#                 'Post_Type': Post_Type,
#                 'Likes': random.randint(100, 1000),
#                 'Comments': random.randint(10, 100),
#                 'Shares': random.randint(5, 50),
#                 'engagement_rate': random.uniform(1.0, 5.0)
#             })
    
#     return pd.DataFrame(data)

# Setup page config
st.set_page_config(page_title="Social Media Analytics Dashboard", layout="wide")

# Add debug section in sidebar
if st.sidebar.checkbox("Show Debug Info"):
    st.sidebar.write("API Configuration:")
    st.sidebar.write(f"LANGFLOW_ID: {LANGFLOW_ID[:8]}...")
    st.sidebar.write(f"FLOW_ID: {FLOW_ID[:8]}...")
    st.sidebar.write(f"Token exists: {'Yes' if APPLICATION_TOKEN else 'No'}")
    
    # Test API connection button
    if st.sidebar.button("Test API Connection"):
        test_response = run_flow("test")
        if test_response:
            st.sidebar.success("API connection successful!")
        else:
            st.sidebar.error("API connection failed!")

# Load or generate data
# df = generate_sample_data()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Data Explorer", "Chat with Data"])

if page == "Dashboard":
    st.title("Social Media Analytics Dashboard")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Posts", len(df))
    with col2:
        st.metric("Avg. Likes", int(df['Likes'].mean()))
    with col3:
        st.metric("Avg. Comments", int(df['Comments'].mean()))
    with col4:
        st.metric("Avg. Engagement Rate", f"{df['engagement_rate'].mean():.2f}%")
    
    # [Rest of the Dashboard code]

elif page == "Data Explorer":
    st.title("Data Explorer")
    # [Rest of the Data Explorer code]

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
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from Langflow RAG
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
            # Extract the response content from the Langflow response
            response_content = response.get('response', 'Sorry, I could not process your request.')
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response_content})
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.markdown(response_content)
        else:
            st.error("Failed to get a response from the chat system.")

# Add CSS to improve the look
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)