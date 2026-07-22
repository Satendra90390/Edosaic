import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_django.settings')

import django
django.setup()

from django.core.management import call_command
call_command('migrate', '--noinput')

from django.contrib.sites.models import Site
Site.objects.get_or_create(id=1, defaults={
    'domain': os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost'),
    'name': 'Edosaic',
})

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
