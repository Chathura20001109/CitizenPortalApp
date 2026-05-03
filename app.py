# Load env variables
from dotenv import load_dotenv
import os
import pathlib

# Check root then backend folder for .env
if os.path.exists(".env"):
    load_dotenv()
elif os.path.exists("backend/.env"):
    load_dotenv("backend/.env")
import json
import logging
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
import re
from functools import wraps
import pathlib

from flask import Flask, jsonify, render_template, request, session, redirect, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import bcrypt
import numpy as np
from bson import ObjectId

try:
    import google.generativeai as genai
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    AI_AVAILABLE = True if GEMINI_API_KEY else False
except ImportError:
    AI_AVAILABLE = False

# FAISS and SentenceTransformers removed for Vercel size limits
FAISS_AVAILABLE = False

# ---------------- Flask App ----------------
app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret")
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv("MAX_CONTENT_LENGTH", 16777216))
app.config['SESSION_COOKIE_SECURE'] = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv("SESSION_COOKIE_HTTPONLY", "True") == "True"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

CORS(app, resources={r"/api/*": {"origins": "*"}})

# ---------------- Logging ----------------
try:
    os.makedirs("logs", exist_ok=True)
    log_file = os.getenv("LOG_FILE", "./logs/app.log")
    handlers = [logging.FileHandler(log_file), logging.StreamHandler()]
except Exception:
    handlers = [logging.StreamHandler()]

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

# ---------------- MongoDB ----------------
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "citizen_portal")

if not MONGO_URI:
    logger.warning("MONGO_URI not found. Application will use MockMongoClient.")

class MockCursor:
    def __init__(self, data):
        self.data = data
    def __iter__(self): return iter(self.data)
    def limit(self, *args, **kwargs): return MockCursor(self.data[:args[0]])
    def sort(self, *args, **kwargs): return self

class MockCollection:
    def __init__(self, name):
        self.name = name
        self.docs = []
    
    def find(self, query=None, *args, **kwargs):
        if not query: return MockCursor(self.docs)
        res = []
        for d in self.docs:
            match = True
            for k, v in query.items():
                if isinstance(v, dict): continue
                if str(d.get(k)) != str(v): match = False
            if match: res.append(d)
        return MockCursor(res)
        
    def find_one(self, query=None, *args, **kwargs):
        if not query: return self.docs[0] if self.docs else None
        for d in self.docs:
            match = True
            for k, v in query.items():
                if isinstance(v, dict): continue
                if str(d.get(k)) != str(v): match = False
            if match: return d
        return None
        
    def insert_one(self, doc, *args, **kwargs):
        from bson import ObjectId
        if '_id' not in doc:
            doc['_id'] = ObjectId()
        self.docs.append(doc)
        class Result: 
            def __init__(self, id): self.inserted_id = id
        return Result(doc['_id'])
        
    def update_one(self, query, update, *args, **kwargs):
        doc = self.find_one(query)
        if doc and '$set' in update:
            for k, v in update['$set'].items():
                keys = k.split('.')
                curr = doc
                for key in keys[:-1]:
                    if key not in curr: curr[key] = {}
                    curr = curr[key]
                curr[keys[-1]] = v
                
    def update_many(self, query, update, *args, **kwargs):
        docs = list(self.find(query))
        for doc in docs:
            if '$set' in update:
                for k, v in update['$set'].items():
                    doc[k] = v
        
    def delete_one(self, query, *args, **kwargs):
        doc = self.find_one(query)
        if doc:
            self.docs.remove(doc)
            class Result: deleted_count = 1
            return Result()
        class Result: deleted_count = 0
        return Result()
        
    def count_documents(self, query=None, *args, **kwargs):
        return len(list(self.find(query)))
        
    def distinct(self, key, *args, **kwargs):
        return list(set(d.get(key) for d in self.docs if key in d and d.get(key) is not None))

class MockDB:
    def __init__(self):
        self.collections = {}
    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection(name)
        return self.collections[name]

class MockMongoClient:
    def __init__(self, *args, **kwargs):
        self.admin = self
        self.db = MockDB()
    def command(self, *args, **kwargs): pass
    def __getitem__(self, name): return self.db

try:
    if MONGO_URI:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        logger.info("MongoDB client created")
    else:
        logger.warning("No MONGO_URI provided, skipping real connection.")
        client = MockMongoClient()
except Exception as e:
    logger.warning(f"MongoDB connection failed: {e}. Falling back to in-memory MockMongoClient.")
    client = MockMongoClient()

db = client[DB_NAME]

# Collections
admins_col = db["admins"]
categories_col = db["categories"]
products_col = db["products"]
orders_col = db["orders"]
users_col = db["users"]
eng_col = db["engagements"]
ads_col = db["ads"]
payments_col = db["payments"]
services_col = db["services"]
citizen_logs_col = db["citizen_access_logs"]  # stores login/logout events

# Directories
os.makedirs("data", exist_ok=True)
INDEX_PATH = pathlib.Path("data/faiss.index")
META_PATH = pathlib.Path("data/faiss_meta.json")

def get_embeddings(texts):
    """Get embeddings using Google Gemini API"""
    if not AI_AVAILABLE:
        return None
    try:
        # Using the lightweight embedding model
        result = genai.embed_content(
            model="models/embedding-001",
            content=texts,
            task_type="retrieval_document"
        )
        return np.array(result['embedding'], dtype='float32')
    except Exception as e:
        logger.error(f"Gemini Embedding error: {e}")
        return None

def cosine_sim(a, b):
    """Simple cosine similarity using numpy"""
    # a: (1, dim), b: (N, dim)
    norm_a = np.linalg.norm(a, axis=1, keepdims=True)
    norm_b = np.linalg.norm(b, axis=1, keepdims=True)
    return np.dot(a, b.T) / (norm_a * norm_b.T)

# ---------------- Decorators ----------------
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not (session.get("admin_logged_in") or session.get("admin")):
            return jsonify({"error": "Unauthorized"}), 401
        return fn(*args, **kwargs)
    return wrapper

def handle_errors(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {fn.__name__}: {e}", exc_info=True)
            return jsonify({"error": "Internal server error", "message": str(e)}), 500
    return wrapper

# ── Citizen token helpers ─────────────────────────────────────────────────────
def generate_citizen_token(user_id: str) -> str:
    """Create a simple signed token: sha256(user_id + secret)."""
    raw = f"{user_id}:{app.secret_key}"
    return hashlib.sha256(raw.encode()).hexdigest()

def citizen_required(fn):
    """Decorator: require a valid citizen token in Authorization header."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "").strip()
        user_id = request.headers.get("X-Citizen-Id", "").strip()
        if not token or not user_id:
            return jsonify({"error": "Authentication required"}), 401
            
        expected = generate_citizen_token(user_id)
        # Check backward compatibility with older date-based tokens (up to 120 days old)
        valid_tokens = [expected]
        for i in range(120):
            valid_tokens.append(hashlib.sha256(f"{user_id}:{app.secret_key}:{(datetime.now(timezone.utc) - timedelta(days=i)).date()}".encode()).hexdigest())
        
        if token not in valid_tokens:
            logger.error(f"401 Token mismatch - UserID: {user_id}, Token: {token}")
            return jsonify({"error": "Invalid or expired token"}), 401
        request.citizen_id = user_id
        return fn(*args, **kwargs)
    return wrapper

# ---------------- Routes ----------------
@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "mongodb": "mock" if isinstance(client, MockMongoClient) else "connected",
        "ai": AI_AVAILABLE
    })

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/citizen/login")
def citizen_login_page():
    return render_template("citizen_login.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/store")
def store():
    return render_template("store.html")

# ---------------- Admin ----------------
@app.route("/admin")
def admin_dashboard():
    if not (session.get("admin_logged_in") or session.get("admin")):
        return redirect("/admin/login")
    return render_template("admin.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect("/admin")
    if request.method == "GET":
        return render_template("login.html")
    data = request.form or request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")
    admin = admins_col.find_one({"username": username})
    if admin:
        stored = admin.get("password")
        if isinstance(stored, bytes):
            ok = bcrypt.checkpw(password.encode("utf-8"), stored)
        else:
            ok = stored == password
        if ok:
            session.permanent = True
            session["admin_logged_in"] = True
            session["admin_user"] = username
            session["admin"] = True
            return redirect("/admin")
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/admin/logout", methods=["POST"])
@admin_required
def admin_logout():
    session.clear()
    return jsonify({"status": "logged out"})

# ---------------- Citizen Auth ----------------
@app.route("/api/citizen/register", methods=["POST"])
@handle_errors
def citizen_register():
    data = request.json or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    phone = data.get("phone", "").strip()
    age = data.get("age", "")
    interests = data.get("interests", "").strip()
    job = data.get("job", "").strip()
    education = data.get("education", "").strip()

    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400
    if users_col.find_one({"email": email, "sample_data": {"$ne": True}}):
        return jsonify({"error": "An account with this email already exists."}), 409
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    res = users_col.insert_one({
        "email": email,
        "password": hashed,
        "profile": {"basic": {"name": name, "age": age, "phone": phone}},
        "extended_profile": {"interests": interests, "employment": {"job": job, "education": education}},
        "created": datetime.now(timezone.utc),
        "sample_data": False,
        "role": "citizen",
        "active": True,
    })
    citizen_logs_col.insert_one({
        "user_id": str(res.inserted_id),
        "email": email,
        "name": name,
        "event": "register",
        "ip": request.remote_addr,
        "timestamp": datetime.now(timezone.utc)
    })
    logger.info(f"New citizen registered: {email}")
    return jsonify({"status": "ok", "message": "Account created successfully."}), 201

@app.route("/api/citizen/login", methods=["POST"])
@handle_errors
def citizen_login():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400
    user = users_col.find_one({"email": email, "sample_data": {"$ne": True}})
    if not user:
        return jsonify({"error": "No account found with this email."}), 401
    stored_pwd = user.get("password")
    if isinstance(stored_pwd, bytes):
        ok = bcrypt.checkpw(password.encode("utf-8"), stored_pwd)
    else:
        ok = False
    if not ok:
        citizen_logs_col.insert_one({
            "user_id": str(user["_id"]),
            "email": email,
            "name": (user.get("profile") or {}).get("basic", {}).get("name", ""),
            "event": "login_failed",
            "ip": request.remote_addr,
            "timestamp": datetime.now(timezone.utc)
        })
        return jsonify({"error": "Incorrect password."}), 401
    user_id = str(user["_id"])
    token = generate_citizen_token(user_id)
    name = (user.get("profile") or {}).get("basic", {}).get("name", email)
    citizen_logs_col.insert_one({
        "user_id": user_id,
        "email": email,
        "name": name,
        "event": "login",
        "ip": request.remote_addr,
        "timestamp": datetime.now(timezone.utc)
    })
    logger.info(f"Citizen login: {email}")
    return jsonify({"status": "ok", "token": token, "user_id": user_id, "name": name})

@app.route("/api/citizen/logout", methods=["POST"])
@citizen_required
@handle_errors
def citizen_logout():
    user = users_col.find_one({"_id": ObjectId(request.citizen_id)}, {"email": 1, "profile": 1})
    email = (user or {}).get("email", "")
    name = ((user or {}).get("profile") or {}).get("basic", {}).get("name", "")
    citizen_logs_col.insert_one({
        "user_id": request.citizen_id,
        "email": email,
        "name": name,
        "event": "logout",
        "ip": request.remote_addr,
        "timestamp": datetime.now(timezone.utc)
    })
    return jsonify({"status": "ok", "message": "Logged out."})

@app.route("/api/citizen/profile", methods=["GET"])
@citizen_required
@handle_errors
def citizen_profile():
    user = users_col.find_one({"_id": ObjectId(request.citizen_id)}, {"password": 0})
    if not user:
        return jsonify({"error": "User not found"}), 404
    user["_id"] = str(user["_id"])
    if isinstance(user.get("created"), datetime):
        user["created"] = user["created"].isoformat() + "Z"
    return jsonify(user)

@app.route("/api/citizen/profile", methods=["PUT"])
@citizen_required
@handle_errors
def citizen_update_profile():
    data = request.json or {}
    updates = {}
    if data.get("name"): updates["profile.basic.name"] = data["name"]
    if data.get("phone"): updates["profile.basic.phone"] = data["phone"]
    if data.get("age"): updates["profile.basic.age"] = data["age"]
    if data.get("job"): updates["extended_profile.employment.job"] = data["job"]
    if data.get("education"): updates["extended_profile.employment.education"] = data["education"]
    if updates:
        updates["updated"] = datetime.now(timezone.utc)
        users_col.update_one({"_id": ObjectId(request.citizen_id)}, {"$set": updates})
    return jsonify({"status": "ok", "message": "Profile updated."})

@app.route("/api/dashboard/analytics", methods=["GET"])
@admin_required
@handle_errors
def get_dashboard_analytics():
    # User Metrics
    total_users = users_col.count_documents({})
    # Engagement Metrics
    total_engagements = eng_col.count_documents({})
    # Store Metrics
    total_orders = orders_col.count_documents({})
    
    # Recent Engagements
    recent_engagements = list(eng_col.find().sort("timestamp", -1).limit(10))
    # Serialize ObjectIds and Datetimes
    for eng in recent_engagements:
        eng["_id"] = str(eng["_id"])
        if isinstance(eng.get("timestamp"), datetime):
            eng["timestamp"] = eng["timestamp"].isoformat() + "Z"
            
        if eng.get("user_id"):
            try:
                user = users_col.find_one({"_id": ObjectId(eng["user_id"])})
            except:
                user = users_col.find_one({"_id": eng["user_id"]})
            if user:
                eng["user_name"] = user.get("profile", {}).get("basic", {}).get("name") or user.get("email")
                eng["user_email"] = user.get("email")

    # Recent Users
    recent_users = list(users_col.find({"sample_data": {"$ne": True}}, {"password": 0}).sort("created", -1).limit(5))
    print(f"DEBUG: Found {len(recent_users)} recent users")
    for u in recent_users:
        u["_id"] = str(u["_id"])
        # Handle cases where created might be missing or string
        created = u.get("created")
        if isinstance(created, datetime):
            u["created"] = created.isoformat() + "Z"
        elif not created:
             u["created"] = datetime.now(timezone.utc).isoformat() + "Z"

    # Citizen login stats
    total_logins = citizen_logs_col.count_documents({"event": "login"})
    total_registered = citizen_logs_col.count_documents({"event": "register"})
    total_login_failed = citizen_logs_col.count_documents({"event": "login_failed"})

    # Recent access logs
    recent_access_logs = list(citizen_logs_col.find().sort("timestamp", -1).limit(20))
    for log in recent_access_logs:
        log["_id"] = str(log["_id"])
        if isinstance(log.get("timestamp"), datetime):
            log["timestamp"] = log["timestamp"].isoformat() + "Z"

    return jsonify({
        "user_metrics": {
            "total_users": total_users,
            "total_registered": total_registered,
            "active_now": 0
        },
        "engagement_metrics": {
            "total_engagements": total_engagements
        },
        "store_metrics": {
            "total_orders": total_orders
        },
        "citizen_access_metrics": {
            "total_logins": total_logins,
            "total_registered": total_registered,
            "total_login_failed": total_login_failed,
        },
        "recent_engagements": recent_engagements,
        "recent_users": recent_users,
        "recent_access_logs": recent_access_logs,
    })

# ---------------- Public API Routes ----------------
@app.route("/api/categories", methods=["GET"])
@handle_errors
def get_categories():
    cats = list(categories_col.find({}, {"_id": 0}))
    # Deduplicate by id
    seen = set()
    unique_cats = []
    for c in cats:
        cid = c.get('id')
        if cid and cid not in seen:
            seen.add(cid)
            unique_cats.append(c)
    return jsonify(unique_cats)

@app.route("/api/services", methods=["GET"])
@handle_errors
def get_services():
    return jsonify(list(services_col.find({}, {"_id": 0})))

@app.route("/api/service/<service_id>", methods=["GET"])
@handle_errors
def get_service(service_id):
    service = services_col.find_one({"id": service_id}, {"_id": 0})
    if not service:
        return jsonify({"error": "Service not found"}), 404
    return jsonify(service)

@app.route("/api/admin/ads/seed", methods=["POST"])
def seed_ads():
    new_ads = [
        {"id": "ad_al_university", "title": "University Admissions for A/L Students", "content": "Applications for the upcoming university intake are now open for all A/L students. Apply online.", "target_segments": ["al", "student", "a/l", "education", "school"], "active": True, "link": "https://ugc.ac.lk/"},
        {"id": "ad_al_zscore", "title": "A/L Z-Score Released", "content": "The A/L Z-scores for 2023 have been released. Check your eligibility for university courses.", "target_segments": ["al", "student", "a/l", "university", "school"], "active": True, "link": "https://doenets.lk/"},
        {"id": "ad_business_tax", "title": "SME Tax Exemptions", "content": "Small and Medium Enterprises can now apply for the new digital tax exemption scheme.", "target_segments": ["business", "sme", "entrepreneur", "career", "professional"], "active": True, "link": "http://www.ird.gov.lk/"},
        {"id": "ad_senior_pension", "title": "Digital Pension Registration", "content": "Retirees can now register their pension details fully online via the Citizen Portal.", "target_segments": ["senior", "retiree", "pension", "elderly"], "active": True, "link": "https://www.pensions.gov.lk/"},
        {"id": "ad_housing_loans", "title": "Government Housing Loans", "content": "Low-interest housing loans available for first-time home buyers. Check your eligibility today.", "target_segments": ["housing", "family", "married", "professional"], "active": True, "link": "https://www.smib.lk/"}
    ]
    for ad in new_ads:
        ads_col.update_one({"id": ad["id"]}, {"$set": ad}, upsert=True)
    return jsonify({"status": "seeded"})

@app.route("/api/ads", methods=["GET"])
@handle_errors
def get_ads():
    ads = list(ads_col.find({}, {"_id": 0}))
    
    user_id = request.args.get("user_id")
    if user_id:
        try:
            user = users_col.find_one({"_id": ObjectId(user_id)})
        except:
            user = users_col.find_one({"_id": user_id})
            
        if user:
            # Build user profile string
            keywords = []
            ext_prof = user.get("extended_profile", {})
            job = ext_prof.get("employment", {}).get("job", "")
            education = ext_prof.get("employment", {}).get("education", "")
            interests = ext_prof.get("interests", "")
            if job: keywords.extend(job.lower().split())
            if education: keywords.extend(education.lower().split())
            if interests: keywords.extend(interests.lower().replace(",", " ").split())
            
            basic_prof = user.get("profile", {}).get("basic", {})
            age = basic_prof.get("age", "")
            if age: keywords.append(str(age))
            
            user_text = " ".join([job, education, interests] + keywords).strip()
            
            if user_text:
                try:
                    # Using Gemini API for embeddings
                    user_emb = get_embeddings([user_text])
                    
                    if user_emb is not None:
                        ad_texts = []
                        for a in ads:
                            a_text = f"{a.get('title', '')} {a.get('content', '')} {' '.join(a.get('target_segments', []))}"
                            ad_texts.append(a_text)
                            
                        ad_embs = get_embeddings(ad_texts)
                        if ad_embs is not None:
                            # Using custom cosine_sim
                            sims = cosine_sim(user_emb, ad_embs)[0]
                            
                            for i, a in enumerate(ads):
                                a["relevance_score"] = float(sims[i]) * 100
                                
                            ads.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
                except Exception as e:
                    logger.error(f"Error in ad recommendation: {e}")
                    
    return jsonify(ads)

@app.route("/api/store/products", methods=["GET"])
@handle_errors
def get_products():
    query = {}
    category = request.args.get("category")
    if category:
        query["category"] = category
    products = list(products_col.find(query, {"_id": 0}))
    
    # Recommendation algorithm based on user engagements and profile
    user_id = request.args.get("user_id")
    if user_id:
        keywords = []
        
        # 1. From Engagements
        user_engs = list(eng_col.find({"user_id": user_id}))
        if user_engs:
            for eng in user_engs:
                if eng.get("query"): keywords.extend(eng["query"].lower().split())
                if eng.get("service"): keywords.append(eng["service"].lower())
                if eng.get("question_clicked"): keywords.extend(eng["question_clicked"].lower().split())
                if eng.get("desires"): keywords.extend([d.lower() for d in eng["desires"]])
                
        # 2. From User Profile
        try:
            user = users_col.find_one({"_id": ObjectId(user_id)})
        except:
            user = users_col.find_one({"_id": user_id})
            
        if user:
            # Extended profile
            ext_prof = user.get("extended_profile", {})
            job = ext_prof.get("employment", {}).get("job", "")
            education = ext_prof.get("employment", {}).get("education", "")
            interests = ext_prof.get("interests", "")
            if job: keywords.extend(job.lower().split())
            if education: keywords.extend(education.lower().split())
            if interests: keywords.extend(interests.lower().replace(",", " ").split())
            
            # Basic profile
            basic_prof = user.get("profile", {}).get("basic", {})
            age = basic_prof.get("age", "")
            if age: keywords.append(str(age))
            
            keywords = [kw for kw in keywords if len(kw) > 3]
            
            # Advanced Recommendation Engine using NLP Embeddings
            user_text = " ".join([job, education, interests] + keywords).strip()
            
            if user_text:
                try:
                    # Using Gemini API for embeddings
                    user_emb = get_embeddings([user_text])
                    
                    if user_emb is not None:
                        prod_texts = []
                        for p in products:
                            p_text = f"{p.get('name', '')} {p.get('description', '')} {p.get('category', '')} {' '.join(p.get('tags', []))} {' '.join(p.get('target_segments', []))}"
                            prod_texts.append(p_text)
                            
                        prod_embs = get_embeddings(prod_texts)
                        if prod_embs is not None:
                            # Using custom cosine_sim
                            sims = cosine_sim(user_emb, prod_embs)[0]
                            
                            for i, p in enumerate(products):
                                p["recommendation_score"] = float(sims[i]) * 100
                                
                            products.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
                except Exception as e:
                    logger.error(f"Error in advanced recommendation algorithm: {e}")
                    # Fallback to basic keyword matching
                    for p in products:
                        score = 0
                        p_text = f"{p.get('name', '')} {p.get('description', '')} {p.get('category', '')}".lower()
                        for kw in keywords:
                            if kw in p_text:
                                score += 1
                        p["recommendation_score"] = score
                    
                    products.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)
                
    return jsonify(products)

@app.route("/api/store/categories", methods=["GET"])
@handle_errors
def get_store_categories():
    # Get unique categories from products collection
    categories = products_col.distinct("category")
    return jsonify({"categories": categories})

@app.route("/api/store/order", methods=["POST"])
@citizen_required
@handle_errors
def create_order():
    data = request.json or {}
    if not data.get("items"):
        return jsonify({"error": "No items in order"}), 400

    order = {
        "order_id": f"ORD-{int(datetime.now(timezone.utc).timestamp())}",
        "user_id": data.get("user_id"),
        "items": data.get("items"),
        "amount": data.get("total", 0),
        "customer": data.get("customer", {}),
        "status": "pending",
        "created": datetime.now(timezone.utc)
    }
    orders_col.insert_one(order)
    return jsonify({"status": "ok", "message": "Order placed successfully", "order_id": order["order_id"]})

# ---------------- Search & AI ----------------
@app.route("/api/search/autosuggest", methods=["GET"])
@handle_errors
def autosuggest():
    q = request.args.get("q", "").lower()
    if not q or len(q) < 2:
        return jsonify([])
    escaped_q = re.escape(q)
    results = []
    services = services_col.find({
        "$or": [
            {"name.en": {"$regex": escaped_q, "$options": "i"}},
            {"subservices.name.en": {"$regex": escaped_q, "$options": "i"}}
        ]
    }).limit(5)
    for s in services:
        s_name = s.get("name", {}).get("en", "")
        if q in s_name.lower():
            results.append({"id": s.get("id"), "name": s_name, "type": "service"})
        for sub in s.get("subservices", []):
            sub_name = sub.get("name", {}).get("en", "")
            if q in sub_name.lower():
                results.append({"id": s.get("id"), "sub_id": sub.get("id"), "name": sub_name, "type": "subservice"})
    return jsonify(results[:5])

@app.route("/api/admin/build_index", methods=["POST"])
@admin_required
@handle_errors
def build_index():
    if os.getenv("VERCEL"):
        return jsonify({"error": "Indexing is disabled on Vercel's read-only filesystem. Please build locally and commit the data/ directory."}), 400
    count = rebuild_search_index()
    return jsonify({"status": "ok", "count": count, "faiss": FAISS_AVAILABLE})

def rebuild_search_index():
    # No local model needed
    docs = []
    services = list(services_col.find())
    for s in services:
        s_name = s.get("name", {}).get("en", "")
        for sub in s.get("subservices", []):
            sub_name = sub.get("name", {}).get("en", "")
            for q in sub.get("questions", []):
                q_text = q.get("q", {}).get("en", "")
                ans_text = q.get("answer", {}).get("en", "")
                text = f"{s_name} {sub_name} {q_text} {ans_text}"
                docs.append({"text": text, "metadata": {"service_id": s.get("id"), "sub_id": sub.get("id"), "question": q_text, "answer": ans_text}})
    if not docs:
        raise ValueError("No data to index")
    texts = [d["text"] for d in docs]
    embeddings = get_embeddings(texts)
    if embeddings is None:
        raise ValueError("Failed to generate embeddings")
    
    with open(META_PATH, "w") as f:
        json.dump(docs, f)
    
    np.save("data/embeddings.npy", embeddings)
    return len(docs)

@app.route("/api/ai/search", methods=["POST"])
@citizen_required
@handle_errors
def ai_search():
    data = request.json or {}
    query = data.get("query", "")
    top_k = data.get("top_k", 3)
    if not query:
        return jsonify({"error": "Query required"}), 400

    # ── Primary path: vector-similarity search (needs built index) ──
    if os.path.exists(META_PATH):
        try:
            with open(META_PATH, "r") as f:
                docs = json.load(f)
            
            q_embed = get_embeddings([query])
            if q_embed is None:
                raise ValueError("AI Search unavailable")
                
            hits = []
            if os.path.exists("data/embeddings.npy"):
                embeddings = np.load("data/embeddings.npy")
                
                # Check for dimension mismatch (e.g., switching from 384 to 768)
                if q_embed.shape[-1] == embeddings.shape[-1]:
                    # Calculate similarities
                    sims = cosine_sim(q_embed, embeddings)[0]
                    top_indices = sims.argsort()[-top_k:][::-1]
                    for idx in top_indices:
                        hits.append(docs[idx]["metadata"])
                else:
                    logger.warning(f"Embedding dimension mismatch: {q_embed.shape[-1]} vs {embeddings.shape[-1]}. Rebuild index.")
            if hits:
                best = hits[0]
                return jsonify({
                    "answer": best.get("answer", ""),
                    "downloads": best.get("downloads", []),
                    "location": best.get("location", ""),
                    "instructions": best.get("instructions", ""),
                })
        except Exception as e:
            logger.warning(f"Vector search failed, falling back to keyword search: {e}")

    # ── Fallback path: keyword search directly in MongoDB ──
    keywords = [w for w in re.split(r'\s+', query.strip()) if len(w) >= 2]
    if not keywords:
        return jsonify({"answer": "Please provide more details in your question.", "sources": []})

    # Build a regex that matches any keyword
    pattern = '|'.join(re.escape(k) for k in keywords)
    mongo_filter = {
        "$or": [
            {"subservices.questions.q.en": {"$regex": pattern, "$options": "i"}},
            {"subservices.questions.answer.en": {"$regex": pattern, "$options": "i"}},
            {"subservices.name.en": {"$regex": pattern, "$options": "i"}},
            {"name.en": {"$regex": pattern, "$options": "i"}},
        ]
    }
    services_cursor = services_col.find(mongo_filter).limit(5)

    hits = []
    for svc in services_cursor:
        svc_name = (svc.get("name") or {}).get("en", "")
        for sub in svc.get("subservices", []):
            sub_name = (sub.get("name") or {}).get("en", "")
            for q in sub.get("questions", []):
                q_text = (q.get("q") or {}).get("en", "")
                ans_text = (q.get("answer") or {}).get("en", "")
                combined = f"{svc_name} {sub_name} {q_text} {ans_text}".lower()
                score = sum(1 for k in keywords if k.lower() in combined)
                if score > 0:
                    hits.append({
                        "score": score,
                        "question": q_text,
                        "answer": ans_text,
                        "service_id": svc.get("id", ""),
                        "title": f"{svc_name} – {sub_name}",
                        "downloads": q.get("downloads", []),
                        "location": q.get("location", ""),
                        "instructions": q.get("instructions", ""),
                    })

    if not hits:
        return jsonify({
            "answer": "I couldn't find specific information about your question. Please try rephrasing or browse the categories on the left.",
            "downloads": [], "location": "", "instructions": ""
        })

    hits.sort(key=lambda x: x["score"], reverse=True)
    best = hits[0]
    return jsonify({
        "answer": best["answer"] or "Please visit the relevant government office for more details.",
        "downloads": best.get("downloads", []),
        "location": best.get("location", ""),
        "instructions": best.get("instructions", ""),
    })

# ---------------- Recommendation Engine ----------------
class RecommendationEngine:
    def __init__(self, db):
        self.db = db
        self.users_col = db["users"]
        self.eng_col = db["engagements"]
        self.ads_col = db["ads"]

    def get_user_segment(self, user_id):
        try:
            user = self.users_col.find_one({"_id": ObjectId(user_id)})
        except Exception:
            user = self.users_col.find_one({"_id": user_id})
        if not user:
            return ["unknown"]
        profile = user.get('extended_profile', {})
        segments = []
        # Age, education, children, career-based segments
        try:
            age = int(profile.get('family', {}).get('age') or 0)
        except Exception:
            age = None
        education = profile.get('education', {}).get('highest_qualification', 'unknown')
        children = profile.get('family', {}).get('children', [])
        job = profile.get('career', {}).get('current_job', '').lower()
        if age is not None:
            if age < 25: segments.append("young_adult")
            elif age <= 35: segments.append("early_career")
            elif age <= 45: segments.append("mid_career_family")
            elif age <= 60: segments.append("established_professional")
            else: segments.append("senior")
        if education in ['none', 'school', 'ol']: segments.append("needs_qualification")
        elif education in ['al', 'diploma']: segments.append("mid_education")
        elif education in ['degree', 'masters', 'phd']: segments.append("highly_educated")
        if children: segments.append("parent")
        if 'government' in job: segments.append("government_employee")
        if any(w in job for w in ['manager', 'director', 'head']): segments.append("management")
        return list(set(segments))

    def get_personalized_ads(self, user_id, limit=5):
        segments = self.get_user_segment(user_id)
        user_engs = list(self.eng_col.find({"user_id": user_id}))
        interests = []
        for eng in user_engs:
            interests.extend(eng.get('desires', []))
            if eng.get('question_clicked'): interests.append(eng['question_clicked'])
            if eng.get('service'): interests.append(eng['service'])
        ads = list(self.ads_col.find({"active": True}))
        scored = []
        for ad in ads:
            score = len(set(segments) & set(ad.get('target_segments', []))) * 10
            score += len(set(interests) & set(ad.get('tags', []))) * 5
            created = ad.get('created')
            if created:
                days_old = (datetime.now(timezone.utc) - created).days
                score += 5 if days_old < 7 else 2 if days_old < 30 else 0
            scored.append((ad, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [ad for ad, _ in scored[:limit]]

    def generate_education_recommendations(self, user_id):
        try:
            user = self.users_col.find_one({"_id": ObjectId(user_id)})
        except Exception:
            user = self.users_col.find_one({"_id": user_id})
        if not user: return []
        profile = user.get('extended_profile', {})
        recs = []
        # Children education recommendations
        children_ages = profile.get('family', {}).get('children_ages', [])
        children_education = profile.get('family', {}).get('children_education', [])
        for i, c_age in enumerate(children_ages):
            child_edu = (children_education[i] if i < len(children_education) else "") or ""
            child_edu_l = child_edu.lower()
            if 14 <= c_age <= 16 and 'ol' not in child_edu_l:
                recs.append({"type": "child_education", "title": "O/L Exam Preparation Support", "message": "Special tuition for O/L exams", "priority": "medium", "tags": ["ol_exams"]})
            if 17 <= c_age <= 20 and 'al' not in child_edu_l:
                recs.append({"type": "child_education", "title": "A/L Stream Guidance", "message": "Expert guidance for A/L selection", "priority": "medium", "tags": ["al_exams"]})
        return recs

recommendation_engine = RecommendationEngine(db)

@app.route("/api/recommendations/<user_id>", methods=["GET"])
@citizen_required
@handle_errors
def get_recommendations(user_id):
    return jsonify({
        "ads": recommendation_engine.get_personalized_ads(user_id),
        "education_recommendations": recommendation_engine.generate_education_recommendations(user_id),
        "user_segment": recommendation_engine.get_user_segment(user_id)
    })

# ---------------- GDPR / Consent ----------------
@app.route("/api/consent/update", methods=["POST"])
@citizen_required
@handle_errors
def update_consent():
    payload = request.json or {}
    user_id = payload.get("user_id")
    if not user_id: return jsonify({"error": "user_id required"}), 400
    updates = {
        "extended_profile.consent.marketing_emails": payload.get("marketing_emails", False),
        "extended_profile.consent.personalized_ads": payload.get("personalized_ads", False),
        "extended_profile.consent.data_analytics": payload.get("data_analytics", False),
        "extended_profile.consent.updated": datetime.now(timezone.utc)
    }
    users_col.update_one({"_id": ObjectId(user_id)}, {"$set": updates})
    return jsonify({"status": "ok", "message": "Consent updated"})

@app.route("/api/data/export/<user_id>", methods=["GET"])
@citizen_required
@handle_errors
def export_user_data(user_id):
    try: user = users_col.find_one({"_id": ObjectId(user_id)})
    except Exception: user = users_col.find_one({"_id": user_id})
    if not user: return jsonify({"error": "User not found"}), 404
    export_data = {"profile": user.get("profile", {}), "extended_profile": user.get("extended_profile", {}), "consent_preferences": user.get("extended_profile", {}).get("consent", {})}
    return jsonify(export_data)

@app.route("/api/data/delete/<user_id>", methods=["DELETE"])
@citizen_required
@handle_errors
def delete_user_data(user_id):
    try: res = users_col.delete_one({"_id": ObjectId(user_id)})
    except Exception: res = users_col.delete_one({"_id": user_id})
    try: eng_col.update_many({"user_id": user_id}, {"$set": {"user_id": None, "anonymized": True}})
    except Exception: pass
    try: 
        orders_col.update_many({"user_id": user_id}, {"$set": {"user_id": None, "anonymized": True}})
        payments_col.update_many({"user_id": user_id}, {"$set": {"user_id": None, "anonymized": True}})
    except Exception: pass
    if getattr(res, "deleted_count", 0) > 0:
        return jsonify({"status": "ok", "message": "User data deleted/anonymized"})
    else:
        return jsonify({"error": "User not found"}), 404

# ---------------- Features: Engagement, Profile, Payment ----------------

@app.route("/api/engagement", methods=["POST"])
@app.route("/api/engagement/enhanced", methods=["POST"])
@citizen_required
@handle_errors
def log_engagement():
    data = request.json or {}
    data["timestamp"] = datetime.now(timezone.utc)
    
    user_id = data.get("user_id") or getattr(request, "citizen_id", None)
    if user_id:
        data["user_id"] = user_id
        try:
            user = users_col.find_one({"_id": ObjectId(user_id)})
        except:
            user = users_col.find_one({"_id": user_id})
            
        if user:
            data["user_name"] = user.get("profile", {}).get("basic", {}).get("name") or user.get("email")
            data["user_email"] = user.get("email")
            data["user_details"] = user.get("extended_profile", {})
        else:
            data["anonymous"] = True
    else:
        data["user_id"] = None
        data["anonymous"] = True
    
    eng_col.insert_one(data)
    return jsonify({"status": "ok", "message": "Engagement logged"})

@app.route("/api/profile/step", methods=["POST"])
@citizen_required
@handle_errors
def profile_step():
    data = request.json or {}
    step = data.get("step")
    profile_data = data.get("data", {})
    email = data.get("email")
    profile_id = data.get("profile_id")
    
    if not step:
        return jsonify({"error": "Step required"}), 400

    if step == "basic":
        if not email:
            return jsonify({"error": "Email required for basic profile"}), 400
        
        # Check if user exists
        existing = users_col.find_one({"email": email})
        if existing:
            # Update existing
            user_id = existing["_id"]
            users_col.update_one({"_id": user_id}, {"$set": {"profile.basic": profile_data, "updated": datetime.now(timezone.utc)}})
        else:
            # Create new
            res = users_col.insert_one({
                "email": email,
                "profile": {"basic": profile_data},
                "created": datetime.now(timezone.utc),
                "sample_data": False
            })
            user_id = res.inserted_id
            print(f"DEBUG: Inserted new user {user_id} with email {email}")
            
        return jsonify({"status": "ok", "profile_id": str(user_id), "step": "basic"})

    elif step in ["contact", "employment", "family_interests"]:
        if not profile_id:
            return jsonify({"error": "Profile ID required"}), 400
        
        try:
            oid = ObjectId(profile_id)
        except:
            return jsonify({"error": "Invalid Profile ID"}), 400
            
        users_col.update_one({"_id": oid}, {"$set": {f"extended_profile.{step}": profile_data, "updated": datetime.now(timezone.utc)}})
        return jsonify({"status": "ok", "step": step})

    return jsonify({"error": "Invalid step"}), 400


@app.route("/api/store/payment", methods=["POST"])
@citizen_required
@handle_errors
def process_payment():
    data = request.json or {}
    order_id = data.get("order_id")
    amount = data.get("amount")
    
    if not order_id:
        return jsonify({"error": "Order ID required"}), 400
        
    # Simulate payment processing
    payment_record = {
        "order_id": order_id,
        "amount": amount,
        "user_id": data.get("user_id"),
        "method": data.get("method", "card"),
        "status": "completed",
        "transaction_id": data.get("transaction_id", f"TXN-{int(datetime.now(timezone.utc).timestamp())}"),
        "timestamp": datetime.now(timezone.utc)
    }
    
    payments_col.insert_one(payment_record)
    
    # Update order status
    orders_col.update_one({"order_id": order_id}, {"$set": {"status": "paid", "payment_id": payment_record["transaction_id"]}})
    
    return jsonify({"status": "ok", "message": "Payment successful", "transaction_id": payment_record["transaction_id"]})

# ---------------- Init default admin ----------------
def init_admin_user():
    if admins_col.count_documents({}) == 0:
        pwd = os.getenv("ADMIN_PWD", "admin123")
        hashed = bcrypt.hashpw(pwd.encode("utf-8"), bcrypt.gensalt())
        admins_col.insert_one({"username": "admin", "email": os.getenv("ADMIN_EMAIL", "admin@example.com"), "password": hashed, "created": datetime.now(timezone.utc)})
        logger.info("Default admin created")
    # Ensure indexes
    try:
        citizen_logs_col.create_index([("timestamp", -1)])
        citizen_logs_col.create_index("event")
        citizen_logs_col.create_index("user_id")
        users_col.create_index([("email", 1)], unique=False, sparse=True)
    except Exception:
        pass

# ---------------- Run App ----------------
if __name__ == "__main__":
    init_admin_user()
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "True") == "True"
    logger.info(f"Starting server at {host}:{port}")
    app.run(debug=debug, host=host, port=port)
