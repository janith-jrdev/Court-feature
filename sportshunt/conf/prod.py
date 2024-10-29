from .common import *
from django.core.exceptions import ImproperlyConfigured

if not os.getenv("SECRET_KEY"):
    raise ImproperlyConfigured("Environment variables not set")

SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = False
SOCIAL_AUTH_AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
SOCIAL_AUTH_AUTH0_KEY = os.getenv("AUTH0_CLIENT_ID")
SOCIAL_AUTH_AUTH0_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

RAZOR_KEY_ID = None # os.getenv("RAZOR_KEY_ID")
RAZOR_SECRET_KEY = None # os.getenv("RAZOR_SECRET_KEY")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1").split(",") + ["sportshunt.in"]
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS").split(",") if os.getenv("CSRF_TRUSTED_ORIGINS") else ["https://sportshunt.in"]

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

WSGI_APPLICATION = "sportshunt.wsgi_prod.application"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
