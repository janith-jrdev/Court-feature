from .common import *

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True
SOCIAL_AUTH_AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
SOCIAL_AUTH_AUTH0_KEY = os.getenv("AUTH0_CLIENT_ID")
SOCIAL_AUTH_AUTH0_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

RAZOR_KEY_ID = None # os.getenv("RAZOR_KEY_ID")
RAZOR_SECRET_KEY = None # os.getenv("RAZOR_SECRET_KEY")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "sportshunt.in,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "https://sportshunt.in").split(",")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PGDATABASE'),
        'USER': os.getenv('PGUSER'),
        'PASSWORD': os.getenv('PGPASSWORD'),
        'HOST': os.getenv('PGHOST'),
        'PORT': os.getenv('PGPORT'),
    }
}

# WSGI_APPLICATION = "sportshunt.wsgi.prod"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]