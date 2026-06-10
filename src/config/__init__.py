"""Carga la app de Celery al importar config (setup canónico Django+Celery).

Sin esto, los @shared_task usados desde el proceso web/tests se atan a un app
de Celery sin configurar (broker amqp por defecto, sin modo eager).
"""

from .celery import app as celery_app

__all__ = ("celery_app",)
