import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGO_URI'))
db = client[os.getenv('DB_NAME', 'citizen_portal')]

new_ads = [
    {
        "id": "ad_al_university",
        "title": "University Admissions for A/L Students",
        "content": "Applications for the upcoming university intake are now open for all A/L students. Apply online.",
        "target_segments": ["al", "student", "a/l", "education", "school"],
        "active": True
    },
    {
        "id": "ad_al_zscore",
        "title": "A/L Z-Score Released",
        "content": "The A/L Z-scores for 2023 have been released. Check your eligibility for university courses.",
        "target_segments": ["al", "student", "a/l", "university", "school"],
        "active": True
    },
    {
        "id": "ad_business_tax",
        "title": "SME Tax Exemptions",
        "content": "Small and Medium Enterprises can now apply for the new digital tax exemption scheme.",
        "target_segments": ["business", "sme", "entrepreneur", "career", "professional"],
        "active": True
    },
    {
        "id": "ad_senior_pension",
        "title": "Digital Pension Registration",
        "content": "Retirees can now register their pension details fully online via the Citizen Portal.",
        "target_segments": ["senior", "retiree", "pension", "elderly"],
        "active": True
    },
    {
        "id": "ad_housing_loans",
        "title": "Government Housing Loans",
        "content": "Low-interest housing loans available for first-time home buyers. Check your eligibility today.",
        "target_segments": ["housing", "family", "married", "professional"],
        "active": True
    }
]

for ad in new_ads:
    db.ads.update_one({"id": ad["id"]}, {"$set": ad}, upsert=True)

print("New targeted announcements added successfully.")
