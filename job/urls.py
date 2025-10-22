from django.urls import path
from . import views
from .views import (
    JobListAPIView, JobCreateAPIView, JobDetailAPIView,
    MyJobPostingsAPIView, JobStatsAPIView,
    ApplicationCreateAPIView, MyApplicationsAPIView,
    EmployerApplicationsAPIView, ApplicationStatusUpdateAPIView,
    ApplicationDetailAPIView,
)

urlpatterns = [
    # -------------------
    # Job API Root
    # -------------------
    path('', views.job_api_root, name='job-root'), 

    # -------------------
    # NEW ENDPOINT: Job Category Counts for Frontend Tiles
    # This corresponds to the frontend call: http://localhost:8000/api/job-counts/
    # -------------------
    path('job-counts/', views.job_counts, name='job-category-counts'), # <-- ADD THIS LINE

    # -------------------
    # The main project urls.py should add the /api/ prefix.
    # -------------------
    path('list/', JobListAPIView.as_view(), name='job-list'), 
    path('create/', JobCreateAPIView.as_view(), name='job-create'), 
    path('<int:pk>/', JobDetailAPIView.as_view(), name='job-detail'), 
    path('my/', MyJobPostingsAPIView.as_view(), name='my-jobs'), 
    path('stats/', JobStatsAPIView.as_view(), name='job-stats'), 

    # -------------------
    # Application Endpoints
    # -------------------
    path('applications/create/', ApplicationCreateAPIView.as_view(), name='application-create'),
    path('applications/my/', MyApplicationsAPIView.as_view(), name='my-applications'),
    path('applications/job/<int:job_id>/', EmployerApplicationsAPIView.as_view(), name='employer-applications'),
    path('applications/<int:application_id>/update-status/', ApplicationStatusUpdateAPIView.as_view(), name='application-update-status'),
    path('applications/<int:application_id>/', ApplicationDetailAPIView.as_view(), name='application-detail'),
]