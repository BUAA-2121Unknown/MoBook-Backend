from django.db import models
from django.utils import timezone


# Create your models here.

class RefreshToken(models.Model):
    uid = models.BigIntegerField()  # corresponding user id
    token = models.CharField(max_length=63)
    created = models.DateTimeField()
    expires = models.DateTimeField()
    revoked = models.DateTimeField(default=None, null=True)

    @classmethod
    def create(cls, uid, token, created, expires):
        return cls(uid=uid, token=token, created=created, expires=expires)

    def is_expired(self):
        return timezone.now() > self.expires

    def is_active(self):
        return self.revoked is None and not self.is_expired()

    class Meta:
        verbose_name = "refresh_token"


class EmailRecord(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=31)
    expire = models.DateTimeField()
    usage = models.CharField(max_length=31)
    valid = models.BooleanField(default=True)

    @classmethod
    def create(cls, _email, _code, _expire, _usage):
        return cls(email=_email, code=_code, expire=_expire, usage=_usage)

    class Meta:
        ordering = ['id']
        verbose_name = "email_record"
