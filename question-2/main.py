from __future__ import annotations
import os
import glob
import re
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

# months present in CSV in this exact order (from sample CSV)
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# mapping month -> season (Australian)
MONTH_TO_SEASON = {
    "December": "Summer", "January": "Summer", "February": "Summer",
    "March": "Autumn", "April": "Autumn", "May": "Autumn",
    "June": "Winter", "July": "Winter", "August": "Winter",
    "September": "Spring", "October": "Spring", "November": "Spring",
}

# rounding for outputs
ROUND_DECIMALS = 1


def find_csv_files(folder: str) -> List[str]:
    pattern = os.path.join(folder, "*.csv")
    files = sorted(glob.glob(pattern))
    return files


def load_and_concat_csv(files: List[str]) -> pd.DataFrame:
    parts = []
    for fpath in files:
        try:
            df = pd.read_csv(fpath, dtype={"STATION_NAME": str})
        except Exception as e:
            print(f"Warning: could not read {fpath}: {e}")
            continue

        # ensure months exist
        missing_months = [m for m in MONTHS if m not in df.columns]
        if missing_months:
            raise ValueError(
                f"File {fpath} is missing month columns: {missing_months}")

        # Attach source filename and try to extract year from filename if present
        base = os.path.basename(fpath)
        df["SOURCE_FILE"] = base
        m = re.search(r"(\d{4})", base)
        df["SOURCE_YEAR"] = int(m.group(1)) if m else np.nan

        parts.append(df)

    if not parts:
        return pd.DataFrame()  # empty

    combined = pd.concat(parts, ignore_index=True, sort=False)
    return combined
    """
    Output Will be like this:
                                STATION_NAME  STN_ID    LAT     LON  ...  November  December              SOURCE_FILE  SOURCE_YEAR
        0                ADELAIDE-KENT-TOWN   23090 -34.92  138.62  ...     26.65     28.38  stations_group_1986.csv         1986
        1         ALBANY-AIRPORT-COMPARISON    9741 -34.94  117.80  ...     21.85     23.75  stations_group_1986.csv         1986
        2             ALICE-SPRINGS-AIRPORT   15590 -23.80  133.89  ...     34.38     36.06  stations_group_1986.csv         1986
        3                      AMBERLEY-AMO   40004 -27.63  152.71  ...     31.04     32.28  stations_group_1986.csv         1986
        4            BARCALDINE-POST-OFFICE   36007 -23.55  145.29  ...     35.93     37.41  stations_group_1986.csv         1986
        ...                             ...     ...    ...     ...  ...       ...       ...                      ...          ...
        2235  WILSONS-PROMONTORY-LIGHTHOUSE   85096 -39.13  146.42  ...     18.47     19.47  stations_group_2005.csv         2005
        2236                      WITTENOOM    5026 -22.24  118.34  ...     40.02     41.35  stations_group_2005.csv         2005
        2237              WOOMERA-AERODROME   16001 -31.16  136.81  ...     31.84     33.69  stations_group_2005.csv         2005
        2238            WYALONG-POST-OFFICE   73054 -33.93  147.24  ...     30.91     33.34  stations_group_2005.csv         2005
        2239            YAMBA-PILOT-STATION   58012 -29.43  153.36  ...     25.88     27.14  stations_group_2005.csv         2005
    """


def melt_months_to_long(df: pd.DataFrame) -> pd.DataFrame:
    id_vars = [c for c in ("STATION_NAME", "STN_ID", "LAT",
                           "LON", "SOURCE_FILE", "SOURCE_YEAR") if c in df.columns]
    long = df.melt(id_vars=id_vars, value_vars=MONTHS,
                   var_name="Month", value_name="Temperature")
    # convert to numeric (in case numeric strings) and coerce errors to NaN
    long["Temperature"] = pd.to_numeric(long["Temperature"], errors="coerce")
    return long
    """
    Output will be like this:
                                STATION_NAME  STN_ID    LAT     LON              SOURCE_FILE  SOURCE_YEAR     Month  Temperature
        0                 ADELAIDE-KENT-TOWN   23090 -34.92  138.62  stations_group_1986.csv         1986   January        31.48
        1          ALBANY-AIRPORT-COMPARISON    9741 -34.94  117.80  stations_group_1986.csv         1986   January        25.24
        2              ALICE-SPRINGS-AIRPORT   15590 -23.80  133.89  stations_group_1986.csv         1986   January        38.40
        3                       AMBERLEY-AMO   40004 -27.63  152.71  stations_group_1986.csv         1986   January        32.90
        4             BARCALDINE-POST-OFFICE   36007 -23.55  145.29  stations_group_1986.csv         1986   January        38.03
        ...                              ...     ...    ...     ...                      ...          ...       ...          ...
        26875  WILSONS-PROMONTORY-LIGHTHOUSE   85096 -39.13  146.42  stations_group_2005.csv         2005  December        19.47
        26876                      WITTENOOM    5026 -22.24  118.34  stations_group_2005.csv         2005  December        41.35
        26877              WOOMERA-AERODROME   16001 -31.16  136.81  stations_group_2005.csv         2005  December        33.69
        26878            WYALONG-POST-OFFICE   73054 -33.93  147.24  stations_group_2005.csv         2005  December        33.34
        26879            YAMBA-PILOT-STATION   58012 -29.43  153.36  stations_group_2005.csv         2005  December        27.14
    """


def compute_seasonal_average(long_df: pd.DataFrame) -> Dict[str, float]:
    # map months to seasons
    long_df = long_df.copy()
    long_df["Season"] = long_df["Month"].map(MONTH_TO_SEASON)

    # group and mean, automatically ignores NaN
    season_mean = long_df.groupby("Season", observed=True)[
        "Temperature"].mean()

    return season_mean


def format_temperature(value: float) -> str:
    """
    Format a temperature float to one decimal place.
    Handles NaN by returning 'NaN°C'.
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "NaN°C"
    return f"{round(value, ROUND_DECIMALS):.{ROUND_DECIMALS}f}°C"


def write_seasonal_average(results: Dict[str, float]) -> None:
    OUTPUT_SEASONAL = "average_temp.txt"
    with open(OUTPUT_SEASONAL, "w", encoding="utf-8") as fh:
        for season, val in results.items():
            fh.write(f"{season}: {format_temperature(val)}\n")
    print(f"Wrote seasonal averages to: {OUTPUT_SEASONAL}")


def compute_largest_temperature_range(long_df: pd.DataFrame):
    # grouping by station. using both name and id in grouping key to avoid same station merges
    group_cols = []
    if "STATION_NAME" in long_df.columns:
        group_cols.append("STATION_NAME")
    if "STN_ID" in long_df.columns:
        group_cols.append("STN_ID")

    # dropping rows that have NaN temperature before computing
    df_valid = long_df.dropna(subset=["Temperature"])
    agg = df_valid.groupby(group_cols, observed=True)[
        "Temperature"].agg(["max", "min"]).reset_index()
    if agg.empty:
        return []

    agg["range"] = agg["max"] - agg["min"]
    max_range = agg["range"].max()
    winners = agg[agg["range"] == max_range]

    results = []
    for _, row in winners.iterrows():
        name = row.get("STATION_NAME", "")
        stn_id = str(row.get("STN_ID", "")) if "STN_ID" in row.index else ""
        results.append((name, stn_id, float(
            row["range"]), float(row["max"]), float(row["min"])))
    return results


def write_largest_range(results) -> None:
    OUTPUT_RANGE = "largest_temp_range_station.txt"
    with open(OUTPUT_RANGE, "w", encoding="utf-8") as fh:
        if not results:
            fh.write("No data available\n")
            return
        for name, stn_id, rng, mx, mn in results:
            label = f"{name}" + \
                (f" (ID {stn_id})" if stn_id and stn_id != "nan" else "")
            fh.write(
                f"{label}: Range {format_temperature(rng)} (Max: {format_temperature(mx)}, Min: {format_temperature(mn)})\n")
    print(f"Wrote largest temperature range station(s) to: {OUTPUT_RANGE}")


def compute_temperature_stability(long_df: pd.DataFrame, ddof: int = 0):
    group_cols = []
    if "STATION_NAME" in long_df.columns:
        group_cols.append("STATION_NAME")
    if "STN_ID" in long_df.columns:
        group_cols.append("STN_ID")
    df_valid = long_df.dropna(subset=["Temperature"])
    # compute std per station
    stds = df_valid.groupby(group_cols, observed=True)["Temperature"].agg(
        lambda x: float(np.nan) if x.size == 0 else float(x.std(ddof=ddof))).reset_index()
    if stds.empty:
        return [], []

    # name the std column
    stds = stds.rename(columns={"Temperature": "StdDev"})
    min_std = stds["StdDev"].min()
    max_std = stds["StdDev"].max()

    most_stable = stds[stds["StdDev"] == min_std]
    most_variable = stds[stds["StdDev"] == max_std]

    def rows_to_tuples(df_rows):
        rows = []
        for _, r in df_rows.iterrows():
            name = r.get("STATION_NAME", "")
            stn_id = str(r.get("STN_ID", "")) if "STN_ID" in r.index else ""
            rows.append((name, stn_id, float(r["StdDev"])))
        return rows

    return rows_to_tuples(most_stable), rows_to_tuples(most_variable)


def main():
    # 1) find CSV files
    TEMPERATURES_FOLDER = "temperatures"
    files = find_csv_files(TEMPERATURES_FOLDER)

    # 2) load and concat
    combined = load_and_concat_csv(files)

    # 3) melt to long form
    long_df = melt_months_to_long(combined)

    # 4) seasonal averages
    seasonal = compute_seasonal_average(long_df)
    write_seasonal_average(seasonal)

    # 5) largest temperature range
    largest_ranges = compute_largest_temperature_range(long_df)
    write_largest_range(largest_ranges)


if __name__ == "__main__":
    main()
