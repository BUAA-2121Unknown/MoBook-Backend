from django.db import models


class Organization(models.Model):
    chat_id = models.IntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=63)

    @classmethod
    def create(cls, chat_id, description, name):
        return cls(chat_id=chat_id, description=description, name=name)

    class Meta:
        managed = True
        db_table = 'Organization'


