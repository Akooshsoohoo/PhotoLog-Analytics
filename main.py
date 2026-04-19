import json

def main():
    path = "data/sample.json"   
     
    with open(path, "r") as f:
            data = json.load(f)
    
    print (data)
    
if __name__ == "__main__":
    main()