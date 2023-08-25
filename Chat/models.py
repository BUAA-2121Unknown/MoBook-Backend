from django.db import models


class Chat(models.Model):
    org_id = models.IntegerField()

    @classmethod
    def create(cls, org_id):
        return cls(org_id=org_id)

    class Meta:
        managed = True
        db_table = 'Chat'


class Message(models.Model):
    image_path = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.IntegerField(blank=True, null=True)
    type = models.IntegerField()
    src_id = models.IntegerField()
    dst_id = models.IntegerField()
    chat_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(max_length=255, auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'Message'
