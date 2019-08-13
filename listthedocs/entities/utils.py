import os
import base64


def generate_api_key() -> str:
    try:
        # Python >= 3.6
        import secrets
        return secrets.token_urlsafe()
    except ImportError:
        # Python 3.5

        return base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('ascii')
