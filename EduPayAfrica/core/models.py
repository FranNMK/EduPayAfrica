from django.db import models
from django.utils import timezone


class ContactInquiry(models.Model):
    """Store contact form submissions"""
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    privacy_agreed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"

class NewsletterSubscriber(models.Model):
    """Model for newsletter subscribers"""
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"

    def __str__(self):
        return f"{self.full_name or self.email} - Subscribed on {self.subscribed_at.strftime('%Y-%m-%d')}"


class NewsArticle(models.Model):
    """Model for news articles"""
    title = models.CharField(max_length=500)
    excerpt = models.TextField(max_length=500)
    content = models.TextField()
    icon_class = models.CharField(max_length=100, default="fas fa-newspaper", help_text="FontAwesome icon class")
    gradient_start = models.CharField(max_length=50, default="#1e40af", help_text="Start color for gradient")
    gradient_end = models.CharField(max_length=50, default="#7c3aed", help_text="End color for gradient")
    featured_image = models.ImageField(upload_to='news/', blank=True, null=True)
    published_date = models.DateField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order on page")

    class Meta:
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"
        ordering = ['-published_date']

    def __str__(self):
        return f"{self.title} - {self.published_date.strftime('%Y-%m-%d')}"


class JobPosition(models.Model):
    """Model for job positions"""
    title = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(help_text="Enter requirements separated by new lines")
    location = models.CharField(max_length=255)
    employment_type = models.CharField(max_length=100, choices=[
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ])
    salary_range = models.CharField(max_length=255, blank=True)
    is_open = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Position"
        verbose_name_plural = "Job Positions"
        ordering = ['-created_date']

    def __str__(self):
        status = "Open" if self.is_open else "Closed"
        return f"{self.title} ({status}) - {self.department}"


class JobApplication(models.Model):
    """Model for job applications"""
    job_position = models.ForeignKey(JobPosition, on_delete=models.CASCADE, related_name='applications')
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    current_position = models.CharField(max_length=255)
    experience_years = models.IntegerField()
    cover_letter = models.TextField()
    cv_file = models.FileField(upload_to='applications/cv/')
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('submitted', 'Submitted'),
        ('reviewing', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    ], default='submitted')

    class Meta:
        verbose_name = "Job Application"
        verbose_name_plural = "Job Applications"
        ordering = ['-applied_date']

    def __str__(self):
        return f"{self.full_name} - {self.job_position.title} ({self.applied_date.strftime('%Y-%m-%d')})"

