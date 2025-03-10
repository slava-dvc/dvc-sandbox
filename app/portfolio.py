import sys
import streamlit as st
from pathlib import Path
from app.integrations import airtable


def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Google", on_click=st.login)


def is_email_allowed():
    email = st.experimental_user.email
    return email == 'galilei.mail@gmail.com' or email.endswith('davidovs.com')


if not st.experimental_user.is_logged_in:
    login_screen()
elif not is_email_allowed():
    st.error("You are not authorized to access this app.")
    st.write("Sorry, your email address is not authorized to access this dashboard.")
    st.write("Please contact the administrator if you believe this is an error.")
    st.button("Log out", on_click=st.logout)
else:
    st.header(f"Welcome, {st.experimental_user.name}!")
    st.text(f"You are logged in as {st.experimental_user.email}")
    st.button("Log out", on_click=st.logout)
