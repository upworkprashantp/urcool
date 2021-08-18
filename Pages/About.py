import streamlit as st
from Actions.components import side_nav
from Actions.helpers import set_page, update_db, update_data


def about():
    page = side_nav()
    st.title("About")

    st.write("Hi! Someone I love thinks you're cool. ")
    if st.session_state.current_user.FirstLogin.item() == 1:
        del_butt = st.button("Thanks but no thanks, this isn't for me.")
        if del_butt:
            st.session_state.db.drop(st.session_state.current_user.index, inplace=True)
            update_db()
            update_data("db.csv")
            set_page("Login")
        st.session_state.db.loc[st.session_state.current_user.index, "FirstLogin"] = 0
    set_page(page)
