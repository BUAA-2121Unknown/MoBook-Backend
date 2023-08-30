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

    @classmethod
    def all(cls):
        return [cls.FOLDER, cls.DOCUMENT, cls.PROTOTYPE]


class Item(MP_Node):
    # fields for tree model

    # name include name and extension
    name = models.CharField(max_length=127)
    type = models.SmallIntegerField()  # ItemType
    prop = models.SmallIntegerField()  # ItemProperty

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    status = models.SmallIntegerField(default=Existence.ACTIVE)

    # extra fields
    proj_id = models.BigIntegerField()
    org_id = models.BigIntegerField()

    file_id = models.SmallIntegerField(default=0)  # only valid when property is not FOLDER

    node_order = ['name']

    class Meta:
        db_table = 'artifact_item'
        verbose_name = 'item'


class FileItem(models.Model):
    """
    A file item should only be obtained through item.
    """
    # whether support live share or not
    live = models.BooleanField(default=False)

    # last version
    version = models.IntegerField(default=1)

    # created and updated fields are automatically set by Django
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, label, live):
        return cls(label=label, live=live)

    class Meta:
        db_table = 'artifact_file_item'
        verbose_name = 'file item'


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
