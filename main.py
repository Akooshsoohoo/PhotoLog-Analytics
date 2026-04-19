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

            filename = data["originalFilename"]
            timestamp = data["photoTakenTime"]["timestamp"]
            file_type = data["mimeType"]

            photo_record = {
                "filename": filename,
                "timestamp": timestamp,
                "type": file_type
            }

            records.append(photo_record)  # add to list

    df = pd.DataFrame(records)  
    print(df)  

if __name__ == "__main__":
    main()