# Core Site

import streamlit as st 

PAGE_DASHBOARD = "Dashboard"
PAGE_LOGIN = "Login"
PAGE_SIGNUP = "Signup"

def run():
    st.set_page_config(
        page_title = "Welcome to the Energy Engine"
    )

    with st.sidebar:
        st.link_button(PAGE_DASHBOARD, "pages/dashboard")
        st.link_button(PAGE_LOGIN, "pages/login")
        st.link_button(PAGE_SIGNUP, "pages/signup")
        

if __name__ == "__main__":
    run()