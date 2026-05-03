CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    photo_taken_ts INTEGER NOT NULL,
    taken_year INTEGER,
    taken_month INTEGER,
    taken_day INTEGER,
    taken_weekday INTEGER,
    taken_hour INTEGER CHECK (taken_hour BETWEEN 0 AND 23),
    device_type TEXT,
    media_type TEXT,
    file_ext TEXT,
    has_geo INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_taken_year ON photos (taken_year);
CREATE INDEX IF NOT EXISTS idx_taken_month ON photos (taken_month);

CREATE TABLE IF NOT EXISTS daily_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    taken_year INTEGER NOT NULL,
    taken_month INTEGER NOT NULL,
    taken_day INTEGER NOT NULL,
    taken_weekday INTEGER NOT NULL,
    total_count INTEGER NOT NULL,
    photo_count INTEGER NOT NULL,
    video_count INTEGER NOT NULL,
    burst_day INTEGER DEFAULT 0
);
