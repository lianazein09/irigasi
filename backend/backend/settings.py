from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def load_env_file(env_path):
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


for candidate in (BASE_DIR.parent / '.env', BASE_DIR.parent / '.env.production', BASE_DIR / '.env'):
    load_env_file(candidate)


def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def get_database_config():
    engine_name = os.environ.get('DB_ENGINE', 'postgresql').strip().lower()
    if engine_name == 'postgres':
        engine_name = 'postgresql'

    common_config = {
        'NAME': os.environ.get('DB_NAME', 'tani_cerdas'),
        'USER': os.environ.get('DB_USER', 'postgres' if engine_name == 'postgresql' else 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '5432' if engine_name == 'postgresql' else '3307'),
    }

    if engine_name == 'postgresql':
        return {
            'ENGINE': 'django.db.backends.postgresql',
            **common_config,
        }

    if engine_name == 'mysql':
        import pymysql
        pymysql.install_as_MySQLdb()
        import MySQLdb
        MySQLdb.version_info = (2, 2, 1, "final", 0)

        # Preserve the MariaDB/MySQL compatibility behavior used by the legacy app.
        from django.db.backends.base.base import BaseDatabaseWrapper
        from django.db.backends.mysql.features import DatabaseFeatures

        BaseDatabaseWrapper.check_database_version_supported = lambda self: None
        DatabaseFeatures.can_return_columns_from_insert = property(lambda self: False)
        DatabaseFeatures.can_return_rows_from_bulk_insert = property(lambda self: False)

        return {
            'ENGINE': 'django.db.backends.mysql',
            **common_config,
        }

    raise ValueError("Unsupported DB_ENGINE. Use 'postgresql' or 'mysql'.")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-bs9*ewvgi$j1@d#bz1em@eha)6ofk7=!oi_vf5n%@5x%gzcmhb')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env_bool('DJANGO_DEBUG', True)

ALLOWED_HOSTS = [host.strip() for host in os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',') if host.strip()]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': get_database_config()
}

cors_origins = [origin.strip() for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if origin.strip()]
CORS_ALLOW_ALL_ORIGINS = env_bool('CORS_ALLOW_ALL_ORIGINS', DEBUG or not cors_origins)
CORS_ALLOWED_ORIGINS = cors_origins
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.environ.get('TIME_ZONE', 'UTC')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MQTT Configuration
MQTT_BROKER_HOST = os.environ.get('MQTT_BROKER_HOST', 'broker.emqx.io')
MQTT_BROKER_PORT = int(os.environ.get('MQTT_BROKER_PORT', 1883))
MQTT_ENABLED = env_bool('MQTT_ENABLED', True)
DEVICE_API_KEY = os.environ.get('DEVICE_API_KEY', '')
# MQTT_USERNAME = 'your_username'
# MQTT_PASSWORD = 'your_password'
