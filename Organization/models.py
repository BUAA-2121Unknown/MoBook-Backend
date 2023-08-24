from django.db import models


class Organization(models.Model):
    chat_id = models.IntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=63)

    class Meta:
        managed = True
        db_table = 'Organization'


class UserOrganizationProfile(models.Model):
    auth = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(primary_key=True)
    org_id = models.IntegerField()
    nickname = models.CharField(max_length=63)

    class Meta:
        managed = True
        db_table = 'UserOrganizationProfile'
        unique_together = (('user_id', 'org_id'),)
