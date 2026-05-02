import sqlite3
import pandas as pd

DB_PATH = "photos.db"

def load_from_db():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM photos", conn)
    conn.close()
    return df

def extract_time_features(df):
    df["dt"] = pd.to_datetime(df["photo_taken_ts"], unit="s", errors="coerce")
    df["taken_year"] = df["dt"].dt.year
    df["taken_month"] = df["dt"].dt.month
    df["taken_day"] = df["dt"].dt.day
    df["taken_weekday"] = df["dt"].dt.weekday  # 0=Monday, 6=Sunday
    df["taken_hour"] = df["dt"].dt.hour
    return df

def drop_bad_rows(df):
    before = len(df)
    df = df[df["photo_taken_ts"] > 0]
    df = df.dropna(subset=["photo_taken_ts"])
    df = df.drop_duplicates(subset=["title", "photo_taken_ts"])
    after = len(df)
    print(f"Dropped {before - after} rows (nulls + duplicates), {after} remaining")
    return df

if __name__ == "__main__":
    df = load_from_db()
    print(f"Loaded {len(df)} rows")

    df = extract_time_features(df)
    df = drop_bad_rows(df)
    print(df[["title", "photo_taken_ts", "taken_year", "taken_month", "taken_hour"]].head())
