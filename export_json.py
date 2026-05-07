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

def build_data(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)

    yearly = query(conn, """
        SELECT taken_year as year, COUNT(*) as count
        FROM photos WHERE taken_year IS NOT NULL
        GROUP BY taken_year ORDER BY taken_year
    """)

    monthly = query(conn, """
        SELECT taken_month as month, COUNT(*) as count
        FROM photos WHERE taken_month IS NOT NULL
        GROUP BY taken_month ORDER BY taken_month
    """)

    hourly = query(conn, """
        SELECT taken_hour as hour, COUNT(*) as count
        FROM photos WHERE taken_hour IS NOT NULL
        GROUP BY taken_hour ORDER BY taken_hour
    """)

    weekday = query(conn, """
        SELECT taken_weekday as weekday, COUNT(*) as count
        FROM photos WHERE taken_weekday IS NOT NULL
        GROUP BY taken_weekday ORDER BY taken_weekday
    """)

    media = query(conn, """
        SELECT media_type, COUNT(*) as count
        FROM photos GROUP BY media_type
    """)

    burst = query(conn, """
        SELECT taken_year as year, COUNT(*) as burst_days
        FROM daily_summary WHERE burst_day = 1
        GROUP BY taken_year ORDER BY taken_year
    """)

    yoy = query(conn, """
        SELECT curr.taken_year as year,
               curr.count as this_year,
               prev.count as last_year,
               ROUND((curr.count - prev.count) * 100.0 / prev.count, 1) as pct_change
        FROM (SELECT taken_year, COUNT(*) as count FROM photos
              WHERE taken_year IS NOT NULL GROUP BY taken_year) curr
        LEFT JOIN (SELECT taken_year, COUNT(*) as count FROM photos
                   WHERE taken_year IS NOT NULL GROUP BY taken_year) prev
          ON curr.taken_year = prev.taken_year + 1
        ORDER BY curr.taken_year
    """)

    stats = query(conn, """
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN media_type = 'photo' THEN 1 ELSE 0 END) as total_photos,
            SUM(CASE WHEN media_type = 'video' THEN 1 ELSE 0 END) as total_videos,
            MIN(taken_year) as first_year,
            MAX(taken_year) as last_year
        FROM photos WHERE taken_year IS NOT NULL
    """)[0]

    daily_rows = query(conn, "SELECT taken_year, taken_month, taken_weekday, total_count FROM daily_summary")
    if daily_rows:
        import statistics
        counts = [r["total_count"] for r in daily_rows]
        q1, q3 = statistics.quantiles(counts, n=4)[0], statistics.quantiles(counts, n=4)[2]
        stats["burst_threshold"] = round(q3 + 1.5 * (q3 - q1), 1)

        def pearson(xs, ys):
            n = len(xs)
            mx, my = sum(xs)/n, sum(ys)/n
            num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
            den = (sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys)) ** 0.5
            return round(num/den, 4) if den else 0

        years    = [r["taken_year"]    for r in daily_rows]
        months   = [r["taken_month"]   for r in daily_rows]
        weekdays = [r["taken_weekday"] for r in daily_rows]
        stats["correlations"] = {
            "weekday": pearson(weekdays, counts),
            "month":   pearson(months,   counts),
            "year":    pearson(years,    counts),
        }
    else:
        stats["burst_threshold"] = None
        stats["correlations"] = {"weekday": 0, "month": 0, "year": 0}

    years = [r["year"] for r in yearly]
    by_year = {}
    for yr in years:
        by_year[str(yr)] = {
            "monthly": query(conn, f"""
                SELECT taken_month as month, COUNT(*) as count
                FROM photos WHERE taken_year = {yr} AND taken_month IS NOT NULL
                GROUP BY taken_month ORDER BY taken_month
            """),
            "hourly": query(conn, f"""
                SELECT taken_hour as hour, COUNT(*) as count
                FROM photos WHERE taken_year = {yr} AND taken_hour IS NOT NULL
                GROUP BY taken_hour ORDER BY taken_hour
            """),
            "weekday": query(conn, f"""
                SELECT taken_weekday as weekday, COUNT(*) as count
                FROM photos WHERE taken_year = {yr} AND taken_weekday IS NOT NULL
                GROUP BY taken_weekday ORDER BY taken_weekday
            """),
        }

    conn.close()

    data = {
        "yearly": yearly,
        "monthly": monthly,
        "hourly": hourly,
        "weekday": weekday,
        "media": media,
        "burst": burst,
        "yoy": yoy,
        "stats": stats,
        "by_year": by_year,
    }

    return data

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    data = build_data(DB_PATH)
    out_path = os.path.join(OUT_DIR, "photos.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Exported data to {out_path}")

if __name__ == "__main__":
    main()
