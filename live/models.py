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
    # token is a base64 encoded string that contains the share info
    token = models.CharField(max_length=255, primary_key=True)

    created = models.DateTimeField()
    expires = models.DateTimeField(default=None, null=True)
    revoked = models.DateTimeField(default=None, null=True)

    auth = models.SmallIntegerField()
    org_only = models.BooleanField(default=False)

    def is_expired(self):
        return self.expires is not None and timezone.now() > self.expires

    def is_active(self):
        return self.revoked is None and not self.is_expired()

    @classmethod
    def create(cls, token, created, expires, auth):
        return cls(token=token,
                   created=created,
                   expires=expires,
                   auth=auth)

    class Meta:
        verbose_name = 'share_token'
