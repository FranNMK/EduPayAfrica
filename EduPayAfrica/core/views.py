from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib import messages
from .models import NewsArticle, JobPosition, JobApplication
from .forms import NewsletterSubscriberForm, JobApplicationForm

@require_http_methods(["GET"])
def index(request):
    """Home page view"""
    return render(request, 'core/index.html')

@require_http_methods(["GET"])
def about(request):
    """About Us page view"""
    return render(request, 'core/about.html')

@require_http_methods(["GET", "POST"])
def contact(request):
    """Contact Us page view"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        privacy_agreed = request.POST.get('privacy_agreed', False)
        
        # Basic validation
        if not all([full_name, email, phone, subject, message, privacy_agreed]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'core/contact.html')
        
        # TODO: Save contact inquiry to database and send email
        # For now, just show success message
        messages.success(request, 'Thank you for reaching out! We will get back to you shortly.')
        return render(request, 'core/contact.html')
    
    return render(request, 'core/contact.html')

@require_http_methods(["GET", "POST"])
def news(request):
    """News & Careers page view"""
    if request.method == 'POST':
        form = NewsletterSubscriberForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Thank you for subscribing to our newsletter!')
            except Exception as e:
                messages.info(request, 'You are already subscribed to our newsletter.')
        else:
            messages.error(request, 'Please enter a valid email address.')
        return redirect('news')
    
    articles = NewsArticle.objects.filter(is_published=True).order_by('order', '-published_date')
    job_positions = JobPosition.objects.filter(is_open=True)
    form = NewsletterSubscriberForm()
    
    context = {
        'articles': articles,
        'job_positions': job_positions,
        'form': form,
    }
    return render(request, 'core/news.html', context)

@require_http_methods(["GET", "POST"])
def apply_job(request, job_id):
    """Job application view"""
    job_position = get_object_or_404(JobPosition, id=job_id, is_open=True)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job_position = job_position
            application.save()
            messages.success(request, 'Your application has been submitted successfully! We will review it and get back to you soon.')
            return redirect('news')
        else:
            messages.error(request, 'Please check your form and try again.')
    else:
        form = JobApplicationForm()
    
    context = {
        'job_position': job_position,
        'form': form,
    }
    return render(request, 'core/apply_job.html', context)

@require_http_methods(["GET"])
def privacy(request):
    """Privacy Policy page view"""
    return render(request, 'core/privacy.html')

@require_http_methods(["GET"])
def terms(request):
    """Terms of Service page view"""
    return render(request, 'core/terms.html')

