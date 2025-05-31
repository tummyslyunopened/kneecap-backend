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
MEDIA_ROOT = validate_env("MEDIA_ROOT", default=os.path.join(BASE_DIR, "media"), redact=False)
DB_PATH = validate_env("DB_PATH", default=os.path.join(BASE_DIR, "db.sqlite3"), redact=False)
SITE_URL = validate_env("SITE_URL", default="localhost:8000", redact=False)
TRANSCRIPTION_SERVICE_HOST = validate_env("TRANSCRIPTION_SERVICE_HOST", blank=True, redact=False)
TRANSCRIPTION_THREADS = int(validate_env("TRANSCRIPTION_THREADS", default=1, redact=False))
LOW_QUALITY_THREADS = int(validate_env("LOW_QUALITY_THREADS", default=1, redact=False))

LLM_ENDPOINT = validate_env("LLM_ENDPOINT", blank=True, redact=False)
# Use lemon24/reader for feed fetching/parsing if set to True
USE_READER_BACKEND = validate_env("USE_READER_BACKEND", default=False, bool=True)

# Path for lemon24/reader database
READER_DB_PATH = validate_env(
    "READER_DB_PATH", default=os.path.join(BASE_DIR, "reader.db"), redact=False
)

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static/")
]  # validate_env("STATIC_DIR", default=os.path.join(BASE_DIR, "static/"), redact=False)
ALLOWED_HOSTS = [
    SITE_URL
]  # [validate_env("ALLOWED_HOST", default="localhost:8000", redact=False)]
STATIC_URL = "/static/"  # validate_env("STATIC_URL", default="/static/", redact=False)
MEDIA_URL = "/media/"  # validate_env("MEDIA_URL", default="/media/", redact=False)

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "solo",
    "rest_framework",
    "tools",
    "throttle",
    "subscriptions",
    "rss",
    "dashboard",
    "opml",
    "player",
    "transcripts",
    "ad_detect",
    "feeds",
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

# Add or update the LOGGING configuration to show INFO-level logs for the opml app
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "opml": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "transcripts": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "subscriptions": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "rss": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
