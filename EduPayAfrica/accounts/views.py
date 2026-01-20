from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib import messages

@require_http_methods(["GET", "POST"])
def login_view(request):
    """Login page and authentication"""
    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        remember = request.POST.get('remember', False)
        
        # Validate input
        if not email or not password:
            messages.error(request, 'Please enter both email and password.')
            return render(request, 'accounts/login.html')
        
        try:
            # Attempt authentication
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Set session timeout based on "Remember me"
                if not remember:
                    request.session.set_expiry(0)  # Browser session
                else:
                    request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
                
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('dashboard')  # TODO: Create dashboard view
            else:
                messages.error(request, 'Invalid email or password.')
                return render(request, 'accounts/login.html')
        except Exception as e:
            messages.error(request, 'An error occurred during login. Please try again.')
            return render(request, 'accounts/login.html')
    
    return render(request, 'accounts/login.html')
