from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login
from django.contrib import messages

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
                
                # Route super admins to platform admin dashboard
                if user.is_staff and user.is_superuser:
                    return redirect('platform_admin:dashboard')
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
