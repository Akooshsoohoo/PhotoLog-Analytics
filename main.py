import json
import os

def main():
    folder = "data"  # folder containing json files
    records = []  # store all photo records

    for file_name in os.listdir(folder):
        if file_name.endswith(".json"):
            path = os.path.join(folder, file_name)

            with open(path, "r") as f:
                data = json.load(f)

            # extract fields
            filename = data["originalFilename"]
            timestamp = data["photoTakenTime"]["timestamp"]
            file_type = data["mimeType"]

            # create structured record
            photo_record = {
                "filename": filename,
                "timestamp": timestamp,
                "type": file_type
            }

            records.append(photo_record)  # add to list

    print(records)  

if __name__ == "__main__":
    main()