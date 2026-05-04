import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

DB_PATH = "photos.db"
PLOTS_DIR = "plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM photos WHERE taken_year IS NOT NULL",
        conn
    )
    conn.close()
    return df

def plot_monthly_trend(df):
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    years = sorted(df["taken_year"].unique())
    x = range(1, 13)
    width = 0.2

    plt.figure(figsize=(12, 5))
    for i, year in enumerate(years):
        year_df = df[df["taken_year"] == year]
        counts = year_df.groupby("taken_month").size().reindex(range(1, 13), fill_value=0)
        offset = [xi + i * width for xi in x]
        plt.bar(offset, counts.values, width=width, label=str(year))

    plt.xticks([xi + width for xi in x], month_names)
    plt.xlabel("Month")
    plt.ylabel("Number of Photos")
    plt.title("Monthly Photo Count by Year")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "monthly_trend.png"))
    plt.close()
    print("Saved monthly_trend.png")

def plot_hourly_distribution(df):
    hour_counts = df.groupby("taken_hour").size().reindex(range(24), fill_value=0)

    plt.figure(figsize=(10, 4))
    plt.bar(range(24), hour_counts.values)
    plt.xlabel("Hour of Day (UTC)")
    plt.ylabel("Number of Photos")
    plt.title("Photo Activity by Hour of Day")
    plt.xticks(range(24))
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "hourly_distribution.png"))
    plt.close()
    print("Saved hourly_distribution.png")

def plot_weekday_distribution(df):
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    counts = df.groupby("taken_weekday").size().reindex(range(7), fill_value=0)

    plt.figure(figsize=(8, 4))
    plt.bar(day_names, counts.values)
    plt.xlabel("Day of Week")
    plt.ylabel("Number of Photos")
    plt.title("Photo Count by Day of Week")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "weekday_distribution.png"))
    plt.close()
    print("Saved weekday_distribution.png")

def plot_media_type_pie(df):
    counts = df["media_type"].value_counts()

    plt.figure(figsize=(6, 6))
    plt.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90)
    plt.title("Photo vs Video Breakdown")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "media_type_breakdown.png"))
    plt.close()
    print("Saved media_type_breakdown.png")

def plot_seasonal_breakdown(df):
    def get_season(month):
        if month in (12, 1, 2): return "Winter"
        if month in (3, 4, 5):  return "Spring"
        if month in (6, 7, 8):  return "Summer"
        return "Fall"

    df = df.copy()
    df["season"] = df["taken_month"].apply(get_season)
    order = ["Spring", "Summer", "Fall", "Winter"]
    counts = df.groupby("season").size().reindex(order, fill_value=0)

    plt.figure(figsize=(7, 4))
    plt.bar(counts.index, counts.values, color=["#a8d8a8", "#f9c74f", "#f4845f", "#90c7e8"])
    plt.xlabel("Season")
    plt.ylabel("Number of Photos")
    plt.title("Photo Count by Season")
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "seasonal_breakdown.png"))
    plt.close()
    print("Saved seasonal_breakdown.png")

if __name__ == "__main__":
    df = load_data()
    plot_monthly_trend(df)
    plot_hourly_distribution(df)
    plot_weekday_distribution(df)
    plot_media_type_pie(df)
    plot_seasonal_breakdown(df)
