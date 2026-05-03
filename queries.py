import sqlite3
import pandas as pd

DB_PATH = "photos.db"

def run_query(conn, label, sql):
    print(f"\n--- {label} ---")
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))

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

    conn.close()

if __name__ == "__main__":
    main()
