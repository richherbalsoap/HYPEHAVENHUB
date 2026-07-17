import os
from pathlib import Path
from importlib.util import find_spec

try:
    from decouple import config as decouple_config
except ImportError:
    def config(key, default=None, cast=None):
        value = os.environ.get(key, default)
        if cast is None:
            return value
        if cast is bool:
            if isinstance(value, bool):
                return value
            return str(value).strip().lower() in {'1', 'true', 't', 'yes', 'y', 'on'}
        return cast(value)
else:
    config = decouple_config


def module_available(module_name):
    return find_spec(module_name) is not None


HAS_CORSHEADERS = module_available('corsheaders')
HAS_WHITENOISE = module_available('whitenoise')
HAS_CRISPY_FORMS = module_available('crispy_forms')
HAS_CRISPY_BOOTSTRAP5 = module_available('crispy_bootstrap5')
HAS_REST_FRAMEWORK = module_available('rest_framework')
HAS_SIMPLE_JWT = module_available('rest_framework_simplejwt')
HAS_PSYCOPG = module_available('psycopg2') or module_available('psycopg')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-glamour-store-key-change-in-production')

DEBUG = config('DEBUG', default=False, cast=bool)


ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app', 'https://hypehavenhub.vercel.app']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # allauth apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

    'store',
]

SITE_ID = 1
if HAS_REST_FRAMEWORK:
    INSTALLED_APPS.append('rest_framework')
if HAS_REST_FRAMEWORK and HAS_SIMPLE_JWT:
    INSTALLED_APPS.append('rest_framework_simplejwt')
if HAS_CORSHEADERS:
    INSTALLED_APPS.append('corsheaders')
if HAS_CRISPY_FORMS:
    INSTALLED_APPS.append('crispy_forms')
if HAS_CRISPY_FORMS and HAS_CRISPY_BOOTSTRAP5:
    INSTALLED_APPS.append('crispy_bootstrap5')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'store.middleware.SecurityHeadersMiddleware',
    'store.middleware.RateLimitMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # allauth middleware
    'allauth.account.middleware.AccountMiddleware',
    
    'store.middleware.ExceptionHandlingMiddleware',
]
if HAS_WHITENOISE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
if HAS_CORSHEADERS:
    MIDDLEWARE.insert(4 if HAS_WHITENOISE else 3, 'corsheaders.middleware.CorsMiddleware')

ROOT_URLCONF = 'glamour_store.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.cart_count',
                'store.context_processors.wishlist_count',
                'store.context_processors.categories_list',
                'store.context_processors.company_dashboard_access',
                'store.context_processors.global_country_context',
                'store.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'glamour_store.wsgi.application'

PGDATABASE = config('PGDATABASE', default='')
POSTGRES_URL = (
    config('POSTGRES_URL', default='')
    or config('DATABASE_URL', default='')
    or config('POSTGRES_PRISMA_URL', default='')
)

if POSTGRES_URL and HAS_PSYCOPG:
    # Vercel Postgres (via Neon/Supabase/etc. through the Vercel
    # Marketplace) and most other managed Postgres providers give you a
    # single connection string instead of separate host/user/password
    # vars. dj_database_url parses that reliably (including query-string
    # options like sslmode) instead of us hand-rolling urlparse.
    import dj_database_url

    DATABASES = {
        'default': dj_database_url.parse(
            POSTGRES_URL,
            conn_max_age=0,
            ssl_require=True,
        )
    }
elif PGDATABASE and HAS_PSYCOPG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': PGDATABASE,
            'USER': config('PGUSER', default=''),
            'PASSWORD': config('PGPASSWORD', default=''),
            'HOST': config('PGHOST', default='localhost'),
            'PORT': config('PGPORT', default='5432'),
        }
    }
else:
    # Local development only. NEVER used on Vercel — if you see this
    # branch running in production, POSTGRES_URL / PGDATABASE env vars
    # are missing and nothing you save will persist between deploys.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'store.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_ADAPTER = 'store.adapters.MySocialAccountAdapter'
LOGIN_REDIRECT_URL = '/'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('GOOGLE_CLIENT_ID', default=''),
            'secret': config('GOOGLE_CLIENT_SECRET', default=''),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
if HAS_WHITENOISE:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
# NOTE: product/category images are now stored in Vercel Blob storage
# (see store/storage.py and image_url fields on Category/ProductImage) —
# this MEDIA_ROOT only matters for local development or any leftover
# legacy ImageField uploads, since Vercel's filesystem is wiped on every
# cold start and was never a safe place to keep uploaded files.
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if HAS_CRISPY_FORMS and HAS_CRISPY_BOOTSTRAP5:
    CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
    CRISPY_TEMPLATE_PACK = 'bootstrap5'

CORS_ALLOW_ALL_ORIGINS = True

if HAS_REST_FRAMEWORK:
    auth_classes = [
        'rest_framework.authentication.SessionAuthentication',
    ]
    if HAS_SIMPLE_JWT:
        auth_classes.insert(0, 'rest_framework_simplejwt.authentication.JWTAuthentication')

    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': auth_classes,
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        ],
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 20,
    }

if HAS_SIMPLE_JWT:
    from datetime import timedelta
    SIMPLE_JWT = {
        'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
        'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    }

EMAIL_HOST = config('EMAIL_HOST', default='smtp.resend.com')
_email_port_str = config('EMAIL_PORT', default='587')
EMAIL_PORT = int(_email_port_str) if _email_port_str and _email_port_str.isdigit() else 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='resend')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='re_fSntXRXy_FMc8NsS85SojBvNp94PZDBLR')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)

EMAIL_BACKEND = (
    'django.core.mail.backends.smtp.EmailBackend'
    if EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
    else 'django.core.mail.backends.console.EmailBackend'
)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
_email_timeout_str = config('EMAIL_TIMEOUT', default='20')
EMAIL_TIMEOUT = int(_email_timeout_str) if _email_timeout_str and _email_timeout_str.isdigit() else 20
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@hypehavenhub.in')

TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', default='')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', default='')
TWILIO_FROM_NUMBER = config('TWILIO_FROM_NUMBER', default='')
SMS_TIMEOUT = config('SMS_TIMEOUT', default=15, cast=int)
SITE_URL = config('SITE_URL', default='http://127.0.0.1:8000')

SESSION_COOKIE_AGE = 86400 * 30
SESSION_SAVE_EVERY_REQUEST = True

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Razorpay Configuration
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')

# Shiprocket Configuration
SHIPROCKET_EMAIL = config('SHIPROCKET_EMAIL', default='')
SHIPROCKET_PASSWORD = config('SHIPROCKET_PASSWORD', default='')
SHIPROCKET_API_KEY = config('SHIPROCKET_API_KEY', default='')
SHIPROCKET_PICKUP_LOCATION = config('SHIPROCKET_PICKUP_LOCATION', default='Primary')
SHIPROCKET_CHECKOUT_API_KEY = config('SHIPROCKET_CHECKOUT_API_KEY', default='')
SHIPROCKET_CHECKOUT_SECRET_KEY = config('SHIPROCKET_CHECKOUT_SECRET_KEY', default='')

# Cloudflare R2 Storage Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', default='')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False # Public URLs
    AWS_S3_REGION_NAME = 'auto' # Required for Cloudflare R2
    if AWS_S3_CUSTOM_DOMAIN:
        AWS_S3_CUSTOM_DOMAIN = AWS_S3_CUSTOM_DOMAIN.replace('https://', '').replace('http://', '').strip('/')

# Production Storage settings with WhiteNoise and S3 uploads combined
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage" if (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME) else "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Production Security Headers & HSTS Settings
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = False
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Redis Caching Config (Graceful LocMem fallback for local development)
REDIS_URL = config('REDIS_URL', default='')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
            'KEY_PREFIX': 'hypehaven',
            'TIMEOUT': 3600,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'hypehaven-local-cache',
        }
    }

# Celery Configurations
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=REDIS_URL or 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Production Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
        'store': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Only write to file handler when NOT on Vercel's read-only serverless platform
ON_VERCEL = config('VERCEL', default='') or config('VERCEL_ENV', default='')
if not ON_VERCEL:
    try:
        import os
        os.makedirs(BASE_DIR / 'logs', exist_ok=True)
        
        LOGGING['handlers']['file'] = {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/django_error.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        }
        LOGGING['root']['handlers'].append('file')
        LOGGING['loggers']['django']['handlers'].append('file')
        LOGGING['loggers']['store']['handlers'].append('file')
    except Exception:
        pass


