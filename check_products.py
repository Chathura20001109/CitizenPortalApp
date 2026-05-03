
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME", "citizen_portal")]
products = list(db.products.find({}, {"id": 1, "name": 1, "_id": 0}))
print(f"Total products: {len(products)}")
for p in products:
    print(f"- {p['id']}: {p['name']}")
