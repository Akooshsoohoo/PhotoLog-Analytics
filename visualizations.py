import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import os

DB_PATH = "photos.db"
PLOTS_DIR = "plots"

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

if __name__ == "__main__":
    df = load_data()
    plot_monthly_trend(df)
