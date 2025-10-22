from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("student", "Student"),
        ("employer", "Employer"),
    ]
    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Prefer not to say"),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)

    def is_student(self):
        return self.role == "student"

    def is_employer(self):
        return self.role == "employer"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    student_id = models.CharField(max_length=50, unique=True)
    degree = models.CharField(max_length=100, blank=True)
    year_of_study = models.CharField(max_length=50, blank=True)
    cv = models.FileField(upload_to="cvs/", blank=True, null=True)

<<<<<<< HEAD
    bio = models.TextField(blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    zip = models.CharField(max_length=20, blank=True, null=True)

    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)

=======
>>>>>>> 7afbf2608e9044b265d0e408f4daa2beb500f4c6
    def __str__(self):
        return self.user.username or f"Student ID {self.student_id}"
       


class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employer_profile")
    employer_id = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)

    def __str__(self):
        return self.company_name or self.user.username
