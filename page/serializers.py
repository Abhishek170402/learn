from rest_framework import serializers
from .models import Student
# from .models import details

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'
        
        
# class detailsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = details
#         fields = '__all__'
