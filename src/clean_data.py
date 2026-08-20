import re
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------
# Lookup tables built from inspecting the actual unique values in the
# dataset (airport codes / "X Airport" variants -> a single city name)
# ---------------------------------------------------------------------
CITY_MAP = {
    "AMD": "Ahmedabad", "AHMEDABAD AIRPORT": "Ahmedabad", "AHMEDABAD": "Ahmedabad",
    "BKK": "Bangkok", "BANGKOK AIRPORT": "Bangkok", "BANGKOK": "Bangkok",
    "BLR": "Bangalore", "BANGALORE AIRPORT": "Bangalore", "BANGALORE": "Bangalore",
    "BOM": "Mumbai", "MUMBAI AIRPORT": "Mumbai", "MUMBAI": "Mumbai",
    "CCU": "Kolkata", "KOLKATA AIRPORT": "Kolkata", "KOLKATA": "Kolkata",
    "DEL": "Delhi", "DELHI AIRPORT": "Delhi", "DELHI": "Delhi",
    "DOH": "Doha", "DOHA AIRPORT": "Doha", "DOHA": "Doha",
    "DXB": "Dubai", "DUBAI AIRPORT": "Dubai", "DUBAI": "Dubai",
    "FRA": "Frankfurt", "FRANKFURT AIRPORT": "Frankfurt", "FRANKFURT": "Frankfurt",
    "GOI": "Goa", "GOA AIRPORT": "Goa", "GOA": "Goa",
    "HYD": "Hyderabad", "HYDERABAD AIRPORT": "Hyderabad", "HYDERABAD": "Hyderabad",
    "JAI": "Jaipur", "JAIPUR AIRPORT": "Jaipur", "JAIPUR": "Jaipur",
    "JFK": "New York", "NEW YORK AIRPORT": "New York", "NEW YORK": "New York",
    "LHR": "London", "LONDON AIRPORT": "London", "LONDON": "London",
    "MAA": "Chennai", "CHENNAI AIRPORT": "Chennai", "CHENNAI": "Chennai",
    "PNQ": "Pune", "PUNE AIRPORT": "Pune", "PUNE": "Pune",
    "SIN": "Singapore", "SINGAPORE AIRPORT": "Singapore", "SINGAPORE": "Singapore",
    "SYD": "Sydney", "SYDNEY AIRPORT": "Sydney", "SYDNEY": "Sydney",
}

WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
}


def clean_airline(series: pd.Series) -> pd.Series:
    """Standardize airline casing, e.g. 'AIR INDIA' / 'air india' -> 'Air India'."""
    return series.str.strip().str.title().replace({
        "Airasia India": "AirAsia India",
        "Gofirst": "GoFirst",
        "Spicejet": "SpiceJet",
    })


def clean_city(series: pd.Series) -> pd.Series:
    """Map airport codes and '<City> Airport' text to a single clean city name."""
    return series.str.strip().str.upper().map(CITY_MAP).fillna(series)


def clean_stops(series: pd.Series) -> pd.Series:
    """Normalize Total_Stops to a numeric 0 / 1 / 2 value."""
    def _parse(val):
        if pd.isna(val):
            return np.nan
        val = str(val).strip().lower()
        if val in ("0", "non-stop", "nonstop"):
            return 0
        if val in ("1", "1 stop"):
            return 1
        if val in ("2", "2 stops"):
            return 2
        try:
            return int(val)
        except ValueError:
            return np.nan
    return series.map(_parse)


def duration_to_minutes(val) -> float:
    """Convert any of the 3 raw Duration formats into total minutes."""
    if pd.isna(val):
        return np.nan
    val = str(val).strip()

    # Format: "177 min"
    m = re.match(r"^(\d+)\s*min$", val)
    if m:
        return float(m.group(1))

    # Format: "3h 11m" / "0h 45m"
    m = re.match(r"^(\d+)h\s*(\d+)m$", val)
    if m:
        hours, mins = int(m.group(1)), int(m.group(2))
        return hours * 60 + mins

    # Format: "1.67"  (decimal hours)
    m = re.match(r"^\d+(\.\d+)?$", val)
    if m:
        return float(val) * 60

    return np.nan


def clean_passenger_count(series: pd.Series) -> pd.Series:
    """Convert number-words ('three') to digits and cast to numeric."""
    def _parse(val):
        if pd.isna(val):
            return np.nan
        val = str(val).strip().lower()
        if val in WORD_TO_NUM:
            return WORD_TO_NUM[val]
        try:
            return int(val)
        except ValueError:
            return np.nan
    return series.map(_parse)


def time_to_bucket(val) -> str:
    """Bucket a departure time string (12h or 24h format) into a part of day."""
    if pd.isna(val):
        return np.nan
    val = str(val).strip()
    try:
        if "AM" in val.upper() or "PM" in val.upper():
            t = pd.to_datetime(val, format="%I:%M %p", errors="coerce")
        else:
            t = pd.to_datetime(val, format="%H:%M", errors="coerce")
        if pd.isna(t):
            return np.nan
        hour = t.hour
    except Exception:
        return np.nan

    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"


def load_and_clean(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)

    # ---- Price: numeric, drop rows with missing Price (our target) ----
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df = df.dropna(subset=["Price"]).copy()

    # ---- Categorical / text cleanup ----
    df["Airline"] = clean_airline(df["Airline"])
    df["Source"] = clean_city(df["Source"])
    df["Destination"] = clean_city(df["Destination"])
    df["Total_Stops"] = clean_stops(df["Total_Stops"])
    df["Duration_Minutes"] = df["Duration"].map(duration_to_minutes)
    df["Passenger_Count"] = clean_passenger_count(df["Passenger_Count"])
    df["Departure_TimeOfDay"] = df["Departure_Time"].map(time_to_bucket)

    # ---- Numeric columns ----
    df["Distance_km"] = pd.to_numeric(df["Distance_km"], errors="coerce")
    df["Days_Before_Departure"] = pd.to_numeric(df["Days_Before_Departure"], errors="coerce")

    # ---- Drop rows that are missing too much to be useful ----
    key_cols = ["Airline", "Source", "Destination", "Total_Stops",
                "Duration_Minutes", "Price"]
    df = df.dropna(subset=key_cols).copy()

    # ---- Remove obvious outliers using the IQR method on Price ----
    q1, q3 = df["Price"].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - 3 * iqr, q3 + 3 * iqr
    df = df[(df["Price"] >= lower) & (df["Price"] <= upper)].copy()

    # ---- Drop the now-redundant raw Duration column ----
    df = df.drop(columns=["Duration"])

    df = df.reset_index(drop=True)
    return df


if __name__ == "__main__":
    cleaned = load_and_clean("data/flight_pricing_dataset.csv")
    cleaned.to_csv("outputs/cleaned_data.csv", index=False)
    print(f"Cleaned dataset saved: {cleaned.shape[0]} rows, {cleaned.shape[1]} columns")
    print(cleaned.head())
