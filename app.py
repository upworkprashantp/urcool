import streamlit as st
import pandas as pd
from Pages.Login import Login
from Pages.About import about
from Pages.SignUp import SignUp
from Pages.Friends import Friends
from Pages.Profile import Profile
from Actions.helpers import generate_graph, read_data

st.set_page_config(
    page_title="Urcool",
    page_icon="🕶️",
    initial_sidebar_state="expanded")

st.session_state.db = read_data("urcool", "db.csv")

st.session_state.notifications = read_data("urcool", "notifications.csv")

st.session_state.graph = generate_graph()  # generate friends graph

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Login"

cp = st.session_state.current_page

if cp == "Login":
    Login()
elif cp == "SignUp":
    SignUp()
elif cp == "About":
    about()
elif cp == "Friends":
    Friends()
elif cp == "Profile":
    Profile()