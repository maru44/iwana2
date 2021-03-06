from pathlib import Path
import os
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_random_secret_key()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    
    'social_core.backends.open_id.OpenIdAuth',
    'social_core.backends.google.GoogleOAuth2',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''  # client id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = '' # client secret


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(BASE_DIR / 'db.sqlite3'),
    }
}


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = '<your_address>@gmail.com'
EMAIL_HOST_PASSWORD = '<your_password>'
FROM_EMAIL = 'smtp.gmail.com'
EMAIL_PORT = 587

# inquiry
INQ_URL_AWS = ""

#local desu

SQRAPE_URL_AWS = ""

SCRAPE_HEROKU = ""

