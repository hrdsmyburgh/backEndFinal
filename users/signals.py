from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Student, Employer


# @receiver(post_save, sender=User)
# def send_welcome_email(sender, instance, created, **kwargs):
#     if created:
#         # Skip sending email for superusers
#         if instance.is_superuser:
#             return
#         send_mail(
#             "Welcome to Placement Portal",
#             f"Hi {instance.username}, thanks for registering as a {instance.get_role_display()}!",
#             settings.EMAIL_HOST_USER,
#             [instance.email],
#             fail_silently=False,
#         )
