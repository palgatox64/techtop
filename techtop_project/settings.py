from pathlib import Path
import os
import platform
from dotenv import load_dotenv
load_dotenv()  

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-zmwjx@35r3hbyyzn$rc0^(2!0vptp3ttzac=bo5%9d-gh0&jb2'

# Detectar sistema operativo
IS_LINUX = platform.system() == 'Linux'
IS_WINDOWS = platform.system() == 'Windows'

# Configuración según entorno
DEBUG = os.getenv('DEBUG', 'False') == 'True'
PRODUCTION = os.getenv('PRODUCTION', 'False') == 'True'

ALLOWED_HOSTS = ['techtop.warevision.net', 'www.techtop.warevision.net', 'localhost', '127.0.0.1']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
    'storages',
    'meta',  # django-meta para SEO
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Debe estar después de SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'techtop_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'store.context_processors.menu_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'techtop_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'Connection Timeout=60;Login Timeout=60;',
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

USE_TZ = True
TIME_ZONE = 'America/Santiago'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuración para encontrar archivos estáticos
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Configuración de WhiteNoise para servir archivos estáticos en producción
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Azure Blob Storage Configuration (solo para archivos de media)
AZURE_ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = os.getenv('AZURE_STORAGE_KEY')
AZURE_CONTAINER = os.getenv('AZURE_CONTAINER')

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.azure_storage.AzureStorage",
        "OPTIONS": {
            "account_name": AZURE_ACCOUNT_NAME,
            "account_key": AZURE_ACCOUNT_KEY,
            "azure_container": AZURE_CONTAINER,
            "timeout": 20,
            "expiration_secs": 500,
        },
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Transbank WebPay Plus Configuration
TRANSBANK_COMMERCE_CODE = os.getenv('TRANSBANK_COMMERCE_CODE', '597055555532')  # Código de comercio de prueba
TRANSBANK_API_KEY = os.getenv('TRANSBANK_API_KEY', '579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C')  # API Key de prueba
TRANSBANK_ENVIRONMENT = os.getenv('TRANSBANK_ENVIRONMENT', 'INTEGRACION')  # INTEGRACION o PRODUCCION

# Mercado Pago Configuration
MERCADOPAGO_ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN', 'TEST-4660967168423158-102716-610c5f083948a0ce493719033f911bd3-835057213')  # Access Token de prueba
MERCADOPAGO_PUBLIC_KEY = os.getenv('MERCADOPAGO_PUBLIC_KEY', 'TEST-b729921c-1996-4f1a-9f68-0785f2d67619')  # Public Key de prueba
MERCADOPAGO_ENVIRONMENT = os.getenv('MERCADOPAGO_ENVIRONMENT', 'TEST')  # TEST o PRODUCTION

# Configuración de Email con Amazon SES
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('AWS_SES_EMAIL_HOST')
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('AWS_SES_SMTP_USER')
EMAIL_HOST_PASSWORD = os.getenv('AWS_SES_SMTP_PASSWORD')
DEFAULT_FROM_EMAIL = 'tienda-techtop@warevision.net'  # Usar el dominio verificado en SES
SERVER_EMAIL = DEFAULT_FROM_EMAIL

SITE_URL = os.getenv('SITE_URL', 'http://localhost:8000')

# Configuración de seguridad para HTTPS (solo en producción)
if PRODUCTION:
    SECURE_SSL_REDIRECT = False  # Cloudflare Tunnel maneja SSL
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Configuración para confiar en los headers de proxy de Cloudflare
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True
    USE_X_FORWARDED_PORT = True
    
    CSRF_TRUSTED_ORIGINS = [
        'https://techtop.warevision.net', 
        'https://www.techtop.warevision.net'
    ]
else:
    # Configuración para desarrollo
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000'
    ]

# Logging para debug en Linux
if IS_LINUX:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'debug.log'),
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
            },
            'django.staticfiles': {
                'handlers': ['console', 'file'],
                'level': 'DEBUG',
            },
        },
    }

# Configuración de Meta Tags SEO    
META_SITE_PROTOCOL = 'https' if PRODUCTION else 'http'
META_SITE_DOMAIN = 'techtop.warevision.net' if PRODUCTION else 'localhost:8000'
META_SITE_TYPE = 'website'
META_SITE_NAME = 'Techtop'
META_INCLUDE_KEYWORDS = ['techtop', 'tecnología', 'radio android', 'auto', 'electrónica', 'chile']
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True
META_USE_SCHEMAORG_PROPERTIES = True