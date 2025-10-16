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

# Global CSS overrides for Streamlit dialog positioning issues
st.markdown("""
<style>
/* Override Streamlit's internal st-dg class */
.st-dg {
    min-height: auto !important;
    width: auto !important;
    height: auto !important;
}

/* Override Streamlit's internal st-dn class */
.st-dn {
    padding-top: 0 !important;
}

/* Ensure proper dialog positioning */
[data-testid="stDialog"] {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    z-index: 9999 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Dialog content styling */
[data-testid="stDialog"] > div {
    width: min(750px, 90vw) !important; /* Medium width for better UX */
    height: fit-content !important;
    background: white !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2) !important;
    margin: 0 !important;
    position: relative !important;
}

/* Create backdrop overlay */
[data-testid="stDialog"]::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    z-index: -1;
}

/* Textarea styling */
[data-testid="stDialog"] textarea {
    width: 100% !important;
    resize: vertical !important;
    min-height: 120px !important;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    [data-testid="stDialog"] > div {
        width: 95vw !important;
        max-width: 95vw !important;
        margin: 10px !important;
    }
}
</style>
""", unsafe_allow_html=True)

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
