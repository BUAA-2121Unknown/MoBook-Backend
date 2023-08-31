from django.db import models
from django.utils import timezone

from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.model.model_extension import Existence, first_or_default


class Organization(models.Model):
    chat_id = models.IntegerField(default=0)
    description = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=63)
    avatar = models.CharField(max_length=63, default=None, null=True)

    status = models.SmallIntegerField(default=Existence.ACTIVE)

    def is_active(self):
        return self.status == Existence.ACTIVE

    @classmethod
    def create(cls, chat_id, name, description):
        return cls(chat_id=chat_id, name=name, description=description)

    class Meta:
        db_table = 'Organization'
        verbose_name = 'organization'


class Invitation(models.Model):
    token = models.CharField(max_length=63)
    created = models.DateTimeField()
    expires = models.DateTimeField(default=None, null=True)
    revoked = models.DateTimeField(default=None, null=True)
    oid = models.BigIntegerField()  # organization id
    review = models.BooleanField()  # whether it require review or not

    @classmethod
    def create(cls, token, created, expires, oid, review):
        return cls(token=token, created=created, expires=expires, revoked=None, oid=oid, review=review)

    def is_expired(self):
        return self.expires is not None and timezone.now() > self.expires

    def is_active(self):
        return self.revoked is None and not self.is_expired()

    def get_org(self):
        return first_or_default_by_cache(Organization, self.oid)

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
        return [cls.PENDING,
                cls.REVOKED,
                cls.ACCEPTED,
                cls.REJECTED,
                cls.DELETED]


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

    class Meta:
        verbose_name = 'pending_record'