from django.apps import AppConfig


class MatchmakingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'matchmaking'

    # Spécifiez le chemin des migrations
    migrations_module = 'database.migrations'