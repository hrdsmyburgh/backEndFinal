from django.contrib import admin
from .models import Job, Application

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'location', 'is_active', 'posted_on')
    search_fields = ('title', 'description', 'employer__user__username')
    list_filter = ('is_active', 'type', 'experience', 'location')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_date')
    search_fields = ('job__title', 'applicant__user__username')
    list_filter = ('status', 'applied_date')
