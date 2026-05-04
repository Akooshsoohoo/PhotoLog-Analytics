import json
import os
import pandas as pd

import parse_data
import clean_data
import queries
import visualizations
import ml_models
import export_json

DB_PATH = "photos.db"

def main():
    print("parsing takeout json files...")
    parse_data.main()

    print("cleaning + feature extraction...")
    df = clean_data.load_from_db(DB_PATH)
    df = clean_data.extract_time_features(df)
    df = clean_data.drop_bad_rows(df)
    clean_data.write_features_to_db(df, DB_PATH)
    clean_data.populate_daily_summary(df, DB_PATH)

    print("running queries...")
    queries.main()

    print("generating visualizations...")
    viz_df = visualizations.load_data()
    visualizations.plot_monthly_trend(viz_df)
    visualizations.plot_hourly_distribution(viz_df)
    visualizations.plot_weekday_distribution(viz_df)
    visualizations.plot_media_type_pie(viz_df)
    visualizations.plot_seasonal_breakdown(viz_df)

    print("running ML models...")
    monthly_df = ml_models.load_monthly_counts()
    ml_models.run_linear_regression(monthly_df)
    daily_df = ml_models.load_daily_counts()
    ml_models.run_logistic_regression(daily_df)
    ml_models.run_kmeans_clustering(monthly_df)

    print("exporting to web...")
    export_json.main()

if __name__ == "__main__":
    main()
