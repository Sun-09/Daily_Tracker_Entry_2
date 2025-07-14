import streamlit as st
import json
import os
import plotly.graph_objs as go
from datetime import datetime

# Load users from Streamlit Secrets
users = json.loads(st.secrets["users"])

# Authenticate user
if "authenticated" not in st.session_state:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.success(f"Welcome {username}!")
            st.rerun()
        else:
            st.error("Invalid credentials.")
    st.stop()

# If logged in, continue with app
st.title("📊 Daily Input Tracker")

DATA_DIR = "user_data"
os.makedirs(DATA_DIR, exist_ok=True)

user_file = os.path.join(DATA_DIR, f"{st.session_state['username']}.json")

def load_user_data():
    if os.path.exists(user_file):
        with open(user_file, 'r') as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(user_file, 'w') as f:
        json.dump(data, f, indent=4)

data = load_user_data()

today_str = datetime.now().strftime("%Y-%m-%d")

st.subheader("Enter today's data")

number = st.number_input("Enter the number (up to two decimal places):", format="%.2f")
yes_no = st.toggle("Click on yes/no")

if st.button("Submit"):
    if today_str not in data:
        data[today_str] = {"value": number, "yes": yes_no}
        save_user_data(data)
        st.success("Data saved!")
    else:
        st.warning("You have already submitted for today.")

# Pagination for plotting
st.subheader("🗕️ 7-Day View")
dates = sorted(data.keys())
view_size = 7
page = st.number_input("Page:", min_value=1, max_value=max(1, (len(dates) + view_size - 1) // view_size), step=1)

start_idx = (page - 1) * view_size
end_idx = start_idx + view_size
selected_dates = dates[start_idx:end_idx]

values = [data[d].get("value", 0) for d in selected_dates if "value" in data[d]]
colors = ['green' if data[d].get("yes") else 'red' for d in selected_dates if "value" in data[d]]
selected_dates = [d for d in selected_dates if "value" in data[d]]

colors = ['green' if data[d]['yes'] else 'red' for d in selected_dates]

fig = go.Figure(data=[
    go.Bar(x=selected_dates, y=values, marker_color=colors)
])

fig.update_layout(
    title="Number vs Date",
    xaxis_title="Date",
    yaxis_title="Number",
    template="plotly_white"
)

st.plotly_chart(fig)
