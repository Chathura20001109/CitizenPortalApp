from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "citizen_portal")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
ads_col = db["ads"]

ad = ads_col.find_one({"id": "ad_passport_eappointment"})
if ad:
    print(f"ID: {ad['id']}")
    print(f"Title: {ad['title']}")
    print(f"Link: {ad['link']}")
else:
    print("Ad not found!")
