from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from django.apps import apps

class Command(BaseCommand):
    help = 'Initialize content types for all models'

    def handle(self, *args, **options):
        # Get all models from the inventory app
        app_config = apps.get_app_config('inventory')
        
        for model in app_config.get_models():
            ContentType.objects.get_or_create(
                app_label='inventory',
                model=model._meta.model_name
            )
            self.stdout.write(f'Created content type for {model._meta.model_name}')

        self.stdout.write(self.style.SUCCESS('Successfully created all content types'))