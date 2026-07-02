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
    'store',
]
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
if HAS_WHITENOISE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
if HAS_CORSHEADERS:
    MIDDLEWARE.insert(3 if HAS_WHITENOISE else 2, 'corsheaders.middleware.CorsMiddleware')

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
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='resend')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='re_RPhraYhb_ER8RYYQUVB46AcVQafEjASxF')
EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default=(
        'django.core.mail.backends.smtp.EmailBackend'
        if EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
        else 'django.core.mail.backends.console.EmailBackend'
    )
)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=20, cast=int)
DEFAULT_FROM_EMAIL = config(
    'DEFAULT_FROM_EMAIL',
    default='noreply@hypehavenhub.in'
)

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

# Cloudflare R2 Storage Configuration
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', default='')
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default='')

if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY and AWS_STORAGE_BUCKET_NAME:
    # Use STORAGES for Django 4.2+
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False # Public URLs
    AWS_S3_REGION_NAME = 'auto' # Required for Cloudflare R2
    if AWS_S3_CUSTOM_DOMAIN:
        AWS_S3_CUSTOM_DOMAIN = AWS_S3_CUSTOM_DOMAIN.replace('https://', '').replace('http://', '').strip('/')

