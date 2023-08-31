# Create your tests here.
from django.test import TestCase
from django.utils import timezone

from shared.utils.json.serializer import serialize, serialize_as_raw_dict
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
