# auth_smartapi.py

from SmartApi import SmartConnect
import getpass
import json
from TOTP import generate_totp
API_KEY   = "AgTALyun"
CLIENT_ID = "AAAP636199"

def login():
    api = SmartConnect(api_key=API_KEY)
    
    client_code = CLIENT_ID
    pin    = "0711"
    totp        = generate_totp()  # Generate TOTP using the function from TOTP.py

    print("\n📡 Sending login request…")
    resp = api.generateSession(client_code, pin, totp)

    # Debug: full response
    print("🔍 Raw response:")
    print(json.dumps(resp, indent=4))

    if not resp.get("status"):
        raise Exception(f"❌ Login failed: {resp.get('message')}")

    session_data = resp.get("data", {})
    jwt = session_data.get("jwtToken")
    if not jwt:
        raise Exception("❌ No jwtToken in response—check the raw output above")

    # Strip leading "Bearer " if present
    if jwt.startswith("Bearer "):
        jwt = jwt.split(" ", 1)[1]

    print("✅ Login successful.")
    return api, jwt

if __name__ == "__main__":
    try:
        api, token = login()
        print("\n🔑 Session JWT Token:", token)
    except Exception as e:
        print(e)
        exit(1)
