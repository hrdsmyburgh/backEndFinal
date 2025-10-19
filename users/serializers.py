from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
# Removed 'User' from this import list, as it is correctly loaded via get_user_model() below
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
    user = UserSerializer(read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",
            "user",
            "student_id",
            "degree",
            "year_of_study",
            "cv",
        ]


class EmployerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Employer
        fields = [
            "id",
            "user",
            "employer_id",
            "company_name",
            "industry",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    # User fields that are not part of AbstractUser default, but are in your model:
    phone_number = serializers.CharField(write_only=True, required=False, allow_blank=True)
    gender = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    # Profile-specific fields:
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
            # All fields being passed from the client
            "phone_number", "gender", 
            "student_id", "degree", "year_of_study", "company_name", "industry" 
        ]

    def create(self, validated_data):
        # 1. Pop fields required for user creation and authentication
        password = validated_data.pop("password")
        role = validated_data.pop("role")
        
        # 2. Extract ALL base User fields explicitly from validated_data
        # This ensures they are removed from validated_data and passed only to User.create_user
        user_create_data = {
            'username': validated_data.pop("username"),
            'email': validated_data.pop("email"),
            'first_name': validated_data.pop("first_name", None),
            'last_name': validated_data.pop("last_name", None),
            
            # CRITICAL: These are base User fields, but they must be popped here
            'phone_number': validated_data.pop("phone_number", None),
            'gender': validated_data.pop("gender", None), 
        }

        # 3. Extract profile-specific data (validated_data should now only contain profile fields)
        student_data = {
            'student_id': validated_data.pop("student_id", None),
            'degree': validated_data.pop("degree", None),
            'year_of_study': validated_data.pop("year_of_study", None),
        }
        employer_data = {
            'company_name': validated_data.pop("company_name", None),
            'industry': validated_data.pop("industry", None),
        }
        
        # 4. Final check: Ensure validated_data is empty after popping all known fields
        # This step is critical if any unexpected data remains! 
        if validated_data:
            # Although this block should not run, it guarantees only known fields are passed.
            for key in list(validated_data.keys()):
                validated_data.pop(key)
        
        # 5. Create the base User object
        user = User.objects.create_user(
            password=password,
            role=role,
            **user_create_data # Unpack ALL base user fields here
        )
        
        # 6. Create linked profile (only profile-specific data is passed)
        if user.role == "student":
            Student.objects.create(
                user=user, 
                student_id=student_data.get("student_id"),
                degree=student_data.get("degree"),
                year_of_study=student_data.get("year_of_study"),
            )
        elif user.role == "employer":
            # You might need to adjust this employer_id generation logic if it needs more padding
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
        # FIX: Removed the explicit type hint ': User' to resolve Pylance warning
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
            # 'self.user' will be the correct User type
            self.user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uidb64": "Invalid UID"})

        if not default_token_generator.check_token(self.user, data["token"]):
            raise serializers.ValidationError({"token": "Invalid or expired token"})

        return data

    def save(self):
        # self.user is implicitly the User model instance
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