import sqlite3
import pandas as pd

DB_PATH = "photos.db"

def load_from_db(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
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

def write_features_to_db(df, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    rows = df[["taken_year", "taken_month", "taken_day", "taken_weekday", "taken_hour", "id"]].values.tolist()
    cursor.executemany("""
        UPDATE photos
        SET taken_year = ?, taken_month = ?, taken_day = ?,
            taken_weekday = ?, taken_hour = ?
        WHERE id = ?
    """, rows)

    conn.commit()
    conn.close()

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

def populate_daily_summary(df, db_path=DB_PATH):
    daily = df.groupby(["taken_year", "taken_month", "taken_day", "taken_weekday"]).agg(
        total_count=("title", "count"),
        photo_count=("media_type", lambda x: (x == "photo").sum()),
        video_count=("media_type", lambda x: (x == "video").sum()),
    ).reset_index()

    daily = flag_burst_days(daily)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daily_summary")

    rows = daily[["taken_year", "taken_month", "taken_day", "taken_weekday",
                   "total_count", "photo_count", "video_count", "burst_day"]].values.tolist()
    cursor.executemany("""
        INSERT INTO daily_summary
            (taken_year, taken_month, taken_day, taken_weekday,
             total_count, photo_count, video_count, burst_day)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)

    conn.commit()
    conn.close()
    print(f"Populated daily_summary with {len(daily)} rows")

if __name__ == "__main__":
    df = load_from_db(DB_PATH)
    print(f"Loaded {len(df)} rows")

    df = extract_time_features(df)
    df = drop_bad_rows(df)
    write_features_to_db(df, DB_PATH)
    populate_daily_summary(df, DB_PATH)
    print(df[["title", "photo_taken_ts", "taken_year", "taken_month", "taken_hour"]].head())
