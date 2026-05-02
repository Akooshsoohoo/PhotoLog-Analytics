CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    photo_taken_ts INTEGER,
    taken_year INTEGER,
    taken_month INTEGER,
    taken_day INTEGER,
    taken_weekday INTEGER,
    taken_hour INTEGER,
    device_type TEXT,
    media_type TEXT,
    file_ext TEXT,
    has_geo INTEGER
);
