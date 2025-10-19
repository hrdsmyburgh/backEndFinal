from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Employer

# -------------------------
# Inline for Student (optional, keep for editing via User)
# -------------------------
class StudentInline(admin.StackedInline):
    model = Student
    can_delete = False
    verbose_name_plural = "Student Profile"

# -------------------------
# Inline for Employer (optional, keep for editing via User)
# -------------------------
class EmployerInline(admin.StackedInline):
    model = Employer
    can_delete = False
    verbose_name_plural = "Employer Profile"

# -------------------------
# User Admin
# -------------------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("username", "email", "first_name", "last_name", "role", "is_active", "is_staff", "date_joined")
    list_filter = ("role", "is_active", "is_staff", "date_joined")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("-date_joined",)

    def get_inline_instances(self, request, obj=None):
        """
        Show profile inline depending on user role
        """
        inlines = []
        if obj:
            if obj.is_student():
                inlines = [StudentInline(self.model, self.admin_site)]
            elif obj.is_employer():
                inlines = [EmployerInline(self.model, self.admin_site)]
        return inlines

# -------------------------
# Standalone Student Admin
# -------------------------
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "student_id", "get_first_name", "get_last_name", "degree", "year_of_study")
    list_filter = ("degree", "year_of_study")
    search_fields = ("user__username", "user__email", "student_id")

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'

# -------------------------
# Standalone Employer Admin
# -------------------------
@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ("user", "employer_id", "company_name", "industry")
    list_filter = ("industry",)
    search_fields = ("user__username", "user__email", "company_name", "employer_id")
