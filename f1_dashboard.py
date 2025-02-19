import streamlit as st
import pandas as pd
import plotly.express as px
import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import os
import numpy as np
from fastf1.ergast import Ergast

# Enable FastF1 caching
if not os.path.exists("cache"):
    os.mkdir("cache")
ff1.Cache.enable_cache("cache")

# Set up FastF1 plotting
plotting.setup_mpl()


def inject_custom_css():
    st.markdown(
        """
        <style>
            /* Main title */
            h1 {
                color: #FF1801;
                font-family: 'Formula1', sans-serif;
                text-align: center;
                font-size: 3rem;
                margin-bottom: 1rem;
            }

            /* Sidebar */
            .css-1d391kg {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border-radius: 10px;
                padding: 1rem;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }

            /* Buttons */
            .stButton button {
                background-color: #FF1801;
                color: #FFFFFF;
                border-radius: 10px;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                transition: background-color 0.3s ease;
            }

            .stButton button:hover {
                background-color: #E51600;
            }

            /* Plotly charts */
            .stPlotlyChart {
                border-radius: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                background-color: #2E2E2E;
                padding: 1rem;
            }

            /* Tables */
            .stDataFrame {
                border-radius: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                background-color: #2E2E2E;
                padding: 1rem;
            }

            /* Custom font */
            @import url('https://fonts.googleapis.com/css2?family=Formula1&display=swap');

            /* Containers */
            .stContainer {
                border-radius: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                background-color: #2E2E2E;
                padding: 1rem;
                margin-bottom: 1rem;
            }

            /* Markdown text */
            .stMarkdown {
                color: #FFFFFF;
            }

            /* Input widgets */
            .stTextInput input, .stSelectbox select, .stNumberInput input {
                background-color: #2E2E2E;
                color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #FF1801;
                padding: 0.5rem;
            }

            /* Sliders */
            .stSlider {
                color: #FF1801;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Function to fetch all races for a given year
def fetch_races(year):
    schedule = ff1.get_event_schedule(year)
    return schedule


# Function to fetch session data for a specific race
def fetch_session_data(year, race_name):
    session = ff1.get_session(year, race_name, "R")  # Race session
    session.load()
    return session


# Function to get driver names with their numbers
def get_driver_names_with_numbers(session):
    drivers = session.drivers
    driver_info = []
    for driver in drivers:
        driver_name = session.get_driver(driver)["FullName"]
        driver_info.append(f"{driver_name} ({driver})")
    return driver_info


# Function to create telemetry plots
def create_telemetry_plots(session, selected_driver_info):
    st.subheader("Telemetry Analysis")
    selected_driver = selected_driver_info.split("(")[-1].strip(")")
    lap = session.laps.pick_driver(selected_driver).pick_fastest()
    tel = lap.get_telemetry()

    # Speed vs Distance
    fig_speed = px.line(
        tel,
        x="Distance",
        y="Speed",
        title=f"Speed vs Distance - {selected_driver_info}",
    )
    st.plotly_chart(fig_speed, use_container_width=True)

    # Throttle vs Distance
    fig_throttle = px.line(
        tel,
        x="Distance",
        y="Throttle",
        title=f"Throttle vs Distance - {selected_driver_info}",
    )
    st.plotly_chart(fig_throttle, use_container_width=True)

    # Brake vs Distance
    fig_brake = px.line(
        tel,
        x="Distance",
        y="Brake",
        title=f"Brake vs Distance - {selected_driver_info}",
    )
    st.plotly_chart(fig_brake, use_container_width=True)

    # Gear Shifts vs Distance
    fig_gear = px.line(
        tel,
        x="Distance",
        y="nGear",
        title=f"Gear Shifts vs Distance - {selected_driver_info}",
    )
    st.plotly_chart(fig_gear, use_container_width=True)

    # DRS Usage
    fig_drs = px.line(
        tel, x="Distance", y="DRS", title=f"DRS Usage - {selected_driver_info}"
    )
    st.plotly_chart(fig_drs, use_container_width=True)


# Function to create lap time analysis
def create_lap_time_analysis(session):
    st.subheader("Lap Time Analysis")
    laps = session.laps
    fig_lap_times = px.line(laps, x="LapNumber", y="LapTime", title="Lap Times")
    st.plotly_chart(fig_lap_times, use_container_width=True)


# Function to create tire usage analysis
def create_tire_usage_analysis(session):
    st.subheader("Tire Usage Analysis")
    laps = session.laps
    fig_tire_usage = px.box(laps, x="Compound", y="LapTime", title="Tire Usage")
    st.plotly_chart(fig_tire_usage, use_container_width=True)


# Function to create sector time analysis
def create_sector_time_analysis(session, selected_driver_info):
    st.subheader("Sector Time Analysis")
    selected_driver = selected_driver_info.split("(")[-1].strip(")")
    laps = session.laps.pick_driver(selected_driver)
    sector_times = laps[["LapNumber", "Sector1Time", "Sector2Time", "Sector3Time"]]
    sector_times_melted = sector_times.melt(
        id_vars=["LapNumber"],
        value_vars=["Sector1Time", "Sector2Time", "Sector3Time"],
        var_name="Sector",
        value_name="Time",
    )
    fig_sector_times = px.line(
        sector_times_melted,
        x="LapNumber",
        y="Time",
        color="Sector",
        title=f"Sector Times - {selected_driver_info}",
    )
    st.plotly_chart(fig_sector_times, use_container_width=True)


# Function to create pit stop analysis
def create_pit_stop_analysis(session):
    st.subheader("Pit Stop Analysis")

    # Get laps data
    laps = session.laps

    # Filter laps where pit stops occurred
    pit_stops = laps[laps["PitInTime"].notna() | laps["PitOutTime"].notna()]

    if not pit_stops.empty:
        # Calculate pit stop duration
        pit_stops["PitDuration"] = pit_stops["PitOutTime"] - pit_stops["PitInTime"]

        # Convert pit duration to seconds
        pit_stops["PitDuration"] = pit_stops["PitDuration"].dt.total_seconds()

        # Group by driver and calculate average pit stop duration
        pit_stop_summary = (
            pit_stops.groupby("Driver")["PitDuration"].mean().reset_index()
        )

        # Add driver names
        pit_stop_summary["DriverName"] = pit_stop_summary["Driver"].apply(
            lambda x: session.get_driver(x)["FullName"]
        )

        # Plot pit stop durations
        fig_pit_stops = px.bar(
            pit_stop_summary,
            x="DriverName",
            y="PitDuration",
            title="Average Pit Stop Durations",
            labels={"PitDuration": "Duration (seconds)"},
        )
        st.plotly_chart(fig_pit_stops, use_container_width=True)
    else:
        st.write("No pit stop data available for this session.")


# Function to create position change analysis
def create_position_change_analysis(session):
    st.subheader("Position Change Analysis")
    laps = session.laps
    fig_position = px.line(
        laps,
        x="LapNumber",
        y="Position",
        color="Driver",
        title="Position Changes During the Race",
    )
    st.plotly_chart(fig_position, use_container_width=True)


def create_fuel_usage_analysis(session, selected_driver_info):
    st.subheader("Fuel Usage Analysis")
    selected_driver = selected_driver_info.split("(")[-1].strip(")")

    # Get the fastest lap for the selected driver
    fastest_lap = session.laps.pick_driver(selected_driver).pick_fastest()

    # Get telemetry data for the fastest lap
    tel = fastest_lap.get_telemetry()

    if not tel.empty:
        # Simulate fuel usage based on throttle and distance
        tel["FuelUsage"] = (
            tel["Throttle"] * tel["Distance"] / 1000
        )  # Simulated fuel usage in liters

        # Plot fuel usage over distance
        fig_fuel_usage = px.line(
            tel,
            x="Distance",
            y="FuelUsage",
            title=f"Fuel Usage - {selected_driver_info}",
        )
        st.plotly_chart(fig_fuel_usage, use_container_width=True)
    else:
        st.write("No telemetry data available for this driver.")


def create_weather_analysis(session):
    st.subheader("Weather Analysis")
    weather_data = session.weather_data

    if not weather_data.empty:
        # Plot temperature over time
        fig_temperature = px.line(
            weather_data, x="Time", y="AirTemp", title="Air Temperature Over Time"
        )
        st.plotly_chart(fig_temperature, use_container_width=True)

        # Plot humidity over time
        fig_humidity = px.line(
            weather_data, x="Time", y="Humidity", title="Humidity Over Time"
        )
        st.plotly_chart(fig_humidity, use_container_width=True)

        # Plot rainfall over time
        fig_rainfall = px.line(
            weather_data, x="Time", y="Rainfall", title="Rainfall Over Time"
        )
        st.plotly_chart(fig_rainfall, use_container_width=True)
    else:
        st.write("No weather data available for this session.")


def create_team_radio_analysis(session, selected_driver_info):
    st.subheader("Team Radio Analysis")
    selected_driver = selected_driver_info.split("(")[-1].strip(")")
    team_radio = session.team_radio

    # Filter radio messages for the selected driver
    driver_radio = team_radio[team_radio["Driver"] == selected_driver]

    if not driver_radio.empty:
        # Display radio messages
        st.write("Team Radio Messages:")
        for _, row in driver_radio.iterrows():
            st.write(f"**{row['Time']}**: {row['Message']}")

        # Play audio (if available)
        if "AudioURL" in driver_radio.columns:
            st.write("Play Audio:")
            for _, row in driver_radio.iterrows():
                if row["AudioURL"]:
                    st.audio(row["AudioURL"], format="audio/mp3")
    else:
        st.write("No team radio data available for this driver.")


# Function to create race track visualization with fastest lap colormap
def create_track_visualization(session, selected_driver_info):
    st.subheader("Race Track Visualization")
    selected_driver = selected_driver_info.split("(")[-1].strip(")")

    # Get the fastest lap for the selected driver
    fastest_lap = session.laps.pick_driver(selected_driver).pick_fastest()

    # Get telemetry data for the fastest lap
    tel = fastest_lap.get_telemetry()

    if not tel.empty:
        # Plot the track layout with speed as a colormap
        fig, ax = plt.subplots()
        ff1.plotting.plot_track(session.track, ax=ax)
        ax.plot(tel["X"], tel["Y"], color="red", label=selected_driver_info)
        ax.set_title(f"Fastest Lap - {selected_driver_info}")
        st.pyplot(fig)
    else:
        st.write("No telemetry data available for this driver.")


def create_lap_time_scatterplot(session):
    st.subheader("Drivers' Lap Time Comparison")
    laps = session.laps
    fig_scatter = px.scatter(
        laps, x="LapNumber", y="LapTime", color="Driver", title="Lap Time Comparison"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)


def who_can_win_wdc(year, round_number):
    st.subheader("Who Can Still Win the WDC?")
    
    # Get the current driver standings
    ergast = Ergast()
    standings = ergast.get_driver_standings(season=year, round=round_number)
    if standings.content.empty:
        st.write("No standings data available.")
        return
    
    driver_standings = standings.content[0]
    
    # Calculate the maximum points for the remaining season
    def calculate_max_points_for_remaining_season():
        POINTS_FOR_SPRINT = 8 + 25 + 1  # Winning the sprint, race, and fastest lap
        POINTS_FOR_CONVENTIONAL = 25 + 1  # Winning the race and fastest lap

        events = fastf1.events.get_event_schedule(year, backend='ergast')
        events = events[events['RoundNumber'] > round_number]
        
        # Count how many sprints and conventional races are left
        sprint_events = len(events.loc[events["EventFormat"] == "sprint_shootout"])
        conventional_events = len(events.loc[events["EventFormat"] == "conventional"])

        # Calculate points for each
        sprint_points = sprint_events * POINTS_FOR_SPRINT
        conventional_points = conventional_events * POINTS_FOR_CONVENTIONAL

        return sprint_points + conventional_points
    
    max_points = calculate_max_points_for_remaining_season()
    
    # Get the leader's points
    leader_points = int(driver_standings.loc[0]['points'])
    
    st.write(f"Current Leader: {driver_standings.loc[0]['givenName']} {driver_standings.loc[0]['familyName']}")
    st.write(f"Leader's Points: {leader_points}")
    st.write(f"Maximum Points Available in Remaining Races: {max_points}")
    
    # Determine which drivers can still win
    for i, _ in enumerate(driver_standings.iterrows()):
        driver = driver_standings.loc[i]
        driver_max_points = int(driver["points"]) + max_points
        can_win = driver_max_points > leader_points
        
        st.write(
            f"{driver['position']}: {driver['givenName']} {driver['familyName']}, "
            f"Current Points: {driver['points']}, "
            f"Theoretical Max Points: {driver_max_points}, "
            f"Can Win: {'Yes' if can_win else 'No'}"
        )


def draw_track_map(session):
    st.subheader("Track Map with Numbered Corners")

    # Get the fastest lap
    lap = session.laps.pick_fastest()
    pos = lap.get_pos_data()

    # Get circuit information
    circuit_info = session.get_circuit_info()

    # Define a helper function for rotating points
    def rotate(xy, *, angle):
        rot_mat = np.array(
            [[np.cos(angle), np.sin(angle)], [-np.sin(angle), np.cos(angle)]]
        )
        return np.matmul(xy, rot_mat)

    # Get the track coordinates and rotate them
    track = pos.loc[:, ("X", "Y")].to_numpy()
    track_angle = circuit_info.rotation / 180 * np.pi
    rotated_track = rotate(track, angle=track_angle)

    # Create the plot
    fig, ax = plt.subplots()
    ax.plot(rotated_track[:, 0], rotated_track[:, 1], color="black")

    # Define an offset vector for corner annotations
    offset_vector = [500, 0]  # Adjust this value as needed

    # Iterate over all corners and annotate them
    for _, corner in circuit_info.corners.iterrows():
        txt = f"{corner['Number']}{corner['Letter']}"  # Corner number and letter

        # Convert the angle from degrees to radians
        offset_angle = corner["Angle"] / 180 * np.pi

        # Rotate the offset vector
        offset_x, offset_y = rotate(offset_vector, angle=offset_angle)

        # Add the offset to the corner position
        text_x = corner["X"] + offset_x
        text_y = corner["Y"] + offset_y

        # Rotate the text position
        text_x, text_y = rotate([text_x, text_y], angle=track_angle)

        # Rotate the corner position
        track_x, track_y = rotate([corner["X"], corner["Y"]], angle=track_angle)

        # Draw a circle next to the track
        ax.scatter(text_x, text_y, color="grey", s=140)

        # Draw a line from the track to the circle
        ax.plot([track_x, text_x], [track_y, text_y], color="grey")

        # Print the corner number inside the circle
        ax.text(
            text_x,
            text_y,
            txt,
            va="center_baseline",
            ha="center",
            size="small",
            color="white",
        )

    # Add a title and clean up the plot
    ax.set_title(session.event["Location"])
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axis("equal")

    # Display the plot in Streamlit
    st.pyplot(fig)


# Main function
def main():
    
    # Inject custom CSS
    inject_custom_css()
    st.title("Formula One Dashboard 🏎️")
    
    

    # Sidebar for year selection
    st.sidebar.title("Filters")
    year = st.sidebar.selectbox("Select Year", range(2025, 2020, -1))
    round_number = st.sidebar.number_input("Select Round", min_value=1, max_value=22, value=15)

    # Fetch all races for the selected year
    schedule = fetch_races(year)
    st.sidebar.write(f"Races in {year}:")
    race_names = schedule.EventName.tolist()
    selected_race = st.sidebar.selectbox("Select Race", race_names)

    # Fetch session data for the selected race
    session = fetch_session_data(year, selected_race)

    # Display race details
    st.header(f"{selected_race} - {year}")
    st.write(f"Race Date: {session.event['EventDate']}")
    st.write(f"Track: {session.event['Location']}")

    # Driver selection
    driver_info = get_driver_names_with_numbers(session)
    selected_driver_info = st.selectbox("Select Driver", driver_info)
    
    draw_track_map(session)  # Track map with numbered corners


    # Create a grid layout for graphs
    col1, col2 = st.columns(2)
    
    with col1:
        create_telemetry_plots(session, selected_driver_info)
        create_sector_time_analysis(session, selected_driver_info)
        create_fuel_usage_analysis(session, selected_driver_info)  # Fuel usage analysis
        create_lap_time_scatterplot(session)  # Lap time scatterplot

    with col2:
        create_lap_time_analysis(session)
        create_tire_usage_analysis(session)
        create_pit_stop_analysis(session)
        create_position_change_analysis(session)
        create_weather_analysis(session)  # Weather analysis


if __name__ == "__main__":
    main()
