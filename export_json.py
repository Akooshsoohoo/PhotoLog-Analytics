import sqlite3
import json
import os

DB_PATH = "photos.db"
OUT_DIR = "web/data"

def query(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, row)) for row in cursor.fetchall()]

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # total photos per year
    yearly = query(conn, """
        SELECT taken_year as year, COUNT(*) as count
        FROM photos WHERE taken_year IS NOT NULL
        GROUP BY taken_year ORDER BY taken_year
    """)

    # photos per month (all years combined)
    monthly = query(conn, """
        SELECT taken_month as month, COUNT(*) as count
        FROM photos WHERE taken_month IS NOT NULL
        GROUP BY taken_month ORDER BY taken_month
    """)

    # hour of day distribution
    hourly = query(conn, """
        SELECT taken_hour as hour, COUNT(*) as count
        FROM photos WHERE taken_hour IS NOT NULL
        GROUP BY taken_hour ORDER BY taken_hour
    """)

    # day of week distribution
    weekday = query(conn, """
        SELECT taken_weekday as weekday, COUNT(*) as count
        FROM photos WHERE taken_weekday IS NOT NULL
        GROUP BY taken_weekday ORDER BY taken_weekday
    """)

    # media type breakdown
    media = query(conn, """
        SELECT media_type, COUNT(*) as count
        FROM photos GROUP BY media_type
    """)

    # summary stats
    stats = query(conn, """
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN media_type = 'photo' THEN 1 ELSE 0 END) as total_photos,
            SUM(CASE WHEN media_type = 'video' THEN 1 ELSE 0 END) as total_videos,
            MIN(taken_year) as first_year,
            MAX(taken_year) as last_year
        FROM photos WHERE taken_year IS NOT NULL
    """)[0]

    conn.close()

    data = {
        "yearly": yearly,
        "monthly": monthly,
        "hourly": hourly,
        "weekday": weekday,
        "media": media,
        "stats": stats,
    }

    out_path = os.path.join(OUT_DIR, "photos.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Exported data to {out_path}")

if __name__ == "__main__":
    main()
