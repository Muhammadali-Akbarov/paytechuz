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

    def ready(self):
        """
        Initialize the app.
        """
        # Import signals
        try:
            import paytechuz.integrations.django.signals  # noqa
        except ImportError:
            pass
