from django.db import models


class Notification(models.Model):
    user_id = models.IntegerField()
    org_id = models.IntegerField(blank=True, null=True)
    chat_id = models.IntegerField(blank=True, null=True)
    type = models.IntegerField()
    timestamp = models.DateTimeField(max_length=255, auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'Notification'
