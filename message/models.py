import os
import uuid

from django.db import models


def message_image_path(self, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    # return the whole path to the file
    return os.path.join(self.chat_id, "images", filename)


def message_file_path(self, filename):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex[:10], ext)
    # return the whole path to the file
    return os.path.join(self.chat_id, "files", filename)


class Message(models.Model):
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=message_image_path, blank=True, null=True)
    file = models.FileField(upload_to=message_file_path, blank=True, null=True)
    type = models.IntegerField()  # 0 : text, 1 : image, 2 : file
    src_id = models.IntegerField(default=0)
    dst_id = models.IntegerField(blank=True, null=True)
    chat_id = models.IntegerField(default=0)
    timestamp = models.DateTimeField(max_length=255, auto_now_add=True)

    @classmethod
    def create(cls, image_path, file_path, type, src_id, dst_id, chat_id, timestamp):
        return cls(image_path=image_path, file_path=file_path, type=type, src_id=src_id, dst_id=dst_id, chat_id=chat_id, timestamp=timestamp)

    class Meta:
        managed = True
        db_table = 'Message'




