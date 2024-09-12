from .common import *

SECRET_KEY = "django-insecure-a5$u$o^s8o)y%bsaxnl%lbzn$mc&w#7po^gy#b_oe%g&(py_yj"
DEBUG = True
SOCIAL_AUTH_AUTH0_DOMAIN = config('AUTH0_DOMAIN')
SOCIAL_AUTH_AUTH0_KEY = config('AUTH0_CLIENT_ID')
SOCIAL_AUTH_AUTH0_SECRET = config('AUTH0_CLIENT_SECRET')

ALLOWED_HOSTS = []


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


WSGI_APPLICATION = "sportshunt.wsgi.application"