import json
import os
import pandas as pd

import parse_data
import clean_data
import queries
import visualizations
import ml_models
import export_json

def main():
    print("=== Step 1: Parsing Takeout JSON files ===")
    parse_data.main()

    print("\n=== Step 2: Cleaning data and extracting features ===")
    df = clean_data.load_from_db()
    df = clean_data.extract_time_features(df)
    df = clean_data.drop_bad_rows(df)
    clean_data.write_features_to_db(df)

    print("\n=== Step 3: Running SQL queries ===")
    queries.main()

    print("\n=== Step 4: Generating visualizations ===")
    viz_df = visualizations.load_data()
    visualizations.plot_monthly_trend(viz_df)
    visualizations.plot_hourly_distribution(viz_df)
    visualizations.plot_weekday_distribution(viz_df)
    visualizations.plot_media_type_pie(viz_df)
    visualizations.plot_seasonal_breakdown(viz_df)

    print("\n=== Step 5: Running ML models ===")
    monthly_df = ml_models.load_monthly_counts()
    ml_models.run_linear_regression(monthly_df)
    daily_df = ml_models.load_daily_counts()
    ml_models.run_logistic_regression(daily_df)
    ml_models.run_kmeans_clustering(monthly_df)

    print("\n=== Step 6: Exporting data for web dashboard ===")
    export_json.main()

    print("\n=== Done ===")

if __name__ == "__main__":
    main()
