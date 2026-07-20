import os
import threading
from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        if os.environ.get('RENDER'):
            thread = threading.Thread(target=self._run_setup)
            thread.daemon = True
            thread.start()

    def _run_setup(self):
        import sys
        try:
            from django.core.management import call_command
            from django.contrib.sites.models import Site
            from django.contrib.auth import get_user_model

            call_command('migrate', '--noinput', verbosity=0)

            site, _ = Site.objects.get_or_create(id=1, defaults={
                'domain': os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost'),
                'name': 'SMS Pro',
            })
            site.domain = os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost')
            site.name = 'SMS Pro'
            site.save()

            User = get_user_model()
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@smspro.com',
                    password='admin123',
                )
                print('Admin user created: admin / admin123')
        except Exception as e:
            print(f'Auto setup error: {e}', file=sys.stderr)
