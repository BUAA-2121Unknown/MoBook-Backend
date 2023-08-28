from django.db import models
from django.utils.encoding import escape_uri_path

from org.models import Organization
from shared.utils.model.model_extension import first_or_default, Existence


# Create your models here.


class Project(models.Model):
    org_id = models.BigIntegerField()

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


class Artifact(models.Model):
    proj_id = models.BigIntegerField()
    creator_id = models.BigIntegerField()

    type = models.CharField(max_length=31)
    name = models.CharField(max_length=63)

    raw = models.BooleanField(default=True)
    filename = models.CharField(max_length=127, default=None, null=True)
    extension = models.CharField(max_length=15, default=None, null=True)

    # created and updated fields are automatically set by Django
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    live = models.BooleanField(default=False)

    status = models.SmallIntegerField(default=Existence.ACTIVE)

    @classmethod
    def create(cls, proj_id, creator_id, type: str, name: str, live: bool = False):
        return cls(proj_id=proj_id, creator_id=creator_id, type=type, name=name, live=live)

    def is_active(self):
        return self.status == Existence.ACTIVE

    def get_proj(self):
        return first_or_default(Project, id=self.proj_id)

    def get_org(self):
        return self.get_proj().get_org()

    def is_external(self):
        return self.filename is None or self.extension is None

    def has_file(self):
        return not self.is_external()

    def get_path(self):
        if self.is_external():
            return None
        return f"./files/projects/{self.proj_id}/attachments/{self.id}{self.extension}"

    def get_filename(self):
        if self.is_external():
            return None
        return escape_uri_path(f"{self.name}{self.extension}")

    class Meta:
        verbose_name = 'artifact'
