from django.db import models

from shared.utils.json.serializer import serialize


class NotifStatus:
    UNREAD = 0
    READ = 1
    DELETED = 2

    @classmethod
    def all(cls):
        return [cls.UNREAD, cls.READ, cls.DELETED]

    @classmethod
    def valid(cls):
        return [cls.UNREAD, cls.READ]


class Notification(models.Model):
    user_id = models.BigIntegerField(default=0)  # target user
    org_id = models.BigIntegerField(default=0)  # belonging org

    type = models.SmallIntegerField(default=0)
    payload = models.TextField(default="{}")

    timestamp = models.DateTimeField(max_length=255, auto_now_add=True)

    status = models.SmallIntegerField(default=NotifStatus.UNREAD)

    @classmethod
    def create(cls, user_id, org_id, payload):
        try:
            print(payload)
            typ = payload.type
            pl = serialize(payload)
        except Exception as e:
            print(e)
            return None
        return cls(user_id=user_id, org_id=org_id, type=typ, payload=pl)

    class Meta:
        managed = True
        db_table = 'Notification'
