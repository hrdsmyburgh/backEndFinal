from django.db import models
from django.conf import settings
from users.models import Employer, Student


class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=200, default="")  # full time, part time
    experience = models.CharField(max_length=200, default="")
    detailed_experience = models.TextField(default="")
    education = models.TextField(default="")
    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name="jobs"
    )
    location = models.CharField(max_length=100, default="")
    salary_range = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    vacancies = models.PositiveIntegerField(default=1)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("reviewed", "Under Review"),
        ("shortlisted", "Shortlisted"),
        ("rejected", "Rejected"),
        ("accepted", "Accepted"),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    cover_letter = models.FileField(upload_to="cover_letters/", blank=True, null=True)
    resume = models.FileField(upload_to="resumes/")
    additional_documents = models.FileField(upload_to="documents/", blank=True, null=True)
    applied_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('job', 'applicant')  # Prevent duplicate applications

    def __str__(self):
        return f"{self.applicant.student_id} - {self.job.title}"
