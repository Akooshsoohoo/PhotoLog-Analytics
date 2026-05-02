import sqlite3
import pandas as pd

DB_PATH = "photos.db"

def load_monthly_counts():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """SELECT taken_year, taken_month, COUNT(*) as count
           FROM photos
           WHERE taken_year IS NOT NULL AND taken_month IS NOT NULL
           GROUP BY taken_year, taken_month
           ORDER BY taken_year, taken_month""",
        conn
    )
    conn.close()
    return df

if __name__ == "__main__":
    df = load_monthly_counts()
    print("Monthly photo counts:")
    print(df.to_string(index=False))
    print(f"\nTotal months in dataset: {len(df)}")
