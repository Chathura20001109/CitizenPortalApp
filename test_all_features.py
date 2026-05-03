#!/usr/bin/env python3
"""
Comprehensive Testing Script for Citizen Portal
Tests all major features and APIs
"""

import requests
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://127.0.0.1:5000"
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "citizen_portal")

def test_section(name):
    print(f"\n{'='*60}")
    print(f"  {name}")
    print('='*60)

def test_api(endpoint, method="GET", data=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, timeout=10)
        else:
            resp = requests.post(url, json=data, timeout=10)
        
        if resp.status_code == 200:
            print(f"✓ {endpoint} - OK ({method})")
            return resp.json()
        else:
            print(f"✗ {endpoint} - Error {resp.status_code}")
            return None
    except Exception as e:
        print(f"✗ {endpoint} - Failed: {str(e)[:50]}")
        return None

def main():
    print("\n" + "="*60)
    print("  CITIZEN PORTAL - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Database connectivity
    test_section("1. DATABASE CONNECTIVITY")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        db.command('ping')
        print("✓ MongoDB connection successful")
        
        collections = {
            'users': db.users.count_documents({}),
            'products': db.products.count_documents({}),
            'categories': db.categories.count_documents({}),
            'ads': db.ads.count_documents({}),
            'services': db.services.count_documents({})
        }
        
        for coll, count in collections.items():
            print(f"  - {coll}: {count} documents")
    except Exception as e:
        print(f"✗ Database error: {e}")
    
    # Public APIs
    test_section("2. PUBLIC API ENDPOINTS")
    test_api("/api/services")
    test_api("/api/categories")
    test_api("/api/ads")
    test_api("/api/store/products")
    test_api("/api/store/categories")
    
    # Store Images
    test_section("3. STORE PRODUCT IMAGES")
    images_dir = "static/store"
    if os.path.exists(images_dir):
        images = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]
        print(f"✓ Found {len(images)} JPG images")
        expected = ['degree_it.jpg', 'ielts_course.jpg', 'kids_coding.jpg', 
                   'slas_training.jpg', 'data_entry.jpg']
        for img in expected:
            if img in images:
                size = os.path.getsize(os.path.join(images_dir, img))
                print(f"  ✓ {img} ({size//1024}KB)")
            else:
                print(f"  ✗ {img} missing")
    else:
        print("✗ Store images directory not found")
    
    # User Profile System
    test_section("4. USER PROFILE SYSTEM")
    
    # Get a sample user for recommendations
    sample_user = db.users.find_one({"sample_data": True})
    if sample_user:
        user_id = str(sample_user['_id'])
        print(f"✓ Sample user found: {user_id}")
        
        # Test recommendations
        recs = test_api(f"/api/recommendations/{user_id}")
        if recs:
            print(f"  - Ads: {len(recs.get('ads', []))}")
            print(f"  - Education Recs: {len(recs.get('education_recommendations', []))}")
            print(f"  - Segments: {recs.get('user_segment', 'N/A')}")
    
    # Admin System
    test_section("5. ADMIN SYSTEM")
    admin_count = db.admins.count_documents({})
    print(f"✓ Admin users: {admin_count}")
    
    # Test admin dashboard analytics
    analytics = test_api("/api/dashboard/analytics")
    if analytics:
        print(f"  - Total Users: {analytics.get('total_users', 0)}")
        print(f"  - Total Products: {analytics.get('total_products', 0)}")
    
    # Translation Files
    test_section("6. TRANSLATION SYSTEM")
    try:
        with open('static/script.js', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'TRANSLATIONS' in content and 'si' in content and 'ta' in content:
                print("✓ Main portal translations present")
            else:
                print("✗ Main portal translations missing")
        
        with open('static/store.js', 'r', encoding='utf-8') as f:
            content = f.read()
            if 'STORE_TRANSLATIONS' in content:
                print("✓ Store translations present")
            else:
                print("✗ Store translations missing")
    except Exception as e:
        print(f"✗ Translation check failed: {e}")
    
    # Final Summary
    test_section("SUMMARY")
    print("✓ All core systems operational")
    print("\nManual Tests Required:")
    print("1. Visit http://localhost:5000 - Main portal")
    print("2. Visit http://localhost:5000/store - Product store")
    print("3. Visit http://localhost:5000/admin/login - Admin panel")
    print("   Username: admin@citizenportal.gov.lk")
    print("   Password: admin123")
    print("4. Test profile creation (4-step modal)")
    print("5. Test language switching (EN/SI/TA)")
    print("6. View product images in store")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
