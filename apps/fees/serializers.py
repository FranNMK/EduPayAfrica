from rest_framework import serializers
from .models import FeeCategory, FeeStructure, FeeItem, StudentFee

class FeeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeCategory
        fields = '__all__'

class FeeItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    class Meta:
        model = FeeItem
        fields = '__all__'

class FeeStructureSerializer(serializers.ModelSerializer):
    items = FeeItemSerializer(many=True, read_only=True)
    class Meta:
        model = FeeStructure
        fields = '__all__'

class StudentFeeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.admission_number', read_only=True)
    class Meta:
        model = StudentFee
        fields = '__all__'
