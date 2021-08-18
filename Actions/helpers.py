import random
from datetime import datetime
from google.cloud import storage
from google.oauth2 import service_account
import json
import streamlit as st
import geocoder
import networkx as nx
import pandas as pd


def set_page(page):
    st.session_state.current_page = page


def generate_code():
    return ''.join(random.choice('0123456789') for i in range(8))


def list_states():
    return ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA",
            "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
            "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
            "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
            "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]


def update_db():
    st.session_state.db.to_csv("db.csv", index=False)


def update_notifications():
    st.session_state.notifications.to_csv("notifications.csv", index=False)


def get_time():
    return datetime.datetime.utcnow()


def get_location():
    g = geocoder.ip('me')
    return g, g.latlng


def generate_graph():
    G = nx.Graph()
    for i, user in st.session_state.db.iterrows():  # iterate through db
        G.add_node(user.ID, name=user.Name)  # add node with user ID and user Name attribute
        friend_list = user.First.split(',')  # split friend ids into list
        for friend in friend_list:
            G.add_edge(user.ID, friend.strip())  # add edge between friends
    return G


def get_friends_by_distance(G, ID, dist, strict=False):
    if strict:
        friends_1 = nx.single_source_shortest_path_length(G, ID, 1)
        friends_2 = nx.single_source_shortest_path_length(G, ID, 2)
        return list(set(friends_2) - set(friends_1))
    else:
        return list(nx.single_source_shortest_path_length(G, ID, dist))[1:]


# def download_blob(bucket_name, source_blob_name):
#     """Downloads a blob from the google bucket."""
#     # bucket_name = "your-bucket-name"
#     # source_blob_name = "storage-object-name"
#     # destination_file_name = "local/path/to/file"
#
#     # current_directory = os.path.abspath(os.path.dirname(__file__))
#     read_secret()
#     # if public app do
#     try:
#         storage_client = storage.Client.from_service_account_json("./secret.txt")
#     # else load from local
#     except:
#         path_to_service_account_json = os.path.join(current_directory, 'gvdashboards-e481433de9af.json')
#         storage_client = storage.Client.from_service_account_json(path_to_service_account_json)
#
#     bucket = storage_client.bucket(bucket_name)
#
#     # Construct a client side representation of a blob.
#     # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
#     # any content from Google Cloud Storage. As we don't need additional data,
#     # using `Bucket.blob` is preferred here.
#     blob = bucket.get_blob(source_blob_name)
#     return blob


# read secret from streamlit to access data  in bucket
def read_secret():
    try:
        type_ = st.secrets["type"]
        project_id = st.secrets["project_id"]
        private_key_id = st.secrets["private_key_id"]
        private_key = st.secrets["private_key"]
        client_email = st.secrets["client_email"]
        client_id = st.secrets["client_id"]
        auth_uri = st.secrets["auth_uri"]
        token_uri = st.secrets["token_uri"]
        auth = st.secrets["auth_provider_x509_cert_url"]
        client = st.secrets["client_x509_cert_url"]
        dictionary = {type_[0]: type_[1], project_id[0]: project_id[1], private_key_id[0]: private_key_id[1],
                      private_key[0]: private_key[1], client_email[0]: client_email[1], client_id[0]: client_id[1],
                      auth_uri[0]: auth_uri[1], token_uri[0]: token_uri[1], auth[0]: auth[1], client[0]: client[1]}

        return dictionary
    except:
        return service_account.Credentials.from_service_account_file("gvdashboards-e481433de9af.json")


def read_data(bucket_name, source_blob_name):
    # read in data from csv to df
    return pd.read_csv("http://storage.googleapis.com/{}/{}".format(bucket_name, source_blob_name))


def update_data(filename):
    credentials = read_secret()
    client = storage.Client(credentials=credentials, project="gvdashboards")
    bucket = client.get_bucket("urcool")
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)


def synchroninze_db(bucket_name, source_blob_name):
    db = read_data(bucket_name, source_blob_name)
    if not db.equals(st.session_state.db):
        st.session_state.db = db
