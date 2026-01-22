"""
URL configuration for EduPayAfrica project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Core views
from core import views as core_views

# Leads views
from leads import views as leads_views

# Accounts views
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core app URLs
    path('', core_views.index, name='home'),
    path('about/', core_views.about, name='about'),
    path('contact/', core_views.contact, name='contact'),
    path('news/', core_views.news, name='news'),
    path('apply/<int:job_id>/', core_views.apply_job, name='apply_job'),
    path('privacy/', core_views.privacy, name='privacy'),
    path('terms/', core_views.terms, name='terms'),
    
    # Leads app URLs
    path('demo/', leads_views.book_demo, name='demo'),
    
    # Accounts app URLs
    path('login/', accounts_views.login_view, name='login'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
