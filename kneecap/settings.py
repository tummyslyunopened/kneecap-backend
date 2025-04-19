from pathlib import Path
import os
from dotenv import load_dotenv

PROD = os.getenv("PROD") == "True"
if not PROD: 
    load_dotenv()

DEBUG = os.getenv("DEBUG") == "True"
SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_HOSTS = [os.getenv("ALLOWED_HOST")]
STATIC_DIR = os.getenv("STATIC_DIR")
MEDIA_ROOT = os.getenv("MEDIA_DIR")
DB_PATH = os.getenv("DB_PATH")

BASE_DIR = Path(__file__).resolve().parent.parent

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "solo",
    "rest_framework",
    "tools",
    "subscriptions",
    "rss",
    "dashboard",
    "opml",
    "player",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "kneecap.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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
WSGI_APPLICATION = "kneecap.wsgi.application"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

SITE_URL = os.getenv("SITE_URL")
STATIC_URL = "/static/"

if STATIC_DIR: 
    STATICFILES_DIRS = [
        STATIC_DIR
    ]
else:
    STATICFILES_DIRS = [
        BASE_DIR / "static",
    ]
if not MEDIA_ROOT:
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
MEDIA_URL = "/media/"

