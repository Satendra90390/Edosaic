import requests
from django.conf import settings


def verify_turnstile(token, remote_ip=None):
    """Verify a Cloudflare Turnstile token. Returns True if valid."""
    secret_key = getattr(settings, 'TURNSTILE_SECRET_KEY', '')
    if not secret_key:
        return True

    if not token:
        return False

    payload = {
        'secret': secret_key,
        'response': token,
    }
    if remote_ip:
        payload['remoteip'] = remote_ip

    try:
        resp = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data=payload,
            timeout=5,
        )
        result = resp.json()
        return result.get('success', False)
    except Exception:
        return False
