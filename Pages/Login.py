import streamlit as st
import datetime
from Actions.helpers import set_page, update_db, get_location, update_data


class Login:
    def __init__(self):
        db = st.session_state.db
        st.title("Login")
        form = st.form(key='Login')
        email = form.text_input(label='Email')
        password = form.text_input(label='Password', type="password")
        submit_button = form.form_submit_button(label='Submit')
        if submit_button and password and email:
            self.validate_user(db, email=email, password=password)
        signup = st.button(label="Not cool yet?")
        if signup:
            set_page("SignUp")

    def validate_user(self, db, **kwargs):
        login_time = datetime.datetime.utcnow()
        user = db[db.Email == kwargs['email']]
        place, latlng = get_location()
        if user.Password.item() == kwargs['password']:
            db.loc[user.index, "LastLogin"] = login_time  # set users login time (row, column, value)
            db.loc[user.index, "CurrentLocation"] = place
            db.loc[user.index, "CurrentLat"] = latlng[0]
            db.loc[user.index, "CurrentLng"] = latlng[1]
            st.session_state.current_user = user
            st.session_state.db = db
            update_db()
            update_data("db.csv")
            set_page("About")
        else:
            st.warning("Incorrect email or password")
