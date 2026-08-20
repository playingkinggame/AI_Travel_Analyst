# AI Travel Analyst — Part 1: Exploration

## Project Overview
This project analyzes a flight pricing dataset to uncover the major factors
that drive flight ticket prices, and turns those findings into clear,
actionable insights. It covers Part 1 of the "AI Travel Analyst" brief:
data cleaning, exploratory visualization, and insight generation.

## Problem Statement
Raw flight pricing data is messy and hard to use directly — inconsistent
airline names, mixed date/duration formats, and airport codes mixed with
city names all make it difficult to compare prices meaningfully. This
project cleans the data and answers: **what actually drives flight prices,
and how can a traveler use that to book smarter?**

## Installation Instructions
1. Make sure you have Python 3.9+ installed.
2. Open this folder in VS Code.
3. (Recommended) create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the full pipeline:
   ```bash
   python main.py
   ```
   This cleans the data and regenerates every chart in `outputs/figures/`.

## Dataset Used
`data/flight_pricing_dataset.csv` — 100,000 rows, 18 columns, covering
domestic (India) and international flights with fields such as Airline,
Source, Destination, Departure/Arrival time, Duration, Total Stops,
Distance, Travel Class, Days Before Departure, Season, Weekday, Aircraft
Type, Booking Channel, Passenger Count, and Price.

## Methodology

### 1. Data Cleaning (`src/clean_data.py`)
The raw data had several real-world quality issues, all handled explicitly:
- **Airline names**: inconsistent casing (`AIR INDIA`, `air india`, `Air India`)
  → standardized to a single clean spelling per airline.
- **Source / Destination**: a mix of city names, IATA airport codes (`HYD`),
  and `"<City> Airport"` text all referring to the same place → mapped to a
  single clean city name using a lookup table.
- **Total_Stops**: mixed text/number formats (`"non-stop"`, `"0"`, `"1 stop"`,
  `"1"`) → normalized to numeric 0/1/2.
- **Duration**: written in **three different formats** in the same column —
  decimal hours (`"1.67"`), hour-minute text (`"3h 11m"`), and raw minutes
  (`"177 min"`) → all converted to a single `Duration_Minutes` numeric column.
- **Passenger_Count**: mixed digits and number-words (`"3"` vs `"three"`)
  → converted to numeric.
- **Departure_Time**: mixed 12-hour and 24-hour formats → parsed and bucketed
  into Morning / Afternoon / Evening / Night for easier analysis.
- **Missing values**: every column had ~5% missing values, including the
  target column (Price). Rows missing Price, or missing any of the key
  fields needed for analysis, were dropped rather than imputed, to avoid
  introducing bias into the price analysis.
- **Outliers**: extreme price outliers were removed using the IQR method
  (3×IQR bounds) to avoid a handful of erroneous entries skewing the charts.

Result: **71,289 clean, usable rows** out of the original 100,000.

### 2. Exploratory Analysis (`src/eda.py`)
Six visualizations were generated to explore what drives price
(see `outputs/figures/`):
1. Overall price distribution
2. Average price by airline
3. Price vs number of stops
4. Price vs days-before-departure (booking window)
5. Average price by season
6. Price by travel class

## Technologies Used
- Python 3
- pandas, numpy — data cleaning and manipulation
- matplotlib, seaborn — visualization

## Results — Key Insights
- **Domestic vs. international split dominates price.** The price
  distribution is clearly bimodal: budget domestic carriers (GoFirst,
  Indigo, AirAsia India, SpiceJet) cluster cheap, while international
  long-haul carriers (Etihad, Qatar Airways, Emirates, Singapore Airlines)
  cluster far higher — this single factor explains most of the price spread
  in the dataset.
- **Distance is the strongest numeric driver of price** (correlation ≈ 0.81
  with Price) — unsurprising, but confirms distance-based pricing dominates
  over most other factors.
- **More stops correlates with higher price**, not lower — non-stop flights
  average ~₹58,900 vs ~₹82,900 for 2-stop flights in this dataset, likely
  because non-stop routes are dominated by cheaper short-haul domestic
  flights, while multi-stop routes are more often longer international
  itineraries.
- **Booking earlier has only a weak effect on price** (correlation ≈ -0.11
  with days-before-departure) — a much weaker "book early to save" signal
  than commonly assumed, at least in this dataset.
- **Travel class is a major, predictable price driver**: Economy
  (~₹57k avg) → Premium Economy (~₹79k) → Business (~₹114k) → First
  (~₹131k) — a clear, consistent step up in price at each class tier.
- **Season has a smaller effect**, with Monsoon being the cheapest season
  on average — a much smaller effect than airline/class/distance.

## Challenges Faced
- The `Duration` column mixed three completely different formats in the
  same field, requiring a custom parser to unify them.
- Source/Destination values mixed city names, airport codes, and
  "Airport"-suffixed text for the same location, requiring a manual mapping
  table built from the dataset's actual unique values.
- Every column had a meaningful amount (~5%) of missing data, requiring a
  deliberate decision on where to drop vs. impute rather than blindly
  filling in values.

## Future Improvements
- Part 2: feature engineering + a price prediction model (e.g. Random
  Forest / Gradient Boosting) using the cleaned features here.
- Part 3: a booking-time recommender or price forecasting tool.
- An interactive dashboard (e.g. Streamlit) to explore prices by route.

## Screenshots
See `outputs/figures/` for all generated charts:
- `01_price_distribution.png`
- `02_avg_price_by_airline.png`
- `03_price_vs_stops.png`
- `04_price_vs_booking_window.png`
- `05_avg_price_by_season.png`
- `06_price_by_travel_class.png`