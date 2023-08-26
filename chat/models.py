import os
import uuid

from django.db import models


def chat_avatar_path(self, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    # return the whole path to the file
    return os.path.join(self.chat_id, "avatar", filename)


class Chat(models.Model):
    org_id = models.IntegerField(default=0)
    chat_name = models.CharField(max_length=63)
    chat_avatar = models.ImageField(upload_to=chat_avatar_path, blank=True, null=True)
    latest_message = models.IntegerField(default=0)
    type = models.IntegerField(default=0)  # 0 : private, 1 : group chat

    @classmethod
    def create(cls, org_id):
        return cls(org_id=org_id)

    class Meta:
        managed = True
        db_table = 'Chat'


