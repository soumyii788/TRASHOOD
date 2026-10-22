"""
Social login – verify ID tokens issued by Google and Apple.

Both providers sign their ID tokens with RS256; we verify the signature
against the provider's published JWKS and validate issuer/audience/expiry.
"""
import jwt
from jwt import PyJWKClient
from django.conf import settings

GOOGLE_JWKS_URL = 'https://www.googleapis.com/oauth2/v3/certs'
APPLE_JWKS_URL = 'https://appleid.apple.com/auth/keys'

GOOGLE_ISSUERS = {'accounts.google.com', 'https://accounts.google.com'}
APPLE_ISSUER = 'https://appleid.apple.com'


class SocialTokenError(Exception):
    """Raised when an ID token fails verification."""


def _decode_with_jwks(id_token, jwks_url, audience, issuers):
    if not audience:
        raise SocialTokenError('Provider client ID is not configured on the server.')
    jwks_client = PyJWKClient(jwks_url, cache_keys=True)
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(id_token).key
        claims = jwt.decode(
            id_token,
            signing_key,
            algorithms=['RS256'],
            audience=audience,
            issuer=issuers if isinstance(issuers, (list, tuple, set)) else issuers,
        )
    except jwt.PyJWTError as exc:
        raise SocialTokenError(f'Invalid ID token: {exc}') from exc
    return claims


def verify_google_id_token(id_token):
    """Verify a Google ID token; returns the decoded claims."""
    claims = _decode_with_jwks(
        id_token,
        GOOGLE_JWKS_URL,
        settings.GOOGLE_CLIENT_ID,
        tuple(GOOGLE_ISSUERS),
    )
    if not claims.get('sub'):
        raise SocialTokenError('Token missing subject (sub).')
    return claims


def verify_apple_id_token(id_token):
    """Verify an Apple ID token; returns the decoded claims.

    Apple may withhold the email on subsequent sign-ins unless the scope
    was granted; sub is always present and stable per (user, client).
    """
    claims = _decode_with_jwks(
        id_token,
        APPLE_JWKS_URL,
        settings.APPLE_CLIENT_ID,
        APPLE_ISSUER,
    )
    if not claims.get('sub'):
        raise SocialTokenError('Token missing subject (sub).')
    return claims


VERIFIERS = {
    'google': verify_google_id_token,
    'apple': verify_apple_id_token,
}


def verify_social_token(provider, id_token):
    """Verify an ID token for the given provider ('google' | 'apple')."""
    verifier = VERIFIERS.get(provider)
    if verifier is None:
        raise SocialTokenError(f'Unsupported provider: {provider}')
    return verifier(id_token)
