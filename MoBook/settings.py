"""
Django settings for MoBook project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import datetime
import os
from pathlib import Path

import yaml

ROOT_URL = 'http://127.0.0.1:8000'

################################################################################
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

################################################################################
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Load secrets
if DEBUG:
    SECRET_FILENAME = "secrets_debug.yaml"
else:
    SECRET_FILENAME = "secrets.yaml"
with open(SECRET_FILENAME, "r") as f:
    SECRETS = yaml.safe_load(f)

BASE_URL = SECRETS['BASE_URL']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRETS["key"]
ALLOWED_HOSTS = ['*']

################################################################################
# Application definition

INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "channels",
    "oauth.apps.OauthConfig",
    "chat",
    "message",
    "notif",
    "user.apps.UserConfig",
    "org.apps.OrgConfig",
    "project.apps.ProjectConfig",
    "live.apps.LiveConfig",
    "artifact.apps.ArtifactConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "MoBook.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI_APPLICATION = "MoBook.wsgi.application"
ASGI_APPLICATION = 'MoBook.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('localhost', 6379)],
        },
    },
}

################################################################################
# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": SECRETS["database"]
}

print("==================================================")
print(SECRETS["database"])
print("==================================================")


################################################################################
# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

################################################################################
# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True
USE_L10N = True

USE_TZ = True

os.environ["TZ"] = TIME_ZONE

################################################################################
# Static & Media files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    "static"
]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

################################################################################
# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

################################################################################
# CORS configurations
#

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# CORS_ALLOWED_ORIGINS = SECRETS['CORS_ALLOWED_ORIGINS']

################################################################################


# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
#     ),
# }

# JWT token will expire after 3000 seconds = 50 min
# For debug, you can set it to 14 days = 1,209,600 seconds
JWT_AUTH = {
    'JWT_VERIFY': True,
    'JWT_VERIFY_EXPIRATION': True,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=1209600),
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}

###############################################################################


with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

################################################################################
# Email configuration
#
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_CONFIG = SECRETS['email']
EMAIL_HOST = EMAIL_CONFIG['EMAIL_HOST']
EMAIL_PORT = EMAIL_CONFIG['EMAIL_PORT']
EMAIL_HOST_USER = EMAIL_CONFIG['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = EMAIL_CONFIG['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = EMAIL_CONFIG['EMAIL_USE_TLS']
EMAIL_FROM = EMAIL_CONFIG['EMAIL_FROM']

# EMAIL_CONFIG = SECRETS['mailtrap']
# EMAIL_HOST = EMAIL_CONFIG['EMAIL_HOST']
# EMAIL_HOST_USER = EMAIL_CONFIG['EMAIL_HOST_USER']
# EMAIL_HOST_PASSWORD = EMAIL_CONFIG['EMAIL_HOST_PASSWORD']
# EMAIL_PORT = EMAIL_CONFIG['EMAIL_PORT']

################################################################################
# Celery settings
#

CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = False
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
