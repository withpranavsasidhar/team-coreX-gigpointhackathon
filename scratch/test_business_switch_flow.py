"""Integration test script for A.R.I.A. Business Switching & Context Preservation.

Tests Requirement #14 (Bakery -> Kirana -> Bakery repeat business switching with real DB).
"""
import requests

BASE_URL = "http://localhost:8000/api"

def run_test():
    print("=" * 60)
    print("STARTING MULTI-BUSINESS SWITCHING INTEGRATION TEST")
    print("=" * 60)

    # 1. Register User
    phone = "9888877777"
    password = "SwitchTestPass123!"
    name = "MultiStore Trader"

    print("\n[1] Registering User...")
    reg_resp = requests.post(
        f"{BASE_URL}/auth/register",
        json={"name": name, "phone": phone, "password": password, "confirm_password": password}
    )
    if reg_resp.status_code == 201:
        user_id = reg_resp.json()["user"]["id"]
    else:
        login_resp = requests.post(f"{BASE_URL}/auth/login", json={"phone": phone, "password": password})
        user_id = login_resp.json()["user"]["id"]

    headers = {"X-User-Id": user_id}
    print(f"Authenticated User ID: {user_id}")

    # 2. Create Business A: Test Bakery
    print("\n[2] Creating Business A (Test Bakery)...")
    bakery_resp = requests.post(
        f"{BASE_URL}/auth/user/{user_id}/businesses",
        json={"user_id": user_id, "business_name": "Test Bakery", "business_type": "bakery", "seed_catalogue": False}
    )
    assert bakery_resp.status_code in (200, 201), f"Create Bakery failed: {bakery_resp.text}"
    bakery = bakery_resp.json()
    bakery_id = bakery["id"]
    print(f"Test Bakery created: {bakery_id}")

    # 3. Create Business B: Test Kirana
    print("\n[3] Creating Business B (Test Kirana)...")
    kirana_resp = requests.post(
        f"{BASE_URL}/auth/user/{user_id}/businesses",
        json={"user_id": user_id, "business_name": "Test Kirana", "business_type": "kirana", "seed_catalogue": False}
    )
    assert kirana_resp.status_code in (200, 201), f"Create Kirana failed: {kirana_resp.text}"
    kirana = kirana_resp.json()
    kirana_id = kirana["id"]
    print(f"Test Kirana created: {kirana_id}")

    # 4. Fetch Bakery via GET /businesses/{business_id} (Switch to Bakery)
    print("\n[4] Switching to Test Bakery (GET /businesses/{bakery_id})...")
    b_get = requests.get(f"{BASE_URL}/businesses/{bakery_id}", headers=headers)
    assert b_get.status_code == 200, f"GET /businesses/{bakery_id} failed with {b_get.status_code}: {b_get.text}"
    print(f"Switched to Bakery: {b_get.json()['business_name']}")

    # Verify Bakery Summary & Inventory
    sum_b = requests.get(f"{BASE_URL}/businesses/summary?business_id={bakery_id}", headers=headers)
    assert sum_b.status_code == 200
    inv_b = requests.get(f"{BASE_URL}/inventory?business_id={bakery_id}", headers=headers)
    assert inv_b.status_code == 200
    print(f"Bakery Dashboard loaded cleanly. Items count: {len(inv_b.json())}")

    # 5. Switch: Bakery -> Kirana (GET /businesses/{kirana_id})
    print("\n[5] Switching: Bakery -> Kirana (GET /businesses/{kirana_id})...")
    k_get = requests.get(f"{BASE_URL}/businesses/{kirana_id}", headers=headers)
    assert k_get.status_code == 200, f"GET /businesses/{kirana_id} failed with {k_get.status_code}: {k_get.text}"
    print(f"Switched to Kirana: {k_get.json()['business_name']}")

    # Verify Kirana Summary
    sum_k = requests.get(f"{BASE_URL}/businesses/summary?business_id={kirana_id}", headers=headers)
    assert sum_k.status_code == 200
    print(f"Kirana Dashboard loaded cleanly. Type: {sum_k.json()['business_type']}")

    # 6. Add Test Product to Kirana: "Basmati Rice 10kg"
    print("\n[6] Adding product 'Basmati Rice 10kg' to Kirana...")
    prod_resp = requests.post(
        f"{BASE_URL}/products?business_id={kirana_id}",
        headers=headers,
        json={"name": "Basmati Rice 10kg", "category": "grains", "base_unit": "bags", "initial_quantity": 10, "price": 1200}
    )
    assert prod_resp.status_code in (200, 201), f"Add product to Kirana failed: {prod_resp.text}"
    print("Product 'Basmati Rice 10kg' added to Kirana.")

    # 7. Switch: Kirana -> Bakery
    print("\n[7] Switching: Kirana -> Bakery...")
    b_get2 = requests.get(f"{BASE_URL}/businesses/{bakery_id}", headers=headers)
    assert b_get2.status_code == 200
    inv_b2 = requests.get(f"{BASE_URL}/inventory?business_id={bakery_id}", headers=headers).json()
    assert not any(p["name"] == "Basmati Rice 10kg" for p in inv_b2), "ERROR: Kirana product leaked into Bakery!"
    print("Verified: Kirana product does NOT appear in Bakery.")

    # 8. Switch: Bakery -> Kirana
    print("\n[8] Switching back: Bakery -> Kirana...")
    k_get2 = requests.get(f"{BASE_URL}/businesses/{kirana_id}", headers=headers)
    assert k_get2.status_code == 200
    inv_k2 = requests.get(f"{BASE_URL}/inventory?business_id={kirana_id}", headers=headers).json()
    assert any(p["name"] == "Basmati Rice 10kg" for p in inv_k2), "ERROR: Kirana product missing!"
    print("Verified: Kirana product 'Basmati Rice 10kg' is present in Kirana.")

    # 9. Verify User Businesses List
    print("\n[9] Verifying user businesses list...")
    ub_resp = requests.get(f"{BASE_URL}/auth/user/{user_id}/businesses", headers=headers)
    assert ub_resp.status_code == 200
    ub_list = ub_resp.json()
    assert len(ub_list) >= 2
    print(f"User owns {len(ub_list)} businesses: {[b['business_name'] for b in ub_list]}")

    print("\n" + "=" * 60)
    print("BUSINESS SWITCHING INTEGRATION TEST PASSED! (100% SUCCESS)")
    print("=" * 60)

if __name__ == "__main__":
    run_test()
