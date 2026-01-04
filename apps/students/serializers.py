from rest_framework import serializers
from .models import Student, Parent

class ParentSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = Parent
        fields = ['id', 'user', 'user_email', 'phone_number', 'occupation', 'address']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
