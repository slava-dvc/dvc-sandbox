import streamlit as st
import os
from app.dashboard.navigation import show_navigation

# Set local development mode for mock data
os.environ['LOCAL_DEV'] = 'True'

st.set_page_config(
    page_title="DVC Portfolio Dashboard",
    layout='wide',
    page_icon = "resources/favicon.png"
)


def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Google", on_click=st.login, width=192)


def is_email_allowed():
    email = st.user.email
    return email.endswith('davidovs.com')


def handle_not_authorized():
    st.navigation.hidden = True
    st.error("You are not authorized to access this app.")
    st.write("Sorry, your email address is not authorized to access this dashboard.")
    st.write("Please contact the administrator if you believe this is an error.")
    st.button("Log out", on_click=st.logout, width=192)

st.markdown("""<style> div[data-testid="stMainBlockContainer"] { width: 100% !important; padding: 3rem !important; } </style>""", unsafe_allow_html=True)

def main():
    """Main entry point for the Streamlit app"""
    # Bypass authentication for local development
    LOCAL_DEV = True  # Set to False when deploying to production

    if LOCAL_DEV:
        show_navigation()
    else:
        if not st.user.is_logged_in:
            login_screen()
        elif not is_email_allowed():
            handle_not_authorized()
        else:
            show_navigation()

if __name__ == "__main__":
    main()
