# Create your tests here.
from django.test import TestCase
from django.utils import timezone

from shared.utils.json.serializer import serialize_as_dict, serialize, serialize_as_raw_dict


class Test:
    def __init__(self):
        self.timestamp = timezone.now()


class JsonTestCase(TestCase):
    def test_json(self):
        test = Test()
        print(test.timestamp)
        print(serialize(test))
        print(serialize_as_raw_dict(test))
