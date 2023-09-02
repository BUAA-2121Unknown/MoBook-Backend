import os
import uuid

from django.db import models


def chat_avatar_path(self, filename, ext):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)

    # return the whole path to the file
    return os.path.join("chat/", str(self.chat_id), "avatar", filename)


class ChatType:
    PRIVATE = 0
    PUBLIC = 1
    ORG = 2


class ChatAvatar:
    DEFAULT = "url"


class Chat(models.Model):
    org_id = models.IntegerField(default=0)
    chat_name = models.CharField(max_length=63, default="群聊")
    chat_avatar = models.ImageField(upload_to=chat_avatar_path, blank=True, null=True,
                                    default=ChatAvatar.DEFAULT)  # default
    latest_message = models.IntegerField(default=0)
    type = models.IntegerField(default=ChatType.PUBLIC)  # 0 : private, 1 : group chat

    @classmethod
    def create(cls, org_id, name, type):
        return cls(org_id=org_id, chat_name=name, type=type)

    class Meta:
        managed = True
        db_table = 'Chat'
        verbose_name = 'Chat'
