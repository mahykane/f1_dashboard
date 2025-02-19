# Formula One Dashboard

## Overview
This **Formula One Dashboard** is an interactive **Streamlit application** that allows users to explore and analyze F1 race data. Users can filter races by **year and round number**, select specific races, and view detailed insights about race performance, drivers, and track conditions.

## Features
- **Race Selection:** Choose a **year, round, and race** from the sidebar.
- **Race Details:** Displays **event date, track location, and a track map** with corner details.
- **Driver Analysis:** Select a driver to analyze telemetry data, lap times, and sector times.
- **Fuel Usage Analysis:** Track fuel consumption over the race.
- **Tire Usage & Pit Stop Analysis:** Monitor tire performance and pit stop strategies.
- **Position Changes:** Visualize how driver positions change during the race.
- **Weather Analysis:** Get insights into weather conditions during the event.
- **Interactive Visualizations:** View side-by-side comparisons of key race metrics.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/mahykane/f1-dashboard.git
   cd f1-dashboard
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Run the application:
   ```sh
   streamlit run f1_dashboard.py
   ```

## Usage
- Use the **sidebar filters** to select the race year and round.
- Choose a **race and driver** to analyze detailed statistics.
- View **interactive graphs** for telemetry, lap times, tire usage, pit stops, and more.

## Requirements
- Python 3.8+
- Streamlit
- Pandas
- FastF1
- Matplotlib

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss your ideas.

## License
This project is licensed under the MIT License.

## Author
Mahy KANE - [GitHub Profile](https://github.com/mahykane)

