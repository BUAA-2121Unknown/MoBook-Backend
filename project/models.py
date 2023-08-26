from django.db import models


# Create your models here.

class ProjectStatus:
    ACTIVE = 0
    RECYCLED = 1
    DELETED = 2


class Project(models.Model):
    org_id = models.BigIntegerField()
    name = models.CharField(max_length=63)
    description = models.CharField(max_length=255)
    status = models.SmallIntegerField()


class Artifact(models.Model):
    proj_id = models.BigIntegerField()
    name = models.CharField(max_length=63)
    type = models.CharField(max_length=31)
    suffix = models.CharField(max_length=15)
