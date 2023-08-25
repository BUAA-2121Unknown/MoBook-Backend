from django.db import models


class User(models.Model):
    username = models.CharField(max_length=63)
    password = models.CharField(max_length=63)
    name = models.CharField(max_length=63, default=None, null=True)
    email = models.CharField(max_length=63)
    avatar = models.CharField(max_length=63, default=None, null=True)
    activated = models.BooleanField(default=False)

    @classmethod
    def create(cls, username, password, email, activated=False):
        return cls(username=username, password=password, email=email, activated=False)

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


class UserOrganizationProfile(models.Model):
    auth = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(primary_key=True)
    org_id = models.IntegerField()
    nickname = models.CharField(max_length=63)

    class Meta:
        managed = True
        db_table = 'UserOrganizationProfile'
        unique_together = (('user_id', 'org_id'),)
