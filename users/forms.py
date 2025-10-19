from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Student, Employer


# -------------------------
# User Forms
# -------------------------

class UserCreationForm(UserCreationForm):
    """Form for creating a new User"""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role")


class UserChangeForm(UserChangeForm):
    """Form for updating an existing User"""
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ("username", "email", "role", "is_active", "is_staff")


# -------------------------
# Student Form
# -------------------------

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            "student_id",
            "degree",
            "year_of_study",
            "cv",
            "cover_letter",
        ]


# -------------------------
# Employer Form
# -------------------------

class EmployerForm(forms.ModelForm):
    class Meta:
        model = Employer
        fields = [
            "employer_id",
            "company_name",
            "industry",
        ]
