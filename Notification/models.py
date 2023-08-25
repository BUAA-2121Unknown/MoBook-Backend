from django.db import models


class Notification(models.Model):
    user_id = models.IntegerField()
    org_id = models.IntegerField(blank=True, null=True)
    chat_id = models.IntegerField(blank=True, null=True)
    type = models.IntegerField()
    timestamp = models.DateTimeField(max_length=255, auto_now_add=True)

    @classmethod
    def create(cls, user_id, org_id, chat_id, type, timestamp):
        return cls(user_id=user_id, org_id=org_id, chat_id=chat_id, type=type, timestamp=timestamp)

    class Meta:
        managed = True
        db_table = 'Notification'

