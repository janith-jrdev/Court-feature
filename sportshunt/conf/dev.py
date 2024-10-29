from .common import *

SECRET_KEY = "django-insecure-a5$u$o^s8o)y%bsaxnl%lbzn$mc&w#7po^gy#b_oe%g&(py_yj"
DEBUG = True
SOCIAL_AUTH_AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
SOCIAL_AUTH_AUTH0_KEY = os.getenv("AUTH0_CLIENT_ID")
SOCIAL_AUTH_AUTH0_SECRET = os.getenv("AUTH0_CLIENT_SECRET")

RAZOR_KEY_ID = os.getenv("RAZOR_KEY_ID")
RAZOR_SECRET_KEY = os.getenv("RAZOR_SECRET_KEY")

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["*"]


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


WSGI_APPLICATION = "sportshunt.wsgi.application"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
