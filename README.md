# PhotoLog Analytics

CS 210 Final Project — analyzing personal photo-taking behavior using Google Photos metadata.

## Setup

```
pip install -r requirements.txt
```

Place your Google Takeout export in the path set in `parse_data.py` (`TAKEOUT_PATH`).

## Running

Run the full pipeline:

```
python main.py
```

Or run each step individually:

```
python parse_data.py       # parse JSON sidecar files → photos.db
python clean_data.py       # clean data + extract time features
python queries.py          # SQL analysis queries
python visualizations.py   # generate plots in plots/
python ml_models.py        # linear + logistic regression
```

## Output

- `photos.db` — SQLite database with ~3000 records
- `plots/` — 4 PNG charts (monthly trend, hourly, weekday, media type)
- Terminal output from queries and ML model evaluation
