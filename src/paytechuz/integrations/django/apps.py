"""
Django app configuration for PayTechUZ.
"""
from django.apps import AppConfig


class PaytechuzConfig(AppConfig):
    """
    Django app configuration for PayTechUZ.
    """
    name = 'paytechuz.integrations.django'
    verbose_name = 'PayTechUZ'

    # This is important - it tells Django to use our migrations
    # but not to create new ones automatically
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        """
        Initialize the app.
        """
        # Import signals
        try:
            import paytechuz.integrations.django.signals  # noqa
        except ImportError:
            pass
