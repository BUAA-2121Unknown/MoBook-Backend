from django.db import models
from django.utils import timezone


# Create your models here.

class ShareAuth:
    DENIED = 0
    READONLY = 1
    READWRITE = 2
    FULL = 3

    @classmethod
    def all(cls):
        return [cls.DENIED, cls.READONLY, cls.READWRITE, cls.FULL]

    # can only be set to these
    @classmethod
    def valid(cls):
        return [cls.READONLY, cls.READWRITE, cls.FULL]


class ShareToken(models.Model):
    item_id = models.BigIntegerField()  # item id

    proj_id = models.BigIntegerField()  # project id
    org_id = models.BigIntegerField()  # organization id

    token = models.CharField(max_length=63)

    created = models.DateTimeField()
    expires = models.DateTimeField(default=None, null=True)
    revoked = models.DateTimeField(default=None, null=True)

    auth = models.SmallIntegerField()
    org_only = models.BooleanField()

    def is_expired(self):
        return self.expires is not None and timezone.now() > self.expires

    def is_active(self):
        return self.revoked is None and not self.is_expired()

    @classmethod
    def create(cls, art_id, proj_id, org_id, token, created, expires, auth, org_only):
        return cls(art_id=art_id,
                   proj_id=proj_id,
                   org_id=org_id,
                   token=token,
                   created=created,
                   expires=expires,
                   auth=auth,
                   org_only=org_only)

    class Meta:
        verbose_name = 'share_token'
