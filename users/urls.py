from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "users"

router = DefaultRouter()
router.register(r"users", views.UserViewSet, basename="user")
router.register(r"students", views.StudentViewSet, basename="student")
router.register(r"employers", views.EmployerViewSet, basename="employer")

urlpatterns = [
    path("", include(router.urls)),
    path('', views.user_api_root, name='user-root'),

    # Auth endpoints
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("me/", views.current_user, name="current-user"),
    path("upload-profile-picture/", views.upload_profile_picture, name="upload-profile-picture"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password-confirm/", views.reset_password_confirm, name="reset_password_confirm"),
    path("upload-cv/", views.upload_cv, name="upload_cv"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)