import streamlit as st
import pandas as pd
import plotly.express as px
import fastf1 as ff1
from fastf1 import plotting
import matplotlib.pyplot as plt
import os
import numpy as np
from fastf1.ergast import Ergast
import requests
import json
import logging
from urllib.request import urlopen
import plotly.express as px
import requests
import json

# Enable FastF1 caching
if not os.path.exists("cache"):
    os.mkdir("cache")
ff1.Cache.enable_cache("cache")

# Set page title and layout
st.set_page_config(page_title="Formula One Dashboard", page_icon="🏎️", layout="wide")

# Sidebar Section Toggle (Session State)
if "sections" not in st.session_state:
    st.session_state["sections"] = {
        "Telemetry": False,
        "Lap & Tire Analysis": False,
        "Pit Stops & Weather": False,
        "Driver Comparison": False,
    }


# Function to toggle sections
def toggle_section(section):
    st.session_state["sections"][section] = not st.session_state["sections"][section]


# Set up FastF1 plotting
plotting.setup_mpl()

DRIVER_IMAGES = {
    "Max Verstappen": "https://www.formula1.com/content/dam/fom-website/drivers/2025/max-verstappen.jpg",
    "Liam Lawson": "https://www.formula1.com/content/dam/fom-website/drivers/2025/liam-lawson.jpg",
    "Lewis Hamilton": "https://www.formula1.com/content/dam/fom-website/drivers/2025/lewis-hamilton.jpg",
    "Charles Leclerc": "https://www.formula1.com/content/dam/fom-website/drivers/2025/charles-leclerc.jpg",
    "George Russell": "https://www.formula1.com/content/dam/fom-website/drivers/2025/george-russell.jpg",
    "Andrea Kimi Antonelli": "https://www.formula1.com/content/dam/fom-website/drivers/2025/andrea-kimi-antonelli.jpg",
    "Lando Norris": "https://www.formula1.com/content/dam/fom-website/drivers/2025/lando-norris.jpg",
    "Oscar Piastri": "https://www.formula1.com/content/dam/fom-website/drivers/2025/oscar-piastri.jpg",
    "Fernando Alonso": "https://www.formula1.com/content/dam/fom-website/drivers/2025/fernando-alonso.jpg",
    "Lance Stroll": "https://www.formula1.com/content/dam/fom-website/drivers/2025/lance-stroll.jpg",
    "Pierre Gasly": "https://www.formula1.com/content/dam/fom-website/drivers/2025/pierre-gasly.jpg",
    "Jack Doohan": "https://www.formula1.com/content/dam/fom-website/drivers/2025/jack-doohan.jpg",
    "Esteban Ocon": "https://www.formula1.com/content/dam/fom-website/drivers/2025/esteban-ocon.jpg",
    "Oliver Bearman": "https://www.formula1.com/content/dam/fom-website/drivers/2025/oliver-bearman.jpg",
    "Nico Hülkenberg": "https://www.formula1.com/content/dam/fom-website/drivers/2025/nico-hulkenberg.jpg",
    "Gabriel Bortoleto": "https://www.formula1.com/content/dam/fom-website/drivers/2025/gabriel-bortoleto.jpg",
    "Isack Hadjar": "https://www.formula1.com/content/dam/fom-website/drivers/2025/isack-hadjar.jpg",
    "Yuki Tsunoda": "https://www.formula1.com/content/dam/fom-website/drivers/2025/yuki-tsunoda.jpg",
    "Carlos Sainz Jr.": "https://www.formula1.com/content/dam/fom-website/drivers/2025/carlos-sainz.jpg",
    "Alexander Albon": "https://www.formula1.com/content/dam/fom-website/drivers/2025/alexander-albon.jpg",
}


track_info = {
    "Bahrain International Circuit": {
        "length_km": 5.412,
        "corners": 15,
        "location": "Sakhir",
        "country": "Bahrain",
        "history": "The Bahrain International Circuit has hosted the Bahrain Grand Prix since 2004. Known for its desert setting, the track features multiple layout variations and is often subject to strong winds and sand.",
    },
    "Jeddah Corniche Circuit": {
        "length_km": 6.174,
        "corners": 27,
        "location": "Jeddah",
        "country": "Saudi Arabia",
        "history": "Introduced in 2021, Jeddah Corniche Circuit is one of the fastest street circuits in Formula 1, with an average speed exceeding 250 km/h.",
    },
    "Albert Park Circuit": {
        "length_km": 5.278,
        "corners": 14,
        "location": "Melbourne",
        "country": "Australia",
        "history": "Since 1996, Albert Park Circuit has hosted the Australian Grand Prix. The semi-permanent track combines public roads and racing infrastructure.",
    },
    "Baku City Circuit": {
        "length_km": 6.003,
        "corners": 20,
        "location": "Baku",
        "country": "Azerbaijan",
        "history": "Debuting in 2016, the Baku City Circuit is famous for its long straights and tight corners near the historic old city walls.",
    },
    "Miami International Autodrome": {
        "length_km": 5.412,
        "corners": 19,
        "location": "Miami Gardens, Florida",
        "country": "USA",
        "history": "First held in 2022, the Miami Grand Prix is set around the Hard Rock Stadium, featuring a mix of high-speed sections and technical corners.",
    },
    "Imola Circuit": {
        "length_km": 4.909,
        "corners": 19,
        "location": "Imola",
        "country": "Italy",
        "history": "Hosting the Emilia Romagna Grand Prix, Imola is a historic track famous for its challenging layout and was once the home of the San Marino GP.",
    },
    "Circuit de Monaco": {
        "length_km": 3.337,
        "corners": 19,
        "location": "Monte Carlo",
        "country": "Monaco",
        "history": "The most prestigious race on the calendar, first held in 1929, known for its tight layout and minimal overtaking opportunities.",
    },
    "Circuit de Barcelona-Catalunya": {
        "length_km": 4.675,
        "corners": 16,
        "location": "Montmeló, Catalonia",
        "country": "Spain",
        "history": "Opened in 1991, this track is a favorite testing venue due to its mix of high-speed and technical corners.",
    },
    "Circuit Gilles Villeneuve": {
        "length_km": 4.361,
        "corners": 14,
        "location": "Montreal",
        "country": "Canada",
        "history": "Hosting the Canadian Grand Prix since 1978, the track is known for high-speed straights and the 'Wall of Champions' chicane.",
    },
    "Red Bull Ring": {
        "length_km": 4.318,
        "corners": 10,
        "location": "Spielberg",
        "country": "Austria",
        "history": "A short yet fast track known for its elevation changes and minimal braking zones.",
    },
    "Silverstone Circuit": {
        "length_km": 5.891,
        "corners": 18,
        "location": "Silverstone",
        "country": "United Kingdom",
        "history": "The site of the first-ever Formula One World Championship race in 1950, Silverstone remains one of the most iconic circuits.",
    },
    "Hungaroring": {
        "length_km": 4.381,
        "corners": 14,
        "location": "Mogyoród",
        "country": "Hungary",
        "history": "Hosting the Hungarian GP since 1986, this twisty circuit is known for being one of the hardest to overtake on.",
    },
    "Circuit de Spa-Francorchamps": {
        "length_km": 7.004,
        "corners": 19,
        "location": "Stavelot",
        "country": "Belgium",
        "history": "One of the most legendary circuits in F1, Spa has been a part of the championship since 1950. Known for its elevation changes and unpredictable weather.",
    },
    "Circuit Zandvoort": {
        "length_km": 4.259,
        "corners": 14,
        "location": "Zandvoort",
        "country": "Netherlands",
        "history": "The home of the Dutch Grand Prix, featuring banked corners and a tight, flowing layout.",
    },
    "Autodromo Nazionale Monza": {
        "length_km": 5.793,
        "corners": 11,
        "location": "Monza",
        "country": "Italy",
        "history": "Known as the 'Temple of Speed,' Monza is the fastest circuit on the calendar, featuring long straights and minimal cornering.",
    },
    "Marina Bay Street Circuit": {
        "length_km": 4.940,
        "corners": 19,
        "location": "Marina Bay",
        "country": "Singapore",
        "history": "Since 2008, Marina Bay has hosted F1’s first night race, creating a spectacular atmosphere under the city lights.",
    },
    "Suzuka International Racing Course": {
        "length_km": 5.807,
        "corners": 18,
        "location": "Suzuka",
        "country": "Japan",
        "history": "A figure-eight layout and home to some of F1’s greatest title showdowns since its debut in 1987.",
    },
    "Lusail International Circuit": {
        "length_km": 5.419,
        "corners": 16,
        "location": "Lusail",
        "country": "Qatar",
        "history": "Hosting the Qatar GP since 2021, this track is primarily used for MotoGP but offers a fast and flowing layout for F1.",
    },
    "Circuit of the Americas": {
        "length_km": 5.513,
        "corners": 20,
        "location": "Austin, Texas",
        "country": "USA",
        "history": "Opened in 2012, COTA brought F1 back to the USA, featuring significant elevation changes and technical corners.",
    },
    "Autódromo Hermanos Rodríguez": {
        "length_km": 4.304,
        "corners": 17,
        "location": "Mexico City",
        "country": "Mexico",
        "history": "Hosting the Mexican Grand Prix, the track is notable for its high altitude and famous stadium section.",
    },
    "Interlagos (Autódromo José Carlos Pace)": {
        "length_km": 4.309,
        "corners": 15,
        "location": "São Paulo",
        "country": "Brazil",
        "history": "One of F1’s most beloved circuits, Interlagos has produced legendary races and title-deciding moments.",
    },
    "Las Vegas Strip Circuit": {
        "length_km": 6.2,
        "corners": 17,
        "location": "Las Vegas",
        "country": "USA",
        "history": "F1’s return to Las Vegas in 2023, featuring a high-speed layout through the city’s iconic strip.",
    },
    "Yas Marina Circuit": {
        "length_km": 5.281,
        "corners": 16,
        "location": "Abu Dhabi",
        "country": "UAE",
        "history": "Hosting the season finale, Yas Marina is known for its spectacular twilight races.",
    },
}


grand_prix_to_circuit = {
    "Bahrain Grand Prix": "Bahrain International Circuit",
    "Saudi Arabian Grand Prix": "Jeddah Corniche Circuit",
    "Australian Grand Prix": "Albert Park Circuit",
    "Azerbaijan Grand Prix": "Baku City Circuit",
    "Miami Grand Prix": "Miami International Autodrome",
    "Emilia Romagna Grand Prix": "Imola Circuit",
    "Monaco Grand Prix": "Circuit de Monaco",
    "Spanish Grand Prix": "Circuit de Barcelona-Catalunya",
    "Canadian Grand Prix": "Circuit Gilles Villeneuve",
    "Austrian Grand Prix": "Red Bull Ring",
    "British Grand Prix": "Silverstone Circuit",
    "Hungarian Grand Prix": "Hungaroring",
    "Belgian Grand Prix": "Circuit de Spa-Francorchamps",
    "Dutch Grand Prix": "Circuit Zandvoort",
    "Italian Grand Prix": "Autodromo Nazionale Monza",
    "Singapore Grand Prix": "Marina Bay Street Circuit",
    "Japanese Grand Prix": "Suzuka International Racing Course",
    "Qatar Grand Prix": "Lusail International Circuit",
    "United States Grand Prix": "Circuit of the Americas",
    "Mexico City Grand Prix": "Autódromo Hermanos Rodríguez",
    "São Paulo Grand Prix": "Interlagos (Autódromo José Carlos Pace)",
    "Las Vegas Grand Prix": "Las Vegas Strip Circuit",
    "Abu Dhabi Grand Prix": "Yas Marina Circuit",
}


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

            /* Tables */
            .stDataFrame {
                border-radius: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                background-color: #2E2E2E;
                padding: 1rem;
            }

            /* Custom font */
            @import url('https://fonts.googleapis.com/css2?family=Formula1&display=swap');

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

            /* Headers */
            h2, h3, h4, h5, h6 {
                color: #FF1801;
                font-family: 'Formula1', sans-serif;
            }

            /* Subheaders */
            .stSubheader {
                color: #FF1801;
                font-family: 'Formula1', sans-serif;
            }

            /* Expander */
            .stExpander {
                background-color: #1E1E1E;
                color: #FFFFFF;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }

            /* Plotly charts */
            .plotly {
                background-color: #2E2E2E;
                border-radius: 10px;
                padding: 1rem;
            }
            /* Custom Font */
            @import url('https://fonts.googleapis.com/css2?family=Formula1&display=swap');

            /* Set Background */
            .stApp {
                background-color: #121212;
                color: #FFFFFF;
                font-family: 'Formula1', sans-serif;
            }

            /* Sidebar */
            .css-1d391kg {
                background-color: #1E1E1E;
                border-radius: 10px;
                padding: 1rem;
            }

            /* Buttons */
            .stButton button {
                background-color: #FF1801;
                color: #FFFFFF;
                border-radius: 10px;
                font-weight: bold;
            }

            .stButton button:hover {
                background-color: #E51600;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Function to fetch all races for a given year
def fetch_races(year):
    schedule = ff1.get_event_schedule(year)
    return schedule


def add_footer():
    st.markdown(
        """
        <style>
            .footer {
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100%;
                background-color: #1E1E1E;
                color: white;
                text-align: center;
                padding: 10px;
                font-size: 14px;
                font-family: Arial, sans-serif;
                box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.2);
            }
        </style>
        <div class="footer">
            Developed by <b>KREAITIVE</b> | © 2025 All Rights Reserved
        </div>
        """,
        unsafe_allow_html=True,
    )



# Function to fetch session data for a specific race
def fetch_session_data(year, race_name):
    try:
        # st.write(f"Fetching session data for {year} for the race {race_name} ...")
        # Check if it's the 2025 season pretesting
        if year == 2025 and race_name.lower() == "pre-season testing":
            # st.write("Fetching pre-season testing session data ...")
            session = ff1.get_testing_session(2025, 1, 1)  # Fetch pretesting session
        else:
            session = ff1.get_session(year, race_name, "R")  # Regular race session

        session.load()
        # has_data = not session.laps.empty  # Check if session has lap data
        # st.write("Session data fetched successfully.")

        return session
    except Exception as e:
        st.warning(f"Error fetching session data: {e}")
        return None, False


OLLAMA_API_URL = "http://localhost:11434/"  # Update if your Ollama instance runs on a different port

# Function to check if Ollama API is accessible
def is_ollama_api_available():
    try:
        response = requests.get(OLLAMA_API_URL, timeout=3)  # Quick health check
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Store API availability in session state to avoid multiple checks
if "ollama_available" not in st.session_state:
    st.session_state["ollama_available"] = is_ollama_api_available()


def interpret_data_with_ollama(data):
    """
    Sends telemetry data to Ollama API for AI-based interpretation.

    Args:
        data (dict): A dictionary containing telemetry, lap, or strategy data.

    Returns:
        str: AI-generated insights from Ollama.
    """
    # Prepare request payload
    payload = {
        "model": "llama3",
        "prompt": f"""
            You are a Formula 1 data analyst specializing in telemetry and race performance insights.
            
            Analyze the following telemetry data from an F1 race and provide a structured breakdown:
            
            - **Overall Driver Performance:** Identify key highlights from the data, including top speed, fastest lap, and throttle consistency.
            - **Sector Performance:** Compare Sector 1, Sector 2, and Sector 3 times. Which sector is the driver strongest or weakest in?
            - **Pit Stop Efficiency:** Assess the number and duration of pit stops. How does this compare to an optimal race strategy?
            - **Telemetry Analysis:** Examine speed, throttle, braking, RPM, DRS usage, and gear shifts. Are there any unusual patterns or trends?
            - **Comparative Insights:** If historical data is available, compare this session with previous performances for the same driver or track.
            - **Recommendations:** Suggest potential improvements based on the data. Should the driver optimize braking zones, throttle application, or pit strategy?
            
            Here is the telemetry data for analysis:
            {json.dumps(data, indent=2)}
            
            Provide your insights in a structured and concise manner, using bullet points for clarity.
            """,
        "stream": False,  # Set to True for streaming responses
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        if response.status_code == 200:
            return response.json().get("response", "No insights available.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error communicating with Ollama API: {e}"


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

    st.write(
        "This graph shows the driver's telemetry data, including **Speed, Throttle, Braking, Gear Changes, and DRS Usage** over a lap. "
        "It helps analyze how a driver manages speed, braking zones, and acceleration."
    )
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


def create_enhanced_telemetry_plots(session, selected_driver_info):
    st.subheader("📊 Enhanced Telemetry Analysis")

    st.write(
        """
        This section provides an in-depth analysis of the driver's telemetry data, including:
        - **Speed**: Vehicle speed over the lap distance.
        - **Throttle**: Throttle application as a percentage.
        - **Brake**: Brake pressure indicating braking zones.
        - **Gear**: Gear selection throughout the lap.
        - **DRS**: Drag Reduction System activation points.
        - **RPM**: Engine revolutions per minute.
        - **Steering Angle**: Inferred from positional data.

        These metrics help analyze driver behavior, car performance, and track characteristics.
        """
    )

    # Extract driver identifier
    selected_driver = selected_driver_info.split("(")[-1].strip(")")

    # Load the fastest lap telemetry data
    lap = session.laps.pick_driver(selected_driver).pick_fastest()
    tel = lap.get_telemetry()

    # Calculate Steering Angle
    tel["delta_x"] = tel["X"].diff()
    tel["delta_y"] = tel["Y"].diff()
    tel["SteeringAngle"] = np.arctan2(tel["delta_y"], tel["delta_x"]) * (180 / np.pi)

    # Define telemetry parameters and their labels
    telemetry_params = {
        "Speed": "Speed (km/h)",
        "Throttle": "Throttle (%)",
        "Brake": "Brake Pressure",
        "nGear": "Gear",
        "DRS": "DRS Activation",
        "RPM": "Engine RPM",
        "SteeringAngle": "Steering Angle (°)",
    }

    # Create two columns for the graphs
    col1, col2 = st.columns(2)

    with col1:
        for param, label in list(telemetry_params.items())[:4]:  # First four graphs
            fig = px.line(
                tel,
                x="Distance",
                y=param,
                title=f"{label} vs Distance - {selected_driver_info}",
                labels={"Distance": "Distance (m)", param: label},
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        for param, label in list(telemetry_params.items())[4:]:  # Last three graphs
            fig = px.line(
                tel,
                x="Distance",
                y=param,
                title=f"{label} vs Distance - {selected_driver_info}",
                labels={"Distance": "Distance (m)", param: label},
            )
            st.plotly_chart(fig, use_container_width=True)


# Function to create lap time analysis
def create_lap_time_analysis(session):
    st.subheader("Lap Time Analysis")
    st.write(
        "This graph displays **lap times** for all drivers during the race. "
        "It helps identify **race pace consistency, slow and fast laps, and strategy changes.**"
    )
    laps = session.laps
    fig_lap_times = px.line(laps, x="LapNumber", y="LapTime", title="Lap Times")
    st.plotly_chart(fig_lap_times, use_container_width=True)


# Function to create tire usage analysis
def create_tire_usage_analysis(session):
    st.subheader("Tire Usage Analysis")
    st.write(
        "This box plot compares **tire compounds and lap times**, showing which tires performed best. "
        "It helps analyze strategy choices and how different compounds behave."
    )
    laps = session.laps
    fig_tire_usage = px.box(laps, x="Compound", y="LapTime", title="Tire Usage")
    st.plotly_chart(fig_tire_usage, use_container_width=True)


# Function to create sector time analysis
def create_sector_time_analysis(session, selected_driver_info):
    st.subheader("Sector Time Analysis")

    st.write(
        "This graph breaks down lap times into **Sector 1, Sector 2, and Sector 3**. "
        "It helps identify which parts of the track the driver is fastest or struggling."
    )
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
    st.write(
        "This chart shows **average pit stop durations** for each driver. "
        "It helps compare how quickly teams execute pit stops and their impact on race positions."
    )
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

        events = ff1.events.get_event_schedule(year, backend="ergast")
        events = events[events["RoundNumber"] > round_number]

        # Count how many sprints and conventional races are left
        sprint_events = len(events.loc[events["EventFormat"] == "sprint_shootout"])
        conventional_events = len(events.loc[events["EventFormat"] == "conventional"])

        # Calculate points for each
        sprint_points = sprint_events * POINTS_FOR_SPRINT
        conventional_points = conventional_events * POINTS_FOR_CONVENTIONAL

        return sprint_points + conventional_points

    max_points = calculate_max_points_for_remaining_season()

    # Get the leader's points
    leader_points = int(driver_standings.loc[0]["points"])

    st.write(
        f"Current Leader: {driver_standings.loc[0]['givenName']} {driver_standings.loc[0]['familyName']}"
    )
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


def fetch_round_number(year, race_name):
    schedule = fetch_races(year)
    race_info = schedule[schedule["EventName"] == race_name]

    if not race_info.empty:
        return int(race_info["RoundNumber"].values[0])  # Extract round number
    return None


def fetch_race_results(session):
    try:
        # Get race results (classified finishers)
        race_results = session.results
        if race_results.empty:
            return None, None

        # Extract top 3 finishers
        top_3 = race_results[["Position", "FullName", "TeamName"]].head(3)

        return race_results, top_3
    except Exception as e:
        st.error(f"Error fetching race results: {e}")
        return None, None


def format_time(delta):
    """Convert timedelta to MM:SS.sss format."""
    if pd.isna(delta):  # Handle missing times
        return "N/A"

    total_seconds = delta.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds - (minutes * 60) - seconds) * 1000)

    return f"{minutes:02}:{seconds:02}.{milliseconds:03}"


def fetch_qualifying_results(year, race_name):
    try:
        # Load the qualifying session
        qualifying_session = ff1.get_session(year, race_name, "Q")
        qualifying_session.load()

        # Extract qualifying results
        qualifying_results = qualifying_session.results[
            ["Position", "FullName", "Q1", "Q2", "Q3"]
        ]

        # Convert Position to integer
        qualifying_results["Position"] = qualifying_results["Position"].astype(int)

        # Format Q1, Q2, Q3 times
        for col in ["Q1", "Q2", "Q3"]:
            qualifying_results[col] = qualifying_results[col].apply(format_time)

        return qualifying_results
    except Exception as e:
        st.error(f"Error fetching qualifying results: {e}")
        return None


def fetch_team_radio():
    """Fetches the latest Team Radio messages from the Formula 1 API."""
    try:
        # Get session information to construct the correct URL
        with urlopen(
            "http://livetiming.formula1.com/static/SessionInfo.json"
        ) as response:
            if response.getcode() == 200:
                logging.info("Fetching session info...")
                session_data = json.loads(response.read())

                # Construct the URL for Team Radio data
                team_radio_url = f"http://livetiming.formula1.com/static/{session_data['Path']}TeamRadio.json"
                logging.info("Fetching Team Radio data...")

                # Request Team Radio JSON
                r = requests.get(team_radio_url)
                r.encoding = "utf-8-sig"

                # Load JSON data
                radio_data = json.loads(r.text)
                return radio_data

    except Exception as e:
        logging.error(f"Error fetching Team Radio: {e}")
        return None


def display_team_radio():
    """Displays Team Radio messages in the Streamlit Dashboard."""
    st.subheader("🎙️ Team Radio Messages")

    team_radio_data = fetch_team_radio()

    if team_radio_data and "Messages" in team_radio_data:
        messages = team_radio_data["Messages"]

        if not messages:
            st.info("No team radio messages available at the moment.")
            return

        for message in messages:
            driver = message.get("Driver", "Unknown Driver")
            content = message.get("Message", "No message available")
            time = message.get("Time", "Unknown Time")

            # Format display with driver name, message, and timestamp
            with st.expander(f"🎤 {driver} - {time}"):
                st.write(f"🗣 **Message:** {content}")

    else:
        st.error("Could not retrieve Team Radio messages. Try again later.")


# Create telemetry comparison plots
def create_telemetry_comparison(session, selected_drivers):
    st.subheader("📊 Multi-Driver Telemetry Comparison")

    telemetry_params = {
        "Speed": "Speed (km/h)",
        "Throttle": "Throttle (%)",
        "Brake": "Brake Pressure",
        "nGear": "Gear",
        "DRS": "DRS Activation",
        "RPM": "Engine RPM",
    }

    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)

    for driver_info in selected_drivers:
        driver = driver_info.split("(")[-1].strip(")")
        lap = session.laps.pick_driver(driver).pick_fastest()
        tel = lap.get_telemetry()

        ax.plot(tel["Distance"], tel["Speed"], label=f"{driver_info}")

    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title("Speed Comparison Across Drivers")
    ax.legend()
    st.pyplot(fig)

    col1, col2 = st.columns(2)
    with col1:
        for param, label in list(telemetry_params.items())[:3]:  # First three
            fig_param = px.line(
                title=f"{label} vs Distance",
                labels={"Distance": "Distance (m)", param: label},
            )
            for driver_info in selected_drivers:
                driver = driver_info.split("(")[-1].strip(")")
                lap = session.laps.pick_driver(driver).pick_fastest()
                tel = lap.get_telemetry()
                fig_param.add_scatter(
                    x=tel["Distance"], y=tel[param], mode="lines", name=driver_info
                )
            st.plotly_chart(fig_param, use_container_width=True)

    with col2:
        for param, label in list(telemetry_params.items())[3:]:  # Last three
            fig_param = px.line(
                title=f"{label} vs Distance",
                labels={"Distance": "Distance (m)", param: label},
            )
            for driver_info in selected_drivers:
                driver = driver_info.split("(")[-1].strip(")")
                lap = session.laps.pick_driver(driver).pick_fastest()
                tel = lap.get_telemetry()
                fig_param.add_scatter(
                    x=tel["Distance"], y=tel[param], mode="lines", name=driver_info
                )
            st.plotly_chart(fig_param, use_container_width=True)


# Create lap time comparison
def create_lap_time_comparison(session, selected_drivers):
    st.subheader("⏱️ Lap Time Comparison")

    laps = session.laps
    fig = px.line(title="Lap Time Comparison Across Drivers")

    for driver_info in selected_drivers:
        driver = driver_info.split("(")[-1].strip(")")
        driver_laps = laps.pick_driver(driver)
        fig.add_scatter(
            x=driver_laps["LapNumber"],
            y=driver_laps["LapTime"],
            mode="lines",
            name=driver_info,
        )

    st.plotly_chart(fig, use_container_width=True)


# Create sector time comparison
def create_sector_time_comparison(session, selected_drivers):
    st.subheader("🏎️ Sector Time Comparison")

    fig = px.line(title="Sector Time Comparison")

    for driver_info in selected_drivers:
        driver = driver_info.split("(")[-1].strip(")")
        laps = session.laps.pick_driver(driver)

        sector_times = laps[["LapNumber", "Sector1Time", "Sector2Time", "Sector3Time"]]
        sector_times_melted = sector_times.melt(
            id_vars=["LapNumber"],
            value_vars=["Sector1Time", "Sector2Time", "Sector3Time"],
            var_name="Sector",
            value_name="Time",
        )

        for sector in ["Sector1Time", "Sector2Time", "Sector3Time"]:
            sector_data = sector_times_melted[sector_times_melted["Sector"] == sector]
            fig.add_scatter(
                x=sector_data["LapNumber"],
                y=sector_data["Time"],
                mode="lines",
                name=f"{driver_info} - {sector}",
            )

    st.plotly_chart(fig, use_container_width=True)


# Create pit stop comparison
def create_pit_stop_comparison(session, selected_drivers):
    st.subheader("🛑 Pit Stop Comparison")

    pit_stops = session.laps[session.laps["PitInTime"].notna()]
    pit_stop_data = []

    for driver_info in selected_drivers:
        driver = driver_info.split("(")[-1].strip(")")
        driver_pit_stops = pit_stops[pit_stops["Driver"] == driver]

        for _, row in driver_pit_stops.iterrows():
            pit_duration = (row["PitOutTime"] - row["PitInTime"]).total_seconds()
            pit_stop_data.append(
                {
                    "Driver": driver_info,
                    "Lap": row["LapNumber"],
                    "PitDuration": pit_duration,
                }
            )

    pit_df = pd.DataFrame(pit_stop_data)
    if not pit_df.empty:
        fig = px.bar(
            pit_df, x="Driver", y="PitDuration", color="Lap", title="Pit Stop Durations"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No pit stop data available for these drivers.")


def render_track_map(session, selected_driver_info):
    """
    Render an interactive track map visualization.
    - Displays the driver's racing line based on telemetry GPS data.
    - Color-coded by speed to show acceleration and braking zones.

    Args:
        session: FastF1 session object.
        selected_driver_info: Driver name with number (e.g., "Max Verstappen (33)").
    """
    st.subheader("🗺️ Track Map: Driver Path & Speed")

    # Extract the driver number from the selection
    selected_driver = selected_driver_info.split("(")[-1].strip(")")

    # Get the fastest lap for the selected driver
    fastest_lap = session.laps.pick_driver(selected_driver).pick_fastest()
    if fastest_lap is None:
        st.warning("No fastest lap data available for this driver.")
        return

    # Get telemetry data (GPS X, Y coordinates & Speed)
    telemetry = fastest_lap.get_telemetry()

    # Create a scatter plot with GPS data
    fig = px.scatter(
        telemetry,
        x="X",
        y="Y",
        color="Speed",
        title=f"{selected_driver_info} - Fastest Lap GPS Data",
        labels={
            "Speed": "Speed (km/h)",
            "X": "Track Position (X)",
            "Y": "Track Position (Y)",
        },
        color_continuous_scale=px.colors.sequential.Plasma,
        template="plotly_dark",
    )

    # Display the plot
    st.plotly_chart(fig, use_container_width=True)


def create_ai_analysis_data(session, selected_driver_info, selected_graphs):
    """
    Creates a structured data object for AI analysis based on user-selected graphs.

    Args:
        session: FastF1 session object containing race data.
        selected_driver_info (str): The selected driver with number in format "Driver Name (Number)".
        selected_graphs (list): List of selected graphs for analysis.

    Returns:
        dict: A dictionary containing key telemetry and performance metrics for AI interpretation.
    """

    try:
        selected_driver = selected_driver_info.split("(")[-1].strip(")")
        fastest_lap = session.laps.pick_driver(selected_driver).pick_fastest()
        telemetry = fastest_lap.get_telemetry()
        pit_stops = session.laps[session.laps["PitInTime"].notna()]

        average_pit_duration = (
            (pit_stops["PitOutTime"] - pit_stops["PitInTime"]).dt.total_seconds().mean()
            if not pit_stops.empty
            else None
        )

        def convert_to_serializable(value):
            if isinstance(value, (np.int64, np.float64)):
                return value.item()
            return value

        data_for_analysis = {"Driver": selected_driver_info}

        # Include only user-selected graphs
        if "Fastest Lap Time" in selected_graphs:
            data_for_analysis["Fastest Lap Time (s)"] = convert_to_serializable(
                fastest_lap.LapTime.total_seconds()
            )

        if "Top Speed" in selected_graphs:
            data_for_analysis["Top Speed (km/h)"] = convert_to_serializable(
                telemetry["Speed"].max()
            )

        if "Throttle Analysis" in selected_graphs:
            data_for_analysis["Average Throttle (%)"] = convert_to_serializable(
                telemetry["Throttle"].mean()
            )

        if "Sector Times" in selected_graphs:
            data_for_analysis["Sector Times (s)"] = {
                "Sector 1": (
                    convert_to_serializable(fastest_lap.Sector1Time.total_seconds())
                    if pd.notna(fastest_lap.Sector1Time)
                    else None
                ),
                "Sector 2": (
                    convert_to_serializable(fastest_lap.Sector2Time.total_seconds())
                    if pd.notna(fastest_lap.Sector2Time)
                    else None
                ),
                "Sector 3": (
                    convert_to_serializable(fastest_lap.Sector3Time.total_seconds())
                    if pd.notna(fastest_lap.Sector3Time)
                    else None
                ),
            }

        if "Pit Stop Analysis" in selected_graphs:
            data_for_analysis["Pit Stop Analysis"] = {
                "Total Pit Stops": convert_to_serializable(len(pit_stops)),
                "Average Pit Duration (s)": convert_to_serializable(
                    average_pit_duration
                ),
            }

        if "Telemetry Summary" in selected_graphs:
            data_for_analysis["Telemetry Summary"] = {
                "Max RPM": (
                    convert_to_serializable(telemetry["RPM"].max())
                    if "RPM" in telemetry.columns
                    else None
                ),
                "Gear Shifts Count": (
                    convert_to_serializable(telemetry["nGear"].nunique())
                    if "nGear" in telemetry.columns
                    else None
                ),
                "DRS Activations": (
                    convert_to_serializable(telemetry["DRS"].sum())
                    if "DRS" in telemetry.columns
                    else None
                ),
                "Brake Usage (%)": (
                    convert_to_serializable(telemetry["Brake"].mean())
                    if "Brake" in telemetry.columns
                    else None
                ),
                "Distance Covered (m)": (
                    convert_to_serializable(telemetry["Distance"].max())
                    if "Distance" in telemetry.columns
                    else None
                ),
            }

        return data_for_analysis

    except Exception as e:
        return {"error": f"Failed to process AI analysis data: {e}"}

def generate_strategy_recommendations(data):
    """Send telemetry data to AI for strategy optimization insights."""

    payload = {
        "model": "llama3",
        "prompt": f"""
        You are an expert Formula 1 race strategist. Analyze the telemetry data and provide an **optimal race strategy**.
        
        **Key Areas for Analysis:**
        1. **Lap Time Optimization:** Identify sections where the driver is losing time. Suggest improvements in braking, acceleration, and cornering.
        2. **Fuel & Tire Strategy:** Based on speed, braking, and sector times, determine the best **tire compound** and optimal **pit stop strategy**.
        3. **DRS & Overtaking Opportunities:** Identify where DRS was most effective and suggest overtaking points.
        4. **Pit Stop Recommendations:** Is an **undercut** or **overcut** strategy better based on sector performance and pit lane loss time?
        5. **Defensive & Aggressive Driving Adjustments:** Should the driver **conserve tires and fuel** or push harder based on the race situation?
        6. **Comparisons with Rivals (if available):** How does this driver’s telemetry compare to competitors?

        **Telemetry Data:**
        {json.dumps(data, indent=2)}
        
        Provide clear and structured strategy recommendations, focusing on **data-driven insights** for an optimal race plan.
        """,
        "stream": False  # Set to True for streaming responses
    }

    # Replace with your Ollama API endpoint
    response = requests.post("http://localhost:11434/api/generate", json=payload)

    if response.status_code == 200:
        return response.json().get("response", "No strategy recommendations available.")
    else:
        return f"Error: {response.status_code} - {response.text}"
    
 #Function to send race strategy question to Ollama API
def ask_race_strategy_question(question, data):
    payload = {
        "model": "llama3",
        "prompt": f"Analyze the following Formula 1 telemetry data and provide race strategy insights:\n\n{json.dumps(data, indent=2)}\n\nUser Question: {question}\n\nProvide a professional response with specific strategic insights.",
        "stream": False  # Set to True for streaming responses
    }
    
    # Send request to Ollama API
    response = requests.post("http://localhost:11434/api/generate", json=payload)

    if response.status_code == 200:
        return response.json().get("response", "No response received.")
    else:
        return f"Error: {response.status_code} - Unable to fetch AI insights."

## Main function
def main():
    # Inject custom CSS
    inject_custom_css()
    st.title("Formula One Dashboard 🏎️")

    st.markdown(
        """
        Welcome to the **Formula One Dashboard**, an interactive tool for analyzing F1 race data. 
        Explore telemetry insights, lap times, tire usage, pit stops, fuel consumption, 
        and more. Use the filters in the sidebar to select a **year, race, and driver** 
        and get real-time insights on their performance.
        """,
        unsafe_allow_html=True,
    )

    # Sidebar for filters
    st.sidebar.title("Filters")

    # Ensure session state is initialized
    if "year" not in st.session_state:
        st.session_state["year"] = 2025  # Default value
    if "race_name" not in st.session_state:
        st.session_state["race_name"] = ""

    # Select Year
    st.session_state["year"] = st.sidebar.selectbox(
        "Select Year", range(2025, 2017, -1), index=0
    )
    year = st.session_state["year"]

    # Fetch all races for the selected year
    schedule = fetch_races(year)
    race_names = schedule.EventName.tolist()

    # Retain selected race in session state
    if st.session_state["race_name"] not in race_names:
        st.session_state["race_name"] = race_names[
            0
        ]  # Default to first race if invalid

    # Select Race
    st.session_state["race_name"] = st.sidebar.selectbox(
        "Select Race", race_names, index=race_names.index(st.session_state["race_name"])
    )
    selected_race = st.session_state["race_name"]


    # Dynamically get the round number based on selected race
    round_number = fetch_round_number(year, selected_race)
    session = fetch_session_data(year, selected_race)
    has_data = True  # Check if session has lap data

    # Fetch session data and race results using the retrieved round number
    if round_number:
        session = fetch_session_data(year, selected_race)
        race_results, top_3 = fetch_race_results(session)
        qualifying_results = fetch_qualifying_results(year, selected_race)

        if not has_data:
            st.warning(
                "No data available for the selected race. Please choose another race."
            )
        else:
            st.header(f"🏁 {selected_race} - {year}")

            col1, col2 = st.columns(2)  # Two columns for race details

            with col1:
                st.subheader("Race Information")
                st.write(f"📅 **Race Date:** {session.event['EventDate']}")
                st.write(f"📍 **Track:** {session.event['Location']}")

                if race_results is not None:
                    st.subheader("🏆 Podium Finishers")
                    if top_3 is not None:
                        for _, row in top_3.iterrows():
                            driver_name = row["FullName"]
                            driver_team = row["TeamName"]

                            if row["Position"] == 1:
                                st.markdown(
                                    f"<h1 style='font-size:32px;'>🥇 <b>{driver_name} ({driver_team})</b></h1>",
                                    unsafe_allow_html=True,
                                )
                            elif row["Position"] == 2:
                                st.markdown(
                                    f"<h2 style='font-size:28px;'>🥈 <b>{driver_name} ({driver_team})</b></h2>",
                                    unsafe_allow_html=True,
                                )
                            elif row["Position"] == 3:
                                st.markdown(
                                    f"<h3 style='font-size:26px;'>🥉 <b>{driver_name} ({driver_team})</b></h3>",
                                    unsafe_allow_html=True,
                                )

                # Display qualifying results
                if qualifying_results is not None:
                    st.subheader("🏁 Qualifying Results")
                    st.dataframe(
                        qualifying_results.style.set_properties(
                            **{"text-align": "center"}
                        )
                    )
                else:
                    st.write("No qualifying data available.")

            with col2:
                # Get the circuit name from the selected Grand Prix
                circuit_name = grand_prix_to_circuit.get(selected_race)

                # Retrieve track details using the circuit name
                track_details = track_info.get(circuit_name)

                if track_details:
                    st.subheader("🏁 Track Information")
                    st.write(
                        f"📍 **Location:** {track_details['location']}, {track_details['country']}"
                    )
                    st.write(f"📏 **Length:** {track_details['length_km']} km")
                    st.write(f"🔄 **Number of Corners:** {track_details['corners']}")
                    st.write(f"📜 **History:** {track_details['history']}")
                else:
                    st.warning("Track information not available for this Grand Prix.")

                draw_track_map(session)  # Display the track map in the second column

            st.markdown("---")  # Separator

    else:
        st.warning("Unable to determine the round number for the selected race.")

    st.markdown("---")  # Separator for sections

    if not session:
        st.stop()
    else:
        # Driver selection
        driver_info = get_driver_names_with_numbers(session)
        selected_driver_info = st.selectbox("Select Driver", driver_info)
        
    data_for_analysis = None
    # Hide AI features if Ollama API is unreachable
    if st.session_state["ollama_available"]:

        # Sidebar: User selects graphs for AI analysis
        st.sidebar.subheader("📊 AI Insights Selection")

        graph_options = {
            "Fastest Lap Time": "Fastest Lap Time",
            "Top Speed": "Top Speed",
            "Throttle Analysis": "Throttle Analysis",
            "Sector Times": "Sector Times",
            "Pit Stop Analysis": "Pit Stop Analysis",
            "Telemetry Summary": "Telemetry Summary"
        }

        # Store selected graphs dynamically
        selected_graphs = [label for label, key in graph_options.items() if st.sidebar.checkbox(label, True)]
        
        # Sidebar button to open AI chat
        if st.sidebar.button("💬 Open Race Strategy Chat"):
            st.session_state["show_chat"] = True

        # Check if chat is open
        if st.session_state.get("show_chat", False):
            st.header("💬 Live AI Race Strategy Chat")

            # Ensure chat history is stored in session state
            if "chat_history" not in st.session_state:
                st.session_state["chat_history"] = []

            # Display previous chat messages
            for message in st.session_state["chat_history"]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input field
            user_input = st.chat_input("Ask about race strategy...")

            if user_input:
                # Store user question
                st.session_state["chat_history"].append({"role": "user", "content": user_input})

                # Send question to AI
                ai_response = ask_race_strategy_question(user_input, data_for_analysis)

                # Store AI response
                st.session_state["chat_history"].append({"role": "assistant", "content": ai_response})

                # Display AI response
                with st.chat_message("assistant"):
                    st.markdown(ai_response)

        # Button to generate AI Insights
        if st.sidebar.button("Generate AI Insights"):
            st.sidebar.info("⏳ Analyzing data...")

            # Generate data for AI analysis
            data_for_analysis = create_ai_analysis_data(
                session, selected_driver_info, selected_graphs
            )

            # Convert to JSON string for AI processing
            data_json = json.dumps(data_for_analysis, indent=2)

            # Call Ollama API to interpret data (replace with your API function)
            ai_insights = interpret_data_with_ollama(data_json)

            # Display AI response
            st.sidebar.success("✅ AI Analysis Complete!")
            st.sidebar.write(ai_insights)
            
        if st.button("Generate AI Strategy Recommendations"):
            data_for_analysis = create_ai_analysis_data(
                session, selected_driver_info, selected_graphs
            )
            strategy_recommendations = generate_strategy_recommendations(data_for_analysis)
            st.subheader("🏎️ AI-Powered Strategy Recommendations")
            st.write(strategy_recommendations)
    else:
        st.sidebar.warning("🚨 AI services are currently unavailable.")
        
        

    # **Accordion Sections**
    with st.expander("📊 Telemetry & Performance", expanded=False):
        render_track_map(session, selected_driver_info)
        create_telemetry_plots(session, selected_driver_info)

    with st.expander("⏱️ Lap & Tire Analysis", expanded=False):
        create_lap_time_scatterplot(session)
        create_lap_time_analysis(session)
        create_tire_usage_analysis(session)
        create_sector_time_analysis(session, selected_driver_info)
        create_fuel_usage_analysis(session, selected_driver_info)

    with st.expander("🔧 Pit Stops & Weather", expanded=False):
        create_pit_stop_analysis(session)
        create_position_change_analysis(session)
        create_weather_analysis(session)

    with st.expander("📈 Enhanced Telemetry Analysis", expanded=False):
        create_enhanced_telemetry_plots(session, selected_driver_info)

    # **Driver Comparison Section**
    with st.expander("🏎️ Driver Comparison", expanded=False):
        st.write(
            "Compare multiple drivers across various metrics, including lap times, sector times, pit stops, and telemetry data. Select up to three drivers to analyze their performance side by side."
        )

        driver_info = get_driver_names_with_numbers(session)
        selected_drivers = st.multiselect(
            "Select up to 3 Drivers for Comparison",
            driver_info,
            default=driver_info[:2],
        )

        if len(selected_drivers) < 2:
            st.warning("Please select at least two drivers for comparison.")
            st.stop()

        # Layout for comparison charts
        col1, col2 = st.columns(2)

        with col1:
            create_lap_time_comparison(session, selected_drivers)
            create_pit_stop_comparison(session, selected_drivers)

        with col2:
            create_sector_time_comparison(session, selected_drivers)

        create_telemetry_comparison(session, selected_drivers)
        
        
# Call this function at the end of the app
add_footer()


if __name__ == "__main__":
    main()
