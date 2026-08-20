import pandas as pd
import matplotlib
matplotlib.use("Agg")  # no display needed, just save files
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
FIG_DIR = "outputs/figures"


def save(fig, name):
    fig.savefig(f"{FIG_DIR}/{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {FIG_DIR}/{name}.png")


def plot_price_distribution(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df["Price"], bins=50, kde=True, ax=ax, color="#3b82f6")
    ax.set_title("Distribution of Flight Prices")
    ax.set_xlabel("Price (INR)")
    ax.set_ylabel("Number of Flights")
    save(fig, "01_price_distribution")


def plot_price_by_airline(df):
    order = df.groupby("Airline")["Price"].mean().sort_values(ascending=False).index
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df, x="Price", y="Airline", order=order, ax=ax, color="#3b82f6")
    ax.set_title("Average Flight Price by Airline")
    ax.set_xlabel("Average Price (INR)")
    ax.set_ylabel("")
    save(fig, "02_avg_price_by_airline")


def plot_price_vs_stops(df):
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=df, x="Total_Stops", y="Price", ax=ax, color="#93c5fd")
    ax.set_title("Price vs Number of Stops")
    ax.set_xlabel("Number of Stops")
    ax.set_ylabel("Price (INR)")
    save(fig, "03_price_vs_stops")


def plot_price_vs_booking_window(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    sample = df.sample(min(8000, len(df)), random_state=42)
    sns.scatterplot(data=sample, x="Days_Before_Departure", y="Price",
                     alpha=0.25, ax=ax, color="#3b82f6", s=15)
    sns.regplot(data=df, x="Days_Before_Departure", y="Price", scatter=False,
                ax=ax, color="red")
    ax.set_title("Price vs Days Before Departure (Booking Window)")
    ax.set_xlabel("Days Before Departure")
    ax.set_ylabel("Price (INR)")
    save(fig, "04_price_vs_booking_window")


def plot_price_by_season(df):
    fig, ax = plt.subplots(figsize=(7, 5))
    order = ["Winter", "Summer", "Monsoon", "Autumn"]
    order = [o for o in order if o in df["Season"].unique()]
    sns.barplot(data=df, x="Season", y="Price", order=order, ax=ax, color="#3b82f6")
    ax.set_title("Average Flight Price by Season")
    ax.set_xlabel("Season")
    ax.set_ylabel("Average Price (INR)")
    save(fig, "05_avg_price_by_season")


def plot_price_by_class(df):
    order = ["Economy", "Premium Economy", "Business", "First"]
    order = [o for o in order if o in df["Travel_Class"].unique()]
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=df, x="Travel_Class", y="Price", order=order, ax=ax, color="#93c5fd")
    ax.set_title("Price by Travel Class")
    ax.set_xlabel("Travel Class")
    ax.set_ylabel("Price (INR)")
    save(fig, "06_price_by_travel_class")


def print_insights(df):
    print("\n" + "=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)

    cheapest_airline = df.groupby("Airline")["Price"].mean().idxmin()
    priciest_airline = df.groupby("Airline")["Price"].mean().idxmax()
    print(f"- Cheapest airline on average : {cheapest_airline}")
    print(f"- Most expensive airline      : {priciest_airline}")

    stop_corr = df.groupby("Total_Stops")["Price"].mean()
    print(f"- Avg price, non-stop flights : Rs {stop_corr.get(0, float('nan')):.0f}")
    print(f"- Avg price, 2-stop flights   : Rs {stop_corr.get(2, float('nan')):.0f}")

    corr_days = df["Days_Before_Departure"].corr(df["Price"])
    print(f"- Correlation (days-before-departure vs price): {corr_days:.3f}")

    corr_dist = df["Distance_km"].corr(df["Price"])
    print(f"- Correlation (distance vs price): {corr_dist:.3f}")

    cheapest_season = df.groupby("Season")["Price"].mean().idxmin()
    print(f"- Cheapest season on average   : {cheapest_season}")

    class_price = df.groupby("Travel_Class")["Price"].mean().sort_values()
    print(f"- Price range by class         : {class_price.round(0).to_dict()}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    df = pd.read_csv("outputs/cleaned_data.csv")

    plot_price_distribution(df)
    plot_price_by_airline(df)
    plot_price_vs_stops(df)
    plot_price_vs_booking_window(df)
    plot_price_by_season(df)
    plot_price_by_class(df)

    print_insights(df)
