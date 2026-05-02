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

def load_into_db(records):
    # remove old db so we start fresh each run
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open("schema.sql") as f:
        cursor.executescript(f.read())

    cursor.executemany("""
        INSERT INTO photos (title, photo_taken_ts, taken_year, taken_month, taken_day,
                            taken_weekday, taken_hour, device_type, media_type, file_ext, has_geo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, records)

    conn.commit()
    conn.close()

def main():
    json_files = collect_json_files()
    print(f"Found {len(json_files)} json sidecar files")

    records = []
    for path in json_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            records.append(parse_record(data))
        except Exception:
            pass  # skip malformed files

    load_into_db(records)
    print(f"Inserted {len(records)} rows into {DB_PATH}")

if __name__ == "__main__":
    main()
