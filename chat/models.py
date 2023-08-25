from django.db import models


class Chat(models.Model):
    org_id = models.IntegerField()
    chat_name = models.CharField(max_length=63)
    type = models.IntegerField()  # 0 : private, 1 : group chat

    @classmethod
    def create(cls, org_id):
        return cls(org_id=org_id)

    class Meta:
        managed = True
        db_table = 'Chat'


