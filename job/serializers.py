from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Job, Application
from users.serializers import StudentSerializer, EmployerSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class JobSerializer(serializers.ModelSerializer):
    employer = EmployerSerializer(read_only=True)
    applications_count = serializers.SerializerMethodField()
    user_has_applied = serializers.SerializerMethodField() 
    
    def get_user_has_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            student = getattr(request.user, 'student_profile', None)
            if student:
                return Application.objects.filter(job=obj, applicant=student).exists()
        return False
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'description', 'posted_on', 'type', 'experience',
            'detailed_experience', 'education', 'employer', 'location', 'salary_range',
            'is_active', 'applications_count', 'user_has_applied'
        ]
        read_only_fields = ['posted_on']
    
    def get_applications_count(self, obj):
        return obj.applications.count()


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = StudentSerializer(read_only=True)
    job = JobSerializer(read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'job', 'applicant', 'cover_letter', 'resume',
            'additional_documents', 'applied_date', 'status', 'notes'
        ]
        read_only_fields = ['applied_date', 'applicant', 'job']


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['job', 'cover_letter', 'resume', 'additional_documents']
    
    def validate_job(self, value):
        if not value.is_active:
            raise serializers.ValidationError("This job posting is no longer active.")
        return value

    def validate(self, data):
        user = self.context['request'].user
        if not hasattr(user, 'student_profile'):
            raise serializers.ValidationError("Only students can apply for jobs.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        student_profile = user.student_profile
        
        application = Application.objects.create(
            applicant=student_profile,
            job=validated_data['job'],
            cover_letter=validated_data['cover_letter'],
            resume=student_profile.cv,  # automatically use student's CV
            additional_documents=validated_data.get('additional_documents')
        )
        return application


class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status', 'notes']
    
    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Application.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Status must be one of: {valid_statuses}")
        return value

class JobCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'type', 'experience',
            'detailed_experience', 'education', 'location', 'salary_range'
        ]
    
    def validate_title(self, value):
        if len(value) < 5:
            raise serializers.ValidationError("Job title must be at least 5 characters long.")
        return value
    
    def validate_description(self, value):
        if len(value) < 20:
            raise serializers.ValidationError("Job description must be at least 20 characters long.")
        return value

    def create(self, validated_data):
        employer = self.context['request'].user.employer_profile
        job = Job.objects.create(employer=employer, **validated_data)
        return job
    
    def validate(self, data):
        user = self.context['request'].user
        if not hasattr(user, 'employer_profile'):
            raise serializers.ValidationError("Only employers can create jobs.")
        return data
