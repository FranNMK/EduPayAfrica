"""
Firebase Authentication Service
Handles authentication with Firebase and synchronizes users with Django.
"""

import json
import os
from typing import Optional

import firebase_admin
from django.contrib.auth import get_user_model
from firebase_admin import auth, credentials

User = get_user_model()

# Initialize Firebase Admin SDK
FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH', '')
FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID', '')


def initialize_firebase():
    """Initialize Firebase Admin SDK from credentials with explicit project ID."""
    if firebase_admin._apps:
        return firebase_admin.get_app()

    project_id = (
        FIREBASE_PROJECT_ID
        or os.environ.get('GOOGLE_CLOUD_PROJECT')
        or os.environ.get('GCLOUD_PROJECT')
    )

    options = {'projectId': project_id} if project_id else None

    if FIREBASE_CREDENTIALS_PATH and os.path.exists(FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        return firebase_admin.initialize_app(cred, options)

    # Fallback to Application Default Credentials if available
    try:
        cred = credentials.ApplicationDefault()
        return firebase_admin.initialize_app(cred, options)
    except Exception as e:
        raise ValueError(
            "Firebase credentials not configured. Set FIREBASE_CREDENTIALS_PATH to your service account JSON."
        ) from e


def verify_firebase_token(id_token: str) -> Optional[dict]:
    """
    Verify a Firebase ID token and return the decoded claims.

    Args:
        id_token: Firebase ID token from client

    Returns:
        Decoded token claims or None if invalid
    """
    try:
        initialize_firebase()
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None


def authenticate_firebase_user(email: str, password: str) -> Optional[str]:
    """
    Authenticate user with Firebase REST API using email and password.
    Returns an ID token if successful.

    Args:
        email: User email
        password: User password

    Returns:
        Firebase ID token or None if authentication fails
    """
    try:
        # Note: This uses the REST API because firebase-admin SDK doesn't support
        # email/password authentication directly. In production, use Firebase JS SDK on client.
        import requests

        api_key = os.environ.get('FIREBASE_API_KEY', '')
        if not api_key:
            raise ValueError("FIREBASE_API_KEY not configured")

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {"email": email, "password": password, "returnSecureToken": True}

        response = requests.post(url, json=payload)
        data = response.json()

        if response.status_code == 200:
            return data.get('idToken')
        else:
            error_message = data.get('error', {}).get('message', 'Authentication failed')
            print(f"Firebase auth error: {error_message}")
            return None
    except Exception as e:
        print(f"Firebase authentication error: {e}")
        return None


def get_or_create_django_user(firebase_user: dict) -> Optional[User]:
    """
    Create or update a Django user from Firebase user data.

    Args:
        firebase_user: Decoded Firebase ID token claims

    Returns:
        Django User object or None if creation fails
    """
    try:
        email = firebase_user.get('email', '')
        uid = firebase_user.get('uid', '')

        if not email or not uid:
            return None

        # Get or create Django user
        user, created = User.objects.get_or_create(
            username=email,
            defaults={'email': email, 'first_name': firebase_user.get('name', '').split()[0] if firebase_user.get('name') else ''},
        )

        # Update user info if they already existed
        if not created:
            user.email = email
            user.save()

        return user
    except Exception as e:
        print(f"Error creating/updating Django user: {e}")
        return None


def firebase_login(request, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user via Firebase and sync with Django.
    Also handles permission setup for super admins.

    Args:
        request: Django request object
        email: User email
        password: User password

    Returns:
        Django User object if successful, None otherwise
    """
    try:
        # Authenticate with Firebase
        id_token = authenticate_firebase_user(email, password)
        if not id_token:
            return None

        # Verify token
        decoded_token = verify_firebase_token(id_token)
        if not decoded_token:
            return None

        # Get or create Django user
        user = get_or_create_django_user(decoded_token)
        if not user:
            return None

        # If this is the super admin email, ensure is_staff and is_superuser are set
        if email == os.environ.get('SUPER_ADMIN_EMAIL', 'frankmk2025@gmail.com'):
            user.is_staff = True
            user.is_superuser = True
            user.save()

        return user
    except Exception as e:
        print(f"Firebase login error: {e}")
        return None


def create_firebase_user(email: str, password: str, display_name: str = "") -> Optional[dict]:
    """
    Create a new user in Firebase.

    Args:
        email: User email
        password: User password (min 6 chars)
        display_name: Optional display name

    Returns:
        Firebase user data with uid if successful, None otherwise
    """
    try:
        initialize_firebase()
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            email_verified=False
        )
        return {
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name or '',
        }
    except Exception as e:
        print(f"Error creating Firebase user: {e}")
        return None


def send_password_reset_email(email: str) -> bool:
    """
    Send a password reset email to the user.

    Args:
        email: User email

    Returns:
        True if successful, False otherwise
    """
    try:
        initialize_firebase()
        link = auth.generate_password_reset_link(email)
        # In production, you would send this link via email
        # For now, just return success
        print(f"Password reset link for {email}: {link}")
        return True
    except Exception as e:
        print(f"Error generating password reset link: {e}")
        return False
