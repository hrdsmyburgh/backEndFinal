from rest_framework import viewsets, status
from rest_framework.response import Response
<<<<<<< HEAD
from rest_framework.decorators import api_view, permission_classes, action
=======
from rest_framework.decorators import api_view, permission_classes
>>>>>>> 7afbf2608e9044b265d0e408f4daa2beb500f4c6
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.contrib.auth import authenticate

<<<<<<< HEAD

=======
>>>>>>> 7afbf2608e9044b265d0e408f4daa2beb500f4c6
from .models import User, Student, Employer
from .serializers import (
    UserSerializer, StudentSerializer, EmployerSerializer,
    RegisterSerializer, LoginSerializer, ForgotPasswordSerializer,
    PasswordResetSerializer, ResetPasswordConfirmSerializer, StudentCVUploadSerializer
)

# ------------------------------
# VIEWSETS
# ------------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class EmployerViewSet(viewsets.ModelViewSet):
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer

# ------------------------------
# AUTHENTICATION
# ------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user).data,
            "token": token.key,
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username_or_email = request.data.get("username")
    password = request.data.get("password")

    # Authenticate user using username
    user = authenticate(username=username_or_email, password=password)

    # If not found, try email
    if user is None:
        try:
            user_obj = User.objects.get(email=username_or_email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

    if user is None:
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

    token, _ = Token.objects.get_or_create(user=user)
    user_data = UserSerializer(user).data
    user_data['role'] = user.role if hasattr(user, 'role') else 'unknown'

    return Response({"user": user_data, "token": token.key})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        request.user.auth_token.delete()
    except (AttributeError, Token.DoesNotExist):
        pass
    return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reset_password(request):
    serializer = PasswordResetSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "No user found with this email"}, status=status.HTTP_404_NOT_FOUND)

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{uidb64}/{token}/"
        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password:\n{reset_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        return Response({"detail": "Password reset email sent."}, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_confirm(request):
    serializer = ResetPasswordConfirmSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_cv(request):
    user = request.user
    if not user.is_student():
        return Response({"detail": "Only students can upload CVs."}, status=status.HTTP_403_FORBIDDEN)

    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        return Response({"detail": "Student profile not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = StudentCVUploadSerializer(student, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"detail": "CV uploaded successfully.", "cv": serializer.data.get("cv")}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ------------------------------
# USER API ROOT
# ------------------------------
@api_view(['GET'])
def user_api_root(request, format=None):
    return Response({
        'register': reverse('users:register', request=request, format=format),
        'login': reverse('users:login', request=request, format=format),
        'reset_password': reverse('users:reset_password', request=request, format=format),
        'forgot_password': reverse('users:forgot_password', request=request, format=format),
<<<<<<< HEAD
    })


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current logged-in user's profile"""
    user = request.user

    if request.method == 'GET':
        user_data = UserSerializer(user).data

        # Add student profile if user is a student
        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                student_data = StudentSerializer(student, context={'request': request}).data  
                user_data['student_profile'] = student_data
            except Student.DoesNotExist:
                user_data['student_profile'] = None

        return Response(user_data)

    elif request.method in ['PUT', 'PATCH']:
        # Separate user fields from student fields
        user_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'gender']
        student_fields = ['bio', 'address', 'city', 'province', 'zip']

        user_data_to_update = {k: v for k, v in request.data.items() if k in user_fields}
        student_data_to_update = {k: v for k, v in request.data.items() if k in student_fields}

        # Update user fields
        if user_data_to_update:
            user_serializer = UserSerializer(user, data=user_data_to_update, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Update student profile if exists and has student data
        if student_data_to_update and user.role == 'student':
            try:
                student = Student.objects.get(user=user)
            except Student.DoesNotExist:
                # Create student profile if it doesn't exist
                student = Student.objects.create(user=user, student_id=f'STU{user.id}')
            
            student_serializer = StudentSerializer(student, data=student_data_to_update, partial=True)
            if student_serializer.is_valid():
                student_serializer.save()
            else:
                return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Return updated user data with student profile
        response_data = UserSerializer(user).data
        if user.role == 'student':
            try:
                student = Student.objects.get(user=user)
                response_data['student_profile'] = StudentSerializer(student).data
            except Student.DoesNotExist:
                response_data['student_profile'] = None
        
        return Response(response_data)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_profile_picture(request):
    """Upload profile picture for student"""
    user = request.user
    
    if user.role != 'student':
        return Response({"detail": "Only students can upload profile pictures."}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        student = Student.objects.create(user=user, student_id=f'STU{user.id}')
    
    if 'profile_picture' not in request.FILES:
        return Response({"detail": "No image file provided."}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    # Delete old profile picture if exists
    if student.profile_picture:
        student.profile_picture.delete(save=False)
    
    student.profile_picture = request.FILES['profile_picture']
    student.save()
    
    # Return FULL URL instead of relative path
    profile_picture_url = request.build_absolute_uri(student.profile_picture.url)
    
    return Response({
        "detail": "Profile picture uploaded successfully.",
        "profile_picture": profile_picture_url 
    }, status=status.HTTP_200_OK)
=======
    })
>>>>>>> 7afbf2608e9044b265d0e408f4daa2beb500f4c6
