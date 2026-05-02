import json
import os
import pandas as pd

def main():
    folder = "data"  # folder containing json files
    records = []  # store all photo records

    for file_name in os.listdir(folder):
        if file_name.endswith(".json"):
            path = os.path.join(folder, file_name)

            with open(path, "r") as f:
                data = json.load(f)  

            filename = data["title"]
            timestamp = data["photoTakenTime"]["timestamp"]
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "unknown"
            media_type = "video" if ext in ("mp4", "mov", "avi") else "photo"

            origin = data.get("googlePhotosOrigin", {})
            device_type = origin.get("mobileUpload", {}).get("deviceType", "UNKNOWN")

            photo_record = {
                "filename": filename,
                "timestamp": timestamp,
                "ext": ext,
                "media_type": media_type,
                "device_type": device_type,
            }

            records.append(photo_record)  # add to list

    df = pd.DataFrame(records)  
    print(df)  

if __name__ == "__main__":
    main()