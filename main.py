"""
main.py
-------
Runs the full Part 1 pipeline end to end:
  1. Cleans the raw dataset          (src/clean_data.py)
  2. Generates visualizations + insights (src/eda.py)

Usage:
    python main.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from clean_data import load_and_clean
from eda import (
    plot_price_distribution,
    plot_price_by_airline,
    plot_price_vs_stops,
    plot_price_vs_booking_window,
    plot_price_by_season,
    plot_price_by_class,
    print_insights,
)


def main():
    os.makedirs("outputs/figures", exist_ok=True)

    print("Step 1/2: Cleaning data...")
    df = load_and_clean("data/flight_pricing_dataset.csv")
    df.to_csv("outputs/cleaned_data.csv", index=False)
    print(f"  -> {df.shape[0]} rows, {df.shape[1]} columns after cleaning\n")

    print("Step 2/2: Running EDA and generating charts...")
    plot_price_distribution(df)
    plot_price_by_airline(df)
    plot_price_vs_stops(df)
    plot_price_vs_booking_window(df)
    plot_price_by_season(df)
    plot_price_by_class(df)

    print_insights(df)
    print("Done! Charts saved in outputs/figures/, cleaned data in outputs/cleaned_data.csv")


if __name__ == "__main__":
    main()
