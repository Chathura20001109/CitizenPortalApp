import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"
SESSION = requests.Session()

def print_result(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name}: {detail}")

def login_admin():
    try:
        # Default credentials from .env or app.py
        payload = {"username": "admin", "password": "admin123"}
        res = SESSION.post(f"{BASE_URL}/admin/login", json=payload)
        if res.status_code == 200 or res.url.endswith("/admin"):
            print_result("Admin Login", True)
            return True
        print_result("Admin Login", False, f"Status: {res.status_code}")
        return False
    except Exception as e:
        print_result("Admin Login", False, str(e))
        return False

def verify_analytics():
    try:
        res = SESSION.get(f"{BASE_URL}/api/dashboard/analytics")
        if res.status_code == 200:
            data = res.json()
            if "user_metrics" in data and "recent_engagements" in data and "recent_users" in data:
                e_count = len(data["recent_engagements"])
                u_count = len(data["recent_users"])
                print_result("Analytics API", True, f"Users: {data['user_metrics'].get('total_users')}, Engagements: {e_count}, New Users: {u_count}")
            else:
                print_result("Analytics API", False, "Invalid response structure (missing keys)")
        else:
            print_result("Analytics API", False, f"Status: {res.status_code}")
    except Exception as e:
        print_result("Analytics API", False, str(e))

def verify_engagement():
    try:
        payload = {
            "service": "Test Service",
            "question_clicked": "Test Question",
            "user_id": None
        }
        res = requests.post(f"{BASE_URL}/api/engagement", json=payload)
        if res.status_code == 200:
            print_result("Engagement API", True)
        else:
            print_result("Engagement API", False, f"Status: {res.status_code}")
    except Exception as e:
        print_result("Engagement API", False, str(e))

def verify_payment():
    try:
        payload = {
            "order_id": "TEST-ORDER-001",
            "amount": 1000,
            "method": "card"
        }
        # First create a dummy order to pay for (optional, but good for data integrity if DB enforces it)
        # But for now, we just test the payment endpoint directly as it upserts or updates based on logic
        # Actually app.py updates based on order_id, so we should probably insert an order first if we want strict testing, 
        # but the endpoint itself might just return 200 if logic passes.
        # Let's try to pay for a non-existent order. expected behavior depends on DB. 
        # The code uses update_one, so it won't fail if order missing, just won't update anything.
        
        res = requests.post(f"{BASE_URL}/api/store/payment", json=payload)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "ok":
                print_result("Payment API", True, f"Transaction: {data.get('transaction_id')}")
            else:
                print_result("Payment API", False, f"Response: {data}")
        else:
            print_result("Payment API", False, f"Status: {res.status_code}")
    except Exception as e:
        print_result("Payment API", False, str(e))

if __name__ == "__main__":
    print(f"Testing endpoints at {BASE_URL}...")
    try:
        # Check if server is up
        requests.get(BASE_URL)
    except:
        print("Server not accessible. Make sure it is running.")
        exit(1)

    verify_engagement()
    if login_admin():
        verify_analytics()
    verify_payment()
