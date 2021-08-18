import streamlit as st
import pandas as pd
from Actions.components import side_nav
from Actions.helpers import set_page, update_db, update_notifications, update_data


class Profile:
    def __init__(self):
        page = side_nav()

        user = st.session_state.current_user
        db = st.session_state.db
        notifications = st.session_state.notifications

        # display user's name
        st.title(user.Name.item())
        # invite code
        st.caption(f"Invite code: {user.InviteCode.item()}")
        # show user info
        viz_user = self.user_info(user)
        st.write(viz_user)
        # edit expander
        category, delta = self.change_info(viz_user)
        if category:
            user.loc[user.index, category] = delta
        # requests
        st.title("Requests")
        requests = notifications[notifications["Recipient"] == user.ID.item()]  # get requests for current user
        st.write(db[db.ID.isin(requests.Sender.unique())][["Name", "City", "State"]])
        self.add_friend(requests, user, db)

        set_page(page)

    def user_info(self, user):
        viz_user = pd.concat([user.Name, user.Email, user.Phone, user.City, user.State], axis=1)
        viz_user.columns = ["Name", "Email", "Phone", "City", "State"]
        viz_user.index = user.index
        return viz_user

    def add_friend(self, requests, user, db):
        #  make expander and form with selectbox of Friend Requesters
        expander = st.expander("Answer requests")
        form = expander.form("Answer_requests")
        col1, col2 = form.beta_columns(2)
        name = col1.selectbox("People", requests.SenderName.unique())

        def confirm_request():
            if name:
                # get sender in notifications
                sender = requests[requests == name]
                # add user to graph
                G = st.session_state.graph
                G.add_edge(user.ID.item(), requests.Sender.item())
                st.session_state.graph = G
                # add both users to firsts
                db.at[user.index.item(), "First"] += f",{requests.Sender.item()}"
                db.at[sender.index.item(), "First"] += f",{user.ID.item()}"
                st.session_state.db = db
                update_db()
                update_data("db.csv")
                # remove notification
                notifications = st.session_state.notifications
                notifications.drop(sender.index, inplace=True)
                st.session_state.notifications = notifications
                update_notifications()
                update_data("notifications.csv")

        submit = col2.form_submit_button("Add")
        if submit:
            confirm_request()

    def change_info(self, viz_user):
        expander = st.expander("Edit your info")
        form = expander.form("edit")
        col1, col2 = form.beta_columns(2)
        cat = col1.selectbox("Column", viz_user.columns.unique())  # category to change
        info = col2.text_input("New info")

        def update():
            st.session_state.db.loc[viz_user.index, cat] = info
            if info:
                update_db()
                update_data("db.csv")
        submit = form.form_submit_button("Submit", on_click=update())
        if submit and info:
            st.success("Data changed. Reselect the Page in Navigation to view.")
            return cat, info
        else:
            return None, None


