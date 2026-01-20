from django.contrib import admin
from .models import NewsletterSubscriber, NewsArticle, JobPosition, JobApplication

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'full_name')
    readonly_fields = ('subscribed_at',)

@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'is_published', 'order')
    list_filter = ('is_published', 'published_date')
    search_fields = ('title', 'content')
    ordering = ('order', '-published_date')
    fieldsets = (
        ('Article Content', {
            'fields': ('title', 'excerpt', 'content', 'featured_image', 'published_date')
        }),
        ('Display Settings', {
            'fields': ('icon_class', 'gradient_start', 'gradient_end', 'order', 'is_published')
        }),
    )

@admin.register(JobPosition)
class JobPositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'employment_type', 'is_open', 'created_date')
    list_filter = ('is_open', 'employment_type', 'created_date')
    search_fields = ('title', 'department', 'location')
    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'department', 'employment_type', 'location', 'salary_range')
        }),
        ('Job Details', {
            'fields': ('description', 'requirements')
        }),
        ('Application Status', {
            'fields': ('is_open',)
        }),
    )

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'job_position', 'email', 'applied_date', 'status')
    list_filter = ('status', 'applied_date', 'job_position')
    search_fields = ('full_name', 'email', 'job_position__title')
    readonly_fields = ('applied_date', 'job_position', 'full_name', 'email', 'phone', 'current_position', 'experience_years', 'cover_letter', 'cv_file')
    fieldsets = (
        ('Application Details', {
            'fields': ('job_position', 'full_name', 'email', 'phone', 'applied_date')
        }),
        ('Applicant Information', {
            'fields': ('current_position', 'experience_years', 'cover_letter', 'cv_file')
        }),
        ('Status', {
            'fields': ('status',)
        }),
    )

