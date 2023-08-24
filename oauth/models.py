from datetime import datetime

from django.db import models


# Create your models here.

class RefreshToken(models.Model):
    uid = models.BigIntegerField()  # corresponding user id
    token = models.CharField(max_length=32)
    created = models.DateTimeField()
    expires = models.DateTimeField()
    revoked = models.DateTimeField(default=None)

    @classmethod
    def create(cls, uid, token, created, expires):
        return cls(uid=uid, token=token, created=created, expires=expires)

    def is_expired(self):
        return datetime.now() > self.expires

    def is_active(self):
        return self.revoked is None and not self.is_expired()

    class Meta:
        verbose_name = "refresh_token"
