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
from datetime import datetime, timedelta, timezone
import os
import random
from dotenv import load_dotenv
import bcrypt
import sys

if os.path.exists(".env"):
    load_dotenv()
elif os.path.exists("backend/.env"):
    load_dotenv("backend/.env")

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
        users_col.create_index("email", unique=True)
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
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "cat_public",
            "name": {"en": "Public Administration", "si": "පොදු පරිපාලන", "ta": "பொது நிர்வாகம்"},
            "ministry_ids": ["ministry_public"],
            "icon": "government",
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "cat_land",
            "name": {"en": "Land & Housing", "si": "ඉඩම් සහ නිවාස", "ta": "நிலம் மற்றும் வீடுகள்"},
            "ministry_ids": ["ministry_land", "ministry_housing"],
            "icon": "home",
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "cat_education",
            "name": {"en": "Education", "si": "අධ්‍යාපනය", "ta": "கல்வி"},
            "ministry_ids": ["ministry_education"],
            "icon": "school",
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "cat_health",
            "name": {"en": "Health Services", "si": "සෞඛ්‍ය සේවා", "ta": "சுகாதார சேவைகள்"},
            "ministry_ids": ["ministry_health"],
            "icon": "hospital",
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "cat_transport",
            "name": {"en": "Transport & Vehicles", "si": "ප්‍රවාහන සහ වාහන", "ta": "போக்குவரத்து மற்றும் வாகனங்கள்"},
            "ministry_ids": ["ministry_transport"],
            "icon": "car",
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "cat_immigration",
            "name": {"en": "Immigration & Emigration", "si": "ආගමන හා විගමන", "ta": "குடிவரவு மற்றும் குடியகல்வு"},
            "ministry_ids": ["dept_immigration"],
            "icon": "passport",
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "cat_finance",
            "name": {"en": "Finance & Tax", "si": "මුදල් සහ බදු", "ta": "நிதி மற்றும் வரி"},
            "ministry_ids": ["ministry_finance"],
            "icon": "money",
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "cat_agriculture",
            "name": {"en": "Agriculture", "si": "කෘෂිකර්මය", "ta": "விவசாயம்"},
            "ministry_ids": ["ministry_agriculture"],
            "icon": "leaf",
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "cat_documents",
            "name": {"en": "Official Documents & Services", "si": "නිල ලේඛන සහ සේවා", "ta": "அதிகாரபூர்வ ஆவணங்கள் மற்றும் சேவைகள்"},
            "ministry_ids": ["ministry_documents"],
            "icon": "document",
            "created": datetime.now(timezone.utc)
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
            "id": "ministry_documents",
            "category": "cat_documents",
            "name": {"en": "Department for Registration of Persons & RGD", "si": "පුද්ගලයින් ලියාපදිංචි කිරීමේ දෙපාර්තමේන්තුව", "ta": "ஆட்பதிவுத் திணைக்களம்"},
            "subservices": [
                {
                    "id": "nic_service",
                    "name": {"en": "National Identity Card (NIC)", "si": "ජාතික හැඳුනුම්පත", "ta": "தேசிய அடையாள அட்டை"},
                    "questions": [
                        {
                            "q": {"en": "How to apply for a new NIC?", "si": "නව ජාතික හැඳුනුම්පතක් සඳහා අයදුම් කරන්නේ කෙසේද?", "ta": "புதிய தேசிய அடையாள அட்டைக்கு எவ்வாறு விண்ணப்பிப்பது?"},
                            "answer": {"en": "Submit your application through your Grama Niladhari to the Divisional Secretariat.", "si": "ඔබගේ අයදුම්පත ග්‍රාම නිලධාරී හරහා ප්‍රාදේශීය ලේකම් කාර්යාලයට ඉදිරිපත් කරන්න.", "ta": "உங்கள் கிராம உத்தியோகத்தர் மூலம் பிரதேச செயலகத்திற்கு விண்ணப்பத்தை சமர்ப்பிக்கவும்."},
                            "downloads": ["/static/docs/nic-application.pdf"],  # Official DRP form
                            "location": "https://drp.gov.lk",
                            "verified_source": True,
                            "eligibility": "Sri Lankan citizen over 15 years of age",
                            "processing_time": "1 Day (Urgent), 14 Days (Normal)",
                            "supporting_docs": ["Birth Certificate", "Grama Niladhari Certificate", "3 Passport Size Photos"]
                        }
                    ]
                },
                {
                    "id": "civil_certs",
                    "name": {"en": "Birth/Marriage/Death Certificates", "si": "උප්පැන්න/විවාහ/මරණ සහතික", "ta": "பிறப்பு/திருமண/இறப்பு சான்றிதழ்கள்"},
                    "questions": [
                        {
                            "q": {"en": "How to obtain a certified copy of a birth certificate?", "si": "උප්පැන්න සහතිකයේ සහතික කළ පිටපතක් ලබා ගන්නේ කෙසේද?", "ta": "பிறப்புச் சான்றிதழின் சான்றளிக்கப்பட்ட நகலை எவ்வாறு பெறுவது?"},
                            "answer": {"en": "Apply via the Registrar General's Department online portal or visit your Divisional Secretariat.", "si": "රෙජිස්ට්‍රාර් ජනරාල් දෙපාර්තමේන්තුවේ මාර්ගගත ද්වාරය හරහා අයදුම් කරන්න.", "ta": "பதிவாளர் நாயகம் திணைக்களத்தின் இணைய தளம் மூலம் விண்ணப்பிக்கவும்."},
                            "downloads": ["/static/docs/B63-BirthCert.pdf"],  # Official RGD Birth Cert form
                            "location": "https://www.rgd.gov.lk",
                            "verified_source": True,
                            "eligibility": "Any citizen",
                            "processing_time": "3-5 Working Days",
                            "supporting_docs": ["NIC Copy", "Application Form B63"]
                        }
                    ]
                }
            ],
            "created": datetime.now(timezone.utc)
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
                            "q": {"en": "How to apply for a new passport?", "si": "නව විදේශ ගමන් බලපත්‍රයක් සඳහා අයදුම් කරන්නේ කෙසේද?"},
                            "answer": {"en": "Book an appointment online and visit the head office or regional office. Online appointment is mandatory.", "si": "මාර්ගගතව වේලාවක් වෙන්කර ප්‍රධාන කාර්යාලයට හෝ ප්‍රාදේශීය කාර්යාලයට පැමිණෙන්න."},
                            "location": "https://www.immigration.gov.lk",
                            "downloads": ["/static/docs/K35A-Passport.pdf"],  # Official Immigration Department form
                            "verified_source": True,
                            "eligibility": "Sri Lankan Citizen",
                            "processing_time": "1 Day (Urgent LKR 20,000), 30 Days (Normal LKR 5,000)",
                            "supporting_docs": ["Original Birth Certificate", "NIC", "Studio Photo Receipt"]
                        }
                    ]
                }
            ],
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "ministry_transport",
            "category": "cat_transport",
            "name": {"en": "Department of Motor Traffic", "si": "මෝටර් රථ ප්‍රවාහන දෙපාර්තමේන්තුව", "ta": "மோட்டார் போக்குவரத்து திணைக்களம்"},
            "subservices": [
                {
                    "id": "driving_license",
                    "name": {"en": "Driving License Services", "si": "රියදුරු බලපත්‍ර සේවා"},
                    "questions": [
                        {
                            "q": {"en": "How to apply for a new driving license?"},
                            "answer": {"en": "Visit DMT Werahera or a district office with your NIC and NTMI medical certificate."},
                            "location": "https://dmt.gov.lk",
                            "downloads": ["/static/docs/MTA30-DrivingLicense.pdf"],  # Official DMT form MTA30
                            "verified_source": True,
                            "eligibility": "Age 18+ for Light Vehicles",
                            "processing_time": "Written exam immediately, practical after 3 months",
                            "supporting_docs": ["NIC", "Birth Certificate", "NTMI Medical Certificate"]
                        }
                    ]
                },
                {
                    "id": "vehicle_reg",
                    "name": {"en": "Vehicle Registration & Transfer", "si": "වාහන ලියාපදිංචිය සහ පැවරීම"},
                    "questions": [
                        {
                            "q": {"en": "How to transfer vehicle ownership?"},
                            "answer": {"en": "Submit MTA 6 and MTA 8 forms along with the CR and revenue license to the DMT."}
                        }
                    ]
                }
            ],
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "ministry_finance",
            "category": "cat_finance",
            "name": {"en": "Inland Revenue Department", "si": "දේශීය ආදායම් දෙපාර්තමේන්තුව", "ta": "உள்நாட்டு இறைவரித் திணைக்களம்"},
            "subservices": [
                {
                    "id": "tin_reg",
                    "name": {"en": "TIN Registration (Taxpayer ID)", "si": "බදු ගෙවන්නා හඳුනාගැනීමේ අංකය"},
                    "questions": [
                        {
                            "q": {"en": "How to register for a TIN number online?"},
                            "answer": {"en": "Use the IRD e-Services portal to register for a TIN. It is mandatory for all citizens over 18."},
                            "location": "https://eservices.ird.gov.lk/Registration/TINRegistration",
                            "verified_source": True,
                            "eligibility": "Any citizen over 18 or Registered Business",
                            "processing_time": "Instant via e-Services",
                            "supporting_docs": ["NIC Copy (both sides)", "Proof of billing address"],
                            "downloads": ["/static/docs/TIN-Application.pdf"]  # Official IRD TIN form TPR_002_E
                        }
                    ]
                }
            ],
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "ministry_public",
            "category": "cat_public",
            "name": {"en": "Sri Lanka Police & Public Services", "si": "ශ්‍රී ලංකා පොලිසිය සහ රාජ්‍ය සේවා", "ta": "இலங்கை பொலிஸ் மற்றும் பொது சேவைகள்"},
            "subservices": [
                {
                    "id": "police_clearance",
                    "name": {"en": "Police Clearance Certificate", "si": "පොලිස් නිෂ්කාශන සහතිකය"},
                    "questions": [
                        {
                            "q": {"en": "How to apply for a Police Clearance Certificate online?"},
                            "answer": {"en": "Apply through the official Sri Lanka Police e-Services portal. Required for visas and foreign employment."},
                            "location": "https://www.police.lk/index.php/clearance-certificate/",
                            "verified_source": True,
                            "eligibility": "Sri Lankan Citizens and foreigners who resided in Sri Lanka",
                            "processing_time": "14 Working Days",
                            "supporting_docs": ["NIC Copy", "Valid Passport Copy", "Application Form"],
                            "downloads": ["/static/docs/Police-Clearance.pdf"]  # Official Sri Lanka Police form
                        }
                    ]
                },
                {
                    "id": "pension",
                    "name": {"en": "Department of Pensions", "si": "විශ්‍රාම වැටුප් දෙපාර්තමේන්තුව"},
                    "questions": [
                        {
                            "q": {"en": "How to check my pension status?"},
                            "answer": {"en": "Log into the Department of Pensions portal using your Pension ID."},
                            "location": "https://www.pensions.gov.lk/",
                            "verified_source": True,
                            "processing_time": "Instant lookup",
                            "supporting_docs": ["Pension ID number"]
                        }
                    ]
                }
            ],
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "ministry_land",
            "category": "cat_land",
            "name": {"en": "Land Registry & Survey Department", "si": "ඉඩම් ලියාපදිංචි කිරීමේ දෙපාර්තමේන්තුව", "ta": "காணிப் பதிவாளர் திணைக்களம்"},
            "subservices": [
                {
                    "id": "land_title",
                    "name": {"en": "Title Registration & Search", "si": "ඔප්පු ලියාපදිංචිය සහ සෙවීම"},
                    "questions": [
                        {
                            "q": {"en": "How to obtain a certified copy of a deed?"},
                            "answer": {"en": "Submit a request to your district Land Registry with the relevant folio numbers and stamps."},
                            "location": "https://rgd.gov.lk",
                            "verified_source": True,
                            "eligibility": "Property Owners or Authorized Representatives",
                            "processing_time": "1-2 Weeks",
                            "supporting_docs": ["Folio/Deed Number Details", "NIC"]
                        }
                    ]
                }
            ],
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "ministry_it",
            "category": "cat_it",
            "name": {"en": "Information and Communication Technology Agency", "si": "තොරතුරු හා සන්නිවේදන තාක්ෂණ නියෝජිතායතනය", "ta": "தகவல் மற்றும் தொடர்பு தொழில்நுட்ப நிறுவனம்"},
            "subservices": [
                {
                    "id": "digital_id",
                    "name": {"en": "Lanka Gate e-Services", "si": "ලංකා ගේට් ඊ-සේවා", "ta": "லங்கா கேட் இ-சேவைகள்"},
                    "questions": [
                        {
                            "q": {"en": "How to access government e-Services online?", "si": "රජයේ ඊ-සේවා මාර්ගගතව ලබා ගන්නේ කෙසේද?"},
                            "answer": {"en": "Register through the Lanka Gate portal (srilanka.lk) to access hundreds of government digital services from a single account."},
                            "location": "https://www.srilanka.lk",
                            "downloads": [],
                            "verified_source": True,
                            "eligibility": "All Sri Lankan Citizens",
                            "processing_time": "Instant Registration",
                            "supporting_docs": ["NIC", "Valid Email", "Mobile Number"]
                        }
                    ]
                }
            ],
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "ministry_education",
            "category": "cat_education",
            "name": {"en": "Ministry of Education", "si": "අධ්‍යාපන අමාත්‍යාංශය", "ta": "கல்வி அமைச்சு"},
            "subservices": [
                {
                    "id": "school_admission",
                    "name": {"en": "School Admissions", "si": "පාසල් ප්‍රවේශය", "ta": "பாடசாலை அனுமதி"},
                    "questions": [
                        {
                            "q": {"en": "How to apply for Grade 1 admission in a government school?", "si": "රජයේ පාසලක පළමු ශ්‍රේණියට ඇතුළත් වීමට අයදුම් කරන්නේ කෙසේද?"},
                            "answer": {"en": "Submit the standardized application form to the school principal before the annual deadline published by the Ministry of Education."},
                            "location": "https://moe.gov.lk",
                            "downloads": ["/static/docs/Grade1-Admission-Si.pdf", "/static/docs/Grade1-Admission-Ta.pdf"],
                            "verified_source": True,
                            "eligibility": "Children turning 5 years of age by January 31st of the admission year",
                            "processing_time": "Annual cycle (June-August applications)",
                            "supporting_docs": ["Birth Certificate", "Proof of Residence (Deed/Lease)", "Electoral Register Extracts"]
                        }
                    ]
                },
                {
                    "id": "exam_results",
                    "name": {"en": "Department of Examinations", "si": "විභාග දෙපාර්තමේන්තුව", "ta": "பரீட்சை திணைக்களம்"},
                    "questions": [
                        {
                            "q": {"en": "How to check G.C.E. O/L and A/L results online?"},
                            "answer": {"en": "Visit the official Department of Examinations portal and enter your Index Number or NIC to view results."},
                            "location": "https://www.doenets.lk",
                            "downloads": [],
                            "verified_source": True,
                            "eligibility": "Registered Candidates",
                            "processing_time": "Instant lookup",
                            "supporting_docs": ["Index Number", "NIC"]
                        }
                    ]
                }
            ],
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "ministry_health",
            "category": "cat_health",
            "name": {"en": "Ministry of Health", "si": "සෞඛ්‍ය අමාත්‍යාංශය", "ta": "சுகாதார அமைச்சு"},
            "subservices": [
                {
                    "id": "ambulance",
                    "name": {"en": "1990 Suwa Seriya Ambulance", "si": "1990 සුව සැරිය ගිලන් රථ සේවාව", "ta": "1990 சுவ செரிய நோயாளர் காவு வண்டி"},
                    "questions": [
                        {
                            "q": {"en": "How to call a government ambulance in an emergency?", "si": "හදිසි අවස්ථාවකදී රජයේ ගිලන් රථයක් අමතන්නේ කෙසේද?"},
                            "answer": {"en": "Dial 1990 toll-free from any network for emergency pre-hospital care transport to the nearest government hospital."},
                            "location": "https://www.health.gov.lk",
                            "downloads": [],
                            "verified_source": True,
                            "eligibility": "Any person needing emergency medical transport",
                            "processing_time": "Immediate dispatch (Average response time 11 mins)",
                            "supporting_docs": ["None required during emergency"]
                        }
                    ]
                }
            ],
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "ministry_agriculture",
            "category": "cat_agriculture",
            "name": {"en": "Department of Agrarian Development", "si": "ගොවිජන සංවර්ධන දෙපාර්තමේන්තුව", "ta": "விவசாய அபிவிருத்தி திணைக்களம்"},
            "subservices": [
                {
                    "id": "fertilizer",
                    "name": {"en": "Fertilizer Subsidy Scheme", "si": "පොහොර සහනාධාර ක්‍රමය", "ta": "உர மானியத் திட்டம்"},
                    "questions": [
                        {
                            "q": {"en": "How to apply for the government fertilizer subsidy?", "si": "රජයේ පොහොර සහනාධාරය සඳහා අයදුම් කරන්නේ කෙසේද?"},
                            "answer": {"en": "Register your cultivation details with the regional Agrarian Services Center. Subsidy will be directly credited to your bank account."},
                            "location": "https://www.agrimin.gov.lk",
                            "downloads": [],
                            "verified_source": True,
                            "eligibility": "Registered farmers cultivating Paddy or specific cash crops",
                            "processing_time": "Seasonal (Maha/Yala)",
                            "supporting_docs": ["Farmer ID (Govi ID)", "Land Ownership/Cultivation Proof", "Bank Account Details"]
                        }
                    ]
                }
            ],
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
        },
        {
            "id": "off_edu_01",
            "name": "Mr. Ruwan Silva",
            "role": "Assistant Secretary - Education",
            "ministry_id": "ministry_education",
            "contact": {"email": "ruwan@edu.gov.lk", "phone": "+94 71 987 6543"},
            "created": datetime.now(timezone.utc)
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
        # --- OFFICIAL GOVERNMENT ANNOUNCEMENTS (Citizen-Targeted) ---
        {
            "id": "ad_nic_renewal",
            "title": "NIC Renewal Reminder - Smart NIC Available",
            "body": "The Department for Registration of Persons now issues the Smart National Identity Card. Apply for renewal or a new NIC online via the official portal.",
            "link": "https://drp.gov.lk",
            "link_label": "Apply at DRP Portal",
            "link_type": "external",
            "active": True,
            "priority": "high",
            "tags": ["nic", "identity", "documents", "government"],
            "target_segments": ["young_adult", "all_citizens"],
            "created": datetime.now(timezone.utc),
            "end_date": datetime.now(timezone.utc) + timedelta(days=365)
        },
        {
            "id": "ad_passport_eappointment",
            "title": "Apply for Passports Online - New System",
            "body": "The Department of Immigration and Emigration has launched a new online portal for passport applications. Apply from home and get your appointment integrated with the application process.",
            "link": "https://eservices.immigration.gov.lk/onlinetd/OnlineTD/",
            "link_label": "Apply Online Now",
            "link_type": "external",
            "active": True,
            "priority": "high",
            "tags": ["passport", "immigration", "travel", "overseas"],
            "target_segments": ["overseas_interested", "young_adult", "early_career"],
            "created": datetime.now(timezone.utc),
            "end_date": datetime.now(timezone.utc) + timedelta(days=365)
        },
        {
            "id": "ad_grade1_admission",
            "title": "Grade 1 Admissions 2026 - Applications Open",
            "body": "Applications for Grade 1 admission to government schools for 2026 are now open. Submit to the school principal before the Ministry deadline.",
            "link": "https://moe.gov.lk",
            "link_label": "Ministry of Education",
            "link_type": "external",
            "active": True,
            "priority": "high",
            "tags": ["school", "education", "grade1", "admission", "children"],
            "target_segments": ["parent", "secondary_school_parent", "family"],
            "created": datetime.now(timezone.utc),
            "end_date": datetime.now(timezone.utc) + timedelta(days=180)
        },
        {
            "id": "ad_tin_registration",
            "title": "TIN Registration Now Mandatory for All Citizens Over 18",
            "body": "The Inland Revenue Department requires all citizens over 18 to register for a Taxpayer Identification Number (TIN). Register free via e-Services.",
            "link": "https://eservices.ird.gov.lk/Registration/TINRegistration",
            "link_label": "Register TIN Online (IRD)",
            "link_type": "external",
            "active": True,
            "priority": "high",
            "tags": ["tin", "tax", "ird", "finance", "registration"],
            "target_segments": ["government_employee", "mid_career_family", "early_career"],
            "created": datetime.now(timezone.utc),
            "end_date": datetime.now(timezone.utc) + timedelta(days=365)
        },
        {
            "id": "ad_police_clearance",
            "title": "Police Clearance Certificate - Online Application",
            "body": "Sri Lanka Police now accepts online applications for Police Clearance Certificates required for foreign employment and visa applications.",
            "link": "https://www.police.lk/?page_id=907",
            "link_label": "Apply at Police e-Services",
            "link_type": "external",
            "active": True,
            "priority": "medium",
            "tags": ["police", "clearance", "overseas", "visa", "employment"],
            "target_segments": ["overseas_interested", "young_adult", "early_career"],
            "created": datetime.now(timezone.utc),
            "end_date": datetime.now(timezone.utc) + timedelta(days=365)
        },
        {
            "id": "ad_suwa_seriya",
            "title": "1990 Suwa Seriya - Free Emergency Ambulance",
            "body": "Call 1990 toll-free for emergency ambulance service available 24/7 across Sri Lanka. Service is completely free for all citizens.",
            "link": "https://www.health.gov.lk",
            "link_label": "Ministry of Health",
            "link_type": "external",
            "active": True,
            "priority": "high",
            "tags": ["health", "ambulance", "emergency", "free"],
            "target_segments": ["all_citizens", "elderly", "family"],
            "created": datetime.now(timezone.utc),
            "end_date": datetime.now(timezone.utc) + timedelta(days=730)
        },
        {
            "id": "ad_fertilizer_subsidy",
            "title": "Fertilizer Subsidy Scheme - Maha Season Registration",
            "body": "Registered paddy farmers can apply for the government fertilizer subsidy at their regional Agrarian Services Center. Subsidy credited directly to your bank.",
            "link": "https://www.agrimin.gov.lk",
            "link_label": "Department of Agriculture",
            "link_type": "external",
            "active": True,
            "priority": "medium",
            "tags": ["agriculture", "fertilizer", "subsidy", "farmers", "paddy"],
            "target_segments": ["farmer", "rural", "agriculture"],
            "created": datetime.now(timezone.utc),
            "end_date": datetime.now(timezone.utc) + timedelta(days=180)
        },
        {
            "id": "ad_eservices_lanka",
            "title": "Lanka Gate - All Government Services Online",
            "body": "Access 200+ government services through a single digital account at srilanka.lk. Save time with online applications, payments and tracking.",
            "link": "https://www.srilanka.lk",
            "link_label": "Visit Lanka Gate",
            "link_type": "external",
            "active": True,
            "priority": "medium",
            "tags": ["digital", "eservices", "online", "government"],
            "target_segments": ["tech_professional", "young_adult", "government_employee"],
            "created": datetime.now(timezone.utc),
            "end_date": datetime.now(timezone.utc) + timedelta(days=730)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc)
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
            "created": datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365)),
            "last_active": datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72))
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
            "created": datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365))
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
            "created": datetime.now(timezone.utc) - timedelta(days=random.randint(1, 365))
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
                "created": datetime.now(timezone.utc)
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