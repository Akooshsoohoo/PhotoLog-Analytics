import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report

DB_PATH = "photos.db"

def load_daily_counts():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """SELECT taken_year, taken_month, taken_day, taken_weekday,
                  COUNT(*) as count
           FROM photos
           WHERE taken_year IS NOT NULL
           GROUP BY taken_year, taken_month, taken_day""",
        conn
    )
    conn.close()
    return df

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

def show_correlations(daily_df):
    features = ["taken_weekday", "taken_month", "taken_year", "count"]
    corr = daily_df[features].corr()["count"].drop("count")

    print("\n--- Feature Correlation with Daily Photo Count ---")
    for feat, val in corr.items():
        print(f"  {feat:<20} {val:+.4f}")

def run_logistic_regression(daily_df):
    median = daily_df["count"].median()
    daily_df["high_activity"] = (daily_df["count"] > median).astype(int)

    X = daily_df[["taken_weekday", "taken_month"]]
    y = daily_df["high_activity"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print("\n--- Logistic Regression: High vs Low Activity Day ---")
    print(f"Median photos/day threshold: {median}")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred, target_names=["low", "high"]))

if __name__ == "__main__":
    monthly_df = load_monthly_counts()
    print("Monthly photo counts:")
    print(monthly_df.to_string(index=False))
    print(f"\nTotal months in dataset: {len(monthly_df)}")
    run_linear_regression(monthly_df)

    daily_df = load_daily_counts()
    show_correlations(daily_df)
    run_logistic_regression(daily_df)
