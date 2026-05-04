# PhotoLog Analytics

CS 210 Final Project — analyzing personal photo-taking behavior using Google Photos metadata.

**Live demo:** [your-render-url-here]

---

## What it does

Parses JSON sidecar files from a Google Photos Takeout export, stores the metadata in SQLite, runs SQL queries and ML models, and displays everything in an interactive web dashboard.

---

## Viewing the dashboard

The easiest way is the live link above — no setup needed.

To run it locally:

```
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000`. It will load the pre-built dataset automatically.

To analyze your own Google Photos data, go to [Google Takeout](https://takeout.google.com), export your Google Photos, extract the ZIP, and select the folder on the upload screen.

---

## Running the full pipeline (optional)

If you want to re-run the data pipeline from scratch:

1. Set `TAKEOUT_PATH` in `parse_data.py` to your local Takeout folder
2. Run:

```
python main.py
```

This runs all six steps in order: parse → clean → queries → visualizations → ML models → export.

Or run each step individually:

```
python parse_data.py      # parse JSON sidecars into photos.db
python clean_data.py      # clean data and extract time features
python queries.py         # SQL analysis queries
python visualizations.py  # save charts to plots/
python ml_models.py       # linear regression, logistic regression, k-means
python export_json.py     # export results to web/data/photos.json
```

---

## Project structure

```
app.py              Flask web server
parse_data.py       Parses Google Takeout JSON files into SQLite
clean_data.py       Data cleaning and feature engineering
queries.py          SQL analysis queries
visualizations.py   Matplotlib charts
ml_models.py        Linear regression, logistic regression, K-Means
export_json.py      Exports DB results to JSON for the dashboard
main.py             Runs the full pipeline end to end
schema.sql          SQLite schema
requirements.txt    Dependencies
web/                Frontend (Chart.js dashboard)
web/data/photos.json  Pre-built dataset
```
