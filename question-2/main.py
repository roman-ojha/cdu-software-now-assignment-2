from __future__ import annotations
import os
import glob
import re
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np


TEMPERATURES_FOLDER = "temperatures"


# months present in CSV in this exact order (from sample CSV)
MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def find_csv_files(folder: str) -> List[str]:
    """
    Return list of CSV file paths in the given folder. Uses glob to match *.csv.
    """
    pattern = os.path.join(folder, "*.csv")
    files = sorted(glob.glob(pattern))
    return files


def load_and_concat_csv(files: List[str]) -> pd.DataFrame:
    """
    Load CSV files into a single DataFrame.

    Each CSV is expected to contain columns:
    STATION_NAME, STN_ID, LAT, LON, January, February, ..., December

    Adds a 'SOURCE_FILE' column set to the filename (useful for debugging).
    Returns concatenated DataFrame.
    """
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
    """
    Convert wide table (one row per station with 12 month columns) to long format:
    columns: STATION_NAME, STN_ID, LAT, LON, month, temperature, SOURCE_FILE, SOURCE_YEAR

    Temperatures are converted to numeric and NaNs are preserved for later ignoring.
    """
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


def main():

    # 1) find CSV files
    files = find_csv_files(TEMPERATURES_FOLDER)

    # 2) load and concat
    combined = load_and_concat_csv(files)

    # 3) melt to long form
    long_df = melt_months_to_long(combined)
    print(long_df)


if __name__ == "__main__":
    main()
