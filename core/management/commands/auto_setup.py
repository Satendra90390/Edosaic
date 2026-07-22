import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Run migrations, create site, and ensure site configuration'

    def handle(self, *args, **options):
        self.stdout.write('Running migrations...')
        call_command('migrate', '--noinput')

        self.stdout.write('Ensuring site exists...')
        site, _ = Site.objects.get_or_create(
            id=1,
            defaults={
                'domain': os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost'),
                'name': 'Edosaic',
            }
        )
        site.domain = os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost')
        site.name = 'Edosaic'
        site.save()

        self.stdout.write(self.style.SUCCESS('Site setup complete. Create admin via: python manage.py createsuperuser'))
