import os
from pathlib import Path
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def validate_env(env_name, default=None, blank=False, bool=False, redact=True):
    declared_env = os.getenv(env_name)
    if not blank and not declared_env and default is None:
        raise ValueError(
            f"Environment variable {env_name} is not set and no default value provided."
        )
    if not blank and not declared_env:
        logger.warning(
            f"Environment variable {env_name} is not set. Using default value if provided."
        )
    if bool and declared_env:
        declared_env = declared_env.lower() == "true"
    if not redact and declared_env:
        logger.info(f"Environment variable {env_name} declared: {declared_env}")
    elif not redact:
        logger.info(f"Environment variable {env_name} validated: {default}")
    else:
        logger.info(f"Environment variable {env_name} validated: **********")
    return declared_env if declared_env is not None else default


DEBUG = True
BASE_DIR = Path(__file__).resolve().parent.parent
PROD = validate_env("PROD", default=False, bool=True)
if not PROD:
    load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".dev", ".env"), override=True)

SECRET_KEY = validate_env("SECRET_KEY")
ALLOWED_HOSTS = [validate_env("ALLOWED_HOST", default="localhost:8000", redact=False)]
STATICFILES_DIRS = [
    validate_env("STATIC_DIR", default=os.path.join(BASE_DIR, "static/"), redact=False)
]
MEDIA_ROOT = validate_env("MEDIA_ROOT", default=os.path.join(BASE_DIR, "media"), redact=False)
DB_PATH = validate_env("DB_PATH", default=os.path.join(BASE_DIR, "db.sqlite3"), redact=False)
SITE_URL = validate_env("SITE_URL", default="loclahost:8000", redact=False)
STATIC_URL = validate_env("STATIC_URL", default="/static/", redact=False)
MEDIA_URL = validate_env("MEDIA_URL", default="/media/", redact=False)

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
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": DB_PATH}}
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
