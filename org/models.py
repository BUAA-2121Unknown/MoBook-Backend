from django.db import models
from django.utils import timezone


class Organization(models.Model):
    chat_id = models.IntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=63)
    avatar = models.CharField(max_length=63)

    @classmethod
    def create(cls, chat_id, description, name):
        return cls(chat_id=chat_id, description=description, name=name)

    class Meta:
        managed = True
        db_table = 'Organization'


class Invitation(models.Model):
    token = models.CharField(max_length=63)
    created = models.DateTimeField()
    expires = models.DateTimeField()
    revoked = models.DateTimeField(default=None, null=True)
    oid = models.BigIntegerField()  # organization id
    review = models.BooleanField()  # whether it require review or not

    @classmethod
    def create(cls, token, created, expires, oid, review):
        return cls(token=token, created=created, expires=expires, revoked=None, oid=oid, review=review)

    def is_expired(self):
        return timezone.now() > self.expires

    def is_active(self):
        return self.revoked is None and not self.is_expired()

    class Meta:
        verbose_name = 'invitation'


class PendingStatus:
    PENDING = 0
    REVOKED = 1
    ACCEPTED = 2
    REJECTED = 3
    DELETED = 3

    @classmethod
    def editable(cls):
        # for user side
        return [PendingStatus.PENDING]

    @classmethod
    def reviewable(cls):
        # for admin side
        return [PendingStatus.PENDING]

    @classmethod
    def deletable(cls):
        return [PendingStatus.REVOKED, PendingStatus.ACCEPTED, PendingStatus.REVOKED]

    @classmethod
    def user(cls):
        return [PendingStatus.REVOKED, PendingStatus.DELETED]

    @classmethod
    def admin(cls):
        return [PendingStatus.ACCEPTED, PendingStatus.REJECTED, PendingStatus.DELETED]

    @classmethod
    def all(cls):
        return [PendingStatus.PENDING,
                PendingStatus.REVOKED,
                PendingStatus.ACCEPTED,
                PendingStatus.REJECTED,
                PendingStatus.DELETED]


class PendingRecord(models.Model):
    uid = models.BigIntegerField()
    oid = models.BigIntegerField()
    user_status = models.SmallIntegerField()
    admin_status = models.SmallIntegerField()

    @classmethod
    def create(cls, uid, oid):
        return cls(uid=uid, oid=oid, user_status=PendingStatus.PENDING, admin_status=PendingStatus.PENDING)

    def editable(self):
        return self.user_status == PendingStatus.PENDING

    def deletable(self):
        return not self.editable()
