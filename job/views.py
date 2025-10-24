from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError 
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.reverse import reverse 
#from django.http import JsonResponse 

from .models import Job, Application
from .serializers import (
    JobSerializer, JobCreateSerializer,
    ApplicationSerializer, ApplicationCreateSerializer,
    ApplicationStatusUpdateSerializer
)

@api_view(['GET'])
@permission_classes([AllowAny])
def job_counts(request):
    """
    Returns a JSON object of active job counts grouped by category.
    The format is required by the frontend JavaScript: {"Design-Creative": 52, ...}
    """
    # Filter for active jobs only (optional, but usually desired for display)
    counts = Job.objects.filter(is_active=True).values('type').annotate(count=Count('type'))
    
    # Convert the QuerySet (list of dicts) into the simple dictionary format: {'CategoryName': Count}
    job_counts = {item['type']: item['count'] for item in counts}
    
    # Return the dictionary as a JSON response
    return Response(job_counts)
    #return Response({"Success-Test": 100, "If-This-Works": 50})

# ------------------------------
# JOB VIEWS
# ------------------------------
class JobListAPIView(generics.ListAPIView):
# ... (rest of the existing JobListAPIView) ...
    """List all active jobs with optional filtering"""
    serializer_class = JobSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True)
        search = self.request.query_params.get('search')
        location = self.request.query_params.get('location')
        job_type = self.request.query_params.get('type')
        experience = self.request.query_params.get('experience')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(detailed_experience__icontains=search)
            )
        if location:
            queryset = queryset.filter(location__icontains=location)
        if job_type:
            queryset = queryset.filter(type__icontains=job_type)
        if experience:
            queryset = queryset.filter(experience__icontains=experience)

        return queryset.order_by('-posted_on')


class JobCreateAPIView(generics.CreateAPIView):
# ... (rest of the existing JobCreateAPIView) ...
    """Allow employers to create a new job"""
    serializer_class = JobCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        
        # Ensures only users with an employer profile can post jobs
        if not hasattr(user, 'employer_profile'):
            raise PermissionDenied("Only employers can create jobs.")
        
        # ✅ FIX: Assigns the job to the logged-in employer profile
        serializer.save(employer=user.employer_profile)


class JobDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
# ... (rest of the existing JobDetailAPIView) ...
    """Retrieve, update or delete a job (employer only for updates/deletes)"""
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        job = self.get_object()
        if not hasattr(request.user, 'employer_profile') or job.employer != request.user.employer_profile:
            raise PermissionDenied("You can only edit your own job postings.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        job = self.get_object()
        if not hasattr(request.user, 'employer_profile') or job.employer != request.user.employer_profile:
            raise PermissionDenied("You can only delete your own job postings.")
        return super().destroy(request, *args, **kwargs)


class MyJobPostingsAPIView(generics.ListAPIView):
# ... (rest of the existing MyJobPostingsAPIView) ...
    """List all jobs posted by the logged-in employer"""
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'employer_profile'):
            raise PermissionDenied("Only employers can view their job postings.")
        return Job.objects.filter(employer=user.employer_profile).order_by('-posted_on')


# ------------------------------
# APPLICATION VIEWS
# ------------------------------
class ApplicationCreateAPIView(generics.CreateAPIView):
# ... (rest of the existing ApplicationCreateAPIView) ...
    """Students apply to a job"""
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if not hasattr(user, 'student_profile'):
            raise PermissionDenied("Only students can apply for jobs.")
        serializer.save()


class MyApplicationsAPIView(generics.ListAPIView):
# ... (rest of the existing MyApplicationsAPIView) ...
    """List all applications submitted by the logged-in student"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'student_profile'):
            raise PermissionDenied("Only students can view their applications.")
        return Application.objects.filter(applicant=user.student_profile).order_by('-applied_date')


class EmployerApplicationsAPIView(generics.ListAPIView):
# ... (rest of the existing EmployerApplicationsAPIView) ...
    """List all applications for a specific job (employer only)"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'employer_profile'):
            raise PermissionDenied("Only employers can view job applications.")
        job_id = self.kwargs['job_id']
        job = get_object_or_404(Job, id=job_id, employer=user.employer_profile)
        return Application.objects.filter(job=job).order_by('-applied_date')


class ApplicationStatusUpdateAPIView(generics.UpdateAPIView):
# ... (rest of the existing ApplicationStatusUpdateAPIView) ...
    """Employers update the status or notes of an application"""
    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Application.objects.all()
    lookup_url_kwarg = 'application_id'

    def perform_update(self, serializer):
        application = self.get_object()
        user = self.request.user
        if not hasattr(user, 'employer_profile') or application.job.employer != user.employer_profile:
            raise PermissionDenied("You can only update applications for your own job postings.")
        serializer.save()


class ApplicationDetailAPIView(generics.RetrieveAPIView):
# ... (rest of the existing ApplicationDetailAPIView) ...
    """Retrieve an application (student or employer)"""
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Application.objects.all()
    lookup_url_kwarg = 'application_id'

    def get_object(self):
        application = super().get_object()
        user = self.request.user
        # FIX 2025-10-11: Corrected checks to use 'student_profile' and 'employer_profile'
        if hasattr(user, 'student_profile') and application.applicant == user.student_profile:
            return application
        if hasattr(user, 'employer_profile') and application.job.employer == user.employer_profile:
            return application
        raise PermissionDenied("You do not have permission to view this application.")


# ------------------------------
# EMPLOYER DASHBOARD STATS
# ------------------------------
class JobStatsAPIView(generics.GenericAPIView):
# ... (rest of the existing JobStatsAPIView) ...
    """Return stats for an employer's jobs"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        if not hasattr(user, 'employer_profile'):
            raise PermissionDenied("Only employers can view job stats.")
        jobs = Job.objects.filter(employer=user.employer_profile)
        total_jobs = jobs.count()
        active_jobs = jobs.filter(is_active=True).count()
        total_applications = Application.objects.filter(job__in=jobs).count()
        return Response({
            'total_jobs': total_jobs,
            'active_jobs': active_jobs,
            'total_applications': total_applications,
        })


# ------------------------------
# JOB API ROOT
# ------------------------------
@api_view(['GET'])
def job_api_root(request, format=None):
# ... (rest of the existing job_api_root) ...
    """Root for the Job API, listing main job and application endpoints"""
    return Response({
        'list_jobs': reverse('job-list', request=request, format=format),
        'create_job': reverse('job-create', request=request, format=format),
        'my_jobs': reverse('my-jobs', request=request, format=format),
        'job_stats': reverse('job-stats', request=request, format=format),
        'create_application': reverse('application-create', request=request, format=format),
        'my_applications': reverse('my-applications', request=request, format=format),
    })