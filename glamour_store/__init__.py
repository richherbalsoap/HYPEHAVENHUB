try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery is not installed in the current environment
    pass
