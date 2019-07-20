import secrets


def generate_api_key() -> str:
    return secrets.token_urlsafe()
