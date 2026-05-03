#!/usr/bin/env python3
"""
Seed script for Citizen Portal database.

Improvements in this update:
- Fail fast if MONGO_URI missing
- Idempotent-ish behavior: clears only sample users, and attempts to insert documents with uniqueness indexes
- Adds useful indexes for performance
- Better logging and error handling
- Wraps execution in a main guard so it can be imported safely
"""

from pymongo import MongoClient, errors
from datetime import datetime, timedelta
import os
import random
from dotenv import load_dotenv
import bcrypt
import sys

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "citizen_portal")

if not MONGO_URI:
    print("ERROR: MONGO_URI not set in environment. Exiting.", file=sys.stderr)
    sys.exit(1)

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
services_col = db["services"]
categories_col = db["categories"]
officers_col = db["officers"]
ads_col = db["ads"]
products_col = db["products"]
users_col = db["users"]
admins_col = db["admins"]
orders_col = db["orders"]
payments_col = db["payments"]

def create_indexes():
    """
    Create useful indexes to improve query performance and enforce uniqueness where appropriate.
    Safe to call multiple times.
    """
    try:
        categories_col.create_index("id", unique=True)
        services_col.create_index("id", unique=True)
        ads_col.create_index("id", unique=True)
        products_col.create_index("id", unique=True)
        officers_col.create_index("id", unique=True)
        admins_col.create_index("username", unique=True)
        users_col.create_index("sample_data")
        users_col.create_index("created")
        products_col.create_index("tags")
        products_col.create_index("target_segments")
        products_col.create_index("category")
        eng_index = db["engagements"]
        eng_index.create_index("user_id")
        orders_col.create_index("order_id", unique=True)
        payments_col.create_index("payment_id", unique=True)
        print("✓ Indexes created/ensured")
    except Exception as e:
        print(f"Warning: creating indexes failed: {e}")

def clear_collections():
    """
    Clear non-critical collections before seeding.
    Keep production-safe: only delete sample users (sample_data=True).
    """
    print("\n[1/7] Clearing existing data (limited):")
    try:
        services_col.delete_many({})
        categories_col.delete_many({})
        officers_col.delete_many({})
        ads_col.delete_many({})
        products_col.delete_many({})
        # Keep users but remove only sample data to avoid accidental deletion
        users_col.delete_many({"sample_data": True})
        print("✓ Collections cleared (services, categories, officers, ads, products, sample users)")
    except Exception as e:
        print(f"Error clearing collections: {e}", file=sys.stderr)

def seed_categories():
    print("\n[2/7] Seeding categories...")
    categories = [
        {
            "id": "cat_it",
            "name": {"en": "IT & Digital Services", "si": "තොරතුරු සහ ඩිජිටල්", "ta": "தகவல் மற்றும் டிஜிட்டல்"},
            "ministry_ids": ["ministry_it"],
            "icon": "computer",
            "created": datetime.utcnow()
        },
        {
            "id": "cat_public",
            "name": {"en": "Public Administration", "si": "පොදු පරිපාලන", "ta": "பொது நிர்வாகம்"},
            "ministry_ids": ["ministry_public"],
            "icon": "government",
            "created": datetime.utcnow()
        },
        {
            "id": "cat_land",
            "name": {"en": "Land & Housing", "si": "ඉඩම් සහ නිවාස", "ta": "நிலம் மற்றும் வீடுகள்"},
            "ministry_ids": ["ministry_land", "ministry_housing"],
            "icon": "home",
            "created": datetime.utcnow()
        },
        {
            "id": "cat_education",
            "name": {"en": "Education", "si": "අධ්‍යාපනය", "ta": "கல்வி"},
            "ministry_ids": ["ministry_education"],
            "icon": "school",
            "created": datetime.utcnow()
        },
        {
            "id": "cat_health",
            "name": {"en": "Health Services", "si": "සෞඛ්‍ය සේවා", "ta": "சுகாதார சேவைகள்"},
            "ministry_ids": ["ministry_health"],
            "icon": "hospital",
            "created": datetime.utcnow()
        },
        {
            "id": "cat_transport",
            "name": {"en": "Transport & Vehicles", "si": "ප්‍රවාහන සහ වාහන", "ta": "போக்குவரத்து மற்றும் வாகனங்கள்"},
            "ministry_ids": ["ministry_transport"],
            "icon": "car",
            "created": datetime.utcnow()
        },
        {
            "id": "cat_immigration",
            "name": {"en": "Immigration & Emigration", "si": "ආගමන හා විගමන", "ta": "குடிவரவு மற்றும் குடியகல்வு"},
            "ministry_ids": ["dept_immigration"],
            "icon": "passport",
            "created": datetime.utcnow()
        },
        {
            "id": "cat_finance",
            "name": {"en": "Finance & Tax", "si": "මුදල් සහ බදු", "ta": "நிதி மற்றும் வரி"},
            "ministry_ids": ["ministry_finance"],
            "icon": "money",
            "created": datetime.utcnow()
        },
        {
            "id": "cat_agriculture",
            "name": {"en": "Agriculture", "si": "කෘෂිකර්මය", "ta": "விவசாயம்"},
            "ministry_ids": ["ministry_agriculture"],
            "icon": "leaf",
            "created": datetime.utcnow()
        },
    ]
    try:
        categories_col.insert_many(categories, ordered=False)
        print(f"✓ Seeded {len(categories)} categories")
    except errors.BulkWriteError as bwe:
        print("Note: some categories may already exist or had duplicate keys. BulkWriteError:", bwe.details)
    except Exception as e:
        print(f"Failed to seed categories: {e}", file=sys.stderr)

def seed_services():
    print("\n[3/7] Seeding services...")
    services = [
        {
            "id": "ministry_it",
            "category": "cat_it",
            "name": {"en": "Ministry of IT & Digital Affairs", "si": "තොරතුරු සහ ඩිජිටල් කටයුතු අමාත්‍යාංශය", "ta": "தகவல் மற்றும் டிஜிட்டல் விவகார அமைச்சு"},
            "subservices": [
                {
                    "id": "it_cert",
                    "name": {"en": "IT Certificates", "si": "තොරතුරු තාක්ෂණ සහතික", "ta": "ஐடி சான்றிதழ்கள்"},
                    "questions": [
                        {
                            "q": {"en": "How to apply for an IT certificate?", "si": "තොරතුරු තාක්ෂණ සහතිකයක් සඳහා අයදුම් කරන්නේ කෙසේද?"},
                            "answer": {"en": "Fill the online form and upload your NIC copy. Processing takes 5-7 business days.", "si": "මාර්ගගත පෝරමය පුරවා ඔබගේ ජාතික හැඳුනුම්පතේ පිටපතක් උඩුගත කරන්න."},
                            "downloads": ["/static/forms/it_cert_form.pdf"],
                            "location": "https://maps.google.com/?q=Ministry+of+IT+Colombo",
                            "instructions": "Visit the digital portal at digital.gov.lk, register with your email, and submit the application with required documents."
                        },
                        {
                            "q": {"en": "What documents are required?"},
                            "answer": {"en": "You need: NIC copy, passport-size photo, educational certificates, and proof of address."},
                            "downloads": ["/static/forms/document_checklist.pdf"]
                        }
                    ]
                },
                {
                    "id": "digital_services",
                    "name": {"en": "Digital Services Registration", "si": "ඩිජිටල් සේවා ලියාපදිංචිය"},
                    "questions": [
                        {
                            "q": {"en": "How to register for government digital services?"},
                            "answer": {"en": "Create an account on portal.gov.lk using your email and NIC. Verify your email to activate."},
                            "downloads": [],
                            "location": "https://portal.gov.lk"
                        }
                    ]
                }
            ],
            "created": datetime.utcnow()
        },
        {
            "id": "ministry_education",
            "category": "cat_education",
            "name": {"en": "Ministry of Education", "si": "අධ්‍යාපන අමාත්‍යාංශය", "ta": "கல்வி அமைச்சு"},
            "subservices": [
                {
                    "id": "school_reg",
                    "name": {"en": "School Registration", "si": "පාසල් ලියාපදිංචිය"},
                    "questions": [
                        {
                            "q": {"en": "How to register a child in government school?"},
                            "answer": {"en": "Visit the nearest school with birth certificate, NIC copies of parents, and proof of address. Registration is free."},
                            "downloads": ["/static/forms/school_admission_form.pdf"],
                            "location": "https://maps.google.com/?q=schools+near+me"
                        }
                    ]
                },
                {
                    "id": "exam_results",
                    "name": {"en": "Exam Results", "si": "විභාග ප්‍රතිඵල"},
                    "questions": [
                        {
                            "q": {"en": "How to check O/L and A/L results?"},
                            "answer": {"en": "Visit exam.gov.lk and enter your index number. Results are published within 3 months of exams."},
                            "location": "https://exam.gov.lk"
                        }
                    ]
                }
            ],
            "created": datetime.utcnow()
        },
        {
            "id": "ministry_land",
            "category": "cat_land",
            "name": {"en": "Land Registry Department", "si": "ඉඩම් ලේඛන දෙපාර්තමේන්තුව"},
            "subservices": [
                {
                    "id": "land_title",
                    "name": {"en": "Land Title Search", "si": "ඉඩම් හිමිකම් සෙවීම"},
                    "questions": [
                        {
                            "q": {"en": "How to obtain land title certificate?"},
                            "answer": {"en": "Submit application at district land registry with deed number, NIC, and payment of Rs. 1000. Processing takes 2 weeks."},
                            "downloads": ["/static/forms/land_title_application.pdf"]
                        }
                    ]
                }
            ],
            "created": datetime.utcnow()
        },
        {
            "id": "ministry_public",
            "category": "cat_public",
            "name": {"en": "Ministry of Public Administration", "si": "රාජ්‍ය පරිපාලන අමාත්‍යාංශය", "ta": "பொது நிர்வாக அமைச்சு"},
            "subservices": [
                {
                    "id": "grama_niladhari",
                    "name": {"en": "Grama Niladhari Services", "si": "ග්‍රාම නිලධාරී සේවා"},
                    "questions": [
                        {
                            "q": {"en": "How to find my Grama Niladhari?"},
                            "answer": {"en": "Visit the divisional secretariat website or use the government directory."},
                            "location": "https://maps.google.com/?q=divisional+secretariat"
                        },
                        {
                            "q": {"en": "How to obtain a character certificate?"},
                            "answer": {"en": "Submit a request to your Grama Niladhari with a police report and NIC copy."}
                        }
                    ]
                }
            ],
            "created": datetime.utcnow()
        },
        {
            "id": "ministry_health",
            "category": "cat_health",
            "name": {"en": "Ministry of Health", "si": "සෞඛ්‍ය අමාත්‍යාංශය", "ta": "சுகாதார அமைச்சு"},
            "subservices": [
                {
                    "id": "hospital_clinics",
                    "name": {"en": "Hospital Clinics", "si": "රෝහල් සායන"},
                    "questions": [
                        {
                            "q": {"en": "How to register for a clinic?"},
                            "answer": {"en": "Visit the OPD with your referral letter."}
                        }
                    ]
                }
            ],
            "created": datetime.utcnow()
        },
        {
            "id": "ministry_housing",
            "category": "cat_land",
            "name": {"en": "Ministry of Housing", "si": "නිවාස අමාත්‍යාංශය", "ta": "வீடமைப்பு அமைச்சு"},
            "subservices": [
                {
                    "id": "housing_loan",
                    "name": {"en": "Housing Loans", "si": "නිවාස ණය"},
                    "questions": [
                        {
                            "q": {"en": "How to apply for government housing loan?"},
                            "answer": {"en": "Applications are available at the district office."}
                        }
                    ]
                }
            ],
            "created": datetime.utcnow()
        },
        {
            "id": "ministry_transport",
            "category": "cat_transport",
            "name": {"en": "Ministry of Transport", "si": "ප්‍රවාහන අමාත්‍යාංශය", "ta": "போக்குவரத்து அமைச்சு"},
            "subservices": [
                {
                    "id": "driving_license",
                    "name": {"en": "Driving License Services", "si": "රියදුරු බලපත්‍ර සේවා"},
                    "questions": [
                        {
                            "q": {"en": "How to apply for a new driving license?"},
                            "answer": {"en": "Visit the Department of Motor Traffic (DMT) with your NIC, birth certificate, and medical certificate. You must pass the written and practical exams."},
                            "location": "https://maps.google.com/?q=DMT+Werahera"
                        },
                        {
                            "q": {"en": "How to renew my driving license?"},
                            "answer": {"en": "Renewals can be done at DMT offices or selected Divisional Secretariats. Bring your old license and a medical certificate."}
                        }
                    ]
                },
                {
                    "id": "vehicle_reg",
                    "name": {"en": "Vehicle Registration", "si": "වාහන ලියාපදිංචිය"},
                    "questions": [
                        {
                            "q": {"en": "How to transfer vehicle ownership?"},
                            "answer": {"en": "Submit MTA 6 and MTA 8 forms along with the vehicle book (CR) and revenue license to the DMT."}
                        }
                    ]
                }
            ],
            "created": datetime.utcnow()
        },
        {
            "id": "dept_immigration",
            "category": "cat_immigration",
            "name": {"en": "Department of Immigration & Emigration", "si": "ආගමන හා විගමන දෙපාර්තමේන්තුව", "ta": "குடிவரவு மற்றும் குடியகல்வு திணைக்களம்"},
            "subservices": [
                {
                    "id": "passport_service",
                    "name": {"en": "Passport Services", "si": "විදේශ ගමන් බලපත්‍ර සේවා"},
                    "questions": [
                        {
                            "q": {"en": "How to apply for a passport?"},
                            "answer": {"en": "Book an appointment online via the department website. Visit the Battaramulla office with NIC, birth certificate, and photos."},
                            "location": "https://maps.google.com/?q=Immigration+Battaramulla",
                            "instructions": "Online appointment is mandatory."
                        },
                        {
                            "q": {"en": "What are the fees for a passport?"},
                            "answer": {"en": "Normal service: LKR 5,000 (30 days). One-day service: LKR 20,000."}
                        }
                    ]
                }
            ],
            "created": datetime.utcnow()
        },
        {
            "id": "ministry_finance",
            "category": "cat_finance",
            "name": {"en": "Ministry of Finance", "si": "මුදල් අමාත්‍යාංශය", "ta": "நிதி அமைச்சு"},
            "subservices": [
                {
                    "id": "tin_reg",
                    "name": {"en": "TIN Registration", "si": "බදු ගෙවන්නා හඳුනාගැනීමේ අංකය"},
                    "questions": [
                        {
                            "q": {"en": "How to get a TIN number?"},
                            "answer": {"en": "Register online at the Inland Revenue Department (IRD) website or visit the IRD head office."},
                            "location": "https://ird.gov.lk"
                        }
                    ]
                }
            ],
            "created": datetime.utcnow()
        },
        {
            "id": "ministry_agriculture",
            "category": "cat_agriculture",
            "name": {"en": "Ministry of Agriculture", "si": "කෘෂිකර්ම අමාත්‍යාංශය", "ta": "விவசாய அமைச்சு"},
            "subservices": [
                {
                    "id": "agri_subsidy",
                    "name": {"en": "Fertilizer Subsidy", "si": "පොහොර සහනාධාරය", "ta": "உர மானியம்"},
                    "questions": [
                        {
                            "q": {"en": "How to apply for fertilizer subsidy?", "si": "පොහොර සහනාධාරය සඳහා අයදුම් කරන්නේ කෙසේද?", "ta": "உர மானியத்திற்கு எவ்வாறு விண்ணப்பிப்பது?"},
                            "answer": {"en": "Registered farmers can apply via the Agrarian Services Center in their area. Bring your farmer ID card.", "si": "ලියාපදිංචි ගොවීන්ට තම ප්‍රදේශයේ ගොවිජන සේවා මධ්‍යස්ථානය හරහා අයදුම් කළ හැකිය. ඔබේ ගොවි හැඳුනුම්පත රැගෙන එන්න.", "ta": "பதிவு செய்யப்பட்ட விவசாயிகள் தங்கள் பகுதியில் உள்ள விவசாய சேவை மையத்தின் மூலம் விண்ணப்பிக்கலாம். உங்கள் விவசாயி அடையாள அட்டையை கொண்டு வாருங்கள்."},
                            "downloads": ["/static/forms/fertilizer_subsidy.pdf"],
                            "location": "https://maps.google.com/?q=Agrarian+Services+Center"
                        }
                    ]
                }
            ],
            "created": datetime.utcnow()
        }
    ]
    try:
        services_col.insert_many(services, ordered=False)
        print(f"✓ Seeded {len(services)} services with subservices")
    except errors.BulkWriteError as bwe:
        print("Note: some services may already exist or had duplicate keys. BulkWriteError:", bwe.details)
    except Exception as e:
        print(f"Failed to seed services: {e}", file=sys.stderr)

def seed_officers():
    print("\n[4/7] Seeding officers...")
    officers = [
        {
            "id": "off_it_01",
            "name": "Ms. Nayana Perera",
            "role": "Director - Digital Services",
            "ministry_id": "ministry_it",
            "contact": {"email": "nayana@it.gov.lk", "phone": "+94 71 234 5678"},
            "office_hours": "Mon-Fri, 9:00 AM - 4:00 PM",
            "created": datetime.utcnow()
        },
        {
            "id": "off_edu_01",
            "name": "Mr. Ruwan Silva",
            "role": "Assistant Secretary - Education",
            "ministry_id": "ministry_education",
            "contact": {"email": "ruwan@edu.gov.lk", "phone": "+94 71 987 6543"},
            "created": datetime.utcnow()
        }
    ]
    try:
        officers_col.insert_many(officers, ordered=False)
        print(f"✓ Seeded {len(officers)} officers")
    except errors.BulkWriteError as bwe:
        print("Note: some officers may already exist. BulkWriteError:", bwe.details)
    except Exception as e:
        print(f"Failed to seed officers: {e}", file=sys.stderr)

def seed_ads():
    print("\n[5/7] Seeding ads and announcements...")
    ads = [
        {
            "id": "ad_degree_01",
            "title": "Complete Your Degree - Government Employee Discount",
            "body": "SpaceXP Campus offers weekend degree programs. Special 20% discount for government employees. Limited seats available.",
            "link": "/store?product=prod_degree_01",
            "active": True,
            "priority": "high",
            "tags": ["degree", "education", "government", "career"],
            "target_segments": ["government_employee", "needs_qualification", "mid_career_family"],
            "image": "/static/img/degree_ad.jpg",
            "created": datetime.utcnow(),
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=90)
        },
        {
            "id": "ad_ielts_01",
            "title": "IELTS Preparation - Batch Starting Soon",
            "body": "Comprehensive IELTS course with mock tests and speaking practice. 90% success rate.",
            "link": "/store?product=prod_ielts_01",
            "active": True,
            "priority": "high",
            "tags": ["ielts", "english", "overseas", "language"],
            "target_segments": ["young_adult", "early_career", "overseas_interested"],
            "created": datetime.utcnow()
        },
        {
            "id": "ad_japan_visa",
            "title": "Japan Work Visa Assistance",
            "body": "IT and healthcare opportunities in Japan. Complete visa processing and job matching support.",
            "link": "/store?product=prod_japan_visa_01",
            "active": True,
            "priority": "medium",
            "tags": ["japan", "visa", "overseas", "it"],
            "target_segments": ["tech_professional", "early_career"],
            "created": datetime.utcnow()
        },
        {
            "id": "ad_laptop_deal",
            "title": "Government Employee Laptop Deal",
            "body": "Premium laptops at subsidized rates for government employees. Easy installment plans available.",
            "link": "/store?product=prod_laptop_01",
            "active": True,
            "priority": "medium",
            "tags": ["laptop", "electronics", "government"],
            "target_segments": ["government_employee"],
            "created": datetime.utcnow()
        },
        {
            "id": "ad_ol_tuition",
            "title": "O/L Tuition Classes - 2025 Batch",
            "body": "Expert teachers for all subjects. Small batch sizes. Weekend and evening classes available.",
            "link": "/store?category=education&filter=tuition",
            "active": True,
            "priority": "high",
            "tags": ["ol", "tuition", "education", "children"],
            "target_segments": ["parent", "secondary_school_parent"],
            "created": datetime.utcnow()
        }
    ]
    try:
        ads_col.insert_many(ads, ordered=False)
        print(f"✓ Seeded {len(ads)} ads")
    except errors.BulkWriteError as bwe:
        print("Note: some ads may already exist. BulkWriteError:", bwe.details)
    except Exception as e:
        print(f"Failed to seed ads: {e}", file=sys.stderr)

def seed_products():
    print("\n[6/7] Seeding products...")
    products = [
        {
            "id": "prod_degree_01",
            "name": "Bachelor of IT (SpaceXP Campus)",
            "category": "education",
            "subcategory": "degree_programs",
            "price": 185000,
            "original_price": 225000,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=800&q=80"],
            "description": "Complete your IT degree with flexible payment options. Weekend classes available. Industry-recognized curriculum with government employee discount.",
            "features": [
                "3-year program with semester system",
                "Weekend classes (Saturday & Sunday)",
                "Online learning support",
                "Government employee 20% discount",
                "Industry certification included",
                "Job placement assistance"
            ],
            "tags": ["degree", "it", "government", "career_advancement", "weekend"],
            "target_segments": ["government_employee", "needs_qualification", "mid_career_family", "tech_professional"],
            "in_stock": True,
            "delivery_options": ["online", "campus"],
            "rating": 4.5,
            "reviews_count": 47,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_ielts_01",
            "name": "IELTS Preparation Course",
            "category": "education",
            "subcategory": "language_courses",
            "price": 25000,
            "original_price": 35000,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=800&q=80"],
            "description": "Comprehensive IELTS preparation with experienced trainers. Includes mock tests, speaking practice, and study materials.",
            "features": [
                "4-week intensive program",
                "Expert British Council certified trainers",
                "5 full mock tests",
                "Daily speaking practice sessions",
                "Study materials included",
                "Small batch size (max 15 students)"
            ],
            "tags": ["ielts", "english", "overseas", "language", "government"],
            "target_segments": ["young_adult", "early_career", "overseas_interested", "government_employee"],
            "in_stock": True,
            "delivery_options": ["online", "classroom"],
            "rating": 4.7,
            "reviews_count": 89,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_japan_visa_01",
            "name": "Japan Work Visa Assistance Package",
            "category": "visa_services",
            "subcategory": "job_visas",
            "price": 45000,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=800&q=80"],
            "description": "Complete assistance for Japan work visa applications. IT, healthcare, and hospitality opportunities available.",
            "features": [
                "Complete visa processing",
                "Job matching with Japanese employers",
                "Document preparation and translation",
                "Interview preparation",
                "Pre-departure orientation",
                "Post-arrival support"
            ],
            "tags": ["japan", "work_visa", "overseas_jobs", "it_jobs", "healthcare"],
            "target_segments": ["early_career", "mid_career_family", "tech_professional", "young_adult"],
            "in_stock": True,
            "delivery_options": ["consultation"],
            "rating": 4.3,
            "reviews_count": 34,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_laptop_01",
            "name": "Dell Inspiron 15 - Government Employee Package",
            "category": "electronics",
            "subcategory": "computers",
            "price": 85000,
            "original_price": 115000,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80"],
            "description": "Premium laptop package for government employees with extended warranty and free software.",
            "features": [
                "Intel Core i5 11th Gen processor",
                "8GB RAM (upgradeable to 16GB)",
                "256GB SSD",
                "15.6\" FHD display",
                "2-year warranty",
                "Free MS Office license",
                "Free antivirus (1 year)"
            ],
            "tags": ["laptop", "electronics", "government_deal", "technology", "dell"],
            "target_segments": ["government_employee", "early_career", "mid_career_family", "tech_professional"],
            "in_stock": True,
            "delivery_options": ["delivery", "pickup"],
            "rating": 4.4,
            "reviews_count": 156,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_saree_01",
            "name": "Handloom Batik Saree Collection",
            "category": "fashion",
            "subcategory": "traditional_wear",
            "price": 4500,
            "original_price": 6500,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&q=80"],
            "description": "Authentic handloom batik sarees with traditional Sri Lankan designs. Limited edition collection.",
            "features": [
                "Pure cotton fabric",
                "Handmade batik designs",
                "Traditional patterns",
                "Multiple color options",
                "6-yard length",
                "Matching blouse piece included"
            ],
            "tags": ["saree", "batik", "handloom", "traditional", "fashion", "sri_lankan"],
            "target_segments": ["mid_career_family", "established_professional", "senior", "parent"],
            "in_stock": True,
            "delivery_options": ["delivery", "pickup"],
            "rating": 4.6,
            "reviews_count": 203,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_ol_tuition",
            "name": "O/L Complete Tuition Package (All Subjects)",
            "category": "education",
            "subcategory": "tuition",
            "price": 18000,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80"],
            "description": "Comprehensive O/L tuition for all subjects by experienced teachers. Weekend and weekday batches available.",
            "features": [
                "All 9 subjects covered",
                "Experienced teachers",
                "Small batch size (20 students)",
                "Weekend and evening classes",
                "Regular assessments",
                "Free study materials",
                "3-month package"
            ],
            "tags": ["ol", "tuition", "education", "children", "exam_preparation"],
            "target_segments": ["parent", "secondary_school_parent", "mid_career_family"],
            "in_stock": True,
            "delivery_options": ["classroom", "online"],
            "rating": 4.8,
            "reviews_count": 312,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_slas_01",
            "name": "SLAS Exam Intensive Training",
            "category": "education",
            "subcategory": "professional_exams",
            "price": 35000,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&q=80"],
            "description": "Targeted preparation for Sri Lanka Administrative Service (SLAS) open competitive examination.",
            "features": [
                "Comprehensive syllabus coverage",
                "Past paper discussions",
                "IQ and General Knowledge focus",
                "Weekend classes for working professionals",
                "Mock interviews"
            ],
            "tags": ["slas", "government_exam", "career", "professional"],
            "target_segments": ["government_employee", "young_adult", "graduate"],
            "in_stock": True,
            "delivery_options": ["classroom", "online"],
            "rating": 4.9,
            "reviews_count": 120,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_part_time_job_01",
            "name": "Data Entry Specialist (Part-Time)",
            "category": "jobs",
            "subcategory": "part_time",
            "price": 0,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1488190211105-8b0e65b80b4e?w=800&q=80"],
            "description": "Flexible part-time opportunity for data entry operators. Work from home options available.",
            "features": [
                "Flexible hours",
                "Weekly payout",
                "Training provided",
                "No prior experience required"
            ],
            "tags": ["job", "part_time", "data_entry", "work_from_home"],
            "target_segments": ["student", "young_adult", "parent"],
            "in_stock": True,
            "delivery_options": ["online"],
            "rating": 4.2,
            "reviews_count": 45,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_kids_coding",
            "name": "Kids Coding Camp (Ages 8-14)",
            "category": "education",
            "subcategory": "children",
            "price": 12000,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&q=80"],
            "description": "Fun and interactive coding classes for children. Learn Scratch, Python, and Web Basics.",
            "features": [
                "Game-based learning",
                "Weekend batches",
                "Certificate of completion",
                "Project showcase"
            ],
            "tags": ["coding", "kids", "education", "stem"],
            "target_segments": ["parent", "secondary_school_parent"],
            "in_stock": True,
            "delivery_options": ["classroom", "online"],
            "rating": 4.8,
            "reviews_count": 78,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_prof_dev_01",
            "name": "Professional Leadership Workshop",
            "category": "education",
            "subcategory": "professional_development",
            "price": 15000,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=800&q=80"],
            "description": "2-day intensive workshop on leadership and management skills for mid-career professionals.",
            "features": [
                "Industry expert trainers",
                "Networking opportunities",
                "Certificate",
                "Lunch and refreshments included"
            ],
            "tags": ["leadership", "management", "professional", "workshop"],
            "target_segments": ["mid_career_family", "professional", "manager"],
            "in_stock": True,
            "delivery_options": ["classroom"],
            "rating": 4.6,
            "reviews_count": 52,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_solar_panel",
            "name": "Home Solar Power Kit (3kW)",
            "category": "electronics",
            "subcategory": "home_appliances",
            "price": 450000,
            "original_price": 500000,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&q=80"],
            "description": "Complete 3kW solar power system for homes. Includes panels, inverter, and basic installation.",
            "features": [
                "10 Monocrystalline Panels",
                "3kW Hybrid Inverter",
                "10-year warranty",
                "Free basic installation"
            ],
            "tags": ["solar", "energy", "home", "electronics"],
            "target_segments": ["homeowner", "mid_career_family", "senior"],
            "in_stock": True,
            "delivery_options": ["delivery"],
            "rating": 4.7,
            "reviews_count": 89,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_tax_consultation",
            "name": "Expert Tax Consultation & Filing",
            "category": "professional_services",
            "subcategory": "finance",
            "price": 5000,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=800&q=80"],
            "description": "Professional assistance with annual tax filing for individuals and SMEs.",
            "features": [
                "1-hour consultation",
                "TIN registration support",
                "Document verification",
                "Filing submission"
            ],
            "tags": ["tax", "finance", "business", "consultation"],
            "target_segments": ["business_owner", "professional", "freelancer"],
            "in_stock": True,
            "delivery_options": ["online", "consultation"],
            "rating": 4.9,
            "reviews_count": 210,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_organic_fert",
            "name": "Government Certified Organic Fertilizer (50kg)",
            "category": "agriculture",
            "subcategory": "supplies",
            "price": 1500,
            "original_price": 2500,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=800&q=80"],
            "description": "High-quality, eco-friendly organic fertilizer. Subsidized rate for registered farmers.",
            "features": [
                "100% Organic",
                "Government Certified",
                "Rich in nutrients",
                "Suitable for all crops"
            ],
            "tags": ["agriculture", "farming", "organic", "fertilizer"],
            "target_segments": ["farmer", "home_gardener", "business_owner"],
            "in_stock": True,
            "delivery_options": ["pickup"],
            "rating": 4.5,
            "reviews_count": 450,
            "created": datetime.utcnow()
        },
        {
            "id": "prod_driver_training",
            "name": "Heavy Vehicle Driving Course",
            "category": "training",
            "subcategory": "skills",
            "price": 25000,
            "currency": "LKR",
            "images": ["https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?w=800&q=80"],
            "description": "Comprehensive training course for heavy vehicle driving license. Includes theory and practical sessions.",
            "features": [
                "RMV Approved Curriculum",
                "Experienced Instructors",
                "Practical sessions included",
                "License application support"
            ],
            "tags": ["driving", "training", "license", "career"],
            "target_segments": ["young_adult", "job_seeker", "career_changer"],
            "in_stock": True,
            "delivery_options": ["classroom"],
            "rating": 4.6,
            "reviews_count": 112,
            "created": datetime.utcnow()
        }
    ]
    try:
        products_col.insert_many(products, ordered=False)
        print(f"✓ Seeded {len(products)} products")
    except errors.BulkWriteError as bwe:
        print("Note: some products may already exist. BulkWriteError:", bwe.details)
    except Exception as e:
        print(f"Failed to seed products: {e}", file=sys.stderr)

def seed_sample_users():
    print("\n[7/7] Seeding sample users...")
    sample_users = []

    # Government employees without degrees
    for i in range(15):
        age = random.randint(35, 45)
        children_count = random.randint(1, 3)
        children_ages = [random.randint(5, 20) for _ in range(children_count)]

        user = {
            "sample_data": True,
            "profile": {
                "basic": {
                    "name": f"Government Employee {i+1}",
                    "age": age,
                    "location": random.choice(["Colombo", "Kandy", "Gampaha", "Galle"]),
                    "phone": f"071{random.randint(1000000, 9999999)}"
                }
            },
            "extended_profile": {
                "family": {
                    "age": age,
                    "marital_status": "married",
                    "children": [f"Child {j+1}" for j in range(children_count)],
                    "children_ages": children_ages,
                    "children_education": [random.choice(["primary", "secondary", "ol", "tuition"]) for _ in range(children_count)],
                    "dependents": children_count
                },
                "education": {
                    "highest_qualification": random.choice(["ol", "al", "diploma"]),
                    "institution": "Local School/College",
                    "year_graduated": 2000 + random.randint(0, 10)
                },
                "career": {
                    "current_job": f"Government {random.choice(['Clerk', 'Officer', 'Administrator'])}",
                    "years_experience": age - 22,
                    "skills": ["administration", "management"],
                    "career_goals": ["degree_completion", "promotion"]
                },
                "interests": {
                    "learning_interests": ["degree_programs", "professional_courses"],
                    "service_preferences": ["education", "career_development"]
                },
                "consent": {
                    "marketing_emails": True,
                    "personalized_ads": True,
                    "data_analytics": True
                }
            },
            "created": datetime.utcnow() - timedelta(days=random.randint(1, 365)),
            "last_active": datetime.utcnow() - timedelta(hours=random.randint(1, 72))
        }
        sample_users.append(user)

    # Young professionals
    for i in range(15):
        age = random.randint(25, 35)
        user = {
            "sample_data": True,
            "profile": {
                "basic": {
                    "name": f"Young Professional {i+1}",
                    "age": age,
                    "location": random.choice(["Colombo", "Kandy", "Negombo"]),
                    "phone": f"077{random.randint(1000000, 9999999)}"
                }
            },
            "extended_profile": {
                "family": {
                    "age": age,
                    "marital_status": random.choice(["single", "married"])
                },
                "education": {
                    "highest_qualification": random.choice(["degree", "diploma", "al"]),
                    "year_graduated": 2015 + random.randint(0, 8)
                },
                "career": {
                    "current_job": f"{random.choice(['IT', 'Marketing', 'Finance'])} Executive",
                    "career_goals": ["overseas_opportunities", "skill_development"]
                },
                "interests": {
                    "learning_interests": ["ielts", "overseas_jobs", "certifications"]
                },
                "consent": {
                    "marketing_emails": True,
                    "personalized_ads": True
                }
            },
            "created": datetime.utcnow() - timedelta(days=random.randint(1, 365))
        }
        sample_users.append(user)

    # Parents with school children
    for i in range(20):
        age = random.randint(40, 55)
        children_count = random.randint(1, 3)
        children_ages = [random.randint(5, 18) for _ in range(children_count)]

        user = {
            "sample_data": True,
            "profile": {
                "basic": {
                    "name": f"Parent {i+1}",
                    "age": age,
                    "location": random.choice(["Colombo", "Kandy", "Kurunegala"]),
                    "phone": f"075{random.randint(1000000, 9999999)}"
                }
            },
            "extended_profile": {
                "family": {
                    "age": age,
                    "marital_status": "married",
                    "children": [f"Child {j+1}" for j in range(children_count)],
                    "children_ages": children_ages,
                    "children_education": [random.choice(["primary", "secondary", "ol_prep", "al_prep"]) for _ in range(children_count)]
                },
                "education": {
                    "highest_qualification": random.choice(["al", "degree", "diploma"])
                },
                "career": {
                    "current_job": random.choice(["Business Owner", "Teacher", "Professional"]),
                    "career_goals": ["children_education", "financial_security"]
                },
                "interests": {
                    "learning_interests": ["children_education", "exam_preparation"],
                    "service_preferences": ["education_services", "family_products"]
                },
                "consent": {
                    "marketing_emails": True,
                    "personalized_ads": True
                }
            },
            "created": datetime.utcnow() - timedelta(days=random.randint(1, 365))
        }
        sample_users.append(user)

    try:
        users_col.insert_many(sample_users, ordered=False)
        print(f"✓ Seeded {len(sample_users)} sample users")
    except errors.BulkWriteError as bwe:
        print("Note: some sample users may already exist. BulkWriteError:", bwe.details)
    except Exception as e:
        print(f"Failed to seed sample users: {e}", file=sys.stderr)

def ensure_admin():
    if admins_col.count_documents({}) == 0:
        pwd = os.getenv("ADMIN_PWD", "admin123")
        hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
        try:
            admins_col.insert_one({
                "username": "admin",
                "email": os.getenv("ADMIN_EMAIL", "admin@example.com"),
                "password": hashed,
                "created": datetime.utcnow()
            })
            print("\n✓ Admin user created (username: admin)")
        except errors.DuplicateKeyError:
            print("Admin user already exists (duplicate key).")
        except Exception as e:
            print(f"Failed to create admin user: {e}", file=sys.stderr)
    else:
        print("Admin user(s) already present, skipping admin creation.")

def print_summary():
    print("\n" + "=" * 60)
    print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print(f"\nServices: {services_col.count_documents({})}")
    print(f"Categories: {categories_col.count_documents({})}")
    print(f"Officers: {officers_col.count_documents({})}")
    print(f"Ads: {ads_col.count_documents({})}")
    print(f"Products: {products_col.count_documents({})}")
    print(f"Sample Users: {users_col.count_documents({'sample_data': True})}")
    print(f"Admins: {admins_col.count_documents({})}")
    print("\nNext steps:")
    print("1. Run the app: python app.py")
    print("2. Login to admin panel: http://localhost:5000/admin")
    print("3. Build AI index: flask build-index (Required for AI search)")
    print("\nNote: This script only removes sample users (sample_data=True). It clears services/products/ads to ensure consistent seed state.")

def main():
    print("=" * 60)
    print("CITIZEN PORTAL - DATABASE SEEDING")
    print("=" * 60)

    create_indexes()
    clear_collections()
    seed_categories()
    seed_services()
    seed_officers()
    seed_ads()
    seed_products()
    seed_sample_users()
    ensure_admin()
    print_summary()

if __name__ == "__main__":
    main()