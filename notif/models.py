from django.db import models

from org.dtos.models.org_dto import OrganizationDto
from org.models import Organization
from shared.utils.json.exceptions import JsonSerializeException
from shared.utils.json.serializer import serialize
from user.models import UserAuth


class NotifType:
    TEXT = 0
    AT_MESSAGE = 1
    INVITATION = 2
    ROLE_CHANGE = 3


class NotifBasePayload:
    def __init__(self, text: str):
        self.text: str = text


class NotifTextPayload(NotifBasePayload):
    def __init__(self, text: str):
        super().__init__(text)


class NotifAtPayload(NotifBasePayload):
    def __init__(self, text: str, chat_id: int):
        super().__init__(text)
        self.chatId = chat_id


class NotifInvitationPayload(NotifBasePayload):
    def __init__(self, text: str, status: int, org: Organization):
        super().__init__(text)
        self.status: int = status  # 0 rejected, 1 accepted
        self.org: OrganizationDto = OrganizationDto(org)


class NotifRoleChangePayload(NotifBasePayload):
    def __init__(self, text: str, org: Organization, new_auth: int):
        super().__init__(text)
        self.newAuth: str = UserAuth.to_string(new_auth)
        self.org: OrganizationDto = OrganizationDto(org)


class NotifStatus:
    UNREAD = 0
    READ = 0
    DELETED = 0


class Notification(models.Model):
    user_id = models.IntegerField(default=0)  # target user
    org_id = models.IntegerField(blank=True, null=True)  # belonging org

    type = models.SmallIntegerField(default=0)
    payload = models.TextField(default="{}")

    timestamp = models.DateTimeField(max_length=255, auto_now_add=True)

    status = models.SmallIntegerField(default=NotifStatus.UNREAD)

    @classmethod
    def create(cls, user_id, org_id, type, payload):
        try:
            pl = serialize(payload)
        except JsonSerializeException:
            pl = "{}"
        return cls(user_id=user_id, org_id=org_id, type=type, payload=pl)

    class Meta:
        managed = True
        db_table = 'Notification'
