from django.apps import AppConfig


class PaieConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'paie'  # ← Cette ligne était manquante ou mal placée
    
    def ready(self):
        import paie.audit  # Charger les signaux d'audit