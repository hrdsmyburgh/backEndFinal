Developer Guide – profiles App
1. Purpose

The profiles app extends Django’s built-in authentication system (User) by adding:

Extra fields like full name and bio.

File uploads like CVs and certificates.

A simple form and page where users can edit their profile.

It ensures every user has one profile, either automatically created via signals or manually linked.

2. How it fits into the backend

The profiles app connects to the backend through several key pieces:

a) Models

Profile is a Django model linked one-to-one with User.

Each user gets a corresponding profile that stores personal info and uploaded files.

b) Forms

ProfileForm provides a way to safely handle profile edits (protecting against bad input).

It controls what fields users can edit.

c) Views

edit_profile view handles displaying and saving profile edits.

Protected with @login_required so only authenticated users can access their own profile.

d) URLs

Routes are defined in profiles/urls.py.

Example: /profile/edit/ opens the edit profile page.

e) Templates

edit_profile.html is a simple form page for users to view/update their profile and upload files.

f) Signals

A post_save signal ensures whenever a User is created, a corresponding Profile is automatically created too.

3. Integration with the rest of the system
a) backend/settings.py

You must add:

INSTALLED_APPS = [
    ...
    'profiles',   # register the app
]

# Media files (for uploads like CVs and certificates)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


This tells Django where to store uploaded files and enables the app.

b) backend/urls.py

Add:

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    ...
    path("profile/", include("profiles.urls")),  # hook in profile routes
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


Now requests like /profile/edit/ are routed to the profiles app.

4. How it works with the Database

When you run python manage.py makemigrations && python manage.py migrate, Django creates a Profile table.

This table links one-to-one with the User table.

Uploaded files (CVs, certificates) are stored on disk (in media/cvs/ and media/certificates/) with references saved in the database.

Example DB structure:

auth_user table
-------------------
id | username | password | email | ...

profiles_profile table
----------------------
id | user_id | full_name | bio | cv | certificate

5. How it works with the Frontend

The frontend (if separate, e.g., React/Angular/Vue) will communicate with Django via:

Django Templates (default option, server-side rendering).

Or via a REST API (using Django REST Framework if you decide to expose endpoints).

a) Template-based frontend

Users visit /profile/edit/

Django renders edit_profile.html

Form is pre-filled with profile data

After editing and submitting, Django saves the profile and refreshes the page

b) API-based frontend

If you decide to add a frontend SPA (React, etc.), you’ll need:

A ProfileSerializer (via Django REST Framework)

API endpoints like /api/profile/

Then frontend fetches/sends data with JSON instead of using templates.

6. File Uploads

Files uploaded (CV, certificates) are stored under MEDIA_ROOT (/media/).

During development, Django serves them automatically.

In production, they should be served via a cloud provider (Azure Blob Storage, AWS S3, etc.).

Example:

User uploads CV → stored in /media/cvs/mycv.pdf

URL to access it: https://<domain>/media/cvs/mycv.pdf

7. Developer Notes & Best Practices
a) Authentication

Relies on Django’s built-in auth system (User).

Make sure django.contrib.auth is in INSTALLED_APPS.

Profile is linked one-to-one with User.

b) Signals

Profiles are auto-created when a User is created.

This avoids null issues where a user doesn’t have a profile yet.

c) Extending Profiles

If more fields are needed (phone number, LinkedIn, work experience, etc.), simply add them to Profile model and re-run migrations.

d) Testing

Add unit tests in profiles/tests.py to ensure profile creation, file uploads, and form validation work properly.

e) Deployment

In production, configure Azure Blob Storage or another cloud storage for file uploads instead of local disk.

Update DEFAULT_FILE_STORAGE in settings for that.

8. Example Workflow (End-to-End)

User registers/login → Django creates a User object.

Signal triggers → Auto-creates a Profile linked to that User.

User navigates to /profile/edit/ → Sees a form with profile fields + upload fields.

User uploads CV + certificate and saves → Files saved in media/, DB updated with file references.

User views their profile later → Sees download links to uploaded CV and certificate.