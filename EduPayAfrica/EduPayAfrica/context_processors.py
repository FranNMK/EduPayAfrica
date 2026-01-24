"""
Context processors for making settings available in templates
"""
import json
from django.conf import settings
from django.utils.safestring import mark_safe


def firebase_config(request):
    """Add Firebase configuration to template context"""
    return {
        'firebase_config': settings.FIREBASE_CONFIG
    }
