from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import DemoRequest

@require_http_methods(["GET", "POST"])
def book_demo(request):
    """Book a demo page and handle form submissions"""
    if request.method == 'POST':
        # Collect form data
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        job_title = request.POST.get('job_title', '')
        institution_name = request.POST.get('institution_name', '')
        institution_type = request.POST.get('institution_type', '')
        student_count = request.POST.get('student_count', '')
        country = request.POST.get('country', '')
        challenge = request.POST.get('challenge', '')
        message = request.POST.get('message', '')
        preferred_time = request.POST.get('preferred_time', '')
        include_team = request.POST.get('include_team', False)
        agree = request.POST.get('agree', False)
        
        # Validation
        if not all([full_name, email, phone, job_title, institution_name, 
                   institution_type, student_count, country, challenge, preferred_time, agree]):
            messages.error(request, 'Please fill in all required fields and agree to the terms.')
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
            return render(request, 'leads/demo.html')
            
        except Exception as e:
            messages.error(request, f'An error occurred while processing your request. Please try again.')
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
