import pandas as pd
from pathlib import Path


def analyze_temperatures(directory_path):
    """
    Reads all station CSV files in a directory, extracts annual extremes, 
    and determines the overall historical extremes.

    Args:
        directory_path (str): The relative or absolute path to the 'temperatures' folder.
    """

    # Define the directory and search for the pattern stations_group_<year>.csv
    base_dir = Path(directory_path)
    csv_files = list(base_dir.glob("stations_group_*.csv"))

    if not csv_files:
        print(
            f"No CSV files found in {directory_path}. Please check your project structure.")
        return

    # Trackers for overall records
    overall_max = {"temp": float('-inf'), "station": None, "year": None}
    overall_min = {"temp": float('inf'), "station": None, "year": None}

    # List of month columns to check for temperatures
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']

    print("--- Yearly Temperature Analysis ---")

    for file_path in sorted(csv_files):
        # Extract year from filename (e.g., stations_group_1986.csv -> 1986)
        year = file_path.stem.split('_')[-1]

        # Load the dataset
        df = pd.read_csv(file_path)

        # 1. Find Highest Temperature for this year
        # idxmax() finds the index, max() finds the value across the month columns
        row_max = df[months].max(axis=1)
        yearly_high_val = row_max.max()
        high_station_idx = row_max.idxmax()
        high_station_name = df.loc[high_station_idx, 'STATION_NAME']

        # print(f"Year {year}:")
        # print(f"  - Highest: {yearly_high_val}°C at {high_station_name}")

        # 2. Find Lowest Temperature for this year
        row_min = df[months].min(axis=1)
        yearly_low_val = row_min.min()
        low_station_idx = row_min.idxmin()
        low_station_name = df.loc[low_station_idx, 'STATION_NAME']

        # print(f"Year {year}:")
        # print(f"  - Lowest: {yearly_low_val}°C at {low_station_name}")

        # Print Yearly Results
        print(f"Year {year}:")
        print(f"  - Highest: {yearly_high_val}°C at {high_station_name}")
        print(f"  - Lowest:  {yearly_low_val}°C at {low_station_name}\n")

    #     # Update Overall Maximum
    #     if yearly_high_val > overall_max["temp"]:
    #         overall_max = {"temp": yearly_high_val,
    #                        "station": high_station_name, "year": year}

    #     # Update Overall Minimum
    #     if yearly_low_val < overall_min["temp"]:
    #         overall_min = {"temp": yearly_low_val,
    #                        "station": low_station_name, "year": year}

    # Final Summary Report
    # print("-" * 40)
    # print("HISTORICAL RECORDS SUMMARY")
    # print("-" * 40)
    # print(f"OVERALL HIGHEST: {overall_max['temp']}°C")
    # print(f"Station:         {overall_max['station']}")
    # print(f"Year:            {overall_max['year']}")
    # print("")
    # print(f"OVERALL LOWEST:  {overall_min['temp']}°C")
    # print(f"Station:         {overall_min['station']}")
    # print(f"Year:            {overall_min['year']}")
    # print("-" * 40)


if __name__ == "__main__":
    # Ensure the 'temperatures' folder exists relative to this script
    analyze_temperatures("temperatures")
