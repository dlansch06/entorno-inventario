from django.apps import AppConfig


class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventario'
    label ='portal_institucional'
    verbose_name = "Portal Institucional"
    def ready(self):
        import inventario.signals
