import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, ads_col, users_col, seed_ads

# mock a student and a doctor
student_id = users_col.insert_one({
    "email": "student@gmail.com",
    "extended_profile": {"employment": {"job": "student", "education": "A/L"}}
}).inserted_id

doctor_id = users_col.insert_one({
    "email": "doctor@gmail.com",
    "extended_profile": {"employment": {"job": "doctor"}}
}).inserted_id

with app.test_client() as client:
    # First seed the ads
    client.post("/api/admin/ads/seed")
    
    # Check student
    print("\n--- Student Ads ---")
    resp_student = client.get(f"/api/ads?user_id={student_id}")
    for ad in resp_student.json:
        print(f"[{ad.get('relevance_score', 0):.1f}] {ad['title']} (Segments: {ad['target_segments']})")
        
    # Check doctor
    print("\n--- Doctor Ads ---")
    resp_doctor = client.get(f"/api/ads?user_id={doctor_id}")
    for ad in resp_doctor.json:
        print(f"[{ad.get('relevance_score', 0):.1f}] {ad['title']} (Segments: {ad['target_segments']})")

