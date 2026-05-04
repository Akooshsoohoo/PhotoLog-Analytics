import json
import os
import sqlite3

TAKEOUT_PATH = r"C:\Users\1saha\OneDrive\Desktop\The Mainframe\takeout-20260419T154518Z-3-001\Takeout\Google Photos"
YEARS = ["Photos from 2022", "Photos from 2023", "Photos from 2024", "Photos from 2025"]
DB_PATH = "photos.db"

def collect_json_files():
    json_files = []
    for year_folder in YEARS:
        folder_path = os.path.join(TAKEOUT_PATH, year_folder)
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".json"):
                json_files.append(os.path.join(folder_path, file_name))
    return json_files

def parse_record(data):
    title = data.get("title", "")
    photo_taken_ts = int(data.get("photoTakenTime", {}).get("timestamp", 0))
    ext = title.rsplit(".", 1)[-1].lower() if "." in title else "unknown"
    media_type = "video" if ext in ("mp4", "mov", "avi") else "photo"

    origin = data.get("googlePhotosOrigin", {})
    device_type = origin.get("mobileUpload", {}).get("deviceType", "UNKNOWN")

    geo = data.get("geoData", {})
    has_geo = 1 if geo.get("latitude", 0.0) != 0.0 else 0

    return (title, photo_taken_ts, None, None, None, None, None, device_type, media_type, ext, has_geo)

def load_into_db(records, db_path=DB_PATH):
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path) as f:
        cursor.executescript(f.read())

    cursor.executemany("""
        INSERT INTO photos (title, photo_taken_ts, taken_year, taken_month, taken_day,
                            taken_weekday, taken_hour, device_type, media_type, file_ext, has_geo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)

    conn.commit()
    conn.close()

def parse_from_paths(json_paths, db_path=DB_PATH):
    records = []
    for path in json_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            records.append(parse_record(data))
        except Exception:
            pass
    load_into_db(records, db_path)
    return len(records)

def main():
    json_files = collect_json_files()
    print(f"Found {len(json_files)} json sidecar files")
    n = parse_from_paths(json_files, DB_PATH)
    print(f"Inserted {n} rows into {DB_PATH}")

if __name__ == "__main__":
    main()
