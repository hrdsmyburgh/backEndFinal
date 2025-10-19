from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # The root URL redirects to the user API path
    path('', RedirectView.as_view(url='api/users/', permanent=False)),
    path('admin/', admin.site.urls),
    
    # This include provides /accounts/login/, /accounts/logout/, etc.
    # The views here respect LOGIN_REDIRECT_URL and the ?next= parameter.
    path("accounts/", include("django.contrib.auth.urls")), 
    
    path("api/users/", include("users.urls")),
    path('api/job/', include('job.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)