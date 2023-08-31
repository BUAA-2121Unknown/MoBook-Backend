# Create your tests here.
import json
import pickle

from django.test import TestCase
from django.utils import timezone

from shared.utils.json.serializer import serialize, serialize_as_raw_dict
from shared.utils.token.base64_token import to_base64_token, from_base64_token
from user.dtos.user_dto import UserDto
from user.models import User, UserOrganizationRecord


class Test:
    def __init__(self):
        self.timestamp = timezone.now()


class JsonTestCase(TestCase):
    def test_json(self):
        test = Test()
        print(test.timestamp)
        print(serialize(test))
        print(serialize_as_raw_dict(test))


class UserOrgRecordTestCase(TestCase):
    def test_user_org_record(self):
        users = User.objects.all()
        for user in users:
            record = UserOrganizationRecord.create(user.id, 0)
            record.save()
            print(record.id)


class CacheTestCase(TestCase):
    def test_pickle(self):
        user = User.create("test", "password", "123@qq.com", True)
        if user is None:
            print("No user")
        user_pickle = pickle.dumps(user)
        print(f"pickle: {user_pickle}")
        user_unpickle = pickle.loads(user_pickle)
        print(user_unpickle)
        print(f"unpickle: {json.dumps(serialize_as_raw_dict(UserDto(user_unpickle)), indent=4)}")

    def test_cache(self):
        pass


class TokenTestCase(TestCase):
    def test_token(self):
        string = "12345678901234567"
        token = to_base64_token(string)
        print(token)
        string = from_base64_token(token)
        print(string)
