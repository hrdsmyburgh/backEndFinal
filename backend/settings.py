import os
from pathlib import Path
import dj_database_url
import ssl 

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-oi_$((p6v5_rfrar(bxdby3bv71ifo%wqs(c(y^f07gv6()3b!'

DEBUG = True

#AZURE_HOST = 'http://127.0.0.1:8000/users/register/'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
 #   AZURE_HOST 
]

# CSRF_TRUSTED_ORIGINS must include the HTTPS version of the Azure domain
# *** FIX: Added local HTTP frontend origins to pass CSRF check in dev ***
CSRF_TRUSTED_ORIGINS = [
    #f'https://{AZURE_HOST}',
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]

CORS_ALLOW_CREDENTIALS = True

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    
    # Local apps
    'job',
    'users',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",   
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000", 
    "http://127.0.0.1:8000",
    "http://localhost:9000",
    "http://127.0.0.1:9000",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


IS_LOCAL_DEV = True

if IS_LOCAL_DEV:
    DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB", "placementdb"),
        "USER": os.getenv("DJANGO_USER", "user"),
        "PASSWORD": os.getenv("DJANGO_PASSWORD", "password"),
        "HOST": os.getenv("DJANGO_HOST", "db"), 
        "PORT": os.getenv("DJANGO_PORT", "5432"),
        "OPTIONS": {
            "sslmode": os.getenv("DJANGO_SSLMODE", "disable"),
        },
    }
}
else:
     # Production configuration (Azure or other)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DJANGO_NAME", "placementdb"),
            "USER": os.getenv("DJANGO_USER", "user"),
            "PASSWORD": os.getenv("DJANGO_PASSWORD", "password"),
            "HOST": os.getenv("DJANGO_HOST", "mydbserver123.postgres.database.azure.com"),
            "PORT": os.getenv("DJANGO_PORT", "5432"),
            "OPTIONS": {
                "sslmode": os.getenv("DJANGO_SSLMODE", "require"),
            },
        }
    }
    


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 🔑 FIX 1: Set the default post-login destination to the student profile path
LOGIN_REDIRECT_URL = '/studentprofile/' 
# 🔑 FIX 2: Set the correct logout redirect path (assuming you want to go to the main login page)
LOGOUT_REDIRECT_URL = "/accounts/login/"
AUTH_USER_MODEL = "users.User"


# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8080") 

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "jobplacementhubco@gmail.com"
EMAIL_HOST_PASSWORD = "123jetstream" 
EMAIL_SSL_CONTEXT = ssl._create_unverified_context()
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24