from django.test import TestCase

from shared.utils.email.email import send_activation_email
from shared.utils.email.exception import EmailException
from shared.utils.json.serializer import serialize
from shared.utils.token.jwt_token import generate_jwt_token
from shared.utils.token.refresh_token import generate_refresh_token


# Create your tests here.

class TokenTestCase(TestCase):
    def test_jwt_token(self):
        token = generate_jwt_token(123)
        print(token)

    def test_refresh_token(self):
        refresh_token = generate_refresh_token(123)
        print(serialize(refresh_token))


class EmailTestCase(TestCase):
    def test_email(self):
        try:
            send_activation_email("badge-board@foxmail.com", "www.example.com")
        except EmailException as e:
            print(e)
