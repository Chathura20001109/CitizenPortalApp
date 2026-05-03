from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('DB_NAME')]

products = list(db.products.find({}, {'name': 1, 'category': 1, 'images': 1}))
for p in products:
    name = p['name']['en'] if isinstance(p['name'], dict) else p['name']
    img = p.get('images', [])[0] if p.get('images') else 'No Image'
    print(f"{name}: {img}")
