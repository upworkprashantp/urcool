import streamlit as st
from .helpers import set_page


def side_nav():
    cp = st.session_state.current_page
    page = st.sidebar.selectbox(label="Navigation", options=("About", "Friends", "Profile"))
    return page