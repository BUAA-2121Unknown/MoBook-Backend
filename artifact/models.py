from django.db import models
from treebeard.mp_tree import MP_Node

from shared.utils.model.model_extension import Existence


# Create your models here.

class ItemType:
    ROOT = 0
    DIRECTORY = 1
    FILE = 2

    @classmethod
    def all(cls):
        return [cls.ROOT, cls.DIRECTORY, cls.FILE]

    @classmethod
    def dirs(cls):
        return [cls.ROOT, cls.DIRECTORY]

    @classmethod
    def files(cls):
        return [cls.FILE]


class ItemProperty:
    FOLDER = 0
    DOCUMENT = 1
    PROTOTYPE = 2
    TEMPLATE = 3

    @classmethod
    def all(cls):
        return [cls.FOLDER, cls.DOCUMENT, cls.PROTOTYPE, cls.TEMPLATE]

    @classmethod
    def dirs(cls):
        return [cls.FOLDER]

    @classmethod
    def files(cls):
        return [cls.DOCUMENT, cls.PROTOTYPE, cls.TEMPLATE]


class Item(MP_Node):
    # fields for tree model

    # name include name and extension
    name = models.CharField(max_length=127, default="")
    extension = models.CharField(max_length=31, default="")

    type = models.SmallIntegerField()  # ItemType
    prop = models.SmallIntegerField()  # ItemProperty

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    status = models.SmallIntegerField(default=Existence.ACTIVE)

    live = models.BooleanField(default=False)

    # last version
    version = models.IntegerField(default=1)
    total_version = models.IntegerField(default=1)

    # extra fields
    proj_id = models.BigIntegerField()
    org_id = models.BigIntegerField()
    user_id = models.BigIntegerField()  # creator

    file_id = models.SmallIntegerField(default=0)  # only valid when property is not FOLDER

    node_order_by = ['type', 'name']

    def is_active(self):
        return self.status == Existence.ACTIVE

    def is_dir(self):
        return self.type in ItemType.dirs()

    def is_file(self):
        return not self.is_dir()

    def get_filename(self):
        return f"{self.name}{self.extension}"

    class Meta:
        db_table = 'artifact_item'
        verbose_name = 'item'


class FileVersion(models.Model):
    version = models.IntegerField()

    file_id = models.BigIntegerField()
    user_id = models.BigIntegerField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, version, file_id, user_id):
        return cls(version=version, file_id=file_id, user_id=user_id)

    class Meta:
        db_table = 'artifact_file_version'
        verbose_name = 'file version'
