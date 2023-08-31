from django.db import models

from org.models import Organization
from project.models import Project
from shared.utils.cache.cache_utils import first_or_default_by_cache
from shared.utils.model.model_extension import first_or_default


class User(models.Model):
    username = models.CharField(max_length=63)
    password = models.CharField(max_length=63)
    name = models.CharField(max_length=63, default=None, null=True)
    email = models.CharField(max_length=63)
    avatar = models.CharField(max_length=63, default=None, null=True)
    activated = models.BooleanField(default=False)

    def is_active(self):
        return self.activated

    @classmethod
    def create(cls, username, password, email, activated=False):
        return cls(username=username, password=password, email=email, activated=activated)

    class Meta:
        managed = True
        db_table = 'User'
        verbose_name = 'user'


class UserChatJump(models.Model):
    user_id = models.IntegerField()
    chat_id = models.IntegerField()
    message_id = models.IntegerField()
    valid = models.IntegerField()

    @classmethod
    def create(cls, user_id, chat_id, message_id, valid):
        return cls(user_id=user_id, chat_id=chat_id, message_id=message_id, valid=valid)

    class Meta:
        db_table = 'UserChatJump'
        verbose_name = 'user_chat_jump'


class ChatAuth:
    NORMAL = 0
    ADMIN = 1


class UserChatRelation(models.Model):
    user_id = models.BigIntegerField()
    chat_id = models.BigIntegerField()
    org_id = models.IntegerField(default=0)
    unread = models.IntegerField(default=0)
    authority = models.IntegerField(default=ChatAuth.NORMAL)  # 0 : ordinary, 1 : admin
    at_message_id = models.IntegerField(default=0)

    @classmethod
    def create(cls, user_id, chat_id, org_id, authority):
        return cls(user_id=user_id, chat_id=chat_id, org_id=org_id, authority=authority)

    class Meta:
        db_table = 'UserChatRelation'
        verbose_name = 'user_chat_relation'


class UserAuth:
    CREATOR = 0
    ADMIN = 1
    NORMAL = 2

    @classmethod
    def authorized(cls):
        return [UserAuth.CREATOR, UserAuth.ADMIN]

    @classmethod
    def all(cls):
        return [cls.CREATOR, cls.ADMIN, cls.NORMAL]

    @classmethod
    def to_string(cls, auth: int):
        if auth == UserAuth.CREATOR:
            return "Creator"
        elif auth == UserAuth.ADMIN:
            return "Administrator"
        elif auth == UserAuth.NORMAL:
            return "Member"
        else:
            return "Unknown"


class UserOrganizationProfile(models.Model):
    # 0 creator, 1 admin, 2 normal
    auth = models.IntegerField()
    user_id = models.BigIntegerField()
    org_id = models.BigIntegerField()
    nickname = models.CharField(max_length=63)

    def get_user(self):
        _, user = first_or_default_by_cache(User, self.user_id)
        return user

    def get_org(self):
        _, org = first_or_default_by_cache(Organization, self.org_id)
        return org

    @classmethod
    def create(cls, auth, user: User, org: Organization, nickname=None):
        if nickname is None:
            nickname = user.username
        return cls(auth=auth, user_id=user.id, org_id=org.id, nickname=nickname)

    class Meta:
        db_table = 'UserOrganizationProfile'
        verbose_name = 'user_org_profile'


class UserOrganizationRecord(models.Model):
    user_id = models.BigIntegerField()
    org_id = models.BigIntegerField(default=0)

    last_accessed = models.DateTimeField(auto_now=True)

    @classmethod
    def create(cls, user_id, org_id):
        return cls(user_id=user_id, org_id=org_id)

    class Meta:
        db_table = 'UserOrganizationRecord'
        verbose_name = 'user_org_record'