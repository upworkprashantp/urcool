import streamlit as st
from .helpers import synchroninze_db


def side_nav():
    synchroninze_db("urcool", "db.csv")  # synchronize db across users
    return st.sidebar.selectbox(label="Navigation", options=("About", "Friends", "Profile"))  # return current page
