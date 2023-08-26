from django.db import models

from org.models import Organization
from project.models import Project
from shared.utils.model.model_extension import first_or_default


class User(models.Model):
    username = models.CharField(max_length=63)
    password = models.CharField(max_length=63)
    name = models.CharField(max_length=63, default=None, null=True)
    email = models.CharField(max_length=63)
    avatar = models.CharField(max_length=63, default=None, null=True)
    activated = models.BooleanField(default=False)

    @classmethod
    def create(cls, username, password, email, activated=False):
        return cls(username=username, password=password, email=email, activated=activated)

    class Meta:
        managed = True
        db_table = 'User'
        verbose_name = 'user'


class UserChatJump(models.Model):
    user_id = models.IntegerField()
    chat_id = models.IntegerField(primary_key=True)
    message_id = models.IntegerField()
    valid = models.IntegerField()

    @classmethod
    def create(cls, user_id, chat_id, message_id, valid):
        return cls(user_id=user_id, chat_id=chat_id, message_id=message_id, valid=valid)

    class Meta:
        managed = True
        db_table = 'UserChatJump'
        unique_together = (('chat_id', 'user_id', 'message_id'),)


class UserChatRelation(models.Model):
    user_id = models.IntegerField(primary_key=True)
    chat_id = models.IntegerField()
    unread = models.IntegerField()
    at_message_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'UserChatRelation'
        unique_together = (('user_id', 'chat_id'),)


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
    user_id = models.IntegerField(primary_key=True)
    org_id = models.IntegerField()
    nickname = models.CharField(max_length=63)

    def get_user(self):
        return first_or_default(User, id=self.user_id)

    def get_org(self):
        return first_or_default(Organization, id=self.org_id)

    @classmethod
    def create(cls, auth, user: User, org: Organization, nickname=None):
        if nickname is None:
            nickname = user.username
        return cls(auth, user_id=user.id, org_id=org.id, nickname=nickname)

    class Meta:
        managed = True
        db_table = 'UserOrganizationProfile'
        unique_together = (('user_id', 'org_id'),)


class UserProjectProfile(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    proj_id = models.BigIntegerField()
    role = models.CharField(max_length=63)

    @classmethod
    def create(cls, user: User, proj: Project, role: str):
        return cls(user_id=user.id, proj_id=proj.id, role=role)

    class Meta:
        db_table = 'UserProjectProfile'
