from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .models import DemoRequest

@require_http_methods(["GET", "POST"])
def book_demo(request):
    """Book a demo page and handle form submissions"""
    if request.method == 'POST':
        # Collect form data
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        job_title = request.POST.get('job_title', '').strip()
        institution_name = request.POST.get('institution_name', '').strip()
        institution_type = request.POST.get('institution_type', '').strip()
        student_count = request.POST.get('student_count', '').strip()
        country = request.POST.get('country', '').strip()
        challenge = request.POST.get('challenge', '').strip()
        message = request.POST.get('message', '').strip()
        preferred_time = request.POST.get('preferred_time', '').strip()
        include_team = request.POST.get('include_team') == 'on'
        agree = request.POST.get('agree') == 'on'
        
        # Validation
        if not all([full_name, email, phone, job_title, institution_name,
                   institution_type, student_count, country, challenge, preferred_time]):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': 'Please fill in all required fields.'}, status=400)
            # Re-render without flashing server error banner
            return render(request, 'leads/demo.html')
        
        if not agree:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': 'Please agree to the Privacy Policy and Terms of Service.'}, status=400)
            # Re-render without flashing server error banner
            return render(request, 'leads/demo.html')
        if not agree:
            messages.error(request, 'Please agree to the Privacy Policy and Terms of Service.')
            return render(request, 'leads/demo.html')
        
        try:
            # Create DemoRequest record
            demo_request = DemoRequest.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                job_title=job_title,
                institution_name=institution_name,
                institution_type=institution_type,
                student_count=student_count,
                country=country,
                challenge=challenge,
                message=message,
                preferred_time=preferred_time,
                include_team=bool(include_team)
            )
            
            # Send confirmation email
            send_confirmation_email(full_name, email)
            
            messages.success(request, 'Thank you for booking a demo! We will be in touch within 24 hours.')
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': True, 'message': 'Thank you for booking a demo! We will be in touch within 24 hours.'})
            messages.success(request, 'Thank you for booking a demo! We will be in touch within 24 hours.')
            # PRG: redirect to clear form and show success after refresh
            return redirect('demo')
            
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'ok': False, 'error': 'An error occurred while processing your request. Please try again.'}, status=500)
            messages.error(request, 'An error occurred while processing your request. Please try again.')
            return render(request, 'leads/demo.html')
    
    return render(request, 'leads/demo.html')

def send_confirmation_email(full_name, email):
    """Send automated confirmation email to demo requestor"""
    subject = "Welcome to EduPay Africa - Demo Request Confirmed"
    message = f"""Hello {full_name},

Thank you for requesting a demo of EduPay Africa.

We're excited to show you how our platform can simplify education finance management for your institution. Our team will review your request and get back to you within 24 business hours to confirm the demo date and time.

In the meantime, if you have any questions, feel free to reach out to us at support@edupayafrica.com or +254 700 000 000.

Welcome to EduPay Africa!

Best regards,
The EduPay Africa Team
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
    except Exception as e:
        # Log error but don't fail the form submission
        print(f"Error sending confirmation email: {e}")
