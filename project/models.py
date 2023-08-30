from django.db import models

from org.models import Organization
from shared.utils.model.model_extension import first_or_default, Existence


# Create your models here.


class Project(models.Model):
    org_id = models.BigIntegerField()
    root_id = models.BigIntegerField()  # root folder id

    name = models.CharField(max_length=63)
    description = models.CharField(max_length=255)

    status = models.SmallIntegerField(default=Existence.ACTIVE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, org: Organization, name: str, descr: str):
        return cls(org_id=org.id, name=name, description=descr)

    def is_active(self):
        return self.status == Existence.ACTIVE

    def get_org(self) -> Organization:
        return first_or_default(Organization, id=self.org_id)

    class Meta:
        verbose_name = 'project'
