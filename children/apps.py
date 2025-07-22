from django.apps import AppConfig

class ChildrenConfig(AppConfig):
    name = 'children'

    def ready(self):
        # Import here to register the OpenApiAuthenticationExtension class
        import children.authentication
