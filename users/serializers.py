from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Student, Employer 
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Ensure 'phone_number' and 'gender' are included if you want them visible
        fields = ["id", "username", "email", "first_name", "last_name", "role", "phone_number", "gender"]


class StudentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    gender = serializers.CharField(source='user.gender', read_only=True)



    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and request:
            return request.build_absolute_uri(obj.profile_picture.url)
        return None
    
    profile_picture = serializers.SerializerMethodField() 


    def update(self, instance, validated_data):
        user_data_to_update = {}
        user_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'gender']
        
        for field in user_fields:
            if field in validated_data:
                user_data_to_update[field] = validated_data.pop(field) 

        user = instance.user
        for attr, value in user_data_to_update.items():
            if value is not None:
                setattr(user, attr, value)
        user.save()

        return super().update(instance, validated_data)

    class Meta:
        model = Student
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "gender",
            "student_id",
            "degree",
            "year_of_study",
            "cv",
            "bio",
            "address",
            "city",
            "province",
            "zip",
            "profile_picture"
        ]


class EmployerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    def update(self, instance, validated_data):
        user_data_to_update = {}
        user_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
        
        for field in user_fields:
            if field in validated_data:
                user_data_to_update[field] = validated_data.pop(field) 

        user = instance.user
        for attr, value in user_data_to_update.items():
            if value is not None:
                setattr(user, attr, value)
        user.save()

        return super().update(instance, validated_data)

    class Meta:
        model = Employer
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "employer_id",
            "company_name",
            "industry",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    gender = serializers.CharField(write_only=True, required=False, allow_blank=True)
    student_id = serializers.CharField(write_only=True, required=False, allow_blank=True) 
    degree = serializers.CharField(write_only=True, required=False, allow_blank=True)
    year_of_study = serializers.CharField(write_only=True, required=False, allow_blank=True) 
    company_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    industry = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "password", 
            "first_name", "last_name", "role",
            "phone_number", "gender", 
            "student_id", "degree", "year_of_study", "company_name", "industry" 
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.pop("role")

        user_create_data = {
            'username': validated_data.pop("username"),
            'email': validated_data.pop("email"),
            'first_name': validated_data.pop("first_name", None),
            'last_name': validated_data.pop("last_name", None),
            
            'phone_number': validated_data.pop("phone_number", None),
            'gender': validated_data.pop("gender", None), 
        }

        student_data = {
            'student_id': validated_data.pop("student_id", None),
            'degree': validated_data.pop("degree", None),
            'year_of_study': validated_data.pop("year_of_study", None),
        }
        employer_data = {
            'company_name': validated_data.pop("company_name", None),
            'industry': validated_data.pop("industry", None),
        }
        
        if validated_data:
            for key in list(validated_data.keys()):
                validated_data.pop(key)
        
        user = User.objects.create_user(
            password=password,
            role=role,
            **user_create_data 
        )
        

        if user.role == "student":
            Student.objects.create(
                user=user, 
                student_id=student_data.get("student_id"),
                degree=student_data.get("degree"),
                year_of_study=student_data.get("year_of_study"),
            )
        elif user.role == "employer":
            Employer.objects.create(
                user=user,
                employer_id=f"EMP{user.id}",
                company_name=employer_data.get("company_name"),
                industry=employer_data.get("industry"),
            )

        return user
    
    def validate(self, data):
        if not data.get("role"):
            raise serializers.ValidationError("Role is required.")
        
        if data.get("role") == "student":
            if not data.get("first_name") or not data.get("last_name") or not data.get("student_id"):
                raise serializers.ValidationError("First name, last name, and student ID are required for students.")
                
        if data.get("role") == "employer":
            if not data.get("company_name") or not data.get("industry"):
                raise serializers.ValidationError("Company name and industry are required for employers.")
                
        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        data["user"] = user
        return data


class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        user = self.context["request"].user
        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError({"old_password": "Old password is not correct."})
        return data

    def save(self, **kwargs):
        user = self.context["request"].user 
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is registered with this email.")
        return value


class ResetPasswordConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data["uidb64"]))
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uidb64": "Invalid UID"})

        if not default_token_generator.check_token(self.user, data["token"]):
            raise serializers.ValidationError({"token": "Invalid or expired token"})

        return data

    def save(self):
        self.user.set_password(self.validated_data["new_password"])
        self.user.save()
        return self.user


class StudentCVUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["cv"]

    def update(self, instance, validated_data):
        instance.cv = validated_data.get("cv", instance.cv)
        instance.save()
        return instance