import streamlit as st
import pandas as pd
import plotly.express as px
from langflow.load import run_flow_from_json
from pathlib import Path
import json

# Configure Streamlit page
st.set_page_config(page_title="Data Analytics & Chatbot", layout="wide")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Define Langflow tweaks
TWEAKS = {
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

def load_data():
    """Load and cache the dataset"""
    try:
        df = pd.read_csv('data.csv')  # Replace with your CSV file path
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def create_analytics_dashboard(df):
    """Create analytics visualizations"""
    st.header("Data Analytics Dashboard")
    
    # Display basic statistics
    st.subheader("Data Overview")
    st.write(f"Total Records: {len(df)}")
    
    # Create columns for side-by-side metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Columns", len(df.columns))
    with col2:
        st.metric("Numeric Columns", len(df.select_dtypes(include=['float64', 'int64']).columns))
    with col3:
        st.metric("Text Columns", len(df.select_dtypes(include=['object']).columns))
    
    # Create visualizations based on data types
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
    
    if len(numeric_cols) > 0:
        st.subheader("Distribution Analysis")
        selected_col = st.selectbox("Select column for histogram:", numeric_cols)
        fig = px.histogram(df, x=selected_col, title=f"Distribution of {selected_col}")
        st.plotly_chart(fig, use_container_width=True)
        
        if len(numeric_cols) > 1:
            st.subheader("Correlation Analysis")
            x_col = st.selectbox("Select X axis:", numeric_cols, key='x_axis')
            y_col = st.selectbox("Select Y axis:", numeric_cols, key='y_axis')
            fig = px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
            st.plotly_chart(fig, use_container_width=True)

def chat_interface():
    """Create the chatbot interface"""
    st.header("Data Chatbot")
    
    # Chat input
    user_input = st.text_input("Ask a question about your data:", key="user_input")
    
    if user_input:
        try:
            # Run the Langflow pipeline
            response = run_flow_from_json(
                flow="Untitled document.json",
                input_value=user_input,
                session_id=st.session_id,
                fallback_to_env_vars=True,
                tweaks=TWEAKS
            )
            
            # Add to chat history
            st.session_state.chat_history.append({"user": user_input, "bot": response})
        
        except Exception as e:
            st.error(f"Error processing request: {e}")
    
    # Display chat history
    st.subheader("Chat History")
    for chat in st.session_state.chat_history:
        st.text_area("You:", chat["user"], height=50, disabled=True)
        st.text_area("Bot:", chat["bot"], height=100, disabled=True)
        st.markdown("---")

def main():
    """Main application"""
    st.title("Data Analytics & Chatbot Application")
    
    # Create sidebar for navigation
    page = st.sidebar.radio("Navigate to:", ["Analytics Dashboard", "Chatbot"])
    
    if page == "Analytics Dashboard":
        df = load_data()
        if df is not None:
            create_analytics_dashboard(df)
    else:
        chat_interface()

if __name__ == "__main__":
    main()