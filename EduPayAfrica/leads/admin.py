from django.contrib import admin
from .models import DemoRequest

@admin.register(DemoRequest)
class DemoRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'institution_name', 'institution_type', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status', 'institution_type', 'student_count', 'country', 'created_at')
    search_fields = ('full_name', 'email', 'institution_name', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'email', 'phone', 'job_title')
        }),
        ('Institution Details', {
            'fields': ('institution_name', 'institution_type', 'student_count', 'country')
        }),
        ('Request Details', {
            'fields': ('challenge', 'message', 'preferred_time', 'include_team')
        }),
        ('Management', {
            'fields': ('status', 'notes', 'created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ('full_name', 'email', 'phone', 'institution_name')
        return self.readonly_fields
