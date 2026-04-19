import json

def main():
    path = "data/sample.json"   
    with open(path, "r") as f:
            data = json.load(f)
    
    filename = data ["originalFilename"]
    timestamp = data["photoTakenTime"]["timestamp"]
    file_type = data["mimeType"]
    
    photo_record = {
        "filename": filename,
        "timestamp": timestamp,
        "type": file_type
    }
    
    print (photo_record)
    
if __name__ == "__main__":
    main()