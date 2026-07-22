from django.conf import settings


def turnstile_context(request):
    return {
        'TURNSTILE_SITE_KEY': getattr(settings, 'TURNSTILE_SITE_KEY', ''),
    }
