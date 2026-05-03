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

def write_features_to_db(df):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            UPDATE photos
            SET taken_year = ?, taken_month = ?, taken_day = ?,
                taken_weekday = ?, taken_hour = ?
            WHERE id = ?
        """, (row["taken_year"], row["taken_month"], row["taken_day"],
              row["taken_weekday"], row["taken_hour"], row["id"]))

    conn.commit()
    conn.close()
    print("Done writing features to database")

def drop_bad_rows(df):
    before = len(df)
    df = df[df["photo_taken_ts"] > 0]
    df = df.dropna(subset=["photo_taken_ts"])
    df = df.drop_duplicates(subset=["title", "photo_taken_ts"])
    after = len(df)
    print(f"Dropped {before - after} rows (nulls + duplicates), {after} remaining")
    return df

def flag_burst_days(daily_df):
    q1 = daily_df["total_count"].quantile(0.25)
    q3 = daily_df["total_count"].quantile(0.75)
    iqr = q3 - q1
    threshold = q3 + 1.5 * iqr
    daily_df["burst_day"] = (daily_df["total_count"] > threshold).astype(int)
    burst_count = daily_df["burst_day"].sum()
    print(f"Flagged {burst_count} burst days (IQR threshold: {threshold:.1f} photos/day)")
    return daily_df

def populate_daily_summary(df):
    daily = df.groupby(["taken_year", "taken_month", "taken_day", "taken_weekday"]).agg(
        total_count=("title", "count"),
        photo_count=("media_type", lambda x: (x == "photo").sum()),
        video_count=("media_type", lambda x: (x == "video").sum()),
    ).reset_index()

    daily = flag_burst_days(daily)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daily_summary")

    for _, row in daily.iterrows():
        cursor.execute("""
            INSERT INTO daily_summary
                (taken_year, taken_month, taken_day, taken_weekday,
                 total_count, photo_count, video_count, burst_day)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (int(row["taken_year"]), int(row["taken_month"]), int(row["taken_day"]),
              int(row["taken_weekday"]), int(row["total_count"]),
              int(row["photo_count"]), int(row["video_count"]), int(row["burst_day"])))

    conn.commit()
    conn.close()
    print(f"Populated daily_summary with {len(daily)} rows")

if __name__ == "__main__":
    df = load_from_db()
    print(f"Loaded {len(df)} rows")

    df = extract_time_features(df)
    df = drop_bad_rows(df)
    write_features_to_db(df)
    populate_daily_summary(df)
    print(df[["title", "photo_taken_ts", "taken_year", "taken_month", "taken_hour"]].head())
