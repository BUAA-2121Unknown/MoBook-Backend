from django.db import models


class Message(models.Model):
    image_path = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.IntegerField(blank=True, null=True)
    type = models.IntegerField()  # 0 : ordinary, 1 : image, 2 : file
    src_id = models.IntegerField()
    dst_id = models.IntegerField()
    chat_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(max_length=255, auto_now_add=True)

    @classmethod
    def create(cls, image_path, file_path, type, src_id, dst_id, chat_id, timestamp):
        return cls(image_path=image_path, file_path=file_path, type=type, src_id=src_id, dst_id=dst_id, chat_id=chat_id, timestamp=timestamp)

    class Meta:
        managed = True
        db_table = 'Message'
