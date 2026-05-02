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

    conn.close()

if __name__ == "__main__":
    main()
