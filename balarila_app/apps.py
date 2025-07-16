from django.apps import AppConfig


class BalarilaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'balarila_app'

    def ready(self):
        # Import the model loading function here to avoid circular imports
        # as models might depend on app registry.
        from .utils import get_gec_model

        # Call the function to load the model
        # This will load the model into _model_cache when the app is ready.
        try:
            get_gec_model()
        except ValueError as e:
            # Handle case where BALARILA_GEC_MODEL_PATH might not be set
            print(f"Warning: Could not pre-load GEC model during app startup: {e}")
            print("Make sure BALARILA_GEC_MODEL_PATH is set as an environment variable.")
        except Exception as e:
            # Error handling if the model fails to load
            print(f"Error pre-loading GEC model during app startup: {e}")