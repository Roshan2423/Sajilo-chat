from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models.signals import post_migrate

class Command(BaseCommand):
    help = 'Disables signals during migration.'

    def handle(self, *args, **kwargs):
        # Disconnect the post_migrate signal to avoid issues
        post_migrate.disconnect(dispatch_uid='django.contrib.sites.management.create_default_site')

        # Optional: Add custom logic here for migration handling
        self.stdout.write(self.style.SUCCESS('Post-migrate signal disabled for site creation.'))

        # Run the necessary migrations
        with connection.schema_editor() as schema_editor:
            schema_editor.execute("YOUR SQL COMMANDS HERE")

        self.stdout.write(self.style.SUCCESS('Custom migration commands executed.'))
