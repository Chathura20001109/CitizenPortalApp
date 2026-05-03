
import requests
import json
import random

BASE_URL = "http://127.0.0.1:5000"

def test_profile_flow():
    email = f"test_user_{random.randint(1000, 9999)}@example.com"
    print(f"Testing profile creation for {email}...")

    # Step 1: Basic
    payload1 = {
        "step": "basic",
        "email": email,
        "data": {
            "name": "Test User",
            "age": 30
        }
    }
    
    try:
        res1 = requests.post(f"{BASE_URL}/api/profile/step", json=payload1)
        print(f"Step 1 Status: {res1.status_code}")
        print(f"Step 1 Response: {res1.text}")
        
        if res1.status_code != 200:
            return False
            
        data1 = res1.json()
        profile_id = data1.get("profile_id")
        print(f"Profile ID: {profile_id}")
        
        if not profile_id:
            return False
            
        # Step 2: Contact
        payload2 = {
            "step": "contact",
            "profile_id": profile_id,
            "data": {
                "email": email,
                "phone": "0771234567"
            }
        }
        res2 = requests.post(f"{BASE_URL}/api/profile/step", json=payload2)
        print(f"Step 2 Status: {res2.status_code}")
        
        # Verify in Analytics
        res_admin = requests.get(f"{BASE_URL}/api/dashboard/analytics")
        analytics = res_admin.json()
        
        recent_users = analytics.get("recent_users", [])
        found = any(u.get("email") == email or u.get("profile", {}).get("basic", {}).get("name") == "Test User" for u in recent_users)
        
        if found:
            print("SUCCESS: User found in admin analytics.")
            return True
        else:
            print("FAILURE: User NOT found in admin analytics.")
            print("Recent Users:", json.dumps(recent_users, indent=2))
            return False

    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == "__main__":
    test_profile_flow()
