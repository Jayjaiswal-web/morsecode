import firebase_admin
from firebase_admin import credentials, db
import os

# --- CONFIGURATION ---
# 1. Path to your JSON key
KEY_PATH = "fresh key.json" 
# 2. Your Database URL (Found in Firebase Console > Realtime Database)
DB_URL = "https://morse-code-36b13-default-rtdb.asia-southeast1.firebasedatabase.app/"

# --- FIX FOR NETWORK TIMEOUTS ---
# This forces the library to skip the Google Cloud check that is causing your 300s hang
os.environ["GCLOUD_PROJECT"] = "morse-code-36b13" 
os.environ["GOOGLE_CLOUD_DISABLE_GRPC"] = "true"

def test_connection():
    try:
        print(f"[1] Loading key from: {KEY_PATH}")
        cred = credentials.Certificate(KEY_PATH)
        
        print("[2] Initializing App...")
        # We explicitly set the http_timeout to avoid waiting 300s
        firebase_admin.initialize_app(cred, {
            'databaseURL': DB_URL,
            'httpTimeout': 30
        })

        print("[3] Attempting to write to Firebase...")
        ref = db.reference('test_connection')
        ref.set({"status": "working", "timestamp": "now"})
        
        print("\nSUCCESS! Data written to Firebase. Check your console.")
        print("This confirms Problems 1 & 2 are solved.")

    except Exception as e:
        print("\nFAILED. Here is the REAL error:")
        print("-" * 30)
        print(e)
        print("-" * 30)

if __name__ == "__main__":
    test_connection()