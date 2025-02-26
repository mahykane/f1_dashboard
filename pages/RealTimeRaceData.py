import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime


def fetch_car_data(session_key, driver_number):
    url = f'https://api.openf1.org/v1/car_data?session_key={session_key}&driver_number={driver_number}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data: {response.status_code}")
        return []

def fetch_latest_session_key():
    url = 'https://api.openf1.org/v1/sessions?latest=true'
    response = requests.get(url)
    if response.status_code == 200:
        sessions = response.json()
        if sessions:
            return sessions[0]['session_key']
    st.error("No active session found.")
    return None


def main():
    st.title("Real-Time F1 Car Speed Dashboard")

    # Sidebar for user inputs
    st.sidebar.header("Configuration")
    driver_number = st.sidebar.text_input("Driver Number", value="44")  # Default to driver number 55
    update_interval = st.sidebar.slider("Update Interval (seconds)", 1, 10, 5)

    # Fetch the latest session key
    session_key = fetch_latest_session_key()
    if not session_key:
        st.stop()

    # Initialize the data container
    speed_data = pd.DataFrame(columns=['Time', 'Speed'])

    # Create a placeholder for the line chart
    chart_placeholder = st.empty()

    # Real-time data fetching and updating
    while True:
        new_data = fetch_car_data(session_key, driver_number)
        if new_data:
            # Process and append new data
            for entry in new_data:
                time_stamp = datetime.fromisoformat(entry['date'])
                speed = entry['speed']
                speed_data = speed_data.append({'Time': time_stamp, 'Speed': speed}, ignore_index=True)

            # Update the line chart
            with chart_placeholder.container():
                st.line_chart(speed_data.set_index('Time'))

        # Wait for the next update
        time.sleep(update_interval)

if __name__ == "__main__":
    main()