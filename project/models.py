from random import Random

from django.db import models

from org.models import Organization
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.model.model_extension import Existence


# Create your models here.


class Project(models.Model):
    org_id = models.BigIntegerField()
    root_id = models.BigIntegerField(default=0)  # root folder id

    name = models.CharField(max_length=63)
    description = models.CharField(max_length=255)

    status = models.SmallIntegerField(default=Existence.ACTIVE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    avatar = models.CharField(max_length=31, default="1.svg")

    @classmethod
    def create(cls, org_id, name: str, descr: str):
        avatar = f"{Random().randint(1, 10)}.png"
        return cls(org_id=org_id, name=name, description=descr, avatar=avatar)

    def is_active(self):
        return self.status == Existence.ACTIVE

    def get_org(self) -> Organization:
        _, org = first_or_default_by_cache(Organization, self.org_id)
        return org

    class Meta:
        verbose_name = 'project'
