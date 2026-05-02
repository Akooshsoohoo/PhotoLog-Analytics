import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

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

def run_linear_regression(df):
    X = df[["taken_year", "taken_month"]]
    y = df["count"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print("\n--- Linear Regression: Predict Monthly Photo Count ---")
    print(f"MSE: {mse:.2f}")
    print(f"R²:  {r2:.4f}")

if __name__ == "__main__":
    df = load_monthly_counts()
    print("Monthly photo counts:")
    print(df.to_string(index=False))
    print(f"\nTotal months in dataset: {len(df)}")
    run_linear_regression(df)
