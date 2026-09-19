"""Integration test script for A.R.I.A. Real Authentication and Multi-Business Data Isolation.

Tests Requirements #22 & #23 against the live backend database.
"""
import sys
import uuid
import requests

BASE_URL = "http://localhost:8000/api"

def run_tests():
    print("=" * 60)
    print("STARTING A.R.I.A. REAL AUTH & DATA ISOLATION INTEGRATION TESTS")
    print("=" * 60)

    # 1. Sign Up Test User A
    user_a_phone = "9999999999"
    user_a_pass = "TestPassword123"
    user_a_name = "Test User"

    print("\n[1] Registering User A (Test User)...")
    reg_resp = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "name": user_a_name,
            "phone": user_a_phone,
            "password": user_a_pass,
            "confirm_password": user_a_pass,
        }
    )
    if reg_resp.status_code not in (200, 201):
        # If user already registered, proceed to login
        print(f"Register status: {reg_resp.status_code}, assuming user exists.")
    else:
        reg_data = reg_resp.json()
        print(f"User A registered successfully: id={reg_data['user']['id']}, name={reg_data['user']['name']}")

    # 2. Login User A
    print("\n[2] Logging in User A...")
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"phone": user_a_phone, "password": user_a_pass}
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    user_a_data = login_resp.json()
    user_a = user_a_data["user"]
    user_a_id = user_a["id"]
    print(f"User A Logged in: {user_a['name']} ({user_a['phone']})")

    # 3. Create Business 1 for User A: Test General Store
    print("\n[3] Creating Business 1 (Test General Store) for User A...")
    b1_resp = requests.post(
        f"{BASE_URL}/auth/user/{user_a_id}/businesses",
        json={
            "user_id": user_a_id,
            "business_name": "Test General Store",
            "business_type": "general_store",
            "seed_catalogue": False, # empty start for verification
        }
    )
    assert b1_resp.status_code in (200, 201), f"Create Business 1 failed: {b1_resp.text}"
    b1_data = b1_resp.json()
    b1_id = b1_data["id"]
    print(f"Business 1 Created: id={b1_id}, name={b1_data['business_name']}")

    # 4. Add Inventory Item to Test General Store: Coke, 5 cartons
    print("\n[4] Adding 'Coke' (5 cartons) to Test General Store...")
    prod_resp = requests.post(
        f"{BASE_URL}/products?business_id={b1_id}",
        headers={"X-User-Id": user_a_id},
        json={
            "name": "Coke",
            "category": "beverages",
            "base_unit": "cartons",
            "initial_quantity": 5,
            "price": 500,
        }
    )
    assert prod_resp.status_code in (200, 201), f"Create product failed: {prod_resp.text}"
    print("Product 'Coke' (5 cartons) added successfully to Test General Store.")

    # 5. Verify Inventory in Test General Store
    inv_resp = requests.get(
        f"{BASE_URL}/inventory?business_id={b1_id}",
        headers={"X-User-Id": user_a_id}
    )
    assert inv_resp.status_code == 200, f"Get inventory failed: {inv_resp.text}"
    items = inv_resp.json()
    assert len(items) == 1 and items[0]["name"] == "Coke", f"Unexpected items: {items}"
    print(f"Verified Test General Store inventory: {[i['name'] for i in items]} (Qty: {items[0]['current_quantity']})")

    # 6. Create Business 2 for User A: Test Bakery
    print("\n[5] Creating Business 2 (Test Bakery) for User A...")
    b2_resp = requests.post(
        f"{BASE_URL}/auth/user/{user_a_id}/businesses",
        json={
            "user_id": user_a_id,
            "business_name": "Test Bakery",
            "business_type": "bakery",
            "seed_catalogue": False,
        }
    )
    assert b2_resp.status_code in (200, 201), f"Create Business 2 failed: {b2_resp.text}"
    b2_data = b2_resp.json()
    b2_id = b2_data["id"]
    print(f"Business 2 Created: id={b2_id}, name={b2_data['business_name']}")

    # 7. Data Isolation Check: Test Bakery should have 0 items (no Coke!)
    inv2_resp = requests.get(
        f"{BASE_URL}/inventory?business_id={b2_id}",
        headers={"X-User-Id": user_a_id}
    )
    assert inv2_resp.status_code == 200
    items2 = inv2_resp.json()
    assert len(items2) == 0, f"Bakery should be empty, but got: {items2}"
    print("Verified Data Isolation: Test Bakery has 0 items (Coke is NOT leaked to Bakery).")

    # 8. Security Authorization Test: Register User B
    print("\n[6] Registering User B...")
    user_b_phone = "8888888888"
    user_b_pass = "UserBPassword123"
    requests.post(
        f"{BASE_URL}/auth/register",
        json={"name": "User B", "phone": user_b_phone, "password": user_b_pass, "confirm_password": user_b_pass}
    )
    login_b = requests.post(
        f"{BASE_URL}/auth/login",
        json={"phone": user_b_phone, "password": user_b_pass}
    ).json()
    user_b_id = login_b["user"]["id"]

    # User B attempts to access User A's business (b1_id)
    print("\n[7] SECURITY TEST: User B attempts to access User A's Business (Test General Store)...")
    sec_resp = requests.get(
        f"{BASE_URL}/inventory?business_id={b1_id}",
        headers={"X-User-Id": user_b_id}
    )
    assert sec_resp.status_code in (400, 403, 422), f"Security breach! Expected 400/403/422, got {sec_resp.status_code}: {sec_resp.text}"
    print(f"SECURITY TEST PASSED! Backend blocked User B from accessing User A's business ({sec_resp.status_code}: {sec_resp.json()['error']['message']}).")


    print("\n" + "=" * 60)
    print("ALL INTEGRATION TESTS PASSED SUCCESSFULLY! (100% SUCCESS)")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
