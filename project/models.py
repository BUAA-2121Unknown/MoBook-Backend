from django.db import models

from org.models import Organization
from shared.utils.model.model_extension import first_or_default


# Create your models here.

class Existence:
    ACTIVE = 0
    RECYCLED = 1
    DELETED = 2

    @classmethod
    def all(cls):
        return [cls.ACTIVE, cls.RECYCLED, cls.DELETED]


class Project(models.Model):
    org_id = models.BigIntegerField()

    name = models.CharField(max_length=63)
    description = models.CharField(max_length=255)

    status = models.SmallIntegerField(default=Existence.ACTIVE)

    @classmethod
    def create(cls, org: Organization, name: str, descr: str):
        return cls(org_id=org.id, name=name, description=descr)

    def get_org(self):
        return first_or_default(Organization, id=self.org_id)

    class Meta:
        verbose_name = 'project'


class Artifact(models.Model):
    proj_id = models.BigIntegerField()

    type = models.CharField(max_length=31)

    filename = models.CharField(max_length=63)
    extension = models.CharField(max_length=15)

    # live collaborating documents are stored on another database and
    # managed by another server
    external = models.BooleanField(default=False)

    # created and updated fields are automatically set by Django
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    status = models.SmallIntegerField(default=Existence.ACTIVE)

    @classmethod
    class Meta:
        verbose_name = 'artifact'
