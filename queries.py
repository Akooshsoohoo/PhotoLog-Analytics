import sqlite3
import pandas as pd
from datetime import timedelta

DB_PATH = "photos.db"

def run_query(conn, label, sql):
    print(f"\n--- {label} ---")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))

def streak_analysis(conn):
    df = pd.read_sql_query(
        """SELECT DISTINCT taken_year, taken_month, taken_day
           FROM photos
           WHERE taken_year IS NOT NULL
           ORDER BY taken_year, taken_month, taken_day""",
        conn
    )

    df["date"] = pd.to_datetime(df[["taken_year", "taken_month", "taken_day"]].rename(
        columns={"taken_year": "year", "taken_month": "month", "taken_day": "day"}
    ))

    df = df.sort_values("date").reset_index(drop=True)
    df["diff"] = df["date"].diff()

    streak = 1
    best = 1
    best_start = df["date"].iloc[0]
    cur_start = df["date"].iloc[0]

    for i in range(1, len(df)):
        if df["diff"].iloc[i] == timedelta(days=1):
            streak += 1
            if streak > best:
                best = streak
                best_start = cur_start
        else:
            streak = 1
            cur_start = df["date"].iloc[i]

    gaps = df[df["diff"] > timedelta(days=1)].copy()
    gaps["gap_days"] = gaps["diff"].dt.days
    longest_gap = gaps.nlargest(1, "gap_days").iloc[0]

    print("\n--- Streak Analysis ---")
    print(f"Longest streak:  {best} consecutive days (starting {best_start.date()})")
    print(f"Longest gap:     {int(longest_gap['gap_days'])} days (ending {longest_gap['date'].date()})")
    print(f"Total active days: {len(df)}")

def main():
    conn = sqlite3.connect(DB_PATH)

    run_query(conn, "Total photos per year",
        "SELECT taken_year, COUNT(*) as count FROM photos WHERE taken_year IS NOT NULL GROUP BY taken_year ORDER BY taken_year")

    run_query(conn, "Photo vs video breakdown",
        "SELECT media_type, COUNT(*) as count FROM photos GROUP BY media_type")

    run_query(conn, "Most active month (overall)",
        """SELECT taken_month, COUNT(*) as count FROM photos
           WHERE taken_month IS NOT NULL
           GROUP BY taken_month ORDER BY count DESC LIMIT 5""")

    run_query(conn, "Most common hour of day",
        """SELECT taken_hour, COUNT(*) as count FROM photos
           WHERE taken_hour IS NOT NULL
           GROUP BY taken_hour ORDER BY count DESC LIMIT 5""")

    run_query(conn, "Average photos per weekday",
        """SELECT taken_weekday,
                  ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT taken_year || '-' || taken_month || '-' || taken_day), 2) as avg_per_day
           FROM photos WHERE taken_weekday IS NOT NULL
           GROUP BY taken_weekday ORDER BY taken_weekday""")

    run_query(conn, "Burst days by year",
        """SELECT taken_year, COUNT(*) as burst_days
           FROM daily_summary WHERE burst_day = 1
           GROUP BY taken_year ORDER BY taken_year""")

    run_query(conn, "Year-over-year photo count change",
        """SELECT curr.taken_year,
                  curr.count as this_year,
                  prev.count as last_year,
                  ROUND((curr.count - prev.count) * 100.0 / prev.count, 1) as pct_change
           FROM (SELECT taken_year, COUNT(*) as count FROM photos
                 WHERE taken_year IS NOT NULL GROUP BY taken_year) curr
           LEFT JOIN (SELECT taken_year, COUNT(*) as count FROM photos
                      WHERE taken_year IS NOT NULL GROUP BY taken_year) prev
             ON curr.taken_year = prev.taken_year + 1
           ORDER BY curr.taken_year""")

    run_query(conn, "Days with above-average photo count",
        """SELECT taken_year, taken_month, taken_day, total_count
           FROM daily_summary
           WHERE total_count > (SELECT AVG(total_count) FROM daily_summary)
           ORDER BY total_count DESC
           LIMIT 10""")

    run_query(conn, "Top month per year (subquery)",
        """SELECT taken_year, taken_month, count FROM (
               SELECT taken_year, taken_month, COUNT(*) as count,
                      RANK() OVER (PARTITION BY taken_year ORDER BY COUNT(*) DESC) as rnk
               FROM photos WHERE taken_year IS NOT NULL
               GROUP BY taken_year, taken_month
           ) WHERE rnk = 1
           ORDER BY taken_year""")

    run_query(conn, "Daily summary joined with photo details (top 5 busiest days)",
        """SELECT d.taken_year, d.taken_month, d.taken_day,
                  d.total_count, d.photo_count, d.video_count,
                  p.device_type
           FROM daily_summary d
           JOIN photos p
             ON d.taken_year = p.taken_year
            AND d.taken_month = p.taken_month
            AND d.taken_day = p.taken_day
           GROUP BY d.taken_year, d.taken_month, d.taken_day
           ORDER BY d.total_count DESC
           LIMIT 5""")

    streak_analysis(conn)

    run_query(conn, "Photos by season",
        """SELECT
               CASE
                   WHEN taken_month IN (12, 1, 2) THEN 'Winter'
                   WHEN taken_month IN (3, 4, 5)  THEN 'Spring'
                   WHEN taken_month IN (6, 7, 8)  THEN 'Summer'
                   ELSE 'Fall'
               END as season,
               COUNT(*) as count
           FROM photos
           WHERE taken_month IS NOT NULL
           GROUP BY season
           ORDER BY count DESC""")

    conn.close()

if __name__ == "__main__":
    main()
