import json
import os

TAKEOUT_PATH = r"C:\Users\1saha\OneDrive\Desktop\The Mainframe\takeout-20260419T154518Z-3-001\Takeout\Google Photos"
YEARS = ["Photos from 2022", "Photos from 2023", "Photos from 2024", "Photos from 2025"]

def collect_json_files():
    json_files = []
    for year_folder in YEARS:
        folder_path = os.path.join(TAKEOUT_PATH, year_folder)
        for file_name in os.listdir(folder_path):
            if file_name.endswith(".json"):
                json_files.append(os.path.join(folder_path, file_name))
    return json_files

if __name__ == "__main__":
    files = collect_json_files()
    print(f"Found {len(files)} json sidecar files")
