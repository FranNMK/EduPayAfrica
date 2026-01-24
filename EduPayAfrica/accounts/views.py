from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from django.contrib import messages
import requests
import os

from .firebase_auth import firebase_login

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Login page with Firebase authentication"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember', False)
        
        # Validate input
        if not email or not password:
            messages.error(request, 'Please enter both email and password.')
            return render(request, 'accounts/login.html')
        
        try:
            # Authenticate via Firebase and sync with Django
            user = firebase_login(request, email, password)
            
            if user is not None:
                login(request, user)
                
                # Set session timeout based on "Remember me"
                if not remember:
                    request.session.set_expiry(0)  # Browser session
                else:
                    request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
                
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                # Route users based on their role
                if user.is_staff and user.is_superuser:
                    # Super admins go to platform admin dashboard
                    return redirect('platform_admin:dashboard')
                elif hasattr(user, 'platform_profile'):
                    # Check if user has institution admin role
                    if user.platform_profile.role == 'institution_admin':
                        return redirect('institutions:dashboard')
                    else:
                        return redirect('home')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid email or password. Please check your credentials.')
                return render(request, 'accounts/login.html')
        except Exception as e:
            messages.error(request, 'An error occurred during login. Please try again.')
            print(f"Login error: {e}")
            return render(request, 'accounts/login.html')
    
    return render(request, 'accounts/login.html')


@require_http_methods(["GET", "POST"])
def password_reset_request(request):
    """Request password reset - sends reset email via Firebase"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'accounts/password_reset_request.html')
        
        try:
            # Use Firebase REST API to send password reset email
            api_key = os.environ.get('FIREBASE_API_KEY', '')
            if not api_key:
                messages.error(request, 'Password reset service not configured.')
                return render(request, 'accounts/password_reset_request.html')
            
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
            payload = {
                "requestType": "PASSWORD_RESET",
                "email": email
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                messages.success(request, 
                    f'Password reset link has been sent to {email}. Please check your inbox and spam folder.')
                return redirect('login')
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Failed to send reset email')
                messages.error(request, f'Error: {error_msg}')
                return render(request, 'accounts/password_reset_request.html')
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            print(f"Password reset error: {e}")
            return render(request, 'accounts/password_reset_request.html')
    
    return render(request, 'accounts/password_reset_request.html')


@require_http_methods(["GET", "POST"])
def password_reset_confirm(request):
    """Confirm password reset with reset code"""
    if request.method == 'POST':
        reset_code = request.POST.get('reset_code', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Validate inputs
        if not reset_code or not new_password:
            messages.error(request, 'Please provide all required information.')
            return render(request, 'accounts/password_reset_confirm.html')


        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/password_reset_confirm.html')
        
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'accounts/password_reset_confirm.html')
        
        try:
            # Use Firebase REST API to reset password
            api_key = os.environ.get('FIREBASE_API_KEY', '')
            if not api_key:
                messages.error(request, 'Password reset service not configured.')
                return render(request, 'accounts/password_reset_confirm.html')
            
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:resetPassword?key={api_key}"
            payload = {
                "oobCode": reset_code,
                "newPassword": new_password
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                messages.success(request, 
                    'Password has been reset successfully. You can now login with your new password.')
                return redirect('login')
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Failed to reset password')
                messages.error(request, f'Error: {error_msg}')
                return render(request, 'accounts/password_reset_confirm.html')
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            print(f"Password reset confirm error: {e}")
            return render(request, 'accounts/password_reset_confirm.html')
    
    return render(request, 'accounts/password_reset_confirm.html')


@require_http_methods(["GET"])
def logout_view(request):
    """Log the user out and return to the login page."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')
