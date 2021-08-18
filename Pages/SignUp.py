import streamlit as st
import pandas as pd
import datetime
import geocoder
from Actions.helpers import generate_code, list_states, set_page, update_db, get_location, get_time, update_data, \
    synchroninze_db


class SignUp:
    def __init__(self):
        synchroninze_db("urcool", "db.csv")  # synchronize db across users
        db = st.session_state.db
        st.title("Sign Up")
        form = st.form(key='SignUp')
        email = form.text_input(label='Email')
        password = form.text_input(label='Password', type="password")
        confirm = form.text_input(label='Confirm Password', type="password")
        name = form.text_input(label='Name')
        phone = form.text_input(label='Phone Number')
        state = form.selectbox(label='Home State', options=list_states())
        city = form.text_input(label='Home City')
        code = form.text_input(label='Code')
        submit_button = form.form_submit_button(label='Submit')
        if submit_button and email and password and confirm and name and phone and state and city and code:
            self.validate_user(db, email=email, password=password, confirm=confirm, name=name, phone=phone, state=state,
                               city=city, code=code)
        login = st.button(label="Login")
        if login:
            set_page("Login")

    def validate_user(self, db, **kwargs):
        login_time = get_time()
        inviter = db[db.InviteCode == int(kwargs["code"])]
        if kwargs["password"] != kwargs["confirm"]:
            # check if passwords match
            st.warning("Passwords did not match.")
        elif inviter.empty:
            # check if new user has a real code
            st.warning("No matching code found")
        else:
            # create new user and add to db
            place, latlng = get_location()
            info = {"Name": kwargs["name"], "ID": kwargs["code"], "Email": kwargs["email"], "Password": kwargs["password"],
                    "Phone": kwargs["phone"], "City": kwargs["city"], "State": kwargs["state"], "CurrentLocation": place,
                    "CurrentLat": latlng[0],  "CurrentLng": latlng[1], "InviteCode": generate_code(), "LastInvite": "",
                    "InvitedBy": inviter["ID"], "Notifications": "", "LastLogin": login_time, "FirstLogin": 1, "First": inviter.ID}
            new_user = pd.DataFrame(info)
            # store user in session state
            st.session_state.current_user = new_user
            # set new invitation code for inviter
            db.loc[inviter.index, "InviteCode"] = generate_code()  # give inviter new code
            db.loc[inviter.index, "LastInvite"] = login_time  # record last time inviter added someone
            db = db.append(new_user, ignore_index=True)
            st.session_state.db = db
            update_db()
            update_data("db.csv")
            set_page("About")
