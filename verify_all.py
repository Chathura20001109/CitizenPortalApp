
import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# 1. Check images
print("Checking images in static/store...")
store_dir = "static/store"
files = os.listdir(store_dir)
print(f"Found {len(files)} files.")
expected = ["slas_training.jpg", "kids_coding.jpg", "degree_it.jpg"]
for e in expected:
    if e in files:
        print(f"✓ {e} exists")
    else:
        print(f"✗ {e} MISSING")

# 2. Check Recommendations API
print("\nChecking Recommendations API...")
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client[os.getenv("DB_NAME", "citizen_portal")]
    user = db.users.find_one({"sample_data": True})
    
    if user:
        user_id = str(user["_id"])
        print(f"Testing with User ID: {user_id}")
        
        try:
            resp = requests.get(f"http://127.0.0.1:5000/api/recommendations/{user_id}", timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                print("✓ API Response 200 OK")
                print(f"  - Ads: {len(data.get('ads', []))}")
                print(f"  - Education Recs: {len(data.get('education_recommendations', []))}")
                print(f"  - Segments: {data.get('user_segment')}")
            else:
                print(f"✗ API Error {resp.status_code}: {resp.text}")
        except Exception as e:
            print(f"✗ Request failed: {e}")
    else:
        print("No sample user found to test.")
except Exception as e:
    print(f"DB Error: {e}")
