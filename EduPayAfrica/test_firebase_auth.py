"""
Quick test to check Firebase authentication
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_firebase_login(email, password):
    """Test Firebase authentication with email/password"""
    api_key = os.environ.get('FIREBASE_API_KEY', '')
    
    if not api_key:
        print("❌ FIREBASE_API_KEY not found in .env file")
        return False
    
    print(f"✅ Firebase API Key found: {api_key[:10]}...")
    print(f"🔐 Testing login for: {email}")
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        if response.status_code == 200:
            print("✅ Authentication successful!")
            print(f"   User ID: {data.get('localId')}")
            print(f"   Email: {data.get('email')}")
            print(f"   ID Token received: {data.get('idToken')[:20]}...")
            return True
        else:
            print(f"❌ Authentication failed!")
            print(f"   Status Code: {response.status_code}")
            error = data.get('error', {})
            error_message = error.get('message', 'Unknown error')
            print(f"   Error: {error_message}")
            
            # Common error messages
            if 'EMAIL_NOT_FOUND' in error_message:
                print("\n💡 This email doesn't exist in Firebase.")
                print("   Go to Firebase Console → Authentication → Users → Add User")
            elif 'INVALID_PASSWORD' in error_message:
                print("\n💡 The password is incorrect.")
            elif 'INVALID_LOGIN_CREDENTIALS' in error_message:
                print("\n💡 Email or password is incorrect.")
                print("   Check your Firebase Console to verify the user exists.")
            
            return False
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Firebase Authentication Test")
    print("=" * 60)
    print()
    
    # Get credentials
    email = input("Enter email: ").strip()
    password = input("Enter password: ").strip()
    
    print()
    test_firebase_login(email, password)
