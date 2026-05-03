
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def check_categories():
    try:
        res = requests.get(f"{BASE_URL}/api/store/categories")
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("Categories:", json.dumps(data, indent=2))
        else:
            print("Error:", res.text)
            
        print("-" * 20)
        
        res2 = requests.get(f"{BASE_URL}/api/categories")
        print(f"Status: {res2.status_code}")
        if res2.status_code == 200:
            data = res2.json()
            print("Legacy Categories:", json.dumps(data, indent=2))
        else:
            print("Error:", res.text)

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_categories()
