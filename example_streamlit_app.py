"""
Example Streamlit App - My New Website
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page configuration
st.set_page_config(
    page_title="My New Website",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("🚀 Welcome to My New Website")
st.markdown("This is a complete example of setting up a new website on Streamlit Cloud")

# Sidebar
st.sidebar.header("Navigation")
page = st.sidebar.selectbox(
    "Choose a page:",
    ["Home", "Data Visualization", "Forms", "About"]
)

if page == "Home":
    st.header("🏠 Home Page")
    
    # Two columns layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Features")
        st.markdown("""
        - 📊 Interactive data visualization
        - 📝 Form handling
        - 🎨 Beautiful UI components
        - 📱 Responsive design
        - ☁️ Cloud deployment ready
        """)
    
    with col2:
        st.subheader("Quick Stats")
        st.metric("Total Users", "1,234", "+50")
        st.metric("Page Views", "45,678", "+12%")
        st.metric("Conversion Rate", "3.2%", "-0.1%")

elif page == "Data Visualization":
    st.header("📊 Data Visualization")
    
    # Generate sample data
    np.random.seed(42)
    data = pd.DataFrame({
        'Month': pd.date_range('2024-01-01', periods=12, freq='M'),
        'Sales': np.random.randint(1000, 5000, 12),
        'Marketing': np.random.randint(500, 2000, 12)
    })
    
    # Create charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales Over Time")
        fig1 = px.line(data, x='Month', y='Sales', title='Monthly Sales')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("Marketing vs Sales")
        fig2 = px.scatter(data, x='Marketing', y='Sales', 
                         title='Marketing Spend vs Sales')
        st.plotly_chart(fig2, use_container_width=True)
    
    # Data table
    st.subheader("Raw Data")
    st.dataframe(data, use_container_width=True)

elif page == "Forms":
    st.header("📝 Forms & Input")
    
    with st.form("contact_form"):
        st.subheader("Contact Us")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="Enter your name")
            email = st.text_input("Email", placeholder="your@email.com")
        
        with col2:
            age = st.number_input("Age", min_value=18, max_value=100, value=25)
            country = st.selectbox("Country", ["USA", "Canada", "UK", "Germany", "France"])
        
        message = st.text_area("Message", placeholder="Tell us what you think...")
        
        newsletter = st.checkbox("Subscribe to newsletter")
        
        submitted = st.form_submit_button("Send Message")
        
        if submitted:
            st.success("✅ Form submitted successfully!")
            st.json({
                "name": name,
                "email": email,
                "age": age,
                "country": country,
                "message": message,
                "newsletter": newsletter
            })

elif page == "About":
    st.header("ℹ️ About This Website")
    
    st.markdown("""
    ## 🎯 Purpose
    This website demonstrates how to create and deploy a complete Streamlit application on Streamlit Cloud.
    
    ## 🛠️ Technologies Used
    - **Streamlit** - Web app framework
    - **Plotly** - Interactive charts
    - **Pandas** - Data manipulation
    - **NumPy** - Numerical computing
    
    ## 🚀 Deployment
    This app is deployed on Streamlit Cloud, which provides:
    - Free hosting
    - Automatic updates from GitHub
    - HTTPS by default
    - Global CDN
    
    ## 📚 Features Demonstrated
    - Multi-page navigation
    - Interactive data visualization
    - Form handling with validation
    - Responsive layout
    - Session state management
    """)
    
    # Contact info
    st.subheader("📞 Contact Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Email**\n\ncontact@mywebsite.com")
    
    with col2:
        st.markdown("**Phone**\n\n+1 (555) 123-4567")
    
    with col3:
        st.markdown("**Address**\n\n123 Main St\nNew York, NY 10001")

# Footer
st.markdown("---")
st.markdown(
    "Made with ❤️ using [Streamlit](https://streamlit.io) | "
    "Deployed on [Streamlit Cloud](https://streamlit.io/cloud)"
)
