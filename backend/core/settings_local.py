from .settings import *

# Configurações para desenvolvimento local (fora do Docker)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "conectades",
        "USER": "admin_conectades",
        "PASSWORD": "conectaZ0Z6@",
        "HOST": "localhost",  # localhost em vez de "db"
        "PORT": 5433,   # porta externa do container
        "CONN_MAX_AGE": 600,
    }
}

# Desabilitar Redis para desenvolvimento local
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Session configuration para desenvolvimento local
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
