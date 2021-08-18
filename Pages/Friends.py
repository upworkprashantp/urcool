import networkx as nx
import streamlit as st
import pandas as pd
import numpy as np
import time
from Actions.components import side_nav
from Actions.helpers import set_page, get_friends_by_distance, update_db, update_notifications, update_data


class Friends:
    def __init__(self):
        page = side_nav()
        # time.sleep(2)
        st.title("Friends")
        db = st.session_state.db
        viz = self.viz_db(db)
        viz = self.filter(viz)
        map_graph = self.map_db(db)
        map_expander = st.expander(label="Map", expanded=False)
        map_expander.map(map_graph)
        self.add_friend(viz)
        st.write(viz.iloc[:, :-2])  # last columns contain IDs and Friends
        set_page(page)

    def viz_db(self, db):
        # database for displaying user info
        viz = pd.concat(
            [db.Name, db.Email, db.Phone, db.InvitedBy, db.CurrentLocation, db.State, db.City, db.ID, db.First], axis=1)
        viz.columns = ["Name", "Email", "Phone", "Invited By", "Last Check-in", "Home State", "Home City", "ID",
                       "First"]
        return viz

    @st.cache
    def map_db(self, db):
        # database for displaying map of users
        map_graph = db[["CurrentLat", "CurrentLng"]].dropna()
        map_graph.columns = ["lat", "lon"]
        return map_graph

    def add_friend(self, viz_db):
        # add friends
        expander = st.expander("Add Friends")
        form = expander.form("Add")
        col1, col2 = form.beta_columns(2)
        # get second degree friends.
        curr_user = st.session_state.current_user
        friends_of_friends = get_friends_by_distance(st.session_state.graph, curr_user.ID.item(), 2, strict=True)
        # allow user to add second degree people
        index = col1.selectbox("ID", viz_db[viz_db["ID"].isin(friends_of_friends)].index,
                               help="ID is the number on the far left of the friends list.")

        def request(index):
            index = int(index)
            notifications = st.session_state.notifications
            #  add row to notifications of df
            new_row = pd.DataFrame(data=[[curr_user.Name.item(), curr_user.ID.item(), viz_db.loc[index, "ID"]]],
                                   columns=["SenderName", "Sender", "Recipient"])
            notifications = notifications.append(new_row, ignore_index=True).dropna()
            #  make sure there aren't any duplicates and add if there's a new request
            notifications = notifications.drop_duplicates()
            if not st.session_state.notifications.equals(notifications):
                st.session_state.notifications = notifications  # update state
                update_notifications()
                update_data("notifications.csv")
        submit = col2.form_submit_button("Send request")

        if submit:
            request(index)

    def filter(self, viz):
        # filter visible df
        expander = st.expander(label="Filter")
        col1, col2 = expander.beta_columns(2)
        col3, col4, col5 = expander.beta_columns(3)
        # options to select from
        state = col1.selectbox("Home State", ["All"] + list(viz["Home State"].dropna().unique()))
        city = col2.selectbox("Home City", ["All"] + list(viz["Home City"].dropna().unique()))
        cur_loc = col3.selectbox("Current Location", ["All"] + list(viz["Last Check-in"].dropna().unique()))
        degree = col4.selectbox("Distance", ["Friends", "Friend of Friends"])
        text = col5.text_input("Name")
        # change selection to universal regex string if selecting "All"
        choices = [state, city, cur_loc, text, degree]
        for i, selection in enumerate(choices):
            if selection == "All":
                choices[i] = ".*"
            elif not selection:
                choices[i] = ".*"
        # get current user ID
        user_ID = st.session_state.current_user.ID.item()
        # get list of friends or friends of friends
        friends = get_friends_by_distance(st.session_state.graph, user_ID, 1) if choices[i] == "Friends" else \
            get_friends_by_distance(st.session_state.graph, user_ID, 2)
        # filter visible df
        return viz[viz["Home State"].str.match(choices[0]) & viz["Home City"].str.match(choices[1])
                   & viz["Last Check-in"].str.match(choices[2]) & viz["Name"].str.match(choices[3])
                   & viz["ID"].isin(friends)]
