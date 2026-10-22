"""Tests for social login (Google / Apple).

Token-verification tests generate a real RSA keypair and sign real RS256 ID
tokens locally, then swap in a fake JWKS client so nothing ever hits the
network. Endpoint tests mock the verifier and exercise account creation,
account linking, and error paths on POST /api/v1/auth/social/.
"""
import time
from types import SimpleNamespace
from unittest import mock

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.customers.models import CustomerProfile

from .models import User
from .social import (
    SocialTokenError,
    verify_apple_id_token,
    verify_google_id_token,
    verify_social_token,
)

# ------------------------------------------------------------------ #
# Local RSA keys + fake JWKS client (no network in tests)
# ------------------------------------------------------------------ #
PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PUBLIC_KEY = PRIVATE_KEY.public_key()

OTHER_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)

GOOGLE_AUD = 'google-test-client.apps.googleusercontent.com'
APPLE_AUD = 'com.example.trashhood.services'

NOW = int(time.time())


class FakeJWKClient:
    """Drop-in replacement for jwt.PyJWKClient that serves a fixed key."""

    def __init__(self, uri, **kwargs):
        self.uri = uri

    def get_signing_key_from_jwt(self, token):
        return SimpleNamespace(key=PUBLIC_KEY)


def make_token(claims, key=PRIVATE_KEY):
    return jwt.encode(claims, key, algorithm='RS256')


def google_claims(**overrides):
    claims = {
        'sub': 'google-user-123',
        'iss': 'accounts.google.com',
        'aud': GOOGLE_AUD,
        'iat': NOW,
        'exp': NOW + 3600,
        'email': 'jane.doe@example.com',
        'email_verified': True,
    }
    claims.update(overrides)
    return claims


def apple_claims(**overrides):
    claims = {
        'sub': 'apple-user-0001',
        'iss': 'https://appleid.apple.com',
        'aud': APPLE_AUD,
        'iat': NOW,
        'exp': NOW + 3600,
        'email': 'apple.user@example.com',
    }
    claims.update(overrides)
    return claims


class JWSPatchedMixin:
    """Route PyJWKClient through the local fake key in every test."""

    def setUp(self):
        super().setUp()
        patcher = mock.patch('apps.accounts.social.PyJWKClient', FakeJWKClient)
        patcher.start()
        self.addCleanup(patcher.stop)


# ------------------------------------------------------------------ #
# Google ID token verification
# ------------------------------------------------------------------ #
@override_settings(GOOGLE_CLIENT_ID=GOOGLE_AUD)
class GoogleTokenVerificationTests(JWSPatchedMixin, SimpleTestCase):
    def test_valid_token_returns_claims(self):
        claims = verify_google_id_token(make_token(google_claims()))
        self.assertEqual(claims['sub'], 'google-user-123')
        self.assertEqual(claims['email'], 'jane.doe@example.com')

    def test_accepts_accounts_google_com_issuer_variant(self):
        claims = verify_google_id_token(
            make_token(google_claims(iss='https://accounts.google.com'))
        )
        self.assertEqual(claims['sub'], 'google-user-123')

    def test_expired_token_rejected(self):
        token = make_token(google_claims(iat=NOW - 7200, exp=NOW - 3600))
        with self.assertRaises(SocialTokenError):
            verify_google_id_token(token)

    def test_wrong_audience_rejected(self):
        token = make_token(google_claims(aud='someone-else.example'))
        with self.assertRaises(SocialTokenError):
            verify_google_id_token(token)

    def test_wrong_issuer_rejected(self):
        token = make_token(google_claims(iss='evil.example'))
        with self.assertRaises(SocialTokenError):
            verify_google_id_token(token)

    def test_signature_signed_by_unknown_key_rejected(self):
        token = make_token(google_claims(), key=OTHER_PRIVATE_KEY)
        with self.assertRaises(SocialTokenError):
            verify_google_id_token(token)

    def test_token_without_sub_rejected(self):
        claims = google_claims()
        del claims['sub']
        with self.assertRaises(SocialTokenError):
            verify_google_id_token(make_token(claims))

    def test_garbage_token_rejected(self):
        with self.assertRaises(SocialTokenError):
            verify_google_id_token('not.a.jwt')


@override_settings(GOOGLE_CLIENT_ID='')
class UnconfiguredGoogleClientTests(JWSPatchedMixin, SimpleTestCase):
    def test_missing_client_id_rejected_before_verification(self):
        with self.assertRaises(SocialTokenError) as ctx:
            verify_google_id_token(make_token(google_claims()))
        self.assertIn('not configured', str(ctx.exception))


# ------------------------------------------------------------------ #
# Apple ID token verification
# ------------------------------------------------------------------ #
@override_settings(APPLE_CLIENT_ID=APPLE_AUD)
class AppleTokenVerificationTests(JWSPatchedMixin, SimpleTestCase):
    def test_valid_token_returns_claims(self):
        claims = verify_apple_id_token(make_token(apple_claims()))
        self.assertEqual(claims['sub'], 'apple-user-0001')

    def test_expired_token_rejected(self):
        token = make_token(apple_claims(iat=NOW - 7200, exp=NOW - 3600))
        with self.assertRaises(SocialTokenError):
            verify_apple_id_token(token)

    def test_wrong_audience_rejected(self):
        token = make_token(apple_claims(aud='com.other.app'))
        with self.assertRaises(SocialTokenError):
            verify_apple_id_token(token)

    def test_wrong_issuer_rejected(self):
        token = make_token(apple_claims(iss='https://evil.example'))
        with self.assertRaises(SocialTokenError):
            verify_apple_id_token(token)


class ProviderDispatchTests(SimpleTestCase):
    def test_unknown_provider_rejected(self):
        with self.assertRaises(SocialTokenError) as ctx:
            verify_social_token('facebook', 'tok')
        self.assertIn('Unsupported provider', str(ctx.exception))

    def test_dispatches_to_matching_verifier(self):
        google = mock.Mock(return_value={'sub': 'g'})
        apple = mock.Mock(return_value={'sub': 'a'})
        # verify_social_token dispatches through the VERIFIERS dict, whose
        # entries are bound at import time, so patch the dict itself.
        with mock.patch.dict('apps.accounts.social.VERIFIERS',
                             {'google': google, 'apple': apple}):
            self.assertEqual(verify_social_token('google', 't1'), {'sub': 'g'})
            self.assertEqual(verify_social_token('apple', 't2'), {'sub': 'a'})
            google.assert_called_once_with('t1')
            apple.assert_called_once_with('t2')


# ------------------------------------------------------------------ #
# POST /api/v1/auth/social/
# ------------------------------------------------------------------ #
class SocialLoginEndpointTests(APITestCase):
    def setUp(self):
        patcher = mock.patch('apps.accounts.views.verify_social_token')
        self.verify = patcher.start()
        self.addCleanup(patcher.stop)
        self.url = reverse('social-login')

    @staticmethod
    def google_payload():
        return {
            'sub': 'google-user-123',
            'iss': 'accounts.google.com',
            'aud': GOOGLE_AUD,
            'email': 'jane.doe@example.com',
        }

    def post_social(self, **data):
        return self.client.post(self.url, data, format='json')

    def test_new_google_user_is_created_and_tokens_returned(self):
        self.verify.return_value = self.google_payload()
        before = User.objects.count()

        response = self.post_social(provider='google', id_token='tok')

        self.assertEqual(response.status_code, 200)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertEqual(User.objects.count(), before + 1)

        user = User.objects.get(social_provider='google',
                                social_sub='google-user-123')
        self.assertTrue(user.is_verified)
        self.assertEqual(user.email, 'jane.doe@example.com')
        self.assertFalse(user.has_usable_password())
        self.assertEqual(str(user.id), response.data['user']['id'])
        # Default role is CUSTOMER → a profile must exist.
        self.assertTrue(CustomerProfile.objects.filter(user=user).exists())

    def test_second_login_reuses_the_same_account(self):
        self.verify.return_value = self.google_payload()

        first = self.post_social(provider='google', id_token='tok')
        second = self.post_social(provider='google', id_token='tok')

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.data['user']['id'], second.data['user']['id'])
        self.assertEqual(
            User.objects.filter(social_provider='google',
                                social_sub='google-user-123').count(),
            1,
        )

    def test_links_to_existing_phone_account_by_email(self):
        existing = User.objects.create_user(
            phone_number='+911234567890',
            email='linked@example.com',
        )
        self.verify.return_value = dict(self.google_payload(),
                                        email='LINKED@example.com')

        response = self.post_social(provider='google', id_token='tok')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['user']['id'], str(existing.id))
        existing.refresh_from_db()
        self.assertEqual(existing.social_provider, 'google')
        self.assertEqual(existing.social_sub, 'google-user-123')
        self.assertEqual(User.objects.count(), 1)

    def test_apple_first_and_last_name_saved_on_first_login(self):
        self.verify.return_value = {'sub': 'apple-user-0001',
                                    'email': 'apple.user@example.com'}

        response = self.post_social(provider='apple', id_token='tok',
                                    first_name='Ada', last_name='Lovelace')

        self.assertEqual(response.status_code, 200)
        user = User.objects.get(social_provider='apple',
                                social_sub='apple-user-0001')
        profile = CustomerProfile.objects.get(user=user)
        self.assertEqual(profile.first_name, 'Ada')
        self.assertEqual(profile.last_name, 'Lovelace')

    def test_invalid_token_returns_401(self):
        self.verify.side_effect = SocialTokenError('Invalid ID token: bogus')

        response = self.post_social(provider='google', id_token='bad')

        self.assertEqual(response.status_code, 401)
        self.assertIn('error', response.data)
        self.assertEqual(User.objects.count(), 0)

    def test_unsupported_provider_returns_400(self):
        response = self.post_social(provider='facebook', id_token='tok')
        self.assertEqual(response.status_code, 400)

    def test_missing_id_token_returns_400(self):
        response = self.post_social(provider='google')
        self.assertEqual(response.status_code, 400)
