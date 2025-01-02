"""
Django settings for clickessms_backend project.

Generated by 'django-admin startproject' using Django 3.2.22.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-*e73@q%+sv9z^ec(%)fo3=_2_)@mt%z=$1!%5o+ln&2lqc11wm'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles', # Required for GraphiQL
    'corsheaders',
    'daphne',
    'channels',
    'graphene_django',
    'graphql_jwt.refresh_token.apps.RefreshTokenConfig',
    'graphql_auth',
    'django_filters',
    # Mes applications
    'data_management',
    'accounts',
    'medias',
    'searching',
    'dashboard',
    'companies',
    'human_ressources',
    'stocks',
    'computers',
    'vehicles',
    'partnerships',
    'sales',
    'purchases',
    'works',
    'feedbacks',
    'notifications',
    'chat',
    'loan_management',
    'activities',
    'qualities',
    'administratives',
    'finance',
    'governance',
    'sce',
    'blog',
    'planning',
    'building_estate',
    'robert_ia'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'clickessms_backend.middlewares.auth_middlewares.JWTAuthenticationMiddleware'
]

ROOT_URLCONF = 'clickessms_backend.urls'

#cors
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "Apollographql-Client-Name",
    "Apollographql-Client-Version",
    "Referer",
    "Sec-Ch-Ua",
    "Sec-Ch-Ua-Mobile",
    "Sec-Ch-Ua-Platform",
    "Set-Cookie"
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'clickessms_backend.wsgi.application'
ASGI_APPLICATION = "clickessms_backend.asgi.application"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

#DEV
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

#PROD
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'roberp_db',
        'USER' : 'roberp',
        'PASSWORD' : 'roberp01/@X',
        'HOST' : 'localhost',
        'PORT' : '',
        'OPTION':{
                'init_command' : "SET sql_mode='STRICT_TRANS_TABLES'"
                }
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = 'public/static/'

MEDIA_ROOT = BASE_DIR / 'public/media'
MEDIA_URL = '/public/media/'
 
AUTH_USER_MODEL = 'accounts.User'

GRAPHENE = {
    'SCHEMA' : 'clickessms_backend.schema.schema',
    'MIDDLEWARE': [
        'graphql_jwt.middleware.JSONWebTokenMiddleware',
    ],
    "SUBSCRIPTION_PATH" :  "/graphql"   # Le chemin que vous avez configuré dans `routing.py`, y compris une barre oblique. 
}

AUTHENTICATION_BACKENDS = [
    'graphql_auth.backends.GraphQLAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

GRAPHQL_JWT = {
    "JWT_ALLOW_ANY_CLASSES": [
        "graphql_auth.mutations.Register",
        "graphql_auth.mutations.VerifyAccount",
        "graphql_auth.mutations.ObtainJSONWebToken",
        "graphql_auth.mutations.VerifyToken",
        "graphql_auth.mutations.RefreshToken",
        "graphql_auth.mutations.RevokeToken",
    ],
    "JWT_VERIFY_EXPIRATION": True,
    "JWT_LONG_RUNNING_REFRESH_TOKEN": True,
    'JWT_EXPIRATION_DELTA': timedelta(days=360),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
}

GRAPHQL_AUTH = {
    # ...
    'REGISTER_MUTATION_FIELDS' : [
    "email", "username",
    "first_name", "last_name",
    "is_cgu_accepted"
    ],
    'REGISTER_MUTATION_FIELDS_OPTIONAL' : [
        # ...
        'first_name',
        'last_name',
        "account_type"
    ]
}

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             # Configuration Redis (par exemple : "redis://localhost:6379/1")
#             "hosts": [("localhost", 6379)],
#         },
#     },
# }

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FCM_KEY = "AAAAcZ-1XUU:APA91bG4oSUn39sLzHC7hEOC87TAgGUSRTDmWPkZR5DQRul-cbw9StMHRXMtHpCpDXrk7Eys5BIhaD2-gCtM2NJutbfpSJL7Y1cbzEzbkGVYXCzrd0FfNqOkiRzO5Gf7ili1yOhV4dpQ"

MONTHS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
DAYS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
